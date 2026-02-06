# Redaction Guide

Redact sensitive data before storing or sharing evidence. Use this guide with
`docs/EVIDENCE_LOG.md` and `scripts/redact_evidence.py`.

## Redaction rules
- Replace secrets, tokens, and PII with `<redacted>`.
- Keep just enough context to understand impact.
- Avoid storing raw payloads in the repo.

## Common patterns to redact
- API keys and bearer tokens.
- Session cookies and CSRF tokens.
- Email addresses and phone numbers.
- Full names when not required.
- IP addresses tied to real users.

## Recommended workflow
1. Capture raw evidence outside the repo.
2. Create a sanitized copy for reporting.
3. Hash the sanitized file and log it.
4. Record the redaction notes in the evidence log.

## Example note
`Replaced API token and user email with <redacted>.`
