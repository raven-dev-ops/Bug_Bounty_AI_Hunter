import argparse
from pathlib import Path


def _find_non_ascii_lines(text, limit=3):
    hits = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if any(ord(ch) >= 128 for ch in line):
            # Render non-ASCII as '?' so output stays ASCII-only.
            snippet = "".join(ch if ord(ch) < 128 else "?" for ch in line)
            hits.append((line_no, snippet[:160]))
            if len(hits) >= limit:
                break
    return hits


def main():
    parser = argparse.ArgumentParser(
        description="Fail if any Markdown files contain non-ASCII characters."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repo root to scan (default '.').",
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
        "fetch_cache",
        "ingestion_audit",
        "LOCAL_APPDATA_FONTCONFIG_CACHE",
        "output",
    }

    md_paths = [
        path
        for path in root.rglob("*.md")
        if not any(part in ignore_dirs for part in path.parts)
    ]

    violations = []
    for path in sorted(md_paths):
        data = path.read_bytes()
        if any(byte >= 0x80 for byte in data):
            text = data.decode("utf-8", errors="replace")
            hits = _find_non_ascii_lines(text)
            rel = str(path.relative_to(root))
            violations.append((rel, hits))

    if violations:
        for rel, hits in violations:
            print(f"{rel}: non-ASCII detected")
            for line_no, snippet in hits:
                print(f"  L{line_no}: {snippet}")
        raise SystemExit(
            f"Markdown ASCII validation failed for {len(violations)} file(s)."
        )

    print(f"Markdown ASCII validation passed ({len(md_paths)} file(s) scanned).")


if __name__ == "__main__":
    main()
