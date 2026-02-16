# Agents and tool-use review checklist

## Metadata
- ID: kb-checklist-0008
- Type: checklist
- Status: draft
- Tags: ai-security, agents, prompt-injection, access-control, telemetry
- Source: project
- Date: 2026-01-15

## Summary
Checklist for reviewing tool-using agents, their inputs, and their guardrails.

## Relevance to the project
Agents can blur the boundary between data and instructions. This checklist
keeps reviews focused on safe, authorized validation.

## Checklist
- Identify tool interfaces, allowed commands, and expected inputs.
- Verify the agent uses an explicit allowlist for tools and actions.
- Confirm user inputs and retrieved context are labeled and separated.
- Check for input sanitization and structured arguments for tools.
- Ensure high-risk tools require explicit approval or step-up auth.
- Validate logging and redaction for tool calls and agent outputs.
- Confirm stop conditions for unexpected data or out-of-scope results.

## Safe notes
- Use canary strings and synthetic data only.
- Avoid running high-impact tools without explicit authorization.

## References
- `docs/ROE.md`
- `docs/PROJECT_OUTLINE.md`
