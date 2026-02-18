import { useEffect } from "react";
import type { NavItem } from "../routes";

type CommandPaletteProps = {
  open: boolean;
  onClose: () => void;
  items: NavItem[];
};

export function CommandPalette({ open, onClose, items }: CommandPaletteProps) {
  useEffect(() => {
    if (!open) {
      return;
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-bg/70 px-4 pt-16 backdrop-blur-sm" role="dialog" aria-modal="true">
      <div className="w-full max-w-2xl rounded-2xl border border-border bg-surface/95 shadow-panel">
        <header className="border-b border-border px-5 py-4">
          <p className="text-xs uppercase tracking-[0.2em] text-muted">Command Palette</p>
          <h2 className="mt-1 text-lg font-semibold text-text">Quick actions</h2>
        </header>
        <ul className="space-y-2 p-4">
          {items.map((item, index) => (
            <li key={item.path} className="rounded-xl border border-border/70 bg-bg/40 px-4 py-3">
              <p className="text-sm font-medium text-text">{item.title}</p>
              <p className="mt-1 text-xs text-muted">{item.description}</p>
              <p className="mt-2 text-xs text-accent">Shortcut: Alt+{index + 1}</p>
            </li>
          ))}
        </ul>
        <footer className="border-t border-border px-5 py-3 text-xs text-muted">
          Skeleton only for MVP scaffold. Connect actions to runtime commands in follow-up issues.
        </footer>
      </div>
    </div>
  );
}
