# LLM API authorization review checklist

## Metadata
- ID: kb-checklist-0009
- Type: checklist
- Status: draft
- Tags: ai-security, api-security, access-control, logging
- Source: project
- Date: 2026-02-05

## Summary
Checklist for reviewing authorization and tenant isolation in LLM API calls.

## Relevance to the project
LLM APIs often carry sensitive prompts and context. Authorization gaps can
expose data across tenants or environments.

## Checklist
- Identify API keys, service accounts, and token scopes.
- Verify per-tenant isolation on LLM requests and logs.
- Confirm request signing or tamper protection where applicable.
- Validate server-side enforcement of access controls.
- Review rate limits and abuse protections.
- Ensure redaction of prompts and outputs in logs.
- Confirm approvals for high-impact tool calls.

## Safe notes
- Use canary strings and synthetic data.
- Avoid testing production endpoints without approval.

## References
- `docs/ROE.md`
- `docs/REPORTING.md`
