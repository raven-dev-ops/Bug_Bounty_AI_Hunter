# Platform Export Templates

These templates define platform-specific issue/report drafts produced from
`findings.json` artifacts.

Placeholders use Python `str.format` keys like `{title}`. Unknown keys are left
as `{key}` in the rendered output.

## Files
- `github_issue.md`
  - Used by: `python -m scripts.export_issue_drafts --platform github`
  - Output: Markdown issue drafts for GitHub.
- `hackerone.md`
  - Used by: `python -m scripts.export_issue_drafts --platform hackerone`
  - Output: Markdown report drafts shaped for HackerOne.
- `bugcrowd.md`
  - Used by: `python -m scripts.export_issue_drafts --platform bugcrowd`
  - Output: Markdown report drafts shaped for Bugcrowd.

## Notes
- Outputs include a "Review Required" header. Always verify before submission.
- Do not add exploit payloads. Keep steps safe and reproducible.
- Follow `docs/ROE.md` and the program rules.

