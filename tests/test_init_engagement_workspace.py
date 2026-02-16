import tempfile
import unittest
from pathlib import Path

from scripts import init_engagement_workspace


class TestInitEngagementWorkspace(unittest.TestCase):
    def test_create_workspace_renders_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            template_dir = root / "template"
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "RECON_LOG.md").write_text(
                "{{platform}}/{{slug}} {{engagement_url}} {{created_at_utc}}\n",
                encoding="utf-8",
                newline="\n",
            )

            out_root = root / "out"
            plan = init_engagement_workspace.plan_workspace(
                platform="bugcrowd",
                slug="demo",
                engagement_url="https://example.com/engagements/demo",
                out_root=out_root,
                template_dir=template_dir,
            )
            out_dir = init_engagement_workspace.create_workspace(plan)

            self.assertTrue((out_dir / "RECON_LOG.md").exists())
            content = (out_dir / "RECON_LOG.md").read_text(encoding="utf-8")
            self.assertIn("bugcrowd/demo", content)
            self.assertIn("https://example.com/engagements/demo", content)
            self.assertNotIn("{{platform}}", content)
            self.assertNotIn("{{slug}}", content)
            self.assertNotIn("{{created_at_utc}}", content)

    def test_destination_requires_force_when_not_empty(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            template_dir = root / "template"
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "RECON_LOG.md").write_text("ok\n", encoding="utf-8")

            out_root = root / "out"
            plan = init_engagement_workspace.plan_workspace(
                platform="bugcrowd",
                slug="demo",
                engagement_url="",
                out_root=out_root,
                template_dir=template_dir,
            )
            init_engagement_workspace.create_workspace(plan, force=False)

            # Create an extra file so the destination is non-empty.
            (plan.output_dir / "extra.txt").write_text("x\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                init_engagement_workspace.create_workspace(plan, force=False)


if __name__ == "__main__":
    unittest.main()
