import argparse
import re
from pathlib import Path

from .lib.io_utils import load_data
from .lib.severity_model import format_severity_model
from .lib.template_utils import load_template, render_template


REVIEW_REQUIRED_NOTE = "This output is generated; verify details before submission."


PLATFORM_TEMPLATES = {
    "github": "templates/platforms/github_issue.md",
    "hackerone": "templates/platforms/hackerone.md",
    "bugcrowd": "templates/platforms/bugcrowd.md",
}


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _safe_filename(value):
    value = value or "issue"
    value = value.lower().strip().replace(" ", "-")
    return re.sub(r"[^a-z0-9._-]+", "-", value)


def _load_findings(path):
    data = load_data(path)
    if isinstance(data, dict) and "findings" in data:
        return _list(data.get("findings"))
    if isinstance(data, dict):
        return [data]
    return _list(data)


def _scope_summary(profile):
    if not profile:
        return "Scope not provided."
    scope = profile.get("scope", {}) or {}
    in_scope = [item.get("value") for item in _list(scope.get("in_scope")) if item]
    return ", ".join(in_scope) if in_scope else "Scope not provided."


def main():
    parser = argparse.ArgumentParser(description="Export issue drafts from findings.")
    parser.add_argument("--findings", required=True, help="Findings JSON/YAML.")
    parser.add_argument("--target-profile", help="TargetProfile JSON/YAML.")
    parser.add_argument(
        "--platform",
        default="github",
        choices=sorted(PLATFORM_TEMPLATES.keys()),
    )
    parser.add_argument("--output-dir", default="output/issue_drafts")
    parser.add_argument("--template", help="Override template path.")
    args = parser.parse_args()

    findings = _load_findings(args.findings)
    profile = load_data(args.target_profile) if args.target_profile else {}

    template_path = args.template or PLATFORM_TEMPLATES[args.platform]
    template_text = load_template(template_path)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scope_summary = _scope_summary(profile)
    for index, finding in enumerate(findings, 1):
        finding_id = finding.get("id") or f"finding-{index:03d}"
        context = {
            "id": finding_id,
            "title": finding.get("title", "Untitled finding"),
            "severity": finding.get("severity", "unknown"),
            "severity_model_summary": format_severity_model(
                finding.get("severity_model")
            ),
            "description": finding.get("description", ""),
            "impact": finding.get("impact", ""),
            "remediation": finding.get("remediation", ""),
            "evidence_refs": ", ".join(_list(finding.get("evidence_refs"))),
            "scope_summary": scope_summary,
            "review_required_note": REVIEW_REQUIRED_NOTE,
        }
        content = render_template(template_text, context)
        filename = _safe_filename(finding_id) + ".md"
        (output_dir / filename).write_text(content + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
