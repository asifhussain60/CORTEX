# CORTEX Enterprise Documentation Site

**Live Site:** https://asifhussain60.github.io/CORTEX/

This is the GitHub Pages source for CORTEX 3.0 enterprise documentation.

## Structure

- `index.html` - Executive landing page with CORTEX logo and SKULL prominence
- `governance/skull-rulebook.html` - Complete 22-rule SKULL showcase
- `features/` - Feature catalog and detail pages
- `architecture/` - System architecture pages
- `future/` - CORTEX 4.0 vision
- `assets/` - CSS, JS, images

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
