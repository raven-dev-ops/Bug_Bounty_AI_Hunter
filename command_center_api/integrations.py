from __future__ import annotations

import hashlib
import hmac
import json
import random
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import scripts.connectors  # noqa: F401 - ensures connector registration side effects
from scripts.connectors import get_connector
from scripts.lib.fetcher import Fetcher

from command_center_api import db


BUGCROWD_PROGRAMS_URL = "https://api.bugcrowd.com/programs"
BUGCROWD_SUBMISSIONS_URL = "https://api.bugcrowd.com/submissions"


class SlidingWindowRateLimiter:
    def __init__(self, *, max_requests: int, window_seconds: int):
        self.max_requests = max(1, int(max_requests))
        self.window_seconds = max(1, int(window_seconds))
        self._lock = threading.Lock()
        self._events: dict[str, list[float]] = {}

    def consume(self, key: str) -> dict[str, Any]:
        now = time.monotonic()
        with self._lock:
            events = self._events.get(key, [])
            cutoff = now - self.window_seconds
            events = [value for value in events if value >= cutoff]
            if len(events) >= self.max_requests:
                reset_in = max(0.0, self.window_seconds - (now - events[0]))
                backoff = min(reset_in, 1.0) + random.uniform(0.0, 0.25)
                time.sleep(backoff)
                now = time.monotonic()
                cutoff = now - self.window_seconds
                events = [value for value in events if value >= cutoff]
            allowed = len(events) < self.max_requests
            if allowed:
                events.append(now)
            self._events[key] = events
            remaining = max(0, self.max_requests - len(events))
            reset_in = 0.0
            if events:
                reset_in = max(0.0, self.window_seconds - (now - events[0]))
            return {
                "allowed": allowed,
                "remaining": remaining,
                "limit": self.max_requests,
                "window_seconds": self.window_seconds,
                "reset_in_seconds": round(reset_in, 3),
            }


BUGCROWD_RATE_LIMITER = SlidingWindowRateLimiter(max_requests=60, window_seconds=60)


def _json_get(
    *,
    url: str,
    headers: dict[str, str],
    timeout_seconds: int = 30,
) -> tuple[int, Any, dict[str, str]]:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8", errors="replace")
            payload = json.loads(raw) if raw else {}
            response_headers = {key.lower(): value for key, value in response.headers.items()}
            return response.status, payload, response_headers
    except urllib.error.HTTPError as exc:
        response_headers = {key.lower(): value for key, value in exc.headers.items()} if exc.headers else {}
        if exc.code == 304:
            return 304, None, response_headers
        body = exc.read().decode("utf-8", errors="replace")
        detail = body.strip() or f"HTTP {exc.code}"
        raise RuntimeError(f"request failed for {url}: {detail}") from exc


def _normalize_bugcrowd_program(item: dict[str, Any]) -> dict[str, Any]:
    attributes = item.get("attributes") if isinstance(item.get("attributes"), dict) else {}
    program_id = str(item.get("id") or attributes.get("id") or "").strip()
    name = str(attributes.get("name") or item.get("name") or program_id or "bugcrowd-program")
    handle = str(attributes.get("code") or attributes.get("slug") or program_id).strip()
    policy_url = str(attributes.get("target_url") or attributes.get("program_url") or "").strip()
    return {
        "id": f"bugcrowd:{program_id or handle}",
        "source_id": f"bugcrowd:{program_id or handle}",
        "source": "bugcrowd_api",
        "platform": "bugcrowd",
        "handle": handle or None,
        "name": name,
        "policy_url": policy_url or None,
        "raw": item,
    }


def _bugcrowd_get_with_cache(
    *,
    connection: Any,
    url: str,
    token: str,
) -> tuple[dict[str, Any], bool]:
    cached = db.get_http_cache(connection, url)
    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {token}",
        "User-Agent": "bbhai-command-center/0.1",
    }
    if cached and cached.get("etag"):
        headers["If-None-Match"] = str(cached["etag"])
    if cached and cached.get("last_modified"):
        headers["If-Modified-Since"] = str(cached["last_modified"])

    status_code, payload, response_headers = _json_get(url=url, headers=headers)
    if status_code == 304 and cached and cached.get("response_json"):
        cached_payload = cached["response_json"]
        if isinstance(cached_payload, dict):
            return cached_payload, True
        return {}, True
    payload = payload or {}
    db.upsert_http_cache(
        connection,
        url=url,
        etag=response_headers.get("etag"),
        last_modified=response_headers.get("last-modified"),
        response_json=payload,
    )
    return payload, False


def sync_bugcrowd_programs(
    *,
    connection: Any,
    token: str | None,
    client_ip: str,
    limit: int = 100,
) -> dict[str, Any]:
    budget = BUGCROWD_RATE_LIMITER.consume(client_ip)
    if not budget["allowed"]:
        raise RuntimeError("bugcrowd rate limit exceeded")

    safe_limit = max(1, min(500, int(limit)))
    if not token:
        registry_path = Path("data/program_registry.json")
        if not registry_path.exists():
            return {"count": 0, "mode": "fallback_registry_missing", "budget": budget}
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        programs = registry.get("programs", [])
        filtered = []
        for item in programs:
            if not isinstance(item, dict):
                continue
            if str(item.get("platform") or "").lower() not in {"bugcrowd", "bugcrowd_vdp"}:
                continue
            filtered.append(item)
        count = db.upsert_programs(
            connection,
            filtered[:safe_limit],
            source="bugcrowd_fallback_registry",
        )
        return {"count": count, "mode": "fallback_registry", "budget": budget}

    query = urllib.parse.urlencode({"page[size]": safe_limit})
    url = f"{BUGCROWD_PROGRAMS_URL}?{query}"
    payload, from_cache = _bugcrowd_get_with_cache(connection=connection, url=url, token=token)
    items = payload.get("data", [])
    normalized = []
    if isinstance(items, list):
        normalized = [_normalize_bugcrowd_program(item) for item in items if isinstance(item, dict)]
    count = db.upsert_programs(connection, normalized, source="bugcrowd_api")
    return {
        "count": count,
        "mode": "bugcrowd_api",
        "from_cache": from_cache,
        "budget": budget,
    }


