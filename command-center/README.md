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

## Stack
- React + TypeScript (Vite)
- Tailwind CSS
- React Router

## Run locally
1. `cd command-center`
2. `npm install`
3. `npm run dev`

## Current scope
- Route shell plus implemented Feed/Detail/Workspace pages
- Responsive left navigation and top command bar
- Command palette skeleton (`Ctrl+K`)
- Dark-yellow design tokens with theme toggle
- Program feed table backed by `/api/programs` with local saved filter views
- Program detail view with provenance/conflict display and workspace creation form
- Workspace list + ROE acknowledgement UI backed by `/api/workspaces` endpoints
