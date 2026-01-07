# Phase 0.3: CSS Architecture Review

**Generated:** 2025-06-01  
**Phase:** 0 - Functionality Discovery & Baseline  
**Status:** ✅ COMPLETE

---

## 📊 CSS File Summary

| File | Lines | Version | Purpose |
|------|-------|---------|---------|
| `variables.css` | 258 | v3.0.0 | Design tokens & CSS custom properties |
| `glass-patterns.css` | 1,024 | v3.0.0 | 5 glass patterns + UI components |
| `main.css` | 5,278 | N/A | Base styles + navigation + layout |
| `micro-interactions.css` | ? | N/A | Animation effects |
| `faq.css` | ? | N/A | FAQ page specific |
| `future.css` | ? | N/A | Future page specific |
| `knowledge.css` | ? | N/A | Knowledge library specific |
| `sts.css` | ? | N/A | STS page specific |
| `story.css` | ? | N/A | Story viewer styles |
| `story-print.css` | ? | N/A | Print stylesheet |

**Total CSS Lines:** ~6,560+ (core files)

---

## 🎨 Design Token Categories (variables.css)

### Color Palette
```
--bg-primary: #0a0e27        # Main background
--bg-secondary: #1a1f3a      # Secondary background
--bg-tertiary: #101428       # Tertiary background
--glass-bg: rgba(26, 31, 58, 0.6)    # Glass transparency
--glass-border: rgba(255, 255, 255, 0.1)
--accent-primary: #00d4ff    # Cyan
--accent-secondary: #7b61ff  # Purple
--accent-tertiary: #ff6b9d   # Pink
--text-primary: #ffffff
--text-secondary: #a0a6c0
--text-muted: #6b7280
```

### Status Colors (with RGB variants)
```
--success: #00ff88           # Green
--warning: #ffa500           # Orange
--danger: #ff4444            # Red
--info: #3b82f6              # Blue
```

### Spacing Scale
```
--space-xs: 0.5rem   (8px)
--space-sm: 1rem     (16px)
--space-md: 1.5rem   (24px)
--space-lg: 1.5rem   (24px) - DEFAULT for cards/grids
--space-xl: 3rem     (48px)
--space-2xl: 4rem    (64px)
--space-3xl: 6rem    (96px)
```

### Blur Levels (Glassmorphism)
```
--blur-xs: 5px
--blur-sm: 10px
--blur-md: 20px      # Default for glass-card
--blur-lg: 30px
--blur-xl: 40px
```

### Border Radius
```
--radius-xs: 4px
--radius-sm: 8px
--radius-md: 12px
--radius-lg: 16px    # Default for glass-card
--radius-xl: 24px
--radius-2xl: 32px
--radius-full: 9999px
```

### Z-Index Scale
```
--z-dropdown: 100
--z-sticky: 500
--z-fixed: 900
--z-nav: 1000
--z-drawer: 9998
--z-modal: 9999
--z-tooltip: 10000
--z-toast: 10001
```

---

## 🪟 Glass Patterns Library (glass-patterns.css)

### Pattern 1: Multi-Layer Glass Card (PRIMARY)
- **Class:** `.glass-card`
- **Use Case:** Default card pattern for all content containers
- **Features:**
  - 4-layer effect (background, inner glow, hover depth, border glow)
  - Animated border sweep on hover
  - GPU-accelerated with `will-change`
- **Variants:** `.glass-card--sm`, `.glass-card--lg`, `.glass-card--no-hover`

### Pattern 2: Neuglass Card
- **Class:** `.neuglass-card`
- **Use Case:** Dashboard widgets, settings panels, interactive controls
- **Features:**
  - Neumorphism + Glass hybrid
  - Soft shadows (inner and outer)
  - Pressed/active state support

### Pattern 3: Morphing Glass Card
- **Class:** `.morph-card`
- **Use Case:** Expandable content, detail views, interactive showcases
- **Features:**
  - Border-radius morphing animation
  - Fullscreen expansion capability
  - Close button with rotation animation

### Pattern 4: Light Leak Glass
- **Class:** `.light-leak-glass`
- **Use Case:** Hero sections, feature highlights, ambient backgrounds
- **Features:**
  - Dual light source animation (cyan + purple)
  - 8-second infinite animation cycle
  - Mix-blend-mode overlay effect

### Pattern 5: Liquid Blob Glass
- **Class:** `.liquid-blob`
- **Use Case:** Decorative elements, hero backgrounds
- **Features:**
  - 10-second border-radius morphing
  - Hover pause animation
  - Variants: `.liquid-blob--accent`, `.liquid-blob--success`

---

## 🧩 UI Components

