import type { ReactNode } from "react";

type PagePlaceholderProps = {
  title: string;
  description: string;
};

function Tile({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-2xl border border-border/80 bg-surface/85 p-5 shadow-panel backdrop-blur">
      {children}
    </div>
  );
}

export function PagePlaceholder({ title, description }: PagePlaceholderProps) {
  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Command Center</p>
        <h1 className="text-3xl font-semibold text-text">{title}</h1>
        <p className="max-w-3xl text-sm text-muted">{description}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <Tile>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Status</p>
          <p className="mt-3 text-lg font-semibold text-accent">Operational baseline online</p>
          <p className="mt-2 text-sm text-muted">Routing, shell actions, and API session bootstrap are active.</p>
        </Tile>
        <Tile>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Workflow</p>
          <p className="mt-3 text-lg font-semibold text-text">Drive tasks through the board</p>
          <p className="mt-2 text-sm text-muted">Use linked findings, runs, and reports to keep delivery traceable.</p>
        </Tile>
        <Tile>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Guardrails</p>
          <p className="mt-3 text-lg font-semibold text-text">ROE-first workflow</p>
          <p className="mt-2 text-sm text-muted">Execution flows stay gated behind explicit ROE acknowledgment.</p>
        </Tile>
      </div>
    </section>
  );
}
