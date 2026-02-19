from __future__ import annotations

from pathlib import Path
from typing import Any


DOCS_ROOT = (Path(__file__).resolve().parent.parent / "docs").resolve()


def _safe_relative_path(path: Path) -> str:
    return path.as_posix()


def _snippet(text: str, query: str, *, width: int = 90) -> str:
    lower = text.lower()
    idx = lower.find(query.lower())
    if idx < 0:
        return text[:width].strip()
    start = max(0, idx - width // 2)
    end = min(len(text), idx + width // 2)
    return text[start:end].strip().replace("\n", " ")


def _docs_index() -> dict[str, Path]:
    index: dict[str, Path] = {}
    for markdown_file in DOCS_ROOT.rglob("*.md"):
        relative = markdown_file.relative_to(DOCS_ROOT).as_posix()
        index[relative] = markdown_file
    return index


def search_docs(query: str, *, limit: int = 25) -> list[dict[str, Any]]:
    safe_query = query.strip()
    if not safe_query:
        return []
    safe_limit = max(1, min(100, int(limit)))

    results: list[dict[str, Any]] = []
    for markdown_file in sorted(DOCS_ROOT.rglob("*.md")):
        text = markdown_file.read_text(encoding="utf-8", errors="replace")
        if safe_query.lower() not in text.lower():
            continue
        relative = markdown_file.relative_to(DOCS_ROOT)
        title = relative.stem.replace("_", " ").replace("-", " ").title()
        results.append(
            {
                "path": _safe_relative_path(relative),
                "title": title,
                "snippet": _snippet(text, safe_query),
            }
        )
        if len(results) >= safe_limit:
            break
    return results


def read_doc_page(relative_path: str) -> dict[str, str]:
    requested = Path(str(relative_path or "").strip()).as_posix().lstrip("/")
    if not requested:
        raise ValueError("doc page not found")
    docs_map = _docs_index()
    full_path = docs_map.get(requested)
    if full_path is None:
        raise ValueError("doc page not found")
    content = full_path.read_text(encoding="utf-8", errors="replace")
    return {
        "path": requested,
        "content": content,
    }
