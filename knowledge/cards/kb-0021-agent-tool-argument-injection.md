---
id: kb-0021
title: Agent tool argument injection risk
type: card
status: reviewed
tags: [ai-security, agents, prompt-injection, access-control]
source: project
date: 2026-02-05
---

## Summary
Agent workflows can pass untrusted text into tool arguments. This can change
tool behavior or expand scope unintentionally.

## Relevance to the project
Supports safe review of tool-using agents and their input boundaries.

## Safe notes
- Require structured arguments and strict allowlists.
- Separate user input from tool instructions.
- Log tool invocations with redaction.
- Stop if unexpected access is observed.

## References
- `docs/ROE.md`
- `knowledge/checklists/agents-review.md`
