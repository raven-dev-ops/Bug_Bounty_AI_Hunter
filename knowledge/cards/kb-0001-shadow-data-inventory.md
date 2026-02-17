---
id: kb-0001
title: Shadow data inventory for AI applications
type: card
status: reviewed
tags: [ai-security, rag, embeddings, fine-tuning, logging, privacy]
source: TRANSCRIPT_01.md
date: 2026-01-14
---

## Summary
AI systems often duplicate sensitive data across multiple "shadow stores" such
as fine-tuning datasets, retrieval indexes, prompt assembly, and logs. A clear
inventory is the baseline for safe, authorized review.

## Relevance to the project
- Feeds TargetProfile creation and threat modeling.
- Defines the minimum surfaces that must be reviewed.

## Safe notes
- Identify data stores: fine-tuning datasets, RAG indexes, prompt templates,
  model inputs, logs, caches, and analytics.
- Document where data is copied or transformed, not just its primary location.
- Mark which stores are multi-tenant or shared across environments.
- Treat prompts and logs as data stores, not just telemetry.

## References
- `knowledge/sources/TRANSCRIPT_01.md` (approx 10:36-13:41)
