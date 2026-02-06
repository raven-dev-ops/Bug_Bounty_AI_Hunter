# Operations

Local operational guidance for evidence handling and workflow hygiene.

## Evidence storage
- Store raw artifacts outside the repo.
- Use encryption at rest and restrict access.
- Keep a hash and chain-of-custody note for critical artifacts.

## Key management
- Store encryption keys outside the repo.
- Rotate keys per engagement when possible.
- Document access approvals and custody.

## Naming and organization
- Use consistent IDs for findings and evidence.
- Separate per-program directories for artifacts.
- Keep sanitized copies in `evidence/` if needed.

## Retention
- Follow program policies and legal requirements.
- Delete raw artifacts when no longer needed.
