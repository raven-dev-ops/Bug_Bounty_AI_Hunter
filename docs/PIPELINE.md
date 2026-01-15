# Pipeline

The hub provides a simple pipeline orchestrator for discovery, scan planning,
triage, intel enrichment, and notifications. Scripts are planning oriented and
avoid live exploitation.

## Stages
- Scope import: `python -m scripts.import_scope`
- Discovery: `python -m scripts.discovery_assets`
- Dataflow map: `python -m scripts.dataflow_map`
- Threat model: `python -m scripts.threat_model_generate`
- Template scan planning: `python -m scripts.scan_templates`
- Triage: `python -m scripts.triage_findings`
- External intel: `python -m scripts.external_intel`
- Notifications: `python -m scripts.notify`
- Component registry: `python -m scripts.component_runtime`

## Scope import formats
- `generic` (default) using `examples/scope_generic.json`
- `hackerone` using API credentials (`HACKERONE_API_ID`, `HACKERONE_API_TOKEN`)
  and a program handle via `--program`

## Pipeline config
Use `examples/pipeline_config.yaml` as a starting point. Each stage defines a
`name` and a `config` mapping that matches the stage script flags. Use
underscores in config keys to map to CLI flags with hyphens.

## Artifacts and schemas
- Pipeline config: `schemas/pipeline_config.schema.json` (`examples/pipeline_config.yaml`)
- Pipeline plan output: `schemas/pipeline_plan.schema.json` (`examples/pipeline_plan_output.json`)
- Discovery output: `schemas/discovery_output.schema.json` (`examples/discovery_output.json`)
- Dataflow map: `schemas/dataflow_map.schema.json` (`examples/dataflow_map_example.json`)
- Threat model: `schemas/threat_model.schema.json` (`examples/threat_model_example.json`)
- Scan plan output: `schemas/scan_plan.schema.json` (`examples/scan_plan_output.json`)
- Triage output: `schemas/triage_output.schema.json` (`examples/triage_output.json`)
- Intel output: `schemas/intel_output.schema.json` (`examples/intel_output.json`)
- Component registry: `schemas/component_registry.schema.json`
  (`examples/component_registry_output.json`)

## Orchestrator
Use `python -m scripts.pipeline_orchestrator` to plan or run stages.

```bash
python -m scripts.pipeline_orchestrator --config examples/pipeline_config.yaml --mode plan
```

## Demo runner
Use `python -m scripts.demo_runner` to run the example pipeline with outputs
stored under `output/demo` by default.

```bash
python -m scripts.demo_runner --mode plan
python -m scripts.demo_runner --mode run
```

## Performance controls
Scan planning supports `max_concurrency` and `min_delay_seconds`. Pair those
with TargetProfile `constraints` and ROE guardrails.

## Safety
Keep all steps within scope, use canary strings, and stop immediately if real
user data appears.
