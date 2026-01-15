# Reporting

Reporting turns findings and evidence into report bundles and platform exports.

## Report bundle
- Script: `python -m scripts.report_bundle`
- Inputs: findings, evidence, optional TargetProfile
- Outputs: `report.md` and `findings.json`
- Template: `templates/reporting/report_bundle.md`

## Per-finding reports
- Script: `python -m scripts.export_finding_reports`
- Template: `templates/reporting/finding.md`

## Issue and platform exports
- Script: `python -m scripts.export_issue_drafts`
- Templates: `templates/platforms/` (GitHub, HackerOne, Bugcrowd)
- Jira CSV export: `python -m scripts.export_jira`

## PDF export
- Script: `python -m scripts.export_pdf`
- Requires `pandoc` or `wkhtmltopdf`

## Evidence registry
- Script: `python -m scripts.evidence_manager`
- Registry: `evidence/registry.json`

## Findings database
- Script: `python -m scripts.findings_db`
- Database: `data/findings_db.json`
