import argparse
import json
import math
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from scripts.lib.fetcher import Fetcher


BUGCROWD_DOMAIN = "bugcrowd.com"
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


def _slug_from_brief_url(brief_url):
    brief_url = str(brief_url or "").strip()
    if not brief_url:
        return ""
    brief_url = brief_url.split("?", 1)[0].strip("/")
    parts = [p for p in brief_url.split("/") if p]
    if not parts:
        return ""
    return parts[-1]


def _fetch_json(fetcher, url, headers):
    try:
        text, meta = fetcher.fetch_text(url, headers=headers)
    except Exception as exc:
        return None, {"url": url, "error": str(exc), "from_cache": False}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, {
            "url": url,
            "error": f"Invalid JSON: {exc}",
            "from_cache": bool(meta and meta.get("from_cache")),
            "status": meta.get("status") if meta else None,
        }
    return data, meta


def _bugcrowd_json_headers():
    return {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }


def _list_engagements(fetcher, page, category, sort_by, sort_direction):
    params = {
        "category": category,
        "page": int(page),
        "sort_by": sort_by,
        "sort_direction": sort_direction,
    }
    url = f"{BUGCROWD_ENGAGEMENTS_URL}?{urlencode(params)}"
    data, meta = _fetch_json(fetcher, url, headers=_bugcrowd_json_headers())
    if not isinstance(data, dict):
        raise SystemExit(f"Unexpected response for listing: {url}")
    return data, meta, url


def _fetch_engagement_stats(fetcher, slug):
    url = f"{BUGCROWD_ENGAGEMENTS_URL}/{slug}/statistics"
    data, meta = _fetch_json(fetcher, url, headers=_bugcrowd_json_headers())
    if isinstance(data, dict) and data.get("error"):
        return None, meta
    return data, meta


def _fetch_hall_of_fame(fetcher, slug):
    url = f"{BUGCROWD_ENGAGEMENTS_URL}/{slug}/hall_of_fames.json"
    data, meta = _fetch_json(fetcher, url, headers=_bugcrowd_json_headers())
    if isinstance(data, dict) and data.get("error"):
        return None, meta
    return data, meta


def _fetch_recently_joined(fetcher, slug):
    url = f"{BUGCROWD_ENGAGEMENTS_URL}/{slug}/recently_joined_users.json"
    data, meta = _fetch_json(fetcher, url, headers=_bugcrowd_json_headers())
    if isinstance(data, dict) and data.get("error"):
        return None, meta
    return data, meta


def _md_escape(text):
    # Keep output stable and simple. We do not try to escape every edge case.
    value = _to_ascii(text)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.strip()


def _write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    ascii_text = _to_ascii(text)
    path.write_text(ascii_text.rstrip() + "\n", encoding="utf-8")


def _format_value(value):
    if value is None:
        return "n/a"
    if value == "":
        return "n/a"
    return _md_escape(value)


def _format_bool(value):
    return "true" if bool(value) else "false"


