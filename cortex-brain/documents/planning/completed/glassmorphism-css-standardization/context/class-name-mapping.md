# Class Name Mapping Documentation
## Current State → Proposed Panel Taxonomy

**Generated:** 2026-01-03  
**Purpose:** Map existing CSS class names to proposed named panel system  
**Plan:** glassmorphism-css-standardization

---

## Mapping Strategy

### Current Naming Patterns (3 Patterns Detected)

#### Pattern 1: `.glass-*` (Generic Component Naming)
- **Usage:** 100+ occurrences across 15+ files
- **Strength:** Comprehensive coverage of UI components
- **Weakness:** No semantic meaning (doesn't indicate use case)
- **Action:** Keep for base patterns, supplement with semantic `.panel-*` names

#### Pattern 2: `.panel-*` (Semantic Layout Naming)
- **Usage:** 10+ occurrences in index-multipanel.css
- **Strength:** Indicates layout purpose
- **Weakness:** Limited coverage (headers/titles only)
- **Action:** Expand to become primary naming pattern for layouts

#### Pattern 3: `.tetris-*` (Inline Custom Naming)
- **Usage:** 1 occurrence (inline styles in lens/index.html)
- **Strength:** Descriptive name indicates grid layout
- **Weakness:** Inline styles, not reusable
- **Action:** Extract to `.panel-tetris` in external CSS

---

## Complete Mapping Table

### Base Patterns (Keep As-Is)

| Current Class | File | Purpose | Proposed Action | Notes |
|---------------|------|---------|-----------------|-------|
| `.glass-card` | glass-patterns.css | Base glassmorphism pattern | **KEEP** | Multi-layer card (PRIMARY pattern) |
| `.glass-card--sm` | glass-patterns.css | Small card variant | **KEEP** | Size modifier |
| `.glass-card--lg` | glass-patterns.css | Large card variant | **KEEP** | Size modifier |
| `.glass-card--no-hover` | glass-patterns.css | No hover effect | **KEEP** | Interaction modifier |
| `.glass-card-flat` | main.css | Flat card (no blur) | **KEEP** | Performance fallback |

### UI Components (Keep As-Is)

| Current Class | File | Purpose | Proposed Action | Notes |
|---------------|------|---------|-----------------|-------|
| `.glass-modal` | glass-patterns.css | Modal dialog | **KEEP** | Rename to `.panel-modal-glass` for consistency |
| `.glass-modal-overlay` | glass-patterns.css | Modal backdrop | **KEEP** | |
| `.glass-toast` | glass-patterns.css | Toast notification | **KEEP** | Rename to `.panel-toast-glass` |
| `.glass-toast--success` | glass-patterns.css | Success toast | **KEEP** | Color variant |
| `.glass-toast--warning` | glass-patterns.css | Warning toast | **KEEP** | Color variant |
| `.glass-toast--danger` | glass-patterns.css | Error toast | **KEEP** | Color variant |
| `.glass-toast--info` | glass-patterns.css | Info toast | **KEEP** | Color variant |
| `.glass-drawer` | glass-patterns.css | Side drawer | **KEEP** | Rename to `.panel-sidebar-glass` |
| `.glass-drawer--left` | glass-patterns.css | Left-side drawer | **KEEP** | Direction modifier |
| `.glass-dropdown` | glass-patterns.css | Dropdown menu | **KEEP** | |
| `.glass-dropdown-item` | glass-patterns.css | Dropdown item | **KEEP** | |
| `.glass-tooltip` | glass-patterns.css | Tooltip | **KEEP** | |
| `.glass-header` | main.css | Page header | **KEEP** | |
| `.glass-footer` | main.css | Page footer | **KEEP** | |
| `.glass-table` | main.css | Glass table | **KEEP** | |
| `.glass-table-bordered` | main.css | Bordered table | **KEEP** | |

### Layout Patterns (CREATE NEW Named Panels)

| Current Implementation | Current Class | File | Proposed Panel Name | New CSS Class | Migration Action |
|------------------------|---------------|------|---------------------|---------------|------------------|
| Inline styles | `.tetris-panel` | lens/index.html | **Tetris** | `.panel-tetris` | **EXTRACT** inline styles → `glass-named-panels.css` |
| `.glass-card` (large centered) | `.glass-card` | main.css | **Intro** | `.panel-intro` | **CREATE** new class with hero styling |
| `.glass-card` (horizontal row) | `.glass-card` | learning-hub.css | **Compact Cards** | `.panel-compact-cards` | **CREATE** new class with 5-card grid |
| `.glass-card` (2x3 grid) | `.glass-card` | main.css | **Grid Cards** | `.panel-grid-cards` | **CREATE** new class with detailed grid |
| `.glass-card` (full-width header) | `.glass-card` | index-multipanel.css | **Hero Glass** | `.panel-hero-glass` | **CREATE** new class with full-width styling |
| `.glass-card` (blob shapes) | `.glass-card` | glass-patterns.css | **Blob Glass** | `.panel-blob-glass` | **CREATE** new class with organic shapes |
| `.glass-card` (neon borders) | `.glass-card` | main.css | **Neon Glass** | `.panel-neon-glass` | **CREATE** new class with glowing borders |

### Existing Panel Classes (ENHANCE)

| Current Class | File | Purpose | Proposed Action | New Class | Notes |
|---------------|------|---------|-----------------|-----------|-------|
| `.panel-header-centered` | index-multipanel.css | Centered header | **ENHANCE** | `.panel-header-centered` | Add to named panel system |
| `.panel-title-main` | index-multipanel.css | Main title | **KEEP** | `.panel-title-main` | Typography utility |
| `.panel-subtitle-main` | index-multipanel.css | Subtitle | **KEEP** | `.panel-subtitle-main` | Typography utility |
| `.panel-icon` | main.css | Panel icon | **KEEP** | `.panel-icon` | Icon utility |

### Feature-Specific Classes (CONSOLIDATE OR KEEP)

| Current Class | File | Purpose | Proposed Action | Notes |
|---------------|------|---------|-----------------|-------|
| `.glass-card-clickable` | learning-hub.css | Interactive card | **CONSOLIDATE** | Merge hover effects into `.glass-card` with `.glass-card--interactive` modifier |
| `.glass-strong` | glassmorphism.css | Technical docs glass | **KEEP** | Separate use case (higher opacity for code) |
| `.glass-optimized` | glass-patterns.css | Performance fallback | **KEEP** | Removes backdrop-filter for low-end devices |

### Inline Styles (CRITICAL EXTRACTION)

| Current Implementation | Location | Lines | Proposed Class | Priority | Migration Action |
|------------------------|----------|-------|----------------|----------|------------------|
| `.tetris-panel` + children | lens/index.html | 45-83 | `.panel-tetris` | **CRITICAL** | Extract ALL 40+ lines to `glass-named-panels.css` |
| `.token-metrics-tetris` | lens/index.html | 50-60 | `.panel-tetris__grid` | **CRITICAL** | BEM naming for tetris grid container |
| `.token-metric-tile` | lens/index.html | 60-80 | `.panel-tetris__tile` | **CRITICAL** | BEM naming for tetris tiles |

---

## Named Panel Taxonomy (10 New Panel Styles)

### 1. Panel Tetris (`.panel-tetris`)
**Current:** Inline styles in lens/index.html  
**Use Case:** Compact metrics grid (6 tiles, horizontal icon+value layout)  
**Visual Reference:** CORTEX Lens dashboard top section  
**Grid:** `repeat(auto-fit, minmax(200px, 1fr))`  
**Migration:** Extract 40+ lines from inline `<style>` tag

### 2. Panel Intro (`.panel-intro`)
**Current:** `.glass-card` (large centered variant)  
**Use Case:** Hero description cards, landing sections  
**Visual Reference:** CORTEX Lens dashboard bottom section  
**Layout:** Max-width 800px, centered, gradient background  
**Migration:** Create new class based on `.glass-card` + centering + gradient

### 3. Panel Compact Cards (`.panel-compact-cards`)
**Current:** `.glass-card` (horizontal row layout)  
**Use Case:** 5-card capability highlights, feature lists  
**Visual Reference:** CORTEX capabilities row (Image 2)  
**Grid:** `repeat(5, 1fr)` or `repeat(auto-fit, minmax(250px, 1fr))`  
**Migration:** Create new class with compact card grid

### 4. Panel Grid Cards (`.panel-grid-cards`)
**Current:** `.glass-card` (2x3 or 3x3 grid)  
**Use Case:** Detailed analysis sections, capability grids  
**Visual Reference:** Analysis capabilities grid (Image 3)  
**Grid:** `repeat(3, 1fr)` with responsive breakpoints  
**Migration:** Create new class with larger grid cards

### 5. Panel Hero Glass (`.panel-hero-glass`)
**Current:** `.glass-card` (full-width header variant)  
**Use Case:** Landing sections, CTAs, full-width headers  
**Layout:** Full-width, strong blur (30px), centered content  
**Migration:** Create new class with full-width + hero styling

### 6. Panel Sidebar Glass (`.panel-sidebar-glass`)
**Current:** `.glass-drawer--left`  
**Use Case:** Navigation, filters, metadata sidebars  
**Layout:** Vertical, sticky positioning, subtle blur (10px)  
**Migration:** Rename from `.glass-drawer` for semantic clarity

### 7. Panel Modal Glass (`.panel-modal-glass`)
**Current:** `.glass-modal`  
**Use Case:** Overlays, dialogs, confirmations  
**Layout:** Centered overlay, strong backdrop (rgba 0.8), dismiss actions  
**Migration:** Rename from `.glass-modal` for consistency

### 8. Panel Toast Glass (`.panel-toast-glass`)
**Current:** `.glass-toast`  
**Use Case:** Notifications, alerts, status messages  
**Layout:** Small floating panel, auto-dismiss, icon+message  
**Migration:** Rename from `.glass-toast` for consistency

### 9. Panel Blob Glass (`.panel-blob-glass`)
**Current:** Liquid Blob Glass pattern in glass-patterns.css  
**Use Case:** Decorative elements, backgrounds, organic shapes  
**Layout:** Blob shapes with morphing animation  
**Migration:** Extract from glass-patterns.css as separate named panel

### 10. Panel Neon Glass (`.panel-neon-glass`)
**Current:** `.glass-card` with border glow variants  
**Use Case:** Accent panels, highlights, CTAs  
**Visual:** Glowing borders (cyan/purple), vibrant colors, high contrast  
**Migration:** Create new class with animated neon border

---

## BEM Naming Convention for Complex Panels

### Tetris Panel (BEM Structure)
```css
.panel-tetris                  /* Block: Main panel container */
.panel-tetris__grid            /* Element: Grid container */
.panel-tetris__tile            /* Element: Individual metric tile */
.panel-tetris__tile-icon       /* Element: Tile icon */
.panel-tetris__tile-value      /* Element: Metric value */
.panel-tetris__tile-label      /* Element: Metric label */
.panel-tetris--compact         /* Modifier: Compact variant */
.panel-tetris--wide            /* Modifier: Wide layout */
```

### Intro Panel (BEM Structure)
```css
.panel-intro                   /* Block: Main panel container */
.panel-intro__title            /* Element: Title */
.panel-intro__description      /* Element: Description text */
.panel-intro__cta              /* Element: Call-to-action button */
.panel-intro--centered         /* Modifier: Centered variant (default) */
.panel-intro--left-aligned     /* Modifier: Left-aligned variant */
```

### Compact Cards Panel (BEM Structure)
```css
.panel-compact-cards           /* Block: Main panel container */
.panel-compact-cards__grid     /* Element: Grid container */
.panel-compact-cards__card     /* Element: Individual card */
.panel-compact-cards__icon     /* Element: Card icon */
.panel-compact-cards__title    /* Element: Card title */
.panel-compact-cards__desc     /* Element: Card description */
.panel-compact-cards--5-col    /* Modifier: 5-column layout (default) */
.panel-compact-cards--4-col    /* Modifier: 4-column layout */
```

---

## Migration Priority (Class-by-Class)

### CRITICAL (Phase 3 - Named Panels)
1. **Inline `.tetris-panel`** → Extract to `.panel-tetris` in glass-named-panels.css
2. **Inline `.token-metrics-tetris`** → Extract to `.panel-tetris__grid`
3. **Inline `.token-metric-tile`** → Extract to `.panel-tetris__tile`

### HIGH (Phase 3 - Named Panels)
4. Create `.panel-intro` (based on large centered `.glass-card`)
5. Create `.panel-compact-cards` (5-card horizontal grid)
6. Create `.panel-grid-cards` (3x3 detailed grid)
7. Create `.panel-hero-glass` (full-width hero sections)

### MEDIUM (Phase 4 - Consolidation)
8. Rename `.glass-modal` → `.panel-modal-glass`
9. Rename `.glass-toast` → `.panel-toast-glass`
10. Rename `.glass-drawer` → `.panel-sidebar-glass`
11. Create `.panel-blob-glass` (extract from glass-patterns.css)
12. Create `.panel-neon-glass` (extract border glow variants)

### LOW (Phase 9 - Migration)
13. Consolidate `.glass-card-clickable` → `.glass-card--interactive`
14. Update all HTML files to use new named panels

---

## HTML Migration Examples

### Before (Inline Styles - lens/index.html)
```html
<style>
    .tetris-panel {
        padding: 0 2.5rem;
        width: 70%;
        margin: 0 auto;
        background: rgba(26, 31, 58, 0.7);
        backdrop-filter: blur(20px);
        /* ... 40+ more lines ... */
    }
</style>

<div class="tetris-panel">
    <div class="token-metrics-tetris">
        <div class="token-metric-tile">
            <i class="fas fa-code"></i>
            <div class="metric-content">
                <span class="metric-value">12.5K</span>
                <span class="metric-label">Lines</span>
            </div>
        </div>
    </div>
</div>
```

### After (Named Panel - glass-named-panels.css)
```html
<link rel="stylesheet" href="../assets/css/glass-named-panels.css">

<div class="panel-tetris">
    <div class="panel-tetris__grid">
        <div class="panel-tetris__tile">
            <i class="panel-tetris__tile-icon fas fa-code"></i>
            <div class="panel-tetris__tile-content">
                <span class="panel-tetris__tile-value">12.5K</span>
                <span class="panel-tetris__tile-label">Lines</span>
            </div>
        </div>
    </div>
</div>
```

### Before (Generic Glass Card)
```html
<div class="glass-card" style="max-width: 800px; margin: 0 auto; text-align: center;">
    <h2>What Is CORTEX?</h2>
    <p>AI-powered codebase intelligence platform...</p>
</div>
```

### After (Named Panel)
```html
<div class="panel-intro">
    <h2 class="panel-intro__title">What Is CORTEX?</h2>
    <p class="panel-intro__description">AI-powered codebase intelligence platform...</p>
</div>
```

---

## CSS File Organization

### Current Structure (24 Files)
```
docs/assets/css/
├── glass-patterns.css         (1024 lines - 5 patterns + UI components)
├── main.css                   (4000 lines - 25% glass-related)
├── intentional-classes.css    (1500 lines - 10% glass-related)
├── index-multipanel.css       (400 lines)
├── learning-hub.css           (1000 lines)
├── [19 other CSS files]
```

### Proposed Structure (7 Core Files)
```
docs/assets/css/
├── cortex-glass-system.css           ← NEW: Master import file
├── glass-design-tokens.css           ← NEW: CSS variables (Phase 2)
├── glass-base-patterns.css           ← NEW: 5 core patterns from glass-patterns.css
├── glass-named-panels.css            ← NEW: 10 named panel styles (Phase 3)
├── glass-ui-components.css           ← NEW: Modals, toasts, dropdowns, tooltips
├── glass-animations.css              ← NEW: Hover, focus, loading states
└── glass-utilities.css               ← NEW: Helper classes (blur-lg, shadow-deep, etc.)
```

### Import Order (cortex-glass-system.css)
```css
/* CORTEX Glassmorphism Design System v4.0 */
@import 'glass-design-tokens.css';      /* 1. Design tokens first */
@import 'glass-base-patterns.css';      /* 2. Base patterns */
@import 'glass-named-panels.css';       /* 3. Named panels */
@import 'glass-ui-components.css';      /* 4. UI components */
@import 'glass-animations.css';         /* 5. Animations */
@import 'glass-utilities.css';          /* 6. Utilities last */
```

---

## Semantic Naming Benefits

### Before (Generic)
```css
.glass-card { /* Could be anything */ }
```
**Problem:** Doesn't indicate purpose, leads to overuse

### After (Semantic)
```css
.panel-tetris { /* Compact metrics grid */ }
.panel-intro { /* Hero description card */ }
.panel-compact-cards { /* 5-card capability row */ }
```
**Benefits:**
- ✅ Self-documenting code
- ✅ Easy "style X like Y" commands for CORTEX
- ✅ Prevents class name conflicts
- ✅ Encourages consistent usage

---

## CORTEX Integration Examples

With named panel system, CORTEX can understand natural language styling commands:

### Command: "Style this section like tetris panel"
**Result:** Apply `.panel-tetris` class with compact grid layout

### Command: "Make this intro look like the hero glass"
**Result:** Apply `.panel-hero-glass` class with full-width styling

### Command: "Use compact cards layout for capabilities"
**Result:** Apply `.panel-compact-cards` class with 5-card grid

### Command: "Add neon glass effect to this CTA"
**Result:** Apply `.panel-neon-glass` class with glowing border

---

## Next Steps

### Phase 2 (Design Tokens)
- Create `glass-design-tokens.css` with 100+ CSS variables
- Define all blur, color, border, shadow, and spacing tokens
- Import tokens as first file in master import

### Phase 3 (Named Panels)
- Extract inline `.tetris-panel` to `glass-named-panels.css`
- Create 9 remaining named panel styles
- Implement BEM naming for complex panels
- Add responsive breakpoints

### Phase 4 (Consolidation)
- Merge duplicate patterns from 24 files → 7 core files
- Update `main.css` to remove glassmorphism (import system instead)
- Rename UI components for consistency (`.glass-modal` → `.panel-modal-glass`)

---

**Document Status:** ✅ COMPLETE  
**Generated By:** CORTEX Planning System  
**Phase:** 1 - Discovery & Documentation  
**Next:** Phase 2 - Design Token Extraction
