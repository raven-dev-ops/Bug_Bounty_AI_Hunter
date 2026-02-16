# Local service origin bypass

## Metadata
- ID: kb-0007
- Type: card
- Status: draft
- Tags: update-tools, local-services, validation
- Source: TRANSCRIPT_02.md
- Date: 2026-01-14

## Summary
Local services that trust browser-origin requests can be abused if origin validation is weak or string-based.

## Relevance to the project
Highlights trust boundary issues in local update agents and helper services.

## Safe notes
- Validate origins with strict allowlists, not substring checks.
- Use authenticated channels between browser and local services.
- Disable sensitive actions from untrusted origins.
- Log and rate-limit local service requests.

## References
- knowledge/sources/TRANSCRIPT_02.md (approx 24-196)
