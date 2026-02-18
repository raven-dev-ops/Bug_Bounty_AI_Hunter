import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  generateIssueDrafts,
  generateReportBundle,
  listWorkspaces,
  type WorkspaceRow,
} from "../api/client";

type ReportResult = {
  runId: string;
  status: string;
  files: string[];
};

export function ReportsPage() {
  const [workspaces, setWorkspaces] = useState<WorkspaceRow[]>([]);
  const [workspaceId, setWorkspaceId] = useState("");

  const [findingsPath, setFindingsPath] = useState("examples/outputs/findings.json");
  const [targetProfilePath, setTargetProfilePath] = useState(
    "examples/target_profile_minimal.yaml",
  );
  const [bundleOutDir, setBundleOutDir] = useState("output/command_center/report_bundle");
  const [evidencePath, setEvidencePath] = useState("examples/evidence_example.json");
  const [reproStepsPath, setReproStepsPath] = useState("examples/repro_steps.json");

  const [draftOutDir, setDraftOutDir] = useState("output/command_center/issue_drafts");
  const [platform, setPlatform] = useState("github");

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [bundleResult, setBundleResult] = useState<ReportResult | null>(null);
  const [draftResult, setDraftResult] = useState<ReportResult | null>(null);

  useEffect(() => {
    listWorkspaces()
      .then((items) => {
        setWorkspaces(items);
        if (items.length > 0) {
          setWorkspaceId(items[0].id);
        }
      })
      .catch(() => {
        // Keep optional workspace selector empty on error.
      });
  }, []);

  async function onGenerateBundle(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      const result = await generateReportBundle({
        findings_path: findingsPath,
        target_profile_path: targetProfilePath,
        output_dir: bundleOutDir,
        evidence_path: evidencePath || undefined,
        repro_steps_path: reproStepsPath || undefined,
        workspace_id: workspaceId || undefined,
      });
      setBundleResult({
        runId: result.run.id,
        status: result.run.status,
        files: result.files,
      });
      setMessage("Report bundle execution finished.");
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to generate report bundle";
      setError(text);
    }
  }

  async function onGenerateIssueDrafts(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      const result = await generateIssueDrafts({
        findings_path: `${bundleOutDir}/findings.json`,
        target_profile_path: targetProfilePath,
        output_dir: draftOutDir,
        platform,
        workspace_id: workspaceId || undefined,
      });
      setDraftResult({
        runId: result.run.id,
        status: result.run.status,
        files: result.files,
      });
      setMessage("Issue draft export finished.");
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to generate issue drafts";
      setError(text);
    }
  }

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #180 + #181</p>
        <h1 className="text-3xl font-semibold text-text">Report Composer</h1>
        <p className="max-w-3xl text-sm text-muted">
          Trigger report bundle and issue draft scripts from the UI and review generated artifacts.
        </p>
      </header>

      <p className="text-sm text-muted">
        Findings are managed from the{" "}
        <Link to="/findings" className="text-accent underline underline-offset-2">
          Findings DB page
        </Link>
        .
      </p>

      <div className="grid gap-4 lg:grid-cols-[1fr,1fr]">
        <form className="space-y-3 rounded-2xl border border-border bg-surface/85 p-4" onSubmit={onGenerateBundle}>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Generate report bundle</p>
          <label className="space-y-1">
            <span className="text-xs text-muted">Workspace (optional)</span>
            <select
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={workspaceId}
              onChange={(event) => setWorkspaceId(event.target.value)}
            >
              <option value="">None</option>
              {workspaces.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Findings path</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={findingsPath}
              onChange={(event) => setFindingsPath(event.target.value)}
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Target profile path</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={targetProfilePath}
              onChange={(event) => setTargetProfilePath(event.target.value)}
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Output dir</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={bundleOutDir}
              onChange={(event) => setBundleOutDir(event.target.value)}
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Evidence path</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={evidencePath}
              onChange={(event) => setEvidencePath(event.target.value)}
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Repro steps path</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={reproStepsPath}
              onChange={(event) => setReproStepsPath(event.target.value)}
            />
          </label>
          <button
            type="submit"
            className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
          >
            Run report bundle
          </button>
          {bundleResult ? (
            <div className="rounded-lg border border-border bg-bg/30 p-3">
              <p className="text-xs text-muted">Run: {bundleResult.runId}</p>
              <p className="text-xs text-muted">Status: {bundleResult.status}</p>
              <ul className="mt-2 space-y-1 text-xs text-text">
                {bundleResult.files.map((file) => (
                  <li key={file}>{file}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </form>

        <form className="space-y-3 rounded-2xl border border-border bg-surface/85 p-4" onSubmit={onGenerateIssueDrafts}>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Generate issue drafts</p>
          <label className="space-y-1">
            <span className="text-xs text-muted">Platform</span>
            <select
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={platform}
              onChange={(event) => setPlatform(event.target.value)}
            >
              <option value="github">github</option>
              <option value="hackerone">hackerone</option>
              <option value="bugcrowd">bugcrowd</option>
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Draft output dir</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={draftOutDir}
              onChange={(event) => setDraftOutDir(event.target.value)}
            />
          </label>
          <p className="text-xs text-muted">
            Uses findings from: <code>{bundleOutDir}/findings.json</code>
          </p>
          <button
            type="submit"
            className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
          >
            Run issue draft export
          </button>
          {draftResult ? (
            <div className="rounded-lg border border-border bg-bg/30 p-3">
              <p className="text-xs text-muted">Run: {draftResult.runId}</p>
              <p className="text-xs text-muted">Status: {draftResult.status}</p>
              <ul className="mt-2 space-y-1 text-xs text-text">
                {draftResult.files.map((file) => (
                  <li key={file}>{file}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </form>
      </div>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-300">{message}</p> : null}
    </section>
  );
}
