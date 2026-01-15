import unittest

from scripts.lib.template_utils import render_template


class TemplateUtilsTest(unittest.TestCase):
    def test_render_template_missing_key(self):
        template = "Hello {name} {missing}"
        rendered = render_template(template, {"name": "World"})
        self.assertEqual(rendered, "Hello World {missing}")


if __name__ == "__main__":
    unittest.main()
