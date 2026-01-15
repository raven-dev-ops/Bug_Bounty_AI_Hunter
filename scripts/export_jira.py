import argparse
import csv
from pathlib import Path

from .lib.export_fields import build_export_fields
from .lib.io_utils import load_data


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


def _jira_fields_for_finding(finding):
    export_fields = finding.get("export_fields")
    if isinstance(export_fields, dict):
        jira_fields = export_fields.get("jira")
        if isinstance(jira_fields, dict):
            return jira_fields
    return build_export_fields(finding).get("jira", {})


def main():
    parser = argparse.ArgumentParser(description="Export findings to Jira CSV.")
    parser.add_argument("--findings", required=True, help="Findings JSON/YAML.")
    parser.add_argument("--output", default="output/jira_issues.csv")
    args = parser.parse_args()

    findings = _load_findings(args.findings)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["Summary", "Description", "Priority", "Labels"]
        )
        writer.writeheader()
        for finding in findings:
            jira_fields = _jira_fields_for_finding(finding)
            description_lines = [
                finding.get("description", ""),
                "",
                f"Impact: {finding.get('impact', '')}",
                f"Remediation: {finding.get('remediation', '')}",
                f"Evidence: {', '.join(_list(finding.get('evidence_refs')))}",
            ]
            description = jira_fields.get("description") or "\n".join(
                line for line in description_lines if line
            )
            labels = jira_fields.get("labels") or ["bug-bounty", "ai-security"]
            writer.writerow(
                {
                    "Summary": jira_fields.get("summary")
                    or finding.get("title", "Untitled finding"),
                    "Description": description,
                    "Priority": jira_fields.get("priority", "Low"),
                    "Labels": ", ".join(str(label) for label in labels),
                }
            )


if __name__ == "__main__":
    main()
