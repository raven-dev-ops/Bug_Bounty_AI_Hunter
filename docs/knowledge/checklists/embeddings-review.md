# Embeddings and vector exposure review checklist

## Metadata
- ID: kb-checklist-0007
- Type: checklist
- Status: reviewed
- Tags: embeddings, ai-security, access-control, logging
- Source: kb-0006-embedding-exposure
- Date: 2026-01-15

## Scope
Review embedding generation, storage, export, and logging for authorized
targets.

Reference: `knowledge/cards/kb-0006-embedding-exposure.md`.

## Preconditions
- Written authorization and clear scope.
- Canary or synthetic data available.
- ROE reviewed and accepted.

## Review steps
1. Map embedding pipelines and vector store locations.
2. Confirm access controls for vector queries and exports.
3. Review snapshot, backup, and export controls for embeddings.
4. Inspect logging for embedding payloads or derived identifiers.
5. Validate retention and deletion policies for embeddings.

## Evidence to capture
- Notes on vector store access controls and export paths.
- Minimal examples using canary data.
- Policy references for retention and access controls.

## Stop conditions
- Any exposure of real user data or secrets.
- Any scope ambiguity or unapproved testing technique.

## Outputs
- TestCase entries with safe steps and stop conditions.
- Finding drafts if access or export safeguards fail.

## Example test cases
- `examples/test_case_embedding_minimal.json`
