# Program Registry

Program registry entries unify multiple source records into a single canonical
program record. Use `schemas/program_registry.schema.json` as the contract.

## Identity rules
Records are deduplicated using the first available identity key:
1) `platform` + `handle`
2) `policy_url` (normalized)
3) `name` (normalized)

Normalization rules:
- `platform`, `handle`, and `name` are lowercased and trimmed.
- `policy_url` is lowercased, stripped of query/fragment, and trailing slashes.

## Merge rules
Source precedence (highest first):
1) `manual`
2) `internal`
3) `hackerone`
4) `bugcrowd`
5) `yeswehack`
6) `intigriti`
7) `synack`
8) `public`
9) `unknown`

Field handling:
- `name`, `platform`, `handle`, `policy_url`, `rewards`, and `safe_harbor` use the
  highest-priority non-empty value.
- `scope` uses the highest-priority scope to avoid expanding coverage.
- `restrictions` merge as a union to stay conservative.
- `attribution` entries are retained from all sources with license and terms URLs.

Merged entries include `sources` (all input records) and `conflicts` entries for
fields that differ across sources.
Source records should include provenance metadata such as fetch time, HTTP
status, parser version, git commit, and artifact hashes when available.

## Usage
```bash
python -m scripts.program_registry \
  --input examples/program_registry_sources.json \
  --output examples/program_registry_output.json
```

Build a public-only registry from connectors with:
```bash
python -m scripts.catalog_build --public-only --output data/program_registry.json
```
Default connectors include yeswehack, intigriti, huntr, bounty-targets-data,
disclose-io, and projectdiscovery. Override with `--connectors`.
Audit logs and summaries are written under `data/ingestion_audit/` by default.
The JSON summary uses a `.summary.json` suffix by default.
Use `--audit-log`, `--audit-summary`, and `--audit-summary-json` to override those paths.
Registry outputs validate against `schemas/program_registry.schema.json` at write time.

Review conflicts and confirm scope before use.

## Scoring
Generate difficulty buckets from the registry with:
```bash
python -m scripts.program_scoring --input data/program_registry.json --public-only
```

## Local registry storage
Initialize and update a local registry file with:
```bash
python -m scripts.program_registry_store init --output data/program_registry.json
python -m scripts.program_registry_store add \
  --registry data/program_registry.json \
  --input examples/program_registry_sources.json
```
Registry storage is JSON for portability. SQLite can be added later if needed.

## Change logs
Generate a registry diff between snapshots with:
```bash
python -m scripts.program_registry_diff \
  --before examples/program_registry_before.json \
  --after examples/program_registry_after.json \
  --output-json examples/program_registry_diff.json \
  --output-md examples/program_registry_diff.md
```
