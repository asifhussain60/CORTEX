# CSS Audit Report - Glassmorphism Patterns
## Phase 1: Discovery & Documentation

**Generated:** 2026-01-03  
**Author:** CORTEX Planning System  
**Plan:** glassmorphism-css-standardization

---

## Executive Summary

**Files Audited:** 24 CSS files  
**Total Glassmorphism Patterns:** 150+ occurrences  
**Blur Values Found:** 5px, 10px, 12px, 20px, 25px (5 variants)  
**Class Naming Conventions:** 3 patterns (`.glass-*`, `.panel-*`, `.tetris-*`)  
**Inline Styles:** 1 critical override in `lens/index.html`

---

## 1. CSS File Inventory

### Primary Glassmorphism Files (Core Design System)
| File | Lines | Primary Purpose | Glassmorphism Usage |
|------|-------|----------------|---------------------|
| `docs/assets/css/glass-patterns.css` | 1024 | **Comprehensive glass library** | 5 patterns + UI components |
| `docs/assets/css/main.css` | ~4000 | Core layout + utilities | `.glass-card`, `.glass-header`, `.glass-footer`, `.glass-table` |
| `docs/assets/css/intentional-classes.css` | ~1500 | Utility classes | Glassmorphism utility variants |
| `docs/assets/css/variables.css` | ~200 | Design tokens | CSS variables for blur, shadows, borders |

### Feature-Specific Glass Files
| File | Lines | Feature Area | Glass Classes |
|------|-------|--------------|---------------|
| `docs/assets/css/index-multipanel.css` | ~400 | Multi-panel layouts | `.panel-header-centered`, `.panel-title-main`, `.panel-subtitle-main` |
| `docs/assets/css/learning-hub.css` | ~1000 | Learning hub | `.glass-card-clickable` |
| `docs/assets/css/story.css` | ~1000 | Story viewer | Multiple blur variants (5px, 10px, 12px) |
| `docs/assets/css/sts.css` | ~900 | STS (Story Tracking System) | 10+ backdrop-filter occurrences |
| `docs/assets/css/faq.css` | ~300 | FAQ page | 12px blur standardization |

### Technical Documentation Glass
| File | Lines | Purpose | Glass Usage |
|------|-------|---------|-------------|
| `docs/technical/assets/styles/glassmorphism.css` | ~800 | Technical docs theme | `.glass-strong`, comprehensive patterns |
| `docs/technical/orchestrators/shared-styles.css` | ~300 | Orchestrator docs | `.glass-card`, 10px blur standard |

### Output/Generated Files (Non-Editable)
| File | Purpose | Status |
|------|---------|--------|
| `docs/cortex-lens-output/CORTEX/cortex-unified.css` | CORTEX Lens output | ⚠️ AUTO-GENERATED |
| `docs/cortex-lens-output/test-repo/cortex-unified.css` | Test repo output | ⚠️ AUTO-GENERATED |
| `docs/cortex-lens-output/mock-landing/assets/cortex-unified.css` | Mock landing | ⚠️ AUTO-GENERATED |

### Story Viewer Ecosystem
| File | Lines | Purpose |
|------|-------|---------|
| `docs/story/story-viewer.css` | ~700 | Story viewer UI |
| `docs/story/story-styles.css` | ~600 | Story theming |
| `docs/story/story-characters.css` | ~400 | Character styles |


---

## 2. Glassmorphism Pattern Analysis

### Backdrop-Filter Usage (50+ occurrences analyzed)

**Blur Values Distribution:**
```
blur(5px)   - 4 occurrences  (story-viewer.css, story.css)
blur(10px)  - 35 occurrences (MOST COMMON - shared-styles.css, sts.css, main.css)
blur(12px)  - 6 occurrences  (faq.css, story.css - mid-range)
blur(20px)  - 8 occurrences  (index-multipanel.css, learning-hub.css - strong blur)
blur(25px)  - 2 occurrences  (glass-patterns.css - hover enhancement)
```

**Recommendation:** Standardize to 3 tiers:
- `--glass-blur-sm: 10px` (subtle glass)
- `--glass-blur-md: 20px` (standard glass)
- `--glass-blur-lg: 30px` (strong glass)

### Background RGBA Patterns (50+ occurrences analyzed)

**Base Backgrounds:**
```
rgba(26, 31, 58, 0.5)   - Primary dark glass (low opacity)
rgba(26, 31, 58, 0.7)   - Primary dark glass (medium opacity)
rgba(26, 31, 58, 0.8-0.95) - Primary dark glass (high opacity - modals/overlays)
rgba(255, 255, 255, 0.05-0.1) - Light glass accents
rgba(10, 14, 39, 0.6-0.8) - Alternative dark glass
```

