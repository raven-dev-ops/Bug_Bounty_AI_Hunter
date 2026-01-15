from pathlib import Path
import tempfile
import unittest

from scripts.lib.io_utils import load_data


class IoUtilsTest(unittest.TestCase):
    def test_load_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.json"
            path.write_text("{\"name\": \"example\"}", encoding="utf-8")
            data = load_data(path)
            self.assertEqual(data["name"], "example")

    def test_load_yaml(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed")

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.yaml"
            path.write_text("name: example\n", encoding="utf-8")
            data = load_data(path)
            self.assertEqual(data["name"], "example")


if __name__ == "__main__":
    unittest.main()
