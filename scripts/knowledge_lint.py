import re
from pathlib import Path

import yaml


REQUIRED_FIELDS = {"id", "title", "type", "status", "tags", "source", "date"}
TYPE_VALUES = {"source", "card", "checklist"}
STATUS_VALUES = {"draft", "reviewed"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_frontmatter(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        raise ValueError("Missing frontmatter delimiter.")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Frontmatter not closed with '---'.")
    frontmatter = parts[1].strip()
    data = yaml.safe_load(frontmatter) or {}
    if not isinstance(data, dict):
        raise ValueError("Frontmatter is not a mapping.")
    return data


def _lint_file(path):
    errors = []
    try:
        data = _parse_frontmatter(path)
    except ValueError as exc:
        return [str(exc)]

    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        errors.append(f"Missing fields: {', '.join(sorted(missing))}.")

    item_type = data.get("type")
    if item_type and item_type not in TYPE_VALUES:
        errors.append(f"Invalid type: {item_type}.")

    status = data.get("status")
    if status and status not in STATUS_VALUES:
        errors.append(f"Invalid status: {status}.")

    tags = data.get("tags")
    if tags is not None and not isinstance(tags, list):
        errors.append("Tags must be a list.")

    date_value = data.get("date")
    if date_value and not DATE_RE.match(str(date_value)):
        errors.append("Date must be YYYY-MM-DD.")

    return errors


def main():
    root = Path(__file__).resolve().parents[1]
    knowledge_root = root / "knowledge"
    paths = []
    # "sources/" can contain raw materials that intentionally lack frontmatter.
    # We lint source notes (`*.source.md`) and all cards/checklists.
    mappings = {
        "cards": "*.md",
        "checklists": "*.md",
        "sources": "*.source.md",
    }
    for folder, pattern in mappings.items():
        folder_path = knowledge_root / folder
        if folder_path.exists():
            paths.extend(folder_path.glob(pattern))

    errors = []
    for path in sorted(paths):
        if path.name.lower() == "readme.md":
            continue
        issues = _lint_file(path)
        for issue in issues:
            errors.append(f"{path.relative_to(root)}: {issue}")

    if errors:
        for entry in errors:
            print(entry)
        raise SystemExit(f"Knowledge lint failed with {len(errors)} error(s).")

    print("Knowledge lint passed.")


if __name__ == "__main__":
    main()
