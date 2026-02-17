---
id: kb-0016
title: Credential exposure in files
type: card
status: reviewed
tags: [secrets, file-systems]
source: TRANSCRIPT_05.md
date: 2026-01-14
---

## Summary
Sensitive credentials can be stored in readable files or data sets due to legacy workflows or misconfigurations.

## Relevance to the project
Guides safe audits for secrets in legacy storage.

## Safe notes
- Scan for credentials in readable data sets using approved tooling.
- Restrict access to sensitive files and directories.
- Use vaults or secret managers where possible.
- Document remediation steps for discovered secrets.

## References
- knowledge/sources/TRANSCRIPT_05.md (approx 292-300)
