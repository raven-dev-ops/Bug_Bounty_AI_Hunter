# RAG context leakage risk

## Metadata
- ID: kb-0003
- Type: card
- Status: reviewed
- Tags: ai-security, rag, privacy, access-control
- Source: TRANSCRIPT_01.md
- Date: 2026-01-14

## Summary
RAG systems assemble prompts using retrieved context. If retrieval or access
controls are weak, sensitive context can leak through model outputs.

## Relevance to the project
- Guides review modules for retrieval isolation and prompt assembly.
- Highlights the need for access control checks on retrieved data.

## Safe notes
- Enforce per-tenant and per-document ACLs during retrieval.
- Minimize the context window to only what is required.
- Redact or tokenize sensitive fields before prompt assembly.
- Validate that output filters do not replace access controls.

## References
- `knowledge/sources/TRANSCRIPT_01.md` (approx 10:36-13:41)
