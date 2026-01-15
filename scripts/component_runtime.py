import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data
from lib.manifest_utils import validate_manifest


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


def _load_manifest(path):
    manifest = load_data(path)
    errors = validate_manifest(manifest)
    return {
        "path": str(path),
        "manifest": manifest,
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate component manifests.")
    parser.add_argument(
        "--components-dir", default="components", help="Components directory."
    )
    parser.add_argument("--manifest", help="Single manifest file to validate.")
    parser.add_argument("--output", help="Output registry JSON/YAML path.")
    args = parser.parse_args()

    if args.manifest:
        records = [_load_manifest(Path(args.manifest))]
    else:
        records = [_load_manifest(path) for path in _discover_manifests(args.components_dir)]

    output = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "components": records,
    }

    if args.output:
        dump_data(args.output, output)
    else:
        dump_data("output/component_registry.json", output)


if __name__ == "__main__":
    main()
