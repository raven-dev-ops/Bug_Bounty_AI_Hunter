# Bug_Bounty_Hunter_AI

Docs-first hub for AI bug bounty workflows with schemas, checklists, pipeline
scripts, and component integration guidance for authorized testing of AI-enabled
applications (RAG, embeddings, fine-tuning, tool-using agents, and logging).

This project is informational and operational guidance only. It is not legal
advice. Only test systems where you have explicit authorization.

## Docs
- `ROADMAP.md`
- `BUGCROWD.md`
- `GUIDE.md`
- `CONTEXT.md`
- `dashboard.html` (local repo overview)
- `docs/PROJECT_OUTLINE.md`
- `docs/ROE.md`
- `docs/BUG_BOUNTY_STARTER_WORKFLOW.md`
- `docs/BUGCROWD.md` (MkDocs copy of `BUGCROWD.md`)
- `docs/GUIDE.md` (MkDocs copy of `GUIDE.md`)
- `docs/PROJECT_MANAGEMENT.md`
- `docs/TARGET_PROFILE.md`
- `docs/THREAT_MODEL.md`
- `docs/LLM_THREAT_MODEL.md`
- `docs/PROGRAM_REGISTRY.md`
- `docs/INGESTION_FEASIBILITY.md`
- `docs/KNOWLEDGE_FORMAT.md`
- `docs/KNOWLEDGE_TAGS.md`
- `knowledge/INDEX.md`
- `docs/KNOWLEDGE_INDEX.md` (MkDocs-published knowledge index)
- `docs/knowledge/` (MkDocs-published knowledge pages)
- `docs/ARCHITECTURE.md`
- `docs/PIPELINE.md`
- `docs/TRIAGE.md`
- `docs/SEVERITY_MODEL.md`
- `docs/INTEL.md`
- `docs/TOOLS.md`
- `docs/ENVIRONMENT.md`
- `docs/COMPONENTS.md`
- `docs/COMPONENT_CONTRACT.md`
- `docs/COMPONENT_MANIFEST.md`
- `docs/REPORTING.md`
- `docs/PUBLIC_ONLY_MODE.md`
- `docs/EVIDENCE_LOG.md`
- `docs/TOOLS_POLICY.md`
- `docs/SAFE_DEFAULTS.md`
- `docs/PIPELINE_GUARDRAILS.md`
- `docs/THREAT_MODELING_METHOD.md`
- `docs/SCOPING_GUIDE.md`
- `docs/OPERATIONS.md`
- `docs/REDACTION_GUIDE.md`
- `docs/REPORTING_EXAMPLES.md`
- `docs/GOVERNANCE_SECURITY.md`
- `docs/RISK_ASSESSMENT.md`
- `docs/CHANGELOG_POLICY.md`
- `docs/IMPROVEMENT_TASKS.md`
- `docs/CASE_STUDY_SELECTION.md`
- `docs/SCORING.md`
- `docs/NOTIFICATIONS.md`
- `docs/MODULE_BOUNDARIES.md`
- `docs/HACK_TYPES.md`
- `docs/COVERAGE_MATRIX.md`
- `docs/TESTING.md`
- `docs/RELEASE_PLAN.md`
- `docs/RELEASE_NOTES_TEMPLATE.md`
- `docs/RELEASE_CHECKLIST.md`
- `knowledge/checklists/bug-bounty-starter-workflow.md`

## Choose Your Path
- `docs/paths/bug-bounty-hunter.md`
- `docs/paths/appsec-review.md`
- `docs/paths/threat-model-only.md`

## Local Dashboard
- Preferred: run `python -m http.server 8000` and open `http://localhost:8000/dashboard.html`.
- If you open `dashboard.html` via `file://`, use "Import repo folder" (Chrome/Edge) to load data.
- Bounties include a Level (P0-P4) lens/filter and a "Most Wanted" carousel (official icons when sponsor websites are set in Sponsor Profiles).

