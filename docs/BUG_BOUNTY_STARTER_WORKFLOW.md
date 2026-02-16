# Bug Bounty Starter Workflow Checklist

This checklist is a workflow baseline for authorized bug bounty engagements.
It mirrors `knowledge/checklists/bug-bounty-starter-workflow.md`.

## Summary
Checklist for running a first pass on an authorized bug bounty program without
getting lost in recon or wasting time on false positives.

## Preconditions
- Confirm written authorization and the program rules before touching anything.
- Identify prohibited techniques and rate limits (what would get you banned).

## Scope capture
- Record in-scope targets (domains, apps, APIs, repos).
- Record out-of-scope targets and explicit "do not test" items.
- Record rate limits and prohibited techniques (scanners, brute force, DoS).

## Notes and organization
- Create one folder per engagement.
- Keep a running log with timestamps.
- Maintain an endpoint map (URL, method, params, auth, notes).
- Maintain a hypotheses list (what could break and why).
- Optional: scaffold a workspace with `python -m scripts.init_engagement_workspace --platform bugcrowd --slug <slug>`.

## Recon pass
- Identify key flows (signup, login, reset, payments, admin, settings).
- Enumerate endpoints and parameters from normal usage.
- Record response codes, headers, cookies, and redirects.
- Capture minimal request/response evidence using synthetic data.

## Testing approach
- Use tools to support understanding, not replace it.
- Treat scanner output as untrusted until you reproduce impact.
- Prefer hypothesis-driven testing over random payload spam.
- Start with high-impact boundaries (auth, access control, privacy, logic).
- Avoid scope creep and stop if you drift out of scope.
- Park low-impact or non-reproducible leads and move on.

## Reporting and iteration
- Write reports for someone verifying under time pressure.
- Include step-by-step reproduction and expected vs actual behavior.
- State impact clearly and tie it to the program model.
- Include minimal evidence with no real user data.
- Include exact target identifiers (URL, app version, account type used).
- After each submission, do a short retro and update your workflow.
- Learn from community safely and within ROE and program rules.

## Safe notes
- Follow `docs/ROE.md` and the program's rules at all times.
- Use canary strings and synthetic test data.
- Avoid touching other users' accounts or data.
- Respect rate limits and avoid high-volume automation unless explicitly allowed.

## References
- `ROE.md`
- `SCOPING_GUIDE.md`
- `REPORTING.md`
- Source notes in repo: `knowledge/sources/TRANSCRIPT_07.source.md`
