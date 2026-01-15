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

## Expected outputs
RAG stub:
```bash
curl http://localhost:8000/index.json
curl http://localhost:8000/context.json
```

Vector store stub:
```bash
curl http://localhost:8001/index.json
curl http://localhost:8001/vectors.json
```

## Teardown
```bash
docker compose -f labs/docker-compose.yaml down
```

## Example regression path
1. Generate a TargetProfile from the questionnaire:
   ```bash
   python -m scripts.target_profile_generate --input examples/target_profile_questionnaire.yaml --output output/target_profile.json
   ```
2. Plan scan tests using safe templates:
   ```bash
   python -m scripts.scan_templates --templates templates --targets output/target_profile.json --output output/scan_plan.json
   ```
3. Generate a report bundle from sample findings:
   ```bash
   python -m scripts.report_bundle --findings examples/outputs/findings.json --target-profile output/target_profile.json --output-dir output/report_bundle
   ```
