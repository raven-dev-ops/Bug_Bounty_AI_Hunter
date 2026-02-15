import unittest

from scripts import bugcrowd_board


class TestBugcrowdBoard(unittest.TestCase):
    def test_slug_from_brief_url(self):
        self.assertEqual(
            bugcrowd_board._slug_from_brief_url("/engagements/moovit-mbb-og"),
            "moovit-mbb-og",
        )
        self.assertEqual(
            bugcrowd_board._slug_from_brief_url("https://bugcrowd.com/engagements/x"),
            "x",
        )
        self.assertEqual(bugcrowd_board._slug_from_brief_url(""), "")

    def test_engagement_markdown_is_ascii(self):
        engagement = {
            "name": "Pokemon Go Test",
            "briefUrl": "/engagements/moovit-mbb-og",
            "tagline": "Test engagement",
            "industryName": "Software",
            "accessStatus": "public",
            "isPrivate": False,
            "serviceLevel": "standard",
            "scopeRank": 3,
            "rewardSummary": {"summary": "$100-$500"},
            "logoUrl": "https://example.invalid/logo.png",
        }
        stats = {
            "rewardedVulnerabilities": 12,
            "validationWithin": "24h",
            "averagePayout": "$250",
            "validSubmissionCount": 34,
        }
        md = bugcrowd_board._mk_engagement_markdown(
            engagement=engagement,
            listing_url="https://bugcrowd.com/engagements?page=1",
            fetched_at="2026-02-15T00:00:00+00:00",
            stats=stats,
            community=None,
        )
        self.assertTrue(md.startswith("# "))
        self.assertIn("## Overview", md)
        self.assertIn("Hacker Portal brief URL", md)
        self.assertTrue(all(ord(ch) < 128 for ch in md))

    def test_index_markdown_includes_table(self):
        rows = [
            {
                "rel_path": "moovit-mbb-og.md",
                "name": "Moovit",
                "reward": "$100-$500",
                "access": "public",
                "private": "false",
                "industry": "Software",
                "service": "standard",
                "scope_rank": "3",
                "validation": "24h",
            }
        ]
        md = bugcrowd_board._mk_index_markdown(
            rows=rows,
            listing_url="https://bugcrowd.com/engagements?page=1",
            fetched_at="2026-02-15T00:00:00+00:00",
            pages_fetched=1,
        )
        self.assertIn("| Engagement | Reward | Access |", md)
        self.assertIn("| [Moovit](moovit-mbb-og.md) |", md)


if __name__ == "__main__":
    unittest.main()
