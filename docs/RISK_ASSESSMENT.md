# Risk Assessment Template

Use this template before running active tests. Keep entries concise.

```yaml
schema_version: "0.1.0"
id: risk-001
created_at: 2026-02-05T00:00:00Z
owner: your-name
program: Example Program
scope_reference: https://example.com/policy
targets:
  - type: domain
    value: example.com
test_window:
  start: 2026-02-05T00:00:00Z
  end: 2026-02-06T00:00:00Z
approvals:
  - approver: program-owner
    approved_at: 2026-02-05T00:00:00Z
    notes: Written authorization received.
risks:
  - id: risk-001
    description: Possible rate limit impact from scanning.
    likelihood: low
    impact: medium
    mitigations:
      - Keep concurrency at 1 and delay 1 second.
controls:
  rate_limits:
    max_concurrency: 1
    min_delay_seconds: 1.0
  stop_conditions:
    - Real user data observed.
    - Unexpected access obtained.
notes: Use canary strings only.
```
