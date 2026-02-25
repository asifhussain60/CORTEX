# CORTEX Enterprise Documentation Site

**Live Site:** https://asifhussain60.github.io/CORTEX/

This is the GitHub Pages source for CORTEX 3.0 enterprise documentation.

## Structure

### Three-Tier Documentation Model (v4.0)

**Tier 1: Features (`features/`)** - Overview & Benefits (500-800 words)
- High-level benefits and use cases
- Target audience: Decision makers, new users
- Links to complete documentation in Tier 2

**Tier 2: Orchestrators (`orchestrators/`)** - Complete User Documentation (1500-3000 words)
- **SOURCE OF TRUTH** for all user-facing documentation
- Full workflow descriptions, command examples, troubleshooting
- Target audience: All users (technical and non-technical)

**Tier 3: Technical (`technical/orchestrators/`)** - Implementation Details (2000-5000 words)
- Architecture diagrams, code structure, API references
- Target audience: Contributors, developers extending CORTEX

### Directory Layout

- `index.html` - Executive landing page with CORTEX logo and SKULL prominence
- `features/` - 8 feature overview pages (Tier 1)
- `orchestrators/` - 17 complete orchestrator docs (Tier 2 - SOURCE OF TRUTH)
- `technical/orchestrators/` - Implementation details (Tier 3)
- `governance/skull-rulebook.html` - Complete 22-rule SKULL showcase
- `architecture/` - System architecture pages
- `story/` - CORTEX Awakening narrative
- `assets/` - CSS, JS, images, data sources

### Data Sources

- `assets/data/orchestrator-metrics.json` - Single source of truth for phase counts, success rates, metrics
  - All documentation pages should reference this file
  - Update metrics here to propagate changes across all pages

## Design System

- **Framework:** Custom glassmorphism CSS (based on Admin Dashboard)
- **Colors:** 
  - Primary: `#00d4ff` (cyan)
  - Secondary: `#7b61ff` (purple)
  - Background: `#0a0e27` to `#1a1f3a` gradient
- **Typography:** Segoe UI, Inter, system sans-serif
- **Responsive:** Mobile-first with breakpoints at 768px

## Stub Pages

Pages marked with `<!-- STUB_PAGE: Created 2025-12-10 - Needs full content -->` are placeholders. Search for "STUB_PAGE" to find and replace with full content.

## Local Development

```bash
cd docs/gh-pages
python -m http.server 8000
# Open http://localhost:8000
```

## Deployment

This directory is configured as the GitHub Pages source. Any push to the `CORTEX-3.0` branch will automatically deploy to:

https://asifhussain60.github.io/CORTEX/

## Performance Budget

- First Contentful Paint (FCP): < 1.5s
- Time to Interactive (TTI): < 3.5s
- Lighthouse Score: > 90
- Total Page Weight: < 2MB

## Author

**Asif Hussain**  
GitHub: github.com/asifhussain60/CORTEX  
Copyright © 2024-2025 Asif Hussain. All rights reserved.
# Trigger deployment
