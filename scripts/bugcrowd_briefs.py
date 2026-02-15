import argparse
import getpass
import html
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


BUGCROWD_DOMAIN = "bugcrowd.com"
BUGCROWD_IDENTITY_DOMAIN = "identity.bugcrowd.com"
BUGCROWD_ENGAGEMENTS_URL = "https://bugcrowd.com/engagements"


def _utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


_ASCII_REPLACEMENTS = {
    "\u2013": "-",  # EN DASH
    "\u2014": "-",  # EM DASH
    "\u2019": "'",  # RIGHT SINGLE QUOTATION MARK
    "\u201c": '"',  # LEFT DOUBLE QUOTATION MARK
    "\u201d": '"',  # RIGHT DOUBLE QUOTATION MARK
    "\u2192": "->",  # RIGHTWARDS ARROW
    "\u2264": "<=",  # LESS-THAN OR EQUAL TO
}


def _to_ascii(text):
    if text is None:
        return ""
    value = str(text)
    for src, dst in _ASCII_REPLACEMENTS.items():
        value = value.replace(src, dst)
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    return value


def _md_escape(text):
    value = _to_ascii(text)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.strip()


def _write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    ascii_text = _to_ascii(text)
    path.write_text(ascii_text.rstrip() + "\n", encoding="utf-8")


def _slug_from_brief_url(brief_url):
    brief_url = str(brief_url or "").strip()
    if not brief_url:
        return ""
    brief_url = brief_url.split("?", 1)[0].strip("/")
    parts = [p for p in brief_url.split("/") if p]
    if not parts:
        return ""
    return parts[-1]


def _load_dotenv(path):
    env = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        env[key] = value
    return env


def _env_get(env, key):
    value = os.environ.get(key)
    if value is not None and value != "":
        return value
    return env.get(key, "")


_DEFAULT_BACKUP_CODES_FILENAMES = (
    "BUGCROWD_backup_codes",
    "BUGCROWD_backup_codes.txt",
)


def _env_truthy(value):
    return str(value or "").strip().lower() in ("1", "true", "yes", "y", "on")


def _find_backup_codes_file(path_hint=""):
    candidates = []
    if path_hint:
        candidates.append(Path(path_hint))
    else:
        candidates.extend(Path(name) for name in _DEFAULT_BACKUP_CODES_FILENAMES)

    for path in candidates:
        try:
            if path.exists() and path.is_file():
                return path
        except OSError:
            continue
    return None


def _read_backup_codes_file(path):
    if not path:
        return []

    try:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    seen = set()
    codes = []
    for raw in raw_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line.split("#", 1)[0].strip()
        if not line:
            continue

        for token in re.split(r"[,\s;]+", line):
            token = token.strip()
            if not token or token in seen:
                continue
            seen.add(token)
            codes.append(token)

    return codes


def _consume_backup_code_file(path, codes, used_code):
    if not path or not used_code:
        return False

    remaining = []
    consumed = False
    for code in codes or []:
        if not consumed and code == used_code:
            consumed = True
            continue
        remaining.append(code)

    if not consumed:
        return False

    try:
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for code in remaining:
                handle.write(f"{code}\n")
    except OSError:
        return False

    return True


def _replace_path_params(endpoint_path, params):
    if not params:
        return endpoint_path
    pattern = re.compile(r":(?!\d+(?:[/?#]|$))(\w+)")

    def repl(match):
        name = match.group(1)
        if name not in params:
            raise KeyError(f"Missing param for endpoint: {name}")
        return str(params[name])

    return pattern.sub(repl, endpoint_path)


@dataclass
class HttpResponse:
    url: str
    final_url: str
    status: int
    content_type: str
    headers: dict
    body: bytes


