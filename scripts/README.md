# Scripts

Project automation and pipeline planning scripts live here.

## Requirements
- Python 3.10+
- PyYAML for YAML inputs (`pip install pyyaml`)

## Running scripts
Use `python -m scripts.<module>` to run a script from the repo root.

## Tools
- `target_profile_generate.py` - build TargetProfile from questionnaires
- `dataflow_map.py` - generate a dataflow map from a TargetProfile
- `import_scope.py` - import scope exports into a TargetProfile (generic or HackerOne)
- `discovery_assets.py` - generate candidate assets (no live checks)
- `scan_templates.py` - render template-based scan plans
- `triage_findings.py` - assign priorities and status (optional AI config)
- `external_intel.py` - enrich assets with intel records
- `notify.py` - send summary notifications (console/file by default)
- `component_runtime.py` - validate component manifests
- `pipeline_orchestrator.py` - plan or run pipeline stages
- `report_bundle.py` - generate report.md and findings.json bundles
- `export_finding_reports.py` - render per-finding markdown reports
- `export_issue_drafts.py` - create platform-specific issue drafts
- `export_jira.py` - export findings to Jira CSV
- `export_pdf.py` - export report markdown to PDF (requires pandoc)
- `findings_db.py` - manage a simple findings database
- `evidence_manager.py` - manage evidence registry entries
- `knowledge_index.py` - generate knowledge index from frontmatter
- `validate_schemas.py` - validate example files against schemas
- `bootstrap_issues.sh` - create labels and starter backlog
