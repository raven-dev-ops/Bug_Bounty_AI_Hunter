import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


SECTION_TITLES = {
    "source": "Sources",
    "card": "Cards",
    "checklist": "Checklists",
}


def _read_frontmatter(path):
    yaml = _require_yaml()
    with path.open("r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end_index = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break
    if end_index is None:
        return {}
    raw = "\n".join(lines[1:end_index])
    data = yaml.safe_load(raw) or {}
    return data if isinstance(data, dict) else {}


def _require_yaml():
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required for knowledge index generation. Install with: pip install pyyaml"
        ) from exc
    return yaml


def _gather_items(knowledge_root):
    sections = {key: [] for key in SECTION_TITLES}
    mappings = {
        "sources": "source",
        "cards": "card",
        "checklists": "checklist",
    }

    for folder, default_type in mappings.items():
        base = knowledge_root / folder
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            meta = _read_frontmatter(path)
            if not meta:
                continue
            item_type = str(meta.get("type") or default_type).strip().lower()
            if item_type not in sections:
                item_type = default_type
            item_id = str(meta.get("id") or path.stem).strip()
            title = str(meta.get("title") or path.stem).strip()
            status = str(meta.get("status") or "unknown").strip()
            rel_path = path.relative_to(REPO_ROOT).as_posix()
            sections[item_type].append(
                {
                    "id": item_id,
                    "title": title,
                    "status": status,
                    "path": rel_path,
                }
            )

    for items in sections.values():
        items.sort(key=lambda item: item["id"])
    return sections


def _render_index(sections):
    lines = [
        "# Knowledge Index",
        "",
        "This index lists knowledge sources, cards, and checklists with status.",
        "",
    ]

    for key, title in SECTION_TITLES.items():
        lines.append(f"## {title}")
        items = sections.get(key, [])
        if not items:
            lines.append("- None")
            lines.append("")
            continue
        for item in items:
            lines.append(
                f"- {item['id']} | {item['title']} | {item['status']} | `{item['path']}`"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate knowledge index.")
    parser.add_argument(
        "--knowledge-root",
        default="knowledge",
        help="Knowledge root directory.",
    )
    parser.add_argument(
        "--output",
        default="knowledge/INDEX.md",
        help="Output markdown path.",
    )
    args = parser.parse_args()

    knowledge_root = (REPO_ROOT / args.knowledge_root).resolve()
    sections = _gather_items(knowledge_root)
    content = _render_index(sections)
    output_path = REPO_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
