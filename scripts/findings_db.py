import argparse
from datetime import datetime, timezone
from pathlib import Path

from .lib.io_utils import dump_data, load_data


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _default_db():
    return {
        "schema_version": "0.1.0",
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
        "findings": [],
    }


def _load_db(path):
    path = Path(path)
    if not path.exists():
        return _default_db()
    return load_data(path)


def _save_db(path, db):
    db["updated_at"] = _timestamp()
    dump_data(path, db)


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _load_findings(path):
    data = load_data(path)
    if isinstance(data, dict) and "findings" in data:
        return _list(data.get("findings"))
    if isinstance(data, dict):
        return [data]
    return _list(data)


def cmd_init(args):
    db = _default_db()
    _save_db(args.db, db)


def cmd_add(args):
    db = _load_db(args.db)
    findings = _load_findings(args.input)
    existing = {item.get("id"): item for item in db.get("findings", []) if item.get("id")}

    for finding in findings:
        finding_id = finding.get("id")
        if not finding_id:
            continue
        entry = existing.get(finding_id, {})
        entry.update(finding)
        entry.setdefault("status", args.status)
        entry.setdefault("source", args.source)
        existing[finding_id] = entry

    db["findings"] = list(existing.values())
    _save_db(args.db, db)


def cmd_list(args):
    db = _load_db(args.db)
    findings = db.get("findings", [])
    print(f"Findings: {len(findings)}")
    for finding in findings:
        print(
            f"- {finding.get('id')} | {finding.get('severity')} | {finding.get('status')} | "
            f"{finding.get('title')}"
        )


def main():
    parser = argparse.ArgumentParser(description="Manage a findings database.")
    parser.add_argument("--db", default="data/findings_db.json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize the database.")
    init_parser.set_defaults(func=cmd_init)

    add_parser = subparsers.add_parser("add", help="Add findings to the database.")
    add_parser.add_argument("--input", required=True, help="Findings JSON/YAML.")
    add_parser.add_argument("--status", default="open")
    add_parser.add_argument("--source", default="import")
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="List findings.")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
