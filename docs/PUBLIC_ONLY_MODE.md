# Public-Only Mode

Public-only mode is for cataloging **public** program metadata only. It is not
for testing or probing targets.

## What this mode does
- Collects publicly available program details (name, platform, policy URL).
- Stores high-level scope summaries and restrictions for planning.
- Records provenance (source, fetch date, parser version).

## What this mode does not do
- No scanning, testing, or exploitation of targets.
- No interaction with targets beyond public pages or APIs with permission.
- No encouragement to bypass terms of service or rules of engagement.

## Separation from testing
- Catalog outputs are informational and planning-only.
- Any testing requires explicit authorization and a written ROE.
- Follow `docs/ROE.md` before using any workflow that touches targets.

## Guardrails
- Use public-only sources and respect robots/TOS constraints.
- Apply rate limits and caching to avoid load or scraping abuse.
- Do not store secrets or private data in catalog entries.
- Keep catalog artifacts under `data/` and out of `output/` or `evidence/`.

## Audit logging
- Each run writes an audit log and summaries under `data/ingestion_audit/`.
- Logs and summaries capture counts and timings only; no response bodies or target content.

## CLI
- Use `bbhai catalog build --public-only` for public-only ingestion.
- The catalog builder respects robots.txt checks by default.
