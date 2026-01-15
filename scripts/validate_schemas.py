import argparse

import jsonschema

from .lib.io_utils import load_data


SCHEMA_CASES = [
    ("schemas/target_profile.schema.json", "examples/target_profile_minimal.yaml", False),
    ("schemas/finding.schema.json", "examples/finding_example.json", False),
    ("schemas/finding.schema.json", "examples/outputs/findings.json", True),
    ("schemas/evidence.schema.json", "examples/evidence_example.json", False),
    ("schemas/test_case.schema.json", "examples/test_case_example.json", False),
    ("schemas/test_case.schema.json", "examples/test_case_rag_minimal.json", False),
    ("schemas/test_case.schema.json", "examples/test_case_logging_minimal.json", False),
    ("schemas/test_case.schema.json", "examples/test_case_embedding_minimal.json", False),
    ("schemas/test_case.schema.json", "examples/test_case_agents_minimal.json", False),
    ("schemas/component_manifest.schema.json", "examples/component_manifest.yaml", False),
    ("schemas/dataflow_map.schema.json", "examples/dataflow_map_example.json", False),
    ("schemas/threat_model.schema.json", "examples/threat_model_example.json", False),
    ("schemas/pipeline_config.schema.json", "examples/pipeline_config.yaml", False),
    ("schemas/pipeline_plan.schema.json", "examples/pipeline_plan_output.json", False),
    ("schemas/discovery_output.schema.json", "examples/discovery_output.json", False),
    ("schemas/scan_plan.schema.json", "examples/scan_plan_output.json", False),
    ("schemas/triage_output.schema.json", "examples/triage_output.json", False),
    ("schemas/intel_output.schema.json", "examples/intel_output.json", False),
    ("schemas/component_registry.schema.json", "examples/component_registry_output.json", False),
    ("schemas/findings_db.schema.json", "examples/findings_db_output.json", False),
    ("schemas/evidence_registry.schema.json", "examples/evidence_registry_output.json", False),
    ("schemas/notification_output.schema.json", "examples/notification_output.json", False),
    ("schemas/attachments_manifest.schema.json", "examples/outputs/attachments_manifest.json", False),
    ("schemas/reproducibility_pack.schema.json", "examples/outputs/reproducibility_pack.json", False),
]


def _validate_case(schema_path, data_path, list_items):
    schema = load_data(schema_path)
    data = load_data(data_path)
    if list_items:
        if not isinstance(data, list):
            raise SystemExit(f"Expected list in {data_path}")
        for entry in data:
            jsonschema.validate(entry, schema)
    else:
        jsonschema.validate(data, schema)


def main():
    parser = argparse.ArgumentParser(description="Validate example files.")
    parser.add_argument("--schema", action="append", help="Additional schema file.")
    args = parser.parse_args()

    for schema_path, data_path, list_items in SCHEMA_CASES:
        _validate_case(schema_path, data_path, list_items)

    if args.schema:
        for schema_path in args.schema:
            schema = load_data(schema_path)
            jsonschema.Draft202012Validator.check_schema(schema)


if __name__ == "__main__":
    main()
