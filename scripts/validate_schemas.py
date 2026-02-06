import argparse

import jsonschema

from .lib.io_utils import load_data


SCHEMA_CASES = [
    (
        "schemas/target_profile.schema.json",
        "examples/target_profile_minimal.yaml",
        False,
    ),
    (
        "schemas/scope_asset.schema.json",
        "examples/scope_assets_example.json",
        True,
    ),
    ("schemas/finding.schema.json", "examples/finding_example.json", False),
    ("schemas/finding.schema.json", "examples/outputs/findings.json", True),
    ("schemas/evidence.schema.json", "examples/evidence_example.json", False),
    (
        "schemas/tool_run.schema.json",
        "examples/tool_runs/tool_run_example.json",
        False,
    ),
    ("schemas/test_case.schema.json", "examples/test_case_example.json", False),
    ("schemas/test_case.schema.json", "examples/test_case_rag_minimal.json", False),
    ("schemas/test_case.schema.json", "examples/test_case_logging_minimal.json", False),
    (
        "schemas/test_case.schema.json",
        "examples/test_case_embedding_minimal.json",
        False,
    ),
    ("schemas/test_case.schema.json", "examples/test_case_agents_minimal.json", False),
    (
        "schemas/component_manifest.schema.json",
        "examples/component_manifest.yaml",
        False,
    ),
    ("schemas/dataflow_map.schema.json", "examples/dataflow_map_example.json", False),
    ("schemas/threat_model.schema.json", "examples/threat_model_example.json", False),
    ("schemas/pipeline_config.schema.json", "examples/pipeline_config.yaml", False),
    ("schemas/pipeline_plan.schema.json", "examples/pipeline_plan_output.json", False),
    ("schemas/discovery_output.schema.json", "examples/discovery_output.json", False),
    ("schemas/scan_plan.schema.json", "examples/scan_plan_output.json", False),
    ("schemas/triage_output.schema.json", "examples/triage_output.json", False),
    ("schemas/intel_output.schema.json", "examples/intel_output.json", False),
    (
        "schemas/component_registry.schema.json",
        "examples/component_registry_output.json",
        False,
    ),
    (
        "schemas/component_registry_index.schema.json",
        "data/component_registry_index.json",
        False,
    ),
    (
        "schemas/program_registry.schema.json",
        "data/program_registry.json",
        False,
    ),
    ("schemas/findings_db.schema.json", "examples/findings_db_output.json", False),
    (
        "schemas/evidence_registry.schema.json",
        "examples/evidence_registry_output.json",
        False,
    ),
    (
        "schemas/notification_output.schema.json",
        "examples/notification_output.json",
        False,
    ),
    ("schemas/reward.schema.json", "examples/reward_example.json", False),
    ("schemas/restriction.schema.json", "examples/restriction_example.json", False),
    ("schemas/scope.schema.json", "examples/scope_example.json", False),
    ("schemas/program.schema.json", "examples/program_example.json", False),
    (
        "schemas/risk_assessment.schema.json",
        "examples/risk_assessment_example.json",
        False,
    ),
    (
        "schemas/program.schema.json",
        "examples/program_bundles/yeswehack_acme/catalog_entry.json",
        False,
    ),
    (
        "schemas/program.schema.json",
        "examples/program_bundles/huntr_openwidget/catalog_entry.json",
        False,
    ),
    (
        "schemas/ingestion_audit.schema.json",
        "examples/ingestion_audit_example.json",
        False,
    ),
    (
        "schemas/program_registry_diff.schema.json",
        "examples/program_registry_diff.json",
        False,
    ),
    (
        "schemas/program_registry.schema.json",
        "examples/program_registry_output.json",
        False,
    ),
    (
        "schemas/program_scoring_output.schema.json",
        "examples/program_scoring_output.json",
        False,
    ),
    (
        "schemas/case_study_selection.schema.json",
        "examples/case_study_selection_output.json",
        False,
    ),
    (
        "schemas/suggested_approach.schema.json",
        "examples/suggested_approach_output.json",
        False,
    ),
    (
        "schemas/program_relevance_output.schema.json",
        "examples/program_relevance_output.json",
        False,
    ),
    (
        "schemas/program_provenance_output.schema.json",
        "examples/program_provenance_output.json",
        False,
    ),
    (
        "schemas/scoring_calibration.schema.json",
        "examples/scoring_calibration_dataset.json",
        False,
    ),
    (
        "schemas/scoring_calibration_report.schema.json",
        "examples/scoring_calibration_report.json",
        False,
    ),
    (
        "schemas/attachments_manifest.schema.json",
        "examples/outputs/attachments_manifest.json",
        False,
    ),
    (
        "schemas/reproducibility_pack.schema.json",
        "examples/outputs/reproducibility_pack.json",
        False,
    ),
    ("schemas/repro_steps.schema.json", "examples/repro_steps.json", False),
    (
        "schemas/report_completeness_review.schema.json",
        "examples/report_completeness_review_output.json",
        False,
    ),
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
