import argparse
from datetime import datetime, timezone

from .lib.io_utils import dump_data, load_data


QUALITY_FIELDS = [
    "http_status",
    "parser_version",
    "git_commit",
    "artifact_hash",
    "fetched_at",
]


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _load_registry(path):
    data = load_data(path)
    if isinstance(data, dict) and "programs" in data:
        return data.get("programs") or []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []


def _parse_time(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _latest_fetched_at(sources):
    latest = None
    for source in sources:
        fetched_at = _parse_time(source.get("fetched_at"))
        if fetched_at and (latest is None or fetched_at > latest):
            latest = fetched_at
    return latest


def _field_coverage(sources):
    coverage = {}
    for field in QUALITY_FIELDS:
        coverage[field] = any(source.get(field) for source in sources)
    return coverage


def _quality_score(coverage):
    total = len(QUALITY_FIELDS)
    present = sum(1 for value in coverage.values() if value)
    if total == 0:
        return 0.0
    return round(present / float(total), 2)


def _build_entry(program):
    sources = program.get("sources") or []
    coverage = _field_coverage(sources)
    score = _quality_score(coverage)
    latest = _latest_fetched_at(sources)
    freshness_days = None
    if latest:
        freshness_days = (datetime.now(timezone.utc) - latest).days

    return {
        "program_id": program.get("id"),
        "name": program.get("name"),
        "platform": program.get("platform"),
        "handle": program.get("handle"),
        "provenance_score": score,
        "last_fetched_at": latest.isoformat() if latest else None,
        "freshness_days": freshness_days,
        "signals": {
            "field_coverage": coverage,
            "sources_count": len(sources),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Score provenance quality and freshness for program records."
    )
    parser.add_argument(
        "--input",
        default="data/program_registry.json",
        help="Program registry JSON/YAML.",
    )
    parser.add_argument(
        "--output",
        default="data/program_provenance_output.json",
        help="Provenance output JSON/YAML.",
    )
    args = parser.parse_args()

    programs = _load_registry(args.input)
    output = {
        "schema_version": "0.1.0",
        "generated_at": _timestamp(),
        "programs": [
            _build_entry(program) for program in programs if isinstance(program, dict)
        ],
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
