import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _require_yaml():
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required for knowledge publishing. Install with: pip install pyyaml"
        ) from exc
    return yaml


def _read_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    yaml = _require_yaml()
    meta = yaml.safe_load(parts[1].strip()) or {}
    if not isinstance(meta, dict):
        meta = {}
    body = parts[2].lstrip("\n")
    return meta, body


def _demote_h1(text):
    lines = []
    in_code = False
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            lines.append(line)
            continue
        if not in_code and line.startswith("# "):
            lines.append("## " + line[2:])
            continue
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def _write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


@dataclass(frozen=True)
class Item:
    item_id: str
    title: str
    status: str
    item_type: str
    source: str
    date: str
    tags: list[str]
    src_path: Path
    out_path: Path


def _load_item(src_path, out_path):
    raw = src_path.read_text(encoding="utf-8", errors="replace")
    meta, body = _read_frontmatter(raw)
    if not meta:
        raise SystemExit(f"Missing frontmatter: {src_path}")

    item_id = str(meta.get("id") or "").strip()
    title = str(meta.get("title") or "").strip()
    item_type = str(meta.get("type") or "").strip()
    status = str(meta.get("status") or "").strip()
    source = str(meta.get("source") or "").strip()
    date = str(meta.get("date") or "").strip()
    tags = meta.get("tags") or []
    tags = tags if isinstance(tags, list) else []
    tags_text = ", ".join(str(tag).strip() for tag in tags if str(tag).strip())

    if not title:
        title = src_path.stem
    if not item_id:
        item_id = src_path.stem
    if not item_type:
        item_type = "n/a"
    if not status:
        status = "n/a"

    rendered = []
    rendered.append(f"# {title}")
    rendered.append("")
    rendered.append("## Metadata")
    rendered.append(f"- ID: {item_id}")
    rendered.append(f"- Type: {item_type}")
    rendered.append(f"- Status: {status}")
    if tags_text:
        rendered.append(f"- Tags: {tags_text}")
    if source:
        rendered.append(f"- Source: {source}")
    if date:
        rendered.append(f"- Date: {date}")
    rendered.append("")
    rendered.append(_demote_h1(body).rstrip())
    rendered.append("")

    _write_text(out_path, "\n".join(rendered))

    return Item(
        item_id=item_id,
        title=title,
        status=status,
        item_type=item_type,
        source=source,
        date=date,
        tags=[str(tag).strip() for tag in tags if str(tag).strip()],
        src_path=src_path,
        out_path=out_path,
    )


def _safe_clean_dir(path):
    path = Path(path)
    if not path.exists():
        return
    if not path.is_dir():
        raise SystemExit(f"Refusing to clean non-directory: {path}")
    shutil.rmtree(path)


def _render_index(*, items_by_type, docs_root):
    lines = []
    lines.append("# Knowledge Index (Docs)")
    lines.append("")
    lines.append("Generated from curated knowledge items under `knowledge/`.")
    lines.append("")
    lines.append("Regenerate:")
    lines.append("- `python -m scripts.publish_knowledge_docs`")
    lines.append("")

    sections = [
        ("checklist", "Checklists"),
        ("card", "Cards"),
        ("source", "Sources"),
    ]

    for item_type, title in sections:
        lines.append(f"## {title}")
        items = items_by_type.get(item_type) or []
        if not items:
            lines.append("- None")
            lines.append("")
            continue
        lines.append("| ID | Title | Status | Page |")
        lines.append("| --- | --- | --- | --- |")
        for item in items:
            rel = item.out_path.relative_to(docs_root).as_posix()
            lines.append(
                f"| {item.item_id} | {item.title} | {item.status} | [{item.out_path.name}]({rel}) |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Publish knowledge cards/checklists/sources into docs for MkDocs."
    )
    parser.add_argument(
        "--knowledge-root",
        default="knowledge",
        help="Knowledge root directory (default: knowledge).",
    )
    parser.add_argument(
        "--docs-root",
        default="docs",
        help="Docs root directory (default: docs).",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/knowledge",
        help="Output directory for published knowledge (default: docs/knowledge).",
    )
    parser.add_argument(
        "--index-out",
        default="docs/KNOWLEDGE_INDEX.md",
        help="Output path for docs knowledge index (default: docs/KNOWLEDGE_INDEX.md).",
    )
    args = parser.parse_args(argv)

    os.chdir(REPO_ROOT)

    knowledge_root = Path(args.knowledge_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    index_out = Path(args.index_out).resolve()

    # Ensure we only ever write under docs/.
    docs_root = Path(args.docs_root).resolve()
    if docs_root not in out_dir.resolve().parents:
        raise SystemExit(f"Refusing to write outside docs/: {out_dir}")
    if docs_root not in index_out.resolve().parents:
        raise SystemExit(f"Refusing to write index outside docs/: {index_out}")

    _safe_clean_dir(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mappings = [
        ("cards", "card", "*.md"),
        ("checklists", "checklist", "*.md"),
        ("sources", "source", "*.source.md"),
    ]

    items_by_type = {"card": [], "checklist": [], "source": []}

    for folder, item_type, pattern in mappings:
        src_dir = knowledge_root / folder
        if not src_dir.exists():
            continue
        for src_path in sorted(src_dir.glob(pattern)):
            if src_path.name.lower() == "readme.md":
                continue
            out_path = out_dir / folder / src_path.name
            item = _load_item(src_path, out_path)
            items_by_type[item_type].append(item)

    for items in items_by_type.values():
        items.sort(key=lambda item: item.item_id)

    index_content = _render_index(items_by_type=items_by_type, docs_root=docs_root)
    _write_text(index_out, index_content)


if __name__ == "__main__":
    main()
