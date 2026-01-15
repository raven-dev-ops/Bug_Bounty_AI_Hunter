import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform

from .lib.export_fields import ensure_export_fields
from .lib.io_utils import dump_data, load_data
from .lib.severity_model import ensure_severity_model, format_severity_model
from .lib.template_utils import load_template, render_template


REVIEW_REQUIRED_NOTE = "This output is generated; verify details before submission."


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
        severity_model = format_severity_model(finding.get("severity_model"))
        lines.append(f"### {title}")
        lines.append(f"Severity: {severity}")
        lines.append(f"Severity model: {severity_model}")
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


def _evidence_to_findings(findings):
    mapping = {}
    for finding in findings:
        finding_id = finding.get("id")
        if not finding_id:
            continue
        for ref in _list(finding.get("evidence_refs")):
            mapping.setdefault(ref, set()).add(finding_id)
    return mapping


def _attachments_manifest(findings, evidence, output_dir):
    attachments = [
        {
            "id": "attachment-001",
            "path": "report.md",
            "role": "report",
            "description": "Report bundle markdown.",
            "content_type": "text/markdown",
        },
        {
            "id": "attachment-002",
            "path": "findings.json",
            "role": "findings",
            "description": "Structured findings output.",
            "content_type": "application/json",
        },
        {
            "id": "attachment-003",
            "path": "reproducibility_pack.json",
            "role": "reproducibility",
            "description": "Reproducibility metadata pack.",
            "content_type": "application/json",
        },
    ]

    evidence_map = _evidence_to_findings(findings)
    for item in evidence:
        if not isinstance(item, dict):
            continue
        evidence_id = item.get("id")
        description = item.get("description", "")
        artifacts = _list(item.get("artifacts"))
        for artifact in artifacts:
            entry = {
                "id": f"attachment-{len(attachments) + 1:03d}",
                "path": artifact,
                "role": "evidence",
                "description": description,
                "content_type": "application/octet-stream",
            }
            if evidence_id:
                entry["evidence_id"] = evidence_id
                finding_ids = evidence_map.get(evidence_id)
                if finding_ids:
                    entry["finding_ids"] = sorted(finding_ids)
            attachments.append(entry)

    return {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bundle_root": str(output_dir),
        "attachments": attachments,
    }


def _environment_metadata():
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }


def _load_repro_steps(path):
    if not path:
        return []
    data = load_data(path)
    if isinstance(data, dict) and "steps" in data:
        steps = data.get("steps")
    else:
        steps = data
    if not isinstance(steps, list):
        raise SystemExit("Repro steps must be a list of strings.")
    return [str(step) for step in steps if step]


def _evidence_hashes(evidence):
    hashes = []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        evidence_id = item.get("id")
        for artifact in _list(item.get("artifacts")):
            entry = {
                "path": artifact,
                "status": "pending",
            }
            if evidence_id:
                entry["evidence_id"] = evidence_id
            hashes.append(entry)
    return hashes


def _reproducibility_pack(steps, evidence, output_dir):
    return {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bundle_root": str(output_dir),
        "environment": _environment_metadata(),
        "steps": steps,
        "evidence_hashes": _evidence_hashes(evidence),
        "notes": "Populate evidence hashes when available.",
    }


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
    parser.add_argument(
        "--repro-steps",
        help="JSON/YAML path with reproducibility steps list.",
    )
    args = parser.parse_args()

    findings = _load_findings(args.findings)
    evidence = _load_evidence(args.evidence)
    profile = load_data(args.target_profile) if args.target_profile else {}
    repro_steps = _load_repro_steps(args.repro_steps)

    for finding in findings:
        if isinstance(finding, dict):
            ensure_severity_model(finding)
            ensure_export_fields(finding)
            finding.setdefault("review_required", True)

    context = {
        "program_name": profile.get("name", "Unknown Program"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope_summary": _scope_summary(profile),
        "findings_markdown": _findings_markdown(findings),
        "evidence_summary": _evidence_summary(evidence),
        "review_required_note": REVIEW_REQUIRED_NOTE,
        "attachments_manifest": "attachments_manifest.json",
        "reproducibility_pack": "reproducibility_pack.json",
    }

    template_text = load_template(args.template)
    report_body = render_template(template_text, context)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.md"
    report_path.write_text(report_body + "\n", encoding="utf-8")

    dump_data(output_dir / "findings.json", findings)
    manifest = _attachments_manifest(findings, evidence, output_dir)
    dump_data(output_dir / "attachments_manifest.json", manifest)
    repro_pack = _reproducibility_pack(repro_steps, evidence, output_dir)
    dump_data(output_dir / "reproducibility_pack.json", repro_pack)


if __name__ == "__main__":
    main()
