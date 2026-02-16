# Path: Bug Bounty Hunter

This path focuses on running the workflow end to end for authorized targets.

## Steps
1. Read `ROE.md` and confirm written authorization.
2. Optional: scaffold a local engagement workspace with `python -m scripts.init_engagement_workspace --platform bugcrowd --slug <slug>`.
3. Build a TargetProfile via `TARGET_PROFILE.md`.
4. Generate a threat model and dataflow map (`THREAT_MODEL.md`).
5. Plan the pipeline (`PIPELINE.md`) and review the scan plan.
6. Capture evidence and produce reports (`REPORTING.md`).

## Helpful references
- `HACK_TYPES.md` for coverage ideas.
- `NOTIFICATIONS.md` for alerts and handoffs.
- `knowledge/checklists/bug-bounty-starter-workflow.md` for a baseline workflow and report habits.
