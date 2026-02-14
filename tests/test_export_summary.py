import unittest

from scripts import export_summary


class ExportSummaryTest(unittest.TestCase):
    def test_build_summary_counts(self):
        findings = [
            {
                "id": "finding-1",
                "title": "Example A",
                "severity": "High",
                "review_required": True,
                "evidence_refs": ["evidence-1"],
                "severity_model": {"category": "LLM01: Prompt Injection"},
            },
            {
                "id": "finding-2",
                "title": "Example B",
                "severity": "Low",
                "review_required": False,
                "evidence_refs": [],
            },
        ]
        summary, items = export_summary.build_summary(findings)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["by_severity"]["high"], 1)
        self.assertEqual(summary["review_required"], 1)
        self.assertEqual(summary["with_evidence"], 1)
        self.assertEqual(items[0]["evidence_count"], 1)
        self.assertEqual(items[0]["category"], "LLM01: Prompt Injection")

    def test_render_markdown_table(self):
        summary, items = export_summary.build_summary(
            [{"id": "finding-1", "title": "Example", "severity": "medium"}]
        )
        markdown = export_summary.render_markdown(summary, items)
        self.assertIn("| ID | Title |", markdown)


if __name__ == "__main__":
    unittest.main()
