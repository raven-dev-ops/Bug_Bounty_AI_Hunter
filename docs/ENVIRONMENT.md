# Environment Variables

This repo reads environment variables for optional integrations. Set them in
your shell and avoid committing secrets.

## External intel
- `SHODAN_API_KEY` for the Shodan provider.
- `CENSYS_API_ID` and `CENSYS_API_SECRET` for the Censys provider.

## Scope import (HackerOne)
- `HACKERONE_API_ID`
- `HACKERONE_API_TOKEN`

## Notifications
- `SLACK_WEBHOOK_URL` for Slack webhook delivery.
- `SMTP_SERVER` for SMTP notifications.
- `SMTP_PORT` (default 25).
- `SMTP_USERNAME` and `SMTP_PASSWORD` when authentication is required.
- `EMAIL_TO` and `EMAIL_FROM` for email delivery.

## Triage (AI)
- `OPENAI_API_KEY` is used by default for the OpenAI provider.
- `api_key_env` in the triage config can point to a different env var.

## Catalog ingestion
- `BBHAI_BOUNTY_TARGETS_URL` overrides the bounty-targets-data dataset URL(s).
- `BBHAI_DISCLOSE_IO_URL` overrides the disclose.io diodb dataset URL(s).
- `BBHAI_PROJECTDISCOVERY_URL` overrides the ProjectDiscovery dataset URL(s).

## Opt-in flags (high-risk actions)
These are optional environment flags for explicit opt-in. They are not enabled
by default and should only be used with written approval.
- `BBHAI_ALLOW_ACTIVE_TESTS=1` to allow active testing stages.
- `BBHAI_ALLOW_BRUTEFORCE=1` to allow credential brute-force testing.
- `BBHAI_ALLOW_SOCIAL_ENGINEERING=1` to allow social engineering simulations.
- `BBHAI_ALLOW_LOAD_TESTS=1` to allow load or stress testing.
- `BBHAI_ALLOW_AI_TRIAGE=1` to allow AI-assisted triage with shared data.

## Safety
Keep secrets out of version control and follow `docs/ROE.md`.
