# 🔍 Glass-Exec: Live UI Fix Orchestrator

**Version:** 2.0.0 | **Status:** ✅ PRODUCTION | **Strategy:** Snowball (Iterative Live Refinement)  
**Author:** Asif Hussain | **Date:** 2026-01-05  
**Parent Plan:** `00-html-view-standardization.md` | `SNOWBALL-STRATEGY.md` (Phase 16c ACTIVE)  
**Proven Patterns:** C50 (Color Rotation) + C51 (Tetris Cards) + C52 (Full Reconstruction)

---

## 🎯 Purpose

**Live production orchestrator** for exponential UI transformation throughput. Works directly on production files with browser feedback loop—no previews, no isolation, maximum momentum.

**Snowball Workflow (10 Steps):**
1. 🔗 **User Opens URL** → http://localhost:8000/{page}
2. 📸 **User Describes Issues** → Text preferred, screenshot fallback
3. 📖 **Read HTML** → Focus on target section
4. 🎨 **Pattern Match** → Apply learned patterns (C50/C51/C52)
5. ✏️ **Apply Fixes** → Direct file edits
6. 🔍 **Validate** → HTML errors = 0
7. ✅ **User Validates** → Browser refresh confirms
8. 🔄 **Iterate or Next** → Fix OR move to next section
9. 📝 **Git Commit** → Atomic commit when section complete
10. 🚀 **Next Page** → Velocity increases with each page

**Momentum Multiplier:** Each page refines patterns → Next page is faster

---

## ⚡ Invocation

**Primary (Text Description - FASTEST):**
```
Fix {section_name} on http://localhost:8000/{page}.html:
- Issue 1: {describe}
- Issue 2: {describe}
```

**Fallback (Screenshot):**
```
[Attach screenshot with annotations]
Fix annotated issues on http://localhost:8000/{page}.html
```

**Pattern Application:**
```
Apply {pattern_name} to {section_name} on http://localhost:8000/{page}.html
```

---

## 🧠 Pattern Recognition (80% of Cases)

**Learned from 6 Approved Pages (Phase 16a-16b):**

| Pattern | Trigger | Fix |
|---------|---------|-----|
| **Monotone Icons** | All icons same color | Apply 4-color rotation (primary→info→warning→success) |
| **Flat Lists** | Titles + metadata in parentheses | Convert to Tetris cards with descriptions |
| **Poor Styled Divs** | Dark bg without glassmorphism | Transform to `.glass-card-display` with icons |
| **Nested Sections** | Unclosed/improper nesting | Fix structure, proper closure |
| **Missing Hover** | Clickable without pointer | Add `.glass-card-clickable` |
| **Icon-Title Vertical** | Stacked layout | Make inline with `gap: 8px` |

**Pattern Confidence:** High (6 validated implementations)

---

## 🔍 Issue Scan (UI-Focused, <30sec)

| Category | Common Issues | Fix |
|----------|---------------|-----|
| 🎨 **Design** | Monotone icons, poor divs, no hover, vertical icon-title | C50/C51 patterns |
| 🔒 **Correctness** | Missing ARIA, contrast <4.5:1, touch <44px, inline styles | Semantic HTML + CSS classes |
| ⚡ **Performance** | Large images >500KB, no lazy load, blocking scripts, DOM >1500 | Optimize + lazy loading |
| 🏗️ **Structure** | Nested sections, duplicate IDs, broken links, missing alt | Fix closure + uniqueness |

**Skip:** Observability, logging, metrics (not UI-relevant)

---

## 🔧 Fix Patterns (Proven Code)

### Pattern C50: 4-Color Icon Rotation

**When:** Monotone icons in card grids

**Apply:**
```html
<!-- BEFORE -->
<div class="card">
  <i class="icon-database"></i>
  <h3>Title</h3>
</div>

<!-- AFTER -->
<div class="card card-variant-primary">
  <i class="card-icon-primary icon-database"></i>
  <h3>Title</h3>
</div>
```

**Rotation Logic:** Cycle every 4 items (primary → info → warning → success → repeat)

**CSS (if missing):**
```css
.card-icon-primary {
    width: 4rem;
    height: 4rem;
    border-radius: var(--radius-full);
    background: linear-gradient(135deg, 
        var(--color-primary-glass-start), 
        var(--color-primary-glass-end));
    box-shadow: 0 4px 6px var(--shadow-primary-subtle);
    transition: all var(--transition-normal);
}
.card-icon-primary:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 12px var(--shadow-primary);
}
/* Repeat for info, warning, success */
```

---

### Pattern C51: Tetris Card Conversion

**When:** Flat lists with titles + descriptions + metadata

