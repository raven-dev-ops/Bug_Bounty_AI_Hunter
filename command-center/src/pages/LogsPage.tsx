import { useEffect, useMemo, useState } from "react";
import { getRunLog, listRuns, type ToolRunRow } from "../api/client";

export function LogsPage() {
  const [runs, setRuns] = useState<ToolRunRow[]>([]);
  const [query, setQuery] = useState("");
  const [selectedRunId, setSelectedRunId] = useState("");
  const [logContent, setLogContent] = useState("");
  const [error, setError] = useState("");

  async function refreshRuns() {
    const items = await listRuns();
    setRuns(items);
    if (!selectedRunId && items.length > 0) {
      setSelectedRunId(items[0].id);
    }
  }

  useEffect(() => {
    refreshRuns().catch((reason: unknown) => {
      const text = reason instanceof Error ? reason.message : "Failed to load runs";
      setError(text);
    });
  }, []);

  useEffect(() => {
    if (!selectedRunId) {
      setLogContent("");
      return;
    }
    getRunLog(selectedRunId)
      .then((result) => setLogContent(result.content))
      .catch((reason: unknown) => {
        const text = reason instanceof Error ? reason.message : "Failed to load log";
        setError(text);
      });
  }, [selectedRunId]);

  const filteredRuns = useMemo(() => {
    const safeQuery = query.trim().toLowerCase();
    if (!safeQuery) {
      return runs;
    }
    return runs.filter((run) => {
      const haystack = `${run.id} ${run.tool} ${run.status} ${run.mode}`.toLowerCase();
      return haystack.includes(safeQuery);
    });
  }, [query, runs]);

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #183</p>
        <h1 className="text-3xl font-semibold text-text">Logs</h1>
        <p className="max-w-3xl text-sm text-muted">
          Search tool runs by id, tool, mode, or status and inspect captured log output.
        </p>
      </header>

      <div className="flex items-center gap-2 rounded-2xl border border-border bg-surface/85 p-4">
        <input
          className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
          placeholder="Search run id, tool, mode, status"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button
          type="button"
          className="rounded-lg border border-border bg-bg/40 px-3 py-2 text-xs text-text hover:border-accent"
          onClick={() => {
            refreshRuns().catch((reason: unknown) => {
              const text = reason instanceof Error ? reason.message : "Failed to refresh logs";
              setError(text);
            });
          }}
        >
          Refresh
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr,1fr]">
        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Runs</p>
          <div className="mt-3 space-y-2">
            {filteredRuns.map((run) => (
              <button
                key={run.id}
                type="button"
                className={[
                  "w-full rounded-lg border px-3 py-2 text-left",
                  selectedRunId === run.id
                    ? "border-accent bg-accent/15"
                    : "border-border bg-bg/30 hover:border-accent/60",
                ].join(" ")}
                onClick={() => setSelectedRunId(run.id)}
              >
                <p className="text-sm font-semibold text-text">{run.tool}</p>
                <p className="text-xs text-muted">
                  {run.id} | {run.mode} | {run.status} | exit {run.exit_code ?? "-"}
                </p>
              </button>
            ))}
            {filteredRuns.length === 0 ? <p className="text-sm text-muted">No runs found.</p> : null}
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Log tail</p>
          <pre className="mt-3 max-h-[420px] overflow-auto rounded-lg border border-border bg-bg/40 p-3 text-xs text-muted">
            {logContent || "Select a run to view logs."}
          </pre>
        </div>
      </div>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
    </section>
  );
}
