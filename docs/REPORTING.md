# Reporting

Reporting turns findings and evidence into report bundles and platform exports.

## Report bundle
- Script: `scripts/report_bundle.py`
- Inputs: findings, evidence, optional TargetProfile
- Outputs: `report.md` and `findings.json`
- Template: `templates/reporting/report_bundle.md`

## Per-finding reports
- Script: `scripts/export_finding_reports.py`
- Template: `templates/reporting/finding.md`

## Issue and platform exports
- Script: `scripts/export_issue_drafts.py`
- Templates: `templates/platforms/` (GitHub, HackerOne, Bugcrowd)
- Jira CSV export: `scripts/export_jira.py`

## PDF export
- Script: `scripts/export_pdf.py`
- Requires `pandoc` or `wkhtmltopdf`

## Evidence registry
- Script: `scripts/evidence_manager.py`
- Registry: `evidence/registry.json`

## Findings database
- Script: `scripts/findings_db.py`
- Database: `data/findings_db.json`
