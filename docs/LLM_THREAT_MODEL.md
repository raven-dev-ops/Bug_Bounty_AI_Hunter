# LLM Threat Model (RAG + Agents)

This module documents common threat surfaces for LLM, RAG, and agent systems.
Use it to guide review planning with authorized targets only.

## Core assets
- Prompt context (system prompts, retrieved context, tool outputs).
- Vector store data (embeddings and metadata).
- Tool and plugin permissions.
- Logs, telemetry, and evaluation artifacts.

## Threat surfaces
### Prompt injection at tool boundaries
- Data is treated as instructions when it should be untrusted.
- Tool calls leak secrets or perform unintended actions.

### Cross-tenant data access
- RAG or history access exposes another tenant's data.
- Session isolation failures leak past conversations.

### RAG and vector-store isolation
- Missing ACLs on retrieval filters.
- Export or snapshot endpoints expose embeddings or documents.

### Excessive agency
- Tools execute actions beyond the allowed permission model.
- Missing allowlists or approval steps for high-risk tools.

### Retention and deletion mismatch
- Data deleted in one system persists in logs or indexes.
- Retention policies are inconsistent across stores.

### Encryption-at-rest vs application-layer disclosure
- Encrypted storage does not prevent data leakage at runtime.
- Access control and prompt filtering remain required.

## Mapping to review outputs
- Convert each surface into safe test cases and findings.
- Use canary data and stop conditions per `docs/ROE.md`.