def _mk_engagement_markdown(
    engagement, listing_url, fetched_at, stats=None, community=None
):
    name = _format_value(engagement.get("name"))
    brief_url = str(engagement.get("briefUrl") or "")
    slug = _slug_from_brief_url(brief_url)
    page_url = (
        f"https://{BUGCROWD_DOMAIN}{brief_url}"
        if brief_url.startswith("/")
        else brief_url
    )
    brief_portal_url = (
        f"https://{BUGCROWD_DOMAIN}/h/engagements/{slug}/brief" if slug else ""
    )

    reward_summary = engagement.get("rewardSummary") or {}
    reward_text = reward_summary.get("summary") or ""
    reward_text = _format_value(reward_text)

    tagline = _md_escape(engagement.get("tagline"))

    lines = []
    lines.append(f"# {name}")
    lines.append("")
    lines.append("## Overview")
    lines.append("- Platform: Bugcrowd")
    lines.append(f"- Engagement URL: {_format_value(page_url)}")
    if brief_portal_url:
        lines.append(f"- Hacker Portal brief URL: {_format_value(brief_portal_url)}")
    lines.append(f"- Listing URL: {_format_value(listing_url)}")
    lines.append(f"- Access status: {_format_value(engagement.get('accessStatus'))}")
    lines.append(f"- Private: {_format_bool(engagement.get('isPrivate'))}")
    lines.append(f"- Industry: {_format_value(engagement.get('industryName'))}")
    lines.append(f"- Service level: {_format_value(engagement.get('serviceLevel'))}")
    lines.append(f"- Scope rank: {_format_value(engagement.get('scopeRank'))}")
    if engagement.get("endsAt"):
        lines.append(f"- Ends at: {_format_value(engagement.get('endsAt'))}")
    lines.append(f"- Reward summary: {reward_text}")
    if engagement.get("logoUrl"):
        lines.append(f"- Logo: {_format_value(engagement.get('logoUrl'))}")
    lines.append(f"- Fetched at (UTC): {_format_value(fetched_at)}")
    lines.append("")

    if tagline:
        lines.append("## Tagline")
        lines.append(tagline)
        lines.append("")

    lines.append("## Public JSON Endpoints")
    lines.append(f"- Engagement list (JSON): {_format_value(listing_url)}")
    if slug:
        lines.append(
            f"- Statistics (JSON): https://{BUGCROWD_DOMAIN}/engagements/{slug}/statistics"
        )
        lines.append(
            f"- Hall of fame (JSON): https://{BUGCROWD_DOMAIN}/engagements/{slug}/hall_of_fames.json"
        )
        lines.append(
            f"- Recently joined (JSON): https://{BUGCROWD_DOMAIN}/engagements/{slug}/recently_joined_users.json"
        )
    lines.append("")

    if stats:
        lines.append("## Stats (Public)")
        lines.append(
            f"- Rewarded vulnerabilities: {_format_value(stats.get('rewardedVulnerabilities'))}"
        )
        lines.append(
            f"- Validation within: {_format_value(stats.get('validationWithin'))}"
        )
        lines.append(f"- Average payout: {_format_value(stats.get('averagePayout'))}")
        lines.append(
            f"- Valid submission count: {_format_value(stats.get('validSubmissionCount'))}"
        )
        lines.append("")

    if community:
        lines.append("## Community (Public)")
        hof = community.get("hall_of_fame") or {}
        recently = community.get("recently_joined") or {}
        hof_total = None
        if isinstance(hof, dict):
            hof_total = (hof.get("pagination_meta") or {}).get("totalCount")
        joined_total = None
        if isinstance(recently, dict):
            joined_total = recently.get("total")
        if hof_total is not None:
            lines.append(f"- Hall of fame entries: {_format_value(hof_total)}")
        else:
            lines.append("- Hall of fame entries: n/a")
        if joined_total is not None:
            lines.append(f"- Recently joined users: {_format_value(joined_total)}")
        else:
            lines.append("- Recently joined users: n/a")
        lines.append("")

    lines.append("## Notes")
    lines.append(
        "- Scope, rules, and bounty tables may require logging in and joining the engagement in Bugcrowd."
    )
    lines.append("- Do not test without explicit authorization. Follow `docs/ROE.md`.")
    lines.append("")

    return "\n".join(lines)


