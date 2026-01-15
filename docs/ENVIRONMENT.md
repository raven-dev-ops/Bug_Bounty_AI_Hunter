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

## Safety
Keep secrets out of version control and follow `docs/ROE.md`.
