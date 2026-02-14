# Release Plan

This plan defines versioning, changelog usage, and distribution expectations.

## Versioning
- Use SemVer (`MAJOR.MINOR.PATCH`).
- Increment:
  - MAJOR for breaking schema or workflow changes.
  - MINOR for new features or new schemas.
  - PATCH for fixes and documentation updates.

## Changelog
- Keep changes in `CHANGELOG.md` under **Unreleased**.
- Move entries to a dated release section at publish time.
- Link `docs/RELEASE_NOTES_TEMPLATE.md` for the final summary.

## Distribution
- Primary delivery is the Docker image described in `README.md`.
- Tag git releases after completing `docs/RELEASE_CHECKLIST.md`.
- Package registry support is optional and tracked separately.

## Release flow (summary)
1) Complete `docs/RELEASE_CHECKLIST.md`.
2) Update `CHANGELOG.md` and release notes.
3) Tag release and publish the Docker image.
