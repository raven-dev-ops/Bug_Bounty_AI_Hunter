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
    ("schemas/component_manifest.schema.json", "examples/component_manifest.yaml", False),
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
