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
- `knowledge/cards/kb-0005-fine-tuning-data-leakage.md`
- `knowledge/cards/kb-0006-embedding-exposure.md`

Created checklists:
- `knowledge/checklists/rag-logging-review.md`

## TRANSCRIPT_02
Topic: Rapid discovery of bloatware vulnerabilities (local update tools).

Key themes:
- Local web servers, URL validation issues, and installer workflows.
- DLL loading, scheduled tasks, and privilege escalation paths.
- Tooling: process explorer, Frida, static reversing.

Created cards:
- `knowledge/cards/kb-0007-local-service-origin-bypass.md`
- `knowledge/cards/kb-0008-untrusted-update-fetch.md`
- `knowledge/cards/kb-0009-dll-search-order-hijack.md`
- `knowledge/cards/kb-0010-privilege-escalation-path.md`
- `knowledge/cards/kb-0011-toctou-race.md`

Created checklists:
- `knowledge/checklists/update-installer-review.md`

## TRANSCRIPT_03
Topic: Human cognition, AI, and prompt use (philosophical).

Key themes:
- Prompts as tools for interaction and influence.
- Human-in-the-loop and the limits of linear thinking in AI contexts.

Created cards:
- `knowledge/cards/kb-0020-prompt-social-engineering.md`

Created checklists:
- `knowledge/checklists/human-in-loop-review.md`

## TRANSCRIPT_04
Topic: Reverse engineering a mobile API (Pokemon Go).

Key themes:
- API authentication fields, request container metadata.
- Bypassing client defenses (cert pinning, proxying).
- Tooling: Fiddler, JADX, Ghidra/IDA, Frida.

Created cards:
- `knowledge/cards/kb-0012-auth-container-tampering.md`
- `knowledge/cards/kb-0013-client-trust-bypass.md`
- `knowledge/cards/kb-0014-protocol-reverse-engineering.md`

Created checklists:
- `knowledge/checklists/mobile-api-review.md`

## TRANSCRIPT_05
Topic: Mainframe penetration testing and permissions.

Key themes:
- Legacy access control systems and file permission pitfalls.
- Tooling for enumeration and file traversal on mainframes.

Created cards:
- `knowledge/cards/kb-0015-access-control-misconfig.md`
- `knowledge/cards/kb-0016-credential-exposure-in-files.md`
- `knowledge/cards/kb-0017-privileged-library-misuse.md`

Created checklists:
- `knowledge/checklists/legacy-access-control-review.md`

## TRANSCRIPT_06
Topic: Apple endpoint security API for defenders.

Key themes:
- Endpoint Security event types and authorization flows.
- Entitlements, caching, and performance pitfalls.

Created cards:
- `knowledge/cards/kb-0018-authorization-handling-gaps.md`
- `knowledge/cards/kb-0019-telemetry-gaps.md`

Created checklists:
- `knowledge/checklists/endpoint-telemetry-review.md`

## TRANSCRIPT_07
Topic: Starting bug bounties (beginner traps and workflow).

Key themes:
- Preparation and scope discipline before testing.
- Organized recon with notes and response pattern review.
- Tools as support; avoid scanner-driven workflows and false positives.
- Impact-first prioritization and clear, reproducible reporting.
- Reflection and community learning to reduce repeated mistakes.

Created checklists:
- `knowledge/checklists/bug-bounty-starter-workflow.md`
