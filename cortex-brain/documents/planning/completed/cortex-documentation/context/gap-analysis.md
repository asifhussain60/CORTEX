# Phase -1.3: Gap Analysis

**Plan:** Glassmorphism Documentation Standardization  
**Version:** 7.0.0 | **Date:** January 1, 2026  
**Author:** Asif Hussain

---

## 🎯 Analysis Summary

**Total Required Patterns:** 23  
**Already Available:** 14 (61%)  
**Needs Extraction:** 5 (22%)  
**Needs Creation:** 4 (17%)

---

## ✅ Available Patterns (Ready to Use)

| # | Pattern | Source | Status |
|---|---------|--------|--------|
| 1 | CSS Variables (design tokens) | `variables.css` | ✅ READY |
| 2 | `.glass-card` | `glass-patterns.css` | ✅ READY |
| 3 | `.glass-card--sm` | `glass-patterns.css` | ✅ READY |
| 4 | `.glass-card--lg` | `glass-patterns.css` | ✅ READY |
| 5 | `.glass-card--no-hover` | `glass-patterns.css` | ✅ READY |
| 6 | `.neuglass-card` | `glass-patterns.css` | ✅ READY |
| 7 | `.morph-card` | `glass-patterns.css` | ✅ READY |
| 8 | `.light-leak-glass` | `glass-patterns.css` | ✅ READY |
| 9 | Spacing variables (`--space-*`) | `variables.css` | ✅ READY |
| 10 | Blur variables (`--blur-*`) | `variables.css` | ✅ READY |
| 11 | Glow effects (`--glow-*`) | `variables.css` | ✅ READY |
| 12 | Shadow variables | `variables.css` | ✅ READY |
| 13 | Transition variables | `variables.css` | ✅ READY |
| 14 | Reduced motion media query | `variables.css` | ✅ READY |

---

## ⚠️ Patterns Needing CSS Extraction (inline → external)

| # | Pattern | Current Location | Target Location | Lines |
|---|---------|------------------|-----------------|-------|
| 1 | `.category-panels-grid` | `index.html` inline | `main.css` or new `panels.css` | ~35 |
| 2 | `.category-subpanel` | `index.html` inline | `main.css` or new `panels.css` | ~50 |
| 3 | `.category-subpanel.single-tag` | `index.html` inline | `main.css` or new `panels.css` | ~25 |
| 4 | `.main-panel-wrapper` | `index.html` inline | `main.css` or new `panels.css` | ~20 |
| 5 | `.category-tag` | `index.html` inline | `main.css` or new `tags.css` | ~30 |

**Total Lines to Extract:** ~160

**Extraction Priority:** Phase 1.1 (before any new Level 0 work)

---

## 🆕 Patterns Requiring Creation

### 1. Grid Variants (for multi-panel tiles)

**Required:**
```css
/* 2×2 Grid (Security pattern - 4 panels) */
.category-panels-grid.grid-2x2 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr);
}

/* 2×3 Grid (Orchestrators pattern - 5-6 panels) */
.category-panels-grid.grid-2x3 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, 1fr);
}

/* 3×2 Grid already exists for STS */
```

**Status:** ⚠️ NEEDS CREATION  
**Effort:** Low (~20 lines)

---

### 2. Header Component (Level 1 & 2)

**Required Template:**
```html
<!-- _header-level1-2.html partial -->
<header class="glass-header glass-header--no-logo">
    <div class="header-content">
        <nav class="header-nav">
            <a href="{HOME_PATH}" class="nav-link"><i class="fas fa-home"></i> Home</a>
            <a href="{HUB_PATH}" class="nav-link"><i class="fas fa-{ICON}"></i> {DOMAIN}</a>
        </nav>
    </div>
</header>
```

**CSS Required:**
```css
.glass-header--no-logo .header-brand {
    display: none;
}
```

**Status:** ⚠️ NEEDS CREATION  
**Effort:** Low (~15 lines CSS, ~10 lines HTML)

---

### 3. Non-Clickable Subpanel Differentiation

**Current Issue:** `.category-subpanel` has hover effects that look clickable

**Required Pattern:**
```css
/* Non-clickable subpanel (display only) */
.category-subpanel--display {
    cursor: default;
    /* Remove hover lift effect */
}

.category-subpanel--display:hover {
    transform: none;
    box-shadow: initial;
}

/* Clickable tags within remain interactive */
.category-subpanel--display .category-tag:hover {
    transform: translateY(-2px);
    box-shadow: var(--glow-sm);
}
```