def sync_bugcrowd_submissions(
    *,
    connection: Any,
    token: str | None,
    client_ip: str,
    since: str | None = None,
    cursor: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    budget = BUGCROWD_RATE_LIMITER.consume(client_ip)
    if not budget["allowed"]:
        raise RuntimeError("bugcrowd rate limit exceeded")
    if not token:
        return {"count": 0, "mode": "token_required", "budget": budget}

    safe_limit = max(1, min(200, int(limit)))
    params: dict[str, Any] = {"page[size]": safe_limit}
    if since:
        params["filter[updated_after]"] = since
    if cursor:
        params["page[cursor]"] = cursor
    query = urllib.parse.urlencode(params)
    url = f"{BUGCROWD_SUBMISSIONS_URL}?{query}"
    payload, from_cache = _bugcrowd_get_with_cache(connection=connection, url=url, token=token)
    items = payload.get("data", [])
    count = 0
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            attributes = item.get("attributes") if isinstance(item.get("attributes"), dict) else {}
            submission_id = str(item.get("id") or attributes.get("id") or "").strip()
            status = str(attributes.get("state") or attributes.get("status") or "unknown").strip()
            if not submission_id:
                continue
            event_id = f"bugcrowd:{submission_id}:{status}"
            db.add_submission_status_event(
                connection,
                event_id=event_id,
                platform="bugcrowd",
                submission_id=submission_id,
                status=status,
                payload=item,
            )
            count += 1
    return {
        "count": count,
        "mode": "bugcrowd_api",
        "from_cache": from_cache,
        "budget": budget,
    }


def verify_webhook_signature(
    *,
    payload_raw: bytes,
    signature_header: str | None,
    secret: str | None,
) -> bool:
    if not secret:
        return True
    if not signature_header:
        return False
    digest = hmac.new(secret.encode("utf-8"), payload_raw, hashlib.sha256).hexdigest()
    candidate = signature_header.split("=", 1)[-1].strip().lower()
    return hmac.compare_digest(candidate, digest.lower())


def sync_public_connector(
    *,
    connection: Any,
    connector_name: str,
    fixtures_dir: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    connector = get_connector(connector_name)
    if connector is None:
        raise RuntimeError(f"connector not found: {connector_name}")
    safe_limit = max(1, min(300, int(limit)))
    fetcher = Fetcher(
        cache_dir="data/fetch_cache",
        min_delay_seconds=0.2,
        max_requests_per_domain=120,
        public_only=True,
    )
    listed = connector.list_programs(fetcher, fixtures_dir=fixtures_dir)
    detailed = []
    for program in listed[:safe_limit]:
        if not isinstance(program, dict):
            continue
        merged = connector.fetch_details(fetcher, program, fixtures_dir=fixtures_dir)
        if isinstance(merged, dict):
            program_id = str(merged.get("id") or "").strip()
            if not program_id:
                source_id = str(merged.get("source_id") or "").strip()
                handle = str(merged.get("handle") or "").strip()
                if source_id:
                    program_id = source_id
                elif handle:
                    program_id = f"{connector_name}:{handle}"
                else:
                    program_id = f"{connector_name}:{len(detailed) + 1}"
                merged["id"] = program_id
            detailed.append(merged)
    count = db.upsert_programs(connection, detailed, source=f"{connector_name}_connector")
    return {"count": count, "connector": connector_name, "metrics": fetcher.metrics}


def sync_github_issues(
    *,
    connection: Any,
    repo: str,
    token: str | None = None,
    state: str = "open",
    limit: int = 100,
) -> dict[str, Any]:
    safe_limit = max(1, min(500, int(limit)))
    issues: list[dict[str, Any]] = []
    if token:
        query = urllib.parse.urlencode({"state": state, "per_page": safe_limit})
        url = f"https://api.github.com/repos/{repo}/issues?{query}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "bbhai-command-center/0.1",
        }
        _, payload, _ = _json_get(url=url, headers=headers)
        if isinstance(payload, list):
            issues = [item for item in payload if isinstance(item, dict)]
        elif isinstance(payload, dict):
            data = payload.get("items", [])
            if isinstance(data, list):
                issues = [item for item in data if isinstance(item, dict)]
    else:
        command = [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            state,
            "--limit",
            str(safe_limit),
            "--json",
            "number,title,state,url",
        ]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"gh issue list failed: {completed.stderr.strip()}")
        parsed = json.loads(completed.stdout or "[]")
        if isinstance(parsed, list):
            issues = [item for item in parsed if isinstance(item, dict)]

    count = 0
    for issue in issues:
        number = issue.get("number")
        title = str(issue.get("title") or "").strip()
        status_value = str(issue.get("state") or "open").strip().lower()
        if number is None or not title:
            continue
        task_id = f"github:{repo}:{number}"
        db.upsert_task(
            connection,
            {
                "id": task_id,
                "title": title,
                "status": status_value,
            },
        )
        count += 1
    return {"count": count, "repo": repo, "state": state}
