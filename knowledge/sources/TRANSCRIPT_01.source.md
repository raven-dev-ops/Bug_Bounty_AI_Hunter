---
id: kb-src-0001
title: Transcript 01 - Exploiting shadow data and AI models and embeddings
type: source
status: reviewed
tags: [transcript, ai-security, rag, embeddings, logging, privacy]
source: TRANSCRIPT_01.md
date: 2026-01-14
---

## Summary
Talk focused on AI "shadow data" exposure paths with emphasis on privacy and
cryptography. It highlights fine-tuning, RAG, prompt context, and logs as
primary leakage surfaces.

## Relevance to the project
- Defines where private data sits in AI apps (indexes, prompts, logs).
- Calls out system prompt and RAG context exposure risks.
- Emphasizes logging and retention implications.

## Notable segments
- 10:36-13:41 RAG overview and shadow data inventory.
- 13:41-15:37 Logging and retention implications.
- 15:46-17:34 System prompt and context leakage patterns.

## Derived artifacts
Cards:
- `kb-0001` [Shadow data inventory for AI applications](../cards/kb-0001-shadow-data-inventory.md)
- `kb-0002` [System prompt exposure and reliance risk](../cards/kb-0002-system-prompt-exposure.md)
- `kb-0003` [RAG context leakage risk](../cards/kb-0003-rag-context-leakage.md)
- `kb-0004` [Prompt logging and retention risk](../cards/kb-0004-logging-retention-risk.md)
- `kb-0005` [Fine-tuning data leakage risk](../cards/kb-0005-fine-tuning-data-leakage.md)
- `kb-0006` [Embedding exposure risk](../cards/kb-0006-embedding-exposure.md)

Checklists:
- `kb-checklist-0001` [RAG and logging review checklist](../checklists/rag-logging-review.md)