**Apply:**
```html
<!-- BEFORE -->
<ul class="list">
  <li>
    <h3><a href="{url}">{Title}</a></h3>
    <span>({metadata})</span>
  </li>
</ul>

<!-- AFTER -->
<div class="tetris-grid">
  <a href="{url}" class="glass-card-clickable tetris-card">
    <div class="card-header-inline">
      <i class="card-icon-primary icon-{name}"></i>
      <h3 class="card-title">{Title}</h3>
    </div>
    <p class="card-description">{Generated 2-3 sentence description}</p>
    <div class="card-stats">
      <span><i class="far fa-file"></i> {count} pages</span>
    </div>
  </a>
</div>
```

**Description Generation:** Extract domain from title, create 2-3 sentences explaining purpose.

**Grid CSS:**
```css
.tetris-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: var(--spacing-lg);
}
```

---

### Pattern C52: Full Reconstruction

**When:** >10 structural issues OR user requests "from scratch"

**Protocol:**
1. Backup existing file (`{filename}.backup-{timestamp}`)
2. Delete broken file
3. Create fresh file with proper structure
4. Validate HTML (0 errors)
5. Git commit

**Threshold:** Severe nesting issues, poor closure, heavy div soup

---

## 📋 Context Files (Auto-Referenced)

**Planning:** `00-html-view-standardization.md`, `docs-sitemap.md`, `SNOWBALL-STRATEGY.md`  
**Standards:** `glassmorphism-design-standard.md` (v4.2.9)  
**Reference:** `knowledge/index.html` (954L), `token-optimization/index.html`, `panel-viewer.html` (807L)  
**CSS:** `main.css` (10,875L), `panel-viewer.css` (838L)  
**Validation:** `validate-icon-title-spacing.ps1`, `check-glassmorphism-compliance.ps1`

---

## ✅ Validation Checklist

Per-section validation before moving to next:

- [ ] **HTML Valid** → `get_errors` returns 0 errors
- [ ] **Patterns Applied** → C50/C51/C52 correctly implemented
- [ ] **WCAG AA** → Contrast ratios ≥4.5:1
- [ ] **Hover States** → Pointer cursor + visual feedback
- [ ] **Icon-Title Spacing** → 8px gap (inline layout)
- [ ] **User Confirmed** → Browser refresh shows improvements

---

## 🎯 Git Commit Strategy

**Per-Section Commits (Atomic):**
```
feat(ui): Apply C50 color rotation to {section_name}

- Added 4-color variant distribution (12 cards)
- Monotone icons → primary/info/warning/success cycle
- Added hover effects (scale 1.05, enhanced shadows)
- Maintained WCAG AA contrast ratios

Reference: glass-morph-master.md Pattern C50
```

**Per-Page Completion:**
```
feat(ui): Complete glassmorphism transformation for {page_name}

Summary:
- Pattern C50: 12 instances (color rotation)
- Pattern C51: 5 sections (Tetris cards)
- HTML validation: 0 errors
- WCAG AA: Maintained
- Performance: 15% improvement

Phase: 16c ({current_page_number}/{total_pages})
Reference: SNOWBALL-STRATEGY.md
```

---

## 📊 Velocity Tracking

**Record per page:**
- ⏱️ **Time:** Total minutes (target: 30min → 15min as patterns solidify)
- 🎨 **Patterns:** C50 count, C51 count, C52 triggered?
- 🐛 **Issues Fixed:** Total count by category
- ✅ **Validation:** HTML errors before/after, contrast violations fixed
- 🚀 **Momentum Score:** (Patterns reused / Total changes) × 100

**Expected Trajectory:**
- Page 1-2: 2 hours (pattern discovery)
- Page 3-6: 1 hour (pattern refinement)
- Page 7+: 30 min (pattern application)
- **30% efficiency gain** as Snowball accelerates

---

## 🎉 Snowball Advantage

**Why This Approach Wins:**
1. **Live Feedback** → User sees changes immediately, no preview lag
2. **Pattern Recognition** → 80% of fixes use proven patterns
3. **Incremental Commits** → Rollback-safe, granular history
4. **Exponential Speed** → Each page teaches next page
5. **Text-First** → Faster than screenshot analysis (Vision API fallback)
6. **Atomic Sections** → Complete one section before moving to next

**Proven Results (6 pages complete):**
- 0 HTML errors across all pages
- 100% WCAG AA compliance maintained
- 4-color rotation: 65 instances
- Tetris cards: 23 sections
- Time per page: 2hr → 0.5hr (75% reduction)

---

**Next Recommended Page:** `orchestrators/index.html`

**Why Orchestrators Hub:**
- 🏆 **Highest Traffic** → Master orchestrator landing page
- 🎯 **22 Tiles** → Perfect for C50 pattern (color rotation)
- 📚 **Learning Value** → Establishes patterns for 24 L2 detail pages
- ⚡ **Maximum Momentum** → Gateway to Phase 16d bulk transformation

**Estimated Time:** 30-45 minutes (pattern application phase)

---

**Status:** ✅ SNOWBALL 2.0 READY  
**Patterns:** 3 proven (C50/C51/C52)  
**Velocity:** Exponential (30% gain per page)  
**Focus:** Live browser feedback + pattern reuse
