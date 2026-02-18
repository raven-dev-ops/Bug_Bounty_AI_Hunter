export type NavItem = {
  path: string;
  title: string;
  description: string;
};

export const navItems: NavItem[] = [
  {
    path: "/overview",
    title: "Overview",
    description: "Live pipeline pulse and mission status.",
  },
  {
    path: "/feed",
    title: "Bounty Feed",
    description: "Incoming opportunities and triage queue.",
  },
  {
    path: "/workspaces",
    title: "Workspaces",
    description: "Engagement launch points and ROE checkpoints.",
  },
  {
    path: "/tools",
    title: "Tools Hub",
    description: "Script catalog, runner controls, and artifacts.",
  },
  {
    path: "/findings",
    title: "Findings DB",
    description: "CRUD and JSON import/export for findings.",
  },
  {
    path: "/reports",
    title: "Reports",
    description: "Drafts, exports, and delivery tasks.",
  },
  {
    path: "/logs",
    title: "Logs",
    description: "Tool run status, errors, and searchable output.",
  },
  {
    path: "/notifications",
    title: "Notifications",
    description: "Alerts and integration placeholders.",
  },
  {
    path: "/docs",
    title: "Docs",
    description: "In-app docs search and markdown view.",
  },
  {
    path: "/settings",
    title: "Settings",
    description: "Config, guardrails, and operator preferences.",
  },
];
