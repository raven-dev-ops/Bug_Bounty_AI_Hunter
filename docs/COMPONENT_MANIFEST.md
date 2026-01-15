# Component Manifest

Components declare a manifest that describes capabilities and schema
compatibility. This lets the hub validate plugins and route data safely.

## Location
Store the manifest at the repo root as `component_manifest.yaml` or
`component_manifest.json`.

Schema reference: `schemas/component_manifest.schema.json`.

## Validation
Use `python -m scripts.component_runtime --manifest <path>` to validate a manifest.

## Required fields
- `schema_version`: manifest schema version (string)
- `name`: unique component name (string)
- `version`: semantic version string (string)
- `capabilities`: list of capabilities (array of strings)
- `schemas`: supported schema versions (object)

## Optional fields
- `description`: short summary
- `repository`: URL to source repo
- `license`: SPDX identifier
- `entrypoints`: capability -> entrypoint mapping
- `contact`: maintainer contact info

## Example
```yaml
schema_version: "0.1.0"
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
description: RAG review checklist generator
repository: https://github.com/example/bbhai-review-rag
license: Apache-2.0
contact: support@ravdevops.com
```
