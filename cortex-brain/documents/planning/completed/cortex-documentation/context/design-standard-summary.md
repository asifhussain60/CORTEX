# Phase 0.0: Design Standard Summary

**Plan:** Glassmorphism Documentation Standardization  
**Version:** 7.0.0 | **Date:** January 1, 2026  
**Author:** Asif Hussain  
**Source:** `glassmorphism-design-standard.md` v4.0.1 (3,005 lines)

---

## 🎯 Core Principles (12 Rules)

1. **Multi-Layer Depth** - Stacked glass layers with varying opacity
2. **Dynamic Lighting** - Simulated light sources for realism
3. **Smooth Interactions** - Micro-animations with cubic-bezier easing
4. **GPU Acceleration** - Hardware-accelerated transforms
5. **Performance First** - Conditional blur, lazy loading
6. **Accessibility** - WCAG 2.1 AA compliance, reduced-motion support
7. **Subtle by Default** - T1 animations for ALL Level 1 & Level 2 pages
8. **2-Level Maximum** - All tiles limited to Level 0 → Level 1 → Level 2
9. **NO Inline Styles** - Zero tolerance for `style=""` attributes
10. **Header/Footer Standard** - Standardized glass header/footer across ALL views
11. **Responsive Mandatory** - 375px base, 768px tablet, 1440px desktop
12. **Proper Spacing** - Minimum 24px (1.5rem) vertical gap between cards/panels

---

## 📐 Spacing System

### CSS Variables

```css
:root {
    --space-xs: 0.25rem;   /* 4px */
    --space-sm: 0.5rem;    /* 8px */
    --space-md: 1rem;      /* 16px */
    --space-lg: 1.5rem;    /* 24px - DEFAULT for stacked cards */
    --space-xl: 2rem;      /* 32px */
    --space-2xl: 3rem;     /* 48px - Section spacing */
    --space-3xl: 4rem;     /* 64px - Major section spacing */
}
```

### Minimum Requirements

| Element Type | Spacing | CSS Variable |
|--------------|---------|--------------|
| Cards/Panels | 24px | `var(--space-lg)` |
| Category Sections | 48px | `var(--space-2xl)` |
| Multi-Panel Grids | 24px gap | `gap: var(--space-lg)` |
| Grid Rows | 24px row-gap | `row-gap: var(--space-lg)` |
| Key Features Sections | 64px | `var(--space-3xl)` |
| Main Panel Wrappers | 48px | `var(--space-2xl)` |
| Mobile (≤767px) | 16px | `var(--space-md)` |

---

## 🎬 Animation Tier System

### Tier Definitions

| Tier | Name | Duration | Scope | Effects |
|------|------|----------|-------|---------|
| **T1** | Subtle | 0.2-0.3s | ALL Level 1 & 2 | Opacity, light transforms, simple transitions |
| **T2** | Accent | 0.1-0.2s | UI elements | Button press, form focus, selection |
| **T3** | Dramatic | 2-10s | Level 0 ONLY | borderGlowSweep, blobMorph, particle effects |

### Clickable vs Non-Clickable

| Attribute | Clickable | Non-Clickable |
|-----------|-----------|---------------|
| Cursor | `pointer` | `default` |
| Border | Glowing on hover | Static |
| Transform | `translateY(-2px)` lift | None |
| Shadow | Glow effect | Static shadow |
| Animation | Transition only | Static highlight |

### T1 Clickable Implementation

```css
.glass-card-clickable {
    cursor: pointer;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.glass-card-clickable:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 212, 255, 0.3);
}
```

### T1 Non-Clickable Implementation

```css
.glass-card-display {
    cursor: default;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.glass-card-display::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
}

.glass-card-display:hover {
    /* NO transform, NO glow, NO border change */
}
```

### Forbidden Animations (Level 1 & 2)

- ❌ `borderGlowSweep` keyframe
- ❌ `blobMorph` keyframe
- ❌ `lightLeakPrimary` keyframe
- ❌ `glowPulse` keyframe
- ❌ Any `infinite` animation
- ❌ SVG filter glow effects

---

## 🏗️ Header/Footer Standard

### Level 0 Header (WITH LOGO)

```html
<header class="glass-header">
    <div class="header-content">
        <a href="index.html" class="header-brand">
            <i class="fas fa-brain"></i>
            <h1>CORTEX</h1>
        </a>
        <nav class="header-nav">
            <a href="#features" class="nav-link">Features</a>
        </nav>
    </div>
</header>
```

### Level 1 & 2 Header (NO LOGO)

```html
<header class="glass-header">
    <div class="header-content">
        <nav class="header-nav">
            <a href="../index.html" class="nav-link"><i class="fas fa-home"></i> Home</a>
            <a href="index.html" class="nav-link"><i class="fas fa-[icon]"></i> [Domain]</a>
        </nav>
    </div>
</header>
```

### Footer (All Levels)

```html
<footer class="glass-footer">
    <div class="footer-content">
        <div class="footer-copyright">
            <p>© 2026 Asif Hussain. All rights reserved.</p>
        </div>
        <div class="footer-links">
            <a href="https://github.com/asifhussain60/CORTEX" target="_blank">
                <i class="fab fa-github"></i> GitHub
            </a>
            <span class="footer-version">CORTEX v4.0</span>
        </div>
    </div>
</footer>
```

---

## 📊 Multi-Panel Grid Layouts

### Security (2×2 Grid - 4 panels)

```css
.category-panels-grid:not(.grid-3x2):not(.grid-2x3) {
    grid-template-columns: repeat(2, 1fr);
    row-gap: var(--space-lg);
    column-gap: var(--space-lg);
}
```

### Orchestrators (2×3 Grid - 5 panels)

```css
.category-panels-grid.grid-2x3 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, auto);
    row-gap: var(--space-lg);
    column-gap: var(--space-lg);
}
```

### STS (3×2 Grid - 6 panels)

```css
.category-panels-grid.grid-3x2 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, auto);
    row-gap: var(--space-lg);
    column-gap: var(--space-lg);
}
```

---

## 📱 Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | 375px (base) | Single column, stacked nav, 44px touch targets |
| Tablet | 768px | 2-column grids, horizontal nav |
| Desktop | 1440px | Full grids, expanded spacing, max-width 1400px |

### Mobile-First Pattern

```css
.component { /* Mobile default */ }

@media (min-width: 768px) { /* Tablet */ }

@media (min-width: 1440px) { /* Desktop */ }
```

---

## ✅ Validation Checklist

### Spacing
- [ ] All stacked cards have ≥24px vertical spacing
- [ ] Multi-panel grids use `gap: var(--space-lg)`
- [ ] Grid `row-gap` is explicitly set
- [ ] Section spacing is ≥48px
- [ ] Key features sections have ≥64px bottom margin

### Animation
- [ ] Level 1 & 2 pages use T1 only (0.2-0.3s)
- [ ] No keyframe animations on Level 1 & 2
- [ ] Clickable elements have pointer cursor + lift
- [ ] Non-clickable elements have default cursor

### Structure
- [ ] Level 0 header has logo
- [ ] Level 1 & 2 headers have navigation only
- [ ] All pages have standardized footer
- [ ] Zero inline styles (`style=""`)

### Responsive
- [ ] Works at 375px (mobile)
- [ ] Works at 768px (tablet)
- [ ] Works at 1440px (desktop)

---

**Phase 0.0 Complete** → Proceed to Phase 0.1: Current State Audit
