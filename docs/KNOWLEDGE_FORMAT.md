# Knowledge Format

All knowledge items use a short YAML frontmatter block followed by Markdown
sections. Keep content safe and non-weaponized.

See `docs/KNOWLEDGE_TAGS.md` for standard tags and `knowledge/INDEX.md` for the
current catalog.

Note:
- `knowledge/sources/*.md` may contain raw source material (for example,
  transcripts) and may not include frontmatter.
- Create a matching `knowledge/sources/*.source.md` file with frontmatter for
  anything you want indexed and reviewed.

Regenerate the index with:
```bash
python -m scripts.knowledge_index --output knowledge/INDEX.md
```

Lint frontmatter with:
```bash
python -m scripts.knowledge_lint
```

CI enforces index freshness by regenerating `knowledge/INDEX.md` and failing if
it changes.

## Publish to MkDocs
Publish curated knowledge items into the MkDocs site with:
```bash
python -m scripts.publish_knowledge_docs
```

This generates:
- `docs/KNOWLEDGE_INDEX.md`
- `docs/knowledge/` (cards, checklists, sources)

CI enforces that published docs stay in sync by regenerating these files and
failing if they change.

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
