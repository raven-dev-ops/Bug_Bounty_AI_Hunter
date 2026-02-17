import json
from pathlib import Path


def _require_yaml():
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required for YAML files. Install with: pip install pyyaml"
        ) from exc
    return yaml


def load_data(path):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")

    if path.suffix.lower() in (".yaml", ".yml"):
        yaml = _require_yaml()
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_data(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.suffix.lower() in (".yaml", ".yml"):
        yaml = _require_yaml()
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            yaml.safe_dump(data, handle, sort_keys=False)
        return

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
