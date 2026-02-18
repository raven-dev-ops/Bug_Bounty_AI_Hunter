import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ingestArtifacts, listPrograms, type ProgramRow } from "../api/client";

type SortField = "name" | "platform" | "source" | "updated_at";
type SortDirection = "asc" | "desc";

type SavedView = {
  id: string;
  name: string;
  query: string;
  platform: string;
  source: string;
  sortField: SortField;
  sortDirection: SortDirection;
};

const SAVED_VIEWS_KEY = "command-center-feed-saved-views";

function compareText(a: string, b: string): number {
  return a.localeCompare(b, undefined, { sensitivity: "base" });
}

function loadSavedViews(): SavedView[] {
  const raw = window.localStorage.getItem(SAVED_VIEWS_KEY);
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw) as SavedView[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function BountyFeedPage() {
  const [programs, setPrograms] = useState<ProgramRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [platform, setPlatform] = useState("all");
  const [source, setSource] = useState("all");
  const [sortField, setSortField] = useState<SortField>("updated_at");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [savedViews, setSavedViews] = useState<SavedView[]>(() => loadSavedViews());
  const [viewName, setViewName] = useState("");
  const [refreshTick, setRefreshTick] = useState(0);

  useEffect(() => {
    window.localStorage.setItem(SAVED_VIEWS_KEY, JSON.stringify(savedViews));
  }, [savedViews]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    listPrograms({ query, limit: 500 })
      .then((items) => {
        if (!cancelled) {
          setPrograms(items);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          const message = reason instanceof Error ? reason.message : "Failed to load programs";
          setError(message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [query, refreshTick]);

  const platforms = useMemo(() => {
    const values = new Set<string>();
    for (const item of programs) {
      const value = item.platform?.trim();
      if (value) {
        values.add(value);
      }
    }
    return Array.from(values).sort(compareText);
  }, [programs]);

  const sources = useMemo(() => {
    const values = new Set<string>();
    for (const item of programs) {
      const value = item.source?.trim();
      if (value) {
        values.add(value);
      }
    }
    return Array.from(values).sort(compareText);
  }, [programs]);

  const filteredPrograms = useMemo(() => {
    const filtered = programs.filter((item) => {
      if (platform !== "all" && item.platform !== platform) {
        return false;
      }
      if (source !== "all" && item.source !== source) {
        return false;
      }
      return true;
    });
    filtered.sort((left, right) => {
      let compare = 0;
      if (sortField === "updated_at") {
        compare = compareText(left.updated_at, right.updated_at);
      } else if (sortField === "name") {
        compare = compareText(left.name, right.name);
      } else if (sortField === "platform") {
        compare = compareText(left.platform ?? "", right.platform ?? "");
      } else if (sortField === "source") {
        compare = compareText(left.source ?? "", right.source ?? "");
      }
      return sortDirection === "asc" ? compare : -compare;
    });
    return filtered;
  }, [platform, programs, sortDirection, sortField, source]);

  function saveCurrentView() {
    const safeName = viewName.trim();
    if (!safeName) {
      return;
    }
    const next: SavedView = {
      id: `view:${Date.now()}`,
      name: safeName,
      query,
      platform,
      source,
      sortField,
      sortDirection,
    };
    setSavedViews((current) => [next, ...current].slice(0, 12));
    setViewName("");
  }

  function applySavedView(view: SavedView) {
    setQuery(view.query);
    setPlatform(view.platform);
    setSource(view.source);
    setSortField(view.sortField);
    setSortDirection(view.sortDirection);
  }

  function removeSavedView(viewId: string) {
    setSavedViews((current) => current.filter((view) => view.id !== viewId));
  }

  async function runIngestion() {
    setError("");
    try {
      await ingestArtifacts();
      setRefreshTick((value) => value + 1);
    } catch (reason: unknown) {
      const message = reason instanceof Error ? reason.message : "Ingestion failed";
      setError(message);
    }
  }

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #172 + #173</p>
        <h1 className="text-3xl font-semibold text-text">Bounty Feed</h1>
        <p className="max-w-3xl text-sm text-muted">
          Filter and sort imported programs, then save operator-specific views in local storage.
        </p>
      </header>

      <div className="grid gap-3 rounded-2xl border border-border bg-surface/85 p-4 lg:grid-cols-[2fr,1fr,1fr,1fr,auto]">
        <label className="space-y-1">
          <span className="text-xs uppercase tracking-[0.16em] text-muted">Search</span>
          <input
            className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Program name, handle, platform"
          />
        </label>

        <label className="space-y-1">
          <span className="text-xs uppercase tracking-[0.16em] text-muted">Platform</span>
          <select
            className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
            value={platform}
            onChange={(event) => setPlatform(event.target.value)}
          >
            <option value="all">All</option>
            {platforms.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>

        <label className="space-y-1">
          <span className="text-xs uppercase tracking-[0.16em] text-muted">Source</span>
          <select
            className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
            value={source}
            onChange={(event) => setSource(event.target.value)}
          >
            <option value="all">All</option>
            {sources.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>

        <label className="space-y-1">
          <span className="text-xs uppercase tracking-[0.16em] text-muted">Sort</span>
          <div className="flex gap-2">
            <select
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
              value={sortField}
              onChange={(event) => setSortField(event.target.value as SortField)}
            >
              <option value="updated_at">Updated</option>
              <option value="name">Name</option>
              <option value="platform">Platform</option>
              <option value="source">Source</option>
            </select>
            <select
              className="rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
              value={sortDirection}
              onChange={(event) => setSortDirection(event.target.value as SortDirection)}
            >
              <option value="desc">Desc</option>
              <option value="asc">Asc</option>
            </select>
          </div>
        </label>

        <button
          type="button"
          className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
          onClick={runIngestion}
        >
          Re-ingest
        </button>
      </div>

      <div className="rounded-2xl border border-border bg-surface/85 p-4">
        <div className="mb-3 flex flex-wrap items-end gap-2">
          <label className="flex-1 space-y-1">
            <span className="text-xs uppercase tracking-[0.16em] text-muted">Save current view</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
              value={viewName}
              onChange={(event) => setViewName(event.target.value)}
              placeholder="Example: Bugcrowd high signal"
            />
          </label>
          <button
            type="button"
            className="rounded-lg border border-border bg-bg/40 px-3 py-2 text-xs font-semibold text-text hover:border-accent"
            onClick={saveCurrentView}
          >
            Save view
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          {savedViews.length === 0 ? (
            <p className="text-xs text-muted">No saved views yet.</p>
          ) : null}
          {savedViews.map((view) => (
            <div key={view.id} className="flex items-center gap-2 rounded-lg border border-border bg-bg/30 px-2 py-1">
              <button
                type="button"
                className="text-xs font-semibold text-text hover:text-accent"
                onClick={() => applySavedView(view)}
              >
                {view.name}
              </button>
              <button
                type="button"
                className="text-xs text-muted hover:text-text"
                onClick={() => removeSavedView(view.id)}
                aria-label={`Delete saved view ${view.name}`}
              >
                x
              </button>
            </div>
          ))}
        </div>
      </div>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
      {loading ? <p className="text-sm text-muted">Loading programs...</p> : null}

      <div className="overflow-x-auto rounded-2xl border border-border bg-surface/85">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead className="border-b border-border bg-bg/30">
            <tr>
              <th className="px-4 py-3 font-semibold text-muted">Program</th>
              <th className="px-4 py-3 font-semibold text-muted">Platform</th>
              <th className="px-4 py-3 font-semibold text-muted">Source</th>
              <th className="px-4 py-3 font-semibold text-muted">Updated</th>
              <th className="px-4 py-3 font-semibold text-muted">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredPrograms.map((program) => (
              <tr key={program.id} className="border-b border-border/70">
                <td className="px-4 py-3">
                  <p className="font-semibold text-text">{program.name}</p>
                  <p className="text-xs text-muted">{program.id}</p>
                </td>
                <td className="px-4 py-3 text-muted">{program.platform ?? "-"}</td>
                <td className="px-4 py-3 text-muted">{program.source ?? "-"}</td>
                <td className="px-4 py-3 text-muted">{program.updated_at}</td>
                <td className="px-4 py-3">
                  <Link
                    to={`/feed/${encodeURIComponent(program.id)}`}
                    className="rounded-lg border border-border bg-bg/40 px-2 py-1 text-xs font-semibold text-text hover:border-accent"
                  >
                    Open details
                  </Link>
                </td>
              </tr>
            ))}
            {!loading && filteredPrograms.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-sm text-muted">
                  No programs match the current filter set.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
