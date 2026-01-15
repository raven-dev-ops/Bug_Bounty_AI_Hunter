import unittest

from scripts import migrate


class MigrateTest(unittest.TestCase):
    def test_component_manifest_adds_schema_version(self):
        data = {
            "name": "example-component",
            "version": "0.1.0",
            "capabilities": ["review"],
            "schemas": {"finding": ">=0.1.0"},
        }
        result = migrate.migrate_data(data, "component_manifest", "0.0.0", "0.1.0")
        self.assertEqual(result["schema_version"], "0.1.0")
        self.assertEqual(result["name"], data["name"])

    def test_migrate_rejects_version_mismatch(self):
        data = {
            "schema_version": "0.1.0",
            "name": "example-component",
            "version": "0.1.0",
            "capabilities": ["review"],
            "schemas": {"finding": ">=0.1.0"},
        }
        with self.assertRaises(SystemExit):
            migrate.migrate_data(data, "component_manifest", "0.0.0", "0.1.0")


if __name__ == "__main__":
    unittest.main()
