Current repo status (local context)

raven-dev-ops/Bug_Bounty_Hunter_AI is public, Apache-2.0 licensed, and currently a docs-first planning repo.
PDFs are managed locally and are ignored by git.

1) Markdown file to add to the repo

Create a new file at:

docs/PROJECT_OUTLINE.md

Paste the following content as-is:

# Bug_Bounty_Hunter_AI - Project Outline & Roadmap

## 0. Purpose
Build an AI-assisted bug bounty workflow system that:
- Helps a human hunter or security team **discover**, **review**, and **report** vulnerabilities.
- Focuses on **authorized testing only** and bakes in safety/ROE constraints.
- Treats AI systems as security-critical software: RAG, embeddings, fine-tuning, logs, tool-using agents, and integrations.

End goal:
- Turn "tooling + rules + practices" into **individual features** the AI can use via **component repos** linked into this main repo.

## 1. Non-negotiables (Safety / ROE)
- Only operate against targets with explicit authorization (program scope, written permission, or owned systems).
- No exfiltration of real user data. Use **canary strings** and synthetic test data wherever possible.
- Stop at "proof" and document impact using minimal reproduction.
- Any automation must support rate limiting, allowlists, and clear stop conditions.

## 2. Core concept: Component repos as features
This repo is the "hub/orchestrator".
Each capability ships as a separate **component repository** (independently versioned) and is linked here via:
- Git submodules under `components/` (recommended for clean separation), or
- Git subtree (acceptable if submodules are undesirable).

### 2.1 Proposed repo layout (hub)
- `docs/` - architecture, roadmaps, playbooks, contribution rules
- `schemas/` - JSONSchema/YAML for targets, findings, evidence, tasks
- `components/` - git submodules to feature repos
- `knowledge/` - sources, cards, and checklists
- `scripts/` - bootstrap scripts (labels, issue creation, dev setup)
- `examples/` - sample target profiles, sample outputs, canary datasets

## 3. Capabilities the system MUST cover (from "shadow data" AI security)
The AI must be able to discover/review these risk zones in modern AI apps:

### 3.1 AI data "shadow stores"
- Fine-tuning datasets and fine-tuned model behavior leakage
- RAG retrieval stores (vector DBs / search indices)
- Prompt assembly / system prompts / hidden instructions exposure
- Logs + telemetry (prompt logs, retrieval logs, evaluation traces)
- Embeddings/vector exposure (inversion/approx recovery risk)
- Tool-using agents (indirect prompt injection, data->instruction confusion)

### 3.2 What "discover + review" means operationally
For any target (authorized), produce:
1) **Target Profile** (AI architecture map)
   - Does it use RAG? embeddings? fine-tuning? tool calls? third-party LLM APIs?
   - Where is data stored/copied? (indexes, logs, caches, eval tooling)
   - What permissions/ACL model exists and where it can fail.

2) **Threat Model** (AI-specific)
   - Primary attack surfaces: RAG authz, indirect prompt injection, logging leaks, vector exposure
   - Expected impacts: cross-tenant data disclosure, sensitive context leakage, secrets exposure

3) **Test Plan**
   - Safe test cases using canaries and permission boundaries
   - Prioritized by impact and likelihood

4) **Evidence Pack**
   - Minimal reproduction steps
   - Outputs, request IDs, screenshots
   - Remediation guidance

## 4. Component repos (features)
Use a consistent naming convention (suggested prefix: `bbhai-`).

### 4.1 Core / Orchestrator
- `bbhai-core`
  - CLI entrypoint
  - plugin loading (entry points / manifest)
  - common data models (TargetProfile, Finding, Evidence)
  - policy/ROE enforcement hooks

### 4.2 Knowledge + Playbooks
- `bbhai-knowledge`
  - curated knowledge base (transcripts, papers, blog notes)
  - "attack-pattern cards" (safe, non-weaponized)
  - checklists per surface (RAG, embeddings, logs, tool-using agents)

