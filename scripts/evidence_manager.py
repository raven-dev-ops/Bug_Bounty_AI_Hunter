import argparse
from datetime import datetime, timezone
import hashlib
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


def _hash_file(path, algorithm):
    try:
        hasher = hashlib.new(algorithm)
    except ValueError as exc:
        raise SystemExit(f"Unsupported hash algorithm: {algorithm}") from exc
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _merge_hashes(existing, new_entries):
    merged = {}
    for entry in _list(existing):
        if isinstance(entry, dict) and entry.get("path"):
            merged[entry["path"]] = entry
    for entry in new_entries:
        merged[entry["path"]] = entry
    return list(merged.values())


def _hash_artifacts(item, artifact_root, algorithm):
    if not isinstance(item, dict):
        return
    artifacts = _list(item.get("artifacts"))
    if not artifacts:
        return
    root = Path(artifact_root or ".")
    new_entries = []
    for artifact in artifacts:
        artifact_path = Path(artifact)
        if not artifact_path.is_absolute():
            artifact_path = root / artifact_path
        entry = {
            "path": str(artifact),
            "algorithm": algorithm,
            "computed_at": _timestamp(),
        }
        if artifact_path.exists():
            entry["hash"] = _hash_file(artifact_path, algorithm)
            entry["size_bytes"] = artifact_path.stat().st_size
            entry["status"] = "ok"
        else:
            entry["status"] = "missing"
        new_entries.append(entry)
    if new_entries:
        item["hashes"] = _merge_hashes(item.get("hashes"), new_entries)


def _apply_custody(item, custody):
    if not isinstance(item, dict) or not custody:
        return
    if "custody" not in item:
        item["custody"] = custody


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
    existing = {
        item.get("id"): item for item in registry.get("evidence", []) if item.get("id")
    }
    custody = load_data(args.custody) if args.custody else None

    for item in items:
        item_id = item.get("id")
        if not item_id:
            continue
        _apply_custody(item, custody)
        if args.hash_artifacts:
            _hash_artifacts(item, args.artifact_root, args.hash_algorithm)
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
    add_parser.add_argument(
        "--hash-artifacts",
        action="store_true",
        help="Compute file hashes for listed artifacts.",
    )
    add_parser.add_argument(
        "--hash-algorithm",
        default="sha256",
        help="Hash algorithm for artifacts.",
    )
    add_parser.add_argument(
        "--artifact-root",
        default=".",
        help="Root directory for artifact paths.",
    )
    add_parser.add_argument(
        "--custody",
        help="JSON/YAML path with custody metadata to apply.",
    )
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="List evidence entries.")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
