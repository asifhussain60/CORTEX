# 🎨 Glassmorphism Design Standard

**Version:** 4.0.1 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Last Updated:** January 1, 2026  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## 📋 Purpose

This standard defines **modern glassmorphism patterns** for CORTEX documentation and UI components, incorporating **cutting-edge 2025 design techniques** including multi-layer depth, dynamic lighting, micro-interactions, and performance optimization.

**Target:** HTML documentation, dashboards, STS showcases, interactive visualizations  
**Compatibility:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

**⚠️ Animation Philosophy (v4.0.0):**
- **Subtle & Modern:** All animations designed to be non-distracting
- **Level 1 & Level 2 Pages:** ONLY T1 subtle animations (0.2-0.3s transitions, no dramatic effects)
- **Clickable Tiles:** Glowing border + lift + large pointer cursor on hover
- **Non-Clickable Tiles:** Slow glass reflection (8s) + default cursor, NO glow
- **Consistent Styling:** Clear visual differentiation between interactive and display elements
- **⛔ NO Dramatic Animations:** borderGlowSweep, blobMorph, and other T3 effects ONLY on Level 0 (Home page)

**Scope:** Applies to ALL 9 CORTEX home page tiles and their 2-level hierarchies:
1. 🧠 Architecture → SKULL, Knowledge Graph, Brain Tiers, Context
2. 🛡️ Security → Threat Modeling, Compliance, Audits
3. 🎯 Orchestrators → 17 autonomous workflow detail pages
4. 💰 Token Optimization → Analysis, Strategies, Savings
5. 🔧 Sharpen The Saw → Code Quality, SOLID, Testing, Performance, Security, Docs
6. 📚 CORTEX Best Practices → 35 Guidelines (3 Level 2 pages)
7. 🛠️ Toolkit Manager → Discovery, Orchestration, Integration
8. 🔍 CORTEX LENS → AST, Reverse Engineering, Intelligence
9. 🚀 Get Started → Installation, Configuration, First Steps

---

## 🏗️ View Hierarchy (2-Level Maximum)

**Critical Rule:** All tiles follow this structure:
```
Level 0 (Home) → Level 1 (Tile Overview) → Level 2 (Component Detail)
```

**⛔ NO Level 3:** Use expandable sections, tabs, or modals for deeper content.

**Level 0 Tile Patterns:**

| Tile | Pattern | Grid Layout | Rationale |
|------|---------|-------------|-----------|
| **Security (13 pages, 4 categories)** | Multi-Panel | 2x2 (4 subpanels) | Complex categorization requires visual separation |
| **Orchestrators (19 pages, 5 categories)** | Multi-Panel | 2x3 (5 subpanels, 1 odd) | Most complex tile, needs clear organization |
| **Sharpen The Saw (6 pages, 6 categories)** | Multi-Panel | 3x2 (6 subpanels, compact single-tag) | 6 single-link categories displayed side-by-side |
| **Architecture (4 pages)** | Standard Tile | N/A | Simple structure, direct navigation |
| **Token Optimization (3 pages)** | Standard Tile | N/A | Simple linear workflow |
| **Best Practices (35 guidelines)** | Standard Tile | N/A | Guideline format works in tile |
| **Toolkit Manager (3 pages)** | Standard Tile | N/A | Simple structure |
| **CORTEX Lens (3 pages)** | Standard Tile | N/A | Simple workflow |
| **Get Started (3 pages)** | Standard Tile | N/A | Onboarding sequence |

**Multi-Panel Pattern Intelligence (v4.0.1):**

**Grid Layout Rules:**
- **4 subpanels:** 2x2 grid (Security pattern)
- **5 subpanels:** 2x3 grid with 1 odd panel (Orchestrators pattern)
- **6 subpanels:** 3x2 grid (STS pattern - side-by-side rows)
- **Single-tag subpanels:** More compact sizing (min-height: 280px vs 380px)

**HTML Implementation:**
```html
<!-- 3x2 Grid for 6 panels -->
<div class="category-panels-grid grid-3x2">
    <div class="category-subpanel single-tag">
        <!-- Icon, title, description, single link -->
    </div>
    <!-- Repeat 6 times -->
</div>
```

**CSS Classes:**
- `.grid-3x2` - Forces 3x2 layout (2 columns, 3 rows)
- `.single-tag` - Compact subpanel styling for single links
- Default (no class) - 2x2 grid for 4-5 panels

**When to use each pattern:**
- Main wrapper panel containing multiple category sub-panels
- Each sub-panel shows category icon, title, description, and links
- Tetris/masonry grid layout for visual interest (multi-tag subpanels)
- Full-width single links for single-tag subpanels (STS pattern)
- Non-clickable sub-panels (display only), clickable tags within

**Standard Tile Pattern (All Others):**
- Single clickable card navigating to Level 1 index
- Icon, title, caption layout
- Hover glow and lift effect

---

## 🎯 Core Principles

1. **Multi-Layer Depth** - Stacked glass layers with varying opacity
2. **Dynamic Lighting** - Simulated light sources for realism
3. **Smooth Interactions** - Micro-animations with cubic-bezier easing
4. **GPU Acceleration** - Hardware-accelerated transforms
5. **Performance First** - Conditional blur, lazy loading
6. **Accessibility** - WCAG 2.1 AA compliance, reduced-motion support
7. **Subtle by Default** - T1 animations for ALL Level 1 & Level 2 pages (v4.0.0)
8. **2-Level Maximum** - All 9 tiles limited to Level 0 → Level 1 → Level 2
9. **NO Inline Styles** - All styling via CSS classes (zero tolerance for `style=""` attributes)
10. **Header/Footer Standard** - Standardized glass header/footer across ALL views
11. **Responsive Mandatory** - Mobile-first design with 375px base, tablet 768px, desktop 1440px breakpoints
12. **Proper Spacing** - All stacked elements MUST have adequate margin/padding (minimum 1.5rem vertical gap between cards/panels) (v4.0.1)

---

## 🎨 Header & Footer Standardization

### Required Structure

**⚠️ CRITICAL: Logo only on Level 0 (Home Page)**

#### Level 0 Glass Header (WITH LOGO)
```html
<header class="glass-header">
    <div class="header-content">
        <a href="index.html" class="header-brand">
            <i class="fas fa-brain"></i>
            <h1>CORTEX</h1>
        </a>
        <nav class="header-nav">
            <a href="#features" class="nav-link">Features</a>
            <a href="#documentation" class="nav-link">Documentation</a>
            <a href="https://github.com/asifhussain60/CORTEX" class="nav-link" target="_blank">
                <i class="fab fa-github"></i> GitHub
            </a>
        </nav>
    </div>
</header>
```

#### Level 1 & Level 2 Glass Header (NO LOGO - Home Link Only)
```html
<header class="glass-header">
    <div class="header-content">
        <nav class="header-nav">
            <a href="../index.html" class="nav-link"><i class="fas fa-home"></i> Home</a>
        </nav>
    </div>
</header>
```

#### Glass Footer
```html
<footer class="glass-footer">
    <div class="footer-content">
        <div class="footer-copyright">
            <p>© 2025 Asif Hussain. All rights reserved.</p>
        </div>
        <div class="footer-links">
            <a href="https://github.com/asifhussain60/CORTEX" target="_blank">
                <i class="fab fa-github"></i> GitHub
            </a>
            <a href="https://asifhussain60.github.io/CORTEX/" target="_blank">
                <i class="fas fa-home"></i> Website
            </a>
            <span class="footer-version">CORTEX v4.0</span>
        </div>
    </div>
</footer>
```

### CSS Classes

```css
/* Glass Header */
.glass-header {
    background: rgba(10, 14, 39, 0.8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
    transition: all 0.3s ease;
}

/* Level 0: Header with logo and navigation (space-between) */
.glass-header .header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Level 1 & 2: Header with navigation only (centered) */
.glass-header .header-content:has(.header-nav:only-child) {
    justify-content: center;
}

.header-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
}

.header-brand i {
    font-size: 1.5rem;
    color: var(--accent-primary);
}

.header-brand h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.header-nav {
    display: flex;
    gap: 2rem;
    align-items: center;
}

.nav-link {
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
    cursor: pointer;
}

.nav-link:hover {
    color: var(--accent-primary);
}

.nav-link i {
    margin-right: 0.25rem;
}

/* Mermaid Diagram Container */
.mermaid-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: var(--spacing-xl, 2rem) 0;
    width: 100%;
}

.mermaid {
    max-width: 800px;
    width: 100%;
}

/* Glass Footer */
.glass-footer {
    background: rgba(10, 14, 39, 0.8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2rem;
    margin-top: 4rem;
    transition: all 0.3s ease;
}

.footer-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.footer-copyright p {
    color: var(--text-muted);
    margin: 0;
    font-size: 0.875rem;
}

.footer-links {
    display: flex;
    gap: 1.5rem;
    align-items: center;
}

.footer-links a {
    color: var(--text-secondary);
    text-decoration: none;
    transition: color 0.2s ease;
}

.footer-links a:hover {
    color: var(--accent-primary);
}

.footer-version {
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    background: rgba(0, 212, 255, 0.1);
    border-radius: 12px;
    border: 1px solid rgba(0, 212, 255, 0.2);
}

/* Responsive Breakpoints */
@media (max-width: 768px) {
    .header-content,
    .footer-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .header-nav {
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .footer-links {
        flex-direction: column;
        gap: 0.75rem;
    }
}
```

### Mobile-First Responsive Design

**Base:** 375px (mobile)
- Single column layouts
- Stacked navigation
- Touch-friendly 44px minimum tap targets

