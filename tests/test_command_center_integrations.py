import hashlib
import hmac
import json
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from command_center_api.app import create_app


def _signature(secret: str, payload: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


class TestCommandCenterIntegrations(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        db_path = Path(self.temp_dir.name) / "command_center_integrations.db"
        self.client = TestClient(create_app(db_path=db_path))

    def test_sync_yeswehack_with_fixtures(self):
        response = self.client.post(
            "/api/connectors/yeswehack/sync",
            json={"fixtures_dir": "tests/fixtures/connectors", "limit": 10},
        )
        self.assertEqual(response.status_code, 200)
        summary = response.json()["summary"]
        self.assertGreaterEqual(summary["count"], 1)

    def test_sync_intigriti_with_fixtures(self):
        response = self.client.post(
            "/api/connectors/intigriti/sync",
            json={"fixtures_dir": "tests/fixtures/connectors", "limit": 10},
        )
        self.assertEqual(response.status_code, 200)
        summary = response.json()["summary"]
        self.assertGreaterEqual(summary["count"], 1)

    def test_sync_bugcrowd_programs_without_token_uses_fallback(self):
        response = self.client.post(
            "/api/connectors/bugcrowd/programs/sync",
            json={"limit": 20},
        )
        self.assertEqual(response.status_code, 200)
        summary = response.json()["summary"]
        self.assertEqual(summary["mode"], "fallback_registry")
        self.assertGreaterEqual(summary["count"], 1)

    def test_bugcrowd_webhook_signature_validation(self):
        old_secret = os.environ.get("BUGCROWD_WEBHOOK_SECRET")
        os.environ["BUGCROWD_WEBHOOK_SECRET"] = "test-secret"
        self.addCleanup(self._restore_env, "BUGCROWD_WEBHOOK_SECRET", old_secret)

        payload = {
            "event_type": "submission.updated",
            "submission": {"id": "sub-001", "status": "triaged"},
        }
        raw = json.dumps(payload).encode("utf-8")
        headers = {
            "content-type": "application/json",
            "x-bugcrowd-signature": _signature("test-secret", raw),
        }
        response = self.client.post(
            "/api/connectors/bugcrowd/webhook",
            content=raw,
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status_updates"], 1)

    def test_github_webhook_creates_task(self):
        old_secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
        os.environ["GITHUB_WEBHOOK_SECRET"] = "github-secret"
        self.addCleanup(self._restore_env, "GITHUB_WEBHOOK_SECRET", old_secret)

        payload = {
            "issue": {"number": 42, "title": "Webhook-created issue", "state": "open"},
            "repository": {"full_name": "example/repo"},
        }
        raw = json.dumps(payload).encode("utf-8")
        headers = {
            "content-type": "application/json",
            "x-hub-signature-256": _signature("github-secret", raw),
            "x-github-event": "issues",
        }
        response = self.client.post("/api/connectors/github/webhook", content=raw, headers=headers)
        self.assertEqual(response.status_code, 200)
        task_id = response.json()["task_id"]
        self.assertTrue(task_id.startswith("github:example/repo:42"))

        tasks = self.client.get("/api/tasks")
        self.assertEqual(tasks.status_code, 200)
        self.assertGreaterEqual(tasks.json()["count"], 1)

    @staticmethod
    def _restore_env(key: str, value: str | None):
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
