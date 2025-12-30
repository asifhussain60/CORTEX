# Orchestrator HTML Standardization Plan

**Created:** 2025-12-27  
**Status:** ✅ COMPLETE  
**Author:** Asif Hussain

---

## 📋 Objective

Apply consistent styling and layout standards across all orchestrator documentation pages.

---

## 🎯 Changes Requested (This Session)

| # | Change | Details |
|---|--------|---------|
| 1 | Breadcrumb position | Move to TOP (before logo) |
| 2 | Logo position | Below breadcrumb |
| 3 | Logo size | 300px × 300px |
| 4 | Logo border | Remove (keep glow) |
| 5 | Feature-benefit panel | Delete div, merge text into main card under H1 |
| 6 | DoR/DoD bullets | Large format (1.25rem font, • prefix) |
| 7 | Bullet gaps | Reduced (padding: 0.25rem, line-height: 1.6) |
| 8 | Emoji icons (H2) | Double size (2rem) |
| 9 | Emoji icons (.tier-icon, .phase-icon, .feature-icon) | Double size (2.5rem) |
| 10 | Panel margins | Add 2rem margin-bottom between sections |
| 11 | Feature-list left border | Remove from CSS |

---

## 📁 Files to Update

### Orchestrator Pages (7 files)
- [x] `docs/orchestrators/planning-system.html`
- [x] `docs/orchestrators/index.html`
- [x] `docs/orchestrators/tdd-orchestrator.html`
- [x] `docs/orchestrators/execution-orchestrator.html`
- [x] `docs/orchestrators/ado-operations.html`
- [x] `docs/orchestrators/sanitization.html`
- [x] `docs/orchestrators/upgrade.html`

### CSS (1 file)
- [x] `docs/assets/css/main.css` - Remove `border-left` from `.feature-list li`

---

## ✅ Validation Checklist

- [x] All HTML files pass syntax validation
- [x] Each file has exactly 1 `<h1>` tag (no duplicates)
- [x] All `feature-benefit-panel` divs removed
- [x] Breadcrumb appears before logo in all files
- [x] Logo size is 300x300 in all files
- [x] All H2 emojis have `font-size: 2rem`
- [x] All icon spans have `font-size: 2.5rem`
- [x] All sections have `margin-bottom: 2rem`

---

## 📊 Completion Summary

| Metric | Value |
|--------|-------|
| Files Updated | 8 |
| HTML Files | 7 |
| CSS Files | 1 |
| Validation Status | ✅ All Pass |
| Completion Date | 2025-12-27 |

---

## 🔄 Reusable Pattern

For future orchestrator pages, apply this template structure:

```html
<body>
    <!-- Skip Link -->
    <a href="#main-content" class="skip-link">Skip to main content</a>
    
    <!-- Breadcrumb Navigation (TOP) -->
    <nav class="breadcrumb">...</nav>
    
    <!-- Logo Header (Below Breadcrumb) -->
    <div class="logo-header">
        <img style="width: 300px; height: 300px; border: none;">
    </div>
    
    <!-- Main Content -->
    <main class="container" id="main-content">
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h1>Page Title</h1>
            <span class="badge">Status</span>
            <p style="margin-top: 1.5rem; font-size: 1.1rem;">
                {intro text from feature-benefit-panel}
            </p>
            ...
        </div>
        
        <section style="margin-bottom: 2rem;">
            <div class="glass-card">
                <h2><span style="font-size: 2rem;">🎯</span> Section Title</h2>
                ...
            </div>
        </section>
    </main>
</body>
```

**Icon Sizing:**
- H2 emojis: `<span style="font-size: 2rem;">🎯</span>`
- Card icons: `style="font-size: 2.5rem;"`

**Feature Lists:**
```html
<ul class="feature-list" style="font-size: 1.25rem; line-height: 1.6; margin: 0.5rem 0;">
    <li style="padding: 0.25rem 0;">• Item text</li>
</ul>
```
