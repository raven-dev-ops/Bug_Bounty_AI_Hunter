import argparse
import base64
import json
import os
from urllib.request import Request, urlopen

from .lib.io_utils import dump_data, load_data
from .lib.scope_utils import asset_key, normalize_scope_assets


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _build_scope(data):
    return {
        "in_scope": _list(data.get("in_scope")),
        "out_of_scope": _list(data.get("out_of_scope")),
        "restrictions": _list(data.get("restrictions")),
        "notes": data.get("notes", ""),
    }


def _build_program(data):
    program = {}
    if data.get("program"):
        program["name"] = data.get("program")
    if data.get("platform"):
        program["platform"] = data.get("platform")
    if data.get("policy_url"):
        program["policy_url"] = data.get("policy_url")
    if data.get("contact"):
        program["contact"] = data.get("contact")
    return program


def _http_get_json(url, headers, timeout=15):
    request = Request(url)
    for key, value in headers.items():
        request.add_header(key, value)
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _hackerone_headers():
    api_id = os.environ.get("HACKERONE_API_ID")
    api_token = os.environ.get("HACKERONE_API_TOKEN")
    if not api_id or not api_token:
        raise SystemExit("HACKERONE_API_ID and HACKERONE_API_TOKEN are required.")
    token = base64.b64encode(f"{api_id}:{api_token}".encode("utf-8")).decode("utf-8")
    return {"Authorization": "Basic " + token, "Accept": "application/json"}


def _extract_hackerone_scopes(payload):
    if not payload:
        return []

    if isinstance(payload, dict) and "structured_scopes" in payload:
        return _list(payload.get("structured_scopes"))

    if isinstance(payload, dict) and "data" in payload:
        data = payload.get("data", {})
        included = payload.get("included", [])
        by_id = {
            item.get("id"): item
            for item in included
            if isinstance(item, dict) and item.get("type") == "structured_scope"
        }
        scopes = []
        relationships = data.get("relationships", {})
        structured = relationships.get("structured_scopes", {}).get("data", [])
        for ref in _list(structured):
            if not isinstance(ref, dict):
                continue
            scope = by_id.get(ref.get("id"))
            if scope:
                scopes.append(scope)
        if scopes:
            return scopes

    return _list(payload) if isinstance(payload, list) else []


def _map_hackerone_asset_type(asset_type):
    mapping = {
        "DOMAIN": "domain",
        "URL": "url",
        "CIDR": "cidr",
        "IP_ADDRESS": "ip",
        "IP_RANGE": "ip-range",
        "GOOGLE_PLAY_APP_ID": "mobile",
        "APPLE_APP_STORE": "mobile",
    }
    return mapping.get(str(asset_type).upper(), str(asset_type).lower())


def _build_scope_from_hackerone(scopes):
    in_scope = []
    out_scope = []
    restrictions = []
    for scope in scopes:
        if not isinstance(scope, dict):
            continue
        attributes = scope.get("attributes", scope)
        asset_type = _map_hackerone_asset_type(attributes.get("asset_type"))
        identifier = attributes.get("asset_identifier")
        instruction = attributes.get("instruction")
        eligible = attributes.get("eligible_for_submission", False)
        entry = {
            "type": asset_type,
            "value": identifier,
            "source": "hackerone",
            "notes": instruction,
        }
        if instruction:
            restrictions.append(instruction)
        if eligible:
            in_scope.append(entry)
        else:
            out_scope.append(entry)

    return {
        "in_scope": in_scope,
        "out_of_scope": out_scope,
        "restrictions": list({item for item in restrictions if item}),
        "notes": "Imported from HackerOne.",
    }


def _seed_assets(scope):
    assets = []
    for asset in _list(scope.get("in_scope")):
        if not isinstance(asset, dict):
            continue
        asset_type = asset.get("type")
        value = asset.get("value")
        if not asset_type or not value:
            continue
        ports = asset.get("ports")
        entry = {
            "type": asset_type,
            "value": value,
            "source": "scope",
            "tags": ["seed"],
        }
        if ports:
            entry["ports"] = ports
        if asset.get("notes"):
            entry["notes"] = asset.get("notes")
        assets.append(entry)
    return assets


def main():
    parser = argparse.ArgumentParser(description="Import scope exports.")
    parser.add_argument("--input", help="Scope export JSON/YAML or API payload.")
    parser.add_argument("--format", default="generic", help="Scope format.")
    parser.add_argument("--program", help="Program handle for API imports.")
    parser.add_argument(
        "--api-base",
        default="https://api.hackerone.com/v1",
        help="Base URL for platform APIs.",
    )
    parser.add_argument("--target-profile", help="Existing TargetProfile to update.")
    parser.add_argument("--output", required=True, help="Output TargetProfile path.")
    parser.add_argument("--schema-version", default="0.2.0")
    args = parser.parse_args()

    data = {}
    if args.input:
        data = load_data(args.input)

    if args.format == "generic":
        if not args.input:
            raise SystemExit("--input is required for generic format.")
        scope = _build_scope(data)
        program = _build_program(data)
    elif args.format == "hackerone":
        if not args.program:
            raise SystemExit("--program is required for hackerone format.")
        if data:
            payload = data
        else:
            endpoint = f"{args.api_base}/hackers/programs/{args.program}?include=structured_scopes"
            payload = _http_get_json(endpoint, _hackerone_headers())
        scopes = _extract_hackerone_scopes(payload)
        scope = _build_scope_from_hackerone(scopes)
        program = {
            "platform": "hackerone",
            "handle": args.program,
        }
        if isinstance(payload, dict):
            attributes = payload.get("data", {}).get("attributes", {})
            if attributes.get("name"):
                program["name"] = attributes.get("name")
            if attributes.get("policy_url"):
                program["policy_url"] = attributes.get("policy_url")
            if payload.get("data", {}).get("id"):
                program["id"] = payload.get("data", {}).get("id")
    else:
        raise SystemExit(f"Unsupported format: {args.format}")

    if args.target_profile:
        profile = load_data(args.target_profile)
    else:
        profile = {"schema_version": args.schema_version}

    scope_errors = []
    in_scope, errors = normalize_scope_assets(scope.get("in_scope"))
    scope_errors.extend(errors)
    out_scope, errors = normalize_scope_assets(scope.get("out_of_scope"))
    scope_errors.extend(errors)
    scope["in_scope"] = in_scope
    scope["out_of_scope"] = out_scope

    if program:
        profile["program"] = program
        profile.setdefault("name", program.get("name"))
    profile["scope"] = scope
    profile.setdefault("assets", [])
    profile["assets"].extend(_seed_assets(scope))
    normalized_assets, errors = normalize_scope_assets(profile.get("assets"))
    scope_errors.extend(errors)
    deduped = []
    seen = set()
    for asset in normalized_assets:
        key = asset_key(asset)
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        deduped.append(asset)
    profile["assets"] = deduped

    if scope_errors:
        message = "Scope asset normalization errors:\n" + "\n".join(scope_errors)
        raise SystemExit(message)

    if not profile.get("name"):
        profile["name"] = "Unnamed Program"

    dump_data(args.output, profile)


if __name__ == "__main__":
    main()
