# Hack Types Catalog

This catalog is a non-weaponized list of hack types derived from the
transcripts. It focuses on targets, vulnerability patterns, and safe review
themes. Use only for authorized testing.

## Legend
- Source transcripts: TRANSCRIPT_01 through TRANSCRIPT_06 in `knowledge/sources/`

## Catalog
| ID | Type | Target | Vulnerability pattern | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| HT-001 | System prompt leakage | LLM system prompt | Prompt disclosure/injection | T01 | Prompts are not a security boundary. |
| HT-002 | RAG context leakage | Retrieval index + prompt assembly | Access control gaps, over-broad context | T01 | Retrieval must enforce ACLs. |
| HT-003 | Fine-tuning data leakage | Fine-tuned model | Training data memorization/extraction | T01 | Treat models as data stores. |
| HT-004 | Prompt log exposure | Logging pipelines | Sensitive data retention and access | T01 | Logs can become shadow stores. |
| HT-005 | Embedding exposure | Vector stores | Inversion/approx recovery risk | T01 | Limit export and access. |
| HT-006 | Local service origin bypass | Local update server | Weak origin/host validation | T02 | Trust boundary confusion. |
| HT-007 | Untrusted update fetch | Updater endpoints | Arbitrary download/execute flow | T02 | Validate URL and code signing. |
| HT-008 | DLL search order hijack | Client updater | Untrusted DLL load paths | T02 | Prefer explicit load paths. |
| HT-009 | Privilege escalation path | Installer/updater | UAC or task elevation misuse | T02 | Enforce least privilege. |
| HT-010 | TOCTOU race | Update workflow | Race condition on file swaps | T02 | Validate and lock execution path. |
| HT-011 | Auth container tampering | Mobile API | Forged or modified request metadata | T04 | Validate server-side auth fields. |
| HT-012 | Client trust bypass | Mobile client | Cert pinning or proxy bypass | T04 | Assume client can be modified. |
| HT-013 | Protocol reverse engineering | Mobile API | Weak request signing or parsing | T04 | Use robust auth and signature checks. |
| HT-014 | Access control misconfig | Mainframe data sets | Over-broad permissions/ESM mismatch | T05 | Validate least privilege and ESM rules. |
| HT-015 | Credential exposure in files | Legacy file systems | Secrets stored in readable data sets | T05 | Audit for secrets in files. |
| HT-016 | Privileged library misuse | Mainframe programs | APF or privileged library misuse | T05 | Ensure privileged libs are locked down. |
| HT-017 | Authorization handling gaps | Endpoint security tooling | Incorrect allow/deny flow | T06 | Validate authorization logic. |
| HT-018 | Telemetry gaps | Endpoint security tooling | Cache/coverage blind spots | T06 | Monitor for missed events. |
| HT-019 | Prompt social engineering | Human operators | Manipulative prompts bypass review | T03 | Require human-in-the-loop checks. |
