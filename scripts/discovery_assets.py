import argparse
from datetime import datetime, timezone
from urllib.parse import urlparse

from .lib.io_utils import dump_data, load_data
from .lib.scope_utils import asset_key


DEFAULT_PREFIXES = ["www", "api", "dev", "staging"]


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _asset_key(asset_type, value, ports=None):
    asset = {"type": asset_type, "value": value}
    if ports:
        asset["ports"] = ports
    return asset_key(asset)


def _parse_prefixes(prefixes):
    if not prefixes:
        return []
    if isinstance(prefixes, list):
        return [item.strip() for item in prefixes if item.strip()]
    return [item.strip() for item in str(prefixes).split(",") if item.strip()]


def _domain_from_value(value):
    if "://" in value:
        parsed = urlparse(value)
        return parsed.hostname or value
    return value


def _collect_scope_assets(profile, include_out_of_scope):
    scope = profile.get("scope", {}) or {}
    in_scope = _list(scope.get("in_scope"))
    out_of_scope = _list(scope.get("out_of_scope")) if include_out_of_scope else []
    return in_scope + out_of_scope


def build_assets(profile, prefixes, extra_seeds, include_out_of_scope):
    assets = []
    seen = set()

    for asset in _collect_scope_assets(profile, include_out_of_scope):
        if not isinstance(asset, dict):
            continue
        asset_type = asset.get("type")
        value = asset.get("value")
        if not asset_type or not value:
            continue
        key = _asset_key(asset_type, value, asset.get("ports"))
        if key in seen:
            continue
        seen.add(key)
        asset_entry = dict(asset)
        asset_entry.setdefault("source", "scope")
        assets.append(asset_entry)

    for asset in _list(profile.get("assets")):
        if not isinstance(asset, dict):
            continue
        asset_type = asset.get("type")
        value = asset.get("value")
        if not asset_type or not value:
            continue
        key = _asset_key(asset_type, value, asset.get("ports"))
        if key in seen:
            continue
        seen.add(key)
        asset_entry = dict(asset)
        asset_entry.setdefault("source", "profile")
        assets.append(asset_entry)

    for seed in _parse_prefixes(extra_seeds):
        key = _asset_key("domain", seed)
        if key in seen:
            continue
        seen.add(key)
        assets.append(
            {
                "type": "domain",
                "value": seed,
                "source": "seed",
                "tags": ["seed"],
            }
        )

    derived_assets = []
    for asset in assets:
        if asset.get("type") not in ("domain", "subdomain"):
            continue
        domain = _domain_from_value(asset.get("value", ""))
        for prefix in prefixes:
            candidate = f"{prefix}.{domain}"
            key = _asset_key("subdomain", candidate)
            if key in seen:
                continue
            seen.add(key)
            derived_assets.append(
                {
                    "type": "subdomain",
                    "value": candidate,
                    "source": "derived",
                    "tags": ["candidate"],
                }
            )

    return assets + derived_assets


def main():
    parser = argparse.ArgumentParser(description="Generate an asset discovery list.")
    parser.add_argument("--target-profile", required=True, help="TargetProfile path.")
    parser.add_argument("--output", required=True, help="Output JSON/YAML path.")
    parser.add_argument(
        "--prefixes",
        default=",".join(DEFAULT_PREFIXES),
        help="Comma-separated subdomain prefixes.",
    )
    parser.add_argument("--extra-seeds", default="", help="Comma-separated seeds.")
    parser.add_argument(
        "--include-out-of-scope",
        action="store_true",
        help="Include out-of-scope entries for reference only.",
    )
    args = parser.parse_args()

    profile = load_data(args.target_profile)
    prefixes = _parse_prefixes(args.prefixes)
    assets = build_assets(
        profile, prefixes, args.extra_seeds, args.include_out_of_scope
    )

    output = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_profile": profile.get("id") or profile.get("name"),
        "assets": assets,
        "notes": [
            "Discovery output is a candidate list only.",
            "No live DNS or network checks were performed.",
        ],
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
