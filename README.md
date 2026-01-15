# Bug_Bounty_Hunter_AI

AI-assisted bug bounty workflow system for authorized testing of AI-enabled
applications (RAG, embeddings, fine-tuning, tool-using agents, and logging).

This project is informational and operational guidance only. It is not legal
advice. Only test systems where you have explicit authorization.

## Docs
- `ROADMAP.md`
- `docs/PROJECT_OUTLINE.md`
- `docs/ROE.md`
- `docs/PROJECT_MANAGEMENT.md`
- `docs/TARGET_PROFILE.md`
- `docs/KNOWLEDGE_FORMAT.md`
- `docs/KNOWLEDGE_TAGS.md`
- `knowledge/INDEX.md`
- `docs/ARCHITECTURE.md`
- `docs/PIPELINE.md`
- `docs/TRIAGE.md`
- `docs/INTEL.md`
- `docs/COMPONENTS.md`
- `docs/COMPONENT_MANIFEST.md`
- `docs/REPORTING.md`
- `docs/MODULE_BOUNDARIES.md`
- `docs/HACK_TYPES.md`

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

## Usage
```bash
python scripts/target_profile_generate.py --input examples/target_profile_questionnaire.yaml --output output/target_profile.json
python scripts/pipeline_orchestrator.py --config examples/pipeline_config.yaml --mode plan
python scripts/report_bundle.py --findings examples/outputs/findings.json --target-profile examples/target_profile_minimal.yaml --output-dir output/report_bundle
python scripts/export_issue_drafts.py --findings examples/outputs/findings.json --output-dir output/issue_drafts
```

## Docker
```bash
docker build -t bbhai .
docker run --rm bbhai
```

## Notes
- PDFs are maintained locally and are ignored by git.

## Contributing
See `CONTRIBUTING.md` for how to suggest updates or fixes.

## Security
See `SECURITY.md` for reporting guidance.

## Contact
For questions or feedback, open an issue or email support@ravdevops.com.

## License
Apache-2.0. See `LICENSE`.
