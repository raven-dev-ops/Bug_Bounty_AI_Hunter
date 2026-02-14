import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from .lib.export_fields import build_export_fields
from .lib.io_utils import dump_data, load_data


SEVERITY_ORDER = ["critical", "high", "medium", "low", "info", "unknown"]


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _load_findings(path):
    data = load_data(path)
    if isinstance(data, dict) and "findings" in data:
        return _list(data.get("findings"))
    if isinstance(data, dict):
        return [data]
    return _list(data)


def _severity_category(finding):
    severity_model = finding.get("severity_model")
    if isinstance(severity_model, dict):
        return severity_model.get("category")
    return None


def _labels_for_finding(finding):
    export_fields = finding.get("export_fields")
    if isinstance(export_fields, dict):
        github_fields = export_fields.get("github")
        if isinstance(github_fields, dict):
            labels = github_fields.get("labels")
            if labels:
                return labels
    return build_export_fields(finding).get("github", {}).get("labels", [])


def _sort_severities(items):
    order_map = {name: index for index, name in enumerate(SEVERITY_ORDER)}
    return sorted(items, key=lambda item: order_map.get(item, len(order_map)))


def build_summary(findings):
    severity_counts = {}
    review_required_count = 0
    with_evidence_count = 0
    evidence_refs_total = 0
    items = []

    for finding in findings:
        if not isinstance(finding, dict):
            continue
        severity = str(finding.get("severity") or "unknown")
        severity_key = severity.lower()
        severity_counts[severity_key] = severity_counts.get(severity_key, 0) + 1

        review_required = bool(finding.get("review_required"))
        if review_required:
            review_required_count += 1

        evidence_refs = _list(finding.get("evidence_refs"))
        if evidence_refs:
            with_evidence_count += 1
        evidence_refs_total += len(evidence_refs)

        item = {
            "id": finding.get("id"),
            "title": finding.get("title"),
            "severity": severity,
            "category": _severity_category(finding),
            "review_required": review_required,
            "evidence_count": len(evidence_refs),
            "evidence_refs": evidence_refs,
            "labels": _labels_for_finding(finding),
        }
        items.append(item)

    summary = {
        "generated_at": _timestamp(),
        "total": len(items),
        "by_severity": {
            key: severity_counts[key] for key in _sort_severities(severity_counts)
        },
        "review_required": review_required_count,
        "with_evidence": with_evidence_count,
        "evidence_refs_total": evidence_refs_total,
    }
    return summary, items


def _md_cell(value):
    if value is None:
        return ""
    text = str(value).replace("\r", " ").replace("\n", " ")
    text = " ".join(text.split())
    return text.replace("|", "\\|")


def render_markdown(summary, items):
    lines = [
        "# Findings Summary",
        "",
        f"Generated: {summary.get('generated_at')}",
        "",
        "## Overview",
        f"- Total findings: {summary.get('total', 0)}",
        f"- Review required: {summary.get('review_required', 0)}",
        f"- With evidence: {summary.get('with_evidence', 0)}",
        f"- Evidence refs total: {summary.get('evidence_refs_total', 0)}",
        "",
        "## By severity",
    ]

    by_severity = summary.get("by_severity") or {}
    if not by_severity:
        lines.append("- None")
    else:
        for key in _sort_severities(by_severity):
            lines.append(f"- {key}: {by_severity.get(key, 0)}")

    lines.extend(
        [
            "",
            "## Findings",
            "| ID | Title | Severity | Category | Evidence | Review required |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    if not items:
        lines.append("| - | - | - | - | - | - |")
    else:
        for item in items:
            evidence_count = item.get("evidence_count", 0)
            review_required = "yes" if item.get("review_required") else "no"
            lines.append(
                "| "
                + " | ".join(
                    [
                        _md_cell(item.get("id")),
                        _md_cell(item.get("title")),
                        _md_cell(item.get("severity")),
                        _md_cell(item.get("category")),
                        _md_cell(evidence_count),
                        review_required,
                    ]
                )
                + " |"
            )

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Export summary outputs for findings.")
    parser.add_argument("--findings", required=True, help="Findings JSON/YAML.")
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for summary exports.",
    )
    parser.add_argument("--output-json", help="JSON summary output path.")
    parser.add_argument("--output-csv", help="CSV summary output path.")
    parser.add_argument("--output-md", help="Markdown summary output path.")
    args = parser.parse_args()

    findings = _load_findings(args.findings)
    summary, items = build_summary(findings)

    output_dir = Path(args.output_dir)
    output_json = (
        Path(args.output_json) if args.output_json else output_dir / "summary.json"
    )
    output_csv = (
        Path(args.output_csv) if args.output_csv else output_dir / "summary.csv"
    )
    output_md = Path(args.output_md) if args.output_md else output_dir / "summary.md"

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    dump_data(
        output_json, {"schema_version": "0.1.0", "summary": summary, "findings": items}
    )

    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "title",
                "severity",
                "category",
                "review_required",
                "evidence_count",
                "evidence_refs",
                "labels",
            ],
        )
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "severity": item.get("severity"),
                    "category": item.get("category"),
                    "review_required": item.get("review_required"),
                    "evidence_count": item.get("evidence_count", 0),
                    "evidence_refs": ", ".join(
                        str(entry) for entry in item.get("evidence_refs", [])
                    ),
                    "labels": ", ".join(str(label) for label in item.get("labels", [])),
                }
            )

    output_md.write_text(render_markdown(summary, items), encoding="utf-8")


if __name__ == "__main__":
    main()