## Repository layout
- `dashboard.html` and `dashboard/` - local interactive repo overview (static HTML/CSS/JS)
- `docs/` - architecture, rules, and planning docs
- `bounty_board/` - planning-only bounty board markdown (public metadata only). Bugcrowd boards: `bounty_board/bugcrowd/` and `bounty_board/bugcrowd_vdp/`. Full brief exports are generated with `python -m scripts.bugcrowd_briefs` (gitignored under `bounty_board/bugcrowd_full/`).
- `schemas/` - data model schemas
- `components/` - component repos (submodules or subtrees)
- `knowledge/` - sources, cards, and checklists (publish to `docs/knowledge/` with `python -m scripts.publish_knowledge_docs`)
- `examples/` - sample profiles and outputs
- `data/` - local tracking data and registries
- `evidence/` - evidence registry entries
- `templates/` - scan planning, reporting, platform export, and engagement workspace templates
- `scripts/` - bootstrap and automation scripts
- `labs/` - synthetic lab scaffolding
- `tests/` - unit and validation tests

## Install
```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```
Editable installs:
```bash
python -m pip install -e .
python -m pip install -e .[dev]
```

## How To Use
- Start with `docs/ROE.md` and confirm written authorization.
- Create a TargetProfile from the questionnaire or a minimal YAML in `examples/`.
- Run the pipeline in plan mode (`docs/PIPELINE.md`) to generate artifacts.
- Review outputs and produce report bundles or issue drafts (`docs/REPORTING.md`).
- Report bundles emit `report.md`, `compliance_checklist.md`, `findings.json`,
  `attachments_manifest.json`, and `reproducibility_pack.json`.
- Use `bbhai report --repro-steps <path>` and `--attachments-manifest` to enrich
  report bundles and issue drafts with reproducibility metadata.
- Start from `examples/repro_steps.json` when authoring repro steps.
- Configure optional integrations via `docs/ENVIRONMENT.md` and
  `docs/NOTIFICATIONS.md`.

## Quick Start
```bash
python -m bbhai init --workspace output
python -m bbhai profile --workspace output
python -m bbhai model --workspace output
python -m bbhai plan --workspace output
python -m bbhai report --workspace output --findings examples/outputs/findings.json
```

## Unified CLI
```bash
python -m bbhai --help
python -m bbhai profile --input examples/target_profile_questionnaire.yaml --output output/target_profile.json
python -m bbhai plan --config examples/pipeline_config.yaml
python -m bbhai catalog build --public-only --output data/program_registry.json
python -m bbhai catalog score --public-only --output data/program_scoring_output.json
python -m bbhai export summary --findings examples/outputs/findings.json
python -m bbhai migrate --input components/bbhai-review-sample/component_manifest.yaml --from 0.0.0 --to 0.1.0 --dry-run
```

## Console Script
```bash
python -m pip install -e .
bbhai --help
bbhai --version
bbhai profile --input examples/target_profile_questionnaire.yaml --output output/target_profile.json
```

## Module Usage
```bash
python -m scripts.init_engagement_workspace --platform bugcrowd --slug moovit-mbb-og
python -m scripts.target_profile_generate --input examples/target_profile_questionnaire.yaml --output output/target_profile.json
python -m scripts.dataflow_map --target-profile output/target_profile.json --output output/dataflow_map.json
python -m scripts.threat_model_generate --target-profile output/target_profile.json --output output/threat_model.json
python -m scripts.pipeline_orchestrator --config examples/pipeline_config.yaml --mode plan
python -m scripts.report_bundle --findings examples/outputs/findings.json --target-profile examples/target_profile_minimal.yaml --output-dir output/report_bundle
python -m scripts.report_completeness_review --report output/report_bundle/report.md --findings output/report_bundle/findings.json
python -m scripts.export_issue_drafts --findings examples/outputs/findings.json --output-dir output/issue_drafts
python -m scripts.export_summary --findings examples/outputs/findings.json --output-dir output/summary
python -m scripts.catalog_build --public-only --output data/program_registry.json
python -m scripts.program_scoring --input data/program_registry.json --output data/program_scoring_output.json --public-only
python -m scripts.case_study_selection --registry data/program_registry.json --scoring data/program_scoring_output.json
python -m scripts.suggested_approach --input data/program_scoring_output.json --output data/suggested_approach_output.json
python -m scripts.program_relevance --input data/program_registry.json --output data/program_relevance_output.json
python -m scripts.program_provenance --input data/program_registry.json --output data/program_provenance_output.json
python -m scripts.scoring_calibration --scoring data/program_scoring_output.json --labels examples/scoring_calibration_dataset.json --output data/scoring_calibration_report.json
python -m scripts.program_brief --input data/program_registry.json --output-dir output/program_briefs
python -m scripts.catalog_pdf --input data/program_registry.json --output output/catalog/master_catalog.md --generate-briefs
python -m scripts.component_bootstrap --name bbhai-review-example --output-dir components/bbhai-review-example
python -m scripts.demo_runner --mode plan
```

