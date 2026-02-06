# Reporting

Reporting turns findings and evidence into report bundles and platform exports.

## Report bundle
- Script: `python -m scripts.report_bundle`
- Inputs: findings, evidence, optional TargetProfile
- Outputs: `report.md`, `compliance_checklist.md`, `findings.json` (includes
  `severity_model` and `export_fields`), `attachments_manifest.json`, and
  `reproducibility_pack.json`
- Templates: `templates/reporting/report_bundle.md` and
  `templates/reporting/compliance_checklist.md`
- Note: the compliance checklist content is embedded in `report.md` for PDF exports.
- Standard template pack: `templates/reporting/standard/`
- Note: outputs include a review-required marker for human validation.
- CLI wrapper: `python -m bbhai report` supports `--repro-steps` and
  `--attachments-manifest`.

## Attachments manifest
- Output: `attachments_manifest.json`
- Schema: `schemas/attachments_manifest.schema.json`
- Includes report bundle files and referenced evidence artifacts.

## Reproducibility pack
- Output: `reproducibility_pack.json`
- Schema: `schemas/reproducibility_pack.schema.json`
- Provide steps via `--repro-steps` (JSON/YAML list).
- Steps schema: `schemas/repro_steps.schema.json`.
- Example steps file: `examples/repro_steps.json`.

## Per-finding reports
- Script: `python -m scripts.export_finding_reports`
- Template: `templates/reporting/finding.md`

## Report completeness review (optional)
- Script: `python -m scripts.report_completeness_review`
- Output: `data/report_completeness_review.json`
- Schema: `schemas/report_completeness_review.schema.json`
- Use `--ai-enabled` only with approved data handling.

## Program briefs and catalog
- Program brief script: `python -m scripts.program_brief`
- Master catalog script: `python -m scripts.catalog_pdf`
- Templates: `templates/reporting/program_brief.md`, `templates/reporting/master_catalog.md`
- Use `--pdf` flags to render PDFs locally (not committed).

## Issue and platform exports
- Script: `python -m scripts.export_issue_drafts`
- Templates: `templates/platforms/` (GitHub, HackerOne, Bugcrowd)
- Jira CSV export: `python -m scripts.export_jira`
- Summary export (JSON/CSV/Markdown): `python -m scripts.export_summary`
- CLI wrapper: `python -m bbhai export summary --findings <path>`
- Outputs: `summary.json`, `summary.csv`, `summary.md`.
- Note: issue drafts include a review-required banner by default.
- Tip: pass `--attachments-manifest` to reference the manifest in exports.

## Suggested approach (planning-only)
- Script: `python -m scripts.suggested_approach`
- Input: `data/program_scoring_output.json`
- Output: `data/suggested_approach_output.json`
- Schema: `schemas/suggested_approach.schema.json`

## PDF export
- Script: `python -m scripts.export_pdf`
- Requires `pandoc` or `wkhtmltopdf`
- Example source: `examples/outputs/high_quality_report.md` (render locally)

## Evidence registry
- Script: `python -m scripts.evidence_manager`
- Registry: `evidence/registry.json`
- Example output: `examples/evidence_registry_output.json`
- Evidence entries support `hashes` and `custody` metadata for chain-of-custody.
- Use `add --hash-artifacts --hash-algorithm sha256` to compute artifact hashes.
- Evidence log template and redaction guidance: `docs/EVIDENCE_LOG.md` and
  `docs/REDACTION_GUIDE.md`.

## Tool run logs
- Script: `python -m scripts.tool_run_log`
- Schema: `schemas/tool_run.schema.json`
- Example: `examples/tool_runs/tool_run_example.json`

## Evidence encryption at rest (optional)
- Use full-disk encryption (BitLocker, FileVault, LUKS) for evidence storage.
- Consider encrypted containers (VeraCrypt) for scoped engagements.
- For per-file encryption, use age or GPG and store keys outside the repo.
- Document key custody and access restrictions in evidence notes.

## Notifications
- Script: `python -m scripts.notify`
- Example output: `examples/notification_output.json`
- Guide: `docs/NOTIFICATIONS.md`

## Findings database
- Script: `python -m scripts.findings_db`
- Database: `data/findings_db.json`
- Example output: `examples/findings_db_output.json`
