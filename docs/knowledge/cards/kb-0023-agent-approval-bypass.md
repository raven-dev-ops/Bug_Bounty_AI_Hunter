# Agent approval bypass risk

## Metadata
- ID: kb-0023
- Type: card
- Status: reviewed
- Tags: ai-security, agents, access-control
- Source: project
- Date: 2026-02-05

## Summary
Agent flows can skip approval gates if checks are only enforced in the UI or
the client layer.

## Relevance to the project
Encourages validation of server-side approval enforcement for tool use.

## Safe notes
- Enforce approvals on the server side.
- Log approvals and tool invocations with timestamps.
- Validate that bypass attempts fail safely.
- Use canary inputs for testing.

## References
- `docs/ROE.md`
- `knowledge/checklists/agents-review.md`
