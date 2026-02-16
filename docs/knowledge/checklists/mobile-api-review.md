# Mobile API review checklist

## Metadata
- ID: kb-checklist-0003
- Type: checklist
- Status: draft
- Tags: api-security, mobile, auth
- Source: TRANSCRIPT_04.md
- Date: 2026-01-14

## Scope
Review mobile API authentication, request integrity, and client trust boundaries.

## Preconditions
- Written authorization and clear scope.
- ROE reviewed and accepted.

## Review steps
1. Identify request container fields and auth metadata.
2. Verify server-side validation for signatures and tokens.
3. Confirm replay protections and nonce handling.
4. Ensure server-side authorization does not rely on client-only checks.
5. Review error handling for malformed or missing fields.

## Evidence to capture
- Request field inventory and validation notes.
- Minimal reproduction using synthetic data.

## Stop conditions
- Any exposure of real user data or secrets.
- Any scope ambiguity or unapproved testing technique.

## Outputs
- TestCase entries with safe steps and stop conditions.
- Finding drafts for weak validation or trust assumptions.
