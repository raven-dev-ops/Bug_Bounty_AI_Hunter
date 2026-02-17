# Reporting Templates

These templates are used by reporting/export scripts to render Markdown output
files. They are planning and documentation helpers only. They are not
authorization to test anything.

Placeholders use Python `str.format` keys like `{program_name}`. Unknown keys
are left as `{key}` in the rendered output.

## Files
- `report_bundle.md`
  - Used by: `python -m scripts.report_bundle`
  - Output: a single `report.md` bundle with findings, evidence summary, and
    reproducibility references.
- `finding.md`
  - Used by: `python -m scripts.export_finding_reports`
  - Output: one Markdown file per finding.
- `compliance_checklist.md`
  - Used by: `python -m scripts.report_bundle`
  - Output: a checklist inserted into the report bundle.
- `program_brief.md`
  - Used by: `python -m scripts.program_brief` and `python -m scripts.catalog_pdf`
  - Output: one brief per program plus optional inclusion in the catalog.
- `master_catalog.md`
  - Used by: `python -m scripts.catalog_pdf`
  - Output: a Markdown catalog (optionally rendered to PDF outside git).
- `standard/`
  - Manual-only templates for a fuller report pack.

## Safety notes
- Do not include exploit code or payloads.
- Do not include real user data. Use synthetic canaries where needed.
- Follow `docs/ROE.md` and platform rules.

