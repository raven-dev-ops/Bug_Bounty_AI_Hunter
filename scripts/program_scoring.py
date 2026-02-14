import argparse
import math
from copy import deepcopy
from datetime import datetime, timezone

from .lib.catalog_guardrails import ensure_catalog_path
from .lib.catalog_parsers import (
    classify_feasibility,
    extract_restrictions,
    parse_response_time,
    parse_reward_range,
    parse_safe_harbor,
)
from .lib.io_utils import dump_data, load_data


BUCKETS = ["Easy", "Medium", "Hard", "Impossible", "God Mode"]
DEFAULT_CONFIG = {
    "weights": {
        "response_time": 0.25,
        "scope": 0.25,
        "restrictions": 0.25,
        "reward": 0.25,
    },
    "missing_score": 0.5,
    "bucket_thresholds": [0.2, 0.4, 0.6, 0.8],
    "response_time": {
        "thresholds_hours": [24, 72, 168, 336],
        "scores": [0.1, 0.3, 0.5, 0.7, 0.9],
    },
    "scope": {
        "max_units": 30,
        "wildcard_weight": 0.5,
        "cidr_weight": 0.5,
        "ip_range_weight": 0.5,
        "ports_weight": 0.25,
    },
    "restrictions": {
        "max_count": 6,
        "automation_penalty": 0.2,
        "application_keywords": [
            "application required",
            "apply",
            "invite-only",
            "invitation",
            "approval required",
            "approved researchers",
            "request access",
            "access request",
            "private program",
        ],
        "automation_keywords": [
            "no automated",
            "no scanning",
            "no fuzzing",
            "no automated scanning",
            "no automated testing",
        ],
        "block_keywords": [
            "do not test",
            "no testing",
        ],
    },
    "reward": {
        "max_value": 10000,
    },
}


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _deep_update(base, updates):
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_update(base[key], value)
        else:
            base[key] = value
    return base


def _load_config(path):
    config = deepcopy(DEFAULT_CONFIG)
    if not path:
        return config
    overrides = load_data(path)
    if not isinstance(overrides, dict):
        raise SystemExit("Scoring config must be a mapping.")
    return _deep_update(config, overrides)


def _clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))


def _bucket_for_score(score, thresholds):
    if len(thresholds) != 4:
        thresholds = DEFAULT_CONFIG["bucket_thresholds"]
    for index, threshold in enumerate(thresholds):
        if score <= threshold:
            return BUCKETS[index]
    return BUCKETS[-1]


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _extract_restriction_texts(restrictions):
    texts = []
    for item in _list(restrictions):
        if isinstance(item, dict):
            text = item.get("text") or item.get("notes")
            if text:
                texts.append(text)
            continue
        texts.append(item)
    return extract_restrictions(texts)


def _collect_restrictions(program):
    restrictions = []
    if isinstance(program.get("restrictions"), list):
        restrictions.extend(program.get("restrictions"))
    scope = program.get("scope") or {}
    if isinstance(scope.get("restrictions"), list):
        restrictions.extend(scope.get("restrictions"))
    cleaned = _extract_restriction_texts(restrictions)
    deduped = []
    seen = set()
    for item in cleaned:
        key = str(item).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _match_keywords(values, keywords):
    haystack = " ".join(str(item).lower() for item in values if item)
    return any(keyword in haystack for keyword in keywords)


def _safe_harbor_info(value):
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, bool):
        return {"present": value}
    if isinstance(value, str):
        return parse_safe_harbor(value)
    return {}


def _response_time_hours(value):
    response = None
    if isinstance(value, dict):
        response = value
    elif isinstance(value, str):
        response = parse_response_time(value)

    if not response:
        return None

    hours = []
    first = response.get("first_response_hours")
    resolution = response.get("resolution_time_hours")
    if first is not None:
        hours.append(float(first))
    if resolution is not None:
        hours.append(float(resolution))
    if not hours:
        return None
    return sum(hours) / len(hours)


