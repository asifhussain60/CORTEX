# CORTEX Documentation Styling Standards

**Version:** 1.1.0  
**Created:** December 28, 2025  
**Last Updated:** December 28, 2025  
**Author:** Asif Hussain  
**Purpose:** Standardized styling guide for all CORTEX feature documentation

---

## 🎨 Overview

This document defines the visual styling standards for CORTEX feature documentation to ensure consistency across all orchestrators, agents, and system features. These standards were established based on the Planning System documentation redesign and refined through iterative improvements across multiple documentation pages including orchestrator indexes, technical documentation, and the interactive story viewer.

---

## 📐 Logo Standards

### Page Logo (`.page-logo`)

**Desktop:**
```css
.page-logo {
    width: 300px;
    height: auto;
    filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5));
    transition: filter var(--transition-base);
}
```

**Mobile (max-width: 768px):**
```css
.page-logo {
    width: 200px;
}
```

**Guidelines:**
- Logo must be 300px wide on desktop for optimal visibility
- Scales to 200px on mobile devices for space efficiency
- Always include glow effect for brand consistency
- Center-aligned via `.logo-header` container

---

## 🏷️ Title & Badge Standards

### Page Titles

**Format:** `{Feature Name}` (NO version numbers)

**❌ Incorrect:**
```html
<h1>Planning System 2.0</h1>
```

**✅ Correct:**
```html
<h1>Planning System</h1>
```

**Guidelines:**
- Feature names should be timeless
- Version numbers belong in metadata or footer only
- Keep titles concise and descriptive

### Status Badges

**Usage:** Remove "Production Ready" and similar status badges from main content

**Rationale:**
- Status changes frequently
- Creates visual clutter
- Status should be in version metadata, not UI

---

## 📏 Spacing Standards

### Panel Spacing

All major sections require consistent spacing:

```css
/* Glass cards (main content containers) */
.glass-card {
    margin-bottom: var(--spacing-2xl); /* 3rem / 48px */
}

/* Section containers */
.section-overview,
.section-workflow,
.section-architecture,
.section-integration,
.section-configuration,
.section-usage,
.section-testing,
.section-performance {
    margin-top: var(--spacing-2xl);    /* 3rem / 48px */
    margin-bottom: var(--spacing-2xl);  /* 3rem / 48px */
}
```

**Guidelines:**
- Minimum 48px between major panels
- Prevents visual cramping
- Improves scanability

---

## 🎯 Icon Sizing Standards

### Phase Icons (`.phase-icon`)

```css
.phase-icon {
    font-size: 2.4rem;  /* 20% larger than base 2rem */
    margin-bottom: var(--spacing-sm);
    display: block;
}
```

### Tier/Card Icons (`.tier-icon`)

```css
.tier-icon {
    font-size: 2.4rem;  /* 20% larger than base 2rem */
}
```

**Guidelines:**
- All feature icons scaled to 2.4rem (38.4px)
- 20% increase from original 2rem ensures visibility
- Consistent sizing across all card types

---

## 📝 Typography Standards

### Base Font Settings

```css
html {
    font-size: 16px;
}

body {
    line-height: 1.7;  /* Increased from 1.6 for readability */
}
```

### Component Font Sizes

| Component | Size | Use Case |
|-----------|------|----------|
| Phase Title | 1.125rem (18px) | Workflow phase headers |
| Phase Description | 1rem (16px) | Phase explanations |
| Tier Title | 1.375rem (22px) | DoR/DoD card headers |
| Tier Subtitle | 1rem (16px) | Card sub-headers |
| Feature List Items | 1.0625rem (17px) | Bullet point lists |

**Guidelines:**
- All fonts optimized for desktop AND mobile
- Minimum 16px for body text (accessibility)
- Line-height 1.6-1.7 for comfortable reading
- Scale proportionally for mobile (never below 14px)

---

## 📋 List & Bullet Standards

### Feature Lists (DoR/DoD Cards)

**CSS Implementation:**
```css
.feature-list {
    list-style: none;
    padding: 0;
    margin: var(--spacing-lg) 0;
}

.feature-list li {
    padding: var(--spacing-xs) var(--spacing-sm) var(--spacing-xs) 2rem;  /* Left padding for bullet space */
    margin-bottom: 0;                                                      /* No spacing between items */
    background: var(--glass-bg);
    border-radius: var(--radius-sm);
    backdrop-filter: blur(10px);
    font-size: 1.0625rem;
    line-height: 1.5;                                                      /* Compact line height */
    position: relative;                                                    /* For absolute bullet positioning */
}

.feature-list li::before {
    content: "•";
    font-size: 1.5rem;                    /* Larger bullet */
    color: var(--accent-primary);          /* Branded color */
    font-weight: bold;
    position: absolute;                    /* Absolute positioning */
    left: 0.5rem;                         /* Fixed left position */
    top: 0.125rem;                        /* Slight vertical adjustment */
}

.feature-list li strong {
    color: var(--accent-primary);
}
```

