# DLL search order hijack risk

## Metadata
- ID: kb-0009
- Type: card
- Status: draft
- Tags: windows, dll, load-path
- Source: TRANSCRIPT_02.md
- Date: 2026-01-14

## Summary
Applications that load DLLs from untrusted paths may execute attacker-controlled libraries.

## Relevance to the project
Useful for review of Windows client tooling and update agents.

## Safe notes
- Use explicit DLL load paths and signed binaries.
- Avoid writable directories in the search path.
- Audit dependency loading for client tools.
- Harden installer and updater permissions.

## References
- knowledge/sources/TRANSCRIPT_02.md (approx 350-450)