**Tablet:** 768px breakpoint
- 2-column grids for multi-panels
- Horizontal navigation
- Expanded spacing

**Desktop:** 1440px breakpoint
- 2-column grids with wider gaps
- Full navigation with icons
- Maximum content width: 1400px

**Implementation Rule:**
```css
/* Mobile-first approach */
.component {
    /* Mobile styles (default) */
}

@media (min-width: 768px) {
    .component {
        /* Tablet enhancements */
    }
}

@media (min-width: 1440px) {
    .component {
        /* Desktop enhancements */
    }
}
```

---

## 📐 Spacing System (v4.0.1)

### ⚠️ CRITICAL: Proper Spacing for Stacked Elements

**Issue:** Cards/panels stacking without adequate vertical spacing creates cramped, unprofessional layouts.

**Solution:** Enforce minimum spacing requirements using CSS variables and layout utilities.

### Spacing Variables

```css
:root {
    /* Core spacing scale */
    --space-xs: 0.25rem;   /* 4px - Tiny gaps */
    --space-sm: 0.5rem;    /* 8px - Small gaps */
    --space-md: 1rem;      /* 16px - Medium gaps */
    --space-lg: 1.5rem;    /* 24px - Large gaps (DEFAULT for stacked cards) */
    --space-xl: 2rem;      /* 32px - Extra large gaps */
    --space-2xl: 3rem;     /* 48px - Section spacing */
    --space-3xl: 4rem;     /* 64px - Major section spacing */
}
```

### Stacked Element Rules

**Minimum Requirements:**
- **Cards/Panels:** `margin-bottom: var(--space-lg)` (1.5rem / 24px)
- **Category Sections:** `margin-bottom: var(--space-2xl)` (3rem / 48px)
- **Multi-Panel Grids:** `gap: var(--space-lg)` (1.5rem / 24px)
- **Grid Rows:** `row-gap: var(--space-lg)` minimum

### Grid Layout Spacing

```css
/* Multi-panel grids (Security, Orchestrators, STS) */
.category-panels-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-lg);  /* 24px gaps between all panels */
    margin-bottom: var(--space-2xl);
}

/* 2x2 Grid (4 panels - Security) */
.category-panels-grid:not(.grid-3x2) {
    grid-template-columns: repeat(2, 1fr);
    row-gap: var(--space-lg);
    column-gap: var(--space-lg);
}

/* 3x2 Grid (6 panels - STS) */
.category-panels-grid.grid-3x2 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, auto);
    row-gap: var(--space-lg);  /* CRITICAL: Prevents cramped rows */
    column-gap: var(--space-lg);
}

/* 2x3 Grid (5 panels - Orchestrators) */
.category-panels-grid.grid-2x3 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, auto);
    row-gap: var(--space-lg);
    column-gap: var(--space-lg);
}
```

### Stacked Card Layouts

```css
/* Card stacking (Level 1 & 2 pages) */
.glass-card + .glass-card {
    margin-top: var(--space-lg);  /* 24px between consecutive cards */
}

/* Section spacing */
.content-section {
    margin-bottom: var(--space-2xl);  /* 48px between major sections */
}

/* Key features sections (Security, Orchestrators, STS panels) */
.key-features-section {
    margin-bottom: var(--space-3xl);  /* 64px between major panel sections */
}

/* Main panel wrappers */
.main-panel-wrapper {
    margin-bottom: var(--space-2xl);  /* 48px after each panel */
}

/* Subpanels within multi-panels */
.category-subpanel {
    padding: var(--space-lg);  /* Internal padding */
    /* Spacing handled by parent grid gap */
}
```

### Responsive Spacing

```css
/* Mobile: Tighter spacing for smaller screens */
@media (max-width: 767px) {
    .category-panels-grid {
        grid-template-columns: 1fr;  /* Single column */
        gap: var(--space-md);  /* 16px on mobile */
    }
    
    .glass-card + .glass-card {
        margin-top: var(--space-md);
    }
}

/* Tablet & Desktop: Full spacing */
@media (min-width: 768px) {
    .category-panels-grid {
        gap: var(--space-lg);  /* 24px on larger screens */
    }
}
```

### Common Mistakes to Avoid

❌ **WRONG:**
```css
/* No spacing between stacked elements */
.glass-card {
    margin-bottom: 0;
}

/* Cramped grid rows */
.grid {
    row-gap: 8px;  /* Too tight! */
}
```

✅ **CORRECT:**
```css
/* Adequate spacing */
.glass-card {
    margin-bottom: var(--space-lg);
}

/* Comfortable grid spacing */
.grid {
    gap: var(--space-lg);  /* 24px all around */
}
```

### Validation Checklist

Before marking any phase complete, validate spacing:

- [ ] All stacked cards have ≥24px vertical spacing
- [ ] Multi-panel grids use `gap: var(--space-lg)`
- [ ] Grid `row-gap` is explicitly set (not just `gap`)
- [ ] Section spacing is ≥48px between major sections
- [ ] Key features sections have ≥64px bottom margin
- [ ] Main panel wrappers have ≥48px bottom margin
- [ ] Mobile spacing scales down appropriately (≥16px)
- [ ] Visual inspection shows no cramped/touching elements

---

## 🎬 Animation Tier System (v4.0.0 - Universal Standard)

### ⛔ CRITICAL: Subtle Animations by Default

**ALL documentation pages across ALL 9 tiles** use **T1 (Subtle)** animations. Dramatic animations are ONLY for Level 0 (Home page hero).

### Animation Tiers

| Tier | Name | Use Case | Duration | Effects | Scope |
|------|------|----------|----------|---------|-------|
| **T1** | Subtle | ALL Level 1 & Level 2 pages (9 tiles) | 0.2-0.3s | Opacity, light transforms, simple transitions | Universal |
| **T2** | Accent | Interactive elements requiring feedback | 0.1-0.2s | Button press, form focus, selection highlight | UI elements |
| **T3** | Dramatic | ONLY Level 0 (docs/index.html hero) | 2-10s | borderGlowSweep, blobMorph, particle effects | Home only |

### T1: Subtle Animations (DEFAULT)

**✅ REQUIRED for all Level 1, Level 2, and Level 3 pages**

#### Clickable Tiles (Interactive Cards, Buttons, Links)

**Visual Indicators:**
- ✅ Glowing border on hover (subtle accent)
- ✅ `cursor: pointer` (large hand)
- ✅ Slight lift effect (`translateY(-2px)`)
- ❌ NO glass reflections
- ❌ NO infinite animations

```css
/* T1 Clickable Tile - APPROVED */
.glass-card-clickable {
    position: relative;
    cursor: pointer;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.glass-card-clickable:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 
        0 8px 24px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 212, 255, 0.3); /* Subtle glow */
}

/* Large hand pointer */
.glass-card-clickable:hover {
    cursor: pointer;
}
```

#### Non-Clickable Tiles (Display Cards, Info Panels)

**Visual Indicators:**
- ✅ Static glass highlight (top edge glow)
- ✅ `cursor: default` (no pointer)
- ✅ NO lift effect
- ❌ NO glowing borders
- ❌ NO hover glow
- ❌ NO infinite animations (REMOVED in v4.0.0)

```css
/* T1 Non-Clickable Tile - APPROVED */
.glass-card-display {
    position: relative;
    cursor: default;
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow: hidden;
}

/* T1 Subtle: Static glass highlight (NO animation) */
.glass-card-display::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    pointer-events: none;
}

/* NO hover effects on display cards */
.glass-card-display:hover {
    /* No transform, no glow, no border change */
}
```

#### Subtle Focus States (All Interactive Elements)

```css
/* T1 Focus - APPROVED */
.interactive-element:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
    transition: outline-color 0.2s ease;
}

/* T1 Nav Link - APPROVED */
.nav-link {
    cursor: pointer;
    transition: color 0.2s ease, background-color 0.2s ease;
}
```

**T1 Properties Summary:**
- `transition-duration: 0.2s - 0.3s` (fast, responsive)
- **Clickable:** Glow border + lift + pointer cursor
- **Non-Clickable:** Glass reflection (8s) + default cursor
- NO infinite animations on clickable tiles
- NO keyframe animations on clickable cards
- NO glow on non-clickable tiles

### T2: Accent Animations (Interactive Feedback)

**✅ APPROVED for buttons, forms, tabs**

```css
/* T2 Button Feedback - APPROVED */
.btn-glass:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
}

/* T2 Form Focus - APPROVED */
input:focus {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
    transition: all 0.2s ease;
}

/* T2 Tab Selection - APPROVED */
.tab-active {
    border-bottom: 2px solid var(--accent-primary);
    transition: border-color 0.2s ease;
}
```

### T3: Dramatic Animations (RESTRICTED)

**⛔ ONLY ALLOWED ON:**
- `docs/index.html` (Home page hero section)
- Landing page hero sections
- Explicitly marked showcase pages

**❌ FORBIDDEN ON:**
- Level 2 feature pages
- Documentation content pages
- Architecture visualization pages
- Orchestrator detail pages
- Any page with primary content focus

```css
/* T3 Dramatic - HERO SECTIONS ONLY */
@keyframes borderGlowSweep {
    0%, 100% { background-position: -200% 0; }
    50% { background-position: 200% 0; }
}

@keyframes blobMorph {
    0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
    50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
}

@keyframes lightLeakPrimary {
    0% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
    100% { transform: translate(-30%, -30%) scale(1.2); opacity: 0.5; }
}

@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
    50% { box-shadow: 0 0 40px rgba(0, 212, 255, 0.6); }
}
```

### Animation Tier Quick Reference

