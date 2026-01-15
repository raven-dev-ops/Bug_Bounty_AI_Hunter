# Scan Templates

Templates define scan plans and reporting formats. Avoid exploit payloads and
keep steps high level.

## Subfolders
- `reporting/` - report bundle and per-finding templates
- `platforms/` - platform-specific issue or report formats

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
