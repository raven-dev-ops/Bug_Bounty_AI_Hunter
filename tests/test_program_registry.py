import json
import unittest
from pathlib import Path

from scripts import program_registry


class ProgramRegistryTest(unittest.TestCase):
    def _load_fixture(self, name):
        path = Path(__file__).parent / "fixtures" / name
        return json.loads(path.read_text(encoding="utf-8"))

    def test_merge_sources_is_deterministic_with_conflicts(self):
        sources = self._load_fixture("program_registry_sources.json")
        merged = program_registry.merge_sources(sources)

        self.assertEqual(len(merged), 2)
        example = next(item for item in merged if item["name"] == "Example Program")

        self.assertEqual(example["rewards"]["min"], 200)
        self.assertEqual(example["safe_harbor"], "Written authorization on file.")
        self.assertIn("No denial of service", example["restrictions"])
        self.assertIn("No social engineering", example["restrictions"])
        self.assertEqual(len(example["sources"]), 2)
        self.assertTrue(example.get("attribution"))
        self.assertEqual(example["attribution"][0]["license"], "Public listing terms")
        self.assertEqual(example["sources"][0]["parser_version"], "0.1.0")

        conflict_fields = {conflict["field"] for conflict in example["conflicts"]}
        self.assertIn("rewards", conflict_fields)
        self.assertIn("scope", conflict_fields)
        self.assertIn("safe_harbor", conflict_fields)

        reversed_merge = program_registry.merge_sources(list(reversed(sources)))
        self.assertEqual(merged, reversed_merge)


if __name__ == "__main__":
    unittest.main()