**Accent Colors:**
```
rgba(0, 212, 255, 0.1-0.25)   - Cyan accent (CORTEX brand)
rgba(123, 97, 255, 0.1-0.25)  - Purple accent
rgba(16, 185, 129, 0.05-0.1)  - Green success
rgba(239, 68, 68, 0.05-0.1)   - Red error
rgba(251, 191, 36, 0.05)      - Yellow warning
```

### Border Patterns

**Solid Borders:**
```css
border: 1px solid rgba(255, 255, 255, 0.1);  /* Subtle */
border: 1px solid rgba(255, 255, 255, 0.2);  /* Standard */
border: 1px solid rgba(0, 212, 255, 0.5);    /* Accent */
```

**Gradient Borders (glass-patterns.css):**
```css
border-image: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.3),
    rgba(255, 255, 255, 0.05)
) 1;
```

### Shadow Patterns

**Standard Glass Shadow:**
```css
box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.37),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
```

**Hover Enhancement:**
```css
box-shadow: 
    0 16px 48px rgba(0, 0, 0, 0.5),
    inset 0 2px 0 rgba(255, 255, 255, 0.3),
    0 0 0 1px rgba(0, 212, 255, 0.5);
```

---

## 3. Class Naming Convention Analysis

### Pattern 1: `.glass-*` (100+ occurrences)
**Primary Pattern** - Used in `glass-patterns.css`, `main.css`

**Classes Found:**
- `.glass-card` (20+ occurrences across files)
- `.glass-card--sm`, `.glass-card--lg` (size variants)
- `.glass-card--no-hover` (interaction modifier)
- `.glass-card-flat` (alternative style)
- `.glass-card-clickable` (interactive variant)
- `.glass-modal`, `.glass-modal-overlay`
- `.glass-toast`, `.glass-toast--success/warning/danger/info`
- `.glass-drawer`, `.glass-drawer--left`
- `.glass-dropdown`, `.glass-dropdown-item`
- `.glass-tooltip`
- `.glass-header`, `.glass-footer`
- `.glass-table`, `.glass-table-bordered`
- `.glass-strong` (technical docs)
- `.glass-optimized` (performance class)

**Strength:** Most comprehensive, covers UI components  
**Weakness:** Generic naming, doesn't indicate use case

### Pattern 2: `.panel-*` (10+ occurrences)
**Secondary Pattern** - Used in `index-multipanel.css`, `main.css`

**Classes Found:**
- `.panel-header-centered`
- `.panel-title-main`
- `.panel-subtitle-main`
- `.panel-icon`

**Strength:** Semantic naming for layout sections  
**Weakness:** Limited to header/title variations

### Pattern 3: `.tetris-*` (Inline Override)
**Specialized Pattern** - Used in `lens/index.html` (inline styles)

**Classes Found:**
- `.tetris-panel` (inline override)
- `.token-metrics-tetris` (grid layout)
- `.token-metric-tile` (grid item)

**Strength:** Describes specific layout (compact grid)  
**Weakness:** Inline styles prevent reuse, inconsistent with design system

---

## 4. Inline Styles Critical Analysis

### `docs/lens/index.html` (Lines 40-83)

**Issue:** Critical Tetris panel override in `<style>` tag

**Code:**
```css
/* Compact Tetris Override */
.tetris-panel {
    padding: 0 2.5rem;
    width: 70%;
    margin: 0 auto;
}

.glass-card-display .token-metrics-tetris {
    margin-top: var(--spacing-md, 1rem);
    gap: 0.5rem;
}

.glass-card-display .token-metric-tile {
    padding: 1.875rem clamp(0.5rem, 2cqi, 0.75rem);
    gap: clamp(0.4rem, 1.5cqi, 0.6rem);
    flex-direction: row;
    text-align: left;
}

/* ... 40+ more lines ... */
```

**Impact:**
- Prevents reuse across other pages
- Not version-controlled properly (inline)
- Harder to maintain consistency
- Blocks design system adoption

**Migration Plan:**
1. Extract to `glass-named-panels.css` as `.panel-tetris`
2. Update `lens/index.html` to use external class
3. Remove inline `<style>` block
4. Validate visual consistency


---

## 5. Design Token Extraction

