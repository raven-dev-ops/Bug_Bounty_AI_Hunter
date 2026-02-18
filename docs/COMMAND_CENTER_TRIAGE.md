# Command Center Triage Ledger (Issues #164-#206)

This file records triage completion for the command-center backlog seeded as
GitHub issues `#164` through `#206`.

Triage completion definition used for these issues:
- Scope statement is captured and accepted.
- Delivery success criteria are captured and accepted.
- Milestone, effort, and area labels are present.

Result: each triage stub issue in this range is now complete from a triage
standpoint and can be closed. Delivery is tracked in repo docs and roadmap.

Last updated: 2026-02-18

| Issue | Title | Confirmed Scope | Confirmed Success Criteria | Milestone | Effort |
|---|---|---|---|---|---|
| #164 | Create command-center architecture ADR | Write an Architecture Decision Record describing SPA + API + DB + worker model and how it maps to existing scripts/schemas. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | small |
| #165 | Scaffold frontend app | Create frontend project (React/TS + Tailwind) with routing and layout shell. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #166 | Implement app shell navigation | Left nav + top command bar + command palette skeleton; responsive layout. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #167 | Implement dark-yellow design tokens | Add CSS variables, Tailwind config, theme switcher; enforce contrast targets. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #168 | Scaffold backend API | Add backend service (e.g., FastAPI) providing REST endpoints for programs/findings/workspaces/runs. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #169 | Define internal API contract | OpenAPI spec for core resources and job runner endpoints. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #170 | Add persistence layer | SQLite (MVP) schema for programs, workspaces, findings, evidence metadata, tool runs, tasks. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #171 | Implement artifact ingestion layer | Import existing `bounty_board/` markdown + registry JSON + findings DB into DB. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #172 | Build Bounty Feed page | Feed table with filters/sorts; reads from imported bounty board + program registry data. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #173 | Build saved views | Save filter presets per user (local for MVP). | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #174 | Build Bounty Detail page | Program overview, provenance/conflicts viewer, actions (create workspace). | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #175 | Engagement workspace creation | Create workspace record; scaffold ROE_ACK + pipeline config + report dirs (mirror CLI behavior). | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #176 | ROE acknowledgement UI | Form to populate `acknowledged_at`, `acknowledged_by`, `authorized_target`; enforce run gating. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #177 | Tools Hub: script catalog | Show repo tool catalog (grouped by pipeline stage) with docs and run buttons. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #178 | Tool runner API endpoint | Backend endpoint to run a script safely (subprocess) with captured logs + artifacts. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #179 | Tool runner UI | Input file picker, config form, run/plan toggle, live logs, artifacts list. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #180 | Report Composer MVP | Schema-based Finding editor + "Generate report bundle" action invoking `report_bundle`. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #181 | Issue draft exports UI | Generate platform drafts (GitHub/HackerOne/Bugcrowd) and display previews. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #182 | Findings DB UI | CRUD for findings and statuses; import/export JSON aligned with findings DB schema. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | large |
| #183 | Logs page MVP | Show tool runs, exit codes, errors; searchable log index. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #184 | Notifications center MVP | UI to view notifications produced by scripts; basic Slack/email config placeholders. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #185 | Help/Docs embedding | Embed MkDocs site or render markdown with in-app search across docs. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #186 | Frontend CI pipeline | Add lint/typecheck/unit tests; ensure build passes in CI. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #187 | Backend CI pipeline | Add unit tests for API and script runner; security checks. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | MVP | medium |
| #188 | Bugcrowd API connector | Implement official API ingestion for `/programs` and scoped fields/includes; store programs in DB. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | large |
| #189 | Bugcrowd rate-limiter | Enforce 60 req/min per IP with backoff/jitter and visible budgets. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | medium |
| #190 | Bugcrowd submissions sync | Sync `/submissions` with date filters/cursors; store status history. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | large |
| #191 | Bugcrowd webhook receiver | Receive events; validate signature; store audit events; trigger notifications/tasks. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | large |
| #192 | GitHub integration (issues) | Connect to GitHub Issues as task sink/source; webhook updates into Task board. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | large |
| #193 | Conditional request caching | Use ETag/If-None-Match in polling fallback; reduce rate usage. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | medium |
| #194 | Intigriti connector | Sync programs/submissions; enforce 600 GET/5min and 200 write/5min. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | large |
| #195 | YesWeHack connector | OAuth 2.0 flow and token refresh; ingest invited programs/activities. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | large |
| #196 | Analytics dashboards v1 | Implement Program Intelligence + Operations + Reporting dashboards with charts. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | large |
| #197 | Metrics compute job | Nightly/triggered aggregation jobs; store time series. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | large |
| #198 | Task board v1 | Kanban board with linking to findings/programs; basic automation rules. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | large |
| #199 | Notifications v1 | Connect Slack + SMTP; map repo script behavior into UI workflows. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v1.1 | medium |
| #200 | Full RBAC + org model | Implement orgs/teams; per-object authorization; audit logs; align to OWASP API risks. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v2.0 | large |
| #201 | SSO/OIDC authentication | Add OIDC login and session governance. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v2.0 | large |
| #202 | Secrets vault integration | Replace env-only secrets with vault/KMS; rotation workflows. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v2.0 | large |
| #203 | Advanced audit + compliance exports | Export audit events, ingestion provenance, report metadata for compliance. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v2.0 | large |
| #204 | Plugin SDK for connectors/tools | Formal plugin framework for new sources and tools; versioned contracts. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v2.0 | large |
| #205 | High-scale job runner | Queue + workers; resumable pipelines; retries with idempotency. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v2.0 | large |
| #206 | Advanced visualization layer | D3-based dataflow/threat overlays and interactive scope maps. | Goal scope accepted in triage; implementation definition recorded in roadmap/docs before delivery. | v2.0 | large |
