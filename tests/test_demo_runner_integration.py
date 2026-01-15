import subprocess
import tempfile
import unittest
from pathlib import Path

import jsonschema

from scripts.lib.io_utils import load_data


REPO_ROOT = Path(__file__).resolve().parents[1]


class DemoRunnerIntegrationTest(unittest.TestCase):
    def test_demo_runner_plan_outputs_validate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "demo"
            cmd = [
                "python",
                "-m",
                "scripts.demo_runner",
                "--mode",
                "plan",
                "--output-dir",
                str(output_dir),
            ]
            subprocess.run(cmd, check=True, cwd=REPO_ROOT)

            plan_path = output_dir / "pipeline_plan.json"
            config_path = output_dir / "pipeline_config.demo.yaml"
            self.assertTrue(plan_path.exists())
            self.assertTrue(config_path.exists())

            schema = load_data(REPO_ROOT / "schemas" / "pipeline_plan.schema.json")
            data = load_data(plan_path)
            jsonschema.validate(data, schema)

    def test_bbhai_plan_smoke(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd = [
                "python",
                "-m",
                "bbhai",
                "plan",
                "--config",
                str(REPO_ROOT / "examples" / "pipeline_config.yaml"),
                "--output-dir",
                temp_dir,
            ]
            subprocess.run(cmd, check=True, cwd=REPO_ROOT)
            plan_path = Path(temp_dir) / "pipeline_plan.json"
            self.assertTrue(plan_path.exists())


if __name__ == "__main__":
    unittest.main()