| Animation | Tier | Allowed Pages |
|-----------|------|---------------|
| `transition: transform 0.2s` | T1 | ✅ All pages |
| `transition: opacity 0.2s` | T1 | ✅ All pages |
| `transform: translateY(-2px)` | T1 | ✅ All pages |
| `transform: scale(0.98)` | T2 | ✅ Buttons only |
| `outline` focus states | T2 | ✅ All interactive elements |
| `borderGlowSweep` | T3 | ⛔ Hero only |
| `blobMorph` | T3 | ⛔ Hero only |
| `lightLeakPrimary` | T3 | ⛔ Hero only |
| `glowPulse` | T3 | ⛔ Hero only |
| Infinite animations | T3 | ⛔ Hero only |
| SVG filter glow effects | T3 | ⛔ Hero only |

### Migration from T3 to T1

When simplifying dramatic animations:

```css
/* ❌ BEFORE (T3 Dramatic) */
.glass-card::after {
    animation: borderGlowSweep 2s ease-in-out infinite;
}

.glass-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(0, 212, 255, 0.5);
}

/* ✅ AFTER (T1 Subtle) */
.glass-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
/* Remove ::after with borderGlowSweep entirely */
```

---

## 🏗️ Pattern Library

### Pattern 1: Multi-Layer Glass Card (PRIMARY)

**Use Case:** Default card pattern for all content containers

**⚠️ LEVEL 1 & LEVEL 2 IMPLEMENTATION (T1 Subtle):**
```css
.glass-card {
    position: relative;
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: var(--space-lg);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

/* T1 Hover: Simple lift + glow (NO animation) */
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 212, 255, 0.15);
    border-color: rgba(0, 212, 255, 0.3);
}

/* NO animated border glow on Level 1/2 pages */
/* NO ::after pseudo-elements with borderGlowSweep animations */
/* NO infinite keyframe animations */
```

**⚠️ LEVEL 0 ONLY (T3 Dramatic - Hero Sections):**
```css
.glass-card-hero {
    /* Layer 1: Frosted background with gradient */
    position: relative;
    background: linear-gradient(
        135deg,
        rgba(26, 31, 58, 0.7) 0%,
        rgba(26, 31, 58, 0.4) 100%
    );
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: var(--space-lg);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Layer 2: Inner glow (light source) */
.glass-card-hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 40%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.15) 0%, transparent 100%);
    border-radius: inherit;
    pointer-events: none;
}

/* Layer 3: Animated border glow (HERO ONLY) */
.glass-card-hero::after {
    content: '';
    position: absolute;
    inset: -2px;
    background: linear-gradient(45deg, transparent 30%, rgba(0, 212, 255, 0.3) 50%, transparent 70%);
    background-size: 200% 200%;
    border-radius: inherit;
    opacity: 0;
    z-index: -1;
}

.glass-card-hero:hover::after {
    opacity: 1;
    animation: borderGlowSweep 2s ease-in-out infinite;
}

@keyframes borderGlowSweep {
    0%, 100% { background-position: -200% 0; }
    50% { background-position: 200% 0; }
}
```

**HTML Structure:**
```html
<div class="glass-card">
    <h2>Card Title</h2>
    <p>Content goes here...</p>
</div>
```

**Variables Used:**
- `--space-lg`: 1.5rem (24px) - DEFAULT for stacked cards/grids
- `--accent-primary`: #00d4ff (cyan)

---

### Pattern 2: Neuglass Card (Neumorphism + Glass)

**Use Case:** Dashboard widgets, settings panels, interactive controls

**Implementation:**
```css
.neuglass-card {
    background: linear-gradient(
        145deg,
        rgba(26, 31, 58, 0.8) 0%,
        rgba(16, 20, 40, 0.9) 100%
    );
    backdrop-filter: blur(15px) saturate(150%);
    border-radius: 24px;
    padding: var(--space-lg);
    
    /* Soft neumorphic shadows */
    box-shadow: 
        12px 12px 24px rgba(0, 0, 0, 0.6),
        -12px -12px 24px rgba(255, 255, 255, 0.05),
        inset 2px 2px 4px rgba(255, 255, 255, 0.1),
        inset -2px -2px 4px rgba(0, 0, 0, 0.3);
    
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
}

.neuglass-card:hover {
    box-shadow: 
        6px 6px 12px rgba(0, 0, 0, 0.7),
        -6px -6px 12px rgba(255, 255, 255, 0.03),
        inset 4px 4px 8px rgba(0, 0, 0, 0.4),
        inset -2px -2px 4px rgba(255, 255, 255, 0.1);
    transform: translateY(2px);
}
```

---

### Pattern 3: Morphing Glass Card

**Use Case:** Expandable content, detail views, interactive showcases

**Implementation:**
```css
.morph-card {
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: var(--space-lg);
    cursor: pointer;
    transition: 
        border-radius 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55),
        transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55),
        box-shadow 0.6s ease;
}

.morph-card:hover {
    border-radius: 50px;
    transform: scale(1.05);
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 40px rgba(0, 212, 255, 0.3);
}

.morph-card.expanded {
    position: fixed;
    inset: 20px;
    border-radius: 0;
    transform: scale(1);
    z-index: 9999;
    animation: morphToFullscreen 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes morphToFullscreen {
    0% {
        border-radius: 50px;
        transform: scale(1.05);
    }
    100% {
        border-radius: 0;
        transform: scale(1);
    }
}
```

**JavaScript Toggle:**
```javascript
document.querySelectorAll('.morph-card').forEach(card => {
    card.addEventListener('click', () => {
        card.classList.toggle('expanded');
    });
});
```

---

### Pattern 4: Light Leak Glass

**Use Case:** Hero sections, feature highlights, ambient backgrounds

**Implementation:**
```css
.light-leak-glass {
    position: relative;
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(15px);
    overflow: hidden;
    border-radius: 16px;
    padding: var(--space-xl);
}

/* Light source top-left (cyan) */
.light-leak-glass::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
        circle at 30% 30%,
        rgba(0, 212, 255, 0.3) 0%,
        transparent 50%
    );
    pointer-events: none;
    mix-blend-mode: overlay;
    animation: lightLeakPrimary 8s ease-in-out infinite alternate;
}

@keyframes lightLeakPrimary {
    0% {
        transform: translate(0, 0);
        opacity: 0.5;
    }
    100% {
        transform: translate(10%, 10%);
        opacity: 0.8;
    }
}

/* Light source bottom-right (purple) */
.light-leak-glass::after {
    content: '';
    position: absolute;
    bottom: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
        circle at 70% 70%,
        rgba(123, 97, 255, 0.2) 0%,
        transparent 50%
    );
    pointer-events: none;
    mix-blend-mode: overlay;
    animation: lightLeakSecondary 8s ease-in-out infinite alternate-reverse;
}

@keyframes lightLeakSecondary {
    0% {
        transform: translate(0, 0);
        opacity: 0.4;
    }
    100% {
        transform: translate(-10%, -10%);
        opacity: 0.7;
    }
}
```

---

### Pattern 5: Liquid Blob Glass

**Use Case:** Decorative elements, hero backgrounds, feature showcases

**Implementation:**
```css
.liquid-blob {
    background: linear-gradient(
        135deg,
        rgba(0, 212, 255, 0.3) 0%,
        rgba(123, 97, 255, 0.3) 100%
    );
    backdrop-filter: blur(40px) saturate(200%);
    border-radius: 40% 60% 60% 40% / 60% 40% 60% 40%;
    padding: 3rem;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.4),
        inset 0 0 40px rgba(255, 255, 255, 0.1);
    animation: blobMorph 10s ease-in-out infinite;
    will-change: border-radius;
}

@keyframes blobMorph {
    0%, 100% {
        border-radius: 40% 60% 60% 40% / 60% 40% 60% 40%;
    }
    25% {
        border-radius: 60% 40% 40% 60% / 40% 60% 40% 60%;
    }
    50% {
        border-radius: 50% 50% 50% 50% / 50% 50% 50% 50%;
    }
    75% {
        border-radius: 40% 60% 40% 60% / 60% 40% 60% 40%;
    }
}

.liquid-blob:hover {
    border-radius: 30% 70% 70% 30% / 70% 30% 70% 30%;
    animation-play-state: paused;
}
```

---

## 🎨 UI Component Patterns

### Modal/Dialog
```css
.glass-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(10, 14, 39, 0.8);
    backdrop-filter: blur(20px) saturate(180%);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease;
}

.glass-modal {
    background: rgba(26, 31, 58, 0.9);
    backdrop-filter: blur(30px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 3rem;
    max-width: 600px;
    width: 90%;
    box-shadow: 
        0 30px 80px rgba(0, 0, 0, 0.6),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    animation: modalSlideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalSlideUp {
    from {
        opacity: 0;
        transform: translateY(50px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}
```

### Toast Notification
```css
.glass-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(26, 31, 58, 0.95);
    backdrop-filter: blur(20px);
    border-left: 4px solid var(--accent-primary);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    animation: toastSlideIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    z-index: 10000;
}

@keyframes toastSlideIn {
    from {
        transform: translateX(400px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Auto-dismiss after 5s */
.glass-toast.dismissing {
    animation: toastSlideOut 0.3s ease forwards;
}

@keyframes toastSlideOut {
    to {
        transform: translateX(400px);
        opacity: 0;
    }
}
```

### Sidebar/Drawer
```css
.glass-drawer {
    position: fixed;
    top: 0;
    right: 0;
    width: 400px;
    height: 100vh;
    background: rgba(26, 31, 58, 0.85);
    backdrop-filter: blur(30px) saturate(200%);
    border-left: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: -10px 0 40px rgba(0, 0, 0, 0.5);
    transform: translateX(100%);
    transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    z-index: 9998;
    overflow-y: auto;
}

.glass-drawer.open {
    transform: translateX(0);
}
```

