import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _targets_from_input(data):
    if isinstance(data, dict) and "assets" in data:
        return _list(data.get("assets"))
    if isinstance(data, dict) and "scope" in data:
        scope = data.get("scope", {})
        return _list(scope.get("in_scope"))
    return _list(data)


def _asset_values(assets):
    values = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        value = asset.get("value")
        if value:
            values.append(value.lower())
    return values


def _match_record(record_value, targets):
    record_value = (record_value or "").lower()
    return any(record_value.endswith(target) for target in targets)


def main():
    parser = argparse.ArgumentParser(description="Enrich assets with intel records.")
    parser.add_argument("--source", required=True, help="Intel source JSON/YAML.")
    parser.add_argument("--targets", required=True, help="Targets input path.")
    parser.add_argument("--output", required=True, help="Output JSON/YAML path.")
    parser.add_argument("--provider", default="file", help="Provider name.")
    args = parser.parse_args()

    targets_data = load_data(args.targets)
    targets = _asset_values(_targets_from_input(targets_data))

    records = []
    notes = []
    if args.provider != "file":
        notes.append(f"Provider '{args.provider}' is not implemented. Use file input.")
    else:
        source_data = load_data(args.source)
        if isinstance(source_data, dict) and "records" in source_data:
            records = _list(source_data.get("records"))
        else:
            records = _list(source_data)

    matches = []
    for record in records:
        if not isinstance(record, dict):
            continue
        value = record.get("asset") or record.get("domain") or record.get("host")
        if value and _match_record(value, targets):
            matches.append(record)

    output = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider,
        "matches": matches,
        "notes": notes,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
