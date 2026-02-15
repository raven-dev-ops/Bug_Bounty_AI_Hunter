import argparse
import re
from pathlib import Path


LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")


def _is_external(link):
    lowered = link.lower()
    return lowered.startswith(("http://", "https://", "mailto:", "tel:"))


def _normalize_target(link, root, source_path):
    link = link.split("#", 1)[0].split("?", 1)[0].strip()
    if not link:
        return None
    if link.startswith("#"):
        return None
    if _is_external(link):
        return None
    if link.startswith("<") and link.endswith(">"):
        link = link[1:-1].strip()
    if link.startswith("/"):
        return (root / link.lstrip("/")).resolve()
    return (source_path.parent / link).resolve()


def _scan_file(path, root):
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = []
    for match in LINK_RE.finditer(text):
        link = match.group(1).strip()
        target = _normalize_target(link, root, path)
        if target is None:
            continue
        if not target.exists():
            missing.append(link)
    return missing


def main():
    parser = argparse.ArgumentParser(description="Validate local markdown links exist.")
    parser.add_argument(
        "--root",
        default=".",
        help="Repo root for link resolution (default '.').",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()

    ignore_dirs = {
        ".git",
        ".venv",
        "site",
        "node_modules",
        "__pycache__",
        ".hypothesis",
        ".pytest_cache",
        ".ruff_cache",
        "LOCAL_APPDATA_FONTCONFIG_CACHE",
        "data",
        "output",
    }
    paths = [
        path
        for path in root.rglob("*.md")
        if not any(part in ignore_dirs for part in path.parts)
    ]

    errors = []
    for path in sorted(paths):
        missing = _scan_file(path, root)
        for link in missing:
            errors.append(f"{path.relative_to(root)}: missing {link}")

    if errors:
        for entry in errors:
            print(entry)
        raise SystemExit(
            f"Markdown link validation failed with {len(errors)} error(s)."
        )

    print("Markdown link validation passed.")


if __name__ == "__main__":
    main()
