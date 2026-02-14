import unittest
from pathlib import Path

from scripts.connectors import get_connector


class ConnectorIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures" / "connectors"

    def _load_program(self, connector_name, handle):
        connector = get_connector(connector_name)
        self.assertIsNotNone(connector)
        programs = connector.list_programs(None, fixtures_dir=self.fixtures_dir)
        program = next(item for item in programs if item.get("handle") == handle)
        return connector.fetch_details(None, program, fixtures_dir=self.fixtures_dir)

    def test_yeswehack_connector(self):
        program = self._load_program("yeswehack", "acme")
        self.assertEqual(program["rewards"]["min"], 500)
        self.assertEqual(program["response_time"]["first_response_hours"], 48)
        self.assertTrue(program["safe_harbor"]["present"])
        in_scope = program["scope"]["in_scope"]
        api_asset = next(item for item in in_scope if item["value"] == "api.acme.com")
        self.assertEqual(api_asset["ports"][0]["start"], 443)
        self.assertIn("No social engineering", program["restrictions"])

    def test_intigriti_connector(self):
        program = self._load_program("intigriti", "nova")
        self.assertEqual(program["rewards"]["currency"], "EUR")
        self.assertEqual(program["response_time"]["resolution_time_hours"], 168)
        self.assertTrue(program["safe_harbor"]["present"])
        self.assertIn("No fuzzing", program["restrictions"])

    def test_huntr_connector(self):
        program = self._load_program("huntr", "openwidget")
        self.assertEqual(program["rewards"]["max"], 1000)
        self.assertEqual(program["response_time"]["resolution_time_hours"], 336)
        self.assertTrue(program["safe_harbor"]["present"])

    def test_bounty_targets_data_connector(self):
        program = self._load_program("bounty-targets-data", "acme-rewards")
        self.assertEqual(program["platform"], "hackerone")
        self.assertEqual(program["rewards"]["min"], 100)
        self.assertIn("No automated scanning", program["restrictions"])
        in_scope = program["scope"]["in_scope"]
        api_asset = next(
            item for item in in_scope if item["value"] == "api.acme.example"
        )
        self.assertEqual(api_asset["ports"][0]["start"], 443)

    def test_disclose_io_connector(self):
        program = self._load_program("disclose-io", "beacon")
        self.assertTrue(program["safe_harbor"]["present"])
        self.assertEqual(program["response_time"]["first_response_hours"], 168)
        self.assertIn("No phishing", program["restrictions"])

    def test_projectdiscovery_connector(self):
        program = self._load_program("projectdiscovery", "orbit-discovery")
        self.assertEqual(program["rewards"]["max"], 1000)
        in_scope = program["scope"]["in_scope"]
        api_asset = next(
            item for item in in_scope if item["value"] == "api.orbit.example"
        )
        self.assertEqual(api_asset["ports"][0]["start"], 443)


if __name__ == "__main__":
    unittest.main()
