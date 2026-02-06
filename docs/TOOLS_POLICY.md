# Tools Policy

This policy defines approval requirements for tool usage. It complements
`docs/ROE.md` and `docs/TOOLS.md`.

## Tool classes

### Passive observation
Examples: inventory, metadata review, static analysis.
- Approval: standard written authorization.
- Constraints: stay within scope, do not collect real user data.

### Active probing
Examples: low-rate scanning, authenticated checks, configuration validation.
- Approval: explicit scope approval with rate limits.
- Constraints: follow stated windows and throttles.

### Exploitation and credential testing
Examples: exploit frameworks, brute-force, password cracking, privilege testing.
- Approval: written authorization that explicitly permits the action.
- Constraints: use lab or synthetic data when possible.

### Social engineering and phishing simulations
Examples: simulated phishing, SET training flows.
- Approval: written authorization from program owner and participating users.
- Constraints: use test accounts and internal targets only.

### Load or stress testing
Examples: traffic floods, concurrency spikes, fuzzing at scale.
- Approval: written authorization with safe limits and monitoring plan.
- Constraints: stop at first instability.

## Documentation requirements
- Record tool name, version, and mode (passive or active).
- Capture timestamps and scope references.
- Store raw outputs outside the repo with encryption at rest.
- Redact secrets and PII before sharing.

## Violations and stop conditions
- Stop immediately if real user data appears.
- Pause if scope or rules are unclear.
- Escalate to the program owner before resuming.
