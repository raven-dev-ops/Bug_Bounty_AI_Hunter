import argparse
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data


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


def _seed_assets(scope):
    assets = []
    for asset in _list(scope.get("in_scope")):
        if not isinstance(asset, dict):
            continue
        asset_type = asset.get("type")
        value = asset.get("value")
        if not asset_type or not value:
            continue
        assets.append(
            {
                "type": asset_type,
                "value": value,
                "source": "scope",
                "tags": ["seed"],
            }
        )
    return assets


def main():
    parser = argparse.ArgumentParser(description="Import scope exports.")
    parser.add_argument("--input", required=True, help="Scope export JSON/YAML.")
    parser.add_argument("--format", default="generic", help="Scope format.")
    parser.add_argument("--target-profile", help="Existing TargetProfile to update.")
    parser.add_argument("--output", required=True, help="Output TargetProfile path.")
    parser.add_argument("--schema-version", default="0.2.0")
    args = parser.parse_args()

    data = load_data(args.input)
    if args.format != "generic":
        raise SystemExit(f"Unsupported format: {args.format}")

    scope = _build_scope(data)
    program = _build_program(data)

    if args.target_profile:
        profile = load_data(args.target_profile)
    else:
        profile = {"schema_version": args.schema_version}

    if program:
        profile["program"] = program
        profile.setdefault("name", program.get("name"))
    profile["scope"] = scope
    profile.setdefault("assets", [])
    profile["assets"].extend(_seed_assets(scope))
    deduped = []
    seen = set()
    for asset in profile["assets"]:
        if not isinstance(asset, dict):
            continue
        key = (asset.get("type"), asset.get("value"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(asset)
    profile["assets"] = deduped

    if not profile.get("name"):
        profile["name"] = "Unnamed Program"

    dump_data(args.output, profile)


if __name__ == "__main__":
    main()
