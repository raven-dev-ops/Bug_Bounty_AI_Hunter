# Command Center Frontend Scaffold

This app scaffolds issue delivery for:
- #165 Scaffold frontend app
- #166 Implement app shell navigation
- #167 Implement dark-yellow design tokens
- #172 Build Bounty Feed page
- #173 Build saved views
- #174 Build Bounty Detail page
- #175 Engagement workspace creation
- #176 ROE acknowledgement UI
- #177 Tools Hub: script catalog
- #178 Tool runner API endpoint
- #179 Tool runner UI
- #180 Report Composer MVP
- #181 Issue draft exports UI
- #182 Findings DB UI
- #183 Logs page MVP
- #184 Notifications center MVP
- #185 Help/Docs embedding
- #186 Frontend CI pipeline
- #187 Backend CI pipeline

## Stack
- React + TypeScript (Vite)
- Tailwind CSS
- React Router

## Run locally
1. `cd command-center`
2. `npm install`
3. `npm run dev`
4. `npm run lint`
5. `npm run test`

## Current scope
- Route shell plus implemented Feed/Detail/Workspace pages
- Responsive left navigation and top command bar
- Command palette skeleton (`Ctrl+K`)
- Dark-yellow design tokens with theme toggle
- Program feed table backed by `/api/programs` with local saved filter views
- Program detail view with provenance/conflict display and workspace creation form
- Workspace list + ROE acknowledgement UI backed by `/api/workspaces` endpoints
- Tools Hub and runner UI backed by `/api/tools`, `/api/runs`, and `/api/runs/execute`
- Report composer actions for report bundles and issue draft exports
- Findings DB CRUD with JSON import/export controls
- Logs view for searchable tool runs and log tails
- Notifications center with placeholder channel settings and read state controls
- In-app docs search and markdown page renderer backed by API endpoints
- Frontend lint/typecheck/unit tests wired into CI (`npm run lint`, `npm run test`, `npm run build`)
