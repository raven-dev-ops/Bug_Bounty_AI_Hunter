# Legacy access control review checklist

## Metadata
- ID: kb-checklist-0004
- Type: checklist
- Status: draft
- Tags: access-control, legacy-systems
- Source: TRANSCRIPT_05.md
- Date: 2026-01-14

## Scope
Review legacy system access controls and permission alignment.

## Preconditions
- Written authorization and clear scope.
- ROE reviewed and accepted.

## Review steps
1. Map file permissions and external security manager rules.
2. Identify data sets or directories with broad read/write access.
3. Review privileged roles and assignment workflows.
4. Check for secrets stored in readable data sets.
5. Validate that policy sources do not conflict.

## Evidence to capture
- Access control summaries and policy references.
- Minimal reproduction notes using synthetic identifiers.

## Stop conditions
- Any exposure of real user data or secrets.
- Any scope ambiguity or unapproved testing technique.

## Outputs
- TestCase entries with safe steps and stop conditions.
- Finding drafts for over-broad access or policy conflicts.
