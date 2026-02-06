# Reporting Examples

These are safe, synthetic examples. Do not include real user data.

## Finding summary example
```
Title: Cross-tenant context leakage in RAG retrieval
Severity: high
Summary: The retrieval pipeline returns chunks from other tenants when a
canary string is used in a scoped query.
Impact: Cross-tenant data exposure risk.
Remediation: Enforce per-tenant ACL checks on retrieval and post-filtering.
Evidence: evidence-001 (sanitized).
```

## Evidence note example
```
Evidence ID: evidence-001
Summary: Sanitized request/response pair with canary string.
Artifacts: evidence/request.txt, evidence/response.txt
Hash: sha256: <redacted>
Redactions: API token and email replaced with <redacted>.
```

## Tool run note example
```
Tool: Nmap 7.x
Mode: passive inventory
Scope: example.com
Output: evidence/nmap_sanitized.txt
Notes: Only open ports recorded. No aggressive flags used.
```
