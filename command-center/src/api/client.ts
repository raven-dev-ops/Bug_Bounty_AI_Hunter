export const API_BASE_URL =
  import.meta.env.VITE_COMMAND_CENTER_API_URL ?? "http://127.0.0.1:8787";

type ProgramListResponse = {
  items: ProgramRow[];
  count: number;
};

type WorkspaceListResponse = {
  items: WorkspaceRow[];
  count: number;
};

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
    headers: {
      "Content-Type": "application/json",
    },
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
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<WorkspaceRow>(response);
}
