from __future__ import annotations

from pathlib import Path

from scripts import init_engagement_workspace
from scripts.lib.io_utils import dump_data


DEFAULT_WORKSPACE_ROOT = Path("output/engagements")
DEFAULT_TEMPLATE_DIR = Path("templates/engagement_workspace/skeleton")


def _pipeline_config_template(workspace_dir: Path) -> dict[str, object]:
    reports_root = workspace_dir / "reports"
    bundle_dir = reports_root / "report_bundle"
    issue_drafts_dir = reports_root / "issue_drafts"
    return {
        "schema_version": "0.1.0",
        "limits": {
            "request_budget": 200,
            "token_budget": 8000,
            "max_concurrency": 3,
            "min_delay_seconds": 0.2,
            "stage_timeout_seconds": 300,
        },
        "stages": [
            {
                "name": "report_bundle",
                "config": {
                    "findings": "examples/outputs/findings.json",
                    "target_profile": "examples/target_profile_minimal.yaml",
                    "evidence": "examples/evidence_example.json",
                    "output_dir": bundle_dir.as_posix(),
                    "repro_steps": "examples/repro_steps.json",
                },
            },
            {
                "name": "issue_drafts",
                "config": {
                    "findings": (bundle_dir / "findings.json").as_posix(),
                    "target_profile": "examples/target_profile_minimal.yaml",
                    "output_dir": issue_drafts_dir.as_posix(),
                    "platform": "github",
                },
            },
            {
                "name": "summary_export",
                "config": {
                    "findings": (bundle_dir / "findings.json").as_posix(),
                    "output_dir": (reports_root / "summary").as_posix(),
                },
            },
        ],
    }


def scaffold_workspace_files(
    *,
    platform: str,
    slug: str,
    engagement_url: str,
    out_root: Path | str | None = None,
    force: bool = False,
) -> dict[str, str]:
    workspace_root = Path(out_root) if out_root else DEFAULT_WORKSPACE_ROOT
    plan = init_engagement_workspace.plan_workspace(
        platform=platform,
        slug=slug,
        engagement_url=engagement_url,
        out_root=workspace_root,
        template_dir=DEFAULT_TEMPLATE_DIR,
    )
    workspace_dir = init_engagement_workspace.create_workspace(plan, force=force)

    reports_dir = workspace_dir / "reports"
    logs_dir = workspace_dir / "logs"
    artifacts_dir = workspace_dir / "artifacts"
    for directory in (reports_dir, logs_dir, artifacts_dir):
        directory.mkdir(parents=True, exist_ok=True)

    roe_ack_path = workspace_dir / "ROE_ACK.yaml"
    if force or not roe_ack_path.exists():
        dump_data(
            roe_ack_path,
            {
                "acknowledged_at": "",
                "acknowledged_by": "",
                "authorized_target": "",
                "notes": "Fill this before run mode. See docs/ROE.md.",
            },
        )

    pipeline_config_path = workspace_dir / "pipeline_config.yaml"
    if force or not pipeline_config_path.exists():
        dump_data(pipeline_config_path, _pipeline_config_template(workspace_dir))

    return {
        "root_dir": workspace_dir.as_posix(),
        "roe_ack_path": roe_ack_path.as_posix(),
        "pipeline_config_path": pipeline_config_path.as_posix(),
        "reports_dir": reports_dir.as_posix(),
        "logs_dir": logs_dir.as_posix(),
        "artifacts_dir": artifacts_dir.as_posix(),
    }


def write_roe_ack_file(
    *,
    workspace_dir: Path | str,
    acknowledged_at: str,
    acknowledged_by: str,
    authorized_target: str,
) -> str:
    workspace_dir = Path(workspace_dir)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    ack_path = workspace_dir / "ROE_ACK.yaml"
    dump_data(
        ack_path,
        {
            "acknowledged_at": acknowledged_at,
            "acknowledged_by": acknowledged_by,
            "authorized_target": authorized_target,
        },
    )
    return ack_path.as_posix()
