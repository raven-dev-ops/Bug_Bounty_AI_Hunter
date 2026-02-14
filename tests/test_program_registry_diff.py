import json
import unittest
from pathlib import Path

from scripts import program_registry_diff


class ProgramRegistryDiffTest(unittest.TestCase):
    def test_compute_diff_summary_and_highlights(self):
        before = json.loads(
            Path("examples/program_registry_before.json").read_text(encoding="utf-8")
        )
        after = json.loads(
            Path("examples/program_registry_after.json").read_text(encoding="utf-8")
        )

        diff = program_registry_diff.compute_diff(before, after)
        summary = diff["summary"]

        self.assertEqual(summary["added"], 1)
        self.assertEqual(summary["removed"], 1)
        self.assertEqual(summary["changed"], 1)

        change = diff["changed"][0]
        self.assertIn("rewards", change["highlighted_fields"])
        self.assertIn("scope", change["highlighted_fields"])
        self.assertIn("restrictions", change["highlighted_fields"])

        markdown = program_registry_diff.render_markdown(diff)
        self.assertIn("[highlight] rewards", markdown)


if __name__ == "__main__":
    unittest.main()
