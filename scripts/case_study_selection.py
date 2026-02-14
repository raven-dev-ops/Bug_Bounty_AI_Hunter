import argparse
from datetime import datetime, timezone

from .lib.io_utils import dump_data, load_data


BUCKET_ORDER = ["Easy", "Medium", "Hard", "Impossible", "God Mode"]


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _load_registry(path):
    data = load_data(path)
    if isinstance(data, dict) and "programs" in data:
        return data.get("programs") or []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []


def _load_scoring(path):
    data = load_data(path)
    if isinstance(data, dict) and "programs" in data:
        return data.get("programs") or []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []


def _bucket_rank(bucket):
    try:
        return BUCKET_ORDER.index(bucket)
    except ValueError:
        return len(BUCKET_ORDER)


def _restriction_texts(program, limit=3):
    restrictions = []
    for item in _list(program.get("restrictions")):
        if isinstance(item, dict):
            text = item.get("text") or item.get("notes")
            if text:
                restrictions.append(text)
        else:
            restrictions.append(str(item))
    scope = program.get("scope") or {}
    for item in _list(scope.get("restrictions")):
        restrictions.append(str(item))
    cleaned = [text.strip() for text in restrictions if str(text).strip()]
    deduped = []
    seen = set()
    for text in cleaned:
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(text)
    return deduped[:limit]


def _build_reasons(scored, program):
    reasons = []
    score = scored.get("score")
    bucket = scored.get("bucket")
    if bucket:
        if isinstance(score, (int, float)):
            reasons.append(f"Bucket {bucket} (score {score}).")
        else:
            reasons.append(f"Bucket {bucket}.")

    signals = scored.get("signals") or {}
    safe_harbor = signals.get("safe_harbor_present")
    if safe_harbor is True:
        reasons.append("Safe harbor present.")
    elif safe_harbor is False:
        reasons.append("Safe harbor missing.")

    restrictions_count = signals.get("restrictions_count")
    if restrictions_count is not None:
        reasons.append(f"Restrictions count: {restrictions_count}.")

    response_hours = signals.get("response_time_hours")
    if response_hours is not None:
        reasons.append(f"Response time: {response_hours} hours.")

    scope_count = signals.get("scope_in_count")
    if scope_count is not None:
        reasons.append(f"In-scope assets: {scope_count}.")

    reward_max = signals.get("reward_max")
    if reward_max is not None:
        reasons.append(f"Reward max: {reward_max}.")

    highlights = _restriction_texts(program)
    if highlights:
        reasons.append("Restriction highlights: " + "; ".join(highlights) + ".")

    missing = scored.get("missing_data") or []
    if missing:
        reasons.append("Missing data: " + ", ".join(sorted(set(missing))) + ".")

    if scored.get("review_required"):
        reasons.append("Review required before use.")

    return reasons


def _shortlist(scored, registry_map, allowed_buckets, max_items):
    candidates = []
    for entry in scored:
        program_id = entry.get("program_id")
        program = registry_map.get(program_id)
        if not program:
            continue
        bucket = entry.get("bucket")
        if allowed_buckets and bucket not in allowed_buckets:
            continue
        signals = entry.get("signals") or {}
        restrictions_count = signals.get("restrictions_count")
        candidates.append(
            {
                "scored": entry,
                "program": program,
                "bucket_rank": _bucket_rank(bucket),
                "score": entry.get("score", 0),
                "restrictions_count": restrictions_count,
            }
        )

    if not candidates:
        for entry in scored:
            program_id = entry.get("program_id")
            program = registry_map.get(program_id)
            if not program:
                continue
            candidates.append(
                {
                    "scored": entry,
                    "program": program,
                    "bucket_rank": _bucket_rank(entry.get("bucket")),
                    "score": entry.get("score", 0),
                    "restrictions_count": None,
                }
            )

    candidates.sort(
        key=lambda item: (
            item["bucket_rank"],
            item["score"] if isinstance(item["score"], (int, float)) else 0,
            item["restrictions_count"]
            if item["restrictions_count"] is not None
            else 99,
            (item["program"].get("name") or ""),
        )
    )
    shortlist = []
    for item in candidates[:max_items]:
        scored_entry = item["scored"]
        program = item["program"]
        reasons = _build_reasons(scored_entry, program)
        shortlist.append(
            {
                "program_id": scored_entry.get("program_id"),
                "name": program.get("name"),
                "platform": program.get("platform"),
                "handle": program.get("handle"),
                "policy_url": program.get("policy_url"),
                "bucket": scored_entry.get("bucket"),
                "score": scored_entry.get("score"),
                "reasons": reasons,
                "signals": scored_entry.get("signals") or {},
            }
        )
    return shortlist


def main():
    parser = argparse.ArgumentParser(
        description="Select short case-study candidates from scoring output."
    )
    parser.add_argument(
        "--registry",
        default="data/program_registry.json",
        help="Program registry JSON/YAML.",
    )
    parser.add_argument(
        "--scoring",
        default="data/program_scoring_output.json",
        help="Program scoring JSON/YAML.",
    )
    parser.add_argument(
        "--output",
        default="data/case_study_shortlist.json",
        help="Shortlist output JSON/YAML.",
    )
    parser.add_argument(
        "--buckets",
        help="Comma-separated buckets to include (default: Easy,Medium).",
    )
    parser.add_argument("--max", type=int, default=2, help="Max results.")
    args = parser.parse_args()

    buckets = ["Easy", "Medium"]
    if args.buckets:
        buckets = [item.strip() for item in args.buckets.split(",") if item.strip()]

    registry = _load_registry(args.registry)
    registry_map = {
        program.get("id"): program
        for program in registry
        if isinstance(program, dict) and program.get("id")
    }
    scored = _load_scoring(args.scoring)

    shortlist = _shortlist(scored, registry_map, buckets, args.max)

    output = {
        "schema_version": "0.1.0",
        "generated_at": _timestamp(),
        "criteria": {
            "buckets": buckets,
            "max_results": args.max,
        },
        "shortlist": shortlist,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
