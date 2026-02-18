export const API_BASE_URL =
  import.meta.env.VITE_COMMAND_CENTER_API_URL ?? "http://127.0.0.1:8787";

export type ProgramRow = {
  id: string;
  name: string;
  platform: string | null;
  handle: string | null;
  policy_url: string | null;
  rewards_summary: string | null;
  source: string | null;
  raw_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type FindingRow = {
  id: string;
  title: string;
  severity: string | null;
  status: string | null;
  source: string | null;
  description: string | null;
  impact: string | null;
  remediation: string | null;
  raw_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type WorkspaceRow = {
  id: string;
  platform: string;
  slug: string;
  name: string;
  engagement_url: string | null;
  root_dir: string | null;
  roe_acknowledged: number;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
  authorized_target: string | null;
  created_at: string;
  updated_at: string;
};

export type ToolDescriptor = {
  id: string;
  name: string;
  stage: string;
  description: string;
};

export type ToolRunRow = {
  id: string;
  tool: string;
  mode: string;
  status: string;
  exit_code: number | null;
  started_at: string;
  finished_at: string | null;
  log_path: string | null;
  artifact_path: string | null;
  request_json: Record<string, unknown>;
};

export type NotificationRow = {
  id: string;
  channel: string;
  title: string;
  body: string;
  read: number;
  created_at: string;
};

export type TaskRow = {
  id: string;
  title: string;
  status: string;
  linked_program_id: string | null;
  linked_finding_id: string | null;
  created_at: string;
  updated_at: string;
};

export type MetricSnapshotRow = {
  id: string;
  metric_name: string;
  metric_value: number;
  scope: string;
  captured_at: string;
};

export type ScopeMapNode = {
  id: string;
  type: string;
  label: string;
  x: number;
  y: number;
  severity?: string;
  status?: string;
  platform?: string;
};

export type ScopeMapEdge = {
  source: string;
  target: string;
  relation: string;
};

export type ScopeMapPayload = {
  graph: {
    nodes: ScopeMapNode[];
    edges: ScopeMapEdge[];
    counts: Record<string, number>;
  };
  overlays: {
    threat_score: number;
    severity_counts: Record<string, number>;
    finding_status_counts: Record<string, number>;
    task_status_counts: Record<string, number>;
    run_status_counts: Record<string, number>;
    timeline: Array<{
      metric_name: string;
      value: number;
      captured_at: string;
    }>;
  };
};

export type DocSearchResult = {
  path: string;
  title: string;
  snippet: string;
};

type ProgramListResponse = {
  items: ProgramRow[];
  count: number;
};

type FindingListResponse = {
  items: FindingRow[];
  count: number;
};

type WorkspaceListResponse = {
  items: WorkspaceRow[];
  count: number;
};

type ToolListResponse = {
  items: ToolDescriptor[];
  count: number;
};

type RunListResponse = {
  items: ToolRunRow[];
  count: number;
};

type NotificationListResponse = {
  items: NotificationRow[];
  count: number;
};

type TaskListResponse = {
  items: TaskRow[];
  count: number;
};

type TaskBoardResponse = {
  columns: Record<string, TaskRow[]>;
  count: number;
};

type MetricSnapshotResponse = {
  items: MetricSnapshotRow[];
  count: number;
};

type DocsSearchResponse = {
  items: DocSearchResult[];
  count: number;
};

type FindingsExportResponse = {
  findings: Record<string, unknown>[];
  count: number;
};

type RunLogResponse = {
  run_id: string;
  log_path: string;
  content: string;
};

type ReportRunResponse = {
  run: ToolRunRow;
  output_dir: string;
  files: string[];
};

type MetricsComputeResponse = {
  scope: string;
  metrics: Record<string, number>;
  snapshots: MetricSnapshotRow[];
};

type ScopeMapResponse = ScopeMapPayload;

type ListProgramParams = {
  query?: string;
  limit?: number;
};

type CreateWorkspacePayload = {
  platform: string;
  slug: string;
  name: string;
  engagement_url?: string;
  root_dir?: string;
  scaffold_files?: boolean;
  force?: boolean;
};

type AckWorkspacePayload = {
  acknowledged_by: string;
  authorized_target: string;
};

type ExecuteRunPayload = {
  tool: string;
  mode: "plan" | "run";
  args: string[];
  workspace_id?: string;
  timeout_seconds?: number;
};

type ReportBundlePayload = {
  findings_path: string;
  target_profile_path: string;
  output_dir: string;
  evidence_path?: string;
  repro_steps_path?: string;
  workspace_id?: string;
  timeout_seconds?: number;
};

type IssueDraftPayload = {
  findings_path: string;
  target_profile_path: string;
  output_dir: string;
  platform: string;
  attachments_manifest_path?: string;
  workspace_id?: string;
  timeout_seconds?: number;
};

const ACCESS_TOKEN_KEY = "command-center-access-token";
const DEFAULT_ORG_ID = import.meta.env.VITE_COMMAND_CENTER_ORG_ID ?? "org:command-center-local";
const DEFAULT_OIDC_SUB = import.meta.env.VITE_COMMAND_CENTER_OIDC_SUB ?? "command-center-ui-admin";
const DEFAULT_OIDC_EMAIL =
  import.meta.env.VITE_COMMAND_CENTER_OIDC_EMAIL ?? "operator@command-center.local";
const DEFAULT_OIDC_NAME =
  import.meta.env.VITE_COMMAND_CENTER_OIDC_NAME ?? "Command Center Operator";
const STATIC_ACCESS_TOKEN = import.meta.env.VITE_COMMAND_CENTER_ACCESS_TOKEN ?? "";

const rawFetch: typeof globalThis.fetch = globalThis.fetch.bind(globalThis);
let sessionBootstrapPromise: Promise<string | null> | null = null;

function base64UrlEncode(value: string): string {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function buildUnsignedIdToken(): string {
  const header = base64UrlEncode(JSON.stringify({ alg: "none", typ: "JWT" }));
  const payload = base64UrlEncode(
    JSON.stringify({
      sub: DEFAULT_OIDC_SUB,
      email: DEFAULT_OIDC_EMAIL,
      name: DEFAULT_OIDC_NAME,
      exp: Math.floor(Date.now() / 1000) + 3600,
    }),
  );
  return `${header}.${payload}.sig`;
}

function readStoredToken(): string {
  if (STATIC_ACCESS_TOKEN) {
    return STATIC_ACCESS_TOKEN;
  }
  if (typeof window === "undefined") {
    return "";
  }
  try {
    return window.localStorage.getItem(ACCESS_TOKEN_KEY) ?? "";
  } catch {
    return "";
  }
}

function writeStoredToken(token: string): void {
  if (!token || STATIC_ACCESS_TOKEN) {
    return;
  }
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
  } catch {
    // Ignore storage write errors (private mode / blocked storage).
  }
}

function clearStoredToken(): void {
  if (STATIC_ACCESS_TOKEN || typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  } catch {
    // Ignore storage write errors (private mode / blocked storage).
  }
}

async function bootstrapSessionToken(): Promise<string | null> {
  const orgPayload = JSON.stringify({
    id: DEFAULT_ORG_ID,
    name: "Command Center Local Org",
  });
  const principalPayload = JSON.stringify({
    id: `oidc:${DEFAULT_OIDC_SUB}`,
    email: DEFAULT_OIDC_EMAIL,
    display_name: DEFAULT_OIDC_NAME,
    oidc_sub: DEFAULT_OIDC_SUB,
    org_id: DEFAULT_ORG_ID,
    role: "admin",
  });

  // First-run bootstrap path for a new local DB; these calls may return 401 after bootstrap.
  await rawFetch(`${API_BASE_URL}/api/auth/orgs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: orgPayload,
  }).catch(() => null);
  await rawFetch(`${API_BASE_URL}/api/auth/principals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: principalPayload,
  }).catch(() => null);

  const exchangeResponse = await rawFetch(`${API_BASE_URL}/api/auth/oidc/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id_token: buildUnsignedIdToken(),
      org_id: DEFAULT_ORG_ID,
    }),
  });
  if (!exchangeResponse.ok) {
    return null;
  }
  const data = (await exchangeResponse.json()) as { token?: { access_token?: string } };
  const token = data.token?.access_token;
  if (typeof token !== "string" || token.trim().length === 0) {
    return null;
  }
  writeStoredToken(token);
  return token;
}

export async function ensureApiSession(forceRefresh = false): Promise<string | null> {
  if (!forceRefresh) {
    const existingToken = readStoredToken();
    if (existingToken) {
      return existingToken;
    }
  }
  if (sessionBootstrapPromise) {
    return sessionBootstrapPromise;
  }
  const currentPromise = bootstrapSessionToken();
  sessionBootstrapPromise = currentPromise;
  try {
    return await currentPromise;
  } finally {
    if (sessionBootstrapPromise === currentPromise) {
      sessionBootstrapPromise = null;
    }
  }
}

export function clearApiSession(): void {
  clearStoredToken();
}

async function authedFetch(url: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers ?? {});
  if (!headers.has("Authorization")) {
    const token = await ensureApiSession();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }
  let response = await rawFetch(url, { ...init, headers });
  if (response.status !== 401) {
    return response;
  }

  clearStoredToken();
  const refreshedToken = await ensureApiSession(true);
  if (!refreshedToken) {
    return response;
  }
  const retryHeaders = new Headers(init.headers ?? {});
  retryHeaders.set("Authorization", `Bearer ${refreshedToken}`);
  response = await rawFetch(url, { ...init, headers: retryHeaders });
  return response;
}

const fetch = (url: string, init?: RequestInit): Promise<Response> => authedFetch(url, init);

async function parseJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const data = (await response.json()) as { detail?: string };
      if (data.detail) {
        message = data.detail;
      }
    } catch {
      // Keep HTTP status fallback message when the body is not JSON.
    }
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export async function ingestArtifacts(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/ingest`, {
    method: "POST",
  });
  await parseJsonResponse<{ ok: boolean }>(response);
}

export async function listPrograms(params: ListProgramParams): Promise<ProgramRow[]> {
  const query = new URLSearchParams();
  if (params.query) {
    query.set("query", params.query);
  }
  query.set("limit", String(params.limit ?? 500));
  const response = await fetch(`${API_BASE_URL}/api/programs?${query.toString()}`);
  const data = await parseJsonResponse<ProgramListResponse>(response);
  return data.items;
}

export async function getProgram(programId: string): Promise<ProgramRow> {
  const safeId = encodeURIComponent(programId);
  const response = await fetch(`${API_BASE_URL}/api/programs/${safeId}`);
  return parseJsonResponse<ProgramRow>(response);
}

export async function listFindings(limit = 1000): Promise<FindingRow[]> {
  const response = await fetch(`${API_BASE_URL}/api/findings?limit=${limit}`);
  const data = await parseJsonResponse<FindingListResponse>(response);
  return data.items;
}

export async function upsertFinding(payload: Record<string, unknown>): Promise<FindingRow> {
  const response = await fetch(`${API_BASE_URL}/api/findings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<FindingRow>(response);
}

export async function deleteFinding(findingId: string): Promise<void> {
  const safeId = encodeURIComponent(findingId);
  const response = await fetch(`${API_BASE_URL}/api/findings/${safeId}`, {
    method: "DELETE",
  });
  await parseJsonResponse<{ ok: boolean }>(response);
}

export async function importFindings(
  findings: Record<string, unknown>[],
  source = "command_center_import",
): Promise<number> {
  const response = await fetch(`${API_BASE_URL}/api/findings/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ findings, source }),
  });
  const data = await parseJsonResponse<{ ok: boolean; count: number }>(response);
  return data.count;
}

