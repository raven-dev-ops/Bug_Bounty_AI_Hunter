import argparse
import subprocess
import sys
from pathlib import Path

from .lib.io_utils import dump_data, load_data


STAGE_MODULES = {
    "scope_import": "scripts.import_scope",
    "discovery": "scripts.discovery_assets",
    "dataflow_map": "scripts.dataflow_map",
    "threat_model": "scripts.threat_model_generate",
    "scan": "scripts.scan_templates",
    "triage": "scripts.triage_findings",
    "notify": "scripts.notify",
    "intel": "scripts.external_intel",
    "component_registry": "scripts.component_runtime",
    "report_bundle": "scripts.report_bundle",
    "issue_drafts": "scripts.export_issue_drafts",
    "finding_reports": "scripts.export_finding_reports",
    "jira_export": "scripts.export_jira",
    "pdf_export": "scripts.export_pdf",
}

ORCHESTRATOR_ONLY_KEYS = {"estimated_requests", "estimated_tokens"}
LIMITED_STAGE_KEYS = {
    "scan": {"max_concurrency", "min_delay_seconds"},
    "intel": {"timeout_seconds"},
}


def _config_to_args(config):
    args = []
    for key, value in config.items():
        if key in ORCHESTRATOR_ONLY_KEYS:
            continue
        flag = "--" + key.replace("_", "-")
        if isinstance(value, bool):
            if value:
                args.append(flag)
        elif isinstance(value, list):
            args.extend([flag, ",".join(str(item) for item in value)])
        else:
            args.extend([flag, str(value)])
    return args


def _apply_limits(stage, limits):
    if not isinstance(limits, dict):
        return stage
    config = stage.get("config", {}) or {}
    stage_name = stage.get("name")
    limit_keys = LIMITED_STAGE_KEYS.get(stage_name, set())

    for key in limit_keys:
        limit_value = limits.get(key)
        if limit_value is None:
            continue
        value = config.get(key)
        if value is None:
            config[key] = limit_value
            continue
        try:
            value_num = float(value)
            limit_num = float(limit_value)
        except (TypeError, ValueError):
            raise SystemExit(f"Invalid numeric limit for {key}.")
        if key == "min_delay_seconds":
            if value_num < limit_num:
                raise SystemExit(
                    f"{key} {value} is below the configured limit {limit_value}."
                )
        else:
            if value_num > limit_num:
                raise SystemExit(
                    f"{key} {value} exceeds the configured limit {limit_value}."
                )
    stage["config"] = config
    return stage


def _parse_budget(value, label):
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise SystemExit(f"{label} must be an integer.")
    if parsed < 0:
        raise SystemExit(f"{label} must be non-negative.")
    return parsed


def _parse_timeout(value, label):
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise SystemExit(f"{label} must be a number.")
    if parsed <= 0:
        raise SystemExit(f"{label} must be greater than zero.")
    return parsed


def build_command(stage):
    name = stage.get("name")
    config = stage.get("config", {})
    if name not in STAGE_MODULES:
        raise SystemExit(f"Unknown stage: {name}")
    module_name = STAGE_MODULES[name]
    cmd = [sys.executable, "-m", module_name]
    cmd.extend(_config_to_args(config))
    return cmd


def _validate_roe_ack(path):
    ack_path = Path(path)
    if not ack_path.exists():
        raise SystemExit(
            f"ROE acknowledgement not found: {ack_path}. "
            "Provide --ack-authorization or --roe-ack."
        )
    data = load_data(ack_path)
    if not isinstance(data, dict):
        raise SystemExit("ROE acknowledgement must be a mapping.")
    required = ["acknowledged_at", "acknowledged_by", "authorized_target"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise SystemExit(
            "ROE acknowledgement missing fields: " + ", ".join(missing)
        )


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
    parser.add_argument(
        "--ack-authorization",
        action="store_true",
        help="Acknowledge authorization before running.",
    )
    parser.add_argument(
        "--roe-ack",
        default="ROE_ACK.yaml",
        help="ROE acknowledgement YAML/JSON path.",
    )
    args = parser.parse_args()

    config = load_data(args.config)
    stages = config.get("stages", [])
    if not stages:
        raise SystemExit("No stages found in pipeline config.")

    limits = config.get("limits", {}) or {}
    request_budget = _parse_budget(limits.get("request_budget"), "request_budget")
    token_budget = _parse_budget(limits.get("token_budget"), "token_budget")
    stage_timeout = _parse_timeout(
        limits.get("stage_timeout_seconds"), "stage_timeout_seconds"
    )
    total_requests = 0
    total_tokens = 0

    for stage in stages:
        _apply_limits(stage, limits)
        config_map = stage.get("config", {}) or {}
        est_requests = _parse_budget(
            config_map.get("estimated_requests"), "estimated_requests"
        )
        est_tokens = _parse_budget(
            config_map.get("estimated_tokens"), "estimated_tokens"
        )
        if est_requests is not None:
            total_requests += est_requests
        if est_tokens is not None:
            total_tokens += est_tokens
        stage["config"] = config_map

    if request_budget is not None and total_requests > request_budget:
        raise SystemExit(
            f"Estimated requests {total_requests} exceed request_budget {request_budget}."
        )
    if token_budget is not None and total_tokens > token_budget:
        raise SystemExit(
            f"Estimated tokens {total_tokens} exceed token_budget {token_budget}."
        )

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

    if not args.ack_authorization:
        _validate_roe_ack(args.roe_ack)

    for stage in stages:
        cmd = build_command(stage)
        if stage_timeout:
            subprocess.run(cmd, check=True, timeout=stage_timeout)
        else:
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
