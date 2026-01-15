# Component Contract

This contract defines the minimum interface and readiness expectations for
component repos that integrate with the hub.

## Required artifacts
- `README.md` with purpose, scope, and usage.
- `component_manifest.yaml` or `.json` at the repo root.
- Schema-compatible inputs and outputs (see `schemas/`).
- Example inputs/outputs under `examples/`.
- Tests that validate core behavior and schema compliance.

## Inputs
Components should declare which inputs they accept in the manifest and handle
the following artifacts when applicable:
- TargetProfile (required for most review components).
- DataflowMap and ThreatModel (optional, when relevant).
- PipelineConfig or stage-specific configuration.

## Outputs
Components should emit structured outputs that validate against hub schemas:
- Findings (`schemas/finding.schema.json`).
- Test cases (`schemas/test_case.schema.json`).
- Evidence entries when artifacts are captured.

Outputs must include `schema_version` and avoid embedding sensitive data.

## Interface expectations
- Provide entrypoints in the manifest for each capability.
- Entry points should accept explicit inputs/outputs and avoid side effects.
- Document deterministic behavior and any external dependencies.

## Testing expectations
- Unit tests for schema mapping and core logic.
- Example outputs validated by `python -m scripts.validate_schemas`.
- A smoke test that validates the component manifest.

## Readiness checklist
- [ ] Manifest validated (`schemas/component_manifest.schema.json`).
- [ ] README covers scope, inputs, outputs, and safety limits.
- [ ] Examples validate against schemas.
- [ ] Tests pass locally or in CI.
- [ ] ROE and safety requirements are documented.
- [ ] License and maintainer contact are present.

See `docs/COMPONENTS.md` and `docs/COMPONENT_MANIFEST.md` for supporting details.
