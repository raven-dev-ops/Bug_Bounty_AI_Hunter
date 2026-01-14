# Components

Components are separate repositories that implement one capability. The hub
links them via submodules (preferred) or subtree.

## Linking options
Submodule (preferred):
```bash
git submodule add <repo-url> components/bbhai-<feature>
git submodule update --init --recursive
```

Subtree (alternative):
```bash
git subtree add --prefix components/bbhai-<feature> <repo-url> main --squash
```

## Component contract
Each component should provide:
- A `README.md` describing purpose and usage.
- A small manifest describing capabilities and schema compatibility.
- Tests or examples that demonstrate safe behavior.

## Manifest example
```yaml
name: bbhai-review-rag
version: 0.1.0
capabilities:
  - review
schemas:
  target_profile: ">=0.1.0"
  test_case: ">=0.1.0"
  finding: ">=0.1.0"
entrypoints:
  review: "bbhai_review_rag:run"
```

## Versioning and compatibility
- Use semantic versioning.
- Document schema compatibility in the manifest.
- Avoid breaking changes without a migration path.

## Safety
All components must follow `docs/ROE.md` and avoid weaponized content.
