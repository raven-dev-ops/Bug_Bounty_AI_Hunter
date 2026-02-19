import base64
import json
import os
import tempfile
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from command_center_api import tools
from command_center_api.app import create_app


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _make_id_token(*, sub: str, email: str) -> str:
    header = _b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode("utf-8"))
    payload = _b64url(
        json.dumps(
            {
                "sub": sub,
                "email": email,
                "exp": int(time.time()) + 3600,
            }
        ).encode("utf-8")
    )
    return f"{header}.{payload}.sig"


class TestCommandCenterApi(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        db_path = Path(self.temp_dir.name) / "command_center_test.db"
        self.client = TestClient(create_app(db_path=db_path))
        self.auth_headers = self._bootstrap_admin_auth()

    def _bootstrap_admin_auth(self) -> dict[str, str]:
        org = self.client.post(
            "/api/auth/orgs",
            json={"id": "org:test", "name": "Test Org"},
        )
        self.assertEqual(org.status_code, 200)
        principal = self.client.post(
            "/api/auth/principals",
            json={
                "id": "oidc:bootstrap-admin",
                "email": "admin@test.local",
                "display_name": "Bootstrap Admin",
                "oidc_sub": "bootstrap-admin",
                "org_id": "org:test",
                "role": "admin",
            },
        )
        self.assertEqual(principal.status_code, 200)
        token_response = self.client.post(
            "/api/auth/oidc/token",
            json={
                "id_token": _make_id_token(
                    sub="bootstrap-admin", email="admin@test.local"
                ),
                "org_id": "org:test",
            },
        )
        self.assertEqual(token_response.status_code, 200)
        token = token_response.json()["token"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_run_mode_requires_roe_acknowledgement(self):
        workspace = self.client.post(
            "/api/workspaces",
            json={
                "platform": "bugcrowd",
                "slug": "unit-test",
                "name": "Unit Test Workspace",
                "root_dir": str(Path(self.temp_dir.name) / "engagements"),
                "scaffold_files": True,
            },
            headers=self.auth_headers,
        )
        self.assertEqual(workspace.status_code, 200)
        workspace_id = workspace.json()["id"]

        blocked = self.client.post(
            "/api/runs",
            json={
                "tool": "scripts.pipeline_orchestrator",
                "mode": "run",
                "workspace_id": workspace_id,
                "args": [],
            },
            headers=self.auth_headers,
        )
        self.assertEqual(blocked.status_code, 403)

        acknowledged = self.client.post(
            f"/api/workspaces/{workspace_id}/ack",
            json={
                "acknowledged_by": "unit-test",
                "authorized_target": "https://example.test",
            },
            headers=self.auth_headers,
        )
        self.assertEqual(acknowledged.status_code, 200)

        unlocked = self.client.post(
            "/api/runs",
            json={
                "tool": "scripts.pipeline_orchestrator",
                "mode": "run",
                "workspace_id": workspace_id,
                "args": [],
            },
            headers=self.auth_headers,
        )
        self.assertEqual(unlocked.status_code, 200)

    def test_execute_rejects_disallowed_tool(self):
        response = self.client.post(
            "/api/runs/execute",
            json={
                "tool": "scripts.not_real",
                "mode": "plan",
                "args": [],
                "timeout_seconds": 60,
            },
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("tool not allowed", response.json()["detail"])

    def test_docs_path_traversal_is_blocked(self):
        response = self.client.get(
            "/api/docs/page",
            params={"path": "../README.md"},
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_findings_import_export_round_trip(self):
        imported = self.client.post(
            "/api/findings/import",
            json={
                "source": "unit-test",
                "findings": [{"id": "finding-001", "title": "Sample"}],
            },
            headers=self.auth_headers,
        )
        self.assertEqual(imported.status_code, 200)
        self.assertEqual(imported.json()["count"], 1)

        exported = self.client.get("/api/findings/export", headers=self.auth_headers)
        self.assertEqual(exported.status_code, 200)
        findings = exported.json()["findings"]
        self.assertTrue(any(item.get("id") == "finding-001" for item in findings))

    def test_task_auto_link_from_findings(self):
        self.client.post(
            "/api/findings/import",
            json={
                "source": "unit-test",
                "findings": [{"id": "finding-auto-001", "title": "Auto link me"}],
            },
            headers=self.auth_headers,
        )
        linked = self.client.post("/api/tasks/auto-link", headers=self.auth_headers)
        self.assertEqual(linked.status_code, 200)
        self.assertGreaterEqual(linked.json()["created"], 1)

        board = self.client.get("/api/tasks/board", headers=self.auth_headers)
        self.assertEqual(board.status_code, 200)
        open_tasks = board.json()["columns"]["open"]
        self.assertTrue(
            any(
                task.get("linked_finding_id") == "finding-auto-001"
                for task in open_tasks
            )
        )

    def test_metrics_compute_and_snapshot_listing(self):
        computed = self.client.post(
            "/api/metrics/compute",
            json={"scope": "global"},
            headers=self.auth_headers,
        )
        self.assertEqual(computed.status_code, 200)
        self.assertIn("program_count", computed.json()["metrics"])

        snapshots = self.client.get(
            "/api/metrics/snapshots",
            params={"scope": "global"},
            headers=self.auth_headers,
        )
        self.assertEqual(snapshots.status_code, 200)
        self.assertGreaterEqual(snapshots.json()["count"], 1)

    def test_notifications_send_rejects_unsupported_channel(self):
        response = self.client.post(
            "/api/notifications/send",
            json={
                "channel": "pager",
                "title": "Unsupported",
                "body": "Unsupported channel",
            },
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("unsupported", response.json()["detail"])

    def test_auth_teams_and_session_endpoints(self):
        team = self.client.post(
            "/api/auth/teams",
            json={"org_id": "org:test", "name": "Operators"},
            headers=self.auth_headers,
        )
        self.assertEqual(team.status_code, 200)
        team_id = team.json()["id"]

        member = self.client.post(
            "/api/auth/teams/members",
            json={
                "team_id": team_id,
                "principal_id": "oidc:bootstrap-admin",
                "role": "lead",
            },
            headers=self.auth_headers,
        )
        self.assertEqual(member.status_code, 200)

        members = self.client.get(
            f"/api/auth/teams/{team_id}/members",
            headers=self.auth_headers,
        )
        self.assertEqual(members.status_code, 200)
        self.assertEqual(members.json()["count"], 1)

        sessions = self.client.get("/api/auth/sessions", headers=self.auth_headers)
        self.assertEqual(sessions.status_code, 200)
        self.assertGreaterEqual(sessions.json()["count"], 1)

    def test_secrets_jobs_plugins_compliance_and_visualization(self):
        old_env_secret = os.environ.get("UNIT_TEST_SECRET")
        os.environ["UNIT_TEST_SECRET"] = "super-secret-value"
        self.addCleanup(self._restore_env, "UNIT_TEST_SECRET", old_env_secret)

        resolved = self.client.post(
            "/api/secrets/resolve",
            json={"ref": "env:UNIT_TEST_SECRET"},
            headers=self.auth_headers,
        )
        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(resolved.json()["provider"], "env")

        rotation = self.client.post(
            "/api/secrets/rotation-plan",
            json={"items": [{"ref": "env:UNIT_TEST_SECRET", "rotation_days": 45}]},
            headers=self.auth_headers,
        )
        self.assertEqual(rotation.status_code, 200)
        self.assertEqual(rotation.json()["count"], 1)

        discovered = self.client.get("/api/plugins/discover", headers=self.auth_headers)
        self.assertEqual(discovered.status_code, 200)
        self.assertIn("count", discovered.json())

        job = self.client.post(
            "/api/jobs",
            json={
                "kind": "tool_run",
                "idempotency_key": "job-idem-001",
                "payload": {
                    "tool": "scripts.export_summary",
                    "mode": "plan",
                    "args": [
                        "--findings",
                        "examples/outputs/findings.json",
                        "--output-dir",
                        str(Path(self.temp_dir.name) / "summary"),
                    ],
                    "timeout_seconds": 120,
                },
                "max_attempts": 2,
            },
            headers=self.auth_headers,
        )
        self.assertEqual(job.status_code, 200)
        job_id = job.json()["id"]

        listed = self.client.get("/api/jobs", headers=self.auth_headers)
        self.assertEqual(listed.status_code, 200)
        self.assertGreaterEqual(listed.json()["count"], 1)

        retried = self.client.post(
            f"/api/jobs/{job_id}/retry", headers=self.auth_headers
        )
        self.assertEqual(retried.status_code, 200)
        self.assertEqual(retried.json()["status"], "queued")

        worker_status = self.client.get(
            "/api/jobs/worker/status", headers=self.auth_headers
        )
        self.assertEqual(worker_status.status_code, 200)
        self.assertIn("running", worker_status.json())

        compliance = self.client.post(
            "/api/compliance/export",
            json={"output_dir": str(Path(self.temp_dir.name) / "compliance")},
            headers=self.auth_headers,
        )
        self.assertEqual(compliance.status_code, 200)
        self.assertTrue(Path(compliance.json()["json"]).exists())

        scope_map = self.client.get(
            "/api/visualizations/scope-map", headers=self.auth_headers
        )
        self.assertEqual(scope_map.status_code, 200)
        graph = scope_map.json()["graph"]
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)

    @staticmethod
    def _restore_env(key: str, value: str | None):
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


class TestCommandCenterTools(unittest.TestCase):
    def test_run_tool_executes_allowlisted_module(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "summary"
            result = tools.run_tool(
                tool_id="scripts.export_summary",
                args=[
                    "--findings",
                    "examples/outputs/findings.json",
                    "--output-dir",
                    output_dir.as_posix(),
                ],
                run_id="run_tool_unit_test",
                timeout_seconds=120,
                log_root=Path(tmp_dir) / "logs",
            )
            self.assertEqual(result["status"], "completed")
            self.assertTrue(Path(result["log_path"]).exists())


if __name__ == "__main__":
    unittest.main()