### 4.3 AI-System Discovery
- `bbhai-discovery-ai`
  - guided questionnaire + config parser
  - produces a TargetProfile + dataflow map

### 4.4 Review Modules (each can be separate)
- `bbhai-review-rag`
- `bbhai-review-embeddings`
- `bbhai-review-logging`
- `bbhai-review-agents`

Each module outputs structured Findings + recommended tests.

### 4.5 Reporting + Export
- `bbhai-reporting`
  - bug bounty report templates
  - export to Markdown / JSON
  - export to GitHub Issues "drafts" (paste-ready)

### 4.6 Labs (safe validation)
- `bbhai-labs`
  - synthetic RAG app + vector store + canary dataset
  - regression tests for your review modules (no real data)

## 5. MVP milestones
### Milestone v0.1 - "Documentation-first skeleton"
- Hub repo structure (`docs/`, `schemas/`, `scripts/`, `components/`)
- Label taxonomy + issue templates
- Initial knowledge ingestion (including the shadow-data transcript)
- First checklists: RAG authz, embeddings exposure, logging/telemetry

### Milestone v0.2 - "Target profiling"
- TargetProfile schema + generator
- Dataflow map output (stores + copies + logs + indexes)

### Milestone v0.3 - "Report output"
- Standard report generator + evidence pack format
- GitHub issue export (paste-ready)

### Milestone v0.4 - "Labs + regression"
- Synthetic lab environment
- Automated regression tests for checklists and review modules

## 6. Data formats (schemas)
Define at least:
- `TargetProfile` (what AI features exist, where data flows)
- `TestCase` (safe steps, stop conditions, expected insecure behavior)
- `Finding` (title, severity, affected surface, evidence links, remediation)
- `Evidence` (artifacts, timestamps, request IDs, screenshots)

## 7. Done criteria for "Discover, review, all the stuff mentioned"
The project is "working" when you can:
- Load a TargetProfile (manual YAML) OR generate it via questionnaire,
- Run review modules to produce prioritized tests + findings,
- Generate a report bundle (MD/JSON),
- Export findings into GitHub issues or a bug bounty template,
- Validate the workflow end-to-end against a synthetic lab.


2) GitHub labels + issues to create

You currently have 0 issues in the repo.
Below is a standardized label set and a starter issue backlog.

2.1 Recommended label taxonomy

Priority

priority/p0 - critical / blocking

priority/p1 - high

priority/p2 - medium

priority/p3 - low

Type

type/epic

type/feature

type/docs

type/chore

type/security

Status

status/triage

status/ready

status/in-progress

status/blocked

status/needs-review

Area

area/core

area/knowledge

area/discovery

area/rag

area/embeddings

area/logging

area/agents

area/reporting

area/labs

area/ci

area/docs

Tags

tag/bug-bounty

tag/ai-security

tag/prompt-injection

tag/rag

tag/fine-tuning

tag/embeddings

tag/logging

tag/crypto

2.2 Issue backlog (paste-ready)
Issue 1 - Epic: Define architecture + component repo strategy

Labels: type/epic, priority/p1, area/core, status/triage, tag/ai-security
Body:

Document hub vs component responsibilities.

Decide submodules vs subtree and document the workflow.

Define plugin/manifest interface for components.
Acceptance criteria:

docs/ARCHITECTURE.md exists

docs/COMPONENTS.md exists with linking instructions

Issue 2 - Add hub repo structure (docs/, schemas/, components/, scripts/)

Labels: type/feature, priority/p1, area/core, status/triage
Body:

Add directories and placeholder READMEs.

Add .gitkeep where needed.
Acceptance criteria:

Directory structure exists and is referenced from README.

Issue 3 - Add label set + issue templates

Labels: type/chore, priority/p1, area/docs, status/triage
Body:

Create .github/ISSUE_TEMPLATE/:

Feature request

Bug report (project bug)

Security finding (template for output)

Add label definitions (documented).
Acceptance criteria:

Issue templates appear in GitHub UI

