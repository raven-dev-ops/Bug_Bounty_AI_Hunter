# Testing

## Goals
- Validate schemas and example artifacts.
- Catch regressions in core helper utilities.
- Keep checks fast and deterministic.

## Coverage
- Schema validation: `python -m scripts.validate_schemas`
- Unit tests: `python -m unittest discover -s tests`
- Checklist examples: `tests/test_checklist_examples.py`
- Knowledge index freshness: `python -m scripts.knowledge_index`
- Knowledge frontmatter lint: `python -m scripts.knowledge_lint`
- Markdown link validation: `python -m scripts.validate_markdown_links`
- Demo runner plan: `python -m scripts.demo_runner --mode plan`
- Dependency audit: `python -m pip_audit -r requirements.txt -r requirements-dev.txt`

## Run locally
```bash
python -m ruff check scripts tests
python -m pip_audit -r requirements.txt -r requirements-dev.txt
python -m scripts.validate_schemas
python -m unittest discover -s tests
```

## Docs-only checks
```bash
python -m scripts.knowledge_lint
python -m scripts.validate_markdown_links
python -m scripts.knowledge_index --output knowledge/INDEX.md
python -m scripts.coverage_matrix --input docs/coverage_matrix.yaml --output docs/COVERAGE_MATRIX.md
```

## PDF golden tests (optional)
- Requires `pandoc` or `wkhtmltopdf`.
- Pandoc exports use `templates/reporting/fontconfig.conf` and `templates/reporting/pandoc_header.tex`.
- Override the PDF engine with `BBHAI_PANDOC_PDF_ENGINE=tectonic`.
- Update hashes: `python -m scripts.pdf_golden_update --engine pandoc`
- Run tests: `BBHAI_PDF_TESTS=1 python -m unittest tests/test_pdf_golden.py`

## Notes
Avoid live network calls in tests. Use synthetic examples only.
