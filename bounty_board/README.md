# Bounty Board

Planning-only summaries of bug bounty engagements and programs.

- Bugcrowd board: `bounty_board/bugcrowd/INDEX.md`
- Bugcrowd VDP board: `bounty_board/bugcrowd_vdp/INDEX.md`
- Regenerate (page 1): `python -m scripts.bugcrowd_board --combined`
- Regenerate VDP (all pages): `python -m scripts.bugcrowd_board --category vdp --combined --all-pages --out-dir bounty_board/bugcrowd_vdp`
- Bugcrowd full brief exports (auth-only, gitignored): `python -m scripts.bugcrowd_briefs --combined --all-pages`
- Postprocess local full exports (add rendered sections + `INDEX.md`): `python -m scripts.bugcrowd_full_postprocess`
- Optional flags: `--include-target-group-known-issues` (slow), `--include-community` (includes researcher handles)

Notes:
- These files are metadata only and do not grant authorization to test anything.
- Follow `docs/ROE.md` before any testing.
- Do not commit outputs under `bounty_board/bugcrowd_full/`.
