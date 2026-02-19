from __future__ import annotations

import uuid
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from command_center_api import (
    auth,
    compliance,
    db,
    docs_search,
    ingest,
    integrations,
    job_runner,
    notify_channels,
    plugin_sdk,
    secrets_store,
    tools,
    visualization,
    workspace,
)


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


class ConnectorSyncInput(BaseModel):
    limit: int = Field(default=100, ge=1, le=500)
    fixtures_dir: str | None = None


class BugcrowdProgramSyncInput(BaseModel):
    token: str | None = None
    limit: int = Field(default=100, ge=1, le=500)


class BugcrowdSubmissionSyncInput(BaseModel):
    token: str | None = None
    since: str | None = None
    cursor: str | None = None
    limit: int = Field(default=100, ge=1, le=200)


class GithubSyncInput(BaseModel):
    repo: str = Field(min_length=3)
    token: str | None = None
    state: str = "open"
    limit: int = Field(default=100, ge=1, le=500)


class TaskInput(BaseModel):
    title: str = Field(min_length=1)
    status: str = Field(default="open")
    linked_program_id: str | None = None
    linked_finding_id: str | None = None


class TaskUpdateInput(BaseModel):
    title: str | None = None
    status: str | None = None
    linked_program_id: str | None = None
    linked_finding_id: str | None = None


class NotificationSendInput(BaseModel):
    channel: str = Field(min_length=1)
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    slack_webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_from: str | None = None
    smtp_to: str | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True


class MetricsComputeInput(BaseModel):
    scope: str = "global"


class OrganizationInput(BaseModel):
    id: str | None = None
    name: str = Field(min_length=1)


class PrincipalInput(BaseModel):
    id: str | None = None
    email: str | None = None
    display_name: str | None = None
    oidc_sub: str | None = None
    org_id: str = Field(default="org:default")
    role: str = Field(default="viewer")


class RoleBindingInput(BaseModel):
    org_id: str = Field(min_length=1)
    principal_id: str = Field(min_length=1)
    role: str = Field(min_length=1)
    scope: str = Field(default="global")


class TeamInput(BaseModel):
    id: str | None = None
    org_id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class TeamMemberInput(BaseModel):
    team_id: str = Field(min_length=1)
    principal_id: str = Field(min_length=1)
    role: str = Field(default="member", min_length=1)


class OidcTokenInput(BaseModel):
    id_token: str = Field(min_length=8)
    org_id: str = Field(default="org:default")


class SecretResolveInput(BaseModel):
    ref: str = Field(min_length=1)
    file_path: str | None = None
    reveal: bool = False


class SecretRotationPlanInput(BaseModel):
    items: list[dict[str, Any]]


class ComplianceExportInput(BaseModel):
    output_dir: str = Field(default="output/compliance")


class JobEnqueueInput(BaseModel):
    kind: str = Field(default="tool_run")
    idempotency_key: str | None = None
    payload: dict[str, Any]
    max_attempts: int = Field(default=3, ge=1, le=10)


