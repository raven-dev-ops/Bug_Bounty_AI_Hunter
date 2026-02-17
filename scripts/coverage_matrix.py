import argparse
from pathlib import Path

from .lib.io_utils import load_data


SECTION_TITLES = {
    "owasp_llm_top10": "OWASP LLM Top 10",
    "mitre_atlas": "MITRE ATLAS (High-level tactics)",
    "nist_ai_rmf": "NIST AI RMF Functions",
}


def _render_sources(sources):
    if not sources:
        return ["- None", ""]
    lines = []
    for source in sources:
        name = source.get("name", "Source")
        url = source.get("url")
        if url:
            lines.append(f"- {name}: {url}")
        else:
            lines.append(f"- {name}")
    lines.append("")
    return lines


def _render_table(entries):
    lines = [
        "| ID | Name | Status | Coverage | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in entries or []:
        entry_id = str(entry.get("id") or "-")
        name = str(entry.get("name") or "-")
        status = str(entry.get("status") or "-")
        coverage_items = entry.get("coverage") or []
        if coverage_items:
            coverage = ", ".join(f"`{item}`" for item in coverage_items)
        else:
            coverage = "-"
        notes = str(entry.get("notes") or "").strip()
        issues = entry.get("issues") or []
        if issues:
            issue_text = "Issues: " + ", ".join(str(item) for item in issues)
            notes = f"{notes} {issue_text}".strip() if notes else issue_text
        lines.append(
            f"| {entry_id} | {name} | {status} | {coverage} | {notes or '-'} |"
        )
    lines.append("")
    return lines


def render_matrix(data):
    header = [
        "# Coverage Matrix",
        "",
        "High-level mapping between repo assets and common AI security taxonomies.",
        "Validate against program scope and `docs/ROE.md` before use.",
        "",
    ]

    meta_lines = []
    schema_version = data.get("schema_version")
    if schema_version:
        meta_lines.append(f"- Schema version: {schema_version}")
    updated_at = data.get("updated_at")
    if updated_at:
        meta_lines.append(f"- Updated at: {updated_at}")
    if meta_lines:
        header.append("## Metadata")
        header.extend(meta_lines)
        header.append("")

    header.append("## Sources")
    header.extend(_render_sources(data.get("sources")))

    lines = header
    coverage = data.get("coverage", {}) or {}
    for key, title in SECTION_TITLES.items():
        lines.append(f"## {title}")
        lines.append("")
        lines.extend(_render_table(coverage.get(key, [])))

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate coverage matrix.")
    parser.add_argument(
        "--input",
        default="docs/coverage_matrix.yaml",
        help="Coverage matrix YAML/JSON path.",
    )
    parser.add_argument(
        "--output",
        default="docs/COVERAGE_MATRIX.md",
        help="Output markdown path.",
    )
    args = parser.parse_args()

    data = load_data(args.input)
    content = render_matrix(data if isinstance(data, dict) else {})

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


if __name__ == "__main__":
    main()
