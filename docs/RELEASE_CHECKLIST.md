# Release Checklist

Use this list before tagging or publishing a release. Keep steps concise and
aligned with the docs-first focus of this repo.

## Documentation
- Update `CHANGELOG.md` with notable changes.
- Confirm `ROADMAP.md` milestone tracking is current.
- Verify `README.md` usage examples still match scripts.
- Draft release notes using `docs/RELEASE_NOTES_TEMPLATE.md`.

## Quality checks
- Run `python -m ruff check scripts tests`.
- Run `python -m scripts.validate_schemas`.
- Run `python -m unittest discover -s tests`.

## Artifacts
- Ensure example outputs in `examples/` are up to date.
- Regenerate the knowledge index if needed:
  `python -m scripts.knowledge_index --output knowledge/INDEX.md`.

## Tagging
- Create an annotated git tag (e.g., `v0.7.0`).
- Push tags to GitHub.

## Post-release
- Verify CI passes on the tagged release.
- Announce the release in the project notes or discussions.
