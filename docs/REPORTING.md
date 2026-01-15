# Reporting

Reporting turns findings and evidence into report bundles and platform exports.

## Report bundle
- Script: `python -m scripts.report_bundle`
- Inputs: findings, evidence, optional TargetProfile
- Outputs: `report.md`, `findings.json` (includes `severity_model` and `export_fields`),
  `attachments_manifest.json`, and `reproducibility_pack.json`
- Template: `templates/reporting/report_bundle.md`
- Note: outputs include a review-required marker for human validation.

## Attachments manifest
- Output: `attachments_manifest.json`
- Schema: `schemas/attachments_manifest.schema.json`
- Includes report bundle files and referenced evidence artifacts.

## Reproducibility pack
- Output: `reproducibility_pack.json`
- Schema: `schemas/reproducibility_pack.schema.json`
- Provide steps via `--repro-steps` (JSON/YAML list).
- Example steps file: `examples/repro_steps.json`.

## Per-finding reports
- Script: `python -m scripts.export_finding_reports`
- Template: `templates/reporting/finding.md`

## Issue and platform exports
- Script: `python -m scripts.export_issue_drafts`
- Templates: `templates/platforms/` (GitHub, HackerOne, Bugcrowd)
- Jira CSV export: `python -m scripts.export_jira`
- Note: issue drafts include a review-required banner by default.
- Tip: pass `--attachments-manifest` to reference the manifest in exports.

## PDF export
- Script: `python -m scripts.export_pdf`
- Requires `pandoc` or `wkhtmltopdf`

## Evidence registry
- Script: `python -m scripts.evidence_manager`
- Registry: `evidence/registry.json`
- Example output: `examples/evidence_registry_output.json`
- Evidence entries support `hashes` and `custody` metadata for chain-of-custody.
- Use `add --hash-artifacts --hash-algorithm sha256` to compute artifact hashes.

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
