import argparse
from datetime import datetime, timezone

from .lib.io_utils import dump_data, load_data


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_stores(stores):
    normalized = []
    for index, store in enumerate(_list(stores), 1):
        if not isinstance(store, dict):
            continue
        entry = dict(store)
        if not entry.get("id"):
            entry["id"] = f"store-{index:03d}"
        normalized.append(entry)
    return normalized


def _normalize_flows(flows):
    normalized = []
    for index, flow in enumerate(_list(flows), 1):
        if not isinstance(flow, dict):
            continue
        entry = dict(flow)
        if not entry.get("id"):
            entry["id"] = f"flow-{index:03d}"
        normalized.append(entry)
    return normalized


def build_dataflow_map(profile, schema_version):
    return {
        "schema_version": schema_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_profile": profile.get("id") or profile.get("name"),
        "ai_surfaces": profile.get("ai_surfaces", {}),
        "shadow_stores": _normalize_stores(profile.get("data_stores", [])),
        "flows": _normalize_flows(profile.get("data_flows", [])),
        "notes": [
            "Dataflow maps are high-level summaries only.",
            "Avoid real user data in artifacts.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate a dataflow map from a TargetProfile."
    )
    parser.add_argument("--target-profile", required=True, help="TargetProfile path.")
    parser.add_argument("--output", required=True, help="Output JSON/YAML path.")
    parser.add_argument("--schema-version", default="0.1.0")
    args = parser.parse_args()

    profile = load_data(args.target_profile)
    dataflow_map = build_dataflow_map(profile, args.schema_version)
    dump_data(args.output, dataflow_map)


if __name__ == "__main__":
    main()
