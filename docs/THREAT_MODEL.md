# Threat Model

Threat models capture AI-specific attack surfaces, impacts, and mitigations.
Use `schemas/threat_model.schema.json` as the contract.

Generate an artifact with:
```bash
python -m scripts.threat_model_generate --target-profile examples/target_profile_minimal.yaml --output output/threat_model.json
```

## Recommended sections
- Assumptions and scope
- Attack surfaces and controls
- Threats with impacts and mitigations
- Notes and open questions

## Example
See `examples/threat_model_example.json`.
