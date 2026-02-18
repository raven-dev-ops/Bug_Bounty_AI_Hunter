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

            CREATE TABLE IF NOT EXISTS connector_http_cache (
              url TEXT PRIMARY KEY,
              etag TEXT,
              last_modified TEXT,
              response_json TEXT,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS submission_status_history (
              id TEXT PRIMARY KEY,
              platform TEXT NOT NULL,
              submission_id TEXT NOT NULL,
              status TEXT NOT NULL,
              raw_json TEXT NOT NULL,
              observed_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS organizations (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS principals (
              id TEXT PRIMARY KEY,
              email TEXT,
              display_name TEXT,
              oidc_sub TEXT,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS role_bindings (
              id TEXT PRIMARY KEY,
              org_id TEXT NOT NULL,
              principal_id TEXT NOT NULL,
              role TEXT NOT NULL,
              scope TEXT NOT NULL DEFAULT 'global',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_role_binding_unique
            ON role_bindings(org_id, principal_id, role, scope);

            CREATE TABLE IF NOT EXISTS teams (
              id TEXT PRIMARY KEY,
              org_id TEXT NOT NULL,
              name TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_teams_org_name
            ON teams(org_id, name);

            CREATE TABLE IF NOT EXISTS team_members (
              id TEXT PRIMARY KEY,
              team_id TEXT NOT NULL,
              principal_id TEXT NOT NULL,
              role TEXT NOT NULL DEFAULT 'member',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_team_members_unique
            ON team_members(team_id, principal_id);

            CREATE TABLE IF NOT EXISTS sessions (
              id TEXT PRIMARY KEY,
              principal_id TEXT NOT NULL,
              org_id TEXT NOT NULL,
              token_hash TEXT NOT NULL,
              issued_at TEXT NOT NULL,
              expires_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS job_queue (
              id TEXT PRIMARY KEY,
              idempotency_key TEXT,
              kind TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              status TEXT NOT NULL,
              attempts INTEGER NOT NULL DEFAULT 0,
              max_attempts INTEGER NOT NULL DEFAULT 3,
              last_error TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              started_at TEXT,
              finished_at TEXT
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_job_queue_idempotency
            ON job_queue(idempotency_key);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_token_hash
            ON sessions(token_hash);
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


def delete_finding(connection: sqlite3.Connection, finding_id: str) -> bool:
    cursor = connection.execute(
        "DELETE FROM findings WHERE id = ?",
        (finding_id,),
    )
    return cursor.rowcount > 0


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


def get_tool_run(connection: sqlite3.Connection, run_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM tool_runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        return None
    item = _row_to_dict(row)
    item["request_json"] = json.loads(item["request_json"])
    return item


def update_tool_run(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    status: str,
    exit_code: int | None,
    finished_at: str | None,
    log_path: str | None,
    artifact_path: str | None = None,
) -> dict[str, Any] | None:
    connection.execute(
        """
        UPDATE tool_runs
        SET status = ?,
            exit_code = ?,
            finished_at = ?,
            log_path = ?,
            artifact_path = ?
        WHERE id = ?
        """,
        (status, exit_code, finished_at, log_path, artifact_path, run_id),
    )
    return get_tool_run(connection, run_id)


def create_notification(
    connection: sqlite3.Connection,
    *,
    notification_id: str,
    channel: str,
    title: str,
    body: str,
) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO notifications (id, channel, title, body, read, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (notification_id, channel, title, body, 0, utc_now()),
    )
    row = connection.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to create notification")
    return _row_to_dict(row)


def list_notifications(
    connection: sqlite3.Connection,
    *,
    limit: int = 200,
    unread_only: bool = False,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    if unread_only:
        rows = connection.execute(
            """
            SELECT * FROM notifications
            WHERE read = 0
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT * FROM notifications
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def mark_notification_read(
    connection: sqlite3.Connection,
    *,
    notification_id: str,
    read: bool,
) -> dict[str, Any] | None:
    connection.execute(
        """
        UPDATE notifications
        SET read = ?
        WHERE id = ?
        """,
        (_normalize_bool(read), notification_id),
    )
    row = connection.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,)).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def create_connector_run(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    connector: str,
    status: str,
    summary: dict[str, Any],
) -> dict[str, Any]:
    now = utc_now()
    connection.execute(
        """
        INSERT INTO connector_runs (id, connector, status, summary_json, started_at, finished_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (run_id, connector, status, _json_dump(summary), now, None),
    )
    row = connection.execute("SELECT * FROM connector_runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to create connector run")
    item = _row_to_dict(row)
    item["summary_json"] = json.loads(item["summary_json"])
    return item


def finish_connector_run(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    status: str,
    summary: dict[str, Any],
) -> dict[str, Any] | None:
    now = utc_now()
    connection.execute(
        """
        UPDATE connector_runs
        SET status = ?,
            summary_json = ?,
            finished_at = ?
        WHERE id = ?
        """,
        (status, _json_dump(summary), now, run_id),
    )
    row = connection.execute("SELECT * FROM connector_runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        return None
    item = _row_to_dict(row)
    item["summary_json"] = json.loads(item["summary_json"])
    return item


def get_http_cache(connection: sqlite3.Connection, url: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM connector_http_cache WHERE url = ?",
        (url,),
    ).fetchone()
    if row is None:
        return None
    item = _row_to_dict(row)
    payload = item.get("response_json")
    if payload:
        item["response_json"] = json.loads(str(payload))
    else:
        item["response_json"] = None
    return item


def upsert_http_cache(
    connection: sqlite3.Connection,
    *,
    url: str,
    etag: str | None,
    last_modified: str | None,
    response_json: dict[str, Any] | None,
) -> dict[str, Any]:
    now = utc_now()
    payload = _json_dump(response_json or {})
    connection.execute(
        """
        INSERT INTO connector_http_cache (url, etag, last_modified, response_json, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
          etag = excluded.etag,
          last_modified = excluded.last_modified,
          response_json = excluded.response_json,
          updated_at = excluded.updated_at
        """,
        (url, etag, last_modified, payload, now),
    )
    item = get_http_cache(connection, url)
    if item is None:
        raise RuntimeError("failed to upsert connector_http_cache")
    return item


def add_submission_status_event(
    connection: sqlite3.Connection,
    *,
    event_id: str,
    platform: str,
    submission_id: str,
    status: str,
    payload: dict[str, Any],
) -> None:
    connection.execute(
        """
        INSERT OR REPLACE INTO submission_status_history (
          id, platform, submission_id, status, raw_json, observed_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (event_id, platform, submission_id, status, _json_dump(payload), utc_now()),
    )


def upsert_task(connection: sqlite3.Connection, task: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    task_id = str(task.get("id") or "").strip()
    if not task_id:
        raise ValueError("task.id is required")
    connection.execute(
        """
        INSERT INTO tasks (
          id, title, status, linked_program_id, linked_finding_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          title = excluded.title,
          status = excluded.status,
          linked_program_id = excluded.linked_program_id,
          linked_finding_id = excluded.linked_finding_id,
          updated_at = excluded.updated_at
        """,
        (
            task_id,
            str(task.get("title") or "").strip(),
            str(task.get("status") or "open").strip(),
            str(task.get("linked_program_id") or "").strip() or None,
            str(task.get("linked_finding_id") or "").strip() or None,
            now,
            now,
        ),
    )
    row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to upsert task")
    return _row_to_dict(row)


def get_task(connection: sqlite3.Connection, task_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def delete_task(connection: sqlite3.Connection, task_id: str) -> bool:
    cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cursor.rowcount > 0


def list_tasks(connection: sqlite3.Connection, *, limit: int = 200) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM tasks
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (safe_limit,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def add_metric_snapshot(
    connection: sqlite3.Connection,
    *,
    snapshot_id: str,
    metric_name: str,
    metric_value: float,
    scope: str,
) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO metrics_snapshots (id, metric_name, metric_value, scope, captured_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (snapshot_id, metric_name, float(metric_value), scope, utc_now()),
    )
    row = connection.execute("SELECT * FROM metrics_snapshots WHERE id = ?", (snapshot_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to add metric snapshot")
    return _row_to_dict(row)


def list_metric_snapshots(
    connection: sqlite3.Connection,
    *,
    scope: str = "global",
    limit: int = 200,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM metrics_snapshots
        WHERE scope = ?
        ORDER BY captured_at DESC
        LIMIT ?
        """,
        (scope, safe_limit),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def upsert_organization(
    connection: sqlite3.Connection,
    *,
    org_id: str,
    name: str,
) -> dict[str, Any]:
    now = utc_now()
    connection.execute(
        """
        INSERT INTO organizations (id, name, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          name = excluded.name
        """,
        (org_id, name, now),
    )
    row = connection.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to upsert organization")
    return _row_to_dict(row)


def list_organizations(connection: sqlite3.Connection, *, limit: int = 200) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM organizations
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (safe_limit,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def upsert_principal(
    connection: sqlite3.Connection,
    *,
    principal_id: str,
    email: str | None,
    display_name: str | None,
    oidc_sub: str | None,
) -> dict[str, Any]:
    now = utc_now()
    connection.execute(
        """
        INSERT INTO principals (id, email, display_name, oidc_sub, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          email = excluded.email,
          display_name = excluded.display_name,
          oidc_sub = excluded.oidc_sub
        """,
        (principal_id, email, display_name, oidc_sub, now),
    )
    row = connection.execute("SELECT * FROM principals WHERE id = ?", (principal_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to upsert principal")
    return _row_to_dict(row)


def get_principal(connection: sqlite3.Connection, principal_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM principals WHERE id = ?", (principal_id,)).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def list_principals(connection: sqlite3.Connection, *, limit: int = 200) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM principals
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (safe_limit,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def upsert_role_binding(
    connection: sqlite3.Connection,
    *,
    binding_id: str,
    org_id: str,
    principal_id: str,
    role: str,
    scope: str = "global",
) -> dict[str, Any]:
    now = utc_now()
    connection.execute(
        """
        INSERT INTO role_bindings (id, org_id, principal_id, role, scope, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(org_id, principal_id, role, scope) DO UPDATE SET
          updated_at = excluded.updated_at
        """,
        (binding_id, org_id, principal_id, role, scope, now, now),
    )
    row = connection.execute(
        """
        SELECT * FROM role_bindings
        WHERE org_id = ? AND principal_id = ? AND role = ? AND scope = ?
        """,
        (org_id, principal_id, role, scope),
    ).fetchone()
    if row is None:
        raise RuntimeError("failed to upsert role binding")
    return _row_to_dict(row)


def list_role_bindings_for_principal(
    connection: sqlite3.Connection,
    *,
    principal_id: str,
    org_id: str | None = None,
) -> list[dict[str, Any]]:
    if org_id:
        rows = connection.execute(
            """
            SELECT * FROM role_bindings
            WHERE principal_id = ? AND org_id = ?
            ORDER BY created_at DESC
            """,
            (principal_id, org_id),
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT * FROM role_bindings
            WHERE principal_id = ?
            ORDER BY created_at DESC
            """,
            (principal_id,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def list_role_bindings(
    connection: sqlite3.Connection,
    *,
    org_id: str | None = None,
    principal_id: str | None = None,
    limit: int = 500,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(2000, int(limit)))
    if org_id and principal_id:
        rows = connection.execute(
            """
            SELECT * FROM role_bindings
            WHERE org_id = ? AND principal_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (org_id, principal_id, safe_limit),
        ).fetchall()
    elif org_id:
        rows = connection.execute(
            """
            SELECT * FROM role_bindings
            WHERE org_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (org_id, safe_limit),
        ).fetchall()
    elif principal_id:
        rows = connection.execute(
            """
            SELECT * FROM role_bindings
            WHERE principal_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (principal_id, safe_limit),
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT * FROM role_bindings
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def upsert_team(
    connection: sqlite3.Connection,
    *,
    team_id: str,
    org_id: str,
    name: str,
) -> dict[str, Any]:
    now = utc_now()
    connection.execute(
        """
        INSERT INTO teams (id, org_id, name, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(org_id, name) DO UPDATE SET
          updated_at = excluded.updated_at
        """,
        (team_id, org_id, name, now, now),
    )
    row = connection.execute(
        """
        SELECT * FROM teams
        WHERE org_id = ? AND name = ?
        """,
        (org_id, name),
    ).fetchone()
    if row is None:
        raise RuntimeError("failed to upsert team")
    return _row_to_dict(row)


def list_teams(
    connection: sqlite3.Connection,
    *,
    org_id: str,
    limit: int = 200,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM teams
        WHERE org_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (org_id, safe_limit),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_team(connection: sqlite3.Connection, team_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def upsert_team_member(
    connection: sqlite3.Connection,
    *,
    member_id: str,
    team_id: str,
    principal_id: str,
    role: str = "member",
) -> dict[str, Any]:
    now = utc_now()
    connection.execute(
        """
        INSERT INTO team_members (id, team_id, principal_id, role, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(team_id, principal_id) DO UPDATE SET
          role = excluded.role,
          updated_at = excluded.updated_at
        """,
        (member_id, team_id, principal_id, role, now, now),
    )
    row = connection.execute(
        """
        SELECT * FROM team_members
        WHERE team_id = ? AND principal_id = ?
        """,
        (team_id, principal_id),
    ).fetchone()
    if row is None:
        raise RuntimeError("failed to upsert team member")
    return _row_to_dict(row)


def list_team_members(
    connection: sqlite3.Connection,
    *,
    team_id: str,
    limit: int = 500,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(2000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM team_members
        WHERE team_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (team_id, safe_limit),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def create_session(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    principal_id: str,
    org_id: str,
    token_hash: str,
    issued_at: str,
    expires_at: str,
) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO sessions (id, principal_id, org_id, token_hash, issued_at, expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (session_id, principal_id, org_id, token_hash, issued_at, expires_at),
    )
    row = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to create session")
    return _row_to_dict(row)


def get_session_by_token_hash(
    connection: sqlite3.Connection,
    token_hash: str,
) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM sessions WHERE token_hash = ?",
        (token_hash,),
    ).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def get_session(connection: sqlite3.Connection, session_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def list_sessions_for_principal(
    connection: sqlite3.Connection,
    *,
    principal_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(200, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM sessions
        WHERE principal_id = ?
        ORDER BY issued_at DESC
        LIMIT ?
        """,
        (principal_id, safe_limit),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def delete_session(connection: sqlite3.Connection, session_id: str) -> bool:
    cursor = connection.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    return cursor.rowcount > 0


def enqueue_job(
    connection: sqlite3.Connection,
    *,
    job_id: str,
    idempotency_key: str | None,
    kind: str,
    payload: dict[str, Any],
    max_attempts: int = 3,
) -> dict[str, Any]:
    if idempotency_key:
        existing = get_job_by_idempotency_key(connection, idempotency_key=idempotency_key)
        if existing is not None:
            return existing
    now = utc_now()
    connection.execute(
        """
        INSERT INTO job_queue (
          id, idempotency_key, kind, payload_json, status, attempts, max_attempts,
          last_error, created_at, updated_at, started_at, finished_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job_id,
            idempotency_key,
            kind,
            _json_dump(payload),
            "queued",
            0,
            max(1, int(max_attempts)),
            None,
            now,
            now,
            None,
            None,
        ),
    )
    row = connection.execute("SELECT * FROM job_queue WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        raise RuntimeError("failed to enqueue job")
    item = _row_to_dict(row)
    item["payload_json"] = json.loads(item["payload_json"])
    return item


def get_job(connection: sqlite3.Connection, job_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM job_queue WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        return None
    item = _row_to_dict(row)
    item["payload_json"] = json.loads(item["payload_json"])
    return item


def get_job_by_idempotency_key(
    connection: sqlite3.Connection,
    *,
    idempotency_key: str,
) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM job_queue WHERE idempotency_key = ?",
        (idempotency_key,),
    ).fetchone()
    if row is None:
        return None
    item = _row_to_dict(row)
    item["payload_json"] = json.loads(item["payload_json"])
    return item


def list_jobs(connection: sqlite3.Connection, *, limit: int = 200) -> list[dict[str, Any]]:
    safe_limit = max(1, min(1000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM job_queue
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (safe_limit,),
    ).fetchall()
    items: list[dict[str, Any]] = []
    for row in rows:
        item = _row_to_dict(row)
        item["payload_json"] = json.loads(item["payload_json"])
        items.append(item)
    return items


def claim_next_job(connection: sqlite3.Connection) -> dict[str, Any] | None:
    row = connection.execute(
        """
        SELECT *
        FROM job_queue
        WHERE status = 'queued'
          AND attempts < max_attempts
        ORDER BY created_at ASC
        LIMIT 1
        """,
    ).fetchone()
    if row is None:
        return None
    job_id = row["id"]
    now = utc_now()
    connection.execute(
        """
        UPDATE job_queue
        SET status = 'running',
            attempts = attempts + 1,
            updated_at = ?,
            started_at = ?
        WHERE id = ?
        """,
        (now, now, job_id),
    )
    updated = connection.execute("SELECT * FROM job_queue WHERE id = ?", (job_id,)).fetchone()
    if updated is None:
        return None
    item = _row_to_dict(updated)
    item["payload_json"] = json.loads(item["payload_json"])
    return item


def finish_job(
    connection: sqlite3.Connection,
    *,
    job_id: str,
    status: str,
    last_error: str | None = None,
) -> dict[str, Any] | None:
    now = utc_now()
    current = connection.execute("SELECT * FROM job_queue WHERE id = ?", (job_id,)).fetchone()
    if current is None:
        return None
    attempts = int(current["attempts"] or 0)
    max_attempts = int(current["max_attempts"] or 1)
    next_status = status
    finished_at: str | None = now
    if status == "failed" and attempts < max_attempts:
        # Keep failed jobs retryable until max attempts is reached.
        next_status = "queued"
        finished_at = None
    if next_status in {"queued", "running"}:
        finished_at = None
    connection.execute(
        """
        UPDATE job_queue
        SET status = ?,
            last_error = ?,
            updated_at = ?,
            finished_at = ?
        WHERE id = ?
        """,
        (next_status, last_error, now, finished_at, job_id),
    )
    row = connection.execute("SELECT * FROM job_queue WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        return None
    item = _row_to_dict(row)
    item["payload_json"] = json.loads(item["payload_json"])
    return item


def retry_job(connection: sqlite3.Connection, *, job_id: str) -> dict[str, Any] | None:
    now = utc_now()
    row = connection.execute("SELECT * FROM job_queue WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        return None
    current_status = str(row["status"])
    if current_status == "running":
        raise ValueError("cannot retry running job")
    connection.execute(
        """
        UPDATE job_queue
        SET status = 'queued',
            updated_at = ?,
            started_at = NULL,
            finished_at = NULL
        WHERE id = ?
        """,
        (now, job_id),
    )
    updated = connection.execute("SELECT * FROM job_queue WHERE id = ?", (job_id,)).fetchone()
    if updated is None:
        return None
    item = _row_to_dict(updated)
    item["payload_json"] = json.loads(item["payload_json"])
    return item


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


def list_audit_events(connection: sqlite3.Connection, *, limit: int = 500) -> list[dict[str, Any]]:
    safe_limit = max(1, min(5000, int(limit)))
    rows = connection.execute(
        """
        SELECT * FROM audit_events
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (safe_limit,),
    ).fetchall()
    items: list[dict[str, Any]] = []
    for row in rows:
        item = _row_to_dict(row)
        item["payload_json"] = json.loads(item["payload_json"])
        items.append(item)
    return items
