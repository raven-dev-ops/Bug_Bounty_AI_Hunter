import argparse

from .lib.io_utils import dump_data, load_data


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
            asset_type = asset.get("type")
            asset_value = asset.get("value")
            if not asset_type or not asset_value:
                continue
            key = (asset_type, asset_value)
            if key in seen:
                continue
            seen.add(key)
            seeds.append(
                {
                    "type": asset_type,
                    "value": asset_value,
                    "source": "scope",
                    "tags": ["seed"],
                }
            )
        profile["assets"] = seeds

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
