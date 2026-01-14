---
id: kb-0014
title: Protocol reverse engineering risk
type: card
status: draft
tags: [api-security, reverse-engineering]
source: TRANSCRIPT_04.md
date: 2026-01-14
---

## Summary
Custom protocols can be reverse engineered; obscurity does not replace authentication or authorization.

## Relevance to the project
Highlights the need for robust server-side controls regardless of protocol complexity.

## Safe notes
- Design protocols with explicit authentication and integrity checks.
- Document protocol assumptions and threat models.
- Avoid relying on undocumented fields for security.
- Test for malformed or replayed requests safely.

## References
- knowledge/sources/TRANSCRIPT_04.md (approx 158-244)
