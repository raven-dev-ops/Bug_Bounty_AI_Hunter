# Pipeline Guardrails

Guardrails apply to all pipeline stages. Use `docs/ROE.md` as the baseline.

## Global requirements
- Written authorization is required.
- Use allowlists and conservative rate limits.
- Track request and token budgets per stage.
- Stop at minimal proof.

## Stage-level notes
- Scope import: verify program scope before use.
- Discovery: use passive inventory only.
- Scan planning: generate safe, low-impact steps.
- Triage: do not send sensitive data to AI services without approval.
- External intel: use scope enforcement and timeouts.
- Reporting: redact secrets and include only minimal evidence.

## Run mode gating
- Provide `ROE_ACK.yaml` or `--ack-authorization`.
- Confirm approvals for any active tests.
