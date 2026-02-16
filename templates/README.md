# Scan Templates

Templates define scan plans and reporting formats. Avoid exploit payloads and
keep steps high level.

## Subfolders
- `reporting/` - report bundle, compliance checklist, program briefs, catalog, and per-finding templates
  - `reporting/standard/` - industry-standard Markdown report pack
  - `reporting/pandoc_header.tex` - PDF line-breaking tweaks for Pandoc exports
  - `reporting/fontconfig.conf` - fontconfig config for PDF engine font discovery
- `platforms/` - platform-specific issue or report formats
- `scan_plans/` - safe scan plan templates for `scripts.scan_templates`
- `engagement_workspace/` - engagement notes, recon log, and report draft skeleton

## Fields
- `id`
- `name`
- `description` (optional)
- `category` (optional)
- `target_types` (optional)
- `steps`
- `expected_results`
- `stop_conditions`
- `tags` (optional)

## Placeholders
Use placeholders that the planner can render:
- `{target}` - raw asset value
- `{base_url}` - target as a base URL
- `{canary}` - a synthetic canary string
