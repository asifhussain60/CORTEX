# 🏗️ Design Standards

**Parent:** `cortex-docgen.prompt.md`  
**Purpose:** Enforce glassmorphism 2-level view hierarchy  
**Reference:** `cortex-brain/documents/archive/glassmorphism-design-standards-v2.md`

---

## 2-Level View Hierarchy (ENFORCED)

| Level | Example | Logo Size | Footer | Breadcrumb |
|-------|---------|-----------|--------|------------|
| **Home** | `index.html` | N/A | ✅ YES | ❌ NO |
| **Level 1** | `/orchestrators/index.html` | 200×200 | ❌ NO | ✅ YES |
| **Level 2** | `/orchestrators/planning-system.html` | 150×150 | ❌ NO | ✅ YES |

**⛔ Level 3+ pages are FORBIDDEN** - Restructure content into Level 2 if needed.

---

## Panel Spacing

**See full specification:** `cortex-brain/documents/archive/glassmorphism-design-standards-v2.md#panel-spacing`

```css
:root {
    --panel-gap-xs: 0.5rem;    /* 8px - Tight grouping */
    --panel-gap-sm: 1rem;      /* 16px - Within sections */
    --panel-gap-md: 1.5rem;    /* 24px - Between panels */
    --panel-gap-lg: 2rem;      /* 32px - Between sections */
    --panel-gap-xl: 3rem;      /* 48px - Hero separation */
}
```

---

## Required Elements per Level

### Level 1 Pages
- ✅ Breadcrumb bar at top
- ✅ 200×200 CORTEX logo in top-left
- ✅ Large icon + title centered
- ✅ Category cards for Level 2 pages
- ❌ NO footer

### Level 2 Pages
- ✅ Breadcrumb bar at top
- ✅ 150×150 CORTEX logo in top-left
- ✅ Detailed content, D3.js/Mermaid diagrams
- ❌ NO footer

---

## Footer Standards

| View Level | Footer | Rationale |
|------------|--------|-----------|
| Home Page | ✅ YES | Landing needs full nav/credits |
| Level 1 | ❌ NO | Breadcrumbs provide navigation |
| Level 2 | ❌ NO | Breadcrumbs provide navigation |

---

## View Modification Strategy

### ⛔ PREFER DELETE + RECREATE over Complex Modifications

**When modifications become complex, DELETE the file and RECREATE from scratch.**

### Complexity Threshold

**Prefer Delete + Recreate when:**
- ≥3 sections require structural changes
- Layout changes affect >30% of the HTML structure
- CSS changes require reorganizing >5 selectors
- D3.js/Mermaid diagrams need complete rewrite
- Breadcrumb or navigation hierarchy changes
- Level migration (e.g., Level 1 → Level 2)

**Simple edits (KEEP existing file):**
- Text content updates
- Single CSS property changes
- Minor icon swaps
- Data updates in existing diagrams

### ⚠️ CRITICAL: Preserve Entry Points

When deleting and recreating:
- ✅ Keep same filename (maintain URL stability)
- ✅ Keep same path location
- ✅ Keep same breadcrumb structure
- ❌ DO NOT change URLs (breaks external links)

---

## Design Validation

**Toolkit Script:** `cortex-toolkit/documentation/design_validator.py`

```bash
# Validate a single page
python cortex-toolkit/documentation/design_validator.py --path docs/orchestrators/index.html --level 1

# Validate entire docs directory
python cortex-toolkit/documentation/design_validator.py --path docs/
```

**Checks:**
- Logo size (200×200 for L1, 150×150 for L2)
- Footer presence (should be absent on L1/L2)
- Breadcrumb presence (required on L1/L2)
- Panel spacing CSS variables used
- Mobile responsiveness