export async function exportFindings(): Promise<Record<string, unknown>[]> {
  const response = await fetch(`${API_BASE_URL}/api/findings/export`);
  const data = await parseJsonResponse<FindingsExportResponse>(response);
  return data.findings;
}

export async function listWorkspaces(): Promise<WorkspaceRow[]> {
  const response = await fetch(`${API_BASE_URL}/api/workspaces?limit=500`);
  const data = await parseJsonResponse<WorkspaceListResponse>(response);
  return data.items;
}

export async function createWorkspace(
  payload: CreateWorkspacePayload,
): Promise<WorkspaceRow> {
  const response = await fetch(`${API_BASE_URL}/api/workspaces`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<WorkspaceRow>(response);
}

export async function acknowledgeWorkspace(
  workspaceId: string,
  payload: AckWorkspacePayload,
): Promise<WorkspaceRow> {
  const safeId = encodeURIComponent(workspaceId);
  const response = await fetch(`${API_BASE_URL}/api/workspaces/${safeId}/ack`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<WorkspaceRow>(response);
}

export async function listTools(): Promise<ToolDescriptor[]> {
  const response = await fetch(`${API_BASE_URL}/api/tools`);
  const data = await parseJsonResponse<ToolListResponse>(response);
  return data.items;
}

export async function listRuns(limit = 300): Promise<ToolRunRow[]> {
  const response = await fetch(`${API_BASE_URL}/api/runs?limit=${limit}`);
  const data = await parseJsonResponse<RunListResponse>(response);
  return data.items;
}

export async function getRunLog(runId: string, tailLines = 200): Promise<RunLogResponse> {
  const safeId = encodeURIComponent(runId);
  const response = await fetch(
    `${API_BASE_URL}/api/runs/${safeId}/log?tail_lines=${tailLines}`,
  );
  return parseJsonResponse<RunLogResponse>(response);
}

export async function executeRun(payload: ExecuteRunPayload): Promise<ToolRunRow> {
  const response = await fetch(`${API_BASE_URL}/api/runs/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<ToolRunRow>(response);
}

export async function generateReportBundle(
  payload: ReportBundlePayload,
): Promise<ReportRunResponse> {
  const response = await fetch(`${API_BASE_URL}/api/reports/bundle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<ReportRunResponse>(response);
}

export async function generateIssueDrafts(
  payload: IssueDraftPayload,
): Promise<ReportRunResponse> {
  const response = await fetch(`${API_BASE_URL}/api/reports/issue-drafts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<ReportRunResponse>(response);
}

export async function listNotifications(
  unreadOnly = false,
): Promise<NotificationRow[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/notifications?unread_only=${unreadOnly}`,
  );
  const data = await parseJsonResponse<NotificationListResponse>(response);
  return data.items;
}

export async function sendNotification(payload: {
  channel: string;
  title: string;
  body: string;
  slack_webhook_url?: string;
  smtp_host?: string;
  smtp_port?: number;
  smtp_from?: string;
  smtp_to?: string;
  smtp_username?: string;
  smtp_password?: string;
  smtp_use_tls?: boolean;
}): Promise<{ ok: boolean; channel: string }> {
  const response = await fetch(`${API_BASE_URL}/api/notifications/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<{ ok: boolean; channel: string }>(response);
}

export async function createNotification(payload: {
  channel: string;
  title: string;
  body: string;
}): Promise<NotificationRow> {
  const response = await fetch(`${API_BASE_URL}/api/notifications`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<NotificationRow>(response);
}

export async function setNotificationRead(
  notificationId: string,
  read: boolean,
): Promise<NotificationRow> {
  const safeId = encodeURIComponent(notificationId);
  const response = await fetch(`${API_BASE_URL}/api/notifications/${safeId}/read`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ read }),
  });
  return parseJsonResponse<NotificationRow>(response);
}

export async function listTasks(limit = 500): Promise<TaskRow[]> {
  const response = await fetch(`${API_BASE_URL}/api/tasks?limit=${limit}`);
  const data = await parseJsonResponse<TaskListResponse>(response);
  return data.items;
}

export async function getTaskBoard(limit = 500): Promise<Record<string, TaskRow[]>> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/board?limit=${limit}`);
  const data = await parseJsonResponse<TaskBoardResponse>(response);
  return data.columns;
}

export async function createTask(payload: {
  title: string;
  status?: string;
  linked_program_id?: string;
  linked_finding_id?: string;
}): Promise<TaskRow> {
  const response = await fetch(`${API_BASE_URL}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<TaskRow>(response);
}

export async function updateTask(
  taskId: string,
  payload: {
    title?: string;
    status?: string;
    linked_program_id?: string;
    linked_finding_id?: string;
  },
): Promise<TaskRow> {
  const safeId = encodeURIComponent(taskId);
  const response = await fetch(`${API_BASE_URL}/api/tasks/${safeId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<TaskRow>(response);
}

export async function deleteTask(taskId: string): Promise<void> {
  const safeId = encodeURIComponent(taskId);
  const response = await fetch(`${API_BASE_URL}/api/tasks/${safeId}`, {
    method: "DELETE",
  });
  await parseJsonResponse<{ ok: boolean }>(response);
}

export async function autoLinkTasks(): Promise<number> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/auto-link`, {
    method: "POST",
  });
  const data = await parseJsonResponse<{ ok: boolean; created: number }>(response);
  return data.created;
}

export async function computeMetrics(scope = "global"): Promise<MetricsComputeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/metrics/compute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scope }),
  });
  return parseJsonResponse<MetricsComputeResponse>(response);
}

export async function listMetricSnapshots(
  scope = "global",
  limit = 200,
): Promise<MetricSnapshotRow[]> {
  const query = new URLSearchParams({ scope, limit: String(limit) });
  const response = await fetch(`${API_BASE_URL}/api/metrics/snapshots?${query.toString()}`);
  const data = await parseJsonResponse<MetricSnapshotResponse>(response);
  return data.items;
}

export async function getScopeMap(limit = 200): Promise<ScopeMapPayload> {
  const query = new URLSearchParams({ limit: String(limit) });
  const response = await fetch(`${API_BASE_URL}/api/visualizations/scope-map?${query.toString()}`);
  return parseJsonResponse<ScopeMapResponse>(response);
}

export async function searchDocs(query: string, limit = 30): Promise<DocSearchResult[]> {
  const safeQuery = encodeURIComponent(query);
  const response = await fetch(
    `${API_BASE_URL}/api/docs/search?query=${safeQuery}&limit=${limit}`,
  );
  const data = await parseJsonResponse<DocsSearchResponse>(response);
  return data.items;
}

export async function loadDocPage(path: string): Promise<{ path: string; content: string }> {
  const safePath = encodeURIComponent(path);
  const response = await fetch(`${API_BASE_URL}/api/docs/page?path=${safePath}`);
  return parseJsonResponse<{ path: string; content: string }>(response);
}
