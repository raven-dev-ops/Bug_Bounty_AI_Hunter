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

## Bootstrap a component repo
Use the scaffold script to create a new component skeleton:
```bash
python -m scripts.component_bootstrap --name bbhai-review-example --output-dir components/bbhai-review-example
```

## Component contract
Each component should provide:
- A `README.md` describing purpose and usage.
- A manifest at the repo root (`component_manifest.yaml` or `.json`).
- Tests or examples that demonstrate safe behavior.

See `docs/COMPONENT_MANIFEST.md` and `schemas/component_manifest.schema.json`.

## Manifest example
```yaml
name: bbhai-review-rag
version: 0.1.0
capabilities:
  - review
schemas:
  target_profile: ">=0.2.0"
  test_case: ">=0.1.0"
  finding: ">=0.1.0"
entrypoints:
  review: "bbhai_review_rag:run"
```

## Runtime registry
Use `python -m scripts.component_runtime` to validate manifests and build a registry.
Enable or disable components via a config file such as
`examples/component_runtime_config.yaml`.
Schema validation requires the `jsonschema` package.

Generate the example registry output with:
```bash
python -m scripts.component_runtime --output examples/component_registry_output.json
```

## Versioning and compatibility
- Use semantic versioning.
- Document schema compatibility in the manifest.
- Avoid breaking changes without a migration path.

## Safety
All components must follow `docs/ROE.md` and avoid weaponized content.
