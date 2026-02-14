# Ingestion Feasibility Matrix

This matrix summarizes public sources and ingestion constraints. Use public-only
mode and respect robots and terms of service.

| Source | Official API | Public listing | Scraping feasibility | Notes |
| --- | --- | --- | --- | --- |
| YesWeHack | No public API | Yes | Limited | HTML listing and detail pages; respect robots. |
| Intigriti | No public API | Yes | Limited | HTML listing and detail pages; rate limit. |
| Huntr | No public API | Yes | Limited | Public pages; avoid heavy requests. |
| disclose.io (diodb) | N/A | Yes (dataset) | High | JSON dataset on GitHub. |
| bounty-targets-data | N/A | Yes (dataset) | High | JSON dataset on GitHub. |
| ProjectDiscovery | N/A | Yes (dataset) | High | JSON dataset on GitHub. |

## Notes
- Prefer datasets and official APIs when available.
- Avoid targets that disallow automated access.
- Store only public metadata and provenance.
