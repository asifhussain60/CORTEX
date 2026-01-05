# 🎴 Tetris Card Conversion - Reusable Prompt Template

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION | **Type:** UI Pattern Template  
**Author:** Asif Hussain | **Date:** 2026-01-05  
**Parent Pattern:** Glassmorphism Design Standard v4.2.9

---

## 🎯 Purpose

Convert static list/grid layouts into interactive Tetris-style cards with glassmorphism styling, following approved design patterns from token-optimization and architecture pages.

---

## ⚡ Quick Invocation

```
Convert {section_description} on {file_path} to Tetris-style cards with glassmorphism styling.

CONTEXT FILES (auto-reference):
- Design Standard: cortex-brain/documents/standards/glassmorphism-design-standard.md
- Reference Implementation: docs/token-optimization/index.html (Optimization Strategy cards)
- Card CSS: docs/assets/css/main.css (.card-icon-{variant} classes)
- Pattern Example: C50.md (glassmorphism color application)
```

**Example Usage:**
```
Convert "All 17 Domain Hubs Now Available" section on docs/knowledge/index.html to Tetris-style cards with glassmorphism styling.
```

---

## 🎨 What This Pattern Does Automatically

**WITHOUT explicit reminders:**

1. ✅ **Analyzes source layout** → Identifies list/grid items with icons, titles, metadata
2. ✅ **Selects card variant** → Chooses `.glass-card-clickable` vs `.glass-card-display`
3. ✅ **Applies color rotation** → Cycles through `.card-icon-{primary|success|info|warning}`
4. ✅ **Adds hover effects** → Glowing border, lift, pointer cursor (clickable only)
5. ✅ **Preserves metadata** → Module counts, hours, badges converted to `.card-stats`
6. ✅ **Maintains accessibility** → ARIA labels, semantic HTML, WCAG AA compliance
7. ✅ **Responsive design** → Masonry grid auto-adjusts (3 cols desktop → 2 cols tablet → 1 col mobile)

---

## 📐 Pattern Structure

### Standard Tetris Card Template

```html
<!-- Clickable Card (with link) -->
<a href="{page_url}" class="glass-card-clickable animation-t1">
    <div class="card-icon card-icon-{variant}">
        <i class="{font_awesome_icon}"></i>
    </div>
    <h3 class="card-title">{Title}</h3>
    <p class="card-description">{Description text (2-3 sentences)}</p>
    <div class="card-stats">
        <span class="stat-item"><i class="fas fa-{icon}"></i> {Metadata}</span>
    </div>
</a>

<!-- Display Card (no link) -->
<div class="glass-card-display animation-t1">
    <div class="card-icon card-icon-{variant}">
        <i class="{font_awesome_icon}"></i>
    </div>
    <h3 class="card-title">{Title}</h3>
    <p class="card-description">{Description}</p>
</div>
```

### Color Variant Rotation Pattern

**For balanced visual distribution:**

```
Card 1 → .card-icon-primary (purple)
Card 2 → .card-icon-info (blue)
Card 3 → .card-icon-warning (amber)
Card 4 → .card-icon-success (green)
Card 5 → .card-icon-primary (repeat cycle)
...
```

**Color Meanings:**
- **Primary (Purple):** Core features, essential domains
- **Info (Blue):** Informational, technical domains
- **Warning (Amber):** Important, attention-needed domains
- **Success (Green):** Active, positive, completed domains

---

## 🔄 Conversion Rules

### From List/Grid to Cards

| Source Element | Tetris Card Element | Notes |
|----------------|---------------------|-------|
| `<div class="highlight-grid">` | `<div class="masonry-grid">` | Responsive grid container |
| `<div><i>icon</i> Title</div>` | `.card-icon` + `.card-title` | Icon gets glassmorphism container |
| Inline metadata `(5 modules)` | `.card-stats` with icon | Structured metadata display |
| `<a class="highlight-link">` | `<a class="glass-card-clickable">` | Full card becomes clickable |
| Static content | `.glass-card-display` | Non-clickable display card |

### CSS Classes Required

**Card Structure:**
- `.glass-card-clickable` → Interactive cards (links)
- `.glass-card-display` → Static display cards
- `.animation-t1` → Subtle T1 animations (Level 1 pages)

**Icon Containers:**
- `.card-icon` → Base icon container
- `.card-icon-primary` → Purple gradient + shadow
- `.card-icon-success` → Green gradient + shadow
- `.card-icon-info` → Blue gradient + shadow
- `.card-icon-warning` → Amber gradient + shadow

**Content Elements:**
- `.card-title` → Card heading (h3)
- `.card-description` → Description paragraph
- `.card-stats` → Metadata container
- `.stat-item` → Individual stat with icon

