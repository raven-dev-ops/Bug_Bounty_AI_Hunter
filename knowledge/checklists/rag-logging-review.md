---
id: kb-checklist-0001
title: RAG and logging review checklist
type: checklist
status: reviewed
tags: [rag, logging, privacy, access-control]
source: TRANSCRIPT_01.md
date: 2026-01-14
---

## Scope
Review RAG retrieval, prompt assembly, and logging behavior for authorized
targets.

Reference: `knowledge/cards/kb-0004-logging-retention-risk.md`.

## Preconditions
- Written authorization and clear scope.
- Canary or synthetic data available.
- ROE reviewed and accepted.

## Review steps
1. Map data stores: retrieval index, prompt templates, logs, caches.
2. Verify retrieval access control: per-tenant and per-document checks.
3. Inspect prompt assembly for over-collection of context.
4. Validate output handling for sensitive data exposure.
5. Review logging paths for prompts and retrieved context.
6. Confirm retention and access policies for logs and exports.

## Evidence to capture
- Data flow notes showing where context is stored or logged.
- Minimal examples using canary data.
- Policy references for retention and access controls.

## Stop conditions
- Any exposure of real user data or secrets.
- Any scope ambiguity or unapproved testing technique.

## Outputs
- TestCase entries with safe steps and stop conditions.
- Finding drafts if access controls or logging safeguards fail.

## Example test cases
- `examples/test_case_rag_minimal.json`
- `examples/test_case_logging_minimal.json`
