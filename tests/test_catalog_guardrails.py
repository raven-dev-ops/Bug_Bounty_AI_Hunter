import unittest

from scripts.lib.catalog_guardrails import ensure_catalog_path


class CatalogGuardrailsTest(unittest.TestCase):
    def test_allows_data_path(self):
        ensure_catalog_path("data/program_registry.json")

    def test_blocks_output_path(self):
        with self.assertRaises(SystemExit):
            ensure_catalog_path("output/program_registry.json")

    def test_blocks_evidence_path(self):
        with self.assertRaises(SystemExit):
            ensure_catalog_path("evidence/ingestion_audit.json")


if __name__ == "__main__":
    unittest.main()