---

## 📊 Before & After Example

### ❌ Before (Static List)

```html
<div class="highlight-box highlight-box-success">
    <div class="highlight-icon">
        <i class="fas fa-check-circle"></i>
    </div>
    <div class="highlight-content">
        <h3>All 17 Domain Hubs Now Available!</h3>
        <p>Phase 2 & 3 learning paths are complete with 13 additional domains:</p>
        <div class="highlight-grid">
            <div><i class="fas fa-database"></i> <strong>Database Design</strong> (5 modules)</div>
            <div><i class="fas fa-cloud"></i> <strong>Cloud Architecture</strong> (4 modules)</div>
            <!-- ... more items ... -->
        </div>
    </div>
</div>
```

**Issues:**
- ❌ Low visual hierarchy (flat text list)
- ❌ No hover feedback (not obvious items are clickable)
- ❌ Minimal color differentiation
- ❌ Static presentation (no glassmorphism)
- ❌ Module count buried in parentheses

### ✅ After (Tetris Cards)

```html
<!-- Header Card -->
<div class="glass-card-display animation-t1" style="text-align: center; margin-bottom: 2rem;">
    <div class="card-icon card-icon-success" style="margin: 0 auto 1rem;">
        <i class="fas fa-check-circle"></i>
    </div>
    <h3 style="font-size: 1.75rem; font-weight: 700;">All 17 Domain Hubs Now Available!</h3>
    <p style="font-size: 1.125rem; color: var(--text-secondary);">Phase 2 & 3 learning paths are complete</p>
</div>

<!-- Card Grid -->
<div class="masonry-grid">
    <!-- Database Design -->
    <a href="database-hub.html" class="glass-card-clickable animation-t1">
        <div class="card-icon card-icon-primary">
            <i class="fas fa-database"></i>
        </div>
        <h3 class="card-title">Database Design</h3>
        <p class="card-description">Schema design, normalization, indexing strategies, query optimization, and data modeling best practices.</p>
        <div class="card-stats">
            <span class="stat-item"><i class="fas fa-graduation-cap"></i> 5 Modules</span>
        </div>
    </a>
    
    <!-- More cards... -->
</div>
```

**Improvements:**
- ✅ Clear visual hierarchy (cards with depth)
- ✅ Hover feedback (glowing border, lift, pointer cursor)
- ✅ Color-coded categories (4-color rotation)
- ✅ Glassmorphism styling (blur, gradients, shadows)
- ✅ Structured metadata (icon + label)
- ✅ Expandable descriptions (2-3 sentence summaries)
- ✅ Responsive layout (auto-adjusts to screen size)

---

## 🎯 Use Cases

**When to use Tetris Card conversion:**

1. ✅ **Feature Lists** → Multiple features/domains with icons + metadata
2. ✅ **Learning Paths** → Course modules, training tracks, documentation sections
3. ✅ **Navigation Grids** → Hub pages, category indexes, domain directories
4. ✅ **Achievement Panels** → Completed items, milestones, capabilities
5. ✅ **Static Highlights** → Important announcements with multiple sub-items

**When NOT to use:**

1. ❌ **Single Items** → Use standard `.glass-card` instead
2. ❌ **Tables** → Preserve table structure for data comparison
3. ❌ **Linear Workflows** → Use step indicators for sequential processes
4. ❌ **Inline Lists** → Small lists within paragraphs stay inline
5. ❌ **Dense Content** → Long-form text better suited for paragraphs

---

## 📚 Context Files Reference

### 1. Design Standard
**File:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` (v4.2.9)

**Key Sections:**
- **Color Class Reference** → `.card-icon-{variant}` patterns (Lines 868-950)
- **Animation Philosophy** → T1 subtle animations for Level 1 pages
- **Clickable vs Display** → `.glass-card-clickable` vs `.glass-card-display` distinction
- **CSS Quality Rules** → Zero duplicates, 100% usage, zero inline styles
- **Mobile Optimization** → 44px minimum touch targets, responsive grids

### 2. Reference Implementation (Token Optimization)
**File:** `docs/token-optimization/index.html`

**Key Patterns:**
- Optimization Strategy cards (Lines 220-280)
- `.card-icon-{variant}` color rotation
- `.card-stats` metadata display
- `.glass-card-clickable` with hover effects

### 3. Reference Implementation (Architecture)
**File:** `docs/architecture/index.html`

**Key Patterns:**
- Orchestrator cards with badges
- Feature description structure
- Masonry grid responsive behavior

### 4. Main Stylesheet
**File:** `docs/assets/css/main.css`

**Key Classes:**
- `.card-icon-primary` → Lines 868-877 (purple gradient)
- `.card-icon-success` → Lines 879-888 (green gradient)
- `.card-icon-info` → Lines 908-917 (blue gradient)
- `.card-icon-warning` → Lines 898-907 (amber gradient)
- Hover effects → Lines 919-946

### 5. Previous Example (C50.md)
**File:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/C50.md`

