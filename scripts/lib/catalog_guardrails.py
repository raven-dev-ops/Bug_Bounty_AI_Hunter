from pathlib import Path


FORBIDDEN_PARTS = {"output", "evidence"}


def ensure_catalog_path(path, label="Catalog output"):
    if not path:
        return
    parts = Path(path).parts
    if any(part in FORBIDDEN_PARTS for part in parts):
        raise SystemExit(f"{label} must not live under output/ or evidence/.")
