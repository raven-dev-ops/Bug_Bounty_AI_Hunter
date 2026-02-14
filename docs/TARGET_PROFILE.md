# Target Profile

Target profiles capture authorized scope, AI surfaces, and data flows for a
target. Use `schemas/target_profile.schema.json` as the contract.

## Required fields
- `schema_version`
- `name`

## Recommended fields
- `program` (platform, policy_url, contact)
- `scope` (in_scope, out_of_scope, restrictions)
- `assets` (seed and discovered assets)
- `ai_surfaces` (rag, embeddings, fine_tuning, logging, agents)
- `data_stores`, `data_flows`
- `access_model`
- `constraints` (rate limits, stop conditions)
- `notes`

## Scope assets
Scope assets use `type`, `value`, and optional `ports` entries. Use `wildcard`
types with a leading `*.` value. Port ranges are `{start, end}` pairs.

See `schemas/scope_asset.schema.json` and `examples/scope_assets_example.json`.

## Dataflow map
Document where prompts, retrieval context, embeddings, logs, or training data
move. Keep this high level and avoid real user data.

Use `python -m scripts.dataflow_map` to generate a dataflow map from a
TargetProfile. See `examples/dataflow_map_example.json`.

## Generator
Use `python -m scripts.target_profile_generate` to convert a questionnaire into a
TargetProfile artifact.

See `examples/target_profile_minimal.yaml` and
`examples/target_profile_questionnaire.yaml` for sample inputs.

## Example
```yaml
schema_version: "0.2.0"
name: Example Program
scope:
  in_scope:
    - type: domain
      value: example.com
    - type: domain
      value: api.example.com
      ports:
        - start: 443
          end: 443
ai_surfaces:
  rag: false
  embeddings: false
```
