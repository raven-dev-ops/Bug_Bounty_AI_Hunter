import unittest

import jsonschema

from scripts.lib.io_utils import load_data


SCHEMA_PATH = "schemas/test_case.schema.json"
EXAMPLE_CASES = [
    "examples/test_case_rag_minimal.json",
    "examples/test_case_logging_minimal.json",
    "examples/test_case_embedding_minimal.json",
    "examples/test_case_agents_minimal.json",
]


class TestChecklistExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_data(SCHEMA_PATH)

    def test_examples_validate_against_schema(self):
        for path in EXAMPLE_CASES:
            data = load_data(path)
            jsonschema.validate(data, self.schema)

    def test_examples_include_safe_steps(self):
        for path in EXAMPLE_CASES:
            data = load_data(path)
            self.assertTrue(data.get("steps"), f"{path} missing steps")
            self.assertTrue(data.get("stop_conditions"), f"{path} missing stop conditions")
            self.assertTrue(data.get("expected_results"), f"{path} missing expected results")
            safety_notes = data.get("safety_notes", "")
            self.assertTrue(str(safety_notes).strip(), f"{path} missing safety notes")


if __name__ == "__main__":
    unittest.main()
