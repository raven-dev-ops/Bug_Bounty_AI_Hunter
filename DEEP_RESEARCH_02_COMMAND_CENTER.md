# Deep Research 02 - Command Center Redesign

Processed: 2026-02-17

This is an ASCII-cleaned and repo-safe summary derived from a local deep research draft
that contained non-ASCII characters and web citations. The raw draft was intentionally
removed after processing to keep the repository coherent and to satisfy Markdown ASCII
validation.

Scope note: This repo is "planning-first" and must follow `docs/ROE.md`. Nothing below
is intended as target-specific exploitation guidance.

## Key takeaways (planning)

- Current state: docs-first hub repo with schemas, scripts, and a local `dashboard.html`
  that becomes useful after importing local artifacts.
- Target direction: multi-page UI + backend API + persistence + job orchestration +
  audit logs, with safety/authorization gates mirrored in UX ("plan" vs "run").
- Delivery approach: ship a small MVP focused on read-only planning workflows first,
  then add platform APIs/webhooks, and only later multi-user/RBAC hardening.

## GitHub issue seed table (source of truth)

Columns: `Milestone | Parent | Issue Title | Description | Priority | Tags | Effort`

| Milestone | Parent | Issue Title | Description | Priority | Tags | Effort |
|---|---|---|---|---|---|---|
| MVP | - | Create command-center architecture ADR | Write an Architecture Decision Record describing SPA + API + DB + worker model and how it maps to existing scripts/schemas. | high | docs,backend,UX | small |
| MVP | - | Scaffold frontend app | Create frontend project (React/TS + Tailwind) with routing and layout shell. | high | frontend,UX | medium |
| MVP | Scaffold frontend app | Implement app shell navigation | Left nav + top command bar + command palette skeleton; responsive layout. | high | frontend,UX | medium |
| MVP | Scaffold frontend app | Implement dark-yellow design tokens | Add CSS variables, Tailwind config, theme switcher; enforce contrast targets. | high | frontend,UX | medium |
| MVP | - | Scaffold backend API | Add backend service (e.g., FastAPI) providing REST endpoints for programs/findings/workspaces/runs. | high | backend | large |
| MVP | Scaffold backend API | Define internal API contract | OpenAPI spec for core resources and job runner endpoints. | high | backend,docs | medium |
| MVP | Scaffold backend API | Add persistence layer | SQLite (MVP) schema for programs, workspaces, findings, evidence metadata, tool runs, tasks. | high | backend | large |
| MVP | - | Implement artifact ingestion layer | Import existing `bounty_board/` markdown + registry JSON + findings DB into DB. | high | backend,integration | large |
| MVP | - | Build Bounty Feed page | Feed table with filters/sorts; reads from imported bounty board + program registry data. | high | frontend,UX | large |
| MVP | Build Bounty Feed page | Build saved views | Save filter presets per user (local for MVP). | medium | frontend | medium |
| MVP | - | Build Bounty Detail page | Program overview, provenance/conflicts viewer, actions (create workspace). | high | frontend,UX | large |
| MVP | - | Engagement workspace creation | Create workspace record; scaffold ROE_ACK + pipeline config + report dirs (mirror CLI behavior). | high | backend,UX | large |
| MVP | Engagement workspace creation | ROE acknowledgement UI | Form to populate `acknowledged_at`, `acknowledged_by`, `authorized_target`; enforce run gating. | high | frontend,backend,security | medium |
| MVP | - | Tools Hub: script catalog | Show repo tool catalog (grouped by pipeline stage) with docs and run buttons. | high | frontend,UX | medium |
| MVP | Tools Hub: script catalog | Tool runner API endpoint | Backend endpoint to run a script safely (subprocess) with captured logs + artifacts. | high | backend,security | large |
| MVP | Tools Hub: script catalog | Tool runner UI | Input file picker, config form, run/plan toggle, live logs, artifacts list. | high | frontend,UX | large |
| MVP | - | Report Composer MVP | Schema-based Finding editor + "Generate report bundle" action invoking `report_bundle`. | high | frontend,backend,UX | large |
| MVP | Report Composer MVP | Issue draft exports UI | Generate platform drafts (GitHub/HackerOne/Bugcrowd) and display previews. | medium | frontend,backend | large |
| MVP | - | Findings DB UI | CRUD for findings and statuses; import/export JSON aligned with findings DB schema. | high | frontend,backend | large |
| MVP | - | Logs page MVP | Show tool runs, exit codes, errors; searchable log index. | high | frontend,backend | medium |
| MVP | - | Notifications center MVP | UI to view notifications produced by scripts; basic Slack/email config placeholders. | medium | frontend,UX | medium |
| MVP | - | Help/Docs embedding | Embed MkDocs site or render markdown with in-app search across docs. | medium | frontend,docs | medium |
| MVP | - | Frontend CI pipeline | Add lint/typecheck/unit tests; ensure build passes in CI. | high | frontend,docs | medium |
| MVP | - | Backend CI pipeline | Add unit tests for API and script runner; security checks. | high | backend,security | medium |
| v1.1 | - | Bugcrowd API connector | Implement official API ingestion for `/programs` and scoped fields/includes; store programs in DB. | high | integration,backend | large |
| v1.1 | Bugcrowd API connector | Bugcrowd rate-limiter | Enforce 60 req/min per IP with backoff/jitter and visible budgets. | high | backend,security | medium |
| v1.1 | Bugcrowd API connector | Bugcrowd submissions sync | Sync `/submissions` with date filters/cursors; store status history. | high | integration,backend | large |
| v1.1 | - | Bugcrowd webhook receiver | Receive events; validate signature; store audit events; trigger notifications/tasks. | high | integration,backend,security | large |
| v1.1 | - | GitHub integration (issues) | Connect to GitHub Issues as task sink/source; webhook updates into Task board. | high | integration,backend | large |
| v1.1 | GitHub integration (issues) | Conditional request caching | Use ETag/If-None-Match in polling fallback; reduce rate usage. | medium | backend,integration | medium |
| v1.1 | - | Intigriti connector | Sync programs/submissions; enforce 600 GET/5min and 200 write/5min. | medium | integration,backend | large |
| v1.1 | - | YesWeHack connector | OAuth 2.0 flow and token refresh; ingest invited programs/activities. | medium | integration,backend,security | large |
| v1.1 | - | Analytics dashboards v1 | Implement Program Intelligence + Operations + Reporting dashboards with charts. | high | frontend,backend,UX | large |
| v1.1 | Analytics dashboards v1 | Metrics compute job | Nightly/triggered aggregation jobs; store time series. | high | backend | large |
| v1.1 | - | Task board v1 | Kanban board with linking to findings/programs; basic automation rules. | medium | frontend,backend,UX | large |
| v1.1 | - | Notifications v1 | Connect Slack + SMTP; map repo script behavior into UI workflows. | medium | integration,backend,UX | medium |
| v2.0 | - | Full RBAC + org model | Implement orgs/teams; per-object authorization; audit logs; align to OWASP API risks. | high | backend,security | large |
| v2.0 | - | SSO/OIDC authentication | Add OIDC login and session governance. | medium | backend,security | large |
| v2.0 | - | Secrets vault integration | Replace env-only secrets with vault/KMS; rotation workflows. | high | security,backend | large |
| v2.0 | - | Advanced audit + compliance exports | Export audit events, ingestion provenance, report metadata for compliance. | medium | backend,docs,security | large |
| v2.0 | - | Plugin SDK for connectors/tools | Formal plugin framework for new sources and tools; versioned contracts. | medium | backend,docs | large |
| v2.0 | - | High-scale job runner | Queue + workers; resumable pipelines; retries with idempotency. | medium | backend | large |
| v2.0 | - | Advanced visualization layer | D3-based dataflow/threat overlays and interactive scope maps. | low | frontend,UX | large |

