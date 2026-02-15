# Bounty Board

Planning-only summaries of bug bounty engagements and programs.

- Bugcrowd board: `bounty_board/bugcrowd/INDEX.md`
- Regenerate (page 1): `python -m scripts.bugcrowd_board --combined`
- Bugcrowd full brief exports (auth-only, gitignored): `python -m scripts.bugcrowd_briefs --combined --all-pages`
- Optional flags: `--include-target-group-known-issues` (slow), `--include-community` (includes researcher handles)

Notes:
- These files are metadata only and do not grant authorization to test anything.
- Follow `docs/ROE.md` before any testing.
- Do not commit outputs under `bounty_board/bugcrowd_full/`.
