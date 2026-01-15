import argparse
from pathlib import Path

from .lib.io_utils import dump_data, load_data
from .lib.manifest_utils import validate_manifest


REPO_ROOT = Path(__file__).resolve().parent.parent


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


def _component_entry(path):
    manifest_path = Path(path).resolve()
    repo_root = REPO_ROOT.resolve()
    manifest = load_data(manifest_path)
    errors = validate_manifest(manifest)
    name = None
    if isinstance(manifest, dict):
        name = manifest.get("name")
    if not name:
        name = Path(path).stem

    entrypoints = {}
    schemas = {}
    description = None
    repository = None
    license_id = None
    contact = None
    version = None
    capabilities = []
    if isinstance(manifest, dict):
        entrypoints = manifest.get("entrypoints", {}) or {}
        schemas = manifest.get("schemas", {}) or {}
        description = manifest.get("description")
        repository = manifest.get("repository")
        license_id = manifest.get("license")
        contact = manifest.get("contact")
        version = manifest.get("version")
        capabilities = manifest.get("capabilities", []) or []

    return {
        "name": name,
        "version": version,
        "path": manifest_path.parent.relative_to(repo_root).as_posix(),
        "manifest_path": manifest_path.relative_to(repo_root).as_posix(),
        "capabilities": capabilities,
        "schemas": schemas,
        "entrypoints": entrypoints,
        "description": description,
        "repository": repository,
        "license": license_id,
        "contact": contact,
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate the component registry index."
    )
    parser.add_argument(
        "--components-dir", default="components", help="Components directory."
    )
    parser.add_argument(
        "--output",
        default="data/component_registry_index.json",
        help="Output index JSON/YAML path.",
    )
    args = parser.parse_args()

    entries = [
        _component_entry(path)
        for path in _discover_manifests(args.components_dir)
    ]
    entries = sorted(entries, key=lambda item: item.get("name", ""))

    output = {
        "schema_version": "0.1.0",
        "components": entries,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
