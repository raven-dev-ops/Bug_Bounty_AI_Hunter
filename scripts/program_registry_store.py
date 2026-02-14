import argparse
from datetime import datetime, timezone
from pathlib import Path

from .lib.catalog_guardrails import ensure_catalog_path
from .lib.io_utils import dump_data, load_data
from .lib.schema_utils import validate_schema
from .program_registry import merge_sources


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _default_registry(schema_version):
    return {
        "schema_version": schema_version,
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
        "programs": [],
    }


def _load_registry(path, schema_version):
    if not path:
        return _default_registry(schema_version)
    path = Path(path)
    if not path.exists():
        return _default_registry(schema_version)
    data = load_data(path)
    if not isinstance(data, dict):
        raise SystemExit("Registry file must be a mapping.")
    return data


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
        sources.append(
            {
                "source": program.get("platform") or "registry",
                "source_id": program.get("id"),
                "name": program.get("name"),
                "platform": program.get("platform"),
                "handle": program.get("handle"),
                "policy_url": program.get("policy_url"),
                "rewards": program.get("rewards"),
                "scope": program.get("scope"),
                "restrictions": program.get("restrictions"),
                "safe_harbor": program.get("safe_harbor"),
            }
        )
    return sources


def cmd_init(args):
    registry = _default_registry(args.schema_version)
    ensure_catalog_path(args.output, label="Catalog registry output")
    validate_schema(registry, "schemas/program_registry.schema.json")
    dump_data(args.output, registry)


def cmd_add(args):
    registry = _load_registry(args.registry, args.schema_version)
    sources = _sources_from_registry(registry)
    for source_path in args.input:
        sources.extend(_load_sources(source_path))

    programs = merge_sources(sources)
    registry["programs"] = programs
    registry["updated_at"] = _timestamp()

    output = args.output or args.registry
    if not output:
        raise SystemExit("--output or --registry is required.")
    ensure_catalog_path(output, label="Catalog registry output")
    validate_schema(registry, "schemas/program_registry.schema.json")
    dump_data(output, registry)


def cmd_list(args):
    registry = _load_registry(args.registry, args.schema_version)
    programs = registry.get("programs") or []
    print(f"Programs: {len(programs)}")
    for program in programs:
        name = program.get("name") or "Unnamed Program"
        print(f"- {name} ({program.get('id')})")


def cmd_migrate(args):
    registry = _load_registry(args.registry, args.from_version)
    registry["schema_version"] = args.to_version
    registry["updated_at"] = _timestamp()
    output = args.output or args.registry
    if not output:
        raise SystemExit("--output or --registry is required.")
    ensure_catalog_path(output, label="Catalog registry output")
    validate_schema(registry, "schemas/program_registry.schema.json")
    dump_data(output, registry)


def main():
    parser = argparse.ArgumentParser(description="Manage the program registry store.")
    parser.add_argument("--registry", help="Registry path to load/update.")
    parser.add_argument("--schema-version", default="0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a registry file.")
    init_parser.add_argument(
        "--output", default="data/program_registry.json", help="Output registry path."
    )
    init_parser.set_defaults(func=cmd_init)

    add_parser = subparsers.add_parser("add", help="Merge sources into registry.")
    add_parser.add_argument("--input", action="append", required=True)
    add_parser.add_argument("--output")
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="List registry entries.")
    list_parser.set_defaults(func=cmd_list)

    migrate_parser = subparsers.add_parser(
        "migrate", help="Update registry schema version."
    )
    migrate_parser.add_argument("--from", dest="from_version", required=True)
    migrate_parser.add_argument("--to", dest="to_version", required=True)
    migrate_parser.add_argument("--output")
    migrate_parser.set_defaults(func=cmd_migrate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
