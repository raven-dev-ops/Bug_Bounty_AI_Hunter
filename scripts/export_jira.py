import argparse
import csv
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import load_data


SEVERITY_PRIORITY = {
    "critical": "Highest",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "info": "Lowest",
}


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


def _priority_for_finding(finding):
    severity = str(finding.get("severity", "info")).lower()
    return SEVERITY_PRIORITY.get(severity, "Low")


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
            description_lines = [
                finding.get("description", ""),
                "",
                f"Impact: {finding.get('impact', '')}",
                f"Remediation: {finding.get('remediation', '')}",
                f"Evidence: {', '.join(_list(finding.get('evidence_refs')))}",
            ]
            writer.writerow(
                {
                    "Summary": finding.get("title", "Untitled finding"),
                    "Description": "\n".join(line for line in description_lines if line),
                    "Priority": _priority_for_finding(finding),
                    "Labels": "bug-bounty,ai-security",
                }
            )


if __name__ == "__main__":
    main()
