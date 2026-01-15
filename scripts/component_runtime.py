import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data
from lib.manifest_utils import validate_manifest

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency
    jsonschema = None


def _discover_manifests(components_dir):
    manifests = []
    root = Path(components_dir)
    if not root.exists():
        return manifests
    for path in sorted(root.rglob("component_manifest.*")):
        if path.suffix.lower() not in (".yaml", ".yml", ".json"):
            continue
        manifests.append(path)
    return manifests


def _load_schema():
    schema_path = REPO_ROOT / "schemas" / "component_manifest.schema.json"
    if not schema_path.exists():
        return None
    return load_data(schema_path)


def _schema_errors(manifest, schema):
    if not schema or not jsonschema:
        return []
    errors = []
    try:
        jsonschema.validate(manifest, schema)
    except jsonschema.ValidationError as exc:
        errors.append(str(exc.message))
    return errors


def _parse_csv(value):
    if not value:
        return set()
    if isinstance(value, list):
        return {str(item).strip() for item in value if str(item).strip()}
    return {item.strip() for item in str(value).split(",") if item.strip()}


def _resolve_enabled(name, config, enable_set, disable_set):
    if enable_set:
        return name in enable_set
    if disable_set:
        return name not in disable_set
    config_enable = _parse_csv(config.get("enabled"))
    config_disable = _parse_csv(config.get("disabled"))
    if config_enable:
        return name in config_enable
    if config_disable:
        return name not in config_disable
    return True


def _load_manifest(path, schema, config, enable_set, disable_set):
    manifest = load_data(path)
    errors = validate_manifest(manifest)
    errors.extend(_schema_errors(manifest, schema))
    name = None
    if isinstance(manifest, dict):
        name = manifest.get("name")
    if not name:
        name = Path(path).stem
    return {
        "path": str(path),
        "manifest": manifest,
        "errors": errors,
        "enabled": _resolve_enabled(name, config, enable_set, disable_set),
    }


def main():
    parser = argparse.ArgumentParser(description="Validate component manifests.")
    parser.add_argument(
        "--components-dir", default="components", help="Components directory."
    )
    parser.add_argument("--manifest", help="Single manifest file to validate.")
    parser.add_argument("--config", help="Runtime config JSON/YAML path.")
    parser.add_argument("--enable", help="Comma-separated component names to enable.")
    parser.add_argument("--disable", help="Comma-separated component names to disable.")
    parser.add_argument("--output", help="Output registry JSON/YAML path.")
    args = parser.parse_args()

    config = {}
    if args.config:
        config = load_data(args.config)
        if not isinstance(config, dict):
            raise SystemExit("Runtime config must be a mapping.")

    enable_set = _parse_csv(args.enable)
    disable_set = _parse_csv(args.disable)
    schema = _load_schema()

    if args.manifest:
        records = [_load_manifest(Path(args.manifest), schema, config, enable_set, disable_set)]
    else:
        records = [
            _load_manifest(path, schema, config, enable_set, disable_set)
            for path in _discover_manifests(args.components_dir)
        ]

    output = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "components": records,
        "notes": [
            "Component registry is informational only.",
            "Schema validation requires the jsonschema package.",
        ],
    }

    if args.output:
        dump_data(args.output, output)
    else:
        dump_data("output/component_registry.json", output)


if __name__ == "__main__":
    main()
