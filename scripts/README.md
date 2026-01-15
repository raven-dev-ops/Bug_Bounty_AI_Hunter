# Scripts

Project automation and pipeline planning scripts live here.

## Requirements
- Python 3.10+
- PyYAML for YAML inputs (`pip install pyyaml`)

## Tools
- `target_profile_generate.py` - build TargetProfile from questionnaires
- `import_scope.py` - import scope exports into a TargetProfile
- `discovery_assets.py` - generate candidate assets (no live checks)
- `scan_templates.py` - render template-based scan plans
- `triage_findings.py` - assign priorities and status
- `external_intel.py` - enrich assets with intel records
- `notify.py` - send summary notifications (console/file by default)
- `component_runtime.py` - validate component manifests
- `pipeline_orchestrator.py` - plan or run pipeline stages
- `bootstrap_issues.sh` - create labels and starter backlog