**HTML Implementation:**
```html
<!-- ❌ DON'T include bullets in HTML -->
<ul class="feature-list">
    <li>• Feature description provided</li>
</ul>

<!-- ✅ DO let CSS handle bullets -->
<ul class="feature-list">
    <li>Feature description provided</li>
</ul>
```

**Guidelines:**
- **Minimal spacing:** No margin between items, 2rem left padding for bullets
- **Larger bullets:** 1.5rem (24px) with brand color
- **Absolute positioning:** Bullets positioned absolutely to prevent text wrapping issues
- **Increased font:** 1.0625rem (17px) for readability
- **Compact line-height:** 1.5 for tight vertical spacing
- **CSS-generated bullets:** Use `::before` pseudo-element with `position: absolute`, never text in HTML
- **Multi-line support:** Text wraps properly without overlapping bullets

---

## 📱 Responsive Design Requirements

### Mobile Breakpoints

```css
/* Tablet: 768px */
@media (max-width: 768px) {
    .page-logo { width: 200px; }
    /* Font sizes remain at desktop size */
}

/* Mobile: 480px */
@media (max-width: 480px) {
    .metrics-grid-4,
    .metrics-grid-3 {
        grid-template-columns: 1fr; /* Stack cards */
    }
}
```

**Guidelines:**
- Logo scales proportionally
- Text remains readable (never below 14px)
- Cards stack vertically on mobile
- Touch targets minimum 44x44px

---

## 🎨 Color & Visual Standards

### Background & Theme

**Primary Background Gradient:**
```css
body {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    background-attachment: fixed;
}
```

**Color Variables:**
```css
--bg-primary: #0a0e27;      /* Dark navy blue */
--bg-secondary: #1a1f3a;    /* Medium navy blue */
--glass-bg: rgba(26, 31, 58, 0.7);
--glass-border: rgba(255, 255, 255, 0.1);
```

**Guidelines:**
- All CORTEX documentation uses dark navy blue gradient background
- Consistent across all pages (main docs, technical docs, feature pages)
- Fixed attachment prevents scrolling parallax

### Brand Colors

```css
--accent-primary: #00d4ff;    /* CORTEX cyan */
--accent-secondary: #7b61ff;  /* Purple */
--success: #00ff88;           /* Green */
--warning: #ffa500;           /* Orange */
```

**Usage:**
- Icons: `--accent-primary`
- Bullets: `--accent-primary`
- Titles: `--accent-primary`
- Success badges: `--success`
- Gradients: `linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%)`

### Glass Effects

All cards use glassmorphism:
```css
background: rgba(26, 31, 58, 0.7);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.1);
```

---

## ✅ Quick Checklist for New Documentation

Use this checklist when creating new feature documentation:

**Layout & Structure:**
- [ ] Logo is 300px (desktop) / 200px (mobile)
- [ ] NO version numbers in title or H1
- [ ] NO "Production Ready" or status badges
- [ ] All panels aligned to 1400px max-width
- [ ] 48px spacing between panels (`var(--spacing-2xl)`)
- [ ] Remove redundant "View Full Technical Details" links
- [ ] Remove duplicate reference panels

**Colors & Theme:**
- [ ] Background gradient: `#0a0e27` to `#1a1f3a`
- [ ] All accent gradients use: `#00d4ff` to `#7b61ff`
- [ ] Text color: `#ffffff` (white) on dark backgrounds
- [ ] Diagram text labels: `#ffffff` (white)
- [ ] Theme consistent across main docs, technical docs, and story pages

**Typography:**
- [ ] Icons are 2.4rem (phase-icon, tier-icon)
- [ ] Phase titles: 1.125rem
- [ ] Phase descriptions: 1rem
- [ ] Tier titles: 1.375rem
- [ ] Feature list items: 1.0625rem
- [ ] Story viewer: 1.2em across all breakpoints
- [ ] Line-height: 1.5 for compact lists, 1.7 for body text

**Lists & Bullets:**
- [ ] Bullets use CSS `::before` with `position: absolute`, NOT HTML text
- [ ] Bullet size: 1.5rem with brand color (`--accent-primary`)
- [ ] List item spacing: No margin, minimal padding (2rem left for bullets)
- [ ] Multi-line text wraps properly without overlapping bullets
- [ ] No bullet characters in HTML markup

**Mobile Responsiveness:**
- [ ] Mobile-responsive tested at 768px and 480px
- [ ] Touch targets ≥44px (minimum 60px for buttons)
- [ ] Navigation buttons: full text (desktop), arrows only (mobile)
- [ ] Remove `<hr>` separators on mobile
- [ ] Mobile navigation in glassmorphic panel
- [ ] Cards stack vertically on mobile
- [ ] Font sizes remain readable (≥14px minimum)

**Interactive Elements:**
- [ ] D3.js diagrams match panel width (1400px)
- [ ] Category filters use brand gradient
- [ ] Hover tooltips use glassmorphism
- [ ] All colors use CSS variables
- [ ] Glassmorphism effects applied consistently

**Version Control:**
- [ ] Version numbers removed from UI elements
- [ ] Technical library versions preserved
- [ ] Migration documentation versions kept
- [ ] Viewport meta tags unchanged

