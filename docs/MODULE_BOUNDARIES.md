# Module Boundaries

## Hub responsibilities
- `docs/` and `schemas/` define contracts and guidance.
- `scripts/` provides CLI tooling; `scripts/lib/` holds shared helpers.
- `templates/` stores scan and reporting templates only.
- `examples/` stores synthetic samples and exports.
- `data/` and `evidence/` store local tracking metadata only.
- `labs/` contains scaffold material for synthetic testing.
- `tests/` contains unit and validation tests.

## Component responsibilities
- `components/` contains submodules or subtrees for feature repos.
- Component code should not live in the hub repo.

## Safety boundary
- No exploit code or target-specific tooling belongs in the hub.
- All automation must follow `docs/ROE.md`.
