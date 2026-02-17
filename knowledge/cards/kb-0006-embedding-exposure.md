---
id: kb-0006
title: Embedding exposure risk
type: card
status: reviewed
tags: [ai-security, embeddings, privacy]
source: TRANSCRIPT_01.md
date: 2026-01-14
---

## Summary
Vector stores can leak sensitive information if embeddings or indexes are exposed or exported without controls.

## Relevance to the project
Supports review of embedding access, export, and retention policies.

## Safe notes
- Restrict access to vector stores and export endpoints.
- Apply tenant isolation at query and storage layers.
- Treat embeddings as sensitive data artifacts.
- Log access to embedding data with minimal content.

## References
- knowledge/sources/TRANSCRIPT_01.md (approx 10:36-13:41)
