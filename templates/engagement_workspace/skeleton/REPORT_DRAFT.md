# Report Draft: {{platform}} / {{slug}}

Use this as a draft structure for a single finding. Keep reports clear and
reproducible. Avoid real user data.

## Summary
- Title: <short, specific title>
- Severity: <critical/high/medium/low/info>
- Impact (1 sentence): <who is impacted and what breaks>
- Affected feature/component: <name>

## Target
- Engagement: {{engagement_url}}
- In-scope asset: <hostname/app/API>
- Account type used: <anonymous/user/admin/test account>
- Environment/app version: <prod/staging + version/build>

## Reproduction
### Preconditions
- <auth state, feature flags, tenant/org, etc>

### Steps
1. <step>
2. <step>
3. <step>

## Expected vs actual
- Expected: <expected result>
- Actual: <actual result>

## Evidence (minimal)
- Evidence IDs / filenames: <e.g., screenshot-001, log-2026-01-01.txt>
- Request IDs / timestamps: <request_id, trace_id, time>
- Canary string used (if any): <canary>

## Scope and safety notes
- In scope per program rules: <yes/no + link or quote reference>
- Automation/scanning used: <none/approved>
- Stop conditions observed: <none / describe>

## Suggested remediation
- Primary fix: <what to change>
- Defense in depth: <guards, logging, monitoring>
- How to validate the fix: <simple verification steps>
