import argparse
import json
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from .lib.catalog_guardrails import ensure_catalog_path
from .lib.io_utils import dump_data, load_data
from .lib.schema_utils import validate_schema
from .lib.scope_utils import asset_key, normalize_scope_assets


SOURCE_PRIORITY = {
    "manual": 0,
    "internal": 1,
    "hackerone": 2,
    "bugcrowd": 3,
    "yeswehack": 4,
    "intigriti": 5,
    "synack": 6,
    "public": 7,
    "unknown": 99,
}
KNOWN_PLATFORMS = set(SOURCE_PRIORITY.keys()) - {
    "manual",
    "internal",
    "public",
    "unknown",
}
SLUG_RE = re.compile(r"[^a-z0-9]+")


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _clean_list(values):
    if values is None:
        return []
    if isinstance(values, list):
        items = values
    else:
        items = [values]
    cleaned = []
    for item in items:
        text = _clean_text(item)
        if text:
            cleaned.append(text)
    return cleaned


def _normalize_name(value):
    text = " ".join(_clean_text(value).split())
    return text or ""


def _normalize_handle(value):
    return _clean_text(value).lower()


def _normalize_policy_url(value):
    text = _clean_text(value)
    if not text:
        return ""
    if "://" not in text:
        text = f"https://{text}"
    parsed = urlparse(text)
    netloc = parsed.netloc or parsed.path
    path = parsed.path if parsed.netloc else ""
    scheme = parsed.scheme or "https"
    normalized = f"{scheme}://{netloc}{path}".lower().rstrip("/")
    return normalized


def _normalize_terms_url(value):
    return _normalize_policy_url(value)


def _slugify(value):
    text = SLUG_RE.sub("-", _clean_text(value).lower()).strip("-")
    return text or "unknown"


