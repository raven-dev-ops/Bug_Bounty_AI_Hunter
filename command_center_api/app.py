from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from command_center_api import db, docs_search, ingest, tools, workspace


class FindingInput(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    severity: str | None = None
    status: str | None = "open"
    source: str | None = None
    description: str | None = None
    impact: str | None = None
    remediation: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class FindingsImportInput(BaseModel):
    findings: list[dict[str, Any]]
    source: str = "command_center_import"


class WorkspaceInput(BaseModel):
    platform: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    name: str = Field(min_length=1)
    engagement_url: str | None = None
    root_dir: str | None = None
    scaffold_files: bool = True
    force: bool = False


class WorkspaceAckInput(BaseModel):
    acknowledged_by: str = Field(min_length=1)
    authorized_target: str = Field(min_length=1)


class ToolRunInput(BaseModel):
    tool: str = Field(min_length=1)
    mode: str = Field(default="plan", pattern="^(plan|run)$")
    args: list[str] = Field(default_factory=list)
    workspace_id: str | None = None


class ToolExecuteInput(ToolRunInput):
    timeout_seconds: int = Field(default=600, ge=1, le=7200)


class ReportBundleInput(BaseModel):
    findings_path: str = Field(default="examples/outputs/findings.json")
    target_profile_path: str = Field(default="examples/target_profile_minimal.yaml")
    output_dir: str = Field(default="output/command_center/report_bundle")
    evidence_path: str | None = None
    repro_steps_path: str | None = None
    workspace_id: str | None = None
    timeout_seconds: int = Field(default=600, ge=1, le=7200)


class IssueDraftInput(BaseModel):
    findings_path: str = Field(default="examples/outputs/findings.json")
    target_profile_path: str = Field(default="examples/target_profile_minimal.yaml")
    output_dir: str = Field(default="output/command_center/issue_drafts")
    platform: str = Field(default="github")
    attachments_manifest_path: str | None = None
    workspace_id: str | None = None
    timeout_seconds: int = Field(default=600, ge=1, le=7200)


class NotificationInput(BaseModel):
    channel: str = Field(min_length=1)
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)


class NotificationReadInput(BaseModel):
    read: bool = True


