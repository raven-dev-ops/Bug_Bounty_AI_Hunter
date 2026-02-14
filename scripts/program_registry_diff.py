import argparse
import json
from datetime import datetime, timezone

from .lib.catalog_guardrails import ensure_catalog_path
from .lib.io_utils import dump_data, load_data


HIGHLIGHT_FIELDS = {"scope", "rewards", "restrictions"}
DIFF_FIELDS = [
    "name",
    "platform",
    "handle",
    "policy_url",
    "program_type",
    "rewards",
    "scope",
    "restrictions",
    "safe_harbor",
    "attribution",
]


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _value_key(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    return str(value)


def _program_key(program):
    return program.get("id") or program.get("name")


def _index_programs(data):
    programs = []
    if isinstance(data, dict):
        programs = data.get("programs") or []
    elif isinstance(data, list):
        programs = data
    index = {}
    for program in programs:
        if not isinstance(program, dict):
            continue
        key = _program_key(program)
        if not key:
            continue
        index[key] = program
    return index


def _program_ref(program, key):
    return {
        "id": key,
        "name": program.get("name") if isinstance(program, dict) else None,
    }


def _diff_program(before, after):
    changes = []
    highlighted = []
    for field in DIFF_FIELDS:
        before_value = before.get(field)
        after_value = after.get(field)
        if _value_key(before_value) == _value_key(after_value):
            continue
        changes.append({"field": field, "before": before_value, "after": after_value})
        if field in HIGHLIGHT_FIELDS:
            highlighted.append(field)
    return changes, sorted(set(highlighted))


def compute_diff(before_data, after_data, before_source=None, after_source=None):
    before_index = _index_programs(before_data)
    after_index = _index_programs(after_data)

    before_keys = set(before_index)
    after_keys = set(after_index)

    added_keys = sorted(after_keys - before_keys)
    removed_keys = sorted(before_keys - after_keys)
    common_keys = sorted(before_keys & after_keys)

    added = [_program_ref(after_index[key], key) for key in added_keys]
    removed = [_program_ref(before_index[key], key) for key in removed_keys]

    changed = []
    for key in common_keys:
        before_program = before_index[key]
        after_program = after_index[key]
        changes, highlighted = _diff_program(before_program, after_program)
        if not changes:
            continue
        changed.append(
            {
                "id": key,
                "name": after_program.get("name") or before_program.get("name"),
                "fields": changes,
                "highlighted_fields": highlighted,
            }
        )

    output = {
        "schema_version": "0.1.0",
        "generated_at": _timestamp(),
        "before": {
            "source": before_source,
            "program_count": len(before_index),
        },
        "after": {
            "source": after_source,
            "program_count": len(after_index),
        },
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
        },
        "added": added,
        "removed": removed,
        "changed": changed,
    }
    return output


def _format_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    if value is None:
        return "null"
    return str(value)


def render_markdown(diff):
    lines = [
        "# Program Registry Change Log",
        "",
        f"Generated: {diff.get('generated_at')}",
        "",
        "## Summary",
        f"- Added: {diff.get('summary', {}).get('added', 0)}",
        f"- Removed: {diff.get('summary', {}).get('removed', 0)}",
        f"- Changed: {diff.get('summary', {}).get('changed', 0)}",
        "",
    ]

    added = diff.get("added") or []
    removed = diff.get("removed") or []
    changed = diff.get("changed") or []

    lines.append(f"## Added ({len(added)})")
    if not added:
        lines.append("- None")
    else:
        for item in added:
            name = item.get("name") or "Unnamed Program"
            lines.append(f"- {name} ({item.get('id')})")
    lines.append("")

    lines.append(f"## Removed ({len(removed)})")
    if not removed:
        lines.append("- None")
    else:
        for item in removed:
            name = item.get("name") or "Unnamed Program"
            lines.append(f"- {name} ({item.get('id')})")
    lines.append("")

    lines.append(f"## Changed ({len(changed)})")
    if not changed:
        lines.append("- None")
    else:
        for item in changed:
            name = item.get("name") or "Unnamed Program"
            lines.append(f"### {name} ({item.get('id')})")
            highlights = set(item.get("highlighted_fields") or [])
            for change in item.get("fields", []):
                field = change.get("field")
                before = _format_value(change.get("before"))
                after = _format_value(change.get("after"))
                prefix = "[highlight] " if field in highlights else ""
                lines.append(f"- {prefix}{field}: {before} -> {after}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate diff outputs for program registry snapshots."
    )
    parser.add_argument("--before", required=True, help="Before registry JSON/YAML.")
    parser.add_argument("--after", required=True, help="After registry JSON/YAML.")
    parser.add_argument(
        "--output-json",
        default="data/program_registry_diff.json",
        help="Output JSON diff path.",
    )
    parser.add_argument(
        "--output-md",
        default="data/program_registry_diff.md",
        help="Output Markdown diff path.",
    )
    args = parser.parse_args()

    before_data = load_data(args.before)
    after_data = load_data(args.after)
    diff = compute_diff(before_data, after_data, args.before, args.after)

    if args.output_json:
        ensure_catalog_path(args.output_json, label="Program registry diff output")
        dump_data(args.output_json, diff)
    if args.output_md:
        ensure_catalog_path(args.output_md, label="Program registry diff output")
        markdown = render_markdown(diff)
        with open(args.output_md, "w", encoding="utf-8") as handle:
            handle.write(markdown)


if __name__ == "__main__":
    main()
