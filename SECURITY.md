# Security Policy

## Scope
This repository is docs-first and does not provide a hosted service. It does
include local automation scripts and a Dockerfile for running workflows.

## Operational safety
- Use only authorized targets with written permission.
- Avoid sending sensitive data to external LLMs unless explicitly approved.
- Treat generated outputs as untrusted until reviewed.
- Protect evidence and logs in line with `docs/ROE.md`.

## Reporting a security issue
If you believe the repository contains sensitive information or a security
issue in its assets, email support@ravdevops.com with the subject
"[SECURITY] ..." and include only the minimum details needed to reproduce.
Do not post secrets or exploit code in public issues.

If you need to report a third-party vulnerability, follow the target program's
published policy and disclosure channel. Do not report third-party issues here.

## Supported versions
Only the latest published guidance is maintained.
