import argparse
from datetime import datetime, timezone
import base64
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data
from lib.rate_limit import RateLimiter


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _targets_from_input(data):
    if isinstance(data, dict) and "assets" in data:
        return _list(data.get("assets"))
    if isinstance(data, dict) and "scope" in data:
        scope = data.get("scope", {})
        return _list(scope.get("in_scope"))
    return _list(data)


def _asset_values(assets):
    values = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        value = asset.get("value")
        if value:
            values.append(value.lower())
    return values


def _match_record(record_value, targets):
    record_value = (record_value or "").lower()
    return any(record_value.endswith(target) for target in targets)


def _is_ip(value):
    parts = value.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True


def _http_get_json(url, headers, timeout):
    request = Request(url)
    for key, value in headers.items():
        request.add_header(key, value)
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _shodan_record(asset, api_key, timeout):
    if _is_ip(asset):
        endpoint = f"https://api.shodan.io/shodan/host/{asset}?key={api_key}"
    else:
        endpoint = f"https://api.shodan.io/dns/domain/{asset}?key={api_key}"
    data = _http_get_json(endpoint, {}, timeout)
    return {
        "asset": asset,
        "provider": "shodan",
        "queried_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def _censys_record(asset, api_id, api_secret, timeout, query_override):
    query = query_override
    if not query:
        query = f"dns.names: {asset}" if not _is_ip(asset) else f"ip: {asset}"
    params = urlencode({"q": query, "per_page": 1})
    endpoint = f"https://search.censys.io/api/v2/hosts/search?{params}"
    auth = f"{api_id}:{api_secret}".encode("utf-8")
    token = base64.b64encode(auth).decode("utf-8")
    headers = {"Authorization": "Basic " + token}
    data = _http_get_json(endpoint, headers, timeout)
    return {
        "asset": asset,
        "provider": "censys",
        "query": query,
        "queried_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def main():
    parser = argparse.ArgumentParser(description="Enrich assets with intel records.")
    parser.add_argument("--source", help="Intel source JSON/YAML (file provider).")
    parser.add_argument("--targets", required=True, help="Targets input path.")
    parser.add_argument("--output", required=True, help="Output JSON/YAML path.")
    parser.add_argument(
        "--provider",
        default="file",
        choices=["file", "shodan", "censys"],
        help="Provider name.",
    )
    parser.add_argument("--min-delay-seconds", type=float, default=0.0)
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--max-records", type=int, default=25)
    parser.add_argument(
        "--no-scope-enforcement",
        action="store_true",
        help="Disable target scope allowlist enforcement.",
    )
    parser.add_argument(
        "--query",
        help="Override query for the Censys provider.",
    )
    args = parser.parse_args()

    targets_data = load_data(args.targets)
    targets = _asset_values(_targets_from_input(targets_data))

    records = []
    notes = []
    limiter = RateLimiter(args.min_delay_seconds)
    timeout = args.timeout_seconds

    if args.provider == "file":
        if not args.source:
            raise SystemExit("--source is required for file provider.")
        source_data = load_data(args.source)
        if isinstance(source_data, dict) and "records" in source_data:
            records = _list(source_data.get("records"))
        else:
            records = _list(source_data)
    elif args.provider == "shodan":
        api_key = os.environ.get("SHODAN_API_KEY")
        if not api_key:
            raise SystemExit("SHODAN_API_KEY is required for Shodan.")
        for asset in targets[: args.max_records]:
            limiter.wait()
            try:
                records.append(_shodan_record(asset, api_key, timeout))
            except Exception as exc:
                notes.append(f"Shodan error for {asset}: {exc}")
    elif args.provider == "censys":
        api_id = os.environ.get("CENSYS_API_ID")
        api_secret = os.environ.get("CENSYS_API_SECRET")
        if not api_id or not api_secret:
            raise SystemExit("CENSYS_API_ID and CENSYS_API_SECRET are required.")
        for asset in targets[: args.max_records]:
            limiter.wait()
            try:
                records.append(_censys_record(asset, api_id, api_secret, timeout, args.query))
            except Exception as exc:
                notes.append(f"Censys error for {asset}: {exc}")

    enforce_scope = not args.no_scope_enforcement
    matches = []
    for record in records:
        if not isinstance(record, dict):
            continue
        value = record.get("asset") or record.get("domain") or record.get("host")
        if not value:
            continue
        if enforce_scope and not _match_record(value, targets):
            continue
        if "source" not in record:
            record["source"] = args.provider
        matches.append(record)

    output = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider,
        "matches": matches,
        "notes": notes,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
