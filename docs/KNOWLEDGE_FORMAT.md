# Knowledge Format

All knowledge items use a short YAML frontmatter block followed by Markdown
sections. Keep content safe and non-weaponized.

See `docs/KNOWLEDGE_TAGS.md` for standard tags and `knowledge/INDEX.md` for the
current catalog.

Regenerate the index with:
```bash
python -m scripts.knowledge_index --output knowledge/INDEX.md
```

CI enforces index freshness by regenerating `knowledge/INDEX.md` and failing if
it changes.

## Frontmatter (required)
```yaml
---
id: kb-0000
title: Short, clear title
type: source | card | checklist
status: draft | reviewed
tags: [tag1, tag2]
source: title or URL
date: YYYY-MM-DD
---
```

## Sections (recommended)
- Summary
- Relevance to the project
- Safe notes (no exploit code, no real data)
- References
