from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

from command_center_api import db, tools


_WORKER_THREAD: threading.Thread | None = None
_STOP_EVENT = threading.Event()


def _process_job(connection: Any, job: dict[str, Any]) -> None:
    kind = str(job.get("kind") or "").strip()
    payload = job.get("payload_json")
    if not isinstance(payload, dict):
        raise RuntimeError("job payload must be an object")
    if kind != "tool_run":
        raise RuntimeError(f"unsupported job kind: {kind}")

    tool_name = str(payload.get("tool") or "").strip()
    mode = str(payload.get("mode") or "plan").strip()
    args = payload.get("args", [])
    if not isinstance(args, list):
        raise RuntimeError("job args must be a list")
    timeout_seconds = int(payload.get("timeout_seconds") or 600)
    run_id = f"run:{job['id']}"

    existing = db.get_tool_run(connection, run_id)
    if existing is None:
        db.create_tool_run(
            connection,
            run_id=run_id,
            tool=tool_name,
            mode=mode,
            status="running",
            request=payload,
        )
    else:
        db.update_tool_run(
            connection,
            run_id=run_id,
            status="running",
            exit_code=None,
            finished_at=None,
            log_path=existing.get("log_path"),
        )

    execution = tools.run_tool(
        tool_id=tool_name,
        args=[str(item) for item in args],
        run_id=run_id,
        timeout_seconds=timeout_seconds,
    )
    db.update_tool_run(
        connection,
        run_id=run_id,
        status=str(execution["status"]),
        exit_code=execution["exit_code"],
        finished_at=str(execution["finished_at"]),
        log_path=str(execution["log_path"]),
    )
    if execution["status"] != "completed":
        raise RuntimeError(f"tool run finished with status {execution['status']}")


def _worker_loop(db_path: Path | str) -> None:
    while not _STOP_EVENT.is_set():
        with db.get_connection(db_path) as connection:
            job = db.claim_next_job(connection)
        if job is None:
            time.sleep(0.25)
            continue
        job_id = str(job["id"])
        try:
            with db.get_connection(db_path) as connection:
                _process_job(connection, job)
                db.finish_job(connection, job_id=job_id, status="completed")
        except Exception as exc:  # pragma: no cover - worker failures validated through API
            with db.get_connection(db_path) as connection:
                db.finish_job(connection, job_id=job_id, status="failed", last_error=str(exc))


def start_worker(db_path: Path | str) -> dict[str, Any]:
    global _WORKER_THREAD
    if _WORKER_THREAD and _WORKER_THREAD.is_alive():
        return {"running": True}
    _STOP_EVENT.clear()
    _WORKER_THREAD = threading.Thread(
        target=_worker_loop,
        args=(db_path,),
        name="command-center-job-runner",
        daemon=True,
    )
    _WORKER_THREAD.start()
    return {"running": True}


def stop_worker() -> dict[str, Any]:
    _STOP_EVENT.set()
    return {"running": False}


def worker_status() -> dict[str, Any]:
    running = bool(_WORKER_THREAD and _WORKER_THREAD.is_alive())
    return {"running": running}
