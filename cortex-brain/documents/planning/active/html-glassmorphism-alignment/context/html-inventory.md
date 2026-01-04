# Context: HTML File Inventory

**Generated:** 2026-01-04  
**Source:** Phase 0 Context Discovery

---

## Summary

- **Total HTML Files:** 320
- **Classification System:** 4-tier priority system
- **Primary Target:** `docs/` folder

---

## File Classification

### Tier 1 (T1): Critical Pages - 5 files
**Priority:** CRITICAL  
**Description:** Home + top-level landing pages

- `docs/architecture/index.html`
- `docs/features/index.html`
- `docs/knowledge/index.html`
- `docs/learning-paths/index.html`
- `docs/orchestrators/index.html`

### Tier 2 (T2): High Priority - 60 files
**Priority:** HIGH  
**Description:** Level 1 detail pages (orchestrator pages, feature details, etc.)

Examples:
- `docs/orchestrators/planning-system.html`
- `docs/orchestrators/ado-operations.html`
- `docs/features/context-middleware.html`
- `docs/architecture/brain-tiers.html`

### Tier 3 (T3): Medium Priority - 200 files
**Priority:** MEDIUM  
**Description:** Level 2 documentation pages (learning modules, guides, etc.)

Examples:
- `docs/learning-paths/modules/*.html` (80+ modules)
- `docs/guides/*.html`
- `docs/tutorials/*.html`

### Tier 4 (T4): Low Priority - 55 files
**Priority:** LOW  
**Description:** Legacy/backup/test pages

Examples:
- `backups/*.html`
- `tests/*.html`
- `refinement-output/*.html`

---

## Compliance Status (Phase 0-6 Complete)

- **Compliant Files:** 315/320 (98.4%)
- **Exempted Files:** 5 (documented utility/demo pages)
- **Non-Compliant Files:** 0 (after Phase 3-6 fixes)

---

## Key Directories

```
docs/
├── index.html                    # Home page
├── architecture/                 # Architecture pages (5 files)
├── security/                     # Security pages (13 files)
├── orchestrators/                # Orchestrator pages (22 files)
├── token-optimization/           # Token pages (4 files)
├── sharpen-the-saw/              # STS pages (6 files)
├── learning-paths/               # Learning hub (80 modules)
├── toolkit-manager/              # Toolkit pages (3 files)
├── lens/                         # CORTEX Lens (3 files)
└── getting-started/              # Getting started (3 files)
```

---

## Design Standard Reference

**Source:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` (v4.2.8)

**Key CSS Classes:**
- `.glass-card-clickable` - Interactive tiles/cards
- `.glass-card-display` - Static content cards
- `.animation-t1` - Subtle hover effects
- `.principle-card-grid` - 2-3 column card grid
- `.tier-header` - Inline icon+title (8px gap)

**Critical Spacing Rule (v4.2.6):**
- All icon+title combinations MUST use `gap: var(--spacing-sm)` (8px)
- Icons and titles MUST be inline within the same container

**Zero Inline Styles Rule (v4.2.7):**
- 100% inline styles eliminated in glassmorphism plan
- HTML must use CSS classes only
- Exception: Dynamically generated content (JavaScript)
