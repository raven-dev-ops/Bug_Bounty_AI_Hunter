import { Navigate, Route, Routes } from "react-router-dom";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { AuthCallbackPage } from "./pages/AuthCallbackPage";
import { BountyDetailPage } from "./pages/BountyDetailPage";
import { BountyFeedPage } from "./pages/BountyFeedPage";
import { DocsPage } from "./pages/DocsPage";
import { FindingsDbPage } from "./pages/FindingsDbPage";
import { LogsPage } from "./pages/LogsPage";
import { NotificationsPage } from "./pages/NotificationsPage";
import { PagePlaceholder } from "./pages/PagePlaceholder";
import { ReportsPage } from "./pages/ReportsPage";
import { TaskBoardPage } from "./pages/TaskBoardPage";
import { ToolsHubPage } from "./pages/ToolsHubPage";
import { VisualizationPage } from "./pages/VisualizationPage";
import { WorkspacesPage } from "./pages/WorkspacesPage";
import { navItems } from "./routes";
import { AppShell } from "./shell/AppShell";

function ShellRoutes() {
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
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/scope-map" element={<VisualizationPage />} />
        <Route path="/feed" element={<BountyFeedPage />} />
        <Route path="/feed/:programId" element={<BountyDetailPage />} />
        <Route path="/workspaces" element={<WorkspacesPage />} />
        <Route path="/tasks" element={<TaskBoardPage />} />
        <Route path="/tools" element={<ToolsHubPage />} />
        <Route path="/findings" element={<FindingsDbPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/docs" element={<DocsPage />} />
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

export function App() {
  return (
    <Routes>
      <Route path="/auth/callback" element={<AuthCallbackPage />} />
      <Route path="*" element={<ShellRoutes />} />
    </Routes>
  );
}
