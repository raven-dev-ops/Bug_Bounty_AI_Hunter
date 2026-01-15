# External Intel

External intelligence enrichment is optional and must respect scope and rate
limits. Use `scripts/external_intel.py`.

## Providers
- `file` (default): load records from a local JSON/YAML file
- `shodan`: requires `SHODAN_API_KEY`
- `censys`: requires `CENSYS_API_ID` and `CENSYS_API_SECRET`

## Scope enforcement
Scope allowlists are enforced by default. Use `--no-scope-enforcement` only if
explicitly authorized.

## Example
```bash
python scripts/external_intel.py --provider file --source examples/intel_stub.json --targets output/discovery.json --output output/intel.json
```

## Safety
Do not send sensitive data to third parties. Always follow `docs/ROE.md`.