**Status:** ⚠️ NEEDS CREATION  
**Effort:** Low (~20 lines)

---

### 4. Animation Tier CSS Classes

**Required Pattern:**
```css
/* T1 Subtle (Level 1 & 2) - DEFAULT */
.animation-tier-1,
.t1-animation {
    --animation-duration: 0.2s;
    --transition-duration: 0.2s;
}

/* T2 Accent (Interactive feedback) */
.animation-tier-2,
.t2-animation {
    --animation-duration: 0.15s;
    --transition-duration: 0.15s;
}

/* T3 Dramatic (Level 0 ONLY) */
.animation-tier-3,
.t3-animation {
    --animation-duration: 2s;
    --transition-duration: 0.4s;
}
```

**Status:** ⚠️ NEEDS CREATION  
**Effort:** Low (~25 lines)

---

## 📊 Gap Analysis Matrix

| Category | Required | Available | Gap | Action |
|----------|----------|-----------|-----|--------|
| Glass Cards | 5 | 5 | 0 | ✅ None |
| CSS Variables | 20+ | 20+ | 0 | ✅ None |
| Panel Grids | 3 | 1 | 2 | Create `grid-2x2`, `grid-2x3` |
| Subpanel Styles | 3 | 2 (inline) | 1 | Extract + create `--display` variant |
| Tag Styles | 2 | 1 (inline) | 0 | Extract to external CSS |
| Header Templates | 2 | 1 | 1 | Create Level 1/2 template |
| Footer Template | 1 | 1 (inline) | 0 | Extract to template |
| Animation Tiers | 3 | 0 | 3 | Create T1/T2/T3 classes |

---

## 🔧 Implementation Roadmap

### Phase 0.3 (CSS Architecture Review) - Pre-Work
1. **Extract** 160+ lines from `index.html` inline styles to external CSS
2. **Create** `docs/assets/css/panels.css` for panel-specific styles
3. **Update** `main.css` imports

### Phase 1.1 (Before Level 0 Work)
1. **Create** `.grid-2x2` and `.grid-2x3` variants
2. **Create** `.category-subpanel--display` non-clickable variant
3. **Create** animation tier utility classes

### Phase 2.1 (Before Level 1 Work)
1. **Create** Level 1/2 header template (no logo)
2. **Test** responsive behavior at 375px/768px/1440px

---

## 📁 Proposed New Files

| File | Purpose | Lines (est.) |
|------|---------|--------------|
| `docs/assets/css/panels.css` | Multi-panel grid and subpanel styles | ~200 |
| `docs/assets/css/animation-tiers.css` | T1/T2/T3 animation utilities | ~50 |
| `docs/templates/_header-level0.html` | Level 0 header partial | ~20 |
| `docs/templates/_header-level1-2.html` | Level 1/2 header partial | ~15 |
| `docs/templates/_footer.html` | Universal footer partial | ~10 |

**Total New CSS:** ~250 lines  
**Total New HTML Templates:** ~45 lines

---

## ✅ Phase -1 Acceptance Criteria (Final Check)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 4+ knowledge library documents consulted | ✅ PASS | 5 documents queried |
| Existing patterns documented with file references | ✅ PASS | 14 ready, 5 to extract |
| Reusable components identified | ✅ PASS | Full catalog created |
| Gap analysis completed | ✅ PASS | 4 creation items, 5 extraction items |

---

## 📊 Phase -1 Summary

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ PHASE -1: KNOWLEDGE LIBRARY CONSULTATION - COMPLETE                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ -1.0: Domain Detection          [████████████████████] 100% │ ✅ COMPLETE   ║
║ -1.1: Knowledge Library Query   [████████████████████] 100% │ ✅ COMPLETE   ║
║ -1.2: Pattern Extraction        [████████████████████] 100% │ ✅ COMPLETE   ║
║ -1.3: Gap Analysis              [████████████████████] 100% │ ✅ COMPLETE   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ PHASE -1 OVERALL                [████████████████████] 100% │ 4/4 TASKS     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

**Phase -1 Complete** → Proceed to Phase 0: Functionality Discovery & Baseline
