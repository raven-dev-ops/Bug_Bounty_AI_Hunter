import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from lib.template_utils import render_template


class TemplateUtilsTest(unittest.TestCase):
    def test_render_template_missing_key(self):
        template = "Hello {name} {missing}"
        rendered = render_template(template, {"name": "World"})
        self.assertEqual(rendered, "Hello World {missing}")


if __name__ == "__main__":
    unittest.main()