def _mk_index_markdown(rows, listing_url, fetched_at, pages_fetched):
    lines = []
    lines.append("# Bugcrowd Bounty Board")
    lines.append("")
    lines.append("Generated from Bugcrowd's public engagements listing (JSON).")
    lines.append("")
    lines.append(f"- Listing URL: {_format_value(listing_url)}")
    lines.append(f"- Pages fetched: {_format_value(pages_fetched)}")
    lines.append(f"- Fetched at (UTC): {_format_value(fetched_at)}")
    lines.append("")
    lines.append(
        "| Engagement | Reward | Access | Private | Industry | Service | Scope Rank | Validation |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        rel = row["rel_path"]
        name = row["name"]
        reward = row["reward"]
        access = row["access"]
        private = row["private"]
        industry = row["industry"]
        service = row["service"]
        scope_rank = row["scope_rank"]
        validation = row["validation"]
        lines.append(
            f"| [{name}]({rel}) | {reward} | {access} | {private} | {industry} | {service} | {scope_rank} | {validation} |"
        )
    lines.append("")
    lines.append("Notes:")
    lines.append(
        "- This board is metadata only. It does not grant authorization to test anything."
    )
    lines.append("- Some engagement details require being logged in to Bugcrowd.")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate a Bugcrowd bounty board from public data."
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
        "--include-community",
        action="store_true",
        help="Also fetch hall of fame and recently joined endpoints (adds requests).",
    )
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Write a combined markdown file with all engagements for the run.",
    )
    parser.add_argument(
        "--out-dir",
        default="bounty_board/bugcrowd",
        help="Output directory for markdown (default: bounty_board/bugcrowd).",
    )
    args = parser.parse_args(argv)

    fetched_at = _utc_now_iso()
    out_dir = Path(args.out_dir)
    cache_dir = Path("data") / "fetch_cache" / "bugcrowd_board"

    fetcher = Fetcher(
        cache_dir=cache_dir,
        user_agent="bbhai-bugcrowd-board/0.1",
        timeout_seconds=30,
        max_retries=2,
        backoff_seconds=1.0,
        min_delay_seconds=0.2,
        max_requests_per_domain=1000,
        max_bytes_per_domain=25 * 1024 * 1024,
        allow_domains=[BUGCROWD_DOMAIN],
        robots_mode=True,
        public_only=True,
    )

    first_page_data = None
    listing_url_first = ""

    # Determine how many pages to fetch.
    if args.all_pages:
        data, _, listing_url = _list_engagements(
            fetcher,
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
            data, _, listing_url = _list_engagements(
                fetcher,
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

    # De-dup by briefUrl.
    by_url = {}
    for item in engagements:
        key = str(item.get("briefUrl") or "")
        if not key:
            continue
        by_url.setdefault(key, item)
    engagements = list(by_url.values())

    index_rows = []
    combined_sections = []
    for engagement in sorted(engagements, key=lambda e: _to_ascii(e.get("name") or "")):
        brief_url = str(engagement.get("briefUrl") or "")
        slug = _slug_from_brief_url(brief_url)
        if not slug:
            continue

        stats, _ = _fetch_engagement_stats(fetcher, slug)
        community = None
        if args.include_community:
            hall_of_fame, _ = _fetch_hall_of_fame(fetcher, slug)
            recently_joined, _ = _fetch_recently_joined(fetcher, slug)
            community = {
                "hall_of_fame": hall_of_fame,
                "recently_joined": recently_joined,
            }

        md = _mk_engagement_markdown(
            engagement=engagement,
            listing_url=listing_url_first or "",
            fetched_at=fetched_at,
            stats=stats,
            community=community,
        )
        rel_path = f"{slug}.md"
        _write_text(out_dir / rel_path, md)
        if args.combined:
            combined_sections.append(md)

        reward_summary = engagement.get("rewardSummary") or {}
        reward = reward_summary.get("summary") or ""
        validation = ""
        if isinstance(stats, dict):
            validation = stats.get("validationWithin") or ""

        index_rows.append(
            {
                "rel_path": rel_path,
                "name": _format_value(engagement.get("name")),
                "reward": _format_value(reward),
                "access": _format_value(engagement.get("accessStatus")),
                "private": _format_bool(engagement.get("isPrivate")),
                "industry": _format_value(engagement.get("industryName")),
                "service": _format_value(engagement.get("serviceLevel")),
                "scope_rank": _format_value(engagement.get("scopeRank")),
                "validation": _format_value(validation),
            }
        )

    index_md = _mk_index_markdown(
        rows=sorted(index_rows, key=lambda r: r["name"].lower()),
        listing_url=listing_url_first or "",
        fetched_at=fetched_at,
        pages_fetched=pages_to_fetch,
    )
    _write_text(out_dir / "INDEX.md", index_md)

    if args.combined:
        lines = []
        lines.append("# Bugcrowd Bounty Board (Combined)")
        lines.append("")
        lines.append(f"- Listing URL: {_format_value(listing_url_first or '')}")
        lines.append(f"- Pages fetched: {_format_value(pages_to_fetch)}")
        lines.append(f"- Fetched at (UTC): {_format_value(fetched_at)}")
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