def _value_key(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    return _clean_text(value)


def _source_label(record):
    source = _clean_text(record.get("source"))
    if source:
        return source.lower()
    platform = _clean_text(record.get("platform"))
    return platform.lower() if platform else "unknown"


def _source_priority(record):
    source = _source_label(record)
    return SOURCE_PRIORITY.get(source, SOURCE_PRIORITY["unknown"])


def _candidate_sort_key(record):
    return (
        _source_priority(record),
        _source_label(record),
        _clean_text(record.get("source_id")),
        _normalize_name(record.get("name")),
    )


def _identity_keys(record):
    keys = []
    platform = _clean_text(record.get("platform")).lower()
    handle = _clean_text(record.get("handle")).lower()
    policy_url = _clean_text(record.get("policy_url")).lower()
    name = _normalize_name(record.get("name")).lower()

    if platform and handle:
        keys.append(f"platform:{platform}:{handle}")
    if policy_url:
        keys.append(f"url:{policy_url}")
    if name:
        keys.append(f"name:{name}")
    return keys


def _scope_signature(scope):
    if not scope:
        return ""
    in_scope = sorted(
        key for key in (asset_key(item) for item in scope.get("in_scope", [])) if key
    )
    out_scope = sorted(
        key
        for key in (asset_key(item) for item in scope.get("out_of_scope", []))
        if key
    )
    restrictions = sorted(_clean_list(scope.get("restrictions")))
    return json.dumps(
        {
            "in_scope": in_scope,
            "out_of_scope": out_scope,
            "restrictions": restrictions,
        },
        sort_keys=True,
    )


def _normalize_scope(scope, errors, source_label):
    if not scope:
        return None
    if not isinstance(scope, dict):
        errors.append(f"{source_label}: scope must be a mapping.")
        return None
    normalized = dict(scope)
    in_scope, err = normalize_scope_assets(scope.get("in_scope"))
    if err:
        errors.extend([f"{source_label}: {item}" for item in err])
    out_scope, err = normalize_scope_assets(scope.get("out_of_scope"))
    if err:
        errors.extend([f"{source_label}: {item}" for item in err])
    normalized["in_scope"] = in_scope
    normalized["out_of_scope"] = out_scope
    restrictions = _clean_list(scope.get("restrictions"))
    if restrictions:
        normalized["restrictions"] = sorted(set(restrictions))
    else:
        normalized.pop("restrictions", None)

    if not normalized.get("in_scope") and not normalized.get("out_of_scope"):
        if not normalized.get("restrictions") and not normalized.get("notes"):
            return None

    return normalized


def _normalize_source_record(record, index):
    if not isinstance(record, dict):
        return None, [f"record[{index}]: source record must be a mapping."]

    errors = []
    normalized = dict(record)
    source = _source_label(record)
    normalized["source"] = source

    if not normalized.get("platform") and source in KNOWN_PLATFORMS:
        normalized["platform"] = source

    name = _normalize_name(record.get("name") or record.get("program"))
    if name:
        normalized["name"] = name

    handle = _normalize_handle(record.get("handle"))
    if handle:
        normalized["handle"] = handle

    policy_url = record.get("policy_url") or record.get("url")
    policy_url = _normalize_policy_url(policy_url)
    if policy_url:
        normalized["policy_url"] = policy_url

    terms_url = _normalize_terms_url(record.get("terms_url"))
    if terms_url:
        normalized["terms_url"] = terms_url

    license_text = _clean_text(record.get("license"))
    if license_text:
        normalized["license"] = license_text

    attribution_text = _clean_text(record.get("attribution"))
    if attribution_text:
        normalized["attribution"] = attribution_text

    reuse_constraints = _clean_text(record.get("reuse_constraints"))
    if reuse_constraints:
        normalized["reuse_constraints"] = reuse_constraints

    scope = _normalize_scope(record.get("scope"), errors, source)

    restrictions = _clean_list(record.get("restrictions"))
    if scope and scope.get("restrictions"):
        restrictions.extend(scope.get("restrictions"))
    restrictions = sorted(set(_clean_list(restrictions)))
    if restrictions:
        normalized["restrictions"] = restrictions
    else:
        normalized.pop("restrictions", None)

    if scope:
        if restrictions:
            scope = dict(scope)
            scope["restrictions"] = restrictions
        normalized["scope"] = scope
    else:
        normalized.pop("scope", None)

    source_id = _clean_text(record.get("source_id"))
    if not source_id:
        if normalized.get("platform") and normalized.get("handle"):
            source_id = f"{normalized['platform']}:{normalized['handle']}"
        elif normalized.get("policy_url"):
            source_id = normalized["policy_url"]
        elif normalized.get("name"):
            source_id = _slugify(normalized["name"])
        else:
            source_id = f"{source}-{index}"
    normalized["source_id"] = source_id

    identity_keys = _identity_keys(normalized)
    if not identity_keys:
        errors.append(f"record[{index}]: unable to derive identity keys.")
    normalized["_identity_keys"] = identity_keys

    return normalized, errors


def _select_field(records, field):
    candidates = [record for record in records if record.get(field)]
    if not candidates:
        return None, None
    selected = min(candidates, key=_candidate_sort_key)
    return selected.get(field), _source_label(selected)


def _select_scope(records):
    candidates = [
        record
        for record in records
        if record.get("scope") and _scope_signature(record["scope"])
    ]
    if not candidates:
        return None, None
    selected = min(candidates, key=_candidate_sort_key)
    return selected.get("scope"), _source_label(selected)


def _build_source_record(record):
    fields = (
        "source",
        "source_id",
        "platform",
        "handle",
        "name",
        "policy_url",
        "rewards",
        "terms_url",
        "license",
        "attribution",
        "reuse_constraints",
        "http_status",
        "parser_version",
        "git_commit",
        "artifact_path",
        "artifact_hash",
        "hash_algorithm",
        "scope",
        "restrictions",
        "safe_harbor",
        "fetched_at",
        "url",
        "notes",
    )
    output = {}
    for field in fields:
        value = record.get(field)
        if value is None:
            continue
        if isinstance(value, list) and not value:
            continue
        if isinstance(value, dict) and not value:
            continue
        output[field] = value
    return output


def _collect_conflicts(records, field, selected_source, normalizer=None, notes=None):
    values = {}
    for record in records:
        value = record.get(field)
        if value is None or value == "" or value == [] or value == {}:
            continue
        key = normalizer(value) if normalizer else _value_key(value)
        values.setdefault(key, {"value": value, "sources": []})
        values[key]["sources"].append(_source_label(record))
    if len(values) <= 1:
        return None
    other_sources = sorted(
        {source for entry in values.values() for source in entry["sources"]}
        - {selected_source}
    )
    return {
        "field": field,
        "selected_source": selected_source,
        "other_sources": other_sources,
        "notes": notes,
    }


def _merge_restrictions(records):
    restrictions = []
    for record in records:
        restrictions.extend(_clean_list(record.get("restrictions")))
    merged = sorted(set(restrictions))

    per_record = set()
    for record in records:
        per_record.add(tuple(sorted(_clean_list(record.get("restrictions")))))
    conflict = None
    if len(per_record) > 1:
        conflict = {
            "field": "restrictions",
            "selected_source": "union",
            "other_sources": sorted({_source_label(record) for record in records}),
            "notes": "Merged union of restriction lists.",
        }
    return merged, conflict


def _collect_attribution(records):
    entries = []
    seen = set()
    for record in records:
        text = _clean_text(record.get("attribution"))
        terms_url = _clean_text(record.get("terms_url"))
        license_text = _clean_text(record.get("license"))
        reuse_constraints = _clean_text(record.get("reuse_constraints"))
        if not (text or terms_url or license_text or reuse_constraints):
            continue
        source = _source_label(record)
        key = (source, text, terms_url, license_text, reuse_constraints)
        if key in seen:
            continue
        seen.add(key)
        entry = {
            "source": source,
            "text": text or None,
            "terms_url": terms_url or None,
            "license": license_text or None,
            "reuse_constraints": reuse_constraints or None,
        }
        cleaned = {k: v for k, v in entry.items() if v is not None}
        entries.append(cleaned)
    entries.sort(key=lambda item: (item.get("source", ""), item.get("terms_url", "")))
    return entries


def _merge_group(records):
    records = sorted(records, key=_candidate_sort_key)
    sources = [_build_source_record(record) for record in records]
    sources = sorted(
        sources,
        key=lambda item: (
            _clean_text(item.get("source")),
            _clean_text(item.get("source_id")),
        ),
    )

    name, _ = _select_field(records, "name")
    platform, _ = _select_field(records, "platform")
    handle, _ = _select_field(records, "handle")
    policy_url, _ = _select_field(records, "policy_url")
    rewards, rewards_source = _select_field(records, "rewards")
    safe_harbor, safe_harbor_source = _select_field(records, "safe_harbor")
    scope, scope_source = _select_scope(records)

    restrictions, restrictions_conflict = _merge_restrictions(records)
    if scope and restrictions:
        scope = dict(scope)
        scope["restrictions"] = restrictions

    identity_keys = sorted(
        {key for record in records for key in record.get("_identity_keys", [])}
    )

    base_id = None
    if platform and handle:
        base_id = f"{platform}:{handle}"
    elif policy_url:
        base_id = policy_url
    elif name:
        base_id = name
    program_id = f"program:{_slugify(base_id or 'unknown')}"

    conflicts = []
    conflict = _collect_conflicts(
        records,
        "rewards",
        rewards_source,
        notes="Selected highest-priority source.",
    )
    if conflict:
        conflicts.append(conflict)
    conflict = _collect_conflicts(
        records,
        "safe_harbor",
        safe_harbor_source,
        notes="Selected highest-priority source.",
    )
    if conflict:
        conflicts.append(conflict)
    conflict = _collect_conflicts(
        records,
        "scope",
        scope_source,
        normalizer=_scope_signature,
        notes="Selected highest-priority scope to avoid expanding coverage.",
    )
    if conflict:
        conflicts.append(conflict)
    if restrictions_conflict:
        conflicts.append(restrictions_conflict)

    attribution = _collect_attribution(records)

    output = {
        "id": program_id,
        "name": name or "Unnamed Program",
        "platform": platform,
        "handle": handle,
        "policy_url": policy_url,
        "rewards": rewards,
        "safe_harbor": safe_harbor,
        "scope": scope,
        "restrictions": restrictions or None,
        "attribution": attribution,
        "identity_keys": identity_keys,
        "sources": sources,
        "conflicts": conflicts,
    }

    cleaned = {}
    for key, value in output.items():
        if value is None:
            continue
        if isinstance(value, list) and not value:
            continue
        if isinstance(value, dict) and not value:
            continue
        cleaned[key] = value
    return cleaned


def merge_sources(records):
    normalized = []
    errors = []
    for index, record in enumerate(records):
        entry, entry_errors = _normalize_source_record(record, index)
        if entry is not None:
            normalized.append(entry)
        errors.extend(entry_errors)
    if errors:
        message = "Program registry normalization errors:\n" + "\n".join(errors)
        raise SystemExit(message)

    groups = {}
    key_map = {}
    for record in normalized:
        keys = record.get("_identity_keys", [])
        group_id = None
        for key in keys:
            if key in key_map:
                group_id = key_map[key]
                break
        if group_id is None:
            group_id = f"group-{len(groups) + 1}"
            groups[group_id] = []
        groups[group_id].append(record)
        for key in keys:
            key_map[key] = group_id

    programs = [_merge_group(records) for records in groups.values()]
    programs = sorted(
        programs, key=lambda item: (item.get("name", ""), item.get("id", ""))
    )
    return programs


def _load_sources(path):
    data = load_data(path)
    if isinstance(data, dict):
        if "sources" in data:
            return data.get("sources") or []
        if "programs" in data:
            return data.get("programs") or []
        return [data]
    if isinstance(data, list):
        return data
    return []


def _sources_from_registry(registry):
    sources = []
    if not isinstance(registry, dict):
        return sources
    for program in registry.get("programs", []):
        if not isinstance(program, dict):
            continue
        program_sources = program.get("sources") or []
        if program_sources:
            sources.extend(program_sources)
            continue
        attribution_entries = program.get("attribution") or []
        attribution_entry = (
            attribution_entries[0]
            if isinstance(attribution_entries, list) and attribution_entries
            else {}
        )
        sources.append(
            {
                "source": "registry",
                "source_id": program.get("id"),
                "name": program.get("name"),
                "platform": program.get("platform"),
                "handle": program.get("handle"),
                "policy_url": program.get("policy_url"),
                "rewards": program.get("rewards"),
                "terms_url": attribution_entry.get("terms_url"),
                "license": attribution_entry.get("license"),
                "attribution": attribution_entry.get("text"),
                "reuse_constraints": attribution_entry.get("reuse_constraints"),
                "scope": program.get("scope"),
                "restrictions": program.get("restrictions"),
                "safe_harbor": program.get("safe_harbor"),
            }
        )
    return sources


def main():
    parser = argparse.ArgumentParser(
        description="Merge program records into a normalized registry."
    )
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="JSON/YAML file containing program source records.",
    )
    parser.add_argument(
        "--registry",
        help="Optional existing registry file to merge from.",
    )
    parser.add_argument(
        "--output",
        default="data/program_registry.json",
        help="Output registry JSON/YAML path.",
    )
    args = parser.parse_args()

    sources = []
    for path in args.input:
        sources.extend(_load_sources(path))

    registry = None
    if args.registry:
        registry = load_data(args.registry)
        sources.extend(_sources_from_registry(registry))

    programs = merge_sources(sources)

    if registry and registry.get("created_at"):
        created_at = registry.get("created_at")
    else:
        created_at = _timestamp()

    output = {
        "schema_version": "0.1.0",
        "created_at": created_at,
        "updated_at": _timestamp(),
        "programs": programs,
    }
    ensure_catalog_path(args.output, label="Program registry output")
    validate_schema(output, "schemas/program_registry.schema.json")
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
