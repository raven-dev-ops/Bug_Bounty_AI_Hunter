# Tools

This list tracks open-source tools referenced in project sources.
The repo does not bundle or configure these tools.
Use only with explicit authorization per `docs/ROE.md`.
Approval requirements are documented in `docs/TOOLS_POLICY.md`.

## Scope and safety
- Use only on targets with written authorization.
- Stay within declared scope and restrictions.
- Prefer passive collection and read-only checks.
- Avoid exploitation, brute-force, and social engineering unless explicitly permitted.
- Use canary strings and synthetic data whenever possible.
- Stop immediately if real user data appears.
- Record minimal proof and redact secrets.
- Do not add exploit code or target-specific tooling to this repo.

## How tools fit the workflow
- Discovery outputs can inform `schemas/discovery_output.schema.json`.
- Scan planning can reference tools in `schemas/scan_plan.schema.json`.
- Evidence capture should be logged via `docs/EVIDENCE_LOG.md`.
- Reports should cite tool output at a high level, not raw captures.
- Store raw captures outside the repo with encryption at rest.

## Tool notes
| Tool | Project use | Constraints |
| --- | --- | --- |
| Aircrack-ng | Wireless testing in owned labs or approved scope. | Written permission required for wireless tests. |
| Foremost | File recovery from owned disk images. | Use only on data you are authorized to handle. |
| Hashcat | Hash auditing for owned or synthetic data sets. | Avoid credential stuffing and real user data. |
| hping3 | Packet crafting for lab troubleshooting. | No flood or stress testing without approval. |
| John the Ripper | Password auditing for owned hashes. | Use synthetic or sanctioned test data. |
| Metasploit Framework | Lab validation of known issues. | Avoid payloads that persist or alter production. |
| Nikto | Web server baseline scanning. | Keep scans within allowed targets and rates. |
| Nmap | Network discovery and service inventory. | Use allowlists and conservative timing. |
| Skipfish | Web application scanning for issues. | Avoid aggressive modes without approval. |
| Social-Engineer Toolkit (SET) | Approved training simulations. | Written consent and internal test accounts only. |
| sqlmap | SQLi validation in controlled scope. | Prefer safe checks and avoid destructive actions. |
| THC Hydra | Credential audit for authorized accounts. | No brute force without explicit permission. |
| Wireshark | Packet capture for troubleshooting and evidence. | Capture only authorized traffic and redact. |

## Evidence metadata to capture
- Tool name and version.
- Date and time in UTC.
- Scope reference and asset tested.
- Mode used (passive, active, lab).
- Output location and hash.
- Use `python -m scripts.tool_run_log` for structured tool run logs.
