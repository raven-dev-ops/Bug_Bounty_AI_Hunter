import argparse
import subprocess
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data


STAGE_SCRIPTS = {
    "scope_import": "scripts/import_scope.py",
    "discovery": "scripts/discovery_assets.py",
    "scan": "scripts/scan_templates.py",
    "triage": "scripts/triage_findings.py",
    "notify": "scripts/notify.py",
    "intel": "scripts/external_intel.py",
    "component_registry": "scripts/component_runtime.py",
    "report_bundle": "scripts/report_bundle.py",
    "issue_drafts": "scripts/export_issue_drafts.py",
    "finding_reports": "scripts/export_finding_reports.py",
    "jira_export": "scripts/export_jira.py",
    "pdf_export": "scripts/export_pdf.py",
}


def _config_to_args(config):
    args = []
    for key, value in config.items():
        flag = "--" + key.replace("_", "-")
        if isinstance(value, bool):
            if value:
                args.append(flag)
        elif isinstance(value, list):
            args.extend([flag, ",".join(str(item) for item in value)])
        else:
            args.extend([flag, str(value)])
    return args


def build_command(stage):
    name = stage.get("name")
    config = stage.get("config", {})
    if name not in STAGE_SCRIPTS:
        raise SystemExit(f"Unknown stage: {name}")
    script_path = REPO_ROOT / STAGE_SCRIPTS[name]
    cmd = [sys.executable, str(script_path)]
    cmd.extend(_config_to_args(config))
    return cmd


def main():
    parser = argparse.ArgumentParser(description="Orchestrate pipeline stages.")
    parser.add_argument("--config", required=True, help="Pipeline config path.")
    parser.add_argument(
        "--mode",
        default="plan",
        choices=["plan", "run"],
        help="Plan or run the pipeline.",
    )
    parser.add_argument("--output", help="Plan output JSON/YAML path.")
    args = parser.parse_args()

    config = load_data(args.config)
    stages = config.get("stages", [])
    if not stages:
        raise SystemExit("No stages found in pipeline config.")

    plan = []
    for stage in stages:
        cmd = build_command(stage)
        plan.append(
            {
                "stage": stage.get("name"),
                "argv": cmd,
            }
        )

    if args.mode == "plan":
        output = {"schema_version": "0.1.0", "plan": plan}
        if args.output:
            dump_data(args.output, output)
        else:
            dump_data("output/pipeline_plan.json", output)
        return

    for stage in stages:
        cmd = build_command(stage)
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