def create_app(*, db_path: Path | str = db.DEFAULT_DB_PATH) -> FastAPI:
    app = FastAPI(
        title="Command Center API",
        version="0.1.0",
        description=(
            "MVP backend for command-center planning and reporting workflows. "
            "Provides REST resources for programs, findings, workspaces, tool runs, and docs search."
        ),
    )
    app.state.db_path = Path(db_path)
    db.init_schema(app.state.db_path)

    def _require_workspace_ack_for_run(
        *,
        connection: Any,
        mode: str,
        workspace_id: str | None,
    ) -> None:
        if mode != "run":
            return
        if not workspace_id:
            raise HTTPException(
                status_code=400,
                detail="workspace_id is required for run mode",
            )
        workspace_row = db.get_workspace(connection, workspace_id)
        if workspace_row is None:
            raise HTTPException(status_code=404, detail="workspace not found")
        if not bool(workspace_row.get("roe_acknowledged")):
            raise HTTPException(
                status_code=403,
                detail="workspace ROE acknowledgement is required before run mode",
            )

    def _execute_tool_run(
        *,
        tool: str,
        mode: str,
        args: list[str],
        workspace_id: str | None,
        timeout_seconds: int,
    ) -> dict[str, Any]:
        run_id = f"run:{uuid.uuid4().hex}"
        request = {
            "tool": tool,
            "mode": mode,
            "args": args,
            "workspace_id": workspace_id,
            "timeout_seconds": timeout_seconds,
        }

        with db.get_connection(app.state.db_path) as connection:
            _require_workspace_ack_for_run(
                connection=connection,
                mode=mode,
                workspace_id=workspace_id,
            )
            db.create_tool_run(
                connection,
                run_id=run_id,
                tool=tool,
                mode=mode,
                status="running",
                request=request,
            )

        try:
            execution = tools.run_tool(
                tool_id=tool,
                args=args,
                run_id=run_id,
                timeout_seconds=timeout_seconds,
            )
        except ValueError as exc:
            with db.get_connection(app.state.db_path) as connection:
                row = db.update_tool_run(
                    connection,
                    run_id=run_id,
                    status="failed",
                    exit_code=None,
                    finished_at=tools.utc_now(),
                    log_path=None,
                )
            if row is None:
                raise HTTPException(status_code=500, detail="failed to update tool run") from exc
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        with db.get_connection(app.state.db_path) as connection:
            updated = db.update_tool_run(
                connection,
                run_id=run_id,
                status=str(execution["status"]),
                exit_code=execution["exit_code"],
                finished_at=str(execution["finished_at"]),
                log_path=str(execution["log_path"]),
            )
            notification_id = f"notification:{uuid.uuid4().hex}"
            db.create_notification(
                connection,
                notification_id=notification_id,
                channel="system",
                title=f"Tool run {execution['status']}: {tool}",
                body=f"Run {run_id} finished with status {execution['status']}.",
            )
        if updated is None:
            raise HTTPException(status_code=500, detail="failed to update tool run")
        return updated

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/ingest")
    def ingest_artifacts(
        program_registry_path: str = "data/program_registry.json",
        findings_db_path: str = "data/findings_db.json",
        bounty_board_root: str = "bounty_board",
    ) -> dict[str, Any]:
        counts = ingest.ingest_existing_artifacts(
            db_path=app.state.db_path,
            program_registry_path=program_registry_path,
            findings_db_path=findings_db_path,
            bounty_board_root=bounty_board_root,
        )
        return {"ok": True, "counts": counts}

    @app.get("/api/programs")
    def list_programs(
        query: str = "",
        limit: int = Query(default=100, ge=1, le=500),
    ) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_programs(connection, query=query, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/programs/{program_id}")
    def get_program(program_id: str) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            item = db.get_program(connection, program_id)
        if item is None:
            raise HTTPException(status_code=404, detail="program not found")
        return item

    @app.get("/api/findings")
    def list_findings(limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_findings(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/findings/export")
    def export_findings(limit: int = Query(default=1000, ge=1, le=5000)) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_findings(connection, limit=limit)
        return {"findings": [item["raw_json"] for item in items], "count": len(items)}

    @app.post("/api/findings/import")
    def import_findings(payload: FindingsImportInput) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            count = db.upsert_findings(connection, payload.findings, source=payload.source)
        return {"ok": True, "count": count}

    @app.post("/api/findings")
    def create_or_update_finding(payload: FindingInput) -> dict[str, Any]:
        finding = payload.model_dump()
        finding.update(payload.extra)
        with db.get_connection(app.state.db_path) as connection:
            item = db.upsert_finding(connection, finding, source="command_center_api")
        return item

    @app.delete("/api/findings/{finding_id}")
    def delete_finding(finding_id: str) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            deleted = db.delete_finding(connection, finding_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="finding not found")
        return {"ok": True}

    @app.get("/api/workspaces")
    def list_workspaces(limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_workspaces(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.post("/api/workspaces")
    def create_workspace(payload: WorkspaceInput) -> dict[str, Any]:
        workspace_id = f"workspace:{payload.platform}:{payload.slug}"
        workspace_data = payload.model_dump()
        workspace_data["id"] = workspace_id
        workspace_data["roe_acknowledged"] = False
        if payload.scaffold_files:
            scaffolded = workspace.scaffold_workspace_files(
                platform=payload.platform,
                slug=payload.slug,
                engagement_url=payload.engagement_url or "",
                out_root=payload.root_dir or "output/engagements",
                force=payload.force,
            )
            workspace_data["root_dir"] = scaffolded["root_dir"]
        with db.get_connection(app.state.db_path) as connection:
            item = db.upsert_workspace(connection, workspace_data)
        return item

    @app.get("/api/workspaces/{workspace_id}")
    def get_workspace(workspace_id: str) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            item = db.get_workspace(connection, workspace_id)
        if item is None:
            raise HTTPException(status_code=404, detail="workspace not found")
        return item

    @app.post("/api/workspaces/{workspace_id}/ack")
    def acknowledge_workspace(workspace_id: str, payload: WorkspaceAckInput) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            item = db.acknowledge_workspace(
                connection,
                workspace_id=workspace_id,
                acknowledged_by=payload.acknowledged_by,
                authorized_target=payload.authorized_target,
            )
        if item is None:
            raise HTTPException(status_code=404, detail="workspace not found")
        root_dir = str(item.get("root_dir") or "").strip()
        if root_dir:
            workspace.write_roe_ack_file(
                workspace_dir=root_dir,
                acknowledged_at=str(item.get("acknowledged_at") or ""),
                acknowledged_by=payload.acknowledged_by,
                authorized_target=payload.authorized_target,
            )
        return item

    @app.get("/api/tools")
    def list_tools() -> dict[str, Any]:
        items = tools.list_tools()
        return {"items": items, "count": len(items)}

    @app.get("/api/runs")
    def list_runs(limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_tool_runs(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            item = db.get_tool_run(connection, run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="run not found")
        return item

    @app.get("/api/runs/{run_id}/log")
    def get_run_log(
        run_id: str,
        tail_lines: int = Query(default=200, ge=1, le=2000),
    ) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            item = db.get_tool_run(connection, run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="run not found")
        log_path = str(item.get("log_path") or "").strip()
        content = tools.read_log_tail(log_path, tail_lines=tail_lines) if log_path else ""
        return {"run_id": run_id, "log_path": log_path, "content": content}

    @app.post("/api/runs")
    def create_run(payload: ToolRunInput) -> dict[str, Any]:
        run_id = f"run:{uuid.uuid4().hex}"
        request = payload.model_dump()
        with db.get_connection(app.state.db_path) as connection:
            _require_workspace_ack_for_run(
                connection=connection,
                mode=payload.mode,
                workspace_id=payload.workspace_id,
            )
            item = db.create_tool_run(
                connection,
                run_id=run_id,
                tool=payload.tool,
                mode=payload.mode,
                status="queued",
                request=request,
            )
        return item

    @app.post("/api/runs/execute")
    def execute_run(payload: ToolExecuteInput) -> dict[str, Any]:
        return _execute_tool_run(
            tool=payload.tool,
            mode=payload.mode,
            args=payload.args,
            workspace_id=payload.workspace_id,
            timeout_seconds=payload.timeout_seconds,
        )

    @app.post("/api/reports/bundle")
    def generate_report_bundle(payload: ReportBundleInput) -> dict[str, Any]:
        args = [
            "--findings",
            payload.findings_path,
            "--target-profile",
            payload.target_profile_path,
            "--output-dir",
            payload.output_dir,
        ]
        if payload.evidence_path:
            args.extend(["--evidence", payload.evidence_path])
        if payload.repro_steps_path:
            args.extend(["--repro-steps", payload.repro_steps_path])
        run = _execute_tool_run(
            tool="scripts.report_bundle",
            mode="plan",
            args=args,
            workspace_id=payload.workspace_id,
            timeout_seconds=payload.timeout_seconds,
        )
        output_dir = Path(payload.output_dir)
        files = []
        if output_dir.exists():
            files = [path.as_posix() for path in sorted(output_dir.glob("*")) if path.is_file()]
        return {"run": run, "output_dir": output_dir.as_posix(), "files": files}

    @app.post("/api/reports/issue-drafts")
    def generate_issue_drafts(payload: IssueDraftInput) -> dict[str, Any]:
        args = [
            "--findings",
            payload.findings_path,
            "--target-profile",
            payload.target_profile_path,
            "--output-dir",
            payload.output_dir,
            "--platform",
            payload.platform,
        ]
        if payload.attachments_manifest_path:
            args.extend(["--attachments-manifest", payload.attachments_manifest_path])
        run = _execute_tool_run(
            tool="scripts.export_issue_drafts",
            mode="plan",
            args=args,
            workspace_id=payload.workspace_id,
            timeout_seconds=payload.timeout_seconds,
        )
        output_dir = Path(payload.output_dir)
        files = []
        if output_dir.exists():
            files = [path.as_posix() for path in sorted(output_dir.glob("*")) if path.is_file()]
        return {"run": run, "output_dir": output_dir.as_posix(), "files": files}

    @app.get("/api/notifications")
    def list_notifications(
        limit: int = Query(default=200, ge=1, le=1000),
        unread_only: bool = False,
    ) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_notifications(connection, limit=limit, unread_only=unread_only)
        return {"items": items, "count": len(items)}

    @app.post("/api/notifications")
    def create_notification(payload: NotificationInput) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            item = db.create_notification(
                connection,
                notification_id=f"notification:{uuid.uuid4().hex}",
                channel=payload.channel,
                title=payload.title,
                body=payload.body,
            )
        return item

    @app.post("/api/notifications/{notification_id}/read")
    def set_notification_read(
        notification_id: str,
        payload: NotificationReadInput,
    ) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            item = db.mark_notification_read(
                connection,
                notification_id=notification_id,
                read=payload.read,
            )
        if item is None:
            raise HTTPException(status_code=404, detail="notification not found")
        return item

    @app.get("/api/docs/search")
    def search_docs(
        query: str = "",
        limit: int = Query(default=25, ge=1, le=100),
    ) -> dict[str, Any]:
        items = docs_search.search_docs(query, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/docs/page")
    def get_doc_page(path: str) -> dict[str, Any]:
        try:
            return docs_search.read_doc_page(path)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app


app = create_app()
