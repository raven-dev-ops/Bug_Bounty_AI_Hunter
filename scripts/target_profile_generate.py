import argparse

from .lib.io_utils import dump_data, load_data
from .lib.scope_utils import asset_key, normalize_scope_assets


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def build_profile(questionnaire, schema_version, name, profile_id):
    program = questionnaire.get("program", {}) or {}
    scope = questionnaire.get("scope", {}) or {}
    assets = questionnaire.get("assets", []) or []

    scope_errors = []
    in_scope, errors = normalize_scope_assets(scope.get("in_scope"))
    scope_errors.extend(errors)
    out_scope, errors = normalize_scope_assets(scope.get("out_of_scope"))
    scope_errors.extend(errors)
    scope["in_scope"] = in_scope
    scope["out_of_scope"] = out_scope
    assets, errors = normalize_scope_assets(assets)
    scope_errors.extend(errors)

    profile = {
        "schema_version": schema_version,
        "id": profile_id or questionnaire.get("id"),
        "name": name or questionnaire.get("name") or program.get("name"),
        "program": program,
        "contacts": questionnaire.get("contacts", {}),
        "scope": scope,
        "assets": assets,
        "ai_surfaces": questionnaire.get("ai_surfaces", {}),
        "data_stores": questionnaire.get("data_stores", []),
        "data_flows": questionnaire.get("data_flows", []),
        "access_model": questionnaire.get("access_model", {}),
        "constraints": questionnaire.get("constraints", {}),
        "notes": questionnaire.get("notes", ""),
    }

    if not profile["name"]:
        raise SystemExit("TargetProfile name is required.")

    if not profile["assets"] and scope.get("in_scope"):
        seeds = []
        seen = set()
        for asset in _list(scope.get("in_scope")):
            if not isinstance(asset, dict):
                continue
            key = asset_key(asset)
            if not key:
                continue
            if key in seen:
                continue
            seen.add(key)
            entry = {
                "type": asset.get("type"),
                "value": asset.get("value"),
                "source": "scope",
                "tags": ["seed"],
            }
            if asset.get("ports"):
                entry["ports"] = asset.get("ports")
            if asset.get("notes"):
                entry["notes"] = asset.get("notes")
            seeds.append(entry)
        profile["assets"] = seeds

    if scope_errors:
        message = "Scope asset normalization errors:\n" + "\n".join(scope_errors)
        raise SystemExit(message)

    return profile


def main():
    parser = argparse.ArgumentParser(
        description="Generate a TargetProfile from a questionnaire."
    )
    parser.add_argument("--input", required=True, help="Questionnaire YAML or JSON.")
    parser.add_argument("--output", required=True, help="Output profile path.")
    parser.add_argument("--schema-version", default="0.2.0")
    parser.add_argument("--name", help="Override profile name.")
    parser.add_argument("--id", dest="profile_id", help="Override profile id.")
    args = parser.parse_args()

    questionnaire = load_data(args.input)
    profile = build_profile(
        questionnaire, args.schema_version, args.name, args.profile_id
    )
    dump_data(args.output, profile)


if __name__ == "__main__":
    main()
