import unittest

from scripts.lib import catalog_parsers


class CatalogParsersTest(unittest.TestCase):
    def test_parse_reward_range_empty(self):
        self.assertEqual(catalog_parsers.parse_reward_range(None), {})

    def test_parse_reward_range_basic_range(self):
        reward = catalog_parsers.parse_reward_range("USD 500 - 1500")
        self.assertEqual(reward["currency"], "USD")
        self.assertEqual(reward["min"], 500)
        self.assertEqual(reward["max"], 1500)

    def test_parse_reward_range_up_to(self):
        reward = catalog_parsers.parse_reward_range("Up to $5,000 for criticals")
        self.assertEqual(reward["currency"], "USD")
        self.assertEqual(reward["min"], 0)
        self.assertEqual(reward["max"], 5000)

    def test_parse_reward_range_no_bounty(self):
        reward = catalog_parsers.parse_reward_range("No bounty offered")
        self.assertEqual(reward["summary"], "No bounty offered")
        self.assertNotIn("min", reward)
        self.assertNotIn("max", reward)

    def test_parse_response_time_first_and_resolution(self):
        text = "First response within 2 days. Resolution in 5 hours."
        response = catalog_parsers.parse_response_time(text)
        self.assertEqual(response["first_response_hours"], 48)
        self.assertEqual(response["resolution_time_hours"], 5)
        self.assertEqual(response["notes"], text)

    def test_parse_response_time_no_match(self):
        self.assertEqual(
            catalog_parsers.parse_response_time("Response time varies."), {}
        )

    def test_extract_restrictions_from_text(self):
        text = "- No scanning\n- No social engineering\n"
        restrictions = catalog_parsers.extract_restrictions(text)
        self.assertEqual(restrictions, ["No scanning", "No social engineering"])

    def test_parse_safe_harbor_present(self):
        safe_harbor = catalog_parsers.parse_safe_harbor("Safe harbor applies.")
        self.assertTrue(safe_harbor["present"])

    def test_parse_safe_harbor_absent(self):
        safe_harbor = catalog_parsers.parse_safe_harbor("No safe harbor is provided.")
        self.assertFalse(safe_harbor["present"])

    def test_classify_feasibility_blocked(self):
        result = catalog_parsers.classify_feasibility("Do not test production.", {})
        self.assertEqual(result["feasibility"], "blocked")

    def test_classify_feasibility_limited_restriction(self):
        result = catalog_parsers.classify_feasibility("No scanning or fuzzing.", {})
        self.assertEqual(result["feasibility"], "limited")
        self.assertEqual(result["notes"], "Automation constraints apply.")

    def test_classify_feasibility_limited_safe_harbor(self):
        result = catalog_parsers.classify_feasibility([], {"present": False})
        self.assertEqual(result["feasibility"], "limited")
        self.assertEqual(result["notes"], "Safe harbor absent.")

    def test_classify_feasibility_ok(self):
        result = catalog_parsers.classify_feasibility([], {"present": True})
        self.assertEqual(result["feasibility"], "ok")


if __name__ == "__main__":
    unittest.main()
