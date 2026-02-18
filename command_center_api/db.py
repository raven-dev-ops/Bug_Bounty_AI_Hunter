from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_DB_PATH = Path("data/command_center.db")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def _normalize_bool(value: Any) -> int:
    return 1 if bool(value) else 0


def _connect(db_path: Path | str) -> sqlite3.Connection:
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_connection(db_path: Path | str = DEFAULT_DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = _connect(db_path)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_schema(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS programs (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              platform TEXT,
              handle TEXT,
              policy_url TEXT,
              rewards_summary TEXT,
              source TEXT,
              raw_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS findings (
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              severity TEXT,
              status TEXT,
              source TEXT,
              description TEXT,
              impact TEXT,
              remediation TEXT,
              raw_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS workspaces (
              id TEXT PRIMARY KEY,
              platform TEXT NOT NULL,
              slug TEXT NOT NULL,
              name TEXT NOT NULL,
              engagement_url TEXT,
              root_dir TEXT,
              roe_acknowledged INTEGER NOT NULL DEFAULT 0,
              acknowledged_at TEXT,
              acknowledged_by TEXT,
              authorized_target TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_workspaces_platform_slug
            ON workspaces(platform, slug);

            CREATE TABLE IF NOT EXISTS tool_runs (
              id TEXT PRIMARY KEY,
              tool TEXT NOT NULL,
              mode TEXT NOT NULL,
              status TEXT NOT NULL,
              exit_code INTEGER,
              started_at TEXT NOT NULL,
              finished_at TEXT,
              log_path TEXT,
              artifact_path TEXT,
              request_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tasks (
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              status TEXT NOT NULL,
              linked_program_id TEXT,
              linked_finding_id TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notifications (
              id TEXT PRIMARY KEY,
              channel TEXT NOT NULL,
              title TEXT NOT NULL,
              body TEXT NOT NULL,
              read INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_events (
              id TEXT PRIMARY KEY,
              event_type TEXT NOT NULL,
              actor TEXT,
              payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS metrics_snapshots (
              id TEXT PRIMARY KEY,
              metric_name TEXT NOT NULL,
              metric_value REAL NOT NULL,
              scope TEXT,
              captured_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS connector_runs (
              id TEXT PRIMARY KEY,
              connector TEXT NOT NULL,
              status TEXT NOT NULL,
              summary_json TEXT NOT NULL,
              started_at TEXT NOT NULL,
              finished_at TEXT
            );
            """
        )


def upsert_programs(
    connection: sqlite3.Connection,
    programs: Iterable[dict[str, Any]],
    *,
    source: str,
) -> int:
    now = utc_now()
    count = 0
    for program in programs:
        program_id = str(program.get("id") or "").strip()
        if not program_id:
            continue
        connection.execute(
            """
            INSERT INTO programs (
              id, name, platform, handle, policy_url, rewards_summary,
              source, raw_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              name = excluded.name,
              platform = excluded.platform,
              handle = excluded.handle,
              policy_url = excluded.policy_url,
              rewards_summary = excluded.rewards_summary,
              source = excluded.source,
              raw_json = excluded.raw_json,
              updated_at = excluded.updated_at
            """,
            (
                program_id,
                str(program.get("name") or "").strip() or program_id,
                str(program.get("platform") or "").strip() or None,
                str(program.get("handle") or "").strip() or None,
                str(program.get("policy_url") or program.get("canonical_url") or "").strip()
                or None,
                str((program.get("rewards") or {}).get("summary") or "").strip() or None,
                source,
                _json_dump(program),
                now,
                now,
            ),
        )
        count += 1
    return count


def upsert_findings(
    connection: sqlite3.Connection,
    findings: Iterable[dict[str, Any]],
    *,
    source: str,
) -> int:
    now = utc_now()
    count = 0
    for finding in findings:
        finding_id = str(finding.get("id") or "").strip()
        if not finding_id:
            continue
        connection.execute(
            """
            INSERT INTO findings (
              id, title, severity, status, source, description, impact, remediation,
              raw_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              title = excluded.title,
              severity = excluded.severity,
              status = excluded.status,
              source = excluded.source,
              description = excluded.description,
              impact = excluded.impact,
              remediation = excluded.remediation,
              raw_json = excluded.raw_json,
              updated_at = excluded.updated_at
            """,
            (
                finding_id,
                str(finding.get("title") or "").strip() or finding_id,
                str(finding.get("severity") or "").strip() or None,
                str(finding.get("status") or "open").strip() or "open",
                source,
                str(finding.get("description") or "").strip() or None,
                str(finding.get("impact") or "").strip() or None,
                str(finding.get("remediation") or "").strip() or None,
                _json_dump(finding),
                str(finding.get("created_at") or now),
                now,
            ),
        )
        count += 1
    return count


def list_programs(
    connection: sqlite3.Connection,
    *,
    query: str = "",
    limit: int = 100,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(500, int(limit)))
    safe_query = f"%{query.strip().lower()}%"
    rows = connection.execute(
        """
        SELECT *
        FROM programs
        WHERE lower(name) LIKE ?
          OR lower(COALESCE(handle, '')) LIKE ?
          OR lower(COALESCE(platform, '')) LIKE ?
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (safe_query, safe_query, safe_query, safe_limit),
    ).fetchall()
    items: list[dict[str, Any]] = []
    for row in rows:
        item = _row_to_dict(row)
        item["raw_json"] = json.loads(item["raw_json"])
        items.append(item)
    return items


def get_program(connection: sqlite3.Connection, program_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM programs WHERE id = ?",
        (program_id,),
    ).fetchone()
    if row is None:
        return None
    item = _row_to_dict(row)
    item["raw_json"] = json.loads(item["raw_json"])
    return item


def list_findings(connection: sqlite3.Connection, *, limit: int = 200) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM findings
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (safe_limit,),
    ).fetchall()
    items: list[dict[str, Any]] = []
    for row in rows:
        item = _row_to_dict(row)
        item["raw_json"] = json.loads(item["raw_json"])
        items.append(item)
    return items


def upsert_finding(connection: sqlite3.Connection, finding: dict[str, Any], *, source: str) -> dict[str, Any]:
    upsert_findings(connection, [finding], source=source)
    row = connection.execute("SELECT * FROM findings WHERE id = ?", (finding["id"],)).fetchone()
    if row is None:
        raise RuntimeError("failed to upsert finding")
    item = _row_to_dict(row)
    item["raw_json"] = json.loads(item["raw_json"])
    return item


def upsert_workspace(connection: sqlite3.Connection, workspace: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    workspace_id = str(workspace.get("id") or "").strip()
    if not workspace_id:
        raise ValueError("workspace.id is required")
    connection.execute(
        """
        INSERT INTO workspaces (
          id, platform, slug, name, engagement_url, root_dir, roe_acknowledged,
          acknowledged_at, acknowledged_by, authorized_target, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          platform = excluded.platform,
          slug = excluded.slug,
          name = excluded.name,
          engagement_url = excluded.engagement_url,
          root_dir = excluded.root_dir,
          roe_acknowledged = excluded.roe_acknowledged,
          acknowledged_at = excluded.acknowledged_at,
          acknowledged_by = excluded.acknowledged_by,
          authorized_target = excluded.authorized_target,
          updated_at = excluded.updated_at
        """,
        (
            workspace_id,
            str(workspace.get("platform") or "").strip(),
            str(workspace.get("slug") or "").strip(),
            str(workspace.get("name") or "").strip(),
            str(workspace.get("engagement_url") or "").strip() or None,
            str(workspace.get("root_dir") or "").strip() or None,
            _normalize_bool(workspace.get("roe_acknowledged")),
            str(workspace.get("acknowledged_at") or "").strip() or None,
            str(workspace.get("acknowledged_by") or "").strip() or None,
            str(workspace.get("authorized_target") or "").strip() or None,
            now,
            now,
        ),
    )
    row = connection.execute("SELECT * FROM workspaces WHERE id = ?", (workspace_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to upsert workspace")
    return _row_to_dict(row)


def acknowledge_workspace(
    connection: sqlite3.Connection,
    *,
    workspace_id: str,
    acknowledged_by: str,
    authorized_target: str,
) -> dict[str, Any] | None:
    now = utc_now()
    connection.execute(
        """
        UPDATE workspaces
        SET roe_acknowledged = 1,
            acknowledged_at = ?,
            acknowledged_by = ?,
            authorized_target = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (now, acknowledged_by, authorized_target, now, workspace_id),
    )
    row = connection.execute("SELECT * FROM workspaces WHERE id = ?", (workspace_id,)).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def get_workspace(connection: sqlite3.Connection, workspace_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM workspaces WHERE id = ?",
        (workspace_id,),
    ).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def list_workspaces(connection: sqlite3.Connection, *, limit: int = 200) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM workspaces
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (safe_limit,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def create_tool_run(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    tool: str,
    mode: str,
    status: str,
    request: dict[str, Any],
) -> dict[str, Any]:
    now = utc_now()
    connection.execute(
        """
        INSERT INTO tool_runs (
          id, tool, mode, status, exit_code, started_at, finished_at,
          log_path, artifact_path, request_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            tool,
            mode,
            status,
            None,
            now,
            None,
            None,
            None,
            _json_dump(request),
        ),
    )
    row = connection.execute("SELECT * FROM tool_runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to create tool run")
    item = _row_to_dict(row)
    item["request_json"] = json.loads(item["request_json"])
    return item


def list_tool_runs(connection: sqlite3.Connection, *, limit: int = 200) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    rows = connection.execute(
        """
        SELECT *
        FROM tool_runs
        ORDER BY started_at DESC
        LIMIT ?
        """,
        (safe_limit,),
    ).fetchall()
    items: list[dict[str, Any]] = []
    for row in rows:
        item = _row_to_dict(row)
        item["request_json"] = json.loads(item["request_json"])
        items.append(item)
    return items


def add_audit_event(
    connection: sqlite3.Connection,
    *,
    event_id: str,
    event_type: str,
    actor: str,
    payload: dict[str, Any],
) -> None:
    connection.execute(
        """
        INSERT INTO audit_events (id, event_type, actor, payload_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (event_id, event_type, actor, _json_dump(payload), utc_now()),
    )
