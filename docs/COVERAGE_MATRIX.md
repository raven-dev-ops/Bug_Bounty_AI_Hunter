# Coverage Matrix

High-level mapping between repo assets and common AI security taxonomies.
Validate against program scope and `docs/ROE.md` before use.

## Metadata
- Schema version: 0.1.0
- Updated at: 2026-01-15

## Sources
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- MITRE ATLAS: https://atlas.mitre.org/
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework

## OWASP LLM Top 10

| ID | Name | Status | Coverage | Notes |
| --- | --- | --- | --- | --- |
| LLM01 | Prompt Injection | partial | `knowledge/checklists/agents-review.md`, `knowledge/checklists/rag-logging-review.md`, `knowledge/cards/kb-0020-prompt-social-engineering.md`, `docs/HACK_TYPES.md` | Indirect prompt injection and tool use review guidance. |
| LLM02 | Insecure Output Handling | planned | `docs/REPORTING.md` | Add output review markers and sanitization guidance. Issues: #78 |
| LLM03 | Training Data Poisoning | partial | `docs/THREAT_MODEL.md`, `knowledge/cards/kb-0005-fine-tuning-data-leakage.md`, `docs/HACK_TYPES.md` | Threat modeling and fine-tuning data handling risks. |
| LLM04 | Model Denial of Service | partial | `docs/PIPELINE.md`, `docs/ROE.md` | Rate limiting and safe execution expectations. |
| LLM05 | Supply Chain Vulnerabilities | partial | `knowledge/checklists/update-installer-review.md`, `knowledge/cards/kb-0008-untrusted-update-fetch.md`, `knowledge/cards/kb-0009-dll-search-order-hijack.md` | Update and dependency integrity review. |
| LLM06 | Sensitive Information Disclosure | partial | `knowledge/checklists/rag-logging-review.md`, `knowledge/cards/kb-0003-rag-context-leakage.md`, `knowledge/cards/kb-0004-logging-retention-risk.md`, `docs/ROE.md` | RAG and logging exposure guidance. |
| LLM07 | Insecure Plugin Design | partial | `knowledge/checklists/agents-review.md`, `docs/COMPONENT_MANIFEST.md`, `docs/COMPONENTS.md` | Agent and component integration expectations. |
| LLM08 | Excessive Agency | partial | `knowledge/checklists/agents-review.md`, `docs/ROE.md` | Tool use and approval guardrails. |
| LLM09 | Overreliance | planned | `docs/TRIAGE.md`, `docs/REPORTING.md` | Add explicit human review checkpoints. |
| LLM10 | Model Theft | planned | `docs/THREAT_MODEL.md`, `docs/HACK_TYPES.md` | Model protection and extraction risks are documented at a high level. |

## MITRE ATLAS (High-level tactics)

| ID | Name | Status | Coverage | Notes |
| --- | --- | --- | --- | --- |
| - | Reconnaissance | partial | `docs/PIPELINE.md`, `scripts/import_scope.py`, `scripts/discovery_assets.py` | Scope import and discovery planning. |
| - | Resource Development | partial | `docs/KNOWLEDGE_FORMAT.md`, `knowledge/INDEX.md` | Knowledge sourcing and curation. |
| - | Initial Access | planned | `docs/THREAT_MODEL.md` | Threat modeling only; no exploitation. |
| - | Execution | partial | `docs/PIPELINE.md`, `scripts/pipeline_orchestrator.py` | Orchestrated planning and run modes. |
| - | Collection | partial | `docs/REPORTING.md`, `evidence/README.md` | Evidence capture and reporting guidance. |
| - | Impact | partial | `docs/TRIAGE.md`, `docs/REPORTING.md` | Severity and impact framing in reports. |

## NIST AI RMF Functions

| ID | Name | Status | Coverage | Notes |
| --- | --- | --- | --- | --- |
| GOVERN | Govern | partial | `docs/ROE.md`, `docs/PROJECT_MANAGEMENT.md`, `SECURITY.md` | Governance, safety, and disclosure expectations. |
| MAP | Map | partial | `docs/TARGET_PROFILE.md`, `docs/THREAT_MODEL.md`, `scripts/target_profile_generate.py`, `scripts/dataflow_map.py` | Target profiling and dataflow modeling. |
| MEASURE | Measure | partial | `docs/TESTING.md`, `docs/TRIAGE.md`, `scripts/scan_templates.py` | Test planning and triage measurement. |
| MANAGE | Manage | partial | `docs/REPORTING.md`, `docs/NOTIFICATIONS.md`, `docs/RELEASE_CHECKLIST.md` | Reporting, notification, and release practices. |
