# Transcript Review

This file summarizes the transcript set and maps each to knowledge artifacts.
Sources and source notes live under `knowledge/sources/`.

## Summary
- TRANSCRIPT_01 is strongly aligned with AI shadow data, prompt leakage, and RAG.
- TRANSCRIPT_02 through TRANSCRIPT_06 are general security talks. They can
  inform tooling and methodology but are not AI-specific.

## TRANSCRIPT_01
Topic: Exploiting shadow data and AI models and embeddings (privacy and crypto).

Key themes:
- Private data exposure paths: fine-tuning, RAG retrieval stores, prompt logs.
- System prompt and RAG context extraction via prompt attacks and translation.
- Log retention risks and legal/logging pressure.
- Emphasis on safe handling of sensitive data and scope boundaries.

Created cards:
- `knowledge/cards/kb-0001-shadow-data-inventory.md`
- `knowledge/cards/kb-0002-system-prompt-exposure.md`
- `knowledge/cards/kb-0003-rag-context-leakage.md`
- `knowledge/cards/kb-0004-logging-retention-risk.md`

Created checklist:
- `knowledge/checklists/rag-logging-review.md`

## TRANSCRIPT_02
Topic: Rapid discovery of bloatware vulnerabilities (local update tools).

Key themes:
- Local web servers, URL validation issues, and installer workflows.
- DLL loading, scheduled tasks, and privilege escalation paths.
- Tooling: process explorer, Frida, static reversing.

Candidate cards:
- Local update mechanisms as attack surface (general).
- Safe reverse engineering workflow for client tools (general).

## TRANSCRIPT_03
Topic: Human cognition, AI, and prompt use (philosophical).

Key themes:
- Prompts as tools for interaction and influence.
- Human-in-the-loop and the limits of linear thinking in AI contexts.

Candidate cards:
- Human factors in prompt design and social engineering parallels.

## TRANSCRIPT_04
Topic: Reverse engineering a mobile API (Pokemon Go).

Key themes:
- API authentication fields, request container metadata.
- Bypassing client defenses (cert pinning, proxying).
- Tooling: Fiddler, JADX, Ghidra/IDA, Frida.

Candidate cards:
- API reverse engineering workflow (general).
- Auth container tampering risks (general).

## TRANSCRIPT_05
Topic: Mainframe penetration testing and permissions.

Key themes:
- Legacy access control systems and file permission pitfalls.
- Tooling for enumeration and file traversal on mainframes.

Candidate cards:
- Legacy access controls and least privilege checks (general).

## TRANSCRIPT_06
Topic: Apple endpoint security API for defenders.

Key themes:
- Endpoint Security event types and authorization flows.
- Entitlements, caching, and performance pitfalls.

Candidate cards:
- Endpoint telemetry considerations for defensive tools (general).
