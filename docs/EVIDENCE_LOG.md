# Evidence Log

Use this template to record evidence artifacts with minimal sensitive data.
Follow `docs/ROE.md` and stop if real user data or secrets appear.

## Redaction guidance
- Remove tokens, secrets, and PII before storing or sharing evidence.
- Replace sensitive values with `<redacted>` and note the redaction.
- Prefer canary strings and synthetic data in captures.
- Store raw evidence outside the repo with encryption at rest.
- Record hashes and paths instead of raw content when possible.

## Template
```text
Evidence ID:
Date (UTC):
Program / Target:
Scope reference:

Summary:

Artifacts:
- Path:
  Description:
  Hash (sha256):
  Redactions:

Environment:
- Tooling:
- Configuration:
- Network notes:

Chain of custody:
- Captured by:
- Stored at:
- Access notes:

Notes:
```
