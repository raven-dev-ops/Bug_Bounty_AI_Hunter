import json
from pathlib import Path
import tempfile
import unittest

from scripts import component_runtime


class ComponentRuntimeTest(unittest.TestCase):
    def test_parse_csv(self):
        self.assertEqual(component_runtime._parse_csv(None), set())
        self.assertEqual(
            component_runtime._parse_csv("alpha, beta"),
            {"alpha", "beta"},
        )
        self.assertEqual(
            component_runtime._parse_csv(["gamma", "delta"]),
            {"gamma", "delta"},
        )

    def test_resolve_enabled_cli_overrides_config(self):
        config = {"enabled": "alpha"}
        enable_set = {"beta"}
        disable_set = set()
        self.assertFalse(
            component_runtime._resolve_enabled("alpha", config, enable_set, disable_set)
        )
        self.assertTrue(
            component_runtime._resolve_enabled("beta", config, enable_set, disable_set)
        )

    def test_load_manifest_respects_config_disable(self):
        manifest = {
            "schema_version": "0.1.0",
            "name": "sample",
            "version": "0.1.0",
            "capabilities": ["discovery"],
            "schemas": {"target_profile": ">=0.2.0"},
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "component_manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            record = component_runtime._load_manifest(
                path,
                schema=None,
                config={"disabled": "sample"},
                enable_set=set(),
                disable_set=set(),
            )
            self.assertEqual(record["enabled"], False)
            self.assertEqual(record["errors"], [])
            self.assertEqual(record["manifest"]["name"], "sample")


if __name__ == "__main__":
    unittest.main()