| Component | Class | Features |
|-----------|-------|----------|
| **Modal** | `.glass-modal`, `.glass-modal-overlay` | Centered overlay, scale animation |
| **Toast** | `.glass-toast` | Slide-in right, 4 status variants |
| **Drawer** | `.glass-drawer` | Slide-in panel, left/right variants |
| **Dropdown** | `.glass-dropdown`, `.glass-dropdown-item` | Fade-in, hover states |
| **Tooltip** | `.glass-tooltip` | Arrow pointer, fade animation |

---

## 🏷️ Level 0 Color Variations

### 7-Color Complementary Palette
```css
/* Distribution for category tags */
Cyan (default)  → rgba(0, 212, 255, 0.15)
Purple          → rgba(123, 97, 255, 0.15)
Teal            → rgba(20, 184, 166, 0.15)
Indigo          → rgba(79, 70, 229, 0.15)
Pink            → rgba(236, 72, 153, 0.15)
Emerald         → rgba(16, 185, 129, 0.15)
Amber           → rgba(245, 158, 11, 0.15)
```

### Tag Classes (Level 0 Specific)
```css
.level0-category-tag              # Base cyan
.level0-category-tag.tag-purple
.level0-category-tag.tag-teal
.level0-category-tag.tag-indigo
.level0-category-tag.tag-pink
.level0-category-tag.tag-emerald
.level0-category-tag.tag-amber
```

### Randomized Distribution via nth-child
- Panels 1-6 have unique color assignments per tag position
- Prevents monotonous visual patterns
- Hover states match base colors with increased opacity

---

## 📱 Accessibility & Performance

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
    /* All animations disabled */
    animation: none !important;
    transition: none !important;
}
```

### High Contrast Mode
```css
@media (prefers-contrast: high) {
    --glass-bg: rgba(26, 31, 58, 0.95);
    --glass-border: rgba(255, 255, 255, 0.3);
}
```

### Conditional Blur (Performance)
```css
@media (max-width: 768px) and (max-resolution: 1dppx) {
    /* Blur disabled on low-end devices */
    backdrop-filter: none;
    background-color: rgba(26, 31, 58, 0.95);
}
```

### GPU Acceleration
```css
.glass-optimized {
    transform: translateZ(0);
    will-change: transform, opacity;
    backface-visibility: hidden;
}
```

---

## ⚠️ Version Mismatch Alert

| File | Current Version | Design Standard |
|------|-----------------|-----------------|
| `variables.css` | v3.0.0 | v4.0.1 |
| `glass-patterns.css` | v3.0.0 | v4.0.1 |

**Action Required:** CSS files need update to align with Design Standard v4.0.1

---

## 🔍 Classes for Reuse (Existing)

### Cards & Containers
- `.glass-card` (+ variants)
- `.neuglass-card`
- `.morph-card`
- `.light-leak-glass`
- `.liquid-blob` (+ variants)

### UI Components
- `.glass-modal`, `.glass-modal-overlay`
- `.glass-toast` (+ status variants)
- `.glass-drawer` (+ left/right)
- `.glass-dropdown`, `.glass-dropdown-item`
- `.glass-tooltip`

### Level 0 Specific
- `.level0-category-tag` (+ 7 color variants)
- `.level0-category-subpanel`

### Utility
- `.glass-optimized`
- `.glass-card--no-hover`

---

## 🆕 Classes to Create (Based on Design Standard v4.0.1)

| Class | Purpose | Priority |
|-------|---------|----------|
| `.level0-hero` | Level 0 hero section with T3 animations | HIGH |
| `.level1-hub-header` | Hub page header with T1 animations | HIGH |
| `.level2-detail-header` | Detail page header with T1 animations | HIGH |
| `.breadcrumb-glass` | Glassmorphism breadcrumb component | MEDIUM |
| `.tile-grid-9` | 9-tile grid layout for Level 0 | HIGH |
| `.animation-t1` | Tier 1 subtle animations (L1/L2) | HIGH |
| `.animation-t2` | Tier 2 accent animations (buttons) | MEDIUM |
| `.animation-t3` | Tier 3 dramatic animations (L0 only) | HIGH |

---

## 📋 CSS Architecture Recommendations

### Immediate Actions (Phase 1)
1. Update `variables.css` to v4.0.1 tokens
2. Add animation tier CSS variables
3. Create Level-specific header classes
4. Standardize spacing with `--space-lg` for cards

### Future Enhancements
1. Light mode support preparation
2. Print stylesheet for documentation
3. Component-specific CSS extraction

---

## ✅ Phase 0.3 Summary

| Metric | Value |
|--------|-------|
| Total CSS Files | 10 |
| Core CSS Lines | 6,560+ |
| Glass Patterns | 5 |
| UI Components | 5 |
| Color Variants | 7 |
| Reusable Classes | 25+ |
| Classes to Create | 8 |
| Version Alignment | ⚠️ NEEDS UPDATE (v3.0 → v4.0.1) |

---

*Report generated as part of Phase 0 - Functionality Discovery & Baseline*
