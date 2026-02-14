# Case Study Selection

Use this guide to pick 1-2 public programs and build a safe, compliant case
study based on public metadata only.

## Selection criteria
- Public program page with clear scope and policy URL.
- Explicit safe harbor or disclosure guidance.
- Broad but well-defined scope (avoid unclear wildcard scope).
- Restrictions are manageable and clearly stated.
- Public response-time or activity signals, if available.

## Data collection steps
1) Use public-only mode to capture metadata (name, platform, policy URL).
2) Record scope summary, restrictions, and safe harbor notes.
3) Capture provenance (source, fetch date, parser version).
4) Do not test or probe targets without explicit authorization.

## Case study outline
- Program overview and scope summary.
- Threat model summary (RAG, embeddings, logging, agents as applicable).
- Test plan (planning-only, no execution without authorization).
- Compliance notes (ROE and data handling).
- Report template references and reproducibility notes.

## CLI shortlist
- Generate a shortlist with signals and restriction highlights:
  `python -m scripts.case_study_selection --registry data/program_registry.json --scoring data/program_scoring_output.json`
- Output schema: `schemas/case_study_selection.schema.json`
- Example output: `examples/case_study_selection_output.json`

## Safety reminders
- Follow `docs/PUBLIC_ONLY_MODE.md` and `docs/ROE.md`.
- Do not include secrets or private data in case studies.