### Dropdown/Select
```css
.glass-dropdown {
    position: absolute;
    top: calc(100% + 0.5rem);
    left: 0;
    width: 100%;
    background: rgba(26, 31, 58, 0.95);
    backdrop-filter: blur(25px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    max-height: 300px;
    overflow-y: auto;
    animation: dropdownFadeIn 0.2s ease;
    z-index: 1000;
}

@keyframes dropdownFadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.glass-dropdown-item {
    padding: 0.75rem 1rem;
    transition: background 0.2s ease;
    cursor: pointer;
}

.glass-dropdown-item:hover {
    background: rgba(0, 212, 255, 0.15);
}

.glass-dropdown-item:active {
    background: rgba(0, 212, 255, 0.25);
}
```

### Enhanced Tooltip
```css
.glass-tooltip {
    position: absolute;
    background: rgba(0, 0, 0, 0.95);
    backdrop-filter: blur(15px);
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.875rem;
    border: 1px solid rgba(0, 212, 255, 0.3);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
    pointer-events: none;
    opacity: 0;
    transform: translateY(-5px);
    transition: all 0.2s ease;
    z-index: 10001;
    white-space: nowrap;
}

.glass-tooltip::after {
    content: '';
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid rgba(0, 212, 255, 0.3);
}

[data-tooltip]:hover .glass-tooltip {
    opacity: 1;
    transform: translateY(0);
}
```

---

## 🎨 Tile-Specific Patterns (v4.0.0)

### Pattern 8: Architecture Component Cards

**Use Cases:** SKULL Protection layers, Knowledge Graph nodes, Brain Tiers, Development Context modules

**⚠️ T1 SUBTLE ANIMATIONS ONLY (Level 1 & Level 2 pages)**

**HTML Structure:**
```html
<div class="glass-card architecture-component">
    <div class="component-header">
        <i class="fas fa-brain"></i>
        <h3>SKULL Protection Layer 1</h3>
        <span class="badge">118 Rules</span>
    </div>
    <div class="component-body">
        <p>Protection layer description...</p>
    </div>
    <div class="component-footer">
        <button class="btn-glass">View Details</button>
    </div>
</div>
```

**CSS (T1 Subtle - NO infinite animations):**
```css
.architecture-component {
    border-left: 4px solid var(--accent-primary);
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(20px);
    cursor: pointer;
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

/* T1 Clickable: Simple glow on hover (NO animation) */
.architecture-component:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 
                0 0 40px rgba(0, 212, 255, 0.15);
    border-color: rgba(0, 212, 255, 0.5);
    cursor: pointer;
}

.architecture-component .component-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.architecture-component .badge {
    background: rgba(0, 212, 255, 0.2);
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    margin-left: auto;
}
```

**D3.js Integration:**
- **SKULL Protection:** Concentric rings (15 layers)
- **Knowledge Graph:** Force-directed graph (54 nodes)
- **Brain Tiers:** Sankey diagram (Tier 0→1→2→3)
- **Dev Context:** Hierarchical tree

### Pattern 9: Orchestrator Workflow Cards

**Use Cases:** 17 orchestrator detail pages (TDD, Planning, Debug, ADO, Cleanup, Refinement, etc.)

**HTML Structure:**
```html
<div class="glass-card orchestrator-workflow">
    <div class="workflow-phase-indicator">
        <span class="phase active">1</span>
        <span class="phase-connector"></span>
        <span class="phase">2</span>
        <span class="phase-connector"></span>
        <span class="phase">3</span>
    </div>
    <h3>TDD Orchestrator: RED Phase</h3>
    <p>Write failing test first...</p>
    <div class="workflow-actions">
        <button class="btn-glass">Next Phase</button>
    </div>
</div>
```

**CSS:**
```css
.orchestrator-workflow .workflow-phase-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-xl);
}

.orchestrator-workflow .phase {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.2);
    font-weight: 700;
}

.orchestrator-workflow {
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.orchestrator-workflow:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 8px 24px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 212, 255, 0.3);
    cursor: pointer;
}

.orchestrator-workflow .phase.active {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}

.orchestrator-workflow .phase-connector {
    width: 24px;
    height: 2px;
    background: rgba(255, 255, 255, 0.2);
}
```

**Mermaid Diagrams:** Each orchestrator uses specific diagram type (see Phase 5 in plan)

### Pattern 10: STS Category Grid

**Use Cases:** Sharpen The Saw 6 categories (Code Quality, SOLID, Testing, Performance, Security, Documentation)

**HTML Structure:**
```html
<div class="sts-category-grid">
    <div class="glass-card sts-category">
        <i class="fas fa-code-quality fa-3x"></i>
        <h3>Code Quality</h3>
        <p class="metric-value">92%</p>
        <p class="metric-label">Compliance</p>
        <a href="code-quality.html" class="btn-glass">Explore</a>
    </div>
    <!-- Repeat for 6 categories -->
</div>
```

**CSS:**
```css
.sts-category-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-xl);
    margin: var(--spacing-2xl) 0;
}

.sts-category {
    text-align: center;
    padding: var(--spacing-2xl);
    cursor: pointer;
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.sts-category:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 
        0 8px 24px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 212, 255, 0.3);
    cursor: pointer;
}

.sts-category i {
    color: var(--accent-primary);
    margin-bottom: var(--spacing-lg);
    opacity: 0.8;
}

.sts-category .metric-value {
    font-size: var(--font-3xl);
    font-weight: 800;
    color: var(--accent-primary);
    margin: var(--spacing-md) 0;
}
```

**D3.js Visuals:**
- **Code Quality:** Radar chart (6 dimensions)
- **SOLID:** Force-directed graph (5 principles)
- **Testing:** Bar chart (coverage %)
- **Performance:** Line chart (latency)
- **Security:** Treemap (vulnerabilities)
- **Documentation:** Bar chart (doc coverage)

### Pattern 11: Best Practices Guideline Cards

**Use Cases:** 35 guidelines organized into 3 Level 2 pages

**HTML Structure:**
```html
<div class="glass-card guideline-card">
    <div class="guideline-number">23</div>
    <h4>Always Use Type Hints</h4>
    <p class="guideline-category">Code Quality</p>
    <div class="guideline-content">
        <p>Type hints improve code readability...</p>
        <pre><code class="language-python">
def calculate(x: int, y: int) -> int:
    return x + y
        </code></pre>
    </div>
    <div class="guideline-footer">
        <span class="badge">Recommended</span>
    </div>
</div>
```

**CSS:**
```css
.guideline-card {
    position: relative;
    padding-left: calc(var(--spacing-xl) + 40px);
    cursor: default;
    overflow: hidden;
}

/* Glass reflection (non-clickable display) */
.guideline-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        135deg,
        transparent 0%,
        rgba(255, 255, 255, 0.03) 45%,
        rgba(255, 255, 255, 0.08) 50%,
        rgba(255, 255, 255, 0.03) 55%,
        transparent 100%
    );
    animation: glassReflection 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

.guideline-card > * {
    position: relative;
    z-index: 1;
}

.guideline-card .guideline-number {
    position: absolute;
    top: var(--spacing-xl);
    left: var(--spacing-xl);
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 212, 255, 0.2);
    border: 2px solid var(--accent-primary);
    border-radius: 50%;
    font-weight: 700;
    font-size: 1.125rem;
}

.guideline-card .guideline-category {
    font-size: 0.875rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--spacing-md);
}

.guideline-card pre {
    background: rgba(0, 0, 0, 0.3);
    padding: var(--spacing-md);
    border-radius: 8px;
    overflow-x: auto;
    margin: var(--spacing-md) 0;
}
```

**Visual Organization:** Accordion or tabbed interface with expandable sections

### Pattern 12: Toolkit Tool Cards

**Use Cases:** Tool Discovery, Tool Orchestration, Tool Integration pages

**HTML Structure:**
```html
<div class="glass-card toolkit-tool">
    <div class="tool-header">
        <i class="fas fa-wrench"></i>
        <h3>Semantic Search Tool</h3>
        <span class="tool-status active">ACTIVE</span>
    </div>
    <div class="tool-capabilities">
        <span class="capability-badge">Code Analysis</span>
        <span class="capability-badge">Pattern Detection</span>
        <span class="capability-badge">Context Retrieval</span>
    </div>
    <div class="tool-description">
        <p>Searches codebase using natural language queries...</p>
    </div>
    <div class="tool-stats">
        <div class="stat">
            <span class="stat-value">1,234</span>
            <span class="stat-label">Searches</span>
        </div>
        <div class="stat">
            <span class="stat-value">98%</span>
            <span class="stat-label">Accuracy</span>
        </div>
    </div>
</div>
```

**CSS:**
```css
.toolkit-tool {
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.toolkit-tool:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 8px 24px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 212, 255, 0.3);
    cursor: pointer;
}

.toolkit-tool .tool-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.toolkit-tool .tool-status {
    margin-left: auto;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.toolkit-tool .tool-status.active {
    background: rgba(0, 255, 127, 0.2);
    color: #00ff7f;
    border: 1px solid #00ff7f;
}

.toolkit-tool .tool-capabilities {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
}

.toolkit-tool .capability-badge {
    background: rgba(255, 255, 255, 0.1);
    padding: 0.25rem 0.5rem;
    border-radius: 8px;
    font-size: 0.75rem;
}

.toolkit-tool .tool-stats {
    display: flex;
    gap: var(--spacing-xl);
    margin-top: var(--spacing-lg);
    padding-top: var(--spacing-lg);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.toolkit-tool .stat {
    text-align: center;
}

.toolkit-tool .stat-value {
    display: block;
    font-size: var(--font-2xl);
    font-weight: 700;
    color: var(--accent-primary);
}

.toolkit-tool .stat-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
}
```

