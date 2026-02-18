import { FormEvent, useEffect, useState } from "react";
import {
  deleteFinding,
  exportFindings,
  importFindings,
  listFindings,
  upsertFinding,
  type FindingRow,
} from "../api/client";

type FindingFormState = {
  id: string;
  title: string;
  severity: string;
  status: string;
  description: string;
  impact: string;
  remediation: string;
};

const EMPTY_FORM: FindingFormState = {
  id: "",
  title: "",
  severity: "",
  status: "open",
  description: "",
  impact: "",
  remediation: "",
};

export function FindingsDbPage() {
  const [findings, setFindings] = useState<FindingRow[]>([]);
  const [form, setForm] = useState<FindingFormState>(EMPTY_FORM);
  const [importText, setImportText] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function refreshFindings() {
    const items = await listFindings();
    setFindings(items);
  }

  useEffect(() => {
    refreshFindings().catch((reason: unknown) => {
      const text = reason instanceof Error ? reason.message : "Failed to load findings";
      setError(text);
    });
  }, []);

  async function onSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      await upsertFinding({
        id: form.id.trim(),
        title: form.title.trim(),
        severity: form.severity.trim() || null,
        status: form.status.trim() || "open",
        description: form.description.trim() || null,
        impact: form.impact.trim() || null,
        remediation: form.remediation.trim() || null,
      });
      setForm(EMPTY_FORM);
      setMessage("Finding saved.");
      await refreshFindings();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to save finding";
      setError(text);
    }
  }

  async function onDelete(findingId: string) {
    setError("");
    setMessage("");
    try {
      await deleteFinding(findingId);
      setMessage(`Deleted ${findingId}.`);
      await refreshFindings();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to delete finding";
      setError(text);
    }
  }

  async function onExport() {
    setError("");
    setMessage("");
    try {
      const exported = await exportFindings();
      setImportText(JSON.stringify(exported, null, 2));
      setMessage(`Exported ${exported.length} finding records.`);
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to export findings";
      setError(text);
    }
  }

  async function onImport() {
    setError("");
    setMessage("");
    try {
      const parsed = JSON.parse(importText) as Record<string, unknown>[];
      if (!Array.isArray(parsed)) {
        throw new Error("Import payload must be a JSON array.");
      }
      const count = await importFindings(parsed, "command_center_ui");
      setMessage(`Imported ${count} findings.`);
      await refreshFindings();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to import findings";
      setError(text);
    }
  }

  function loadFindingIntoForm(item: FindingRow) {
    setForm({
      id: item.id,
      title: item.title,
      severity: item.severity ?? "",
      status: item.status ?? "open",
      description: item.description ?? "",
      impact: item.impact ?? "",
      remediation: item.remediation ?? "",
    });
  }

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #182</p>
        <h1 className="text-3xl font-semibold text-text">Findings DB</h1>
        <p className="max-w-3xl text-sm text-muted">
          Create, update, delete, and transfer findings JSON records through the Command Center API.
        </p>
      </header>

      <form className="space-y-3 rounded-2xl border border-border bg-surface/85 p-4" onSubmit={onSave}>
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Finding editor</p>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="space-y-1">
            <span className="text-xs text-muted">ID</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={form.id}
              onChange={(event) => setForm({ ...form, id: event.target.value })}
              required
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Title</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
              required
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Severity</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={form.severity}
              onChange={(event) => setForm({ ...form, severity: event.target.value })}
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Status</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={form.status}
              onChange={(event) => setForm({ ...form, status: event.target.value })}
            />
          </label>
        </div>
        <label className="space-y-1">
          <span className="text-xs text-muted">Description</span>
          <textarea
            className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
            rows={2}
            value={form.description}
            onChange={(event) => setForm({ ...form, description: event.target.value })}
          />
        </label>
        <label className="space-y-1">
          <span className="text-xs text-muted">Impact</span>
          <textarea
            className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
            rows={2}
            value={form.impact}
            onChange={(event) => setForm({ ...form, impact: event.target.value })}
          />
        </label>
        <label className="space-y-1">
          <span className="text-xs text-muted">Remediation</span>
          <textarea
            className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
            rows={2}
            value={form.remediation}
            onChange={(event) => setForm({ ...form, remediation: event.target.value })}
          />
        </label>
        <button
          type="submit"
          className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
        >
          Save finding
        </button>
      </form>

      <div className="grid gap-4 lg:grid-cols-[1fr,1fr]">
        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-xs uppercase tracking-[0.18em] text-muted">Current findings</p>
            <button
              type="button"
              className="rounded-lg border border-border bg-bg/30 px-2 py-1 text-xs text-text hover:border-accent"
              onClick={refreshFindings}
            >
              Refresh
            </button>
          </div>
          <div className="space-y-2">
            {findings.map((item) => (
              <div key={item.id} className="rounded-lg border border-border bg-bg/30 p-3">
                <p className="text-sm font-semibold text-text">{item.title}</p>
                <p className="text-xs text-muted">
                  {item.id} | {item.severity ?? "-"} | {item.status ?? "-"}
                </p>
                <div className="mt-2 flex gap-2">
                  <button
                    type="button"
                    className="rounded-lg border border-border bg-bg/50 px-2 py-1 text-xs text-text hover:border-accent"
                    onClick={() => loadFindingIntoForm(item)}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="rounded-lg border border-red-500/40 bg-red-500/10 px-2 py-1 text-xs text-red-200"
                    onClick={() => onDelete(item.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
            {findings.length === 0 ? <p className="cc-empty-state text-sm">No findings saved.</p> : null}
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Import / export JSON</p>
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              className="rounded-lg border border-border bg-bg/30 px-2 py-1 text-xs text-text hover:border-accent"
              onClick={onExport}
            >
              Export
            </button>
            <button
              type="button"
              className="rounded-lg border border-accent bg-accent/15 px-2 py-1 text-xs font-semibold text-text hover:bg-accent/25"
              onClick={onImport}
            >
              Import
            </button>
          </div>
          <textarea
            className="mt-3 h-[320px] w-full rounded-lg border border-border bg-bg/30 p-3 font-mono text-xs text-text"
            value={importText}
            onChange={(event) => setImportText(event.target.value)}
            placeholder='[{"id":"finding-001","title":"Example"}]'
          />
        </div>
      </div>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-300">{message}</p> : null}
    </section>
  );
}
