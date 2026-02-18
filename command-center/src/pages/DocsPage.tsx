import { FormEvent, useState } from "react";
import { loadDocPage, searchDocs, type DocSearchResult } from "../api/client";

export function DocsPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<DocSearchResult[]>([]);
  const [activePath, setActivePath] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");

  async function onSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    try {
      const items = await searchDocs(query, 40);
      setResults(items);
      if (items.length > 0) {
        await openPage(items[0].path);
      } else {
        setActivePath("");
        setContent("");
      }
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Docs search failed";
      setError(text);
    }
  }

  async function openPage(path: string) {
    setError("");
    try {
      const page = await loadDocPage(path);
      setActivePath(page.path);
      setContent(page.content);
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to load doc page";
      setError(text);
    }
  }

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #185</p>
        <h1 className="text-3xl font-semibold text-text">Help Docs</h1>
        <p className="max-w-3xl text-sm text-muted">
          Search markdown docs from the repo and open pages directly in the command-center UI.
        </p>
      </header>

      <form className="flex gap-2 rounded-2xl border border-border bg-surface/85 p-4" onSubmit={onSearch}>
        <input
          className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search docs, for example: ROE acknowledgement"
        />
        <button
          type="submit"
          className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
        >
          Search
        </button>
      </form>

      <div className="grid gap-4 lg:grid-cols-[1fr,1.2fr]">
        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Results</p>
          <div className="mt-3 space-y-2">
            {results.map((item) => (
              <button
                key={item.path}
                type="button"
                className={[
                  "w-full rounded-lg border px-3 py-2 text-left",
                  activePath === item.path
                    ? "border-accent bg-accent/15"
                    : "border-border bg-bg/30 hover:border-accent/60",
                ].join(" ")}
                onClick={() => openPage(item.path)}
              >
                <p className="text-sm font-semibold text-text">{item.title}</p>
                <p className="text-xs text-muted">{item.path}</p>
                <p className="mt-1 text-xs text-muted">{item.snippet}</p>
              </button>
            ))}
            {results.length === 0 ? <p className="text-sm text-muted">Run a search to see doc matches.</p> : null}
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Doc page</p>
          <p className="mt-2 text-xs text-muted">{activePath || "No page selected"}</p>
          <pre className="mt-3 max-h-[520px] overflow-auto rounded-lg border border-border bg-bg/40 p-3 text-xs text-muted">
            {content || "Select a result to view markdown content."}
          </pre>
        </div>
      </div>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
    </section>
  );
}