**D3.js Visuals:**
- **Tool Discovery:** Treemap (tool categories)
- **Tool Orchestration:** Sankey diagram (tool chain)
- **Tool Integration:** Force-directed graph (dependencies)

### Pattern 13: LENS Analysis Cards

**Use Cases:** AST Analysis, Reverse Engineering, Code Intelligence pages

**HTML Structure:**
```html
<div class="glass-card lens-analysis">
    <div class="analysis-header">
        <i class="fas fa-search-code"></i>
        <h3>Function Complexity Analysis</h3>
    </div>
    <div class="code-preview">
        <pre><code class="language-python">
def complex_function(data, config):
    # Analyzed code...
    pass
        </code></pre>
    </div>
    <div class="analysis-results">
        <div class="metric">
            <span class="metric-label">Cyclomatic Complexity</span>
            <span class="metric-value warning">12</span>
        </div>
        <div class="metric">
            <span class="metric-label">Lines of Code</span>
            <span class="metric-value">45</span>
        </div>
        <div class="metric">
            <span class="metric-label">Dependencies</span>
            <span class="metric-value">8</span>
        </div>
    </div>
    <div class="analysis-insights">
        <p><i class="fas fa-lightbulb"></i> Consider extracting helper functions to reduce complexity.</p>
    </div>
</div>
```

**CSS:**
```css
.lens-analysis {
    cursor: default;
    overflow: hidden;
}

/* Glass reflection (non-clickable display) */
.lens-analysis::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        135deg,
        transparent 0%,
        rgba(255, 255, 255, 0.03) 45%,
        rgba(255, 255, 255, 0.08) 50%,
        rgba(255, 255, 255, 0.03) 55%,
        transparent 100%
    );
    animation: glassReflection 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

.lens-analysis > * {
    position: relative;
    z-index: 1;
}

.lens-analysis .code-preview {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 8px;
    padding: var(--spacing-md);
    margin: var(--spacing-lg) 0;
    max-height: 300px;
    overflow-y: auto;
}

.lens-analysis .analysis-results {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-lg);
    margin: var(--spacing-lg) 0;
}

.lens-analysis .metric {
    flex: 1;
    min-width: 120px;
    text-align: center;
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.lens-analysis .metric-value {
    display: block;
    font-size: var(--font-2xl);
    font-weight: 700;
    margin-top: var(--spacing-xs);
}

.lens-analysis .metric-value.warning {
    color: #ffa500;
}

.lens-analysis .analysis-insights {
    background: rgba(0, 212, 255, 0.1);
    border-left: 4px solid var(--accent-primary);
    padding: var(--spacing-md);
    border-radius: 8px;
    margin-top: var(--spacing-lg);
}

.lens-analysis .analysis-insights i {
    color: var(--accent-primary);
    margin-right: var(--spacing-xs);
}
```

**D3.js Visuals:**
- **AST Analysis:** Hierarchical tree diagram
- **Reverse Engineering:** Force-directed graph (modules)
- **Code Intelligence:** Heatmap (file complexity)

### Pattern 14: Get Started Step Cards

**Use Cases:** Installation, Configuration, First Steps pages

**HTML Structure:**
```html
<div class="glass-card step-card">
    <div class="step-number">1</div>
    <h3>Install CORTEX</h3>
    <p>Run the following command to install CORTEX:</p>
    <div class="code-block">
        <button class="copy-btn" aria-label="Copy code">
            <i class="fas fa-copy"></i>
        </button>
        <pre><code class="language-bash">pip install cortex-ai</code></pre>
    </div>
    <div class="step-footer">
        <p class="time-estimate"><i class="far fa-clock"></i> ~2 minutes</p>
    </div>
</div>
```

**CSS:**
```css
.step-card {
    position: relative;
    padding-top: calc(var(--spacing-xl) + 50px);
    cursor: default;
    overflow: hidden;
}

/* Glass reflection (non-clickable display) */
.step-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        135deg,
        transparent 0%,
        rgba(255, 255, 255, 0.03) 45%,
        rgba(255, 255, 255, 0.08) 50%,
        rgba(255, 255, 255, 0.03) 55%,
        transparent 100%
    );
    animation: glassReflection 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

.step-card > * {
    position: relative;
    z-index: 1;
}

.step-card .step-number {
    position: absolute;
    top: var(--spacing-xl);
    left: var(--spacing-xl);
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
    border-radius: 50%;
    font-size: 1.5rem;
    font-weight: 800;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
}

.step-card .code-block {
    position: relative;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 8px;
    padding: var(--spacing-md);
    margin: var(--spacing-lg) 0;
}

.step-card .copy-btn {
    position: absolute;
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.1);
    border: none;
    padding: 0.5rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.step-card .copy-btn:hover {
    background: rgba(0, 212, 255, 0.3);
}

.step-card .time-estimate {
    color: var(--text-muted);
    font-size: 0.875rem;
    margin-top: var(--spacing-md);
}

.step-card .time-estimate i {
    margin-right: var(--spacing-xs);
}
```

**Visual Elements:** Step-by-step numbered cards with copy-to-clipboard functionality

---

### Pattern 15: Level 0 Multi-Panel System (Security, Orchestrators, STS)

**Use Cases:** Home page tiles with many Level 2 pages requiring categorization
- **Security:** 13 pages/4 categories
- **Orchestrators:** 19 pages/5 categories
- **Sharpen The Saw:** 6 pages/6 categories

**Design Philosophy:**
- **Progressive Disclosure**: Show categories first, then links within categories
- **Visual Hierarchy**: Main panel → Category sub-panels → Links (Tetris grid for multi-tag, full-width for single-tag)
- **Non-Clickable Containers**: Sub-panels are display only, links within are clickable
- **Glassmorphism**: Layered glass effects with gradients and shadows
- **Intelligent Layout**: Adaptive grid based on panel count and tag density

**Grid Layout Intelligence (v4.0.1):**

| Subpanels | Grid Layout | CSS Class | Tag Layout | Use Case |
|-----------|-------------|-----------|------------|----------|
| 4 | 2x2 | (default) | Tetris/masonry | Security pattern |
| 5 | 2x3 (1 odd) | (default) | Tetris/masonry | Orchestrators pattern |
| 6 | 3x2 | `.grid-3x2` | Single full-width | STS pattern |

**Single-Tag Subpanel Styling:**
- Add `.single-tag` class to subpanels with only 1 link
- More compact sizing: `min-height: 280px` (vs 380px for multi-tag)
- Smaller icons: 60x60px (vs 70x70px)
- Full-width link (no Tetris grid needed)

**HTML Structure:**

**Example 1: Security Panel (4 subpanels, multi-tag, 2x2 grid):**
```html
<section class="key-features-section" id="security-panel">
    <div class="main-panel-wrapper">
        <div class="panel-header-centered">
            <h2 class="panel-title-main">
                <span>🛡️</span>
                <span>SECURITY</span>
            </h2>
            <p class="panel-subtitle-main">Comprehensive threat modeling, compliance standards, and security assessments</p>
        </div>

        <div class="category-panels-grid">
            <!-- Protection Category (multi-tag) -->
            <div class="category-subpanel">
                <div class="category-icon-wrapper">
                    <span class="category-icon">🔒</span>
                </div>
                <h3 class="category-title">Protection</h3>
                <p class="category-description">Role-based access control, data encryption, privacy safeguards, and comprehensive activity tracking.</p>
                <div class="category-tags">
                    <a href="security/access-control.html" class="category-tag">
                        <span>Access Control</span>
                    </a>
                    <a href="security/data-protection.html" class="category-tag">
                        <span>Data Protection</span>
                    </a>
                    <a href="security/audit-logging.html" class="category-tag">
                        <span>Audit Logging</span>
                    </a>
                </div>
            </div>
            <!-- Repeat for Assessment, Compliance, Response categories -->
        </div>
    </div>
</section>
```

**Example 2: STS Panel (6 subpanels, single-tag, 3x2 grid):**
```html
<section class="key-features-section" id="sts-panel">
    <div class="main-panel-wrapper">
        <div class="panel-header-centered">
            <h2 class="panel-title-main">
                <span>🔧</span>
                <span>SHARPEN THE SAW</span>
            </h2>
            <p class="panel-subtitle-main">Continuous improvement through security, SOLID principles, and quality standards</p>
        </div>

        <!-- 3x2 Grid with single-tag subpanels -->
        <div class="category-panels-grid grid-3x2">
            <div class="category-subpanel single-tag">
                <div class="category-icon-wrapper">
                    <span class="category-icon">🛡️</span>
                </div>
                <h3 class="category-title">Security</h3>
                <p class="category-description">Security-first development practices, threat modeling integration, and defensive coding patterns.</p>
                <div class="category-tags">
                    <a href="sts/security.html" class="category-tag">
                        <span>Security Best Practices</span>
                    </a>
                </div>
            </div>
            <!-- Repeat for SOLID, Code Quality, Performance, Testing, Documentation -->
        </div>
    </div>
</section>
```

