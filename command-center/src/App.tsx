import { Navigate, Route, Routes } from "react-router-dom";
import { PagePlaceholder } from "./pages/PagePlaceholder";
import { navItems } from "./routes";
import { AppShell } from "./shell/AppShell";

export function App() {
  return (
    <AppShell items={navItems}>
      <Routes>
        <Route path="/" element={<Navigate to="/overview" replace />} />
        {navItems.map((item) => (
          <Route
            key={item.path}
            path={item.path}
            element={<PagePlaceholder title={item.title} description={item.description} />}
          />
        ))}
      </Routes>
    </AppShell>
  );
}