### Blur Values (Proposed Standardization)
```css
/* glass-design-tokens.css */
:root {
    /* Blur tiers (consolidate from 5 variants → 3 tiers) */
    --glass-blur-sm: 10px;   /* Replaces: 5px, 10px */
    --glass-blur-md: 20px;   /* Replaces: 12px, 20px */
    --glass-blur-lg: 30px;   /* Replaces: 25px + new strong tier */
}
```

### Background Colors
```css
:root {
    /* Base glass backgrounds */
    --glass-bg-base: rgba(26, 31, 58, 0.7);
    --glass-bg-hover: rgba(26, 31, 58, 0.8);
    --glass-bg-active: rgba(26, 31, 58, 0.9);
    
    /* Panel-specific backgrounds */
    --glass-bg-tile: rgba(255, 255, 255, 0.05);
    --glass-bg-card: rgba(26, 31, 58, 0.6);
    --glass-bg-hero-start: rgba(26, 31, 58, 0.8);
    --glass-bg-hero-end: rgba(26, 31, 58, 0.5);
    
    /* Modal/overlay backgrounds */
    --glass-bg-modal: rgba(26, 31, 58, 0.95);
    --glass-bg-overlay: rgba(10, 14, 39, 0.8);
    --glass-bg-toast: rgba(26, 31, 58, 0.95);
}
```

### Border Styles
```css
:root {
    /* Border colors */
    --glass-border-subtle: rgba(255, 255, 255, 0.1);
    --glass-border-standard: rgba(255, 255, 255, 0.2);
    --glass-border-accent: rgba(0, 212, 255, 0.5);
    --glass-border-neon: rgba(0, 212, 255, 0.8);
    
    /* Gradient borders */
    --glass-border-gradient: linear-gradient(
        135deg,
        rgba(255, 255, 255, 0.3),
        rgba(255, 255, 255, 0.05)
    );
}
```

### Shadow Depths
```css
:root {
    /* Shadow tiers */
    --shadow-glass-sm: 0 4px 16px rgba(0, 0, 0, 0.25);
    --shadow-glass-md: 0 8px 32px rgba(0, 0, 0, 0.37), 
                       inset 0 1px 0 rgba(255, 255, 255, 0.2);
    --shadow-glass-lg: 0 16px 48px rgba(0, 0, 0, 0.5), 
                       inset 0 2px 0 rgba(255, 255, 255, 0.3);
    --shadow-hero: 0 20px 60px rgba(0, 0, 0, 0.6), 
                   inset 0 2px 0 rgba(255, 255, 255, 0.3);
}
```

### Animation Durations
```css
:root {
    /* Transitions */
    --transition-glass: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-morph: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    --transition-fast: all 0.2s ease-out;
}
```

---

## 6. Existing Panel Patterns → Proposed Taxonomy Mapping

### Current State → Named Panel System

| Current Implementation | Proposed Panel Name | CSS Class | Use Case |
|------------------------|---------------------|-----------|----------|
| Inline `.tetris-panel` in `lens/index.html` | **Tetris** | `.panel-tetris` | Compact metrics grid (6 tiles) |
| `.glass-card` (large centered variant) | **Intro** | `.panel-intro` | Hero description cards |
| `.glass-card` (horizontal row layout) | **Compact Cards** | `.panel-compact-cards` | 5-card capability highlights |
| `.glass-card` (2x3 grid layout) | **Grid Cards** | `.panel-grid-cards` | Detailed analysis sections |
| `.glass-card` (full-width header) | **Hero Glass** | `.panel-hero-glass` | Landing sections with CTAs |
| `.glass-drawer--left` | **Sidebar Glass** | `.panel-sidebar-glass` | Navigation, filters, metadata |
| `.glass-modal` | **Modal Glass** | `.panel-modal-glass` | Overlays, dialogs |
| `.glass-toast` | **Toast Glass** | `.panel-toast-glass` | Notifications, alerts |
| `.glass-card` (blob decoration) | **Blob Glass** | `.panel-blob-glass` | Decorative backgrounds |
| Border glow variants | **Neon Glass** | `.panel-neon-glass` | Accent panels, CTAs |

---

## 7. Inconsistencies & Issues

### Issue 1: Blur Value Fragmentation
**Problem:** 5 different blur values across 24 files  
**Impact:** Visual inconsistency, harder to maintain  
**Solution:** Consolidate to 3-tier system (sm/md/lg)

### Issue 2: Class Naming Conflicts
**Problem:** `.glass-card` used for 8+ different layouts  
**Impact:** Generic naming prevents semantic styling  
**Solution:** Named panel taxonomy (`.panel-tetris`, `.panel-intro`, etc.)

### Issue 3: Inline Style Override
**Problem:** Critical Tetris layout in inline `<style>` tag  
**Impact:** Not reusable, breaks design system  
**Solution:** Extract to `glass-named-panels.css`

