# ADR: Command Center Architecture

- Status: Accepted
- Date: 2026-02-17
- Related issue: #164
- Related plan: `DEEP_RESEARCH_02_COMMAND_CENTER.md`

## Context
The repository is docs-first and script-first. It has strong schemas, examples, and
CLI tooling, but no integrated command center application yet. The command center
must expose planning and reporting workflows without bypassing ROE or safety rules.

## Decision
Adopt a staged architecture that starts with read-only planning workflows and then
adds controlled execution.

### Target runtime shape
- Frontend: Single-page app for feed, program detail, workspace, findings, logs.
- Backend API: REST service for catalog, workspace, findings, tool runs, reports.
- Persistence: SQLite for MVP, then optional Postgres.
- Worker: background job runner for long tasks and script execution.

### Why this shape
- Reuses existing scripts as the execution core.
- Preserves schema contracts already present in `schemas/`.
- Supports a safe "plan first" UX before enabling run mode.
- Keeps audit trails for tool runs and generated artifacts.

## Guardrails and safety mapping
- ROE acknowledgement is required before any run action.
- Plan mode is default in UI and API.
- Tool runner uses allowlisted scripts and explicit input contracts.
- Logs and artifacts include provenance metadata and timestamps.

These controls align with current policy docs and reporting expectations.

## Mapping to current repository assets
- Schemas: use existing JSON schemas for findings, evidence, plans, and outputs.
- Scripts: expose existing `scripts.*` modules through a task wrapper.
- Templates: keep report, issue, and scan templates as source of generated outputs.
- Data: ingest existing `data/`, `bounty_board/`, and `examples/` artifacts.

## Phased rollout
1. MVP read-only pages (catalog, program detail, docs/help, report preview).
2. Workspace creation with ROE acknowledgement and local persistence.
3. Tool runner API with plan/run toggle and structured logs.
4. Findings and report composer flows wired to existing export scripts.
5. Integrations and RBAC hardening after MVP stabilization.

## Consequences
### Positive
- Faster delivery by wrapping proven scripts.
- Stable contracts due to schema-first design.
- Clear path from docs-only to operational command center.

### Trade-offs
- Temporary duplication between CLI and API wrappers.
- SQLite constraints before moving to multi-user scale.
- Additional maintenance for UI + API test coverage.

## Non-goals (MVP)
- Multi-tenant RBAC.
- Direct exploit automation.
- Secret vault integration.

## Notes for implementation
- Keep all markdown ASCII-clean.
- Keep API outputs schema-valid.
- Prefer additive changes to avoid breaking existing CLI workflows.
