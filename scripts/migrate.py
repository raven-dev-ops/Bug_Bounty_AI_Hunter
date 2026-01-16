import argparse
import json
from pathlib import Path

from .lib.io_utils import load_data, dump_data


MIGRATIONS = {}


def _detect_artifact(data, path):
    if path:
        name = Path(path).name.lower()
        if name in (
            "component_manifest.yaml",
            "component_manifest.yml",
            "component_manifest.json",
        ):
            return "component_manifest"
    if isinstance(data, dict):
        required = {"name", "version", "capabilities", "schemas"}
        if required.issubset(set(data.keys())):
            return "component_manifest"
    return None


def _current_version(data):
    if isinstance(data, dict):
        value = data.get("schema_version")
        if isinstance(value, str) and value:
            return value
    return "0.0.0"


def _register_migration(artifact, from_version, to_version):
    def decorator(func):
        MIGRATIONS[(artifact, from_version, to_version)] = func
        return func

    return decorator


@_register_migration("component_manifest", "0.0.0", "0.1.0")
def _migrate_component_manifest_0_0_0_to_0_1_0(data):
    if not isinstance(data, dict):
        raise SystemExit("Component manifest must be a mapping.")
    updated = dict(data)
    updated.setdefault("schema_version", "0.1.0")
    return updated


def migrate_data(data, artifact, from_version, to_version):
    current = _current_version(data)
    if current != from_version:
        raise SystemExit(f"Input schema_version is {current}. Expected {from_version}.")

    key = (artifact, from_version, to_version)
    handler = MIGRATIONS.get(key)
    if not handler:
        raise SystemExit(
            f"No migration registered for {artifact} {from_version} -> {to_version}."
        )
    return handler(data)


def _render_preview(data):
    return json.dumps(data, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Migrate artifacts between schema versions."
    )
    parser.add_argument("--input", required=True, help="Artifact JSON/YAML path.")
    parser.add_argument("--output", help="Output JSON/YAML path.")
    parser.add_argument(
        "--in-place", action="store_true", help="Overwrite the input file."
    )
    parser.add_argument(
        "--artifact",
        default="auto",
        choices=["auto", "component_manifest"],
        help="Artifact type (auto to detect).",
    )
    parser.add_argument("--from", dest="from_version", required=True)
    parser.add_argument("--to", dest="to_version", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.output and args.in_place:
        raise SystemExit("Use --output or --in-place, not both.")

    if not args.output and not args.in_place and not args.dry_run:
        raise SystemExit("Provide --output or --in-place (or use --dry-run).")

    data = load_data(args.input)
    artifact = args.artifact
    if artifact == "auto":
        artifact = _detect_artifact(data, args.input)
    if not artifact:
        raise SystemExit("Unable to detect artifact type. Use --artifact.")

    migrated = migrate_data(data, artifact, args.from_version, args.to_version)

    if args.dry_run:
        print(f"Dry run: {artifact} {args.from_version} -> {args.to_version}")
        print(_render_preview(migrated), end="")
        return

    output_path = Path(args.output) if args.output else Path(args.input)
    dump_data(output_path, migrated)


if __name__ == "__main__":
    main()
