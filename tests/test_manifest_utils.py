import unittest

from scripts.lib.manifest_utils import validate_manifest


class ManifestUtilsTest(unittest.TestCase):
    def test_validate_manifest_missing_fields(self):
        errors = validate_manifest({"name": "example"})
        self.assertTrue(any("version" in error for error in errors))

    def test_validate_manifest_ok(self):
        manifest = {
            "name": "example",
            "version": "0.1.0",
            "capabilities": ["discovery"],
            "schemas": {"target_profile": ">=0.2.0"},
        }
        errors = validate_manifest(manifest)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