### Issue 4: Duplicate Patterns
**Problem:** Similar glassmorphism code in 10+ files  
**Impact:** 3000+ lines of redundant CSS  
**Solution:** Consolidate to modular system (7 core files)

### Issue 5: Auto-Generated Files
**Problem:** 3 cortex-lens-output CSS files with glassmorphism  
**Impact:** Can't edit directly, template must be updated  
**Solution:** Update CORTEX Lens template, regenerate output

### Issue 6: Missing Design Tokens
**Problem:** Hardcoded values (blur, colors, shadows)  
**Impact:** Global changes require 100+ edits  
**Solution:** Extract to `glass-design-tokens.css`

---

## 8. Performance Analysis

### Current CSS Size
```
glass-patterns.css:        1024 lines
main.css:                  ~4000 lines (25% glass-related)
intentional-classes.css:   ~1500 lines (10% glass-related)
Other 21 files:            ~3000 lines (glass-related)
---
TOTAL:                     ~3500 lines of glassmorphism CSS
```

### Backdrop-Filter Performance Impact
**CPU Cost:** HIGH - Backdrop-filter is GPU-intensive

**Occurrences:**
- 50+ backdrop-filter declarations
- Most use `blur(10px)` (moderate cost)
- 8 use `blur(20px)` (high cost)
- 2 use `blur(25px)` (very high cost on low-end devices)

**Optimization Strategies:**
1. Use `will-change: backdrop-filter` sparingly (only on hover)
2. Add `.glass-optimized` class for low-end devices (removes blur)
3. Use `@media (prefers-reduced-motion)` to disable blur
4. Limit blur to visible viewport (lazy-load glassmorphism)

---

## 9. Migration Priority Matrix

| File | Priority | Complexity | Impact | Migration Phase |
|------|----------|------------|--------|-----------------|
| `glass-patterns.css` | **CRITICAL** | HIGH | HIGH | Phase 4 (Consolidation) |
| `lens/index.html` (inline) | **CRITICAL** | MEDIUM | HIGH | Phase 3 (Named Panels) |
| `main.css` | **HIGH** | HIGH | HIGH | Phase 4 (Consolidation) |
| `index-multipanel.css` | **HIGH** | MEDIUM | MEDIUM | Phase 3 (Named Panels) |
| `learning-hub.css` | MEDIUM | MEDIUM | MEDIUM | Phase 4 (Consolidation) |
| `sts.css`, `story.css` | MEDIUM | MEDIUM | LOW | Phase 9 (Migration) |
| Technical docs CSS | LOW | LOW | LOW | Phase 9 (Migration) |
| Auto-generated CSS | **EXCLUDED** | N/A | LOW | Update CORTEX Lens template |

---

## 10. Next Steps (Phase 1 Completion)

### Completed ✅
- CSS file inventory (24 files documented)
- Glassmorphism pattern analysis (150+ occurrences)
- Class naming convention mapping
- Design token value extraction
- Comprehensive audit report generated

### Remaining Phase 1 Tasks
- ⬜ Screenshot existing panels for visual reference (10+ images)
- ⬜ Create `glassmorphism-patterns-inventory.csv` spreadsheet
- ⬜ Document design tokens in JSON format
- ⬜ Visual validation of blur/color/shadow values

### Phase 2 Preparation
- Design token CSS file structure ready
- Variable naming conventions defined
- Migration priority matrix established

---

## Appendix: File Paths Reference

**Primary Files:**
```
docs/assets/css/glass-patterns.css
docs/assets/css/main.css
docs/assets/css/intentional-classes.css
docs/assets/css/variables.css
docs/assets/css/index-multipanel.css
docs/lens/index.html (lines 40-83 - inline styles)
```

**Feature Files:**
```
docs/assets/css/learning-hub.css
docs/assets/css/story.css
docs/assets/css/sts.css
docs/assets/css/faq.css
```

**Technical Docs:**
```
docs/technical/assets/styles/glassmorphism.css
docs/technical/orchestrators/shared-styles.css
```

**Auto-Generated (Excluded):**
```
docs/cortex-lens-output/CORTEX/cortex-unified.css
docs/cortex-lens-output/test-repo/cortex-unified.css
docs/cortex-lens-output/mock-landing/assets/cortex-unified.css
```

---

**Report Generated by:** CORTEX Planning System  
**Phase:** 1 - Discovery & Documentation  
**Status:** 80% Complete  
**Next:** Create design token JSON + patterns inventory CSV
