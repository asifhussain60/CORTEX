# Deprecated Orchestrators Archive

**Date:** December 10, 2025  
**Reason:** Replaced by GitHub Pages enterprise documentation site

## Files Archived

### enterprise_documentation_orchestrator.py.deprecated
- **Original Location:** `cortex-brain/admin/scripts/documentation/`
- **Lines:** 4,668
- **Purpose:** Generated MkDocs documentation with DALL-E prompts and narratives
- **Replaced By:** `docs/gh-pages/` static site with glassmorphism design

### enterprise_documentation_orchestrator_module.py.deprecated
- **Original Location:** `src/operations/modules/documentation/`
- **Lines:** 300
- **Purpose:** Operation module wrapper for orchestrator
- **Replaced By:** Direct GitHub Pages deployment workflow

## New System

The new enterprise documentation system is a beautiful GitHub Pages site located at `docs/gh-pages/`:

- **Design:** Glassmorphism with dark mode (from Admin Dashboard)
- **Features:**
  - SKULL Rulebook showcase (22 rules)
  - CORTEX logo integration
  - Drill-down navigation (Tier 1 → Tier 2 → Tier 3)
  - Progressive disclosure UI
  - Mobile-responsive
  - Sub-pages with stub identifiers for future expansion

- **Deployment:** GitHub Pages at `https://asifhussain60.github.io/CORTEX/`

## Restoration

If you need to restore these files:
```bash
cp enterprise_documentation_orchestrator.py.deprecated ../../../admin/scripts/documentation/enterprise_documentation_orchestrator.py
cp enterprise_documentation_orchestrator_module.py.deprecated ../../../../src/operations/modules/documentation/enterprise_documentation_orchestrator_module.py
```
