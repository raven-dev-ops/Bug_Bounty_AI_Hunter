# Safe Defaults

These defaults are conservative. Tune only with explicit approval and written
scope. Apply the strictest constraint that applies.

## Rate limits
- `max_concurrency`: 1
- `min_delay_seconds`: 1.0
- `timeout_seconds`: 30
- `stage_timeout_seconds`: 600

## Request budgeting
- `request_budget`: 250 per stage
- `token_budget`: 10000 per stage (if AI calls are enabled)

## Stop conditions
- Real user data is observed.
- Unexpected access is obtained.
- Rate limits are exceeded.
- Scope is ambiguous or changed.

## Evidence handling defaults
- Use canary strings and synthetic data.
- Record only minimal proof.
- Redact secrets before storage.
- Store raw artifacts outside the repo.

## When to tighten further
- Production systems without test environments.
- Sensitive data classes (PII, financial, health).
- Programs with explicit low-impact requirements.