## Processing log

- GitHub issues created: 43 issues (#164 to #206), milestone `Backlog`, labeled `status/triage`.

### MVP
- [#164 - Create command-center architecture ADR](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/164)
- [#165 - Scaffold frontend app](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/165)
- [#166 - Implement app shell navigation](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/166)
- [#167 - Implement dark-yellow design tokens](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/167)
- [#168 - Scaffold backend API](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/168)
- [#169 - Define internal API contract](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/169)
- [#170 - Add persistence layer](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/170)
- [#171 - Implement artifact ingestion layer](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/171)
- [#172 - Build Bounty Feed page](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/172)
- [#173 - Build saved views](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/173)
- [#174 - Build Bounty Detail page](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/174)
- [#175 - Engagement workspace creation](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/175)
- [#176 - ROE acknowledgement UI](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/176)
- [#177 - Tools Hub: script catalog](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/177)
- [#178 - Tool runner API endpoint](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/178)
- [#179 - Tool runner UI](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/179)
- [#180 - Report Composer MVP](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/180)
- [#181 - Issue draft exports UI](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/181)
- [#182 - Findings DB UI](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/182)
- [#183 - Logs page MVP](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/183)
- [#184 - Notifications center MVP](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/184)
- [#185 - Help/Docs embedding](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/185)
- [#186 - Frontend CI pipeline](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/186)
- [#187 - Backend CI pipeline](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/187)

### v1.1
- [#188 - Bugcrowd API connector](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/188)
- [#189 - Bugcrowd rate-limiter](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/189)
- [#190 - Bugcrowd submissions sync](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/190)
- [#191 - Bugcrowd webhook receiver](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/191)
- [#192 - GitHub integration (issues)](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/192)
- [#193 - Conditional request caching](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/193)
- [#194 - Intigriti connector](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/194)
- [#195 - YesWeHack connector](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/195)
- [#196 - Analytics dashboards v1](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/196)
- [#197 - Metrics compute job](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/197)
- [#198 - Task board v1](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/198)
- [#199 - Notifications v1](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/199)

### v2.0
- [#200 - Full RBAC + org model](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/200)
- [#201 - SSO/OIDC authentication](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/201)
- [#202 - Secrets vault integration](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/202)
- [#203 - Advanced audit + compliance exports](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/203)
- [#204 - Plugin SDK for connectors/tools](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/204)
- [#205 - High-scale job runner](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/205)
- [#206 - Advanced visualization layer](https://github.com/raven-dev-ops/Bug_Bounty_AI_Hunter/issues/206)
