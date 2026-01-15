import argparse
from datetime import datetime, timezone
from pathlib import Path

from .lib.io_utils import dump_data, load_data


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _default_registry():
    return {
        "schema_version": "0.1.0",
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
        "evidence": [],
    }


def _load_registry(path):
    path = Path(path)
    if not path.exists():
        return _default_registry()
    return load_data(path)


def _save_registry(path, registry):
    registry["updated_at"] = _timestamp()
    dump_data(path, registry)


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _load_evidence(path):
    data = load_data(path)
    if isinstance(data, dict) and "evidence" in data:
        return _list(data.get("evidence"))
    if isinstance(data, dict):
        return [data]
    return _list(data)


def cmd_init(args):
    registry = _default_registry()
    _save_registry(args.registry, registry)


def cmd_add(args):
    registry = _load_registry(args.registry)
    items = _load_evidence(args.input)
    existing = {item.get("id"): item for item in registry.get("evidence", []) if item.get("id")}

    for item in items:
        item_id = item.get("id")
        if not item_id:
            continue
        existing[item_id] = item

    registry["evidence"] = list(existing.values())
    _save_registry(args.registry, registry)


def cmd_list(args):
    registry = _load_registry(args.registry)
    items = registry.get("evidence", [])
    print(f"Evidence entries: {len(items)}")
    for item in items:
        print(f"- {item.get('id')} | {item.get('type')} | {item.get('description')}")


def main():
    parser = argparse.ArgumentParser(description="Manage evidence registry.")
    parser.add_argument("--registry", default="evidence/registry.json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize the registry.")
    init_parser.set_defaults(func=cmd_init)

    add_parser = subparsers.add_parser("add", help="Add evidence entries.")
    add_parser.add_argument("--input", required=True, help="Evidence JSON/YAML.")
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="List evidence entries.")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
