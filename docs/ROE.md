# Rules of Engagement (ROE)

## Authorization required
- Test only targets you explicitly own or have written authorization to test.
- If a target or method is not clearly in scope, treat it as out of scope.

## Safety and data handling
- Use canary strings and synthetic data whenever possible.
- Do not exfiltrate real user data or secrets.
- Stop at minimal proof and avoid unnecessary access.

## Automation guardrails
- Use allowlists, rate limits, and clear stop conditions.
- Avoid load or stress testing unless it is explicitly permitted.

## ROE acknowledgement
Before running any pipeline in run mode, record authorization in a local
`ROE_ACK.yaml` file or pass `--ack-authorization` to acknowledge it explicitly.

## Evidence and reporting
- Record minimal reproduction steps and relevant request IDs.
- Capture only the minimum evidence needed to demonstrate impact.

## Stop conditions
- Stop immediately if you encounter real user data, secrets, or unexpected access.
- Pause and re-check authorization if scope or rules are unclear.
