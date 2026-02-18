import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { clearApiSession, ensureApiSession } from "../api/client";
import { CommandPalette } from "../components/CommandPalette";
import type { NavItem } from "../routes";

type ThemeName = "amber-dark" | "sand-light";

const themeLabels: Record<ThemeName, string> = {
  "amber-dark": "Amber Dark",
  "sand-light": "Sand Light",
};

type AppShellProps = {
  items: NavItem[];
  children: ReactNode;
};

export function AppShell({ items, children }: AppShellProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [sessionState, setSessionState] = useState<"checking" | "ready" | "error">("checking");
  const [sessionError, setSessionError] = useState("");
  const [theme, setTheme] = useState<ThemeName>(() => {
    if (typeof window === "undefined") {
      return "amber-dark";
    }
    const saved = window.localStorage.getItem("command-center-theme");
    if (saved === "amber-dark" || saved === "sand-light") {
      return saved;
    }
    return "amber-dark";
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("command-center-theme", theme);
  }, [theme]);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const isShortcut = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k";
      if (!isShortcut) {
        return;
      }
      event.preventDefault();
      setPaletteOpen((value) => !value);
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  useEffect(() => {
    let active = true;
    setSessionState("checking");
    setSessionError("");
    ensureApiSession()
      .then((token) => {
        if (!active) {
          return;
        }
        if (token) {
          setSessionState("ready");
          return;
        }
        setSessionState("error");
        setSessionError("Session bootstrap failed.");
      })
      .catch((reason: unknown) => {
        if (!active) {
          return;
        }
        const message = reason instanceof Error ? reason.message : "Session bootstrap failed";
        setSessionState("error");
        setSessionError(message);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    function isEditableTarget(target: EventTarget | null): boolean {
      if (!(target instanceof HTMLElement)) {
        return false;
      }
      const tag = target.tagName.toLowerCase();
      return (
        tag === "input" ||
        tag === "textarea" ||
        target.isContentEditable ||
        target.getAttribute("role") === "textbox"
      );
    }

    function onKeyDown(event: KeyboardEvent) {
      if (isEditableTarget(event.target)) {
        return;
      }
      if (!event.altKey || event.ctrlKey || event.metaKey) {
        return;
      }
      if (!/^[1-9]$/.test(event.key)) {
        return;
      }
      const index = Number(event.key) - 1;
      const item = items[index];
      if (!item) {
        return;
      }
      event.preventDefault();
      navigate(item.path);
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [items, navigate]);

  function reconnectSession() {
    setSessionState("checking");
    setSessionError("");
    clearApiSession();
    ensureApiSession(true)
      .then((token) => {
        if (token) {
          setSessionState("ready");
          return;
        }
        setSessionState("error");
        setSessionError("Session bootstrap failed.");
      })
      .catch((reason: unknown) => {
        const message = reason instanceof Error ? reason.message : "Session bootstrap failed";
        setSessionState("error");
        setSessionError(message);
      });
  }

  const currentItem = useMemo(
    () =>
      items.find(
        (item) =>
          item.path === location.pathname || location.pathname.startsWith(`${item.path}/`),
      ) ?? items[0],
    [items, location.pathname],
  );

  return (
    <div className="min-h-screen bg-bg text-text">
      <div className="mx-auto flex min-h-screen max-w-[1600px]">
        <aside
          className={[
            "fixed inset-y-0 left-0 z-40 w-72 border-r border-border bg-surface/95 p-5 shadow-panel transition-transform duration-200 lg:static lg:translate-x-0 lg:shadow-none",
            mobileOpen ? "translate-x-0" : "-translate-x-full",
          ].join(" ")}
        >
          <div className="rounded-2xl border border-border bg-bg/60 p-4">
            <p className="text-xs uppercase tracking-[0.22em] text-muted">Bug Bounty</p>
            <h1 className="mt-2 text-xl font-semibold text-accentstrong">Command Center</h1>
            <p className="mt-1 text-xs text-muted">
              Operator cockpit for triage, execution controls, and reporting workflows.
            </p>
          </div>

          <nav className="mt-5 space-y-2">
            {items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  [
                    "block rounded-xl border px-4 py-3 transition",
                    isActive
                      ? "border-accent bg-accent/15 text-text"
                      : "border-border bg-bg/30 text-muted hover:border-accent/50 hover:text-text",
                  ].join(" ")
                }
              >
                <p className="text-sm font-semibold">{item.title}</p>
                <p className="mt-1 text-xs">{item.description}</p>
              </NavLink>
            ))}
          </nav>
        </aside>

        <div className="flex min-h-screen flex-1 flex-col lg:ml-0">
          <header className="sticky top-0 z-30 border-b border-border bg-surface/80 px-4 py-3 backdrop-blur lg:px-8">
            <div className="flex items-center gap-3">
              <button
                type="button"
                className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border text-text lg:hidden"
                onClick={() => setMobileOpen((value) => !value)}
                aria-label="Toggle navigation"
              >
                {mobileOpen ? "x" : "="}
              </button>

              <div className="min-w-0 flex-1 rounded-xl border border-border bg-bg/40 px-4 py-2">
                <p className="truncate text-sm font-semibold text-text">{currentItem.title}</p>
                <p className="truncate text-xs text-muted">{currentItem.description}</p>
              </div>

              <button
                type="button"
                className="rounded-lg border border-border bg-bg/50 px-3 py-2 text-xs font-semibold text-muted hover:text-text"
                onClick={() => setPaletteOpen(true)}
              >
                Command Palette
              </button>

              <button
                type="button"
                className={[
                  "rounded-lg border px-3 py-2 text-xs font-semibold",
                  sessionState === "ready"
                    ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
                    : sessionState === "checking"
                      ? "border-amber-500/40 bg-amber-500/10 text-amber-200"
                      : "border-red-500/40 bg-red-500/10 text-red-200",
                ].join(" ")}
                onClick={reconnectSession}
                title={sessionError || "Refresh API session"}
              >
                {sessionState === "ready"
                  ? "Session Ready"
                  : sessionState === "checking"
                    ? "Session Sync"
                    : "Session Error"}
              </button>

              <button
                type="button"
                className="rounded-lg border border-border bg-bg/50 px-3 py-2 text-xs font-semibold text-muted hover:text-text"
                onClick={() =>
                  setTheme((current) =>
                    current === "amber-dark" ? "sand-light" : "amber-dark",
                  )
                }
              >
                {themeLabels[theme]}
              </button>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 lg:px-8">{children}</main>
        </div>
      </div>

      {mobileOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-label="Close navigation"
        />
      ) : null}

      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} items={items} />
    </div>
  );
}
