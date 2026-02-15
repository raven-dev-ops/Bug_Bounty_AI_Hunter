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
- `threat_model_generate.py` - generate a threat model from a TargetProfile
- `import_scope.py` - import scope exports into a TargetProfile (generic or HackerOne)
- `discovery_assets.py` - generate candidate assets (no live checks)
- `scan_templates.py` - render template-based scan plans
- `triage_findings.py` - assign priorities and status (optional AI config)
- `external_intel.py` - enrich assets with intel records
- `notify.py` - send summary notifications (console/file by default)
- `component_runtime.py` - validate component manifests
- `component_registry_index.py` - generate the component registry index
- `pipeline_orchestrator.py` - plan or run pipeline stages
- `report_bundle.py` - generate report bundle outputs (report.md, compliance checklist, findings, attachments manifest, reproducibility pack)
- `report_completeness_review.py` - review report bundles for missing content (optional AI)
- `export_finding_reports.py` - render per-finding markdown reports
- `export_issue_drafts.py` - create platform-specific issue drafts
- `export_jira.py` - export findings to Jira CSV
- `export_summary.py` - export findings summary to JSON, CSV, and Markdown
- `export_pdf.py` - export report markdown to PDF (requires pandoc)
- `program_brief.py` - generate per-program brief markdown (optional PDF)
- `catalog_pdf.py` - generate master catalog markdown (optional PDF)
- `pdf_golden_update.py` - regenerate PDF golden hashes for tests
- `findings_db.py` - manage a simple findings database
- `evidence_manager.py` - manage evidence registry entries
- `tool_run_log.py` - generate tool run metadata logs
- `redact_evidence.py` - redact sensitive data from evidence files
- `program_registry.py` - merge program records into a registry
- `program_registry_diff.py` - diff program registry snapshots
- `program_registry_store.py` - manage local program registry storage
- `catalog_build.py` - build the public program registry from connectors (writes audit logs)
- `program_scoring.py` - score programs and assign difficulty buckets
- `case_study_selection.py` - shortlist case-study candidates with reasons
- `suggested_approach.py` - generate planning-only approaches by scoring bucket
- `program_relevance.py` - classify AI/LLM relevance using metadata keywords
- `program_provenance.py` - score provenance quality and freshness
- `scoring_calibration.py` - compare scoring output against labeled calibration data
- `knowledge_index.py` - generate knowledge index from frontmatter
- `coverage_matrix.py` - generate coverage matrix docs from YAML
- `knowledge_lint.py` - lint knowledge frontmatter fields
- `golden_examples.py` - re-emit JSON examples deterministically
- `migrate.py` - migrate artifacts between schema versions
- `component_bootstrap.py` - scaffold a component repo skeleton
- `demo_runner.py` - run the example pipeline end-to-end
- `validate_schemas.py` - validate example files against schemas
- `validate_markdown_links.py` - validate local Markdown links
- `bugcrowd_board.py` - generate a planning-only Bugcrowd bounty board from public listings (writes Markdown under `bounty_board/`)
- `bootstrap_issues.sh` - create labels and starter backlog
- `connectors/` - ingestion connector framework and source implementations