**Workflow:**
- Color application to existing cards
- CSS class selection logic
- Design standard compliance validation

---

## 🔍 Vision API Integration

**AUTOMATIC:** When images attached, Vision API analyzes them for:

1. **Layout Detection** → Identifies list/grid structure to convert
2. **Icon Extraction** → Recognizes Font Awesome icons in source
3. **Metadata Parsing** → Extracts module counts, hours, badges
4. **Color Analysis** → Suggests optimal color variant distribution
5. **Accessibility Check** → Validates contrast, spacing, touch targets

**Vision Middleware:** `src/operations/utilities/vision_context_middleware.py`

---

## ✅ Validation Checklist

After conversion, verify:

- [ ] All cards use `.glass-card-clickable` (links) or `.glass-card-display` (static)
- [ ] Color variants cycle through 4 colors (primary → info → warning → success)
- [ ] Icons wrapped in `.card-icon.card-icon-{variant}` containers
- [ ] Metadata structured in `.card-stats` with icons
- [ ] Descriptions are 2-3 sentences (not single words)
- [ ] Hover effects work (glowing border, lift, pointer cursor)
- [ ] Mobile responsive (cards stack vertically)
- [ ] No inline styles except for header centering
- [ ] Font Awesome 6.x icons used (`fas`, `far`, `fab`)
- [ ] WCAG AA contrast compliance

---

## 🚀 Future Enhancements

**Potential improvements for v2.0:**

1. **Dynamic Badge System** → Auto-generate badges based on domain type
2. **Progress Indicators** → Show completion percentage for learning paths
3. **Card Filtering** → JavaScript filter by category/difficulty
4. **Animated Counters** → Module count animates on scroll into view
5. **Card Sorting** → Sort by popularity, difficulty, completion status

---

## 📝 Related Patterns

| Pattern | Use Case | Template File |
|---------|----------|---------------|
| **Glassmorphism Styling** | Apply colors to existing cards | `PROMPT-TEMPLATE-glassmorphism-styling.md` |
| **Tetris Card Conversion** | List/grid → Interactive cards | This file |
| **Multi-Panel Layout** | 4+ categories in tile | Design standard §5.2 |
| **Token Metrics Tetris** | Horizontal metric tiles | Token optimization page |

---

## 📊 Conversion Summary (C51 - Knowledge Index)

**Applied To:** `docs/knowledge/index.html`  
**Date:** January 5, 2026  
**Pattern:** Tetris Card Conversion v1.0.0

### Changes Made

**HTML Transformation:**
- Removed `.highlight-box.highlight-box-success` wrapper
- Created centered header card with `.card-icon-success`
- Converted 13 list items → 13 individual `.glass-card-clickable` cards
- Added descriptions (2-3 sentences per domain)
- Structured metadata with `.card-stats` + `.stat-item`
- Applied 4-color rotation (primary → info → warning → success)

**Visual Improvements:**
- ✅ Clear visual hierarchy with depth
- ✅ Glassmorphism gradients + shadows
- ✅ Hover effects (glowing border + lift)
- ✅ Color-coded categories
- ✅ Responsive masonry grid
- ✅ Structured metadata display

**Files Modified:**
1. `docs/knowledge/index.html` → Lines 188-358 (tetris cards)

**CSS Classes Used:**
- `.glass-card-clickable` → 13 instances
- `.card-icon-primary` → 4 instances
- `.card-icon-info` → 3 instances
- `.card-icon-warning` → 3 instances
- `.card-icon-success` → 3 instances
- `.card-title` → 13 instances
- `.card-description` → 13 instances
- `.card-stats` → 13 instances

**Color Distribution:**
```
Database Design      → primary (purple)
Cloud Architecture   → info (blue)
DevOps & CI/CD       → warning (amber)
Microservices        → success (green)
Domain-Driven Design → primary (purple)
Software Engineering → info (blue)
Frontend Development → warning (amber)
Performance          → success (green)
Mobile Development   → primary (purple)
Messaging & Events   → info (blue)
RAG Domains          → warning (amber)
UI/UX Design         → success (green)
Containers & K8s     → primary (purple)
```

**Before:** Static list with 13 inline items  
**After:** 13 interactive glassmorphism cards with hover effects

---

**Status:** ✅ COMPLETE | **Reusable:** YES | **Version:** 1.0.0  
**Next Use:** Apply pattern to other hub pages, category indexes, feature lists
