-- Command Center SQLite schema (MVP).
-- Source of truth for issue #170 persistence baseline.

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

