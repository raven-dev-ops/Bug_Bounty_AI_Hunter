import unittest

from scripts import bugcrowd_full_postprocess


class TestBugcrowdFullPostprocess(unittest.TestCase):
    def test_extract_brief_doc(self):
        md = (
            "# test\n\n"
            "## Brief Version Document\n"
            "```json\n"
            '{"data":{"brief":{"name":"Test"}}}\n'
            "```\n"
        )
        doc = bugcrowd_full_postprocess._extract_brief_doc(md)
        self.assertIsInstance(doc, dict)
        self.assertEqual(doc["data"]["brief"]["name"], "Test")

    def test_insert_rendered_sections(self):
        md = "## Overview\n- x\n\n## API Endpoints (From Page)\n- y\n"
        rendered = "## Brief (Rendered)\n\n- Program: Test\n"
        new_text, changed = bugcrowd_full_postprocess._insert_rendered_sections(
            md, rendered
        )
        self.assertTrue(changed)
        self.assertIn("## Brief (Rendered)", new_text)
        self.assertLess(
            new_text.index("## Brief (Rendered)"),
            new_text.index("## API Endpoints (From Page)"),
        )


if __name__ == "__main__":
    unittest.main()
