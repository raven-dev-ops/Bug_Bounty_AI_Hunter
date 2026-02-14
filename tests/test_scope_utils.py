import json
import unittest
from pathlib import Path

from scripts.lib.scope_utils import asset_key, normalize_scope_assets


class ScopeUtilsTest(unittest.TestCase):
    def _load_fixture(self, name):
        path = Path(__file__).parent / "fixtures" / name
        return json.loads(path.read_text(encoding="utf-8"))

    def test_normalize_scope_assets_valid_fixture(self):
        assets = self._load_fixture("scope_assets_valid.json")
        normalized, errors = normalize_scope_assets(assets)
        self.assertEqual(errors, [])
        mixed_ports = normalized[1]
        self.assertEqual(mixed_ports["value"], "api.example.com")
        self.assertEqual(
            mixed_ports["ports"],
            [
                {"start": 443, "end": 443},
                {"start": 8000, "end": 8080},
            ],
        )

    def test_normalize_scope_assets_invalid_fixture(self):
        assets = self._load_fixture("scope_assets_invalid.json")
        _, errors = normalize_scope_assets(assets)
        self.assertTrue(errors)
        self.assertTrue(
            any("Nested wildcard" in error for error in errors),
            "Expected nested wildcard validation error.",
        )

    def test_asset_key_includes_ports(self):
        asset_a = {
            "type": "domain",
            "value": "example.com",
            "ports": [{"start": 80, "end": 80}],
        }
        asset_b = {
            "type": "domain",
            "value": "example.com",
            "ports": [{"start": 443, "end": 443}],
        }
        self.assertNotEqual(asset_key(asset_a), asset_key(asset_b))


if __name__ == "__main__":
    unittest.main()
