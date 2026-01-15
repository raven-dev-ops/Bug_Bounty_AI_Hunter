# Severity Model

This project uses an OWASP LLM Top 10 aligned severity model to keep AI risk
categories and impact axes consistent across findings and triage outputs.

## Model summary
- Name: `owasp-llm-top-10`
- Version: `2023`
- Axes: `data_exposure`, `integrity`, `autonomy`, `cost_dos`
- Scale: `unscored`, `info`, `low`, `medium`, `high`, `critical`
- Overall severity: highest scored axis (ignore `unscored`)

Use category `unassigned` when a finding has not been mapped yet.

## OWASP LLM Top 10 categories
- LLM01: Prompt Injection
- LLM02: Insecure Output Handling
- LLM03: Training Data Poisoning
- LLM04: Model Denial of Service
- LLM05: Supply Chain Vulnerabilities
- LLM06: Sensitive Information Disclosure
- LLM07: Insecure Plugin Design
- LLM08: Excessive Agency
- LLM09: Overreliance
- LLM10: Model Theft

## Axis definitions
- data_exposure: unauthorized disclosure of sensitive data or context.
- integrity: unauthorized modification, incorrect outputs, or trust violations.
- autonomy: unauthorized actions, escalation, or tool misuse.
- cost_dos: resource exhaustion or excessive cost to operate.

## Output fields
Findings and triage outputs include:
- `severity` for the overall rating.
- `severity_model` for model metadata, category, and axis scores.

## Example
```json
{
  "severity": "high",
  "severity_model": {
    "name": "owasp-llm-top-10",
    "version": "2023",
    "category": "LLM01: Prompt Injection",
    "axes": {
      "data_exposure": "medium",
      "integrity": "high",
      "autonomy": "high",
      "cost_dos": "low"
    },
    "method": "overall_severity_is_max_axis",
    "reference": "docs/SEVERITY_MODEL.md"
  }
}
```
