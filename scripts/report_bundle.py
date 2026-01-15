import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data
from lib.template_utils import load_template, render_template


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


def _load_evidence(path):
    if not path:
        return []
    data = load_data(path)
    if isinstance(data, dict) and "evidence" in data:
        return _list(data.get("evidence"))
    if isinstance(data, dict):
        return [data]
    return _list(data)


def _scope_summary(profile):
    if not profile:
        return "No target profile provided."
    scope = profile.get("scope", {}) or {}
    in_scope = [item.get("value") for item in _list(scope.get("in_scope")) if item]
    out_scope = [item.get("value") for item in _list(scope.get("out_of_scope")) if item]
    lines = []
    if in_scope:
        lines.append("In scope: " + ", ".join(in_scope))
    if out_scope:
        lines.append("Out of scope: " + ", ".join(out_scope))
    return "\n".join(lines) if lines else "Scope not provided."


def _findings_markdown(findings):
    if not findings:
        return "No findings recorded."
    lines = []
    for finding in findings:
        title = finding.get("title", "Untitled finding")
        severity = finding.get("severity", "unknown")
        lines.append(f"### {title}")
        lines.append(f"Severity: {severity}")
        description = finding.get("description")
        if description:
            lines.append("")
            lines.append(description)
        impact = finding.get("impact")
        if impact:
            lines.append("")
            lines.append(f"Impact: {impact}")
        remediation = finding.get("remediation")
        if remediation:
            lines.append("")
            lines.append(f"Remediation: {remediation}")
        evidence = finding.get("evidence_refs")
        if evidence:
            lines.append("")
            lines.append("Evidence: " + ", ".join(_list(evidence)))
        lines.append("")
    return "\n".join(lines).rstrip()


def _evidence_summary(evidence):
    if not evidence:
        return "No evidence recorded."
    lines = []
    for item in evidence:
        item_id = item.get("id", "evidence")
        description = item.get("description", "")
        lines.append(f"- {item_id}: {description}".rstrip())
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate a report bundle.")
    parser.add_argument("--findings", required=True, help="Findings JSON/YAML.")
    parser.add_argument("--target-profile", help="TargetProfile JSON/YAML.")
    parser.add_argument("--evidence", help="Evidence JSON/YAML.")
    parser.add_argument("--output-dir", default="output/report_bundle")
    parser.add_argument(
        "--template",
        default="templates/reporting/report_bundle.md",
        help="Report template path.",
    )
    args = parser.parse_args()

    findings = _load_findings(args.findings)
    evidence = _load_evidence(args.evidence)
    profile = load_data(args.target_profile) if args.target_profile else {}

    context = {
        "program_name": profile.get("name", "Unknown Program"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope_summary": _scope_summary(profile),
        "findings_markdown": _findings_markdown(findings),
        "evidence_summary": _evidence_summary(evidence),
    }

    template_text = load_template(args.template)
    report_body = render_template(template_text, context)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.md"
    report_path.write_text(report_body + "\n", encoding="utf-8")

    dump_data(output_dir / "findings.json", findings)


if __name__ == "__main__":
    main()
