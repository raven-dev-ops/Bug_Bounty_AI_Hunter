# Auth container tampering

## Metadata
- ID: kb-0012
- Type: card
- Status: reviewed
- Tags: api-security, auth, mobile
- Source: TRANSCRIPT_04.md
- Date: 2026-01-14

## Summary
Client request containers can be modified or forged; server-side checks must validate auth fields and signatures.

## Relevance to the project
Guides API review for request metadata and signature validation.

## Safe notes
- Validate authentication metadata server-side.
- Use signed requests with server-side verification.
- Treat client metadata as untrusted input.
- Monitor for invalid or replayed requests.

## References
- knowledge/sources/TRANSCRIPT_04.md (approx 214-244)
