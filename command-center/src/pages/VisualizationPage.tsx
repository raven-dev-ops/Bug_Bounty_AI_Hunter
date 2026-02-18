import { useEffect, useMemo, useState } from "react";
import { getScopeMap, type ScopeMapNode, type ScopeMapPayload } from "../api/client";

const typeOptions = ["all", "program", "finding", "task", "workspace"] as const;
type NodeTypeFilter = (typeof typeOptions)[number];

function nodeColor(node: ScopeMapNode): string {
  if (node.type === "finding") {
    const severity = (node.severity ?? "unknown").toLowerCase();
    if (severity === "critical") {
      return "#ef4444";
    }
    if (severity === "high") {
      return "#f97316";
    }
    if (severity === "medium") {
      return "#eab308";
    }
    if (severity === "low") {
      return "#84cc16";
    }
    return "#60a5fa";
  }
  if (node.type === "program") {
    return "#06b6d4";
  }
  if (node.type === "task") {
    return "#c084fc";
  }
  if (node.type === "workspace") {
    return "#22c55e";
  }
  return "#94a3b8";
}

export function VisualizationPage() {
  const [data, setData] = useState<ScopeMapPayload | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [typeFilter, setTypeFilter] = useState<NodeTypeFilter>("all");

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const payload = await getScopeMap(300);
      setData(payload);
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to load scope map";
      setError(text);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh().catch(() => {
      // No-op fallback; error state is handled in refresh.
    });
  }, []);

  const filteredNodes = useMemo(() => {
    if (!data) {
      return [];
    }
    if (typeFilter === "all") {
      return data.graph.nodes;
    }
    return data.graph.nodes.filter((node) => node.type === typeFilter);
  }, [data, typeFilter]);

  const filteredEdges = useMemo(() => {
    if (!data) {
      return [];
    }
    const nodeIds = new Set(filteredNodes.map((node) => node.id));
    return data.graph.edges.filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target));
  }, [data, filteredNodes]);

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #206</p>
        <h1 className="text-3xl font-semibold text-text">Scope Visualization</h1>
        <p className="max-w-3xl text-sm text-muted">
          Interactive scope map with threat overlays for programs, findings, tasks, and workspace
          relationships.
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
          onClick={() => {
            refresh().catch(() => {
              // No-op fallback; error state is handled in refresh.
            });
          }}
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh map"}
        </button>
        <label className="flex items-center gap-2 text-xs text-muted">
          Node filter
          <select
            className="rounded-md border border-border bg-bg/40 px-2 py-1 text-xs text-text"
            value={typeFilter}
            onChange={(event) => setTypeFilter(event.target.value as NodeTypeFilter)}
          >
            {typeOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
      </div>

      {data ? (
        <>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-2xl border border-border bg-surface/85 p-4">
              <p className="text-xs uppercase tracking-[0.16em] text-muted">Threat score</p>
              <p className="mt-2 text-2xl font-semibold text-text">{data.overlays.threat_score}</p>
            </div>
            {Object.entries(data.graph.counts).map(([key, value]) => (
              <div key={key} className="rounded-2xl border border-border bg-surface/85 p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted">{key}</p>
                <p className="mt-2 text-2xl font-semibold text-text">{value}</p>
              </div>
            ))}
          </div>

          <div className="rounded-2xl border border-border bg-surface/85 p-4">
            <p className="text-xs uppercase tracking-[0.16em] text-muted">
              Scope graph ({filteredNodes.length} nodes / {filteredEdges.length} edges)
            </p>
            <div className="mt-3 overflow-x-auto rounded-xl border border-border bg-bg/40 p-2">
              <svg viewBox="0 0 100 100" className="h-[420px] min-w-[680px] w-full">
                {filteredEdges.map((edge, index) => {
                  const source = filteredNodes.find((item) => item.id === edge.source);
                  const target = filteredNodes.find((item) => item.id === edge.target);
                  if (!source || !target) {
                    return null;
                  }
                  return (
                    <line
                      key={`${edge.source}-${edge.target}-${index}`}
                      x1={source.x}
                      y1={source.y}
                      x2={target.x}
                      y2={target.y}
                      stroke="rgba(148, 163, 184, 0.45)"
                      strokeWidth="0.35"
                    />
                  );
                })}
                {filteredNodes.map((node) => (
                  <g key={node.id}>
                    <circle cx={node.x} cy={node.y} r={2} fill={nodeColor(node)} />
                    <text x={node.x + 1.5} y={node.y - 1.2} fontSize="2.4" fill="var(--color-text)">
                      {node.label.slice(0, 24)}
                    </text>
                  </g>
                ))}
              </svg>
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-2xl border border-border bg-surface/85 p-4">
              <p className="text-xs uppercase tracking-[0.16em] text-muted">Severity overlay</p>
              <ul className="mt-3 space-y-1 text-sm text-text">
                {Object.entries(data.overlays.severity_counts).map(([severity, count]) => (
                  <li key={severity} className="flex items-center justify-between">
                    <span>{severity}</span>
                    <span className="font-semibold">{count}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-2xl border border-border bg-surface/85 p-4">
              <p className="text-xs uppercase tracking-[0.16em] text-muted">Metric timeline</p>
              <ul className="mt-3 space-y-1 text-sm text-text">
                {data.overlays.timeline.slice(0, 8).map((entry, index) => (
                  <li
                    key={`${entry.metric_name}-${entry.captured_at}-${index}`}
                    className="flex items-center justify-between"
                  >
                    <span>
                      {entry.metric_name} ({entry.captured_at})
                    </span>
                    <span className="font-semibold">{entry.value}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      ) : null}

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
    </section>
  );
}
