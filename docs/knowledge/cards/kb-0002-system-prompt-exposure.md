# System prompt exposure and reliance risk

## Metadata
- ID: kb-0002
- Type: card
- Status: reviewed
- Tags: ai-security, prompt-injection, privacy
- Source: TRANSCRIPT_01.md
- Date: 2026-01-14

## Summary
System prompts can be exposed through prompt-based attacks. They should not be
treated as a security boundary or a secret store.

## Relevance to the project
- Guides review of prompt handling and disclosure risk.
- Reinforces that controls must exist outside the prompt.

## Safe notes
- Do not place secrets or sensitive data in system prompts.
- Assume prompts can be exposed and build controls at the data and API layers.
- Limit prompt content to minimum necessary instructions.
- Log and monitor prompt exposure attempts without capturing sensitive data.

## References
- `knowledge/sources/TRANSCRIPT_01.md` (approx 15:46-17:34)