class BugcrowdHttp:
    def __init__(
        self,
        *,
        user_agent="bbhai-bugcrowd-briefs/0.1",
        timeout_seconds=30,
        min_delay_seconds=0.2,
        cookie_header=None,
    ):
        import http.cookiejar

        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.min_delay_seconds = min_delay_seconds
        self.cookie_header = cookie_header

        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        self._last_request = {}

    def _throttle(self, netloc):
        if not self.min_delay_seconds:
            return
        last = self._last_request.get(netloc)
        if last is None:
            return
        elapsed = time.time() - last
        remaining = self.min_delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def _request(self, url, *, method="GET", data=None, headers=None):
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        self._throttle(netloc)

        request_headers = {"User-Agent": self.user_agent}
        if headers:
            request_headers.update({str(k): str(v) for k, v in headers.items()})
        if (
            self.cookie_header
            and netloc.endswith(BUGCROWD_DOMAIN)
            and "Cookie" not in request_headers
        ):
            request_headers["Cookie"] = self.cookie_header

        req = urllib.request.Request(
            url, data=data, headers=request_headers, method=method
        )
        try:
            with self.opener.open(req, timeout=self.timeout_seconds) as resp:
                body = resp.read()
                status = getattr(resp, "status", 200)
                content_type = resp.headers.get("content-type", "") or ""
                self._last_request[netloc] = time.time()
                return HttpResponse(
                    url=url,
                    final_url=resp.geturl(),
                    status=status,
                    content_type=content_type,
                    headers=dict(resp.headers),
                    body=body,
                )
        except urllib.error.HTTPError as exc:
            body = exc.read() if hasattr(exc, "read") else b""
            content_type = exc.headers.get("content-type", "") if exc.headers else ""
            self._last_request[netloc] = time.time()
            return HttpResponse(
                url=url,
                final_url=exc.geturl(),
                status=exc.code,
                content_type=content_type or "",
                headers=dict(exc.headers) if exc.headers else {},
                body=body,
            )

    def get_text(self, url, *, headers=None):
        resp = self._request(url, method="GET", headers=headers)
        return resp.body.decode("utf-8", errors="replace"), resp

    def get_json(self, url, *, headers=None):
        text, resp = self.get_text(url, headers=headers)
        try:
            return json.loads(text), resp
        except json.JSONDecodeError:
            return None, resp

    def get_cookie_value(self, name, domain_suffix=None):
        for cookie in self.cookie_jar:
            if cookie.name != name:
                continue
            if domain_suffix and not cookie.domain.lower().endswith(
                domain_suffix.lower()
            ):
                continue
            return cookie.value
        return ""


