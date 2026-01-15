# Bug_Bounty_Hunter_AI

Docs-first hub for AI bug bounty workflows with schemas, checklists, pipeline
scripts, and component integration guidance for authorized testing of AI-enabled
applications (RAG, embeddings, fine-tuning, tool-using agents, and logging).

This project is informational and operational guidance only. It is not legal
advice. Only test systems where you have explicit authorization.

## Docs
- `ROADMAP.md`
- `docs/PROJECT_OUTLINE.md`
- `docs/ROE.md`
- `docs/PROJECT_MANAGEMENT.md`
- `docs/TARGET_PROFILE.md`
- `docs/THREAT_MODEL.md`
- `docs/KNOWLEDGE_FORMAT.md`
- `docs/KNOWLEDGE_TAGS.md`
- `knowledge/INDEX.md`
- `docs/ARCHITECTURE.md`
- `docs/PIPELINE.md`
- `docs/TRIAGE.md`
- `docs/SEVERITY_MODEL.md`
- `docs/INTEL.md`
- `docs/ENVIRONMENT.md`
- `docs/COMPONENTS.md`
- `docs/COMPONENT_MANIFEST.md`
- `docs/REPORTING.md`
- `docs/NOTIFICATIONS.md`
- `docs/MODULE_BOUNDARIES.md`
- `docs/HACK_TYPES.md`
- `docs/COVERAGE_MATRIX.md`
- `docs/TESTING.md`
- `docs/RELEASE_NOTES_TEMPLATE.md`
- `docs/RELEASE_CHECKLIST.md`

## Choose Your Path
- `docs/paths/bug-bounty-hunter.md`
- `docs/paths/appsec-review.md`
- `docs/paths/threat-model-only.md`

## Repository layout
- `docs/` - architecture, rules, and planning docs
- `schemas/` - data model schemas
- `components/` - component repos (submodules or subtrees)
- `knowledge/` - sources, cards, and checklists
- `examples/` - sample profiles and outputs
- `data/` - local tracking data and registries
- `evidence/` - evidence registry entries
- `templates/` - scan planning templates
- `scripts/` - bootstrap and automation scripts
- `labs/` - synthetic lab scaffolding
- `tests/` - unit and validation tests

## Install
```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## How To Use
- Start with `docs/ROE.md` and confirm written authorization.
- Create a TargetProfile from the questionnaire or a minimal YAML in `examples/`.
- Run the pipeline in plan mode (`docs/PIPELINE.md`) to generate artifacts.
- Review outputs and produce report bundles or issue drafts (`docs/REPORTING.md`).
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
python -m bbhai migrate --input components/bbhai-review-sample/component_manifest.yaml --from 0.0.0 --to 0.1.0 --dry-run
```

## Module Usage
```bash
python -m scripts.target_profile_generate --input examples/target_profile_questionnaire.yaml --output output/target_profile.json
python -m scripts.dataflow_map --target-profile output/target_profile.json --output output/dataflow_map.json
python -m scripts.threat_model_generate --target-profile output/target_profile.json --output output/threat_model.json
python -m scripts.pipeline_orchestrator --config examples/pipeline_config.yaml --mode plan
python -m scripts.report_bundle --findings examples/outputs/findings.json --target-profile examples/target_profile_minimal.yaml --output-dir output/report_bundle
python -m scripts.export_issue_drafts --findings examples/outputs/findings.json --output-dir output/issue_drafts
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
- Milestone status and backlog tracking are aligned with `ROADMAP.md` and GitHub milestones.
- Roadmap planning now extends through the v0.8 ops documentation milestone.
- CI runs lint and format checks, schema validation, coverage reporting,
  knowledge index and coverage matrix checks, golden example re-emits, and a
  demo runner plan.

## Contributing
See `CONTRIBUTING.md` for how to suggest updates or fixes.

## Security
See `SECURITY.md` for reporting guidance.

## Contact
For questions or feedback, open an issue or email support@ravdevops.com.

## License
Apache-2.0. See `LICENSE`.
