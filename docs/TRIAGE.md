# Triage

Triage assigns severity, priority, and next-test suggestions to findings or
scan plans.

## Outputs
Each triage item includes:
- `severity` and `priority`
- `rationale`
- `confidence` (0 to 1)
- optional `next_tests`

## AI-assisted triage (opt-in)
AI triage is disabled by default and requires explicit configuration. Use
minimal inputs unless you explicitly allow full data.

### Config fields
- `provider`: `ollama` or `openai`
- `endpoint`: override API endpoint
- `model`: model name
- `api_key_env`: environment variable holding the API key
- `OPENAI_API_KEY` is used by default when `provider` is `openai`
- `timeout_seconds`: request timeout
- `input_mode`: `minimal` or `full`
- `allow_data`: `true` to allow full input to be sent

### Example
```bash
python scripts/triage_findings.py --input examples/outputs/findings.json --output output/triage.json --ai-enabled --ai-config examples/triage_ai_config.yaml
```

## Safety
Do not send sensitive data to external services by default. Always follow
`docs/ROE.md`.