def _response_score(hours, config):
    if hours is None:
        return None
    thresholds = config["response_time"].get("thresholds_hours", [])
    scores = config["response_time"].get("scores", [])
    if len(scores) != len(thresholds) + 1:
        thresholds = DEFAULT_CONFIG["response_time"]["thresholds_hours"]
        scores = DEFAULT_CONFIG["response_time"]["scores"]
    for threshold, score in zip(thresholds, scores):
        if hours <= threshold:
            return score
    return scores[-1]


def _scope_units(program, config):
    scope = program.get("scope") or {}
    in_scope = scope.get("in_scope") or []
    if not in_scope:
        return None, 0
    units = 0.0
    wildcard_weight = config["scope"].get("wildcard_weight", 0.5)
    cidr_weight = config["scope"].get("cidr_weight", 0.5)
    ip_range_weight = config["scope"].get("ip_range_weight", 0.5)
    ports_weight = config["scope"].get("ports_weight", 0.25)

    for asset in in_scope:
        units += 1.0
        if not isinstance(asset, dict):
            continue
        asset_type = str(asset.get("type") or "").lower()
        if asset_type == "wildcard":
            units += wildcard_weight
        elif asset_type == "cidr":
            units += cidr_weight
        elif asset_type == "ip-range":
            units += ip_range_weight
        if asset.get("ports"):
            units += ports_weight

    return units, len(in_scope)


def _scope_score(units, config):
    if units is None:
        return None
    max_units = config["scope"].get("max_units", 30) or 30
    return _clamp(units / float(max_units))


def _reward_max(program):
    reward = program.get("rewards")
    if isinstance(reward, dict):
        return reward.get("max") or reward.get("min")
    if isinstance(reward, (int, float)):
        return float(reward)
    if isinstance(reward, str):
        parsed = parse_reward_range(reward)
        if parsed.get("max") is not None:
            return parsed.get("max")
        if parsed.get("min") is not None:
            return parsed.get("min")
    return None


def _reward_score(max_reward, config):
    if max_reward is None:
        return None
    reward_max_value = config["reward"].get("max_value", 10000) or 10000
    score = math.log1p(max_reward) / math.log1p(reward_max_value)
    return _clamp(score)


def _restriction_score(restrictions, config):
    if restrictions is None:
        return None, False, False, False
    restriction_config = config["restrictions"]
    max_count = restriction_config.get("max_count", 6) or 6
    automation_penalty = restriction_config.get("automation_penalty", 0.2) or 0.0
    automation_keywords = restriction_config.get("automation_keywords", [])
    application_keywords = restriction_config.get("application_keywords", [])
    block_keywords = restriction_config.get("block_keywords", [])

    restriction_count = len(restrictions)
    base_score = _clamp(restriction_count / float(max_count))

    automation_restricted = _match_keywords(restrictions, automation_keywords)
    application_required = _match_keywords(restrictions, application_keywords)
    testing_disallowed = _match_keywords(restrictions, block_keywords)

    score = base_score
    if automation_restricted:
        score = _clamp(score + automation_penalty)
    return score, automation_restricted, application_required, testing_disallowed


def _weighted_score(component_scores, weights, missing_score, missing_data):
    total = 0.0
    weight_sum = 0.0
    for key, weight in weights.items():
        if weight is None:
            continue
        value = component_scores.get(key)
        if value is None:
            missing_data.append(key)
            value = missing_score
        total += value * weight
        weight_sum += weight
    if weight_sum <= 0:
        return missing_score
    return total / weight_sum


