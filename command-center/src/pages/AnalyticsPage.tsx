import { useEffect, useMemo, useState } from "react";
import { computeMetrics, listMetricSnapshots, type MetricSnapshotRow } from "../api/client";

export function AnalyticsPage() {
  const [snapshots, setSnapshots] = useState<MetricSnapshotRow[]>([]);
  const [metrics, setMetrics] = useState<Record<string, number>>({});
  const [error, setError] = useState("");

  async function refreshMetrics() {
    const computed = await computeMetrics("global");
    setMetrics(computed.metrics);
    const history = await listMetricSnapshots("global", 200);
    setSnapshots(history);
  }

  useEffect(() => {
    refreshMetrics().catch((reason: unknown) => {
      const text = reason instanceof Error ? reason.message : "Failed to load analytics";
      setError(text);
    });
  }, []);

  const groupedHistory = useMemo(() => {
    const groups = new Map<string, MetricSnapshotRow[]>();
    for (const item of snapshots) {
      const current = groups.get(item.metric_name) ?? [];
      current.push(item);
      groups.set(item.metric_name, current);
    }
    return Array.from(groups.entries());
  }, [snapshots]);

  const maxValue = useMemo(() => {
    const values = Object.values(metrics);
    if (values.length === 0) {
      return 1;
    }
    return Math.max(...values, 1);
  }, [metrics]);

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #196 + #197</p>
        <h1 className="text-3xl font-semibold text-text">Analytics</h1>
        <p className="max-w-3xl text-sm text-muted">
          Compute and store operational metrics, then review snapshot history for dashboard trends.
        </p>
      </header>

      <div className="flex gap-2">
        <button
          type="button"
          className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
          onClick={() => {
            refreshMetrics().catch((reason: unknown) => {
              const text = reason instanceof Error ? reason.message : "Failed to refresh metrics";
              setError(text);
            });
          }}
        >
          Recompute metrics
        </button>
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {Object.entries(metrics).map(([metricName, metricValue]) => (
          <div key={metricName} className="rounded-2xl border border-border bg-surface/85 p-4">
            <p className="text-xs uppercase tracking-[0.16em] text-muted">{metricName}</p>
            <p className="mt-2 text-2xl font-semibold text-text">{metricValue}</p>
            <div className="mt-3 h-2 rounded-full bg-bg/40">
              <div
                className="h-2 rounded-full bg-accent"
                style={{ width: `${Math.min(100, (metricValue / maxValue) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-border bg-surface/85 p-4">
        <p className="text-xs uppercase tracking-[0.16em] text-muted">Snapshot history</p>
        <div className="mt-3 space-y-3">
          {groupedHistory.map(([metricName, entries]) => (
            <div key={metricName} className="rounded-lg border border-border bg-bg/30 p-3">
              <p className="text-sm font-semibold text-text">{metricName}</p>
              <ul className="mt-2 space-y-1 text-xs text-muted">
                {entries.slice(0, 5).map((entry) => (
                  <li key={entry.id}>
                    {entry.captured_at} {"->"} {entry.metric_value}
                  </li>
                ))}
              </ul>
            </div>
          ))}
          {groupedHistory.length === 0 ? (
            <p className="text-sm text-muted">No snapshots available yet.</p>
          ) : null}
        </div>
      </div>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
    </section>
  );
}
