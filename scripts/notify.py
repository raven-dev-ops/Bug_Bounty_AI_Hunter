import argparse
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def build_summary(data):
    if isinstance(data, dict) and "items" in data:
        items = _list(data.get("items"))
    elif isinstance(data, dict) and "findings" in data:
        items = _list(data.get("findings"))
    else:
        items = _list(data)

    titles = []
    for item in items[:5]:
        title = item.get("title") or item.get("name")
        if title:
            titles.append(title)

    return {
        "count": len(items),
        "sample_titles": titles,
    }


def notify_console(summary):
    print(f"Notifications: {summary['count']} items")
    for title in summary["sample_titles"]:
        print(f"- {title}")


def notify_file(summary, output):
    payload = {
        "channel": "file",
        "summary": summary,
    }
    dump_data(output, payload)


def notify_slack(summary, send):
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    payload = {
        "text": f"Bug bounty updates: {summary['count']} items",
        "attachments": [
            {"text": "\n".join(summary["sample_titles"]) or "No titles available."}
        ],
    }
    if not send:
        print("Slack payload preview:")
        print(json.dumps(payload, indent=2))
        return
    if not webhook:
        raise SystemExit("SLACK_WEBHOOK_URL is required to send Slack notifications.")
    request = Request(webhook, data=json.dumps(payload).encode("utf-8"))
    request.add_header("Content-Type", "application/json")
    with urlopen(request) as response:
        response.read()


def notify_email(summary, send):
    import smtplib
    from email.message import EmailMessage

    if not send:
        print("Email payload preview:")
        print(f"Bug bounty updates: {summary['count']} items")
        for title in summary["sample_titles"]:
            print(f"- {title}")
        return

    server = os.environ.get("SMTP_SERVER")
    to_addr = os.environ.get("EMAIL_TO")
    from_addr = os.environ.get("EMAIL_FROM")
    if not server or not to_addr or not from_addr:
        raise SystemExit("SMTP_SERVER, EMAIL_TO, and EMAIL_FROM are required.")

    port = int(os.environ.get("SMTP_PORT", "25"))
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")

    message = EmailMessage()
    message["Subject"] = f"Bug bounty updates: {summary['count']} items"
    message["From"] = from_addr
    message["To"] = to_addr
    body_lines = summary["sample_titles"] or ["No titles available."]
    message.set_content("\n".join(body_lines))

    with smtplib.SMTP(server, port) as smtp:
        if username and password:
            smtp.starttls()
            smtp.login(username, password)
        smtp.send_message(message)


def main():
    parser = argparse.ArgumentParser(description="Send notification summaries.")
    parser.add_argument("--input", required=True, help="Input JSON/YAML path.")
    parser.add_argument(
        "--channel",
        default="console",
        choices=["console", "file", "slack", "email"],
    )
    parser.add_argument("--output", help="Output file for channel=file.")
    parser.add_argument(
        "--send",
        action="store_true",
        help="Actually send notifications for Slack or email.",
    )
    args = parser.parse_args()

    data = load_data(args.input)
    summary = build_summary(data)

    if args.channel == "console":
        notify_console(summary)
    elif args.channel == "file":
        output = args.output or "output/notification.json"
        notify_file(summary, output)
    elif args.channel == "slack":
        notify_slack(summary, args.send)
    elif args.channel == "email":
        notify_email(summary, args.send)


if __name__ == "__main__":
    main()
