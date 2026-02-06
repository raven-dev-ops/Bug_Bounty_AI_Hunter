# Threat Modeling Method

Use this method to keep threat models consistent and safe. Align outputs with
`schemas/threat_model.schema.json` and `schemas/dataflow_map.schema.json`.

## 1. Scope and assumptions
- Confirm written authorization and in-scope assets.
- Record constraints and stop conditions.
- Define the AI surface coverage (RAG, embeddings, logging, agents).

## 2. Asset and data inventory
- List data stores, logs, caches, and indices.
- Identify trust boundaries and access controls.
- Map external dependencies and third-party APIs.

## 3. Dataflow map
- Describe how prompts, context, embeddings, and logs move.
- Keep the map high level and avoid real user data.

## 4. Threat enumeration
- Use known AI risk zones: prompt injection, data leakage, logging retention.
- Add authorization and isolation risks for multi-tenant systems.
- Include tool-use and agent autonomy risks.

## 5. Impact and likelihood
- Describe potential impact in business terms.
- Note likelihood based on exposure and controls.
- Flag unknowns that need validation.

## 6. Safe test cases
- Propose minimal, non-destructive checks.
- Use canaries and synthetic data.
- Define clear stop conditions.

## 7. Mitigations and follow-up
- Recommend least-privilege and logging controls.
- Identify monitoring and alerting gaps.
- Capture remediation guidance for reports.
