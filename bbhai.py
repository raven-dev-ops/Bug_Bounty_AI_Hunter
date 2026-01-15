import argparse
import runpy
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
EXAMPLES_DIR = REPO_ROOT / "examples"


def _format_extension(value):
    return "yaml" if value == "yaml" else "json"


def _run_module(module, args, dry_run):
    cmd = [sys.executable, "-m", module] + args
    if dry_run:
        print(" ".join(cmd))
        return
    original_argv = sys.argv[:]
    try:
        sys.argv = [module] + args
        runpy.run_module(module, run_name="__main__")
    finally:
        sys.argv = original_argv


def _default_input(path_candidates):
    for candidate in path_candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def _ensure_path(path, strict):
    if strict and Path(path).exists():
        raise SystemExit(f"Output already exists: {path}")


def _ensure_dir(path, strict):
    path = Path(path)
    if strict and path.exists() and any(path.iterdir()):
        raise SystemExit(f"Output directory is not empty: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _copy_file(src, dest, force, dry_run):
    src = Path(src)
    dest = Path(dest)
    if dest.exists() and not force:
        return
    if dry_run:
        print(f"copy {src} -> {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)


def _write_file(path, content, force, dry_run):
    path = Path(path)
    if path.exists() and not force:
        return
    if dry_run:
        print(f"write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def init_workspace(args, workspace, output_root):
    if args.dry_run:
        print(f"init workspace: {workspace}")
    _ensure_dir(workspace, args.strict)
    _ensure_dir(output_root / "report_bundle", args.strict)
    _ensure_dir(output_root / "issue_drafts", args.strict)
    _ensure_dir(output_root / "demo", args.strict)

    _copy_file(
        EXAMPLES_DIR / "pipeline_config.yaml",
        workspace / "pipeline_config.yaml",
        args.force,
        args.dry_run,
    )
    _copy_file(
        EXAMPLES_DIR / "target_profile_questionnaire.yaml",
        workspace / "target_profile_questionnaire.yaml",
        args.force,
        args.dry_run,
    )

    roe_ack = (
        "acknowledged_at:\n"
        "acknowledged_by:\n"
        "authorized_target:\n"
        "notes: Populate before running in run mode.\n"
    )
    _write_file(workspace / "ROE_ACK.yaml", roe_ack, args.force, args.dry_run)


def profile_command(args, workspace, output_root):
    output_path = args.output
    if not output_path:
        output_path = output_root / f"target_profile.{_format_extension(args.format)}"
    input_path = args.input or _default_input(
        [
            workspace / "target_profile_questionnaire.yaml",
            EXAMPLES_DIR / "target_profile_questionnaire.yaml",
        ]
    )
    if not input_path:
        raise SystemExit("Questionnaire input not found.")
    _ensure_path(output_path, args.strict)
    module_args = ["--input", str(input_path), "--output", str(output_path)]
    if args.schema_version:
        module_args.extend(["--schema-version", args.schema_version])
    if args.name:
        module_args.extend(["--name", args.name])
    if args.profile_id:
        module_args.extend(["--id", args.profile_id])
    _run_module("scripts.target_profile_generate", module_args, args.dry_run)


def model_command(args, workspace, output_root):
    format_ext = _format_extension(args.format)
    target_profile = args.target_profile or _default_input(
        [
            output_root / f"target_profile.{format_ext}",
            output_root / "target_profile.json",
            output_root / "target_profile.yaml",
            workspace / "target_profile.json",
            workspace / "target_profile.yaml",
        ]
    )
    if not target_profile:
        raise SystemExit("TargetProfile not found.")

    dataflow_output = args.dataflow_output or (
        output_root / f"dataflow_map.{format_ext}"
    )
    threat_output = args.threat_output or (
        output_root / f"threat_model.{format_ext}"
    )

    _ensure_path(dataflow_output, args.strict)
    _ensure_path(threat_output, args.strict)

    _run_module(
        "scripts.dataflow_map",
        ["--target-profile", str(target_profile), "--output", str(dataflow_output)],
        args.dry_run,
    )
    _run_module(
        "scripts.threat_model_generate",
        ["--target-profile", str(target_profile), "--output", str(threat_output)],
        args.dry_run,
    )


def pipeline_command(args, workspace, output_root, mode):
    config_path = args.config or _default_input(
        [workspace / "pipeline_config.yaml", EXAMPLES_DIR / "pipeline_config.yaml"]
    )
    if not config_path:
        raise SystemExit("Pipeline config not found.")

    module_args = ["--config", str(config_path), "--mode", mode]
    if mode == "plan":
        plan_output = args.plan_output or (
            output_root / f"pipeline_plan.{_format_extension(args.format)}"
        )
        _ensure_path(plan_output, args.strict)
        module_args.extend(["--output", str(plan_output)])
    else:
        if args.ack_authorization:
            module_args.append("--ack-authorization")
        else:
            roe_ack = args.roe_ack or (workspace / "ROE_ACK.yaml")
            module_args.extend(["--roe-ack", str(roe_ack)])
    _run_module("scripts.pipeline_orchestrator", module_args, args.dry_run)


def report_command(args, workspace, output_root):
    findings = args.findings or _default_input(
        [EXAMPLES_DIR / "outputs" / "findings.json"]
    )
    if not findings:
        raise SystemExit("Findings input not found.")

    target_profile = args.target_profile or _default_input(
        [
            output_root / f"target_profile.{_format_extension(args.format)}",
            output_root / "target_profile.json",
            output_root / "target_profile.yaml",
            workspace / "target_profile.json",
            workspace / "target_profile.yaml",
        ]
    )

    report_dir = Path(args.report_dir or output_root / "report_bundle")
    issue_dir = Path(args.issue_dir or output_root / "issue_drafts")
    _ensure_dir(report_dir, args.strict)
    _ensure_dir(issue_dir, args.strict)

    report_args = ["--findings", str(findings), "--output-dir", str(report_dir)]
    if target_profile:
        report_args.extend(["--target-profile", str(target_profile)])
    if args.evidence:
        report_args.extend(["--evidence", str(args.evidence)])
    if args.repro_steps:
        report_args.extend(["--repro-steps", str(args.repro_steps)])
    _run_module("scripts.report_bundle", report_args, args.dry_run)

    attachments_manifest = args.attachments_manifest
    if not attachments_manifest:
        default_manifest = report_dir / "attachments_manifest.json"
        if default_manifest.exists():
            attachments_manifest = default_manifest

    issue_args = [
        "--findings",
        str(findings),
        "--output-dir",
        str(issue_dir),
        "--platform",
        args.platform,
    ]
    if target_profile:
        issue_args.extend(["--target-profile", str(target_profile)])
    if attachments_manifest:
        issue_args.extend(["--attachments-manifest", str(attachments_manifest)])
    _run_module("scripts.export_issue_drafts", issue_args, args.dry_run)


def migrate_command(args):
    module_args = [
        "--input",
        args.input,
        "--from",
        args.from_version,
        "--to",
        args.to_version,
        "--artifact",
        args.artifact,
    ]
    if args.output:
        module_args.extend(["--output", args.output])
    if args.in_place:
        module_args.append("--in-place")
    if args.dry_run:
        module_args.append("--dry-run")
    _run_module("scripts.migrate", module_args, False)


def build_parser():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--workspace", default="output")
    common_parser.add_argument("--output-dir", dest="output_dir")
    common_parser.add_argument("--config")
    common_parser.add_argument("--format", choices=["json", "yaml"], default="json")
    common_parser.add_argument("--strict", action="store_true")
    common_parser.add_argument("--dry-run", action="store_true")
    common_parser.add_argument(
        "--ack-authorization",
        action="store_true",
        help="Acknowledge authorization before running.",
    )
    common_parser.add_argument(
        "--roe-ack",
        help="ROE acknowledgement YAML/JSON path.",
    )

    parser = argparse.ArgumentParser(
        description="Unified CLI for Bug_Bounty_Hunter_AI workflows."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Scaffold a workspace.", parents=[common_parser]
    )
    init_parser.add_argument("--force", action="store_true")

    profile_parser = subparsers.add_parser(
        "profile", help="Generate TargetProfile.", parents=[common_parser]
    )
    profile_parser.add_argument("--input")
    profile_parser.add_argument("--output")
    profile_parser.add_argument("--schema-version")
    profile_parser.add_argument("--name")
    profile_parser.add_argument("--id", dest="profile_id")

    model_parser = subparsers.add_parser(
        "model",
        help="Generate dataflow map and threat model.",
        parents=[common_parser],
    )
    model_parser.add_argument("--target-profile")
    model_parser.add_argument("--dataflow-output")
    model_parser.add_argument("--threat-output")

    plan_parser = subparsers.add_parser(
        "plan", help="Plan the pipeline.", parents=[common_parser]
    )
    plan_parser.add_argument("--plan-output")

    run_parser = subparsers.add_parser(
        "run", help="Run the pipeline.", parents=[common_parser]
    )

    report_parser = subparsers.add_parser(
        "report", help="Generate reports.", parents=[common_parser]
    )
    report_parser.add_argument("--findings")
    report_parser.add_argument("--target-profile")
    report_parser.add_argument("--evidence")
    report_parser.add_argument("--report-dir")
    report_parser.add_argument("--issue-dir")
    report_parser.add_argument("--repro-steps")
    report_parser.add_argument("--attachments-manifest")
    report_parser.add_argument(
        "--platform",
        default="github",
        choices=["github", "hackerone", "bugcrowd"],
    )

    migrate_parser = subparsers.add_parser(
        "migrate", help="Migrate artifacts between schema versions.", parents=[common_parser]
    )
    migrate_parser.add_argument("--input", required=True)
    migrate_parser.add_argument("--output")
    migrate_parser.add_argument("--in-place", action="store_true")
    migrate_parser.add_argument(
        "--artifact",
        default="auto",
        choices=["auto", "component_manifest"],
    )
    migrate_parser.add_argument("--from", dest="from_version", required=True)
    migrate_parser.add_argument("--to", dest="to_version", required=True)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    workspace = Path(args.workspace)
    output_root = Path(args.output_dir) if args.output_dir else workspace

    if args.command == "init":
        init_workspace(args, workspace, output_root)
    elif args.command == "profile":
        profile_command(args, workspace, output_root)
    elif args.command == "model":
        model_command(args, workspace, output_root)
    elif args.command == "plan":
        pipeline_command(args, workspace, output_root, "plan")
    elif args.command == "run":
        pipeline_command(args, workspace, output_root, "run")
    elif args.command == "report":
        report_command(args, workspace, output_root)
    elif args.command == "migrate":
        migrate_command(args)


if __name__ == "__main__":
    main()
