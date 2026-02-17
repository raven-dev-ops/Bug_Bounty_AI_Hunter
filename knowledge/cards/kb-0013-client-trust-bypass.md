---
id: kb-0013
title: Client trust bypass
type: card
status: reviewed
tags: [api-security, client-trust]
source: TRANSCRIPT_04.md
date: 2026-01-14
---

## Summary
Client-side controls can be bypassed; security must rely on server-side enforcement.

## Relevance to the project
Reinforces server-side validation and auth checks.

## Safe notes
- Assume clients can be modified or replayed.
- Enforce auth, rate limits, and input validation server-side.
- Do not rely on client-side secrets for authorization.
- Log anomalies without storing sensitive payloads.

## References
- knowledge/sources/TRANSCRIPT_04.md (approx 108-126)
