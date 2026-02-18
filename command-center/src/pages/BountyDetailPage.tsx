import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { createWorkspace, getProgram, type ProgramRow } from "../api/client";

function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 64);
}

function deriveConflicts(program: ProgramRow): string[] {
  const conflicts: string[] = [];
  const rawName = typeof program.raw_json.name === "string" ? program.raw_json.name : "";
  const rawPlatform =
    typeof program.raw_json.platform === "string" ? program.raw_json.platform : "";
  if (rawName && rawName !== program.name) {
    conflicts.push(`Normalized name "${program.name}" differs from raw source "${rawName}".`);
  }
  if (rawPlatform && rawPlatform !== (program.platform ?? "")) {
    conflicts.push(
      `Normalized platform "${program.platform ?? "-"}" differs from raw source "${rawPlatform}".`,
    );
  }
  if (!program.policy_url) {
    conflicts.push("Program policy URL is missing from normalized fields.");
  }
  return conflicts;
}

export function BountyDetailPage() {
  const params = useParams<{ programId: string }>();
  const programId = decodeURIComponent(params.programId ?? "");
  const [program, setProgram] = useState<ProgramRow | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [createError, setCreateError] = useState("");
  const [createResult, setCreateResult] = useState("");
  const [platform, setPlatform] = useState("");
  const [slug, setSlug] = useState("");
  const [workspaceName, setWorkspaceName] = useState("");
  const [engagementUrl, setEngagementUrl] = useState("");
  const [outRoot, setOutRoot] = useState("output/engagements");

  useEffect(() => {
    if (!programId) {
      setError("Program id is missing from URL.");
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError("");
    getProgram(programId)
      .then((item) => {
        if (cancelled) {
          return;
        }
        setProgram(item);
        setPlatform(item.platform ?? "board");
        setSlug(item.handle ?? slugify(item.name));
        setWorkspaceName(item.name);
        setEngagementUrl(item.policy_url ?? "");
      })
      .catch((reason: unknown) => {
        if (cancelled) {
          return;
        }
        const message = reason instanceof Error ? reason.message : "Failed to load program";
        setError(message);
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [programId]);

  const conflicts = useMemo(() => (program ? deriveConflicts(program) : []), [program]);
  const rawPreview = useMemo(() => {
    if (!program) {
      return "";
    }
    return JSON.stringify(program.raw_json, null, 2);
  }, [program]);

  async function onCreateWorkspace(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!program) {
      return;
    }
    setCreateError("");
    setCreateResult("");
    try {
      const workspace = await createWorkspace({
        platform: platform.trim(),
        slug: slug.trim(),
        name: workspaceName.trim(),
        engagement_url: engagementUrl.trim(),
        root_dir: outRoot.trim(),
        scaffold_files: true,
      });
      setCreateResult(workspace.id);
    } catch (reason: unknown) {
      const message = reason instanceof Error ? reason.message : "Failed to create workspace";
      setCreateError(message);
    }
  }

  if (loading) {
    return <p className="cc-empty-state text-sm">Loading program details...</p>;
  }

  if (error) {
    return (
      <section className="space-y-4 animate-shell-enter">
        <p className="text-sm text-red-300">{error}</p>
        <Link to="/feed" className="text-sm text-accent underline underline-offset-2">
          Back to feed
        </Link>
      </section>
    );
  }

  if (!program) {
    return <p className="cc-empty-state text-sm">Program not found.</p>;
  }

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #174 + #175</p>
        <h1 className="text-3xl font-semibold text-text">{program.name}</h1>
        <p className="text-sm text-muted">Program ID: {program.id}</p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Overview</p>
          <dl className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between gap-3">
              <dt className="text-muted">Platform</dt>
                <dd className="text-text">
                  <span className="cc-pill">{program.platform ?? "-"}</span>
                </dd>
            </div>
            <div className="flex justify-between gap-3">
              <dt className="text-muted">Handle</dt>
                <dd className="text-text">
                  <span className="cc-pill">{program.handle ?? "-"}</span>
                </dd>
            </div>
            <div className="flex justify-between gap-3">
              <dt className="text-muted">Source</dt>
                <dd className="text-text">
                  <span className="cc-pill">{program.source ?? "-"}</span>
                </dd>
            </div>
            <div className="flex justify-between gap-3">
              <dt className="text-muted">Policy URL</dt>
              <dd className="text-text">
                {program.policy_url ? (
                  <a
                    href={program.policy_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-accent underline underline-offset-2"
                  >
                    Open
                  </a>
                ) : (
                  "-"
                )}
              </dd>
            </div>
          </dl>
        </div>

        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Provenance + conflicts</p>
          <ul className="mt-3 space-y-2 text-sm text-muted">
            <li>Normalized source: {program.source ?? "-"}</li>
            <li>Last updated: {program.updated_at}</li>
            {conflicts.map((entry) => (
              <li key={entry} className="text-amber-300">
                {entry}
              </li>
            ))}
            {conflicts.length === 0 ? (
              <li className="cc-empty-state text-emerald-300">No conflicts detected.</li>
            ) : null}
          </ul>
        </div>
      </div>

      <form className="space-y-3 rounded-2xl border border-border bg-surface/85 p-4" onSubmit={onCreateWorkspace}>
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Create engagement workspace</p>
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
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Workspace name</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text outline-none focus:border-accent"
              value={workspaceName}
              onChange={(event) => setWorkspaceName(event.target.value)}
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
          Create workspace
        </button>

        {createError ? <p className="text-sm text-red-300">{createError}</p> : null}
        {createResult ? (
          <p className="text-sm text-emerald-300">
            Workspace created:{" "}
            <Link
              to={`/workspaces?focus=${encodeURIComponent(createResult)}`}
              className="underline underline-offset-2"
            >
              {createResult}
            </Link>
          </p>
        ) : null}
      </form>

      <div className="rounded-2xl border border-border bg-surface/85 p-4">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Raw record</p>
        <pre className="mt-3 max-h-[360px] overflow-auto rounded-lg border border-border bg-bg/40 p-3 text-xs text-muted">
          {rawPreview}
        </pre>
      </div>

      <Link to="/feed" className="text-sm text-accent underline underline-offset-2">
        Back to feed
      </Link>
    </section>
  );
}