def score_program(program, config, public_only=False):
    weights = config.get("weights", DEFAULT_CONFIG["weights"])
    missing_score = config.get("missing_score", 0.5)
    missing_data = []

    response_hours = _response_time_hours(program.get("response_time"))
    response_score = _response_score(response_hours, config)

    scope_units, in_scope_count = _scope_units(program, config)
    scope_score = _scope_score(scope_units, config)

    restrictions = _collect_restrictions(program)
    (
        restriction_score,
        automation_restricted,
        application_required,
        testing_disallowed,
    ) = _restriction_score(restrictions, config)

    reward_max = _reward_max(program)
    reward_score = _reward_score(reward_max, config)

    safe_harbor = _safe_harbor_info(program.get("safe_harbor"))
    safe_harbor_missing = safe_harbor.get("present") is False
    feasibility = classify_feasibility(restrictions, safe_harbor)

    component_scores = {
        "response_time": response_score,
        "scope": scope_score,
        "restrictions": restriction_score,
        "reward": reward_score,
    }
    score = _weighted_score(component_scores, weights, missing_score, missing_data)
    bucket = _bucket_for_score(score, config.get("bucket_thresholds", []))

    overrides = []
    review_required = False

    if public_only and application_required:
        bucket = "Impossible"
        overrides.append(
            {
                "id": "application_required",
                "reason": "Program requires an application or approval.",
                "min_bucket": "Impossible",
            }
        )
        review_required = True

    if safe_harbor_missing:
        if bucket == "Easy":
            bucket = "Medium"
        overrides.append(
            {
                "id": "safe_harbor_missing",
                "reason": "Safe harbor is missing or explicitly absent.",
                "min_bucket": "Medium",
            }
        )
        review_required = True

    if feasibility.get("feasibility") == "blocked":
        bucket = "Impossible"
        overrides.append(
            {
                "id": "testing_disallowed",
                "reason": "Restrictions indicate testing is disallowed.",
                "min_bucket": "Impossible",
            }
        )
        review_required = True

    if bucket in ("Impossible", "God Mode"):
        review_required = True

    signals = {
        "response_time_hours": response_hours,
        "response_score": response_score,
        "scope_units": scope_units,
        "scope_in_count": in_scope_count,
        "scope_score": scope_score,
        "restrictions_count": len(restrictions),
        "automation_restricted": automation_restricted,
        "application_required": application_required,
        "restriction_score": restriction_score,
        "reward_max": reward_max,
        "reward_score": reward_score,
        "safe_harbor_present": safe_harbor.get("present"),
        "feasibility": feasibility.get("feasibility"),
    }

    return {
        "program_id": program.get("id"),
        "name": program.get("name"),
        "platform": program.get("platform"),
        "handle": program.get("handle"),
        "policy_url": program.get("policy_url"),
        "score": round(score * 100, 2),
        "bucket": bucket,
        "review_required": review_required,
        "missing_data": sorted(set(missing_data)),
        "signals": signals,
        "overrides": overrides,
    }


def score_programs(programs, config, public_only=False):
    scored = []
    for program in programs:
        if not isinstance(program, dict):
            continue
        scored.append(score_program(program, config, public_only=public_only))
    return scored


def _load_programs(path):
    data = load_data(path)
    if isinstance(data, dict) and "programs" in data:
        return data.get("programs") or []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []


def _summary(scored):
    by_bucket = {}
    review_required = 0
    scores = []
    for entry in scored:
        bucket = entry.get("bucket") or "Unknown"
        by_bucket[bucket] = by_bucket.get(bucket, 0) + 1
        if entry.get("review_required"):
            review_required += 1
        score_value = entry.get("score")
        if isinstance(score_value, (int, float)):
            scores.append(score_value)

    average_score = round(sum(scores) / len(scores), 2) if scores else None
    return {
        "total": len(scored),
        "by_bucket": by_bucket,
        "review_required": review_required,
        "average_score": average_score,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Score programs for difficulty buckets."
    )
    parser.add_argument(
        "--input",
        default="data/program_registry.json",
        help="Program registry JSON/YAML.",
    )
    parser.add_argument(
        "--output",
        default="data/program_scoring_output.json",
        help="Scoring output JSON/YAML path.",
    )
    parser.add_argument("--config", help="Scoring config JSON/YAML path.")
    parser.add_argument(
        "--public-only",
        action="store_true",
        help="Apply public-only overrides.",
    )
    args = parser.parse_args()

    ensure_catalog_path(args.output, label="Program scoring output")
    config = _load_config(args.config)
    programs = _load_programs(args.input)
    scored = score_programs(programs, config, public_only=args.public_only)

    output = {
        "schema_version": "0.1.0",
        "generated_at": _timestamp(),
        "public_only": bool(args.public_only),
        "summary": _summary(scored),
        "programs": scored,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