def _identity_login(
    http_client,
    *,
    email,
    password,
    otp_code="",
    backup_otp_code="",
    backup_codes_file="",
    consume_backup_code=False,
):
    login_url = f"https://{BUGCROWD_IDENTITY_DOMAIN}/login?user_hint=RESEARCHER"
    http_client.get_text(login_url)
    csrf = http_client.get_cookie_value(
        "csrf-token", domain_suffix=BUGCROWD_IDENTITY_DOMAIN
    )
    if not csrf:
        raise SystemExit("Bugcrowd login failed: missing csrf-token cookie.")

    def prompt_secret(label):
        if not sys.stdin or not sys.stdin.isatty():
            return ""
        try:
            return getpass.getpass(label).strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    file_codes_path = None
    file_codes = None

    def load_file_codes():
        nonlocal file_codes_path, file_codes
        if file_codes is not None:
            return file_codes_path, file_codes
        file_codes_path = _find_backup_codes_file(backup_codes_file)
        file_codes = _read_backup_codes_file(file_codes_path) if file_codes_path else []
        return file_codes_path, file_codes

    def post_form(path, *, otp="", backup=""):
        form = {
            "username": email,
            "password": password,
            "otp_code": otp,
            "backup_otp_code": backup,
            "user_type": "RESEARCHER",
            "remember_me": "false",
        }
        body = urllib.parse.urlencode(form).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-CSRF-Token": csrf,
            "X-Requested-With": "XMLHttpRequest",
            "Origin": f"https://{BUGCROWD_IDENTITY_DOMAIN}",
            "Referer": login_url,
        }
        url = f"https://{BUGCROWD_IDENTITY_DOMAIN}{path}"
        resp = http_client._request(url, method="POST", data=body, headers=headers)
        try:
            payload = json.loads(resp.body.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            payload = None
        return resp.status, payload

    status, payload = post_form("/login", otp=otp_code, backup=backup_otp_code)
    if payload is None:
        raise SystemExit(
            f"Bugcrowd login failed: unexpected response (status {status})."
        )

    if status in (200, 400):
        redirect_to = str(payload.get("redirect_to") or "")
        if not redirect_to:
            raise SystemExit("Bugcrowd login failed: missing redirect_to.")
        http_client.get_text(redirect_to)
        return

    if status == 422:
        inner_form = str(payload.get("inner_form") or "")
        if inner_form not in ("OtpForm", "BackupOtpForm"):
            raise SystemExit(
                f"Bugcrowd login requires additional steps (inner_form={inner_form})."
            )

        def try_complete_login(mfa_status, mfa_payload):
            if mfa_payload is None or mfa_status not in (200, 400):
                return False
            redirect_to = str(mfa_payload.get("redirect_to") or "")
            if not redirect_to:
                return False
            http_client.get_text(redirect_to)
            return True

        def iter_backup_candidates():
            candidates = []
            if backup_otp_code:
                candidates.append(("env", backup_otp_code))

            path, codes = load_file_codes()
            if path and codes:
                candidates.extend(("file", code) for code in codes)

            if not candidates:
                manual = prompt_secret(
                    "Bugcrowd backup code (BUGCROWD_BACKUP_OTP_CODE): "
                )
                if manual:
                    candidates.append(("prompt", manual))

            seen = set()
            out = []
            for source, code in candidates:
                if not code or code in seen:
                    continue
                seen.add(code)
                out.append((source, code))
            return out

        def try_backup_codes(*, consume_file_code):
            for source, code in iter_backup_candidates():
                mfa_status, mfa_payload = post_form("/auth/backup-code", backup=code)
                if try_complete_login(mfa_status, mfa_payload):
                    if source == "file" and consume_file_code:
                        path, codes = load_file_codes()
                        if path:
                            _consume_backup_code_file(path, codes, code)
                    return True
            return False

        def try_otp():
            nonlocal otp_code
            if not otp_code:
                otp_code = prompt_secret("Bugcrowd OTP code (BUGCROWD_OTP_CODE): ")
            if not otp_code:
                return False
            mfa_status, mfa_payload = post_form("/auth/otp-challenge", otp=otp_code)
            return try_complete_login(mfa_status, mfa_payload)

        consume_file_code = bool(consume_backup_code)
        if inner_form == "OtpForm":
            if otp_code or (sys.stdin and sys.stdin.isatty()):
                if try_otp():
                    return
            if try_backup_codes(consume_file_code=consume_file_code):
                return
        else:
            if try_backup_codes(consume_file_code=consume_file_code):
                return
            if try_otp():
                return

        raise SystemExit("Bugcrowd login failed after MFA step.")

    message = str(payload.get("message") or "").strip()
    raise SystemExit(f"Bugcrowd login failed (status {status}): {message or 'unknown'}")


def _bugcrowd_list_json_headers():
    return {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }


def _list_engagements(http_client, *, page, category, sort_by, sort_direction):
    query = {
        "category": category,
        "page": page,
        "sort_by": sort_by,
        "sort_direction": sort_direction,
    }
    url = BUGCROWD_ENGAGEMENTS_URL + "?" + urllib.parse.urlencode(query)
    data, resp = http_client.get_json(url, headers=_bugcrowd_list_json_headers())
    if not isinstance(data, dict):
        raise SystemExit(
            f"Unexpected listing payload for page {page} (status {resp.status})."
        )
    return data, url


def _extract_brief_root(html_text):
    m = re.search(
        r"<div[^>]*\bid=(['\"])researcher-engagement-brief-root\1[^>]*>",
        html_text,
    )
    if not m:
        return None
    tag = m.group(0)

    def get_attr(name):
        m_attr = re.search(rf"{re.escape(name)}='([^']*)'", tag)
        if not m_attr:
            m_attr = re.search(rf'{re.escape(name)}="([^"]*)"', tag)
        return m_attr.group(1) if m_attr else ""

    api_raw = get_attr("data-api-endpoints")
    props_raw = get_attr("data-props")

    api = {}
    props = {}
    if api_raw:
        api = json.loads(html.unescape(api_raw))
    if props_raw:
        props = json.loads(html.unescape(props_raw))
    return {"api": api, "props": props}


def _as_pretty_json(value):
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def _mk_full_brief_markdown(
    *,
    slug,
    engagement_url,
    fetched_at,
    endpoints,
    props,
    brief_doc,
    announcements,
    stats,
    hall_of_fame,
    recently_joined,
    known_issues,
    scope_rank,
    target_group_known_issues,
    errors,
):
    lines = []
    lines.append(f"# {slug}")
    lines.append("")
    lines.append(
        "> WARNING: This export may include auth-only program details. Do not commit this output."
    )
    lines.append("")
    lines.append("## Overview")
    lines.append("- Platform: Bugcrowd")
    lines.append(f"- Engagement URL: {_md_escape(engagement_url)}")
    lines.append(f"- Fetched at (UTC): {_md_escape(fetched_at)}")
    lines.append("")

    if errors:
        lines.append("## Notes / Errors")
        for entry in errors:
            lines.append(f"- {_md_escape(entry)}")
        lines.append("")

    lines.append("## API Endpoints (From Page)")
    if isinstance(endpoints, dict) and endpoints:
        for group in sorted(endpoints.keys()):
            mapping = endpoints.get(group) or {}
            lines.append(f"### {group}")
            if not isinstance(mapping, dict) or not mapping:
                lines.append("- n/a")
                lines.append("")
                continue
            for name in sorted(mapping.keys()):
                value = mapping.get(name) or ""
                lines.append(f"- {name}: {_md_escape(value)}")
            lines.append("")
    else:
        lines.append("- n/a")
        lines.append("")

    lines.append("## Page Props (From Page)")
    if isinstance(props, dict) and props:
        lines.append("```json")
        lines.append(_as_pretty_json(props).rstrip())
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Brief Version Document")
    if brief_doc is not None:
        lines.append("```json")
        lines.append(_as_pretty_json(brief_doc).rstrip())
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Announcements")
    if announcements is not None:
        lines.append("```json")
        lines.append(_as_pretty_json(announcements).rstrip())
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Stats")
    if stats is not None:
        lines.append("```json")
        lines.append(_as_pretty_json(stats).rstrip())
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Hall Of Fame")
    if hall_of_fame is not None:
        lines.append("```json")
        lines.append(_as_pretty_json(hall_of_fame).rstrip())
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Recently Joined")
    if recently_joined is not None:
        lines.append("```json")
        lines.append(_as_pretty_json(recently_joined).rstrip())
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Known Issues")
    if known_issues is not None:
        lines.append("```json")
        lines.append(_as_pretty_json(known_issues).rstrip())
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Scope Rank")
    if scope_rank is not None:
        lines.append("```json")
        lines.append(_as_pretty_json(scope_rank).rstrip())
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Target Group Known Issue Stats")
    if target_group_known_issues:
        lines.append("```json")
        lines.append(_as_pretty_json(target_group_known_issues).rstrip())
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Export Bugcrowd engagement briefs (auth-required) to local Markdown."
    )
    parser.add_argument(
        "--category",
        default="bug_bounty",
        help="Bugcrowd engagement category (default: bug_bounty).",
    )
    parser.add_argument(
        "--sort-by", default="promoted", help="Sort key (default: promoted)."
    )
    parser.add_argument(
        "--sort-direction", default="desc", help="Sort direction (default: desc)."
    )
    parser.add_argument(
        "--start-page", type=int, default=1, help="Start page (default: 1)."
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to fetch starting at --start-page (default: 1).",
    )
    parser.add_argument(
        "--all-pages",
        action="store_true",
        help="Fetch every page for the query (overrides --pages).",
    )
    parser.add_argument(
        "--slugs",
        nargs="*",
        default=None,
        help="Optional engagement slugs to export (default: all from listing).",
    )
    parser.add_argument(
        "--out-dir",
        default="bounty_board/bugcrowd_full",
        help="Output directory for markdown (default: bounty_board/bugcrowd_full).",
    )
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Write a combined markdown file with all engagements for the run.",
    )
    args = parser.parse_args(argv)

    env = _load_dotenv(Path(".env"))
    cookie_header = _env_get(env, "BUGCROWD_COOKIE")
    email = _env_get(env, "BUGCROWD_EMAIL")
    password = _env_get(env, "BUGCROWD_PASSWORD")
    otp_code = _env_get(env, "BUGCROWD_OTP_CODE")
    backup_otp_code = _env_get(env, "BUGCROWD_BACKUP_OTP_CODE")
    backup_codes_file = _env_get(env, "BUGCROWD_BACKUP_CODES_FILE")
    consume_backup_code = _env_truthy(_env_get(env, "BUGCROWD_CONSUME_BACKUP_CODE"))

    http_client = BugcrowdHttp(cookie_header=cookie_header or None)
    if not cookie_header:
        if not email or not password:
            raise SystemExit(
                "Missing auth. Set BUGCROWD_COOKIE or BUGCROWD_EMAIL/BUGCROWD_PASSWORD in .env."
            )
        _identity_login(
            http_client,
            email=email,
            password=password,
            otp_code=otp_code,
            backup_otp_code=backup_otp_code,
            backup_codes_file=backup_codes_file,
            consume_backup_code=consume_backup_code,
        )

    fetched_at = _utc_now_iso()
    out_dir = Path(args.out_dir)

    first_page_data = None
    listing_url_first = ""

    if args.all_pages:
        data, listing_url = _list_engagements(
            http_client,
            page=args.start_page,
            category=args.category,
            sort_by=args.sort_by,
            sort_direction=args.sort_direction,
        )
        listing_url_first = listing_url
        first_page_data = data
        pagination = data.get("paginationMeta") or {}
        limit = int(pagination.get("limit") or 0) or 24
        total = int(pagination.get("totalCount") or 0)
        pages_to_fetch = max(1, int(math.ceil(total / limit)))
    else:
        pages_to_fetch = max(1, int(args.pages))

    engagements = []
    for page in range(args.start_page, args.start_page + pages_to_fetch):
        if page == args.start_page and first_page_data is not None:
            data = first_page_data
        else:
            data, listing_url = _list_engagements(
                http_client,
                page=page,
                category=args.category,
                sort_by=args.sort_by,
                sort_direction=args.sort_direction,
            )
            if not listing_url_first:
                listing_url_first = listing_url
        items = data.get("engagements") or []
        if not isinstance(items, list):
            raise SystemExit(f"Unexpected engagements payload on page {page}")
        engagements.extend(item for item in items if isinstance(item, dict))

    by_slug = {}
    for item in engagements:
        brief_url = str(item.get("briefUrl") or "")
        slug = _slug_from_brief_url(brief_url)
        if not slug:
            continue
        by_slug.setdefault(slug, item)

    slugs = sorted(by_slug.keys())
    if args.slugs:
        requested = {s.strip() for s in args.slugs if s and s.strip()}
        slugs = [s for s in slugs if s in requested]

    combined_sections = []
    for slug in slugs:
        engagement_url = f"https://{BUGCROWD_DOMAIN}/engagements/{slug}"
        page_text, page_resp = http_client.get_text(engagement_url)

        errors = []
        if page_resp.status != 200:
            errors.append(f"Engagement page status {page_resp.status}")

        root = _extract_brief_root(page_text)
        if not root:
            errors.append("Missing researcher-engagement-brief-root element")
            md = _mk_full_brief_markdown(
                slug=slug,
                engagement_url=engagement_url,
                fetched_at=fetched_at,
                endpoints={},
                props={},
                brief_doc=None,
                announcements=None,
                stats=None,
                hall_of_fame=None,
                recently_joined=None,
                known_issues=None,
                scope_rank=None,
                target_group_known_issues={},
                errors=errors,
            )
            _write_text(out_dir / f"{slug}.md", md)
            if args.combined:
                combined_sections.append(md)
            continue

        endpoints = root.get("api") or {}
        props = root.get("props") or {}

        def get_endpoint(group, name):
            if not isinstance(endpoints, dict):
                return ""
            mapping = endpoints.get(group) or {}
            if not isinstance(mapping, dict):
                return ""
            return str(mapping.get(name) or "")

        def fetch_json_relative(path, *, add_json_suffix=False, params=None):
            if not path:
                return None
            try:
                resolved = _replace_path_params(path, params or {})
            except KeyError as exc:
                errors.append(str(exc))
                return None
            if add_json_suffix and not resolved.endswith(".json"):
                resolved = resolved + ".json"
            url = urllib.parse.urljoin(f"https://{BUGCROWD_DOMAIN}", resolved)
            data, resp = http_client.get_json(url)
            if data is None:
                errors.append(
                    f"Non-JSON response for {resolved} (status {resp.status}, type {resp.content_type})"
                )
            return data

        brief_doc = fetch_json_relative(
            get_endpoint("engagementBriefApi", "getBriefVersionDocument"),
            add_json_suffix=True,
        )
        announcements = fetch_json_relative(
            get_endpoint("announcementsApi", "getEngagementAnnouncements"),
            add_json_suffix=True,
        )
        stats = fetch_json_relative(
            get_endpoint("engagementStatsApi", "getBriefStats"),
        )
        hall_of_fame = fetch_json_relative(
            get_endpoint("engagementStatsApi", "getHallOfFamers"),
        )
        recently_joined = fetch_json_relative(
            get_endpoint("engagementStatsApi", "getRecentlyJoinedUsers"),
        )
        known_issues = fetch_json_relative(
            get_endpoint("engagementStatsApi", "getKnownIssuesStats"),
        )
        scope_rank = fetch_json_relative(
            get_endpoint("engagementScopeRankApi", "getEngagementScopeRanks"),
        )

        target_group_known_issues = {}
        tg_path = get_endpoint("engagementStatsApi", "getTargetGroupKnownIssuesStats")
        if tg_path and isinstance(brief_doc, dict):
            groups = (brief_doc.get("data") or {}).get("scope") or []
            for group in groups:
                group_id = group.get("id")
                if not group_id:
                    continue
                data = fetch_json_relative(tg_path, params={"id": group_id})
                if data is not None:
                    target_group_known_issues[str(group_id)] = data

        md = _mk_full_brief_markdown(
            slug=slug,
            engagement_url=engagement_url,
            fetched_at=fetched_at,
            endpoints=endpoints,
            props=props,
            brief_doc=brief_doc,
            announcements=announcements,
            stats=stats,
            hall_of_fame=hall_of_fame,
            recently_joined=recently_joined,
            known_issues=known_issues,
            scope_rank=scope_rank,
            target_group_known_issues=target_group_known_issues,
            errors=errors,
        )
        _write_text(out_dir / f"{slug}.md", md)
        if args.combined:
            combined_sections.append(md)

    if args.combined:
        lines = []
        lines.append("# Bugcrowd Brief Export (Combined)")
        lines.append("")
        lines.append(f"- Listing URL: {_md_escape(listing_url_first or '')}")
        lines.append(f"- Pages fetched: {_md_escape(pages_to_fetch)}")
        lines.append(f"- Fetched at (UTC): {_md_escape(fetched_at)}")
        lines.append("")
        for section in combined_sections:
            section_text = section.lstrip()
            if section_text.startswith("# "):
                section_text = "## " + section_text[2:]
            lines.append(section_text.rstrip())
            lines.append("")
            lines.append("---")
            lines.append("")
        _write_text(out_dir / "ALL.md", "\n".join(lines))


if __name__ == "__main__":
    main()