---

## 📦 Template Files & Examples

**Reference Implementations:**
- **HTML Template:** `docs/orchestrators/planning-system.html` (comprehensive feature page)
- **Index Template:** `docs/orchestrators/index.html` (interactive diagram + organized sections)
- **Technical Template:** `docs/technical/orchestrators/index.html` (D3.js visualizations)
- **Story Viewer:** `docs/story/viewer.html` (responsive mobile navigation)

---

## 🖼️ Interactive Elements

### D3.js Orchestrator Visualization

**Container Width:**
```css
#orchestrator-map {
    max-width: 1400px;
    margin: 0 auto var(--spacing-2xl);
}
```

**Text Color on Diagrams:**
```css
.node text {
    fill: #ffffff;  /* Always white on dark backgrounds */
}
```

**Guidelines:**
- Interactive diagrams match panel width (1400px)
- All text labels must be white (`#ffffff`) on dark backgrounds
- Category filters should use brand gradient colors
- Hover tooltips use glassmorphism styling

### Page Structure (Index Pages)

**Recommended Layout:**
1. **Logo** (centered, 300px)
2. **Interactive Diagram** (if applicable, 1400px max-width)
3. **Introduction Panel** (includes "How It Works" explanations)
4. **Primary Items** (grid of main features/orchestrators)
5. **Secondary Sections** (supporting items, metadata)

**Guidelines:**
- All panels align to 1400px max-width with auto margins
- Remove "View Full Technical Details" links if embedding diagrams
- Remove redundant reference panels
- Maintain consistent glassmorphism across all cards

---

## 📱 Mobile Navigation (Story Viewer)

### Navigation Button Styling

**Desktop (unchanged):**
```css
.chapter-navigation {
    display: flex;
    justify-content: space-between;
    gap: var(--spacing-md);
}

.nav-button {
    /* Full text labels visible */
}
```

**Mobile (max-width: 480px):**
```css
.chapter-navigation {
    display: flex;
    justify-content: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: rgba(26, 31, 58, 0.6);
    backdrop-filter: blur(15px);
    border-radius: var(--radius-lg);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-button {
    min-width: 60px;
    padding: var(--spacing-sm);
}

.nav-button .text {
    display: none;  /* Hide text labels */
}

.nav-button .arrow {
    display: block;  /* Show only arrows: ← → */
}

.chapter-navigation hr {
    display: none;  /* Remove horizontal rules */
}
```

**Guidelines:**
- Desktop: Full navigation with text labels
- Mobile: Arrow-only (← →) in glassmorphic panel
- Remove horizontal rule separators on mobile
- Single row of buttons, centered
- Minimum 60px width per button (touch target)

---

## 📝 Font Size Standards by Section

### Story Viewer Typography

**Chapter Body Paragraphs (all breakpoints):**
```css
.chapter-body p {
    font-family: 'Comic Neue', 'Comic Sans MS', cursive, sans-serif;
    font-size: 1.2em;
    margin-bottom: 1.5rem;
    line-height: 1.6;
}

/* Consistent across desktop, tablet, and mobile */
@media (max-width: 768px) {
    .chapter-body p { font-size: 1.2em; }
}

@media (max-width: 480px) {
    .chapter-body p { font-size: 1.2em; }
}
```

**Guidelines:**
- Standardize font sizes across all devices for consistency
- Comic fonts for storytelling remain at 1.2em
- Technical documentation uses standard system fonts

---

## 🚫 Version Number Removal Policy

### Where to Remove Versions

**❌ Remove from:**
- Page titles (`<title>`)
- H1 headers
- Breadcrumbs
- Meta descriptions
- Feature names in UI

**✅ Keep in:**
- Migration documentation (e.g., "Upgrading from 3.0 to 4.0")
- Technical library versions (e.g., "D3.js 7.4.0")
- Viewport meta tags (e.g., `initial-scale=1.0`)
- Version control references in commit messages
- Code examples demonstrating version-specific features

**Examples:**

| Context | Before | After |
|---------|--------|-------|
| Page title | `CORTEX 4.0 - Planning System` | `CORTEX - Planning System` |
| Feature name | `Planning System 2.0` | `Planning System` |
| Migration doc | `Upgrade to 4.0` | `Upgrade to 4.0` (keep) |
| Library | `D3.js 6.4.0` | `D3.js 7.4.0` (keep) |

**Rationale:**
- Version numbers in UI create maintenance burden
- Features should have timeless names
- Technical references need versions for compatibility
- Migration paths require version context

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-28 | Initial standards from Planning System redesign |
| 1.0.1 | 2025-12-28 | Added background theme, color consistency |
| 1.1.0 | 2025-12-28 | Added interactive elements, mobile navigation, version removal policy, template references, font standardization across breakpoints |

---

## 📧 Contact

**Questions or Suggestions:**  
Asif Hussain | [GitHub](https://github.com/asifhussain60/CORTEX)

---

**© 2025 Asif Hussain. All rights reserved.**