**CSS (defined in `docs/index.html` or external stylesheet):**
```css
/* Main panel wrapper */
.main-panel-wrapper {
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(0, 212, 255, 0.10));
    border: 1px solid rgba(123, 97, 255, 0.4);
    border-radius: 16px;
    padding: 2.5rem;
    backdrop-filter: blur(10px);
}

/* Category panels grid - Intelligent layout */
.category-panels-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}

@media (min-width: 768px) {
    /* Default: 2x2 grid for 4-5 panels */
    .category-panels-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    /* 3x2 grid for 6 panels (STS pattern) */
    .category-panels-grid.grid-3x2 {
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(3, 1fr);
    }
}

/* Category sub-panel (non-clickable) */
.category-subpanel {
    background: linear-gradient(135deg, rgba(10, 14, 39, 0.8), rgba(26, 31, 58, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 2rem 1.5rem;
    cursor: default; /* Non-clickable */
    min-height: 380px;
}

/* Single-tag subpanels: More compact */
.category-subpanel.single-tag {
    min-height: 280px;
    padding: 1.5rem 1.25rem;
}

.category-subpanel.single-tag .category-icon-wrapper {
    width: 60px;
    height: 60px;
    font-size: 2rem;
}

.category-subpanel.single-tag .category-tag {
    grid-column: span 3; /* Full width */
    font-size: 0.95rem;
    padding: 0.75rem 1rem;
}

/* Tetris/masonry grid for category tags */
.category-tags {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 60px;
    gap: 0.75rem;
}

/* Individual tag (clickable link) */
.category-tag {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(123, 97, 255, 0.15));
    border: 1px solid rgba(0, 212, 255, 0.35);
    cursor: pointer;
    transition: all 0.3s ease;
}

.category-tag:hover {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 97, 255, 0.25));
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}
```

/* 🎨 COLOR VARIATIONS (Complementary Palette) */
/* Randomized distribution across panels for visual variety */

/* Cyan - Default base color */
.level0-category-tag {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(123, 97, 255, 0.15));
    border-color: rgba(0, 212, 255, 0.35);
    color: rgba(0, 212, 255, 0.95);
}
.level0-category-tag:hover {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 97, 255, 0.25));
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}

/* Purple - Secondary accent */
.level0-category-tag.tag-purple {
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}
.level0-category-tag.tag-purple:hover {
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.3), rgba(186, 85, 211, 0.25));
    border-color: rgba(123, 97, 255, 0.6);
    box-shadow: 0 6px 20px rgba(123, 97, 255, 0.4);
}

/* Teal - Tertiary accent */
.level0-category-tag.tag-teal {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}
.level0-category-tag.tag-teal:hover {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.3), rgba(0, 212, 255, 0.25));
    border-color: rgba(20, 184, 166, 0.6);
    box-shadow: 0 6px 20px rgba(20, 184, 166, 0.4);
}

/* 🎲 RANDOMIZED COLOR DISTRIBUTION (Anti-Monotony Pattern) */
/* Apply colors pseudo-randomly across categories to avoid predictable patterns */
/* Example for 4-category panel (Security): */

/* Protection category - Mixed colors */
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(1) { /* Cyan */ }
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(2) { 
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(3) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}

/* Assessment category - Different mix */
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(1) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(2) { 
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(3) { /* Cyan */ }
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(4) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}

/* Compliance category - Another mix */
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(1) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(2) { /* Cyan */ }
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(3) { 
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}

/* Response category - Final mix */
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(1) { /* Cyan */ }
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(2) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(3) { 
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}

/* Apply hover states to randomized colors */
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(1):hover,
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(3):hover,
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(2):hover,
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(1):hover {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 97, 255, 0.25));
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}

.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(2):hover,
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(2):hover,
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(3):hover,
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(3):hover {
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.3), rgba(186, 85, 211, 0.25));
    border-color: rgba(123, 97, 255, 0.6);
    box-shadow: 0 6px 20px rgba(123, 97, 255, 0.4);
}

.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(3):hover,
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(1):hover,
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(4):hover,
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(1):hover,
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(2):hover {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.3), rgba(0, 212, 255, 0.25));
    border-color: rgba(20, 184, 166, 0.6);
    box-shadow: 0 6px 20px rgba(20, 184, 166, 0.4);
}

/* Tetris layout patterns (see glassmorphism.css for full specs) */
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(1) { 
    grid-column: span 1; grid-row: span 3; font-size: 1.2rem; 
}
/* ... additional patterns for dynamic sizing */
```

**Key Features:**
- **2-column grid** on desktop (768px+), **1-column** on mobile
- **Tetris/masonry layout** within each category for visual interest
- **Dynamic font sizing** based on tag importance (1rem - 1.2rem)
- **Shimmer hover effect** on tags (light sweep animation)
- **Glassmorphism layers**: Main panel → Sub-panels → Tags (3 depth levels)
- **🎨 Color Variations**: Apply `.tag-purple`, `.tag-teal`, `.tag-indigo`, or `.tag-pink` to create visual variety while maintaining the blue glassmorphism theme

**Color Variation Usage (Anti-Monotony Pattern):**

**🎲 Randomized Distribution:** Instead of applying sequential color patterns (1st=cyan, 2nd=purple, 3rd=teal), distribute colors pseudo-randomly across categories to avoid visual monotony.

**Implementation Strategy:**
```css
/* BAD: Sequential pattern - looks monotonous */
.level0-category-tag:nth-child(3n+1) { color: cyan; }
.level0-category-tag:nth-child(3n+2) { color: purple; }
.level0-category-tag:nth-child(3n+3) { color: teal; }

/* GOOD: Randomized pattern - visual variety */
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(1) { color: cyan; }
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(2) { color: purple; }
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(3) { color: teal; }
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(1) { color: teal; }
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(2) { color: purple; }
/* ... randomized across panels */
```

**Color Palette (7-color system):**
- **Cyan**: `rgba(0, 212, 255)` - Primary accent, complements blue theme
- **Purple**: `rgba(123, 97, 255) → rgba(186, 85, 211)` - Warmth accent
- **Teal**: `rgba(20, 184, 166)` - Bridge accent  
- **Indigo**: `rgba(79, 70, 229) → rgba(99, 102, 241)` - Deep accent
- **Pink**: `rgba(236, 72, 153) → rgba(244, 114, 182)` - Vibrant accent
- **Emerald**: `rgba(16, 185, 129) → rgba(52, 211, 153)` - Success accent
- **Amber**: `rgba(245, 158, 11) → rgba(251, 191, 36)` - Energy accent

**Design Rationale:**
- **Anti-Monotony**: Randomized 7-color distribution prevents predictable visual patterns
- **Complementary**: All 7 colors harmonize with blue glassmorphism base theme
- **Accessibility**: Sufficient contrast ratios maintained across all variants (WCAG 2.1 AA)
- **Visual Hierarchy**: Color variety aids visual scanning and tile distinction
- **Extended Palette**: 7 colors provide maximum diversity for large multi-panel sections

**Usage Guidelines:**
1. Use randomized distribution across all multi-panel sections (Security, Orchestrators, STS)
2. Distribute colors pseudo-randomly via nth-of-type/nth-child CSS selectors
3. Aim for balanced distribution (~14% per color across entire panel)
4. Apply to ALL levels (Level 0, Level 1, Level 2) for consistency
5. Available as `.tag-purple`, `.tag-teal`, `.tag-indigo`, `.tag-pink`, `.tag-emerald`, `.tag-amber` modifier classes

```html
<!-- Example: Security Protection category with randomized colors -->
```html
<!-- Example: Security Protection category with randomized colors -->
<div class="level0-category-tags">
    <a href="security/access-control.html" class="level0-category-tag">Access Control</a> <!-- Cyan -->
    <a href="security/data-protection.html" class="level0-category-tag">Data Protection</a> <!-- Purple -->
    <a href="security/audit-logging.html" class="level0-category-tag">Audit Logging</a> <!-- Teal -->
</div>

<!-- Assessment category - Different distribution -->
<div class="level0-category-tags">
    <a href="security/threat-modeling.html" class="level0-category-tag">Threat Modeling</a> <!-- Teal -->
    <a href="security/risk-assessment.html" class="level0-category-tag">Risk Assessment</a> <!-- Purple -->
    <a href="security/vulnerability-assessment.html" class="level0-category-tag">Vulnerability Assessment</a> <!-- Cyan -->
    <a href="security/penetration-testing.html" class="level0-category-tag">Penetration Testing</a> <!-- Teal -->
</div>
```

**Accessibility:**
- Sub-panels use `cursor: default` (non-interactive containers)
- Tags use `cursor: pointer` (clickable links)
- Semantic HTML with proper heading hierarchy
- Keyboard navigation via tab

**Performance:**
- CSS-only animations (GPU-accelerated)
- No JavaScript required
- Responsive with minimal media queries

---

**Visual Elements:** Step-by-step numbered cards with copy-to-clipboard functionality

---

## ✨ Micro-Interactions Library

### Ripple Effect (Click Feedback)
```css
.ripple-glass {
    position: relative;
    overflow: hidden;
}

.ripple-glass::after {
    content: '';
    position: absolute;
    top: var(--ripple-y, 50%);
    left: var(--ripple-x, 50%);
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.4);
    transform: translate(-50%, -50%);
    animation: rippleEffect 0.6s ease-out;
    pointer-events: none;
}

@keyframes rippleEffect {
    0% {
        width: 0;
        height: 0;
        opacity: 1;
    }
    100% {
        width: 300px;
        height: 300px;
        opacity: 0;
    }
}
```

**JavaScript (Optional - for click position):**
```javascript
document.querySelectorAll('.ripple-glass').forEach(el => {
    el.addEventListener('click', (e) => {
        const rect = el.getBoundingClientRect();
        el.style.setProperty('--ripple-x', `${e.clientX - rect.left}px`);
        el.style.setProperty('--ripple-y', `${e.clientY - rect.top}px`);
    });
});
```

### 3D Tilt Effect (Hover)
```css
.tilt-glass {
    transform-style: preserve-3d;
    transition: transform 0.3s ease;
}

.tilt-glass:hover {
    transform: perspective(1000px) rotateX(5deg) rotateY(5deg);
}
```

