import { Navigate, Route, Routes } from "react-router-dom";
import { BountyDetailPage } from "./pages/BountyDetailPage";
import { BountyFeedPage } from "./pages/BountyFeedPage";
import { PagePlaceholder } from "./pages/PagePlaceholder";
import { WorkspacesPage } from "./pages/WorkspacesPage";
import { navItems } from "./routes";
import { AppShell } from "./shell/AppShell";

export function App() {
  return (
    <AppShell items={navItems}>
      <Routes>
        <Route path="/" element={<Navigate to="/feed" replace />} />
        <Route
          path="/overview"
          element={
            <PagePlaceholder
              title="Overview"
              description="Live pipeline pulse and mission status."
            />
          }
        />
        <Route path="/feed" element={<BountyFeedPage />} />
        <Route path="/feed/:programId" element={<BountyDetailPage />} />
        <Route path="/workspaces" element={<WorkspacesPage />} />
        <Route
          path="/reports"
          element={
            <PagePlaceholder
              title="Reports"
              description="Drafts, exports, and delivery tasks."
            />
          }
        />
        <Route
          path="/settings"
          element={
            <PagePlaceholder
              title="Settings"
              description="Config, guardrails, and operator preferences."
            />
          }
        />
        <Route path="*" element={<Navigate to="/feed" replace />} />
      </Routes>
    </AppShell>
  );
}
