# Agent tool scope bleed risk

## Metadata
- ID: kb-0022
- Type: card
- Status: draft
- Tags: ai-security, agents, access-control
- Source: project
- Date: 2026-02-05

## Summary
Agents can accumulate or inherit broader tool permissions than intended,
leading to scope bleed across tasks or tenants.

## Relevance to the project
Helps reviewers identify over-privileged tool access in agent pipelines.

## Safe notes
- Enforce least-privilege scopes per task.
- Require explicit approval for elevated actions.
- Reset tool context between tasks.
- Validate tenant isolation for multi-tenant tooling.

## References
- `docs/ROE.md`
- `knowledge/checklists/agents-review.md`
