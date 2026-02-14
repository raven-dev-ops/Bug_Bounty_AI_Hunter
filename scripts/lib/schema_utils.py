import json
from pathlib import Path


def _require_jsonschema():
    try:
        import jsonschema
    except ImportError as exc:
        raise SystemExit(
            "Schema validation requires jsonschema. Install with: pip install jsonschema"
        ) from exc
    return jsonschema


def _load_schema(path):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"Schema not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema(data, schema_path):
    jsonschema = _require_jsonschema()
    schema = _load_schema(schema_path)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as exc:
        raise SystemExit(
            f"Schema validation failed for {schema_path}: {exc.message}"
        ) from exc