def create_app(*, db_path: Path | str = db.DEFAULT_DB_PATH) -> FastAPI:
    app = FastAPI(
        title="Command Center API",
        version="0.1.0",
        description=(
            "MVP backend for command-center planning and reporting workflows. "
            "Provides REST resources for programs, findings, workspaces, tool runs, and docs search."
        ),
    )
    cors_env = os.getenv(
        "CC_CORS_ORIGINS",
        ",".join(
            [
                "http://127.0.0.1:4173",
                "http://localhost:4173",
                "http://127.0.0.1:5173",
                "http://localhost:5173",
            ]
        ),
    )
    raw_origins = [item.strip() for item in cors_env.split(",") if item.strip()]
    allow_origins = ["*"] if "*" in raw_origins else raw_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.db_path = Path(db_path)
    db.init_schema(app.state.db_path)

    def _extract_bearer_token(request: Request) -> str | None:
        auth_header = request.headers.get("authorization", "").strip()
        if not auth_header.lower().startswith("bearer "):
            return None
        return auth_header.split(" ", 1)[1].strip()

    def _session_context(request: Request) -> dict[str, Any] | None:
        token = _extract_bearer_token(request)
        if not token:
            return None
        with db.get_connection(app.state.db_path) as connection:
            return auth.get_session_context(connection, token)

    def _count_rows(table: str) -> int:
        with db.get_connection(app.state.db_path) as connection:
            return int(connection.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"])

    def _bootstrap_mode() -> bool:
        return _count_rows("principals") == 0

    def _actor_from_context(context: dict[str, Any] | None) -> str:
        if context and isinstance(context.get("principal"), dict):
            value = str(context["principal"].get("id") or "").strip()
            if value:
                return value
        return "system"

    def _require_roles(
        request: Request,
        allowed_roles: set[str],
        *,
        org_id: str | None = None,
    ) -> dict[str, Any]:
        context = _session_context(request)
        context_org_id = org_id
        if context_org_id is None and context is not None:
            context_org_id = str(context.get("org_id") or "").strip() or None
        try:
            auth.ensure_roles(context, allowed_roles, org_id=context_org_id)
        except PermissionError as exc:
            detail = str(exc)
            status_code = 401 if detail == "authentication required" else 403
            raise HTTPException(status_code=status_code, detail=detail) from exc
        if context is None:
            raise HTTPException(status_code=401, detail="authentication required")
        return context

    def _audit_event(
        connection: Any,
        *,
        event_type: str,
        actor: str,
        payload: dict[str, Any],
    ) -> None:
        db.add_audit_event(
            connection,
            event_id=f"audit:{uuid.uuid4().hex}",
            event_type=event_type,
            actor=actor,
            payload=payload,
        )

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

    def _run_connector_job(
        *,
        connector_name: str,
        job: Any,
    ) -> dict[str, Any]:
        run_id = f"connector:{uuid.uuid4().hex}"
        with db.get_connection(app.state.db_path) as connection:
            db.create_connector_run(
                connection,
                run_id=run_id,
                connector=connector_name,
                status="running",
                summary={},
            )
        try:
            with db.get_connection(app.state.db_path) as connection:
                summary = job(connection)
        except RuntimeError as exc:
            with db.get_connection(app.state.db_path) as connection:
                db.finish_connector_run(
                    connection,
                    run_id=run_id,
                    status="failed",
                    summary={"error": str(exc)},
                )
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        with db.get_connection(app.state.db_path) as connection:
            finished = db.finish_connector_run(
                connection,
                run_id=run_id,
                status="completed",
                summary=summary,
            )
        if finished is None:
            raise HTTPException(status_code=500, detail="failed to finalize connector run")
        return {"run": finished, "summary": summary}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/ingest")
    def ingest_artifacts(
        request: Request,
        program_registry_path: str = "data/program_registry.json",
        findings_db_path: str = "data/findings_db.json",
        bounty_board_root: str = "bounty_board",
    ) -> dict[str, Any]:
        context = _require_roles(request, {"admin"})
        counts = ingest.ingest_existing_artifacts(
            db_path=app.state.db_path,
            program_registry_path=program_registry_path,
            findings_db_path=findings_db_path,
            bounty_board_root=bounty_board_root,
        )
        with db.get_connection(app.state.db_path) as connection:
            _audit_event(
                connection,
                event_type="ingest.run",
                actor=str(context["principal"]["id"]),
                payload={"counts": counts},
            )
        return {"ok": True, "counts": counts}

    @app.post("/api/auth/orgs")
    def create_org(payload: OrganizationInput, request: Request) -> dict[str, Any]:
        context: dict[str, Any] | None = None
        if not _bootstrap_mode():
            context = _require_roles(request, {"admin"})
        org_id = payload.id or f"org:{uuid.uuid4().hex}"
        with db.get_connection(app.state.db_path) as connection:
            item = db.upsert_organization(connection, org_id=org_id, name=payload.name)
            _audit_event(
                connection,
                event_type="auth.org.create",
                actor=_actor_from_context(context),
                payload={"org_id": org_id, "name": payload.name},
            )
        return item

    @app.get("/api/auth/orgs")
    def list_orgs(request: Request, limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_organizations(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.post("/api/auth/principals")
    def create_principal(payload: PrincipalInput, request: Request) -> dict[str, Any]:
        context: dict[str, Any] | None = None
        if not _bootstrap_mode():
            context = _require_roles(request, {"admin"})
        principal_id = payload.id or f"user:{uuid.uuid4().hex}"
        with db.get_connection(app.state.db_path) as connection:
            org = connection.execute(
                "SELECT id FROM organizations WHERE id = ?",
                (payload.org_id,),
            ).fetchone()
            if org is None:
                org_name = payload.org_id.replace("org:", "").replace("_", " ").strip() or payload.org_id
                db.upsert_organization(connection, org_id=payload.org_id, name=org_name.title())
            principal = db.upsert_principal(
                connection,
                principal_id=principal_id,
                email=payload.email,
                display_name=payload.display_name,
                oidc_sub=payload.oidc_sub,
            )
            db.upsert_role_binding(
                connection,
                binding_id=f"role:{uuid.uuid4().hex}",
                org_id=payload.org_id,
                principal_id=principal_id,
                role=payload.role,
                scope="global",
            )
            _audit_event(
                connection,
                event_type="auth.principal.create",
                actor=_actor_from_context(context),
                payload={"principal_id": principal_id, "org_id": payload.org_id, "role": payload.role},
            )
        return principal

    @app.get("/api/auth/principals")
    def list_principals(request: Request, limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        _require_roles(request, {"admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_principals(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.post("/api/auth/roles")
    def grant_role(payload: RoleBindingInput, request: Request) -> dict[str, Any]:
        context: dict[str, Any] | None = None
        if not _bootstrap_mode():
            context = _require_roles(request, {"admin"}, org_id=payload.org_id)
        with db.get_connection(app.state.db_path) as connection:
            item = db.upsert_role_binding(
                connection,
                binding_id=f"role:{uuid.uuid4().hex}",
                org_id=payload.org_id,
                principal_id=payload.principal_id,
                role=payload.role,
                scope=payload.scope,
            )
            _audit_event(
                connection,
                event_type="auth.role.grant",
                actor=_actor_from_context(context),
                payload={
                    "org_id": payload.org_id,
                    "principal_id": payload.principal_id,
                    "role": payload.role,
                    "scope": payload.scope,
                },
            )
        return item

    @app.get("/api/auth/roles")
    def list_roles(
        request: Request,
        org_id: str | None = None,
        principal_id: str | None = None,
        limit: int = Query(default=500, ge=1, le=2000),
    ) -> dict[str, Any]:
        _require_roles(request, {"admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_role_bindings(
                connection,
                org_id=org_id,
                principal_id=principal_id,
                limit=limit,
            )
        return {"items": items, "count": len(items)}

    @app.post("/api/auth/teams")
    def create_team(payload: TeamInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"admin"}, org_id=payload.org_id)
        team_id = payload.id or f"team:{uuid.uuid4().hex}"
        with db.get_connection(app.state.db_path) as connection:
            item = db.upsert_team(
                connection,
                team_id=team_id,
                org_id=payload.org_id,
                name=payload.name,
            )
            _audit_event(
                connection,
                event_type="auth.team.create",
                actor=_actor_from_context(context),
                payload={"team_id": item["id"], "org_id": payload.org_id, "name": payload.name},
            )
        return item

    @app.get("/api/auth/teams")
    def list_teams(
        request: Request,
        org_id: str | None = None,
        limit: int = Query(default=200, ge=1, le=1000),
    ) -> dict[str, Any]:
        context = _require_roles(request, {"viewer", "operator", "admin"})
        target_org = org_id or str(context.get("org_id") or "")
        if not target_org:
            raise HTTPException(status_code=400, detail="org_id is required")
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_teams(connection, org_id=target_org, limit=limit)
        return {"items": items, "count": len(items)}

    @app.post("/api/auth/teams/members")
    def add_team_member(payload: TeamMemberInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"admin"})
        with db.get_connection(app.state.db_path) as connection:
            team = db.get_team(connection, payload.team_id)
            if team is None:
                raise HTTPException(status_code=404, detail="team not found")
            _require_roles(request, {"admin"}, org_id=str(team["org_id"]))
            item = db.upsert_team_member(
                connection,
                member_id=f"teammember:{uuid.uuid4().hex}",
                team_id=payload.team_id,
                principal_id=payload.principal_id,
                role=payload.role,
            )
            _audit_event(
                connection,
                event_type="auth.team.member.upsert",
                actor=_actor_from_context(context),
                payload={
                    "team_id": payload.team_id,
                    "principal_id": payload.principal_id,
                    "role": payload.role,
                },
            )
        return item

    @app.get("/api/auth/teams/{team_id}/members")
    def list_team_members(
        team_id: str,
        request: Request,
        limit: int = Query(default=500, ge=1, le=2000),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            team = db.get_team(connection, team_id)
            if team is None:
                raise HTTPException(status_code=404, detail="team not found")
            items = db.list_team_members(connection, team_id=team_id, limit=limit)
        return {"items": items, "count": len(items)}

    @app.post("/api/auth/oidc/token")
    def oidc_token_exchange(payload: OidcTokenInput) -> dict[str, Any]:
        try:
            claims = auth.parse_oidc_assertion(
                id_token=payload.id_token,
                expected_issuer=os.getenv("OIDC_EXPECTED_ISSUER"),
                expected_audience=os.getenv("OIDC_EXPECTED_AUDIENCE"),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        subject = str(claims.get("sub"))
        email = str(claims.get("email") or "") or None
        display_name = str(claims.get("name") or claims.get("preferred_username") or "") or None
        principal_id = f"oidc:{subject}"
        with db.get_connection(app.state.db_path) as connection:
            org = connection.execute(
                "SELECT id FROM organizations WHERE id = ?",
                (payload.org_id,),
            ).fetchone()
            if org is None:
                db.upsert_organization(
                    connection,
                    org_id=payload.org_id,
                    name=(payload.org_id.replace("org:", "") or payload.org_id).replace("_", " ").title(),
                )
            db.upsert_principal(
                connection,
                principal_id=principal_id,
                email=email,
                display_name=display_name,
                oidc_sub=subject,
            )
            bindings = db.list_role_bindings_for_principal(
                connection,
                principal_id=principal_id,
                org_id=payload.org_id,
            )
            if not bindings:
                db.upsert_role_binding(
                    connection,
                    binding_id=f"role:{uuid.uuid4().hex}",
                    org_id=payload.org_id,
                    principal_id=principal_id,
                    role="viewer",
                    scope="global",
                )
            token = auth.issue_session_token(
                connection,
                principal_id=principal_id,
                org_id=payload.org_id,
                ttl_seconds=int(os.getenv("CC_SESSION_TTL_SECONDS") or 3600),
            )
            context = auth.get_session_context(connection, str(token["access_token"]))
            _audit_event(
                connection,
                event_type="auth.oidc.exchange",
                actor=principal_id,
                payload={"principal_id": principal_id, "org_id": payload.org_id},
            )
        return {"token": token, "context": context}

    @app.get("/api/auth/context")
    def auth_context(request: Request) -> dict[str, Any]:
        context = _session_context(request)
        if context is None:
            raise HTTPException(status_code=401, detail="authentication required")
        return context

    @app.get("/api/auth/sessions")
    def list_sessions(
        request: Request,
        principal_id: str | None = None,
        limit: int = Query(default=20, ge=1, le=200),
    ) -> dict[str, Any]:
        context = _require_roles(request, {"viewer", "operator", "admin"})
        current_principal_id = str(context["principal"]["id"])
        target_principal = principal_id or current_principal_id
        if target_principal != current_principal_id:
            _require_roles(request, {"admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_sessions_for_principal(
                connection,
                principal_id=target_principal,
                limit=limit,
            )
        return {"items": items, "count": len(items)}

    @app.delete("/api/auth/sessions/current")
    def revoke_current_session(request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"viewer", "operator", "admin"})
        session_id = str(context["session"]["id"])
        with db.get_connection(app.state.db_path) as connection:
            deleted = db.delete_session(connection, session_id)
            _audit_event(
                connection,
                event_type="auth.session.revoke",
                actor=str(context["principal"]["id"]),
                payload={"session_id": session_id},
            )
        if not deleted:
            raise HTTPException(status_code=404, detail="session not found")
        return {"ok": True}

    @app.get("/api/programs")
    def list_programs(
        request: Request,
        query: str = "",
        limit: int = Query(default=100, ge=1, le=500),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_programs(connection, query=query, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/programs/{program_id}")
    def get_program(program_id: str, request: Request) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            item = db.get_program(connection, program_id)
        if item is None:
            raise HTTPException(status_code=404, detail="program not found")
        return item

    @app.get("/api/findings")
    def list_findings(
        request: Request,
        limit: int = Query(default=200, ge=1, le=1000),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_findings(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/findings/export")
    def export_findings(
        request: Request,
        limit: int = Query(default=1000, ge=1, le=5000),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_findings(connection, limit=limit)
        return {"findings": [item["raw_json"] for item in items], "count": len(items)}

    @app.post("/api/findings/import")
    def import_findings(payload: FindingsImportInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            count = db.upsert_findings(connection, payload.findings, source=payload.source)
            _audit_event(
                connection,
                event_type="findings.import",
                actor=str(context["principal"]["id"]),
                payload={"source": payload.source, "count": count},
            )
        return {"ok": True, "count": count}

    @app.post("/api/findings")
    def create_or_update_finding(payload: FindingInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        finding = payload.model_dump()
        finding.update(payload.extra)
        with db.get_connection(app.state.db_path) as connection:
            item = db.upsert_finding(connection, finding, source="command_center_api")
            _audit_event(
                connection,
                event_type="finding.upsert",
                actor=str(context["principal"]["id"]),
                payload={"finding_id": item["id"]},
            )
        return item

    @app.delete("/api/findings/{finding_id}")
    def delete_finding(finding_id: str, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            deleted = db.delete_finding(connection, finding_id)
            if deleted:
                _audit_event(
                    connection,
                    event_type="finding.delete",
                    actor=str(context["principal"]["id"]),
                    payload={"finding_id": finding_id},
                )
        if not deleted:
            raise HTTPException(status_code=404, detail="finding not found")
        return {"ok": True}

    @app.get("/api/workspaces")
    def list_workspaces(
        request: Request,
        limit: int = Query(default=200, ge=1, le=1000),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_workspaces(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.post("/api/workspaces")
    def create_workspace(payload: WorkspaceInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
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
            _audit_event(
                connection,
                event_type="workspace.create",
                actor=str(context["principal"]["id"]),
                payload={"workspace_id": workspace_id},
            )
        return item

    @app.get("/api/workspaces/{workspace_id}")
    def get_workspace(workspace_id: str, request: Request) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            item = db.get_workspace(connection, workspace_id)
        if item is None:
            raise HTTPException(status_code=404, detail="workspace not found")
        return item

    @app.post("/api/workspaces/{workspace_id}/ack")
    def acknowledge_workspace(
        workspace_id: str,
        payload: WorkspaceAckInput,
        request: Request,
    ) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            item = db.acknowledge_workspace(
                connection,
                workspace_id=workspace_id,
                acknowledged_by=payload.acknowledged_by,
                authorized_target=payload.authorized_target,
            )
            if item is not None:
                _audit_event(
                    connection,
                    event_type="workspace.ack",
                    actor=str(context["principal"]["id"]),
                    payload={"workspace_id": workspace_id},
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

    @app.get("/api/tasks")
    def list_tasks(request: Request, limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_tasks(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/tasks/board")
    def task_board(request: Request, limit: int = Query(default=500, ge=1, le=1000)) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_tasks(connection, limit=limit)
        columns = {"open": [], "in_progress": [], "blocked": [], "done": []}
        for task in items:
            status = str(task.get("status") or "open").strip().lower()
            if status not in columns:
                status = "open"
            columns[status].append(task)
        return {"columns": columns, "count": len(items)}

    @app.post("/api/tasks")
    def create_task(payload: TaskInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        task_id = f"task:{uuid.uuid4().hex}"
        with db.get_connection(app.state.db_path) as connection:
            item = db.upsert_task(
                connection,
                {
                    "id": task_id,
                    "title": payload.title,
                    "status": payload.status,
                    "linked_program_id": payload.linked_program_id,
                    "linked_finding_id": payload.linked_finding_id,
                },
            )
            _audit_event(
                connection,
                event_type="task.create",
                actor=str(context["principal"]["id"]),
                payload={"task_id": task_id},
            )
        return item

    @app.patch("/api/tasks/{task_id}")
    def update_task(task_id: str, payload: TaskUpdateInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            existing = db.get_task(connection, task_id)
            if existing is None:
                raise HTTPException(status_code=404, detail="task not found")
            next_task = dict(existing)
            patch_data = payload.model_dump(exclude_none=True)
            next_task.update(patch_data)
            item = db.upsert_task(connection, next_task)
            _audit_event(
                connection,
                event_type="task.update",
                actor=str(context["principal"]["id"]),
                payload={"task_id": task_id},
            )
        return item

    @app.delete("/api/tasks/{task_id}")
    def delete_task(task_id: str, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            deleted = db.delete_task(connection, task_id)
            if deleted:
                _audit_event(
                    connection,
                    event_type="task.delete",
                    actor=str(context["principal"]["id"]),
                    payload={"task_id": task_id},
                )
        if not deleted:
            raise HTTPException(status_code=404, detail="task not found")
        return {"ok": True}

    @app.post("/api/tasks/auto-link")
    def auto_link_tasks(request: Request, limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        created = 0
        with db.get_connection(app.state.db_path) as connection:
            findings = db.list_findings(connection, limit=limit)
            tasks = db.list_tasks(connection, limit=5000)
            task_ids = {item["id"] for item in tasks}
            for finding in findings:
                task_id = f"task:finding:{finding['id']}"
                if task_id in task_ids:
                    continue
                db.upsert_task(
                    connection,
                    {
                        "id": task_id,
                        "title": f"Review finding: {finding['title']}",
                        "status": "open",
                        "linked_finding_id": finding["id"],
                    },
                )
                created += 1
            if created:
                _audit_event(
                    connection,
                    event_type="task.auto_link",
                    actor=str(context["principal"]["id"]),
                    payload={"created": created},
                )
        return {"ok": True, "created": created}

    @app.post("/api/connectors/bugcrowd/programs/sync")
    def sync_bugcrowd_programs(payload: BugcrowdProgramSyncInput, request: Request) -> dict[str, Any]:
        _require_roles(request, {"operator", "admin"})
        client_ip = request.client.host if request.client else "unknown"
        return _run_connector_job(
            connector_name="bugcrowd_programs",
            job=lambda connection: integrations.sync_bugcrowd_programs(
                connection=connection,
                token=payload.token or os.getenv("BUGCROWD_API_TOKEN"),
                client_ip=client_ip,
                limit=payload.limit,
            ),
        )

    @app.post("/api/connectors/bugcrowd/submissions/sync")
    def sync_bugcrowd_submissions(payload: BugcrowdSubmissionSyncInput, request: Request) -> dict[str, Any]:
        _require_roles(request, {"operator", "admin"})
        client_ip = request.client.host if request.client else "unknown"
        return _run_connector_job(
            connector_name="bugcrowd_submissions",
            job=lambda connection: integrations.sync_bugcrowd_submissions(
                connection=connection,
                token=payload.token or os.getenv("BUGCROWD_API_TOKEN"),
                client_ip=client_ip,
                since=payload.since,
                cursor=payload.cursor,
                limit=payload.limit,
            ),
        )

    @app.post("/api/connectors/bugcrowd/webhook")
    async def bugcrowd_webhook(request: Request) -> dict[str, Any]:
        raw_body = await request.body()
        signature = request.headers.get("x-bugcrowd-signature")
        secret = os.getenv("BUGCROWD_WEBHOOK_SECRET")
        if not integrations.verify_webhook_signature(
            payload_raw=raw_body,
            signature_header=signature,
            secret=secret,
        ):
            raise HTTPException(status_code=401, detail="invalid webhook signature")

        payload = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="webhook payload must be a JSON object")
        event_type = str(payload.get("event_type") or payload.get("event") or "bugcrowd.webhook")
        submission = payload.get("submission")
        status_updates = 0
        with db.get_connection(app.state.db_path) as connection:
            db.add_audit_event(
                connection,
                event_id=f"audit:{uuid.uuid4().hex}",
                event_type=event_type,
                actor="bugcrowd_webhook",
                payload=payload,
            )
            if isinstance(submission, dict):
                submission_id = str(submission.get("id") or "").strip()
                status = str(submission.get("status") or submission.get("state") or "unknown").strip()
                if submission_id:
                    db.add_submission_status_event(
                        connection,
                        event_id=f"bugcrowd:{submission_id}:{status}",
                        platform="bugcrowd",
                        submission_id=submission_id,
                        status=status,
                        payload=submission,
                    )
                    db.create_notification(
                        connection,
                        notification_id=f"notification:{uuid.uuid4().hex}",
                        channel="bugcrowd",
                        title=f"Bugcrowd submission update: {submission_id}",
                        body=f"Submission status is now {status}.",
                    )
                    status_updates = 1
        return {"ok": True, "event_type": event_type, "status_updates": status_updates}

    @app.post("/api/connectors/github/issues/sync")
    def sync_github_issues(payload: GithubSyncInput, request: Request) -> dict[str, Any]:
        _require_roles(request, {"operator", "admin"})
        return _run_connector_job(
            connector_name="github_issues",
            job=lambda connection: integrations.sync_github_issues(
                connection=connection,
                repo=payload.repo,
                token=payload.token or os.getenv("GITHUB_TOKEN"),
                state=payload.state,
                limit=payload.limit,
            ),
        )

    @app.post("/api/connectors/github/webhook")
    async def github_webhook(request: Request) -> dict[str, Any]:
        raw_body = await request.body()
        signature = request.headers.get("x-hub-signature-256")
        secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not integrations.verify_webhook_signature(
            payload_raw=raw_body,
            signature_header=signature,
            secret=secret,
        ):
            raise HTTPException(status_code=401, detail="invalid webhook signature")

        payload = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="webhook payload must be a JSON object")
        event_type = request.headers.get("x-github-event", "github.webhook")
        issue = payload.get("issue")
        task_id = ""
        with db.get_connection(app.state.db_path) as connection:
            db.add_audit_event(
                connection,
                event_id=f"audit:{uuid.uuid4().hex}",
                event_type=event_type,
                actor="github_webhook",
                payload=payload,
            )
            if isinstance(issue, dict):
                number = issue.get("number")
                title = str(issue.get("title") or "").strip()
                state_value = str(issue.get("state") or "open").strip().lower()
                repository = payload.get("repository")
                if isinstance(repository, dict):
                    repo_name = str(repository.get("full_name") or "unknown/repo")
                else:
                    repo_name = "unknown/repo"
                if number and title:
                    task_id = f"github:{repo_name}:{number}"
                    db.upsert_task(
                        connection,
                        {
                            "id": task_id,
                            "title": title,
                            "status": state_value,
                        },
                    )
                    db.create_notification(
                        connection,
                        notification_id=f"notification:{uuid.uuid4().hex}",
                        channel="github",
                        title=f"GitHub issue event: {repo_name}#{number}",
                        body=f"Issue status: {state_value}.",
                    )
        return {"ok": True, "event_type": event_type, "task_id": task_id}

    @app.post("/api/connectors/intigriti/sync")
    def sync_intigriti(payload: ConnectorSyncInput, request: Request) -> dict[str, Any]:
        _require_roles(request, {"operator", "admin"})
        return _run_connector_job(
            connector_name="intigriti",
            job=lambda connection: integrations.sync_public_connector(
                connection=connection,
                connector_name="intigriti",
                fixtures_dir=payload.fixtures_dir,
                limit=payload.limit,
            ),
        )

    @app.post("/api/connectors/yeswehack/sync")
    def sync_yeswehack(payload: ConnectorSyncInput, request: Request) -> dict[str, Any]:
        _require_roles(request, {"operator", "admin"})
        return _run_connector_job(
            connector_name="yeswehack",
            job=lambda connection: integrations.sync_public_connector(
                connection=connection,
                connector_name="yeswehack",
                fixtures_dir=payload.fixtures_dir,
                limit=payload.limit,
            ),
        )

    @app.get("/api/tools")
    def list_tools(request: Request) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        items = tools.list_tools()
        return {"items": items, "count": len(items)}

    @app.get("/api/runs")
    def list_runs(
        request: Request,
        limit: int = Query(default=200, ge=1, le=1000),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_tool_runs(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str, request: Request) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            item = db.get_tool_run(connection, run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="run not found")
        return item

    @app.get("/api/runs/{run_id}/log")
    def get_run_log(
        run_id: str,
        request: Request,
        tail_lines: int = Query(default=200, ge=1, le=2000),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            item = db.get_tool_run(connection, run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="run not found")
        log_path = str(item.get("log_path") or "").strip()
        content = tools.read_log_tail(log_path, tail_lines=tail_lines) if log_path else ""
        return {"run_id": run_id, "log_path": log_path, "content": content}

    @app.post("/api/runs")
    def create_run(payload: ToolRunInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        run_id = f"run:{uuid.uuid4().hex}"
        request_payload = payload.model_dump()
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
                request=request_payload,
            )
            _audit_event(
                connection,
                event_type="run.create",
                actor=str(context["principal"]["id"]),
                payload={"run_id": run_id, "tool": payload.tool},
            )
        return item

    @app.post("/api/runs/execute")
    def execute_run(payload: ToolExecuteInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        run = _execute_tool_run(
            tool=payload.tool,
            mode=payload.mode,
            args=payload.args,
            workspace_id=payload.workspace_id,
            timeout_seconds=payload.timeout_seconds,
        )
        with db.get_connection(app.state.db_path) as connection:
            _audit_event(
                connection,
                event_type="run.execute",
                actor=str(context["principal"]["id"]),
                payload={"tool": payload.tool, "mode": payload.mode},
            )
        return run

    @app.post("/api/reports/bundle")
    def generate_report_bundle(payload: ReportBundleInput, request: Request) -> dict[str, Any]:
        _require_roles(request, {"operator", "admin"})
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
    def generate_issue_drafts(payload: IssueDraftInput, request: Request) -> dict[str, Any]:
        _require_roles(request, {"operator", "admin"})
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
        request: Request,
        limit: int = Query(default=200, ge=1, le=1000),
        unread_only: bool = False,
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_notifications(connection, limit=limit, unread_only=unread_only)
        return {"items": items, "count": len(items)}

    @app.post("/api/notifications")
    def create_notification(payload: NotificationInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            item = db.create_notification(
                connection,
                notification_id=f"notification:{uuid.uuid4().hex}",
                channel=payload.channel,
                title=payload.title,
                body=payload.body,
            )
            _audit_event(
                connection,
                event_type="notification.create",
                actor=str(context["principal"]["id"]),
                payload={"notification_id": item["id"], "channel": payload.channel},
            )
        return item

    @app.post("/api/notifications/send")
    def send_notification(payload: NotificationSendInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        channel = payload.channel.strip().lower()
        if channel == "slack":
            webhook_url = payload.slack_webhook_url or os.getenv("SLACK_WEBHOOK_URL")
            if not webhook_url:
                raise HTTPException(status_code=400, detail="slack webhook url is required")
            result = notify_channels.send_slack(
                webhook_url=webhook_url,
                title=payload.title,
                body=payload.body,
            )
        elif channel in {"smtp", "email"}:
            smtp_host = payload.smtp_host or os.getenv("SMTP_HOST")
            smtp_from = payload.smtp_from or os.getenv("SMTP_FROM")
            smtp_to = payload.smtp_to or os.getenv("SMTP_TO")
            smtp_username = payload.smtp_username or os.getenv("SMTP_USERNAME")
            smtp_password = payload.smtp_password or os.getenv("SMTP_PASSWORD")
            if not smtp_host or not smtp_from or not smtp_to:
                raise HTTPException(
                    status_code=400,
                    detail="smtp_host, smtp_from, and smtp_to are required",
                )
            result = notify_channels.send_smtp(
                host=smtp_host,
                port=payload.smtp_port,
                from_email=smtp_from,
                to_email=smtp_to,
                title=payload.title,
                body=payload.body,
                username=smtp_username,
                password=smtp_password,
                use_tls=payload.smtp_use_tls,
            )
        else:
            raise HTTPException(status_code=400, detail="unsupported notification channel")

        with db.get_connection(app.state.db_path) as connection:
            item = db.create_notification(
                connection,
                notification_id=f"notification:{uuid.uuid4().hex}",
                channel=channel,
                title=payload.title,
                body=payload.body,
            )
            _audit_event(
                connection,
                event_type="notification.send",
                actor=str(context["principal"]["id"]),
                payload={"notification_id": item["id"], "channel": channel},
            )
        return {"ok": True, "channel": channel, "result": result}

    @app.post("/api/notifications/{notification_id}/read")
    def set_notification_read(
        notification_id: str,
        payload: NotificationReadInput,
        request: Request,
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            item = db.mark_notification_read(
                connection,
                notification_id=notification_id,
                read=payload.read,
            )
        if item is None:
            raise HTTPException(status_code=404, detail="notification not found")
        return item

    @app.post("/api/metrics/compute")
    def compute_metrics(payload: MetricsComputeInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        metrics: dict[str, float] = {}
        with db.get_connection(app.state.db_path) as connection:
            metrics["program_count"] = float(
                connection.execute("SELECT COUNT(*) AS n FROM programs").fetchone()["n"]
            )
            metrics["finding_count"] = float(
                connection.execute("SELECT COUNT(*) AS n FROM findings").fetchone()["n"]
            )
            metrics["workspace_count"] = float(
                connection.execute("SELECT COUNT(*) AS n FROM workspaces").fetchone()["n"]
            )
            metrics["task_count"] = float(
                connection.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
            )
            metrics["run_count"] = float(
                connection.execute("SELECT COUNT(*) AS n FROM tool_runs").fetchone()["n"]
            )
            metrics["notification_count"] = float(
                connection.execute("SELECT COUNT(*) AS n FROM notifications").fetchone()["n"]
            )

            snapshot_items = []
            for metric_name, metric_value in metrics.items():
                snapshot_items.append(
                    db.add_metric_snapshot(
                        connection,
                        snapshot_id=f"metric:{uuid.uuid4().hex}",
                        metric_name=metric_name,
                        metric_value=metric_value,
                        scope=payload.scope,
                    )
                )
            _audit_event(
                connection,
                event_type="metrics.compute",
                actor=str(context["principal"]["id"]),
                payload={"scope": payload.scope},
            )
        return {"scope": payload.scope, "metrics": metrics, "snapshots": snapshot_items}

    @app.get("/api/metrics/snapshots")
    def list_metrics_snapshots(
        request: Request,
        scope: str = "global",
        limit: int = Query(default=200, ge=1, le=1000),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_metric_snapshots(connection, scope=scope, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/docs/search")
    def search_docs(
        request: Request,
        query: str = "",
        limit: int = Query(default=25, ge=1, le=100),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        items = docs_search.search_docs(query, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/docs/page")
    def get_doc_page(path: str, request: Request) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        try:
            return docs_search.read_doc_page(path)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/secrets/resolve")
    def resolve_secret(payload: SecretResolveInput, request: Request) -> dict[str, Any]:
        _require_roles(request, {"admin"})
        try:
            value = secrets_store.resolve_secret(payload.ref, file_path=payload.file_path)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        response: dict[str, Any] = {
            "ref": payload.ref,
            "provider": secrets_store.parse_secret_ref(payload.ref)[0],
            "length": len(value),
            "redacted": secrets_store.redact_secret(value),
        }
        if payload.reveal:
            response["value"] = value
        return response

    @app.post("/api/secrets/rotation-plan")
    def build_secret_rotation_plan(payload: SecretRotationPlanInput, request: Request) -> dict[str, Any]:
        _require_roles(request, {"admin"})
        plan = secrets_store.build_rotation_plan(payload.items)
        return {"items": plan, "count": len(plan)}

    @app.post("/api/compliance/export")
    def export_compliance_bundle(payload: ComplianceExportInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"admin"})
        with db.get_connection(app.state.db_path) as connection:
            result = compliance.export_compliance_bundle(
                connection=connection,
                output_dir=payload.output_dir,
            )
            _audit_event(
                connection,
                event_type="compliance.export",
                actor=str(context["principal"]["id"]),
                payload={"output_dir": payload.output_dir},
            )
        return result

    @app.get("/api/compliance/audit-events")
    def list_compliance_audit_events(
        request: Request,
        limit: int = Query(default=500, ge=1, le=5000),
    ) -> dict[str, Any]:
        _require_roles(request, {"admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_audit_events(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/plugins/discover")
    def discover_plugins(
        request: Request,
        plugin_dir: str = "plugins",
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        items = plugin_sdk.discover_plugins(plugin_dir=plugin_dir)
        loaded = sum(1 for item in items if item.get("status") == "loaded")
        errors = [item for item in items if item.get("status") == "error"]
        return {"items": items, "count": len(items), "loaded": loaded, "errors": len(errors)}

    @app.post("/api/jobs")
    def enqueue_job(payload: JobEnqueueInput, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            item = db.enqueue_job(
                connection,
                job_id=f"job:{uuid.uuid4().hex}",
                idempotency_key=payload.idempotency_key,
                kind=payload.kind,
                payload=payload.payload,
                max_attempts=payload.max_attempts,
            )
            _audit_event(
                connection,
                event_type="job.enqueue",
                actor=str(context["principal"]["id"]),
                payload={"job_id": item["id"], "kind": payload.kind},
            )
        return item

    @app.get("/api/jobs")
    def list_jobs(request: Request, limit: int = Query(default=200, ge=1, le=1000)) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            items = db.list_jobs(connection, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: str, request: Request) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            item = db.get_job(connection, job_id)
        if item is None:
            raise HTTPException(status_code=404, detail="job not found")
        return item

    @app.post("/api/jobs/{job_id}/retry")
    def retry_job(job_id: str, request: Request) -> dict[str, Any]:
        context = _require_roles(request, {"operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            try:
                item = db.retry_job(connection, job_id=job_id)
            except ValueError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            if item is None:
                raise HTTPException(status_code=404, detail="job not found")
            _audit_event(
                connection,
                event_type="job.retry",
                actor=str(context["principal"]["id"]),
                payload={"job_id": job_id},
            )
        return item

    @app.post("/api/jobs/worker/start")
    def start_job_worker(request: Request) -> dict[str, Any]:
        _require_roles(request, {"admin"})
        return job_runner.start_worker(app.state.db_path)

    @app.post("/api/jobs/worker/stop")
    def stop_job_worker(request: Request) -> dict[str, Any]:
        _require_roles(request, {"admin"})
        return job_runner.stop_worker()

    @app.get("/api/jobs/worker/status")
    def get_job_worker_status(request: Request) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        return job_runner.worker_status()

    @app.get("/api/visualizations/scope-map")
    def get_scope_map(
        request: Request,
        limit: int = Query(default=200, ge=10, le=500),
    ) -> dict[str, Any]:
        _require_roles(request, {"viewer", "operator", "admin"})
        with db.get_connection(app.state.db_path) as connection:
            return visualization.build_scope_map(connection, limit=limit)

    return app


app = create_app()
