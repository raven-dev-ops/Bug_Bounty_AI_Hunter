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
    path: "/reports",
    title: "Reports",
    description: "Drafts, exports, and delivery tasks.",
  },
  {
    path: "/settings",
    title: "Settings",
    description: "Config, guardrails, and operator preferences.",
  },
];
