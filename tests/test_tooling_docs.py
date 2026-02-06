import unittest
from pathlib import Path


class TestToolingDocs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]

    def test_tools_doc_referenced(self):
        tools_path = "docs/TOOLS.md"
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        index = (self.root / "docs/index.md").read_text(encoding="utf-8")
        mkdocs = (self.root / "mkdocs.yml").read_text(encoding="utf-8")

        self.assertIn(tools_path, readme)
        self.assertIn(tools_path.split("/", 1)[1], index)
        self.assertIn("TOOLS.md", mkdocs)

    def test_tools_table_entries(self):
        tools_doc = (self.root / "docs/TOOLS.md").read_text(encoding="utf-8")
        rows = []
        for line in tools_doc.splitlines():
            if not line.startswith("|"):
                continue
            if line.strip().startswith("| ---"):
                continue
            if "Tool" in line and "Project use" in line:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            rows.append(cells)

        tool_names = [row[0] for row in rows]
        self.assertGreaterEqual(len(tool_names), 10)
        self.assertEqual(len(tool_names), len(set(tool_names)))
        for name in tool_names:
            self.assertTrue(name)


if __name__ == "__main__":
    unittest.main()
