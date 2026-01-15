import argparse
import re
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import load_data
from lib.template_utils import load_template, render_template


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _safe_filename(value):
    value = value or "finding"
    value = value.lower().strip().replace(" ", "-")
    return re.sub(r"[^a-z0-9._-]+", "-", value)


def _load_findings(path):
    data = load_data(path)
    if isinstance(data, dict) and "findings" in data:
        return _list(data.get("findings"))
    if isinstance(data, dict):
        return [data]
    return _list(data)


def _load_evidence(path):
    if not path:
        return {}
    data = load_data(path)
    if isinstance(data, dict) and "evidence" in data:
        items = _list(data.get("evidence"))
    elif isinstance(data, dict):
        items = [data]
    else:
        items = _list(data)
    return {item.get("id"): item for item in items if isinstance(item, dict)}


def main():
    parser = argparse.ArgumentParser(description="Export per-finding reports.")
    parser.add_argument("--findings", required=True, help="Findings JSON/YAML.")
    parser.add_argument("--evidence", help="Evidence JSON/YAML.")
    parser.add_argument("--output-dir", default="output/finding_reports")
    parser.add_argument(
        "--template",
        default="templates/reporting/finding.md",
        help="Finding template path.",
    )
    args = parser.parse_args()

    findings = _load_findings(args.findings)
    evidence_map = _load_evidence(args.evidence)
    template_text = load_template(args.template)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, finding in enumerate(findings, 1):
        finding_id = finding.get("id") or f"finding-{index:03d}"
        evidence_refs = _list(finding.get("evidence_refs"))
        evidence_lines = []
        for ref in evidence_refs:
            entry = evidence_map.get(ref, {})
            description = entry.get("description", "")
            if description:
                evidence_lines.append(f"{ref}: {description}")
            else:
                evidence_lines.append(ref)

        context = {
            "id": finding_id,
            "title": finding.get("title", "Untitled finding"),
            "severity": finding.get("severity", "unknown"),
            "description": finding.get("description", ""),
            "impact": finding.get("impact", ""),
            "remediation": finding.get("remediation", ""),
            "evidence_refs": "\n".join(f"- {line}" for line in evidence_lines)
            or "None",
        }

        content = render_template(template_text, context)
        filename = _safe_filename(finding_id) + ".md"
        (output_dir / filename).write_text(content + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
