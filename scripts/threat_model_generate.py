import argparse
from datetime import datetime, timezone

from .lib.io_utils import dump_data, load_data


SURFACE_DEFS = [
    {
        "key": "rag",
        "name": "RAG retrieval",
        "description": "Retrieval pipelines and context assembly for prompts.",
        "keywords": ("rag", "retrieval", "vector", "index", "search"),
        "threat": {
            "title": "Cross-tenant context leakage",
            "impact": "Sensitive context exposed to other tenants.",
            "likelihood": "medium",
            "severity": "high",
            "mitigations": [
                "tenant-aware retrieval",
                "per-document ACL enforcement",
                "canary isolation checks",
            ],
        },
    },
    {
        "key": "embeddings",
        "name": "Embedding stores",
        "description": "Vector storage, embedding access, and export paths.",
        "keywords": ("embedding", "vector", "index"),
        "threat": {
            "title": "Embedding exposure via export or logs",
            "impact": "Embedding data leaked through exports or telemetry.",
            "likelihood": "medium",
            "severity": "medium",
            "mitigations": [
                "restrict export endpoints",
                "audit logging access",
                "rotate sensitive embeddings",
            ],
        },
    },
    {
        "key": "fine_tuning",
        "name": "Fine-tuning data",
        "description": "Training data ingestion and model tuning pipelines.",
        "keywords": ("training", "fine", "dataset", "tuning"),
        "threat": {
            "title": "Training data leakage",
            "impact": "Sensitive training data appears in model outputs.",
            "likelihood": "medium",
            "severity": "high",
            "mitigations": [
                "data minimization and redaction",
                "canary tracing in training sets",
                "model output monitoring",
            ],
        },
    },
    {
        "key": "logging",
        "name": "Prompt logging",
        "description": "Prompt and response telemetry pipelines.",
        "keywords": ("log", "telemetry", "trace"),
        "threat": {
            "title": "Over-retained prompt logs",
            "impact": "Long-lived access to sensitive prompts or context.",
            "likelihood": "medium",
            "severity": "medium",
            "mitigations": [
                "short retention",
                "access reviews",
                "redaction at ingest",
            ],
        },
    },
    {
        "key": "agents",
        "name": "Tool-using agents",
        "description": "Agent orchestration and tool call execution.",
        "keywords": ("agent", "tool"),
        "threat": {
            "title": "Untrusted data reaches tool calls",
            "impact": "Agent executes tools with untrusted inputs.",
            "likelihood": "medium",
            "severity": "high",
            "mitigations": [
                "strict tool allowlists",
                "structured arguments for tools",
                "human approval for high-risk actions",
            ],
        },
    },
]


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _scope_values(items):
    values = []
    for item in _list(items):
        if isinstance(item, dict):
            item_type = item.get("type", "asset")
            value = item.get("value")
            if value:
                values.append(f"{item_type}:{value}")
        else:
            values.append(str(item))
    return values


def _store_label(store):
    name = store.get("name") or store.get("id") or store.get("type")
    if not name:
        return None
    return f"store:{name}"


def _stores_for_keywords(stores, keywords):
    matches = []
    for store in _list(stores):
        if not isinstance(store, dict):
            continue
        haystack = " ".join(
            str(store.get(field, "")).lower()
            for field in ("name", "id", "type", "notes")
        )
        if any(keyword in haystack for keyword in keywords):
            label = _store_label(store)
            if label:
                matches.append(label)
    return sorted(set(matches))


def _access_controls(profile):
    access_model = profile.get("access_model", {}) or {}
    controls = []
    tenancy = access_model.get("tenancy")
    if tenancy:
        controls.append(f"tenancy:{tenancy}")
    auth = _list(access_model.get("auth"))
    if auth:
        controls.append(f"auth:{', '.join(str(item) for item in auth)}")
    roles = _list(access_model.get("roles"))
    if roles:
        controls.append(f"roles:{', '.join(str(item) for item in roles)}")
    return controls


def build_threat_model(profile, schema_version):
    ai_surfaces = profile.get("ai_surfaces", {}) or {}
    stores = profile.get("data_stores", [])
    controls = _access_controls(profile)

    surfaces = []
    threats = []
    surface_index = 1
    threat_index = 1

    for surface_def in SURFACE_DEFS:
        if not ai_surfaces.get(surface_def["key"], False):
            continue
        surface_id = f"surface-{surface_index:03d}"
        surface_index += 1
        assets = _stores_for_keywords(stores, surface_def["keywords"])
        surfaces.append(
            {
                "id": surface_id,
                "name": surface_def["name"],
                "description": surface_def["description"],
                "assets": assets,
                "controls": controls,
            }
        )
        threat = surface_def["threat"]
        threats.append(
            {
                "id": f"threat-{threat_index:03d}",
                "title": threat["title"],
                "surface": surface_def["name"],
                "impact": threat["impact"],
                "likelihood": threat["likelihood"],
                "severity": threat["severity"],
                "mitigations": threat["mitigations"],
                "notes": "Use canary strings and synthetic data only.",
            }
        )
        threat_index += 1

    third_party = _list(ai_surfaces.get("third_party"))
    if third_party:
        surface_id = f"surface-{surface_index:03d}"
        surfaces.append(
            {
                "id": surface_id,
                "name": "Third-party LLM APIs",
                "description": "External AI providers and integrations.",
                "assets": [str(item) for item in third_party if str(item)],
                "controls": controls,
            }
        )
        threats.append(
            {
                "id": f"threat-{threat_index:03d}",
                "title": "Third-party prompt retention",
                "surface": "Third-party LLM APIs",
                "impact": "Sensitive prompts retained outside the target boundary.",
                "likelihood": "medium",
                "severity": "medium",
                "mitigations": [
                    "limit data sent to third parties",
                    "review provider retention policies",
                    "tokenize or redact sensitive fields",
                ],
                "notes": "Review contracts and retention policies.",
            }
        )

    assumptions = [
        "Authorized testing only.",
        "Use synthetic data and canary strings.",
    ]
    constraints = profile.get("constraints", {}) or {}
    stop_conditions = _list(constraints.get("stop_conditions"))
    for condition in stop_conditions:
        if condition:
            assumptions.append(f"Stop condition: {condition}")

    scope = profile.get("scope", {}) or {}
    out_of_scope = _scope_values(scope.get("out_of_scope"))

    return {
        "schema_version": schema_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": profile.get("id") or profile.get("name"),
        "assumptions": assumptions,
        "attack_surfaces": surfaces,
        "threats": threats,
        "out_of_scope": out_of_scope,
        "notes": ["Threat model is high level and non-weaponized."],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate a threat model from a TargetProfile."
    )
    parser.add_argument("--target-profile", required=True, help="TargetProfile path.")
    parser.add_argument("--output", required=True, help="Output JSON/YAML path.")
    parser.add_argument("--schema-version", default="0.1.0")
    args = parser.parse_args()

    profile = load_data(args.target_profile)
    threat_model = build_threat_model(profile, args.schema_version)
    dump_data(args.output, threat_model)


if __name__ == "__main__":
    main()