## Docker
```bash
docker build -t bbhai .
docker run --rm bbhai
```

## Distribution
- Docker image builds are the primary distribution mechanism today.
- Tag releases in git and update `docs/RELEASE_CHECKLIST.md` before publishing.
- Package registry support can be added later if needed.

## Notes
- PDFs are maintained locally and are ignored by git.
- Issue backlog is tracked in GitHub Issues.
- Issue labels use `prio:`, `type:`, and `area:` prefixes (see `docs/PROJECT_MANAGEMENT.md`).
- Milestone status and backlog tracking are aligned with `ROADMAP.md` and GitHub milestones.
- Scope assets support ports and wildcards; see `schemas/scope_asset.schema.json` and `examples/scope_assets_example.json`.
- Roadmap planning now reflects completion through the v0.9 milestone.
- Evidence registry entries can include hashes and custody metadata (see `docs/REPORTING.md`).
- Evidence storage can use encryption at rest guidance in `docs/REPORTING.md`.
- Architecture and outline docs call out attachments manifest and reproducibility pack outputs.
- Component registry index lives at `data/component_registry_index.json`.
- Program registry lives at `data/program_registry.json`.
- Tool usage guidance and constraints live in `docs/TOOLS.md`.
- Scan plan templates live in `templates/scan_plans/`.
- Tool run schema and example live in `schemas/tool_run.schema.json` and
  `examples/tool_runs/tool_run_example.json`.
- Risk assessment template and example live in `docs/RISK_ASSESSMENT.md` and
  `examples/risk_assessment_example.json`.
- Example pipeline config includes reporting and export stages (`examples/pipeline_config.yaml`).
- Program schema and registry examples live in `schemas/program.schema.json` and `examples/program_example.json`.
- Issue templates include bug, feature, security, research, and epic scaffolds in `.github/ISSUE_TEMPLATE`.
- Triage rules and milestone guidance are documented in `docs/PROJECT_MANAGEMENT.md`.
- Standard report templates live in `templates/reporting/standard/`.
- PDF exports use `templates/reporting/pandoc_header.tex` and `templates/reporting/fontconfig.conf`.
- Set `BBHAI_PANDOC_PDF_ENGINE=tectonic` to use Tectonic for Pandoc PDF output.
- Master catalog policy URLs render as autolinks to keep PDF tables within margins.
- Program registry entries retain source license and attribution metadata.
- Program registry diffs are generated with `python -m scripts.program_registry_diff`.
- Local program registry storage is managed with `python -m scripts.program_registry_store`.
- CI runs lint and format checks, schema validation, coverage reporting,
  dependency audits, knowledge index and published docs sync checks, coverage
  matrix checks, golden example re-emits, and a demo runner plan.
- Offline connector fixtures for tests live in `tests/fixtures/connectors/`.
- Catalog build connectors include yeswehack, intigriti, huntr, bounty-targets-data,
  disclose-io, and projectdiscovery (override with `--connectors`).
- Catalog ingestion writes audit logs and summaries (JSON/Markdown) under
  `data/ingestion_audit/` and blocks catalog outputs from `output/` or `evidence/`.

## Contributing
See `CONTRIBUTING.md` for how to suggest updates or fixes.

## Security
See `SECURITY.md` for reporting guidance.

## Contact
For questions or feedback, open an issue or email support@ravdevops.com.

## License
Apache-2.0. See `LICENSE`.