Labels documented in docs/PROJECT_MANAGEMENT.md

Issue 4 - Safety / ROE policy and guardrails (project-wide)

Labels: type/security, priority/p0, area/core, status/triage, tag/bug-bounty
Body:

Add docs/ROE.md with:

authorization requirement

no real-data exfil guidance

canary-first testing

stop conditions
Acceptance criteria:

docs/ROE.md exists and is referenced in README and contribution docs.

Issue 5 - Define schemas: TargetProfile, Finding, Evidence, TestCase

Labels: type/feature, priority/p1, area/core, status/triage
Body:

Add JSONSchema or Pydantic-first design (then export schema).
Acceptance criteria:

schemas/target_profile.schema.json

schemas/finding.schema.json

schemas/evidence.schema.json

schemas/test_case.schema.json

Issue 6 - Knowledge base component: structure + ingestion rules

Labels: type/feature, priority/p1, area/knowledge, status/triage, tag/ai-security
Body:

Create knowledge/ layout (cards, checklists, sources).

Define metadata frontmatter standard.
Acceptance criteria:

docs/KNOWLEDGE_FORMAT.md exists

sample cards exist

Issue 7 - Ingest "shadow data / AI models & embeddings" transcript into knowledge base

Labels: type/docs, priority/p2, area/knowledge, status/triage, tag/rag, tag/embeddings, tag/logging
Body:

Add transcript as a curated source note.

Convert into safe "attack-pattern cards" + defensive checklists.
Acceptance criteria:

knowledge/sources/<...>.md

knowledge/cards/ includes at least:

RAG authz bypass card (safe)

embeddings exposure card (safe)

logging/telemetry shadow-store card

Issue 8 - Discovery: questionnaire -> TargetProfile generator (v0)

Labels: type/feature, priority/p1, area/discovery, status/triage
Body:

Create a YAML questionnaire users fill out (LLM provider, RAG, embeddings, logs, tools).

Generate a TargetProfile JSON from it.
Acceptance criteria:

examples/target_profile_minimal.yaml

generator outputs valid schema

Issue 9 - Review module: RAG security checklist (authz + context handling)

Labels: type/feature, priority/p1, area/rag, status/triage, tag/rag, tag/ai-security
Body:

Provide safe test cases for:

per-tenant retrieval isolation

per-document/per-chunk ACL enforcement

prompt assembly minimization
Acceptance criteria:

outputs TestCase[] with clear stop conditions

Issue 10 - Review module: Embeddings/vector exposure checklist

Labels: type/feature, priority/p1, area/embeddings, status/triage, tag/embeddings, tag/ai-security
Body:

Checks for:

cross-tenant vector access

vector export endpoints

logs leaking embeddings

access controls around vector DB snapshots/backups
Acceptance criteria:

outputs TestCase[] + remediation guidance

Issue 11 - Review module: Logging/telemetry shadow-store checklist

Labels: type/feature, priority/p1, area/logging, status/triage, tag/logging
Body:

Checks for:

prompt logging of retrieved context

retention + access controls

eval tooling storing prompts/responses
Acceptance criteria:

outputs TestCase[] + remediation guidance

Issue 12 - Reporting: generate bug bounty report bundle (MD + JSON)

Labels: type/feature, priority/p1, area/reporting, status/triage, tag/bug-bounty
Body:

Input: Findings + Evidence

Output:

report.md

findings.json
Acceptance criteria:

example output committed under examples/outputs/

Issue 13 - Export: create paste-ready GitHub Issue drafts from Findings

Labels: type/feature, priority/p2, area/reporting, status/triage
Body:

Generate one markdown file per finding formatted as a GitHub issue body.
Acceptance criteria:

examples/exports/github_issues/<...>.md exists

Issue 14 - Labs: synthetic RAG + vector store environment for validation

Labels: type/feature, priority/p2, area/labs, status/triage
Body:

Provide a local lab that:

uses only synthetic data + canaries

supports regression checks for review modules
Acceptance criteria:

