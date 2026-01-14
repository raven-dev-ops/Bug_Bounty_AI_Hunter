# Project Management

## Labels
Priority:
- `priority/p0` - critical / blocking
- `priority/p1` - high
- `priority/p2` - medium
- `priority/p3` - low

Type:
- `type/epic`
- `type/feature`
- `type/docs`
- `type/chore`
- `type/security`

Status:
- `status/triage`
- `status/ready`
- `status/in-progress`
- `status/blocked`
- `status/needs-review`

Area:
- `area/core`
- `area/knowledge`
- `area/discovery`
- `area/rag`
- `area/embeddings`
- `area/logging`
- `area/agents`
- `area/reporting`
- `area/labs`
- `area/ci`
- `area/docs`

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
