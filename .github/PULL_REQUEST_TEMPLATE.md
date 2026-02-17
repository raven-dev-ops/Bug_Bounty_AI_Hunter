## Summary
What does this change do, and why?

## Safety
Call out any content that touches testing guidance or tooling behavior.
If this PR changes safety guidance, link the relevant policy sections.

## Checklist
- [ ] Content follows `docs/ROE.md` and avoids unauthorized testing guidance.
- [ ] No secrets, credentials, or private program details are included.
- [ ] `python -m scripts.validate_markdown_ascii` passes.
- [ ] `python -m scripts.validate_markdown_links` passes.
- [ ] I ran `python -m scripts.check_all --fast` (or explained why not).

## Generated files (if applicable)
- [ ] `python -m scripts.knowledge_index --output knowledge/INDEX.md`
- [ ] `python -m scripts.publish_knowledge_docs`
- [ ] `python -m scripts.coverage_matrix --input docs/coverage_matrix.yaml --output docs/COVERAGE_MATRIX.md`
- [ ] `python -m scripts.sync_mkdocs_copies`
- [ ] `python -m scripts.component_registry_index --output data/component_registry_index.json`

## Notes for reviewers
Anything reviewers should focus on (risk, tradeoffs, follow-ups).

