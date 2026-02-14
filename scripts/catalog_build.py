import argparse
from datetime import datetime, timezone
from pathlib import Path

from .connectors import get_connector
from .lib.catalog_guardrails import ensure_catalog_path
from .lib.fetcher import Fetcher
from .lib.git_utils import get_git_commit
from .lib.io_utils import dump_data
from .lib.schema_utils import validate_schema
from .program_registry import merge_sources


DEFAULT_CONNECTORS = [
    "yeswehack",
    "intigriti",
    "huntr",
    "bounty-targets-data",
    "disclose-io",
    "projectdiscovery",
]
CONNECTOR_DOMAINS = {
    "yeswehack": ["yeswehack.com"],
    "intigriti": ["intigriti.com"],
    "huntr": ["huntr.com"],
    "bounty-targets-data": ["raw.githubusercontent.com"],
    "disclose-io": ["raw.githubusercontent.com"],
    "projectdiscovery": ["raw.githubusercontent.com"],
}
PARSER_VERSION = "0.1.0"


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _run_id(start_time):
    return f"ingestion-{start_time.strftime('%Y%m%dT%H%M%SZ')}"


def _ensure_catalog_path(path):
    ensure_catalog_path(path, label="Catalog output")


def _parse_connectors(value):
    if not value:
        return list(DEFAULT_CONNECTORS)
    if isinstance(value, list):
        items = value
    else:
        items = str(value).replace(",", " ").split()
    cleaned = []
    for item in items:
        item = item.strip()
        if item:
            cleaned.append(item)
    return cleaned or list(DEFAULT_CONNECTORS)


def _resolve_allow_domains(connectors, allow_domains):
    domains = set()
    if allow_domains:
        for entry in allow_domains:
            if not entry:
                continue
            domains.add(entry.strip().lower())
        return sorted(domains)
    for name in connectors:
        for domain in CONNECTOR_DOMAINS.get(name, []):
            domains.add(domain)
    return sorted(domains)


def _build_fetcher(args, allow_domains):
    if args.fixtures_dir:
        return None
    if not args.public_only:
        raise SystemExit("Live catalog build requires --public-only.")
    return Fetcher(
        cache_dir=args.cache_dir,
        user_agent=args.user_agent,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        backoff_seconds=args.backoff_seconds,
        min_delay_seconds=args.min_delay_seconds,
        max_requests_per_domain=args.max_requests_per_domain,
        max_bytes_per_domain=args.max_bytes_per_domain,
        allow_domains=allow_domains,
        robots_mode=not args.ignore_robots,
        public_only=args.public_only,
    )


def _collect_sources(connector, fetcher, fixtures_dir, fetched_at, git_commit):
    sources = []
    errors = []
    programs = connector.list_programs(fetcher, fixtures_dir=fixtures_dir)
    for program in programs:
        try:
            detail = connector.fetch_details(
                fetcher, program, fixtures_dir=fixtures_dir
            )
        except Exception as exc:
            errors.append(str(exc))
            continue
        detail["parser_version"] = PARSER_VERSION
        detail["fetched_at"] = fetched_at
        if git_commit:
            detail["git_commit"] = git_commit
        sources.append(detail)
    report = {
        "name": connector.name,
        "listed": len(programs),
        "enriched": len(sources),
        "errors": errors,
    }
    return sources, report


def _empty_metrics():
    return {
        "requests": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "failures": 0,
        "retries": 0,
        "throttle_sleeps": 0,
        "domains": {},
    }


def _build_audit_summary(audit):
    connectors = audit.get("connectors") or []
    outputs = audit.get("outputs") or {}
    metrics = audit.get("metrics") or {}
    domains = metrics.get("domains") or {}

    connector_summary = []
    for connector in connectors:
        errors = connector.get("errors") or []
        connector_summary.append(
            {
                "name": connector.get("name", "unknown"),
                "listed": connector.get("listed", 0),
                "enriched": connector.get("enriched", 0),
                "errors": len(errors),
            }
        )

    domain_summary = {}
    for domain in sorted(domains):
        entry = domains.get(domain) or {}
        domain_summary[domain] = {
            "requests": entry.get("requests", 0),
            "cache_hits": entry.get("cache_hits", 0),
            "failures": entry.get("failures", 0),
            "retries": entry.get("retries", 0),
            "total_time_ms": entry.get("total_time_ms", 0),
            "bytes": entry.get("bytes", 0),
        }

    return {
        "schema_version": audit.get("schema_version"),
        "run_id": audit.get("run_id"),
        "status": audit.get("status"),
        "started_at": audit.get("started_at"),
        "finished_at": audit.get("finished_at"),
        "public_only": audit.get("public_only"),
        "robots_mode": audit.get("robots_mode"),
        "allow_domains": audit.get("allow_domains") or [],
        "sources_total": audit.get("sources_total", 0),
        "connectors": connector_summary,
        "outputs": {
            "registry_path": outputs.get("registry_path"),
            "registry_written": outputs.get("registry_written"),
            "registry_programs": outputs.get("registry_programs"),
            "audit_log_path": outputs.get("audit_log_path"),
            "audit_summary_path": outputs.get("audit_summary_path"),
            "audit_summary_json_path": outputs.get("audit_summary_json_path"),
        },
        "metrics": {
            "requests": metrics.get("requests", 0),
            "cache_hits": metrics.get("cache_hits", 0),
            "cache_misses": metrics.get("cache_misses", 0),
            "failures": metrics.get("failures", 0),
            "retries": metrics.get("retries", 0),
            "throttle_sleeps": metrics.get("throttle_sleeps", 0),
        },
        "domain_metrics": domain_summary,
        "errors": len(audit.get("errors") or []),
    }


