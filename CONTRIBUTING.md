# Contributing

Thanks for improving the project and its documentation.

## Safety (non-negotiable)
- Follow `docs/ROE.md` and only test targets you own or have written authorization to test.
- Do not add exploit code, step-by-step live target instructions, or guidance that enables unauthorized testing.
- Do not include secrets, private program details, or non-public target scope in issues or PRs.

## What to contribute
- Docs and workflow improvements.
- Schemas and examples for data exchange.
- Scripts that improve planning, validation, or reporting.
- Knowledge cards/checklists that follow `docs/KNOWLEDGE_FORMAT.md`.

## How to propose changes
1. Open an issue describing the change and scope.
2. For larger changes, discuss approach and acceptance criteria first.
3. Submit a pull request once the approach is agreed.

## Local checks (recommended)
- Quick pass: `python -m scripts.check_all --fast`
- Full suite: `python -m scripts.check_all`

## Generated files (do not hand-edit)
- `knowledge/INDEX.md` (run `python -m scripts.knowledge_index --output knowledge/INDEX.md`)
- `docs/KNOWLEDGE_INDEX.md` and `docs/knowledge/` (run `python -m scripts.publish_knowledge_docs`)
- `docs/COVERAGE_MATRIX.md` (edit `docs/coverage_matrix.yaml`, then run `python -m scripts.coverage_matrix --input docs/coverage_matrix.yaml --output docs/COVERAGE_MATRIX.md`)
- `data/component_registry_index.json` (run `python -m scripts.component_registry_index --output data/component_registry_index.json`)
- `site/` (MkDocs build output)

## MkDocs copies
`docs/BUGCROWD.md` and `docs/GUIDE.md` are MkDocs copies of root docs.
Edit `BUGCROWD.md` and `GUIDE.md`, then run `python -m scripts.sync_mkdocs_copies`.

## Line endings
This repo enforces LF via `.gitattributes`.
If you are on Windows and see CRLF warnings, set `git config core.autocrlf false` (in this repo) and re-checkout, or run `git add --renormalize .` once.

## Style
- Keep the tone professional and practical.
- Keep sentences concise.
- Keep Markdown ASCII-only.

## Changelog
When docs or structure change, update `README.md` and `CHANGELOG.md`.
