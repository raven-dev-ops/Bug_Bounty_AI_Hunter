import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { completeOidcSignInFromCallback, getApiAuthMode } from "../api/client";

export function AuthCallbackPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  useEffect(() => {
    if (getApiAuthMode() !== "oidc_pkce") {
      navigate("/feed", { replace: true });
      return;
    }

    let active = true;
    completeOidcSignInFromCallback()
      .then((result) => {
        if (!active) {
          return;
        }
        if (result.ok) {
          navigate(result.returnTo || "/feed", { replace: true });
          return;
        }
        setError(result.error);
      })
      .catch((reason: unknown) => {
        if (!active) {
          return;
        }
        const message =
          reason instanceof Error ? reason.message : "Failed to complete OIDC sign-in callback.";
        setError(message);
      });

    return () => {
      active = false;
    };
  }, [navigate]);

  return (
    <section className="mx-auto flex min-h-screen max-w-2xl items-center px-6 py-12">
      <div className="w-full space-y-4 rounded-2xl border border-border bg-surface/90 p-6 shadow-panel">
        <p className="text-xs uppercase tracking-[0.22em] text-muted">Command Center</p>
        <h1 className="text-2xl font-semibold text-text">Completing sign-in</h1>
        {error ? (
          <p className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
            {error}
          </p>
        ) : (
          <p className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-200">
            Finalizing OIDC session and redirecting to the console.
          </p>
        )}
      </div>
    </section>
  );
}
