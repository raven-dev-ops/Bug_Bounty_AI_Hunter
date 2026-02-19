from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG_ROOT = REPO_ROOT / "output/command_center/logs"
DEFAULT_TIMEOUT_SECONDS = 600
RUNNER_MODULE = "command_center_api.tool_runner"
RUN_ID_SAFE_PATTERN = re.compile(r"[^a-zA-Z0-9._-]+")

TOOL_CATALOG: list[dict[str, str]] = [
    {
        "id": "scripts.pipeline_orchestrator",
        "name": "Pipeline Orchestrator",
        "stage": "orchestration",
        "description": "Plan or run staged workflows from a pipeline config file.",
    },
    {
        "id": "scripts.init_engagement_workspace",
        "name": "Init Engagement Workspace",
        "stage": "setup",
        "description": "Scaffold engagement notes and report draft files.",
    },
    {
        "id": "scripts.report_bundle",
        "name": "Report Bundle",
        "stage": "reporting",
        "description": "Generate report bundle artifacts from findings and target profile inputs.",
    },
    {
        "id": "scripts.export_issue_drafts",
        "name": "Issue Draft Export",
        "stage": "reporting",
        "description": "Generate platform-ready issue draft markdown files.",
    },
    {
        "id": "scripts.export_summary",
        "name": "Summary Export",
        "stage": "reporting",
        "description": "Export findings summary in JSON, CSV, and Markdown formats.",
    },
    {
        "id": "scripts.triage_findings",
        "name": "Triage Findings",
        "stage": "analysis",
        "description": "Assign severity/status and enrich findings with triage metadata.",
    },
    {
        "id": "scripts.external_intel",
        "name": "External Intel",
        "stage": "analysis",
        "description": "Attach optional intel provider records to scoped targets.",
    },
    {
        "id": "scripts.notify",
        "name": "Notify",
        "stage": "operations",
        "description": "Emit summary notifications to configured channels.",
    },
]

ALLOWED_TOOLS = {entry["id"] for entry in TOOL_CATALOG}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def list_tools() -> list[dict[str, str]]:
    return [dict(item) for item in TOOL_CATALOG]


def _sanitize_args(args: list[str]) -> list[str]:
    safe_args: list[str] = []
    for value in args:
        text = str(value)
        if any(char in text for char in ("\n", "\r", "\x00")):
            raise ValueError("tool arguments cannot contain control characters")
        safe_args.append(text)
    return safe_args


def _safe_run_id(run_id: str) -> str:
    safe = RUN_ID_SAFE_PATTERN.sub("-", run_id).strip("-")
    return safe or "run"


def build_tool_command(
    tool_id: str, args: list[str], *, request_path: Path
) -> list[str]:
    if tool_id not in ALLOWED_TOOLS:
        raise ValueError(f"tool not allowed: {tool_id}")
    payload = {
        "tool_id": tool_id,
        "args": _sanitize_args(args),
    }
    request_path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
    return [sys.executable, "-m", RUNNER_MODULE, "--request", request_path.as_posix()]


def run_tool(
    *,
    tool_id: str,
    args: list[str],
    run_id: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    log_root: Path | str = DEFAULT_LOG_ROOT,
) -> dict[str, Any]:
    timeout = max(1, int(timeout_seconds))
    safe_run_id = _safe_run_id(run_id)
    logs_dir = Path(log_root)
    if not logs_dir.is_absolute():
        logs_dir = (REPO_ROOT / logs_dir).resolve()
    else:
        logs_dir = logs_dir.resolve()
    logs_dir.mkdir(parents=True, exist_ok=True)
    request_path = logs_dir / f"{safe_run_id}.request.json"
    command = build_tool_command(tool_id, args, request_path=request_path)
    log_path = logs_dir / f"{safe_run_id}.log"

    started_at = utc_now()
    status = "failed"
    exit_code: int | None = None
    stdout = ""
    stderr = ""

    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_code = completed.returncode
        status = "completed" if completed.returncode == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""

    finished_at = utc_now()
    log_text = (
        f"# Command Center tool run\n"
        f"run_id: {run_id}\n"
        f"tool: {tool_id}\n"
        f"started_at: {started_at}\n"
        f"finished_at: {finished_at}\n"
        f"status: {status}\n"
        f"exit_code: {'' if exit_code is None else exit_code}\n"
        f"request: {request_path.as_posix()}\n"
        f"command: {' '.join(command)}\n\n"
        f"## STDOUT\n{stdout}\n\n"
        f"## STDERR\n{stderr}\n"
    )
    log_path.write_text(log_text, encoding="utf-8", newline="\n")

    return {
        "status": status,
        "exit_code": exit_code,
        "finished_at": finished_at,
        "log_path": log_path.as_posix(),
    }


def read_log_tail(log_path: Path | str, *, tail_lines: int = 200) -> str:
    path = Path(log_path)
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    safe_lines = max(1, min(2000, int(tail_lines)))
    return "\n".join(lines[-safe_lines:])
