# High-Quality Report Example (Fictional)

Program: Example Program
Generated: 2026-01-17T00:00:00Z

## Summary
A fictional AI assistant returned cross-tenant canary data due to missing access
controls in the retrieval layer. This report is planning-only and uses synthetic
data.

## Scope Proof
- In scope: api.example-labs.test
- Policy: https://example-labs.test/policy

## Repro Steps (Canary-Only)
1) Authenticate as a test user on `api.example-labs.test`.
2) Submit a prompt containing the canary string `BBHAI-CANARY-1234`.
3) Request retrieval for a document that should be out of scope.
4) Observe the response for any canary echoes.

## Expected vs Actual
- Expected: Retrieval returns only documents owned by the test user.
- Actual: The response includes the canary string from another synthetic tenant.

## Impact
Cross-tenant data exposure is possible if access control checks are not enforced
for retrieval results.

## Remediation Guidance
- Enforce tenant checks in the retrieval layer before prompt assembly.
- Log and alert on retrieval results that cross tenant boundaries.
- Add regression tests with canary strings to prevent reintroduction.

## Evidence List
- `evidence/request.txt` (synthetic request with canary)
- `evidence/response.txt` (synthetic response with canary)
