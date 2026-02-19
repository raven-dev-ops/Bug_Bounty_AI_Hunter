from __future__ import annotations

import json
import smtplib
import ssl
import urllib.request
from email.message import EmailMessage
from typing import Any
from urllib.parse import urlparse


ALLOWED_SLACK_WEBHOOK_HOSTS = {"hooks.slack.com", "hooks.slack-gov.com"}


def _validate_slack_webhook_url(webhook_url: str) -> str:
    parsed = urlparse(webhook_url.strip())
    if parsed.scheme != "https":
        raise ValueError("slack webhook url must use https")
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_SLACK_WEBHOOK_HOSTS:
        raise ValueError("slack webhook host is not allowed")
    if not parsed.path.startswith("/services/"):
        raise ValueError("invalid slack webhook path")
    return parsed.geturl()


def send_slack(
    *,
    webhook_url: str,
    title: str,
    body: str,
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    safe_webhook_url = _validate_slack_webhook_url(webhook_url)
    payload = {"text": f"*{title}*\n{body}"}
    request = urllib.request.Request(
        safe_webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        status = response.status
        content = response.read().decode("utf-8", errors="replace")
    return {"ok": status in (200, 201, 202, 204), "status": status, "response": content}


def send_smtp(
    *,
    host: str,
    port: int,
    from_email: str,
    to_email: str,
    title: str,
    body: str,
    username: str | None = None,
    password: str | None = None,
    use_tls: bool = True,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    message = EmailMessage()
    message["Subject"] = title
    message["From"] = from_email
    message["To"] = to_email
    message.set_content(body)

    if use_tls:
        context = ssl.create_default_context()
        with smtplib.SMTP(host=host, port=port, timeout=timeout_seconds) as server:
            server.starttls(context=context)
            if username and password:
                server.login(username, password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host=host, port=port, timeout=timeout_seconds) as server:
            if username and password:
                server.login(username, password)
            server.send_message(message)
    return {"ok": True}
