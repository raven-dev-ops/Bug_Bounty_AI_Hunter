# Labs

Synthetic lab environment for safe validation and regression testing. Use
synthetic data and canary strings only.

Planned components:
- minimal RAG app
- vector store mock
- prompt logging stub
- canary dataset generator

This repo stores scaffolding only; full implementation can live in a component
repo.

## Setup
1. Install Docker.
2. Start the lab:
   ```bash
   docker compose -f labs/docker-compose.yaml up -d
   ```
3. Verify containers are running:
   ```bash
   docker compose -f labs/docker-compose.yaml ps
   ```

## Teardown
```bash
docker compose -f labs/docker-compose.yaml down
```

## Example regression path
1. Generate a TargetProfile from the questionnaire:
   ```bash
   python scripts/target_profile_generate.py --input examples/target_profile_questionnaire.yaml --output output/target_profile.json
   ```
2. Plan scan tests using safe templates:
   ```bash
   python scripts/scan_templates.py --templates templates --targets output/target_profile.json --output output/scan_plan.json
   ```
3. Generate a report bundle from sample findings:
   ```bash
   python scripts/report_bundle.py --findings examples/outputs/findings.json --target-profile output/target_profile.json --output-dir output/report_bundle
   ```
