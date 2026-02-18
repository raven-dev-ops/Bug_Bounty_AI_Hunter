import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  acknowledgeWorkspace,
  createWorkspace,
  listWorkspaces,
  type WorkspaceRow,
} from "../api/client";

function formatAckStatus(item: WorkspaceRow): string {
  if (item.roe_acknowledged) {
    return `Acknowledged at ${item.acknowledged_at ?? "unknown"}`;
  }
  return "Not acknowledged";
}

export function WorkspacesPage() {
  const [searchParams] = useSearchParams();
  const focusedWorkspaceId = searchParams.get("focus") ?? "";
  const [workspaces, setWorkspaces] = useState<WorkspaceRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState("");

  const [platform, setPlatform] = useState("bugcrowd");
  const [slug, setSlug] = useState("");
  const [name, setName] = useState("");
  const [engagementUrl, setEngagementUrl] = useState("");
  const [outRoot, setOutRoot] = useState("output/engagements");
  const [createError, setCreateError] = useState("");

  const [ackBy, setAckBy] = useState("");
  const [authorizedTarget, setAuthorizedTarget] = useState("");
  const [ackError, setAckError] = useState("");
  const [ackResult, setAckResult] = useState("");

  const refreshWorkspaces = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const items = await listWorkspaces();
      setWorkspaces(items);
      if (items.length > 0) {
        setSelectedWorkspaceId((current) => current || items[0].id);
      }
    } catch (reason: unknown) {
      const message = reason instanceof Error ? reason.message : "Failed to list workspaces";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshWorkspaces();
  }, [refreshWorkspaces]);

  useEffect(() => {
    if (focusedWorkspaceId) {
      setSelectedWorkspaceId(focusedWorkspaceId);
    }
  }, [focusedWorkspaceId]);

  const selectedWorkspace = useMemo(
    () => workspaces.find((item) => item.id === selectedWorkspaceId) ?? null,
    [selectedWorkspaceId, workspaces],
  );

  async function onCreateWorkspace(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCreateError("");
    try {
      const created = await createWorkspace({
        platform: platform.trim(),
        slug: slug.trim(),
        name: name.trim(),
        engagement_url: engagementUrl.trim(),
        root_dir: outRoot.trim(),
        scaffold_files: true,
      });
      setSlug("");
      setName("");
      setEngagementUrl("");
      setSelectedWorkspaceId(created.id);
      await refreshWorkspaces();
    } catch (reason: unknown) {
      const message = reason instanceof Error ? reason.message : "Workspace creation failed";
      setCreateError(message);
    }
  }

  async function onAcknowledge(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedWorkspaceId) {
      return;
    }
    setAckError("");
    setAckResult("");
    try {
      const updated = await acknowledgeWorkspace(selectedWorkspaceId, {
        acknowledged_by: ackBy.trim(),
        authorized_target: authorizedTarget.trim(),
      });
      setAckResult(updated.id);
      await refreshWorkspaces();
    } catch (reason: unknown) {
      const message = reason instanceof Error ? reason.message : "ROE acknowledgement failed";
      setAckError(message);
    }
  }

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #175 + #176</p>
        <h1 className="text-3xl font-semibold text-text">Engagement Workspaces</h1>
        <p className="max-w-3xl text-sm text-muted">
          Create engagement folders and record ROE acknowledgement before run mode execution.
        </p>
      </header>

      <form className="space-y-3 rounded-2xl border border-border bg-surface/85 p-4" onSubmit={onCreateWorkspace}>
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Create workspace</p>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="space-y-1">
            <span className="text-xs text-muted">Platform</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
              value={platform}
              onChange={(event) => setPlatform(event.target.value)}
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Slug</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
              value={slug}
              onChange={(event) => setSlug(event.target.value)}
              required
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Name</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Engagement URL</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
              value={engagementUrl}
              onChange={(event) => setEngagementUrl(event.target.value)}
            />
          </label>
          <label className="space-y-1 md:col-span-2">
            <span className="text-xs text-muted">Workspace output root</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
              value={outRoot}
              onChange={(event) => setOutRoot(event.target.value)}
            />
          </label>
        </div>
        <button
          type="submit"
          className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
        >
          Create and scaffold
        </button>
        {createError ? <p className="text-sm text-red-300">{createError}</p> : null}
      </form>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
      {loading ? <p className="cc-empty-state text-sm">Loading workspaces...</p> : null}

      <div className="grid gap-4 lg:grid-cols-[1.5fr,1fr]">
        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Workspace list</p>
          <div className="mt-3 space-y-2">
            {workspaces.map((item) => (
              <button
                key={item.id}
                type="button"
                className={[
                  "w-full rounded-xl border p-3 text-left transition",
                  item.id === selectedWorkspaceId
                    ? "border-accent bg-accent/10"
                    : "border-border bg-bg/30 hover:border-accent/60",
                ].join(" ")}
                onClick={() => setSelectedWorkspaceId(item.id)}
              >
                <p className="text-sm font-semibold text-text">{item.name}</p>
                <p className="text-xs text-muted">{item.id}</p>
                <p className="mt-1 text-xs text-muted">
                  <span className="cc-pill">{formatAckStatus(item)}</span>
                </p>
              </button>
            ))}
            {workspaces.length === 0 ? (
              <p className="cc-empty-state text-sm">No workspaces created yet.</p>
            ) : null}
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">ROE acknowledgement</p>
          {selectedWorkspace ? (
            <>
              <p className="mt-2 text-sm text-text">{selectedWorkspace.name}</p>
              <p className="text-xs text-muted">{selectedWorkspace.root_dir ?? "-"}</p>
              <p
                className={[
                  "mt-2 rounded-lg border px-2 py-1 text-xs",
                  selectedWorkspace.roe_acknowledged
                    ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
                    : "border-amber-500/40 bg-amber-500/10 text-amber-200",
                ].join(" ")}
              >
                {selectedWorkspace.roe_acknowledged
                  ? "Run mode unlocked for this workspace."
                  : "Run mode locked until acknowledgement is recorded."}
              </p>

              <form className="mt-3 space-y-2" onSubmit={onAcknowledge}>
                <label className="space-y-1">
                  <span className="text-xs text-muted">Acknowledged by</span>
                  <input
                    className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
                    value={ackBy}
                    onChange={(event) => setAckBy(event.target.value)}
                    required
                  />
                </label>
                <label className="space-y-1">
                  <span className="text-xs text-muted">Authorized target</span>
                  <input
                    className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
                    value={authorizedTarget}
                    onChange={(event) => setAuthorizedTarget(event.target.value)}
                    required
                  />
                </label>
                <button
                  type="submit"
                  className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
                >
                  Record acknowledgement
                </button>
                {ackError ? <p className="text-xs text-red-300">{ackError}</p> : null}
                {ackResult ? (
                  <p className="text-xs text-emerald-300">Acknowledgement recorded for {ackResult}.</p>
                ) : null}
              </form>
            </>
          ) : (
            <p className="mt-3 text-sm text-muted">Select a workspace to manage its ROE status.</p>
          )}
        </div>
      </div>
    </section>
  );
}
