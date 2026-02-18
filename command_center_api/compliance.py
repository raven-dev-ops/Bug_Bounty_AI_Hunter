from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

def _query_rows(connection: Any, query: str) -> list[dict[str, Any]]:
    rows = connection.execute(query).fetchall()
    return [{key: row[key] for key in row.keys()} for row in rows]


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8", newline="\n")
        return
    fields = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def export_compliance_bundle(
    *,
    connection: Any,
    output_dir: Path | str = Path("output/compliance"),
) -> dict[str, Any]:
    root = Path(output_dir)
    bundle_queries = {
        "audit_events": "SELECT * FROM audit_events ORDER BY created_at DESC",
        "connector_runs": "SELECT * FROM connector_runs ORDER BY started_at DESC",
        "connector_http_cache": "SELECT * FROM connector_http_cache ORDER BY updated_at DESC",
        "submission_status_history": "SELECT * FROM submission_status_history ORDER BY observed_at DESC",
        "tool_runs": "SELECT * FROM tool_runs ORDER BY started_at DESC",
        "notifications": "SELECT * FROM notifications ORDER BY created_at DESC",
        "metrics_snapshots": "SELECT * FROM metrics_snapshots ORDER BY captured_at DESC",
        "organizations": "SELECT * FROM organizations ORDER BY created_at DESC",
        "principals": "SELECT * FROM principals ORDER BY created_at DESC",
        "role_bindings": "SELECT * FROM role_bindings ORDER BY updated_at DESC",
        "teams": "SELECT * FROM teams ORDER BY updated_at DESC",
        "team_members": "SELECT * FROM team_members ORDER BY updated_at DESC",
        "sessions": "SELECT * FROM sessions ORDER BY issued_at DESC",
        "job_queue": "SELECT * FROM job_queue ORDER BY created_at DESC",
        "programs": "SELECT * FROM programs ORDER BY updated_at DESC",
        "findings": "SELECT * FROM findings ORDER BY updated_at DESC",
        "workspaces": "SELECT * FROM workspaces ORDER BY updated_at DESC",
        "tasks": "SELECT * FROM tasks ORDER BY updated_at DESC",
    }
    bundle = {key: _query_rows(connection, query) for key, query in bundle_queries.items()}

    json_path = root / "compliance_export.json"
    _write_json(
        json_path,
        {
            "schema_version": "v2.0",
            "bundle": bundle,
        },
    )

    csv_paths = []
    for key, rows in bundle.items():
        csv_path = root / f"{key}.csv"
        _write_csv(csv_path, rows)
        csv_paths.append(csv_path.as_posix())

    return {
        "output_dir": root.as_posix(),
        "json": json_path.as_posix(),
        "csv": csv_paths,
        "counts": {key: len(value) for key, value in bundle.items()},
    }
