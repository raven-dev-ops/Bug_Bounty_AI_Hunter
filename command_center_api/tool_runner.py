from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from typing import Any


ALLOWED_TOOLS = {
    "scripts.pipeline_orchestrator",
    "scripts.init_engagement_workspace",
    "scripts.report_bundle",
    "scripts.export_issue_drafts",
    "scripts.export_summary",
    "scripts.triage_findings",
    "scripts.external_intel",
    "scripts.notify",
}


def _load_request(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("request payload must be an object")
    return data


def _validate_args(raw_args: Any) -> list[str]:
    if not isinstance(raw_args, list):
        raise ValueError("tool args must be a list")
    safe_args: list[str] = []
    for value in raw_args:
        text = str(value)
        if any(char in text for char in ("\n", "\r", "\x00")):
            raise ValueError("tool arguments cannot contain control characters")
        safe_args.append(text)
    return safe_args


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run an allowlisted module with request-file arguments."
    )
    parser.add_argument(
        "--request", required=True, help="Path to request JSON payload."
    )
    args = parser.parse_args(argv)

    payload = _load_request(Path(args.request))
    tool_id = str(payload.get("tool_id", "")).strip()
    if tool_id not in ALLOWED_TOOLS:
        raise ValueError(f"tool not allowed: {tool_id}")
    tool_args = _validate_args(payload.get("args", []))

    original_argv = list(sys.argv)
    try:
        sys.argv = [tool_id, *tool_args]
        runpy.run_module(tool_id, run_name="__main__")
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    main()
