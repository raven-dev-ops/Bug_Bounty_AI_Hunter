import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { NavItem } from "../routes";

type CommandPaletteProps = {
  open: boolean;
  onClose: () => void;
  items: NavItem[];
};

function normalize(value: string): string {
  return value.trim().toLowerCase();
}

export function CommandPalette({ open, onClose, items }: CommandPaletteProps) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  const filteredItems = useMemo(() => {
    const safeQuery = normalize(query);
    if (!safeQuery) {
      return items;
    }
    return items.filter((item) => {
      const haystack = normalize(`${item.title} ${item.description} ${item.path}`);
      return haystack.includes(safeQuery);
    });
  }, [items, query]);

  useEffect(() => {
    if (!open) {
      return;
    }
    setQuery("");
    setActiveIndex(0);
  }, [open]);

  useEffect(() => {
    if (activeIndex < filteredItems.length) {
      return;
    }
    setActiveIndex(0);
  }, [activeIndex, filteredItems.length]);

  useEffect(() => {
    if (!open) {
      return;
    }
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveIndex((value) => {
          if (filteredItems.length === 0) {
            return 0;
          }
          return (value + 1) % filteredItems.length;
        });
        return;
      }
      if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIndex((value) => {
          if (filteredItems.length === 0) {
            return 0;
          }
          return (value - 1 + filteredItems.length) % filteredItems.length;
        });
        return;
      }
      if (event.key === "Enter") {
        if (filteredItems.length === 0) {
          return;
        }
        event.preventDefault();
        const target = filteredItems[Math.min(activeIndex, filteredItems.length - 1)];
        navigate(target.path);
        onClose();
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [activeIndex, filteredItems, navigate, onClose, open]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-bg/70 px-4 pt-16 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl rounded-2xl border border-border bg-surface/95 shadow-panel"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="border-b border-border px-5 py-4">
          <p className="text-xs uppercase tracking-[0.2em] text-muted">Command Palette</p>
          <h2 className="mt-1 text-lg font-semibold text-text">Jump to any page</h2>
          <p className="mt-1 text-xs text-muted">
            Use <span className="text-accent">Arrow keys</span> +{" "}
            <span className="text-accent">Enter</span> or <span className="text-accent">Alt+1..9</span>.
          </p>
        </header>

        <div className="border-b border-border px-4 py-3">
          <input
            autoFocus
            className="w-full rounded-lg border border-border bg-bg/35 px-3 py-2 text-sm text-text outline-none focus:border-accent"
            placeholder="Search pages, for example: logs or reports"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setActiveIndex(0);
            }}
          />
        </div>

        <ul className="max-h-[420px] space-y-2 overflow-auto p-4">
          {filteredItems.map((item, index) => (
            <li key={item.path}>
              <button
                type="button"
                className={[
                  "w-full rounded-xl border px-4 py-3 text-left transition",
                  activeIndex === index
                    ? "border-accent bg-accent/15"
                    : "border-border/70 bg-bg/40 hover:border-accent/60",
                ].join(" ")}
                onMouseEnter={() => setActiveIndex(index)}
                onClick={() => {
                  navigate(item.path);
                  onClose();
                }}
              >
                <p className="text-sm font-medium text-text">
                  {item.title} <span className="text-xs text-accent">Alt+{index + 1}</span>
                </p>
                <p className="mt-1 text-xs text-muted">{item.description}</p>
              </button>
            </li>
          ))}
          {filteredItems.length === 0 ? (
            <li className="rounded-xl border border-border/70 bg-bg/35 px-4 py-3 text-sm text-muted">
              No route matches this search.
            </li>
          ) : null}
        </ul>
      </div>
    </div>
  );
}
