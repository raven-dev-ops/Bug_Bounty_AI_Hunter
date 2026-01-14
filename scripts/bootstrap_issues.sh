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

# ---- issues
gh issue create \
  --title "Epic: Define architecture + component repo strategy" \
  --label "type/epic,priority/p1,area/core,status/triage,tag/ai-security" \
  --body $'## Goal\nDocument hub vs component responsibilities.\n\nDecide submodules vs subtree and document the workflow.\n\nDefine plugin/manifest interface for components.\n\n## Acceptance criteria\n- docs/ARCHITECTURE.md exists\n- docs/COMPONENTS.md exists with linking instructions\n'

gh issue create \
  --title "Add hub repo structure (docs/, schemas/, components/, scripts/)" \
  --label "type/feature,priority/p1,area/core,status/triage" \
  --body $'## Goal\nAdd directories and placeholder READMEs.\n\nAdd .gitkeep where needed.\n\n## Acceptance criteria\n- Directory structure exists and is referenced from README\n'

gh issue create \
  --title "Add label set + issue templates" \
  --label "type/chore,priority/p1,area/docs,status/triage" \
  --body $'## Goal\nCreate .github/ISSUE_TEMPLATE/ files:\n- Feature request\n- Bug report (project bug)\n- Security finding (template for output)\n\nAdd label definitions (documented).\n\n## Acceptance criteria\n- Issue templates appear in GitHub UI\n- Labels documented in docs/PROJECT_MANAGEMENT.md\n'

gh issue create \
  --title "Safety / ROE policy and guardrails (project-wide)" \
  --label "type/security,priority/p0,area/core,status/triage,tag/bug-bounty" \
  --body $'## Goal\nAdd docs/ROE.md with:\n- authorization requirement\n- no real-data exfil guidance\n- canary-first testing\n- stop conditions\n\n## Acceptance criteria\n- docs/ROE.md exists and is referenced in README and contribution docs\n'

gh issue create \
  --title "Define schemas: TargetProfile, Finding, Evidence, TestCase" \
  --label "type/feature,priority/p1,area/core,status/triage" \
  --body $'## Goal\nAdd JSONSchema or Pydantic-first design (then export schema).\n\n## Acceptance criteria\n- schemas/target_profile.schema.json\n- schemas/finding.schema.json\n- schemas/evidence.schema.json\n- schemas/test_case.schema.json\n'

gh issue create \
  --title "Knowledge base component: structure + ingestion rules" \
  --label "type/feature,priority/p1,area/knowledge,status/triage,tag/ai-security" \
  --body $'## Goal\nCreate knowledge/ layout (cards, checklists, sources).\n\nDefine metadata frontmatter standard.\n\n## Acceptance criteria\n- docs/KNOWLEDGE_FORMAT.md exists\n- sample cards exist\n'

gh issue create \
  --title "Ingest \"shadow data / AI models & embeddings\" transcript into knowledge base" \
  --label "type/docs,priority/p2,area/knowledge,status/triage,tag/rag,tag/embeddings,tag/logging" \
  --body $'## Goal\nAdd transcript as a curated source note.\n\nConvert into safe \"attack-pattern cards\" + defensive checklists.\n\n## Acceptance criteria\n- knowledge/sources/<...>.md\n- knowledge/cards/ includes at least:\n  - RAG authz bypass card (safe)\n  - embeddings exposure card (safe)\n  - logging/telemetry shadow-store card\n'

gh issue create \
  --title "Discovery: questionnaire -> TargetProfile generator (v0)" \
  --label "type/feature,priority/p1,area/discovery,status/triage" \
  --body $'## Goal\nCreate a YAML questionnaire users fill out (LLM provider, RAG, embeddings, logs, tools).\n\nGenerate a TargetProfile JSON from it.\n\n## Acceptance criteria\n- examples/target_profile_minimal.yaml\n- generator outputs valid schema\n'

gh issue create \
  --title "Review module: RAG security checklist (authz + context handling)" \
  --label "type/feature,priority/p1,area/rag,status/triage,tag/rag,tag/ai-security" \
  --body $'## Goal\nProvide safe test cases for:\n- per-tenant retrieval isolation\n- per-document/per-chunk ACL enforcement\n- prompt assembly minimization\n\n## Acceptance criteria\n- outputs TestCase[] with clear stop conditions\n'

gh issue create \
  --title "Review module: Embeddings/vector exposure checklist" \
  --label "type/feature,priority/p1,area/embeddings,status/triage,tag/embeddings,tag/ai-security" \
  --body $'## Goal\nChecks for:\n- cross-tenant vector access\n- vector export endpoints\n- logs leaking embeddings\n- access controls around vector DB snapshots/backups\n\n## Acceptance criteria\n- outputs TestCase[] + remediation guidance\n'

gh issue create \
  --title "Review module: Logging/telemetry shadow-store checklist" \
  --label "type/feature,priority/p1,area/logging,status/triage,tag/logging" \
  --body $'## Goal\nChecks for:\n- prompt logging of retrieved context\n- retention + access controls\n- eval tooling storing prompts/responses\n\n## Acceptance criteria\n- outputs TestCase[] + remediation guidance\n'

gh issue create \
  --title "Reporting: generate bug bounty report bundle (MD + JSON)" \
  --label "type/feature,priority/p1,area/reporting,status/triage,tag/bug-bounty" \
  --body $'## Goal\nInput: Findings + Evidence\n\nOutput:\n- report.md\n- findings.json\n\n## Acceptance criteria\n- example output committed under examples/outputs/\n'

gh issue create \
  --title "Export: create paste-ready GitHub Issue drafts from Findings" \
  --label "type/feature,priority/p2,area/reporting,status/triage" \
  --body $'## Goal\nGenerate one markdown file per finding formatted as a GitHub issue body.\n\n## Acceptance criteria\n- examples/exports/github_issues/<...>.md exists\n'

gh issue create \
  --title "Labs: synthetic RAG + vector store environment for validation" \
  --label "type/feature,priority/p2,area/labs,status/triage" \
  --body $'## Goal\nProvide a local lab that:\n- uses only synthetic data + canaries\n- supports regression checks for review modules\n\n## Acceptance criteria\n- labs/ documented with setup + teardown\n- no real data included\n'

gh issue create \
  --title "CI baseline (once code exists): lint + schema validation" \
  --label "type/chore,priority/p2,area/ci,status/triage" \
  --body $'## Goal\nAdd GitHub Actions for:\n- lint\n- schema validation on examples\n- markdown link checks\n\n## Acceptance criteria\n- CI runs on PRs and main branch\n'
