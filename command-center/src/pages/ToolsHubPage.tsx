import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  executeRun,
  getRunLog,
  listRuns,
  listTools,
  listWorkspaces,
  type ToolDescriptor,
  type ToolRunRow,
  type WorkspaceRow,
} from "../api/client";

function statusTone(status: string): string {
  const safe = status.toLowerCase();
  if (safe === "completed") {
    return "text-emerald-300";
  }
  if (safe === "running") {
    return "text-sky-300";
  }
  if (safe === "failed" || safe === "timeout") {
    return "text-red-300";
  }
  return "text-amber-300";
}

function parseArgs(input: string): string[] {
  return input
    .split(/\s+/)
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
}

export function ToolsHubPage() {
  const [tools, setTools] = useState<ToolDescriptor[]>([]);
  const [workspaces, setWorkspaces] = useState<WorkspaceRow[]>([]);
  const [runs, setRuns] = useState<ToolRunRow[]>([]);
  const [selectedTool, setSelectedTool] = useState("");
  const [mode, setMode] = useState<"plan" | "run">("plan");
  const [workspaceId, setWorkspaceId] = useState("");
  const [argsText, setArgsText] = useState("");
  const [timeoutSeconds, setTimeoutSeconds] = useState(600);
  const [logContent, setLogContent] = useState("");
  const [activeRunId, setActiveRunId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const refreshData = useCallback(async () => {
    const [catalogItems, workspaceItems, runItems] = await Promise.all([
      listTools(),
      listWorkspaces(),
      listRuns(),
    ]);
    setTools(catalogItems);
    setWorkspaces(workspaceItems);
    setRuns(runItems);
    if (catalogItems.length > 0) {
      setSelectedTool((current) => current || catalogItems[0].id);
    }
  }, []);

  useEffect(() => {
    refreshData().catch((reason: unknown) => {
      const message = reason instanceof Error ? reason.message : "Failed to load tools";
      setError(message);
    });
  }, [refreshData]);

  const groupedTools = useMemo(() => {
    const groups = new Map<string, ToolDescriptor[]>();
    for (const item of tools) {
      const current = groups.get(item.stage) ?? [];
      current.push(item);
      groups.set(item.stage, current);
    }
    return Array.from(groups.entries()).sort(([left], [right]) => left.localeCompare(right));
  }, [tools]);

  async function onExecute(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const run = await executeRun({
        tool: selectedTool,
        mode,
        args: parseArgs(argsText),
        workspace_id: workspaceId || undefined,
        timeout_seconds: timeoutSeconds,
      });
      setActiveRunId(run.id);
      const log = await getRunLog(run.id);
      setLogContent(log.content);
      await refreshData();
    } catch (reason: unknown) {
      const message = reason instanceof Error ? reason.message : "Tool execution failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function openRunLog(runId: string) {
    setActiveRunId(runId);
    try {
      const log = await getRunLog(runId);
      setLogContent(log.content);
    } catch (reason: unknown) {
      const message = reason instanceof Error ? reason.message : "Failed to load run log";
      setError(message);
    }
  }

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #177 + #178 + #179</p>
        <h1 className="text-3xl font-semibold text-text">Tools Hub</h1>
        <p className="max-w-3xl text-sm text-muted">
          Browse script catalog entries, run approved modules, and inspect log output from the API.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[1.1fr,1fr]">
        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Catalog</p>
          <div className="mt-3 space-y-3">
            {groupedTools.map(([stage, entries]) => (
              <div key={stage} className="rounded-xl border border-border bg-bg/30 p-3">
                <p className="text-xs uppercase tracking-[0.16em] text-accent">{stage}</p>
                <ul className="mt-2 space-y-2">
                  {entries.map((entry) => (
                    <li key={entry.id}>
                      <button
                        type="button"
                        className={[
                          "w-full rounded-lg border px-3 py-2 text-left",
                          selectedTool === entry.id
                            ? "border-accent bg-accent/15"
                            : "border-border bg-bg/40 hover:border-accent/60",
                        ].join(" ")}
                        onClick={() => setSelectedTool(entry.id)}
                      >
                        <p className="text-sm font-semibold text-text">{entry.name}</p>
                        <p className="text-xs text-muted">{entry.id}</p>
                        <p className="mt-1 text-xs text-muted">{entry.description}</p>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <form className="space-y-3 rounded-2xl border border-border bg-surface/85 p-4" onSubmit={onExecute}>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Run tool</p>
          <label className="space-y-1">
            <span className="text-xs text-muted">Tool module</span>
            <select
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={selectedTool}
              onChange={(event) => setSelectedTool(event.target.value)}
            >
              {tools.map((entry) => (
                <option key={entry.id} value={entry.id}>
                  {entry.name}
                </option>
              ))}
            </select>
          </label>
          <div className="grid gap-3 md:grid-cols-2">
            <label className="space-y-1">
              <span className="text-xs text-muted">Mode</span>
              <select
                className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
                value={mode}
                onChange={(event) => setMode(event.target.value as "plan" | "run")}
              >
                <option value="plan">plan</option>
                <option value="run">run</option>
              </select>
            </label>
            <label className="space-y-1">
              <span className="text-xs text-muted">Timeout seconds</span>
              <input
                type="number"
                min={1}
                max={7200}
                className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
                value={timeoutSeconds}
                onChange={(event) => setTimeoutSeconds(Number(event.target.value))}
              />
            </label>
          </div>
          <label className="space-y-1">
            <span className="text-xs text-muted">Workspace (required for run mode)</span>
            <select
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={workspaceId}
              onChange={(event) => setWorkspaceId(event.target.value)}
            >
              <option value="">None</option>
              {workspaces.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} ({item.id})
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Args (space separated)</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={argsText}
              onChange={(event) => setArgsText(event.target.value)}
              placeholder="--config examples/pipeline_config.yaml --mode plan"
            />
          </label>
          <button
            type="submit"
            className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
            disabled={loading || !selectedTool}
          >
            {loading ? "Running..." : "Execute"}
          </button>
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
        </form>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr,1fr]">
        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Recent runs</p>
          <div className="mt-3 space-y-2">
            {runs.map((run) => (
              <button
                key={run.id}
                type="button"
                className={[
                  "w-full rounded-lg border px-3 py-2 text-left",
                  activeRunId === run.id
                    ? "border-accent bg-accent/15"
                    : "border-border bg-bg/30 hover:border-accent/60",
                ].join(" ")}
                onClick={() => openRunLog(run.id)}
              >
                <p className="text-sm font-semibold text-text">{run.tool}</p>
                <p className="text-xs text-muted">
                  {run.id} | <span className="cc-pill">{run.mode}</span> |{" "}
                  <span className={statusTone(run.status)}>{run.status}</span> | exit{" "}
                  {run.exit_code ?? "-"}
                </p>
              </button>
            ))}
            {runs.length === 0 ? <p className="cc-empty-state text-sm">No runs yet.</p> : null}
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Live log tail</p>
          <pre className="mt-3 max-h-[360px] overflow-auto rounded-lg border border-border bg-bg/40 p-3 text-xs text-muted">
            {logContent || "Select a run to view logs."}
          </pre>
        </div>
      </div>
    </section>
  );
}
