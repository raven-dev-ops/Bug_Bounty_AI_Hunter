---
id: kb-checklist-0006
title: Human-in-the-loop prompt review checklist
type: checklist
status: reviewed
tags: [human-factors, prompt-injection]
source: TRANSCRIPT_03.md
date: 2026-01-14
---

## Scope
Review human-in-the-loop controls for prompt-driven workflows.

## Preconditions
- Written authorization and clear scope.
- ROE reviewed and accepted.

## Review steps
1. Identify actions that require human approval.
2. Define escalation paths for risky or ambiguous prompts.
3. Add training examples for manipulative prompt patterns.
4. Ensure reviewers can override or stop automated actions.
5. Log decisions without storing sensitive prompt content.

## Evidence to capture
- Approval workflow notes and role definitions.
- Minimal examples using synthetic prompts.

## Stop conditions
- Any exposure of real user data or secrets.
- Any scope ambiguity or unapproved testing technique.

## Outputs
- TestCase entries with safe steps and stop conditions.
- Findings for weak or missing human review gates.
