# Program Registry Change Log

Generated: 2026-01-17T06:09:07.621476+00:00

## Summary
- Added: 1
- Removed: 1
- Changed: 1

## Added (1)
- Other Program (program:bugcrowd-other-program)

## Removed (1)
- Legacy Program (program:legacy-program)

## Changed (1)
### Example Program (program:hackerone-example)
- [highlight] rewards: {"currency": "USD", "max": 5000, "min": 100} -> {"currency": "USD", "max": 10000, "min": 100}
- [highlight] scope: {"in_scope": [{"type": "domain", "value": "example.com"}], "restrictions": ["No denial of service."]} -> {"in_scope": [{"type": "domain", "value": "example.com"}], "out_of_scope": [{"type": "domain", "value": "internal.example.com"}], "restrictions": ["No denial of service.", "No social engineering."]}
- [highlight] restrictions: ["No denial of service."] -> ["No denial of service.", "No social engineering."]
