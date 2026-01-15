# Pipeline

The hub provides a simple pipeline orchestrator for discovery, scan planning,
triage, intel enrichment, and notifications. Scripts are planning oriented and
avoid live exploitation.

## Stages
- Scope import: `scripts/import_scope.py`
- Discovery: `scripts/discovery_assets.py`
- Template scan planning: `scripts/scan_templates.py`
- Triage: `scripts/triage_findings.py`
- External intel: `scripts/external_intel.py`
- Notifications: `scripts/notify.py`
- Component registry: `scripts/component_runtime.py`

## Pipeline config
Use `examples/pipeline_config.yaml` as a starting point. Each stage defines a
`name` and a `config` mapping that matches the stage script flags. Use
underscores in config keys to map to CLI flags with hyphens.

## Orchestrator
Use `scripts/pipeline_orchestrator.py` to plan or run stages.

```bash
python scripts/pipeline_orchestrator.py --config examples/pipeline_config.yaml --mode plan
```

## Performance controls
Scan planning supports `max_concurrency` and `min_delay_seconds`. Pair those
with TargetProfile `constraints` and ROE guardrails.

## Safety
Keep all steps within scope, use canary strings, and stop immediately if real
user data appears.
