# Project Management

## Labels
Priority:
- `prio:P0` - critical / blocking
- `prio:P1` - high
- `prio:P2` - medium
- `prio:P3` - low

Type:
- `type:epic`
- `type:feature`
- `type:research`
- `type:docs`
- `type:test`
- `type:chore`
- `type:security`

Status:
- `status/triage`
- `status/ready`
- `status/in-progress`
- `status/blocked`
- `status/needs-review`

Area:
- `area:schemas`
- `area:storage`
- `area:ingest`
- `area:parsing`
- `area:compliance`
- `area:scoring`
- `area:pdf`
- `area:reporting`
- `area:llm-threat-model`
- `area:cli`
- `area:ci`
- `area:tests`
- `area:docs`
- `area:core`
- `area:knowledge`
- `area:discovery`
- `area:rag`
- `area:embeddings`
- `area:logging`
- `area:agents`
- `area:labs`

Risk:
- `risk:legal`
- `risk:tos`
- `risk:data-privacy`
- `risk:rate-limit`

Meta:
- `needs:decision`
- `good-first-issue`

Tags:
- `tag/bug-bounty`
- `tag/ai-security`
- `tag/prompt-injection`
- `tag/rag`
- `tag/fine-tuning`
- `tag/embeddings`
- `tag/logging`
- `tag/crypto`

## Issue templates
Issue templates live in `.github/ISSUE_TEMPLATE/`.

## Bootstrapping labels and issues
If you want to create labels and the starter backlog via GitHub CLI, use:
- `scripts/bootstrap_issues.sh`
