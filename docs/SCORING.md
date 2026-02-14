# Scoring

Difficulty scoring ranks public programs for planning and case-study selection.
Scores do not authorize testing and remain informational only.

## Signals
- Response time (faster is easier).
- Scope size and complexity.
- Restrictions burden and automation limits.
- Reward range as a competition proxy.
- Missing inputs use a neutral default and are listed in `missing_data`.

## Overrides
- Application required -> minimum bucket "Impossible" in public-only mode.
- Safe harbor missing -> never bucket "Easy" and flag for review.
- Testing disallowed -> bucket "Impossible" and flag for review.

## Usage
```bash
python -m scripts.program_scoring \
  --input data/program_registry.json \
  --output data/program_scoring_output.json \
  --public-only
```
CLI wrapper:
```bash
python -m bbhai catalog score --public-only
```

## Outputs
- Schema: `schemas/program_scoring_output.schema.json`
- Example: `examples/program_scoring_output.json`

## Case-study shortlist
```bash
python -m scripts.case_study_selection \
  --registry data/program_registry.json \
  --scoring data/program_scoring_output.json
```
- Schema: `schemas/case_study_selection.schema.json`
- Example: `examples/case_study_selection_output.json`

## Suggested approach
```bash
python -m scripts.suggested_approach \
  --input data/program_scoring_output.json \
  --output data/suggested_approach_output.json
```
- Schema: `schemas/suggested_approach.schema.json`
- Example: `examples/suggested_approach_output.json`

## Relevance and provenance
```bash
python -m scripts.program_relevance \
  --input data/program_registry.json \
  --output data/program_relevance_output.json
python -m scripts.program_provenance \
  --input data/program_registry.json \
  --output data/program_provenance_output.json
```
- Schemas: `schemas/program_relevance_output.schema.json`,
  `schemas/program_provenance_output.schema.json`
- Examples: `examples/program_relevance_output.json`,
  `examples/program_provenance_output.json`

## Calibration
```bash
python -m scripts.scoring_calibration \
  --scoring data/program_scoring_output.json \
  --labels examples/scoring_calibration_dataset.json \
  --output data/scoring_calibration_report.json
```
- Dataset schema: `schemas/scoring_calibration.schema.json`
- Report schema: `schemas/scoring_calibration_report.schema.json`
- Examples: `examples/scoring_calibration_dataset.json`,
  `examples/scoring_calibration_report.json`

## Tuning
Provide `--config` with weights and thresholds to tune scoring behavior.
