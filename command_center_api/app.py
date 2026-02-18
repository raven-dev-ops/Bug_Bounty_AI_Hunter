from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from command_center_api import db, ingest


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


class WorkspaceInput(BaseModel):
    platform: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    name: str = Field(min_length=1)
    engagement_url: str | None = None
    root_dir: str | None = None


class WorkspaceAckInput(BaseModel):
    acknowledged_by: str = Field(min_length=1)
    authorized_target: str = Field(min_length=1)


class ToolRunInput(BaseModel):
    tool: str = Field(min_length=1)
    mode: str = Field(default="plan", pattern="^(plan|run)$")
    args: list[str] = Field(default_factory=list)
    workspace_id: str | None = None


def create_app(*, db_path: Path | str = db.DEFAULT_DB_PATH) -> FastAPI:
    app = FastAPI(
        title="Command Center API",
        version="0.1.0",
        description=(
            "MVP backend for command-center planning and reporting workflows. "
            "Provides REST resources for programs, findings, workspaces, and tool runs."
        ),
    )
    app.state.db_path = Path(db_path)
    db.init_schema(app.state.db_path)

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

    @app.post("/api/findings")
    def create_or_update_finding(payload: FindingInput) -> dict[str, Any]:
        finding = payload.model_dump()
        finding.update(payload.extra)
        with db.get_connection(app.state.db_path) as connection:
            item = db.upsert_finding(connection, finding, source="command_center_api")
        return item

    @app.get("/api/workspaces")
    def list_workspaces(limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_workspaces(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.post("/api/workspaces")
    def create_workspace(payload: WorkspaceInput) -> dict[str, Any]:
        workspace_id = f"workspace:{payload.platform}:{payload.slug}"
        workspace = payload.model_dump()
        workspace["id"] = workspace_id
        workspace["roe_acknowledged"] = False
        with db.get_connection(app.state.db_path) as connection:
            item = db.upsert_workspace(connection, workspace)
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
        return item

    @app.get("/api/runs")
    def list_runs(limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_tool_runs(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.post("/api/runs")
    def create_run(payload: ToolRunInput) -> dict[str, Any]:
        run_id = f"run:{uuid.uuid4().hex}"
        request = payload.model_dump()
        with db.get_connection(app.state.db_path) as connection:
            item = db.create_tool_run(
                connection,
                run_id=run_id,
                tool=payload.tool,
                mode=payload.mode,
                status="queued",
                request=request,
            )
        return item

    return app


app = create_app()
