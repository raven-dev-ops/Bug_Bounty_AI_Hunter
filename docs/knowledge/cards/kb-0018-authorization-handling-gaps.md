# Authorization handling gaps in telemetry tools

## Metadata
- ID: kb-0018
- Type: card
- Status: draft
- Tags: endpoint-security, authorization
- Source: TRANSCRIPT_06.md
- Date: 2026-01-14

## Summary
Endpoint security tooling can make incorrect allow or deny decisions if authorization events are mishandled.

## Relevance to the project
Guides validation of allow/deny flows and error handling.

## Safe notes
- Verify correct handling of authorization event responses.
- Fail closed when authorization decisions cannot be made.
- Test error paths and timeouts.
- Document decision logic and review it regularly.

## References
- knowledge/sources/TRANSCRIPT_06.md (approx 146-182)