### Glow Pulse (Focus/Active)
```css
.pulse-glow-glass:focus,
.pulse-glow-glass.active {
    animation: glowPulse 2s ease-in-out infinite;
    outline: none;
}

@keyframes glowPulse {
    0%, 100% {
        box-shadow: 
            0 0 20px rgba(0, 212, 255, 0.3),
            0 0 40px rgba(0, 212, 255, 0.2);
    }
    50% {
        box-shadow: 
            0 0 40px rgba(0, 212, 255, 0.5),
            0 0 80px rgba(0, 212, 255, 0.3);
    }
}
```

### Shimmer Effect (Loading)
```css
.shimmer-glass {
    background: linear-gradient(
        90deg,
        rgba(26, 31, 58, 0.6) 0%,
        rgba(255, 255, 255, 0.1) 50%,
        rgba(26, 31, 58, 0.6) 100%
    );
    background-size: 200% 100%;
    animation: shimmerSlide 2s linear infinite;
}

@keyframes shimmerSlide {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
```

### Magnetic Hover (Cursor Pull)
```css
.magnetic-glass {
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.magnetic-glass:hover {
    transform: scale(1.05);
}
```

---

## 🚀 Performance Optimization

### GPU Acceleration
```css
/* Apply to all glass elements */
.glass-optimized {
    transform: translateZ(0);
    will-change: transform, opacity;
    backface-visibility: hidden;
    perspective: 1000px;
}
```

### Conditional Blur (Device-Aware)
```css
/* Disable blur on low-end devices */
@media (max-width: 768px) and (max-resolution: 1dppx) {
    .glass-card {
        backdrop-filter: none;
        background: rgba(26, 31, 58, 0.95); /* More opaque */
    }
}

/* Enhanced blur on high-DPI displays */
@media (min-resolution: 2dppx) {
    .glass-card {
        backdrop-filter: blur(25px) saturate(200%);
    }
}
```

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
    .glass-card,
    .morph-card,
    .liquid-blob,
    .light-leak-glass::before,
    .light-leak-glass::after {
        animation: none !important;
        transition: none !important;
    }
}
```

### Lazy Animation Loading
```javascript
// Only animate visible elements
const glassObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-glass');
            glassObserver.unobserve(entry.target);
        }
    });
}, { rootMargin: '50px' });

document.querySelectorAll('.glass-card').forEach(card => {
    glassObserver.observe(card);
});
```

---

## 🎨 CSS Variables (Design Tokens)

```css
:root {
    /* Colors */
    --accent-primary: #00d4ff;
    --accent-secondary: #7b61ff;
    --glass-bg: rgba(26, 31, 58, 0.6);
    --glass-border: rgba(255, 255, 255, 0.1);
    
    /* Spacing */
    --space-xs: 0.5rem;   /* 8px */
    --space-sm: 1rem;     /* 16px */
    --space-md: 1.5rem;   /* 24px */
    --space-lg: 2rem;     /* 32px */
    --space-xl: 3rem;     /* 48px */
    
    /* Blur Levels */
    --blur-sm: 10px;
    --blur-md: 20px;
    --blur-lg: 30px;
    
    /* Border Radius */
    --radius-sm: 8px;
    --radius-md: 16px;
    --radius-lg: 24px;
    
    /* Transitions */
    --transition-fast: 0.2s ease;
    --transition-normal: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
@media (min-width: 320px) {
    /* Small mobile */
    .glass-card { padding: var(--space-sm); }
}

@media (min-width: 480px) {
    /* Mobile landscape */
    .glass-card { padding: var(--space-md); }
}

@media (min-width: 768px) {
    /* Tablet */
    .glass-card { padding: var(--space-lg); }
}

@media (min-width: 1024px) {
    /* Desktop */
    .glass-card { padding: var(--space-lg); }
}

@media (min-width: 1440px) {
    /* Large desktop */
    .glass-card { padding: var(--space-xl); }
}
```

---

## 🧪 Testing Checklist

### Visual Testing
- [ ] Blur effect renders correctly (Chrome DevTools → Rendering → Show layer borders)
- [ ] Border gradients display properly
- [ ] Animations run at 60fps (Performance monitor)
- [ ] Hover states trigger smoothly

### Cross-Browser Testing
- [ ] Chrome 90+ (backdrop-filter support)
- [ ] Firefox 88+ (backdrop-filter support)
- [ ] Safari 14+ (webkit-backdrop-filter)
- [ ] Edge 90+ (chromium-based)

### Performance Testing
- [ ] Page load <3s on 3G
- [ ] Animation FPS ≥60
- [ ] GPU memory <50MB
- [ ] No layout thrashing (DevTools → Performance)

### Accessibility Testing
- [ ] Keyboard navigation works (Tab, Enter, Esc)
- [ ] Focus indicators visible
- [ ] Reduced-motion respected
- [ ] Screen reader compatible (ARIA labels)

---

## 🛠️ Implementation Scripts

### Auto-Apply Glass Classes (JavaScript)
```javascript
// Automatically apply glass patterns to elements
class GlassManager {
    constructor() {
        this.applyGlassPatterns();
        this.initInteractions();
    }
    
    applyGlassPatterns() {
        // Auto-detect card containers
        document.querySelectorAll('[data-glass="card"]').forEach(el => {
            el.classList.add('glass-card');
        });
        
        // Auto-detect modals
        document.querySelectorAll('[data-glass="modal"]').forEach(el => {
            el.classList.add('glass-modal');
        });
        
        // Auto-detect tooltips
        document.querySelectorAll('[data-tooltip]').forEach(el => {
            this.createTooltip(el);
        });
    }
    
    initInteractions() {
        // Ripple effect
        document.querySelectorAll('.ripple-glass').forEach(el => {
            el.addEventListener('click', this.createRipple.bind(this));
        });
        
        // Modal triggers
        document.querySelectorAll('[data-modal-trigger]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = e.target.dataset.modalTrigger;
                this.openModal(modalId);
            });
        });
    }
    
    createRipple(e) {
        const el = e.currentTarget;
        const rect = el.getBoundingClientRect();
        el.style.setProperty('--ripple-x', `${e.clientX - rect.left}px`);
        el.style.setProperty('--ripple-y', `${e.clientY - rect.top}px`);
    }
    
    createTooltip(el) {
        const text = el.dataset.tooltip;
        const tooltip = document.createElement('div');
        tooltip.className = 'glass-tooltip';
        tooltip.textContent = text;
        el.style.position = 'relative';
        el.appendChild(tooltip);
    }
    
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('open'), 10);
        }
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('open');
            setTimeout(() => modal.style.display = 'none', 300);
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.glassManager = new GlassManager();
});
```

### Performance Monitor
```javascript
// Monitor glassmorphism performance
class GlassPerformanceMonitor {
    constructor() {
        this.fpsSamples = [];
        this.lastFrame = performance.now();
        this.monitoring = false;
    }
    
    start() {
        this.monitoring = true;
        this.measure();
    }
    
    stop() {
        this.monitoring = false;
        return this.getReport();
    }
    
    measure() {
        if (!this.monitoring) return;
        
        const now = performance.now();
        const delta = now - this.lastFrame;
        const fps = 1000 / delta;
        
        this.fpsSamples.push(fps);
        if (this.fpsSamples.length > 60) {
            this.fpsSamples.shift();
        }
        
        this.lastFrame = now;
        requestAnimationFrame(() => this.measure());
    }
    
    getReport() {
        const avgFps = this.fpsSamples.reduce((a, b) => a + b, 0) / this.fpsSamples.length;
        const minFps = Math.min(...this.fpsSamples);
        const maxFps = Math.max(...this.fpsSamples);
        
        return {
            average: avgFps.toFixed(2),
            min: minFps.toFixed(2),
            max: maxFps.toFixed(2),
            status: avgFps >= 55 ? '✅ GOOD' : '⚠️ NEEDS OPTIMIZATION'
        };
    }
}

// Usage:
// const monitor = new GlassPerformanceMonitor();
// monitor.start();
// ... interact with glass elements ...
// const report = monitor.stop();
// console.log('Glass Performance:', report);
```

---

## 📐 Layout Patterns

### Pattern 6: Metrics Dashboard (Centered Flexbox)

**Use Case:** Hero section KPI cards, statistics displays, feature highlights

**Implementation:**
```css
.metrics-dashboard {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-lg);
    width: 100%;
    margin: 0 auto var(--spacing-3xl);
    padding: 0 var(--spacing-lg);
}

.metric-card {
    text-align: center;
    padding: var(--spacing-xl) var(--spacing-2xl);
    min-width: 140px;
    flex: 0 1 auto;
}

.metric-value {
    font-size: var(--font-3xl);
    font-weight: 800;
    margin-bottom: var(--spacing-xs);
}

.metric-label {
    font-size: var(--font-sm);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
```

**Why Flexbox over Grid:**
- Grid with `auto-fit` creates unequal spacing when cards don't fill row
- Flexbox with `justify-content: center` ensures cards are always centered
- `flex: 0 1 auto` prevents cards from stretching

---

### Pattern 7: Balanced Navigation Footer

**Use Case:** Page-to-page navigation with prev/next buttons

**Implementation:**
```css
/* Container */
.nav-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto var(--spacing-2xl);
    padding: var(--spacing-xl);
}

/* Navigation Links - Equal Width for Visual Balance */
.nav-link {
    min-width: 220px;
    text-align: center;
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    text-decoration: none;
    transition: all 0.3s ease;
}

