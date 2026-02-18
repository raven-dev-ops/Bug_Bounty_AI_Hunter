import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from command_center_api import tools
from command_center_api.app import create_app


class TestCommandCenterApi(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        db_path = Path(self.temp_dir.name) / "command_center_test.db"
        self.client = TestClient(create_app(db_path=db_path))

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
        )
        self.assertEqual(blocked.status_code, 403)

        acknowledged = self.client.post(
            f"/api/workspaces/{workspace_id}/ack",
            json={
                "acknowledged_by": "unit-test",
                "authorized_target": "https://example.test",
            },
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
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("tool not allowed", response.json()["detail"])

    def test_docs_path_traversal_is_blocked(self):
        response = self.client.get("/api/docs/page", params={"path": "../README.md"})
        self.assertEqual(response.status_code, 404)

    def test_findings_import_export_round_trip(self):
        imported = self.client.post(
            "/api/findings/import",
            json={
                "source": "unit-test",
                "findings": [{"id": "finding-001", "title": "Sample"}],
            },
        )
        self.assertEqual(imported.status_code, 200)
        self.assertEqual(imported.json()["count"], 1)

        exported = self.client.get("/api/findings/export")
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
        )
        linked = self.client.post("/api/tasks/auto-link")
        self.assertEqual(linked.status_code, 200)
        self.assertGreaterEqual(linked.json()["created"], 1)

        board = self.client.get("/api/tasks/board")
        self.assertEqual(board.status_code, 200)
        open_tasks = board.json()["columns"]["open"]
        self.assertTrue(any(task.get("linked_finding_id") == "finding-auto-001" for task in open_tasks))

    def test_metrics_compute_and_snapshot_listing(self):
        computed = self.client.post("/api/metrics/compute", json={"scope": "global"})
        self.assertEqual(computed.status_code, 200)
        self.assertIn("program_count", computed.json()["metrics"])

        snapshots = self.client.get("/api/metrics/snapshots", params={"scope": "global"})
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
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("unsupported", response.json()["detail"])


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