labs/ documented with setup + teardown

no real data included

Issue 15 - CI baseline (once code exists): lint + schema validation

Labels: type/chore, priority/p2, area/ci, status/triage
Body:

Add GitHub Actions for:

lint

schema validation on examples

markdown link checks
Acceptance criteria:

CI runs on PRs and main branch

2.3 Optional: one-command bootstrap using GitHub CLI (gh)

You can create labels + issues quickly with the GitHub CLI.

Create scripts/bootstrap_issues.sh locally with the following (trim/add issues as desired):

#!/usr/bin/env bash
set -euo pipefail

REPO="raven-dev-ops/Bug_Bounty_Hunter_AI"
gh repo set-default "$REPO"

# ---- labels: name|color|description
labels=(
  "priority/p0|d73a4a|Critical / blocking"
  "priority/p1|ff4500|High priority"
  "priority/p2|fbca04|Medium priority"
  "priority/p3|cfd3d7|Low priority"

  "type/epic|3e4b9e|Epic"
  "type/feature|a2eeef|Feature"
  "type/docs|0075ca|Documentation"
  "type/chore|cfd3d7|Chore/maintenance"
  "type/security|b60205|Security work"

  "status/triage|ededed|Needs triage"
  "status/ready|0e8a16|Ready"
  "status/in-progress|0052cc|In progress"
  "status/blocked|b60205|Blocked"
  "status/needs-review|5319e7|Needs review"

  "area/core|1d76db|Core"
  "area/knowledge|1d76db|Knowledge"
  "area/discovery|1d76db|Discovery"
  "area/rag|1d76db|RAG"
  "area/embeddings|1d76db|Embeddings"
  "area/logging|1d76db|Logging"
  "area/agents|1d76db|Agents"
  "area/reporting|1d76db|Reporting"
  "area/labs|1d76db|Labs"
  "area/ci|1d76db|CI"
  "area/docs|1d76db|Docs"

  "tag/bug-bounty|bfdadc|Bug bounty"
  "tag/ai-security|bfdadc|AI security"
  "tag/prompt-injection|bfdadc|Prompt injection"
  "tag/rag|bfdadc|RAG"
  "tag/fine-tuning|bfdadc|Fine-tuning"
  "tag/embeddings|bfdadc|Embeddings"
  "tag/logging|bfdadc|Logging"
  "tag/crypto|bfdadc|Cryptography"
)

for item in "${labels[@]}"; do
  IFS='|' read -r name color desc <<<"$item"
  gh label create "$name" --color "$color" --description "$desc" --force
done

# ---- issues (example: add more blocks as needed)
gh issue create \
  --title "Epic: Define architecture + component repo strategy" \
  --label "type/epic,priority/p1,area/core,status/triage,tag/ai-security" \
  --body $'## Goal\nDocument hub vs component responsibilities and the plugin interface.\n\n## Acceptance criteria\n- docs/ARCHITECTURE.md exists\n- docs/COMPONENTS.md exists\n'

gh issue create \
  --title "Add hub repo structure (docs/, schemas/, components/, scripts/)" \
  --label "type/feature,priority/p1,area/core,status/triage" \
  --body $'## Goal\nCreate initial folders and placeholders.\n\n## Acceptance criteria\n- Folder structure exists\n- README links to the new docs\n'


Run:

chmod +x scripts/bootstrap_issues.sh

./scripts/bootstrap_issues.sh

3) "Discover, review, all the stuff mentioned" - how the outline enforces this

The outline above forces the system to:

Discover AI features and data flows via a formal TargetProfile and dataflow mapping.

Review the critical AI risk zones (RAG, embeddings, logs, fine-tuning, tool-using agents) via dedicated modules.

Output structured Findings/TestCases/Evidence so results are directly usable in bug bounty reports and GitHub issues.

If you want this turned into a single consolidated ROADMAP.md at repo root instead of docs/PROJECT_OUTLINE.md, use the same content and adjust the file path.
