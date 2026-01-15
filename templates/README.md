# Scan Templates

Templates define safe, non-weaponized test plans for the scan planner. Avoid
exploit payloads and keep steps high level.

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
