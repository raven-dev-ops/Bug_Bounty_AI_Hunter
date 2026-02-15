import tempfile
import unittest
from pathlib import Path

from scripts import bugcrowd_briefs


class TestBugcrowdBriefs(unittest.TestCase):
    def test_extract_brief_root_accepts_double_quoted_id(self):
        html_text = (
            "<html><body>"
            '<div id="researcher-engagement-brief-root" '
            "data-api-endpoints='{&quot;engagementBriefApi&quot;:{&quot;getBriefVersionDocument&quot;:&quot;/engagements/test/changelog/abc&quot;}}' "
            "data-props='{&quot;engagement&quot;:{&quot;name&quot;:&quot;Test Engagement&quot;}}'>"
            "</div>"
            "</body></html>"
        )
        root = bugcrowd_briefs._extract_brief_root(html_text)
        self.assertIsInstance(root, dict)
        self.assertEqual(
            root["api"]["engagementBriefApi"]["getBriefVersionDocument"],
            "/engagements/test/changelog/abc",
        )
        self.assertEqual(root["props"]["engagement"]["name"], "Test Engagement")

    def test_extract_brief_root_returns_none_when_missing(self):
        self.assertIsNone(bugcrowd_briefs._extract_brief_root("<html></html>"))

    def test_replace_path_params(self):
        self.assertEqual(
            bugcrowd_briefs._replace_path_params(
                "/api/:id/items/:name", {"id": 1, "name": "x"}
            ),
            "/api/1/items/x",
        )
        with self.assertRaises(KeyError):
            bugcrowd_briefs._replace_path_params("/api/:id/items/:missing", {"id": 1})

    def test_backup_codes_file_parsing_and_consumption(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "BUGCROWD_backup_codes"
            with path.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write("# comment\n")
                handle.write("\n")
                handle.write("code1\n")
                handle.write("code2, code3  code4\n")
                handle.write("code1 # dup\n")

            codes = bugcrowd_briefs._read_backup_codes_file(path)
            self.assertEqual(codes, ["code1", "code2", "code3", "code4"])

            consumed = bugcrowd_briefs._consume_backup_code_file(path, codes, "code2")
            self.assertTrue(consumed)
            self.assertEqual(
                bugcrowd_briefs._read_backup_codes_file(path),
                ["code1", "code3", "code4"],
            )

    def test_backup_codes_file_strips_utf8_bom(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "BUGCROWD_backup_codes"
            path.write_bytes(b"\xef\xbb\xbf# comment\ncode1\n")
            self.assertEqual(bugcrowd_briefs._read_backup_codes_file(path), ["code1"])


if __name__ == "__main__":
    unittest.main()
