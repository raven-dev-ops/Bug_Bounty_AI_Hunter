# Privilege escalation path in installers

## Metadata
- ID: kb-0010
- Type: card
- Status: draft
- Tags: privilege, installers, windows
- Source: TRANSCRIPT_02.md
- Date: 2026-01-14

## Summary
Installers and updaters can introduce elevation paths if they run actions with unnecessary privileges.

## Relevance to the project
Guides least-privilege review of installation and update flows.

## Safe notes
- Separate privileged actions from user-driven flows.
- Restrict elevated operations to signed and verified code.
- Avoid passing user-controlled paths to elevated tasks.
- Document and review elevation points.

## References
- knowledge/sources/TRANSCRIPT_02.md (approx 236-260)
