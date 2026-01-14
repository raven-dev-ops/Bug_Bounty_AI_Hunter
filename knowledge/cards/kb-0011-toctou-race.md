---
id: kb-0011
title: TOCTOU race in update workflows
type: card
status: draft
tags: [race-condition, update-tools]
source: TRANSCRIPT_02.md
date: 2026-01-14
---

## Summary
Time-of-check to time-of-use gaps can allow swapping files between validation and execution.

## Relevance to the project
Applies to updater validation, staging, and execution pipelines.

## Safe notes
- Use atomic replace or verified handles for execution.
- Re-validate artifacts immediately before use.
- Lock or isolate staging directories.
- Track and audit update artifacts.

## References
- knowledge/sources/TRANSCRIPT_02.md (approx 408-420)
