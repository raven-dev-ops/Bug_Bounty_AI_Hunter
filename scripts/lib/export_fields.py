from .severity_model import format_severity_model


BASE_LABELS = ["bug-bounty", "ai-security"]
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


def _severity_label(severity):
    severity = str(severity or "info").lower()
    return f"severity/{severity}"


def _category_label(category):
    if not category or category == "unassigned":
        return None
    prefix = category.split(":")[0].strip()
    if not prefix:
        return None
    return f"owasp/{prefix.lower()}"


def _labels_for_finding(finding):
    labels = list(BASE_LABELS)
    labels.append(_severity_label(finding.get("severity")))
    severity_model = finding.get("severity_model")
    category = None
    if isinstance(severity_model, dict):
        category = severity_model.get("category")
    category_label = _category_label(category)
    if category_label:
        labels.append(category_label)
    return labels


def _github_body(finding):
    title = finding.get("title", "Untitled finding")
    severity = finding.get("severity", "unknown")
    severity_model = format_severity_model(finding.get("severity_model"))
    lines = [
        "## Summary",
        title,
        "",
        "## Severity",
        str(severity),
        "",
        "## Severity Model",
        severity_model,
    ]

    description = finding.get("description")
    if description:
        lines.extend(["", "## Description", description])
    impact = finding.get("impact")
    if impact:
        lines.extend(["", "## Impact", impact])
    remediation = finding.get("remediation")
    if remediation:
        lines.extend(["", "## Remediation", remediation])
    evidence_refs = ", ".join(str(item) for item in _list(finding.get("evidence_refs")))
    if evidence_refs:
        lines.extend(["", "## Evidence", evidence_refs])

    return "\n".join(line for line in lines if line is not None).strip()


def _jira_description(finding):
    description = finding.get("description", "")
    severity = finding.get("severity", "unknown")
    severity_model = format_severity_model(finding.get("severity_model"))
    impact = finding.get("impact", "")
    remediation = finding.get("remediation", "")
    evidence_refs = ", ".join(str(item) for item in _list(finding.get("evidence_refs")))

    lines = [
        description,
        "",
        f"Severity: {severity}",
        f"Severity model: {severity_model}",
        f"Impact: {impact}",
        f"Remediation: {remediation}",
        f"Evidence: {evidence_refs}",
    ]
    return "\n".join(line for line in lines if line)


def build_export_fields(finding):
    title = finding.get("title", "Untitled finding")
    severity = str(finding.get("severity", "info")).lower()
    labels = _labels_for_finding(finding)
    return {
        "github": {
            "title": title,
            "body": _github_body(finding),
            "labels": labels,
        },
        "jira": {
            "summary": title,
            "description": _jira_description(finding),
            "priority": SEVERITY_PRIORITY.get(severity, "Low"),
            "labels": labels,
            "issue_type": "Bug",
        },
    }


def ensure_export_fields(finding):
    if not isinstance(finding, dict):
        return finding
    export_fields = finding.get("export_fields")
    if not isinstance(export_fields, dict):
        finding["export_fields"] = build_export_fields(finding)
        return finding
    export_fields.setdefault("github", {})
    export_fields.setdefault("jira", {})
    finding["export_fields"] = export_fields
    return finding