.nav-link:hover {
    background: rgba(0, 212, 255, 0.1);
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}
```

**Inline Override (for existing pages):**
```html
<nav class="nav-footer" style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto var(--spacing-2xl); padding: var(--spacing-xl);">
    <a href="prev.html" class="nav-link prev" style="min-width: 220px; text-align: center;">
        ← Previous Page
    </a>
    <a href="next.html" class="nav-link next" style="min-width: 220px; text-align: center;">
        Next Page →
    </a>
</nav>
```

**Key Requirements:**
- Equal `min-width` on both buttons (220px)
- Centered text within each button
- `max-width: 1200px` on container with `margin: 0 auto` for page centering
- `justify-content: space-between` pushes buttons to edges
- Bottom margin (`margin-bottom: var(--spacing-2xl)`) for page breathing room

---

## 🎓 Best Practices

### DO ✅
- Use `backdrop-filter` for glass effect (not just opacity)
- Add GPU acceleration hints (`transform: translateZ(0)`)
- Provide reduced-motion fallbacks
- Test on mobile devices (blur is expensive)
- Use CSS variables for consistency
- **Clickable tiles:** Glow border + lift + `cursor: pointer`
- **Non-clickable tiles:** Glass reflection (8s) + `cursor: default`
- Add subtle animations (0.3s duration max)
- Keep animations modern and non-distracting

### DON'T ❌
- Overuse blur (>30px becomes unreadable)
- Animate backdrop-filter directly (use transform/opacity instead)
- Forget vendor prefixes (`-webkit-backdrop-filter`)
- Apply glass to text-heavy content (readability issues)
- Use glass on low-contrast backgrounds
- Chain multiple backdrop-filters (performance hit)
- Ignore mobile performance (disable blur on low-end devices)

---

## 📊 Pattern Selection Guide

| Use Case | Pattern | Interactivity | Animation | Level |
|----------|---------|---------------|-----------|-------|
| **Level 0 multi-category tile (13-19 pages)** | Pattern 15 (Multi-Panel) | Sub-panels: non-interactive, Tags: clickable | Tetris grid, shimmer on hover | Level 0 |
| **Level 0 simple tile (3-6 pages)** | Standard Tile | Interactive | Glow border + lift | Level 0 |
| Clickable tile/card | Multi-Layer Glass Card (Variant A) | Interactive | Glow border + lift on hover | All levels |
| Display card/panel | Multi-Layer Glass Card (Variant B) | Non-interactive | Glass reflection (8s) | All levels |
| Dashboard widget | Neuglass Card | Interactive | Soft shadow + lift | Level 1-2 |
| Architecture tile | Pattern 8 | Interactive | Left border glow + lift | Level 1-2 |
| Orchestrator card | Pattern 9 | Interactive | Phase glow + lift | Level 1-2 |
| STS category | Pattern 10 | Interactive | Icon glow + lift | Level 1-2 |
| Guideline card | Pattern 11 | Non-interactive | Glass reflection only | Level 1-2 |
| Tool card | Pattern 12 | Interactive | Tool icon glow + lift | Level 1-2 |
| Analysis result | Pattern 13 | Non-interactive | Glass reflection only | Level 1-2 |
| Setup step | Pattern 14 | Non-interactive | Glass reflection only | Level 1-2 |
| Modal overlay | Glass Modal | Interactive | Focus + backdrop blur | All levels |
| Notification | Glass Toast | Non-interactive | Slide-in animation | All levels |
| Form control | Glass Dropdown | Interactive | Border glow on focus | All levels |

**Key Differentiation:**
- **Interactive (Clickable):** `cursor: pointer` + glowing border on hover + `translateY(-2px)` lift
- **Non-Interactive (Display):** `cursor: default` + slow glass reflection (8s) + NO hover glow
- **Level 0 Multi-Panel:** Reserved for tiles with 10+ pages requiring categorization

---| Use Case | Pattern | Interactivity | Animation |
|----------|---------|---------------|------------|
| Clickable tile/card | Multi-Layer Glass Card (Variant A) | Interactive | Glow border + lift on hover |
| Display card/panel | Multi-Layer Glass Card (Variant B) | Non-interactive | Glass reflection (8s) |
| Dashboard widget | Neuglass Card | Interactive | Soft shadow + lift |
| Architecture tile | Pattern 8 | Interactive | Left border glow + lift |
| Orchestrator card | Pattern 9 | Interactive | Phase glow + lift |
| STS category | Pattern 10 | Interactive | Icon glow + lift |
| Guideline card | Pattern 11 | Non-interactive | Glass reflection only |
| Tool card | Pattern 12 | Interactive | Tool icon glow + lift |
| Analysis result | Pattern 13 | Non-interactive | Glass reflection only |
| Setup step | Pattern 14 | Non-interactive | Glass reflection only |
| Modal overlay | Glass Modal | Interactive | Focus + backdrop blur |
| Notification | Glass Toast | Non-interactive | Slide-in animation |
| Form control | Glass Dropdown | Interactive | Border glow on focus |

---

## 🔄 Migration from v2.x

**Breaking Changes:**
- Removed single-layer `.glass-basic` (use `.glass-card` instead)
- Renamed `--glass-opacity` → `--glass-bg`
- Changed default blur from 10px → 20px
- Updated transition timing (now uses cubic-bezier)

**Migration Script:**
```javascript
// Auto-migrate v2.x to v3.0
document.querySelectorAll('.glass-basic').forEach(el => {
    el.classList.remove('glass-basic');
    el.classList.add('glass-card');
});

// Update CSS variables
document.documentElement.style.setProperty('--glass-bg', 'rgba(26, 31, 58, 0.6)');
```

---

## 📚 External Resources

- **MDN backdrop-filter:** https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter
- **Can I Use:** https://caniuse.com/css-backdrop-filter
- **Performance Guide:** https://web.dev/backdrop-filter/
- **Glassmorphism.com:** Design inspiration

---

## 📄 Version History

### v4.0.1 (January 1, 2026)
- 🎯 **NEW:** Added Core Principle #12 - Proper Spacing rule
- ✨ Enforced minimum 1.5rem (24px) vertical gap between stacked cards/panels
- 🐛 **FIX:** Resolved cramped spacing in multi-panel layouts (Security, Orchestrators, STS)
- 📚 Updated spacing requirements for grid layouts and stacked elements

### v4.0.0 (January 1, 2026)
- 🎯 **BREAKING:** Enforced 2-level maximum hierarchy (Level 0 → Level 1 → Level 2)
- 🎯 **BREAKING:** Animation Tier System v4.0.0 with strict scope enforcement
- 🎨 **NEW:** Subtle & modern animation philosophy - non-distracting by design
- 🎨 **NEW:** Clear differentiation between clickable (glow border + pointer) vs non-clickable (glass reflection + default cursor)
- ✨ Added scope for all 9 CORTEX tiles (Architecture, Security, Orchestrators, Token Optimization, STS, Best Practices, Toolkit Manager, LENS, Get Started)
- ✨ Documented 42 Level 2 pages across 9 tiles with specific D3.js/Mermaid visualizations
- ✨ Added T1 (Subtle) as universal default for ALL Level 1/2 pages
- ✨ Added T3 (Dramatic) restriction to ONLY Level 0 (Home hero)
- ✨ Pattern 1 split into Variant A (Clickable) and Variant B (Display) with distinct hover behaviors
- ✨ Updated Pattern 8-14 with consistent clickable/non-clickable styling
- ⛔ Deprecated Level 3 pages (use inline/modal instead)
- 📚 Added tile-specific visual patterns with clear interactivity indicators
- 📚 Added animation migration guide (T3→T1) for existing pages
- 📚 Updated Pattern Selection Guide with interactivity column
- 🔄 Updated view hierarchy architecture diagram
- 🔄 Removed all dramatic animations from standard page patterns

### v3.2.0 (December 31, 2025)
- ✨ Added Animation Tier System (T1/T2/T3)
- ✨ Added Layout Pattern Collection
- 📚 Updated Pattern 6 (Metrics Dashboard) with flexbox vs grid guidance
- 📚 Updated Pattern 7 (Navigation Footer) with balanced layout

### v3.1.0 (December 31, 2025)
- ✨ Added Pattern 6: Metrics Dashboard (Centered Flexbox)
- ✨ Added Pattern 7: Balanced Navigation Footer
- 📚 Documented flexbox vs grid trade-offs for centered layouts
- 📚 Added inline override examples for existing pages

### v3.0.0 (December 31, 2025)
- ✨ Added multi-layer glassmorphism system
- ✨ Added neuglass, morphing, light leak, liquid blob patterns
- ✨ Added 5 UI component patterns (modal, toast, drawer, dropdown, tooltip)
- ✨ Added micro-interactions library (ripple, tilt, glow, shimmer, magnetic)
- ✨ Added performance optimization (GPU acceleration, conditional blur, lazy loading)
- ✨ Added GlassManager and GlassPerformanceMonitor scripts
- 🔄 Changed default blur from 10px → 20px
- 🔄 Updated transitions to cubic-bezier easing
- 📚 Added pattern selection guide

### v2.3.0 (December 31, 2025)
- Added Contained Action Panel pattern
- Added Adaptive Code Panel Height Algorithm
- Added D3.js Layout Pattern Selection Guide

### v2.2.0 (Previous)
- Added STS Code Panel Height Algorithm
- Added responsive breakpoints

### v2.1.0 (Previous)
- Added FontAwesome icon standards
- Added breadcrumb navigation

### v2.0.0 (Previous)
- Initial glassmorphism design system
- Basic glass card pattern
- Mobile responsiveness

---

**Generated by:** CORTEX Optimization Engine v2.0.0  
**Standard Version:** 4.0.1  
**Last Review:** January 1, 2026  
**Next Review:** Q2 2026
