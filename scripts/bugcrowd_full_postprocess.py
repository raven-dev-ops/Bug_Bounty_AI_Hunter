import argparse
import json
import re
from pathlib import Path

from scripts import bugcrowd_briefs


_BRIEF_DOC_RE = re.compile(
    r"## Brief Version Document\s*```json\s*(?P<json>\{.*?\})\s*```",
    re.S,
)


def _extract_brief_doc(markdown_text):
    match = _BRIEF_DOC_RE.search(markdown_text or "")
    if not match:
        return None
    try:
        return json.loads(match.group("json"))
    except json.JSONDecodeError:
        return None


def _insert_rendered_sections(markdown_text, rendered_sections):
    if not rendered_sections:
        return markdown_text, False
    if "## Brief (Rendered)" in (markdown_text or ""):
        return markdown_text, False

    match = re.search(r"^## API Endpoints \(From Page\)", markdown_text, re.M)
    if not match:
        return markdown_text, False

    insert_at = match.start()
    prefix = markdown_text[:insert_at].rstrip() + "\n\n"
    suffix = markdown_text[insert_at:].lstrip()
    return prefix + rendered_sections.rstrip() + "\n\n" + suffix, True


def _index_row_from_brief(slug, brief_doc):
    data = brief_doc.get("data") or {}
    brief = (data.get("brief") or {}) if isinstance(data, dict) else {}
    engagement = (data.get("engagement") or {}) if isinstance(data, dict) else {}
    scope_groups = (data.get("scope") or []) if isinstance(data, dict) else []

    name = bugcrowd_briefs._md_escape(brief.get("name")) or slug
    safe = brief.get("safeHarborStatus") or {}
    safe_label = ""
    if isinstance(safe, dict):
        safe_label = bugcrowd_briefs._md_escape(safe.get("label") or safe.get("status"))
    rewards = bugcrowd_briefs._reward_summary(scope_groups)
    state = bugcrowd_briefs._md_escape(engagement.get("state"))
    starts_at = bugcrowd_briefs._md_escape(engagement.get("startsAt"))
    return {
        "slug": slug,
        "name": name,
        "rewards": rewards,
        "safe_harbor": safe_label,
        "state": state,
        "starts_at": starts_at,
    }


def _write_index(path, rows):
    lines = []
    lines.append("# Bugcrowd Full Brief Board (Local)")
    lines.append("")
    lines.append(
        "> WARNING: These files may include auth-only program details. Do not commit this output."
    )
    lines.append("")
    lines.append("| Engagement | Rewards | Safe Harbor | State | Starts |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in rows:
        name = row.get("name") or row.get("slug") or "n/a"
        slug = row.get("slug") or ""
        rewards = row.get("rewards") or "n/a"
        safe = row.get("safe_harbor") or "n/a"
        state = row.get("state") or "n/a"
        starts = row.get("starts_at") or "n/a"
        lines.append(
            f"| [{name}]({slug}.md) | {rewards} | {safe} | {state} | {starts} |"
        )
    bugcrowd_briefs._write_text(path, "\n".join(lines))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Postprocess local Bugcrowd full brief exports to add rendered sections and an index."
    )
    parser.add_argument(
        "--in-dir",
        default="bounty_board/bugcrowd_full",
        help="Directory containing full exports (default: bounty_board/bugcrowd_full).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write any files.",
    )
    args = parser.parse_args(argv)

    in_dir = Path(args.in_dir)
    if not in_dir.exists():
        raise SystemExit(f"Missing directory: {in_dir}")

    rows = []
    updated = 0
    for path in sorted(in_dir.glob("*.md")):
        if path.name in ("ALL.md", "INDEX.md"):
            continue
        slug = path.stem
        text = path.read_text(encoding="utf-8", errors="replace")
        brief_doc = _extract_brief_doc(text)
        if not isinstance(brief_doc, dict):
            continue

        rendered = bugcrowd_briefs._mk_rendered_brief_sections(
            slug=slug, brief_doc=brief_doc
        )
        new_text, changed = _insert_rendered_sections(text, rendered)
        if changed:
            updated += 1
            if not args.dry_run:
                bugcrowd_briefs._write_text(path, new_text)

        rows.append(_index_row_from_brief(slug, brief_doc))

    rows.sort(key=lambda row: (row.get("name") or row.get("slug") or "").lower())

    if rows and not args.dry_run:
        _write_index(in_dir / "INDEX.md", rows)

    print(f"Processed {len(rows)} engagement(s). Updated {updated} file(s).")


if __name__ == "__main__":
    main()
