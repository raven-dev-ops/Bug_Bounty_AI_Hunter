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
- Demo runner plan: `python -m scripts.demo_runner --mode plan`

## Run locally
```bash
python -m ruff check scripts tests
python -m scripts.validate_schemas
python -m unittest discover -s tests
```

## Notes
Avoid live network calls in tests. Use synthetic examples only.
