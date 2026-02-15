import unittest

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


if __name__ == "__main__":
    unittest.main()
