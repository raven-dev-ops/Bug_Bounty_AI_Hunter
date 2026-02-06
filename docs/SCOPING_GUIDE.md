# Scoping Guide

Use this guide to interpret program scope safely.

## In-scope basics
- Only test assets explicitly listed as in-scope.
- Respect allowed ports, paths, and environments.
- Follow time windows or maintenance windows.

## Out-of-scope signals
- Assets explicitly listed as out-of-scope.
- Third-party services not owned by the program.
- Production systems when only staging is permitted.

## Restrictions
- Rate limits and concurrency caps are mandatory.
- Avoid exploitation or social engineering unless approved.
- Stop at minimal proof and do not access real user data.

## Ambiguity handling
- Treat unclear scope as out-of-scope.
- Ask for clarification in writing before testing.