def _render_audit_summary(audit):
    lines = [
        "# Catalog Ingestion Audit Summary",
        "",
        f"Run ID: {audit.get('run_id')}",
        f"Status: {audit.get('status')}",
        f"Started: {audit.get('started_at')}",
        f"Finished: {audit.get('finished_at')}",
        "",
        "## Connectors",
    ]

    connectors = audit.get("connectors") or []
    if not connectors:
        lines.append("- None")
    else:
        for connector in connectors:
            name = connector.get("name", "unknown")
            listed = connector.get("listed", 0)
            enriched = connector.get("enriched", 0)
            errors = connector.get("errors") or []
            suffix = " (errors)" if errors else ""
            lines.append(f"- {name}: listed {listed}, enriched {enriched}{suffix}")

    outputs = audit.get("outputs") or {}
    lines.extend(
        [
            "",
            "## Outputs",
            f"- Registry: {outputs.get('registry_path')}",
            f"- Programs: {outputs.get('registry_programs')}",
            f"- Audit log: {outputs.get('audit_log_path')}",
            f"- Audit summary: {outputs.get('audit_summary_path')}",
            f"- Audit summary JSON: {outputs.get('audit_summary_json_path')}",
            "",
            "## Metrics",
        ]
    )

    metrics = audit.get("metrics") or {}
    lines.extend(
        [
            f"- Requests: {metrics.get('requests', 0)}",
            f"- Cache hits: {metrics.get('cache_hits', 0)}",
            f"- Cache misses: {metrics.get('cache_misses', 0)}",
            f"- Failures: {metrics.get('failures', 0)}",
            f"- Retries: {metrics.get('retries', 0)}",
            f"- Throttle sleeps: {metrics.get('throttle_sleeps', 0)}",
        ]
    )

    domains = metrics.get("domains") or {}
    if domains:
        lines.extend(["", "## Domain Metrics"])
        for domain in sorted(domains):
            entry = domains.get(domain) or {}
            lines.append(
                "- {}: requests {}, total_time_ms {}, bytes {}, failures {}, retries {}".format(
                    domain,
                    entry.get("requests", 0),
                    entry.get("total_time_ms", 0),
                    entry.get("bytes", 0),
                    entry.get("failures", 0),
                    entry.get("retries", 0),
                )
            )

    errors = audit.get("errors") or []
    if errors:
        lines.extend(["", "## Errors"])
        for error in errors:
            lines.append(f"- {error}")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Build the public program registry from ingestion sources."
    )
    parser.add_argument("--connectors", help="Comma-separated connector names.")
    parser.add_argument(
        "--output",
        default="data/program_registry.json",
        help="Registry output path.",
    )
    parser.add_argument("--fixtures-dir", help="Use offline fixtures for testing.")
    parser.add_argument(
        "--cache-dir",
        default="data/catalog_cache",
        help="Cache directory for fetched pages.",
    )
    parser.add_argument(
        "--public-only",
        action="store_true",
        help="Restrict to public HTTP(S) sources.",
    )
    parser.add_argument(
        "--allow-domain",
        action="append",
        help="Allowlisted domain (repeatable).",
    )
    parser.add_argument(
        "--ignore-robots",
        action="store_true",
        help="Disable robots.txt checks.",
    )
    parser.add_argument("--user-agent", default="bbhai-catalog/0.1")
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--backoff-seconds", type=float, default=1.0)
    parser.add_argument("--min-delay-seconds", type=float, default=1.0)
    parser.add_argument("--max-requests-per-domain", type=int, default=10)
    parser.add_argument("--max-bytes-per-domain", type=int)
    parser.add_argument("--audit-log", help="Audit log output path.")
    parser.add_argument("--audit-summary", help="Audit summary Markdown output.")
    parser.add_argument("--audit-summary-json", help="Audit summary JSON output.")
    args = parser.parse_args()

    start_time = datetime.now(timezone.utc)
    started_at = start_time.isoformat()
    run_id = _run_id(start_time)
    git_commit = get_git_commit()

    connectors = _parse_connectors(args.connectors)
    missing = [name for name in connectors if get_connector(name) is None]
    if missing:
        raise SystemExit(f"Unknown connectors: {', '.join(missing)}")

    if args.fixtures_dir:
        fixtures_path = Path(args.fixtures_dir)
        if not fixtures_path.exists():
            raise SystemExit(f"Fixtures directory not found: {fixtures_path}")
    else:
        fixtures_path = None

    allow_domains = _resolve_allow_domains(connectors, args.allow_domain)
    fetcher = None

    audit_errors = []
    connector_reports = []
    sources = []
    registry_programs = None
    output_written = False

    audit_dir = Path("data") / "ingestion_audit"
    audit_log_path = (
        Path(args.audit_log) if args.audit_log else audit_dir / f"{run_id}.json"
    )
    audit_summary_path = (
        Path(args.audit_summary) if args.audit_summary else audit_dir / f"{run_id}.md"
    )
    audit_summary_json_path = (
        Path(args.audit_summary_json)
        if args.audit_summary_json
        else audit_dir / f"{run_id}.summary.json"
    )

    _ensure_catalog_path(args.output)
    _ensure_catalog_path(args.cache_dir)
    _ensure_catalog_path(audit_log_path)
    _ensure_catalog_path(audit_summary_path)
    _ensure_catalog_path(audit_summary_json_path)

    status = "success"
    try:
        try:
            fetcher = _build_fetcher(args, allow_domains)
        except SystemExit as exc:
            audit_errors.append(str(exc))
            status = "failed"
        except Exception as exc:
            audit_errors.append(str(exc))
            status = "failed"

        fetched_at = _timestamp()
        if status != "failed":
            for name in connectors:
                connector = get_connector(name)
                try:
                    batch, report = _collect_sources(
                        connector, fetcher, fixtures_path, fetched_at, git_commit
                    )
                except Exception as exc:
                    audit_errors.append(f"{name}: {exc}")
                    connector_reports.append(
                        {
                            "name": name,
                            "listed": 0,
                            "enriched": 0,
                            "errors": [str(exc)],
                        }
                    )
                    if status == "success":
                        status = "partial"
                    continue
                sources.extend(batch)
                connector_reports.append(report)
                if report.get("errors") and status == "success":
                    status = "partial"

        programs = None
        if status != "failed":
            try:
                programs = merge_sources(sources)
            except SystemExit as exc:
                audit_errors.append(f"merge_sources: {exc}")
                status = "failed"
            except Exception as exc:
                audit_errors.append(f"merge_sources: {exc}")
                status = "failed"

        if status != "failed" and programs is not None:
            registry_programs = len(programs)
            registry = {
                "schema_version": "0.1.0",
                "created_at": fetched_at,
                "updated_at": _timestamp(),
                "programs": programs,
            }
            validate_schema(registry, "schemas/program_registry.schema.json")
            dump_data(args.output, registry)
            output_written = True
    finally:
        finished_at = _timestamp()
        metrics = fetcher.metrics if fetcher else _empty_metrics()
        audit = {
            "schema_version": "0.1.0",
            "run_id": run_id,
            "status": status,
            "started_at": started_at,
            "finished_at": finished_at,
            "public_only": args.public_only,
            "robots_mode": not args.ignore_robots,
            "allow_domains": allow_domains,
            "connectors": connector_reports,
            "sources_total": len(sources),
            "outputs": {
                "registry_path": str(args.output),
                "registry_written": output_written,
                "registry_programs": registry_programs,
                "audit_log_path": str(audit_log_path),
                "audit_summary_path": str(audit_summary_path),
                "audit_summary_json_path": str(audit_summary_json_path),
            },
            "cache_dir": str(args.cache_dir),
            "fixtures_dir": str(fixtures_path) if fixtures_path else None,
            "metrics": metrics,
            "errors": audit_errors,
        }
        dump_data(audit_log_path, audit)
        audit_summary_path.parent.mkdir(parents=True, exist_ok=True)
        audit_summary_path.write_text(_render_audit_summary(audit), encoding="utf-8")
        dump_data(audit_summary_json_path, _build_audit_summary(audit))

    if status == "failed":
        raise SystemExit(f"Catalog build failed. Audit log: {audit_log_path}")


if __name__ == "__main__":
    main()
