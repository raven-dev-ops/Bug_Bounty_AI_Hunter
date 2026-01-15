# Notifications

Notifications summarize findings or other outputs for console, file, Slack, or
email delivery. The file channel writes a schema-compliant payload; other
channels send a summary derived from the input.

## Channels

### Console
- Default output; prints a summary to stdout.

### File
- Writes a JSON payload for downstream handling.
- Use `--output` to choose the file path.

### Slack
- Requires `SLACK_WEBHOOK_URL`.
- Add `--send` to post; omit to preview the payload.

### Email (SMTP)
- Requires `SMTP_SERVER`, `EMAIL_TO`, and `EMAIL_FROM`.
- Optional: `SMTP_PORT` (default 25), `SMTP_USERNAME`, `SMTP_PASSWORD`.
- Add `--send` to send; omit to preview the payload.

## Usage
```bash
python -m scripts.notify --input examples/notification_output.json --channel console
python -m scripts.notify --input examples/notification_output.json --channel file --output output/notification.json
python -m scripts.notify --input examples/notification_output.json --channel slack --send
python -m scripts.notify --input examples/notification_output.json --channel email --send
```

## Outputs
- Schema: `schemas/notification_output.schema.json`
- Example: `examples/notification_output.json`

## Safety
Only send summaries for authorized targets. Follow `docs/ROE.md`.
