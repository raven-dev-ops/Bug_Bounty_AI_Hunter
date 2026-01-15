# Component Manifest

Components declare a manifest that describes capabilities and schema
compatibility. This lets the hub validate plugins and route data safely.

## Required fields
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
description: RAG review checklist generator
repository: https://github.com/example/bbhai-review-rag
license: Apache-2.0
contact: support@ravdevops.com
```
