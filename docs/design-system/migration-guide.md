# Migration Guide: Glassmorphism CSS Standardization

**Version:** 4.0.0  
**Last Updated:** 2026-01-03  
**Target:** Existing CORTEX HTML pages

---

## 📋 Overview

This guide helps you migrate existing HTML pages from scattered glassmorphism styles to the unified design system. The new system consolidates 24+ CSS files into a modular 6-tier architecture with semantic panel names.

**Benefits:**
- 45% smaller CSS (54 KB minified)
- Consistent styling across all pages
- Natural language styling via CORTEX commands
- Better performance (mobile optimized)
- Easier maintenance

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Replace CSS Imports

**Before:**
```html
<link rel="stylesheet" href="assets/css/glass-patterns.css">
<link rel="stylesheet" href="assets/css/variables.css">
<link rel="stylesheet" href="assets/css/main.css">
<!-- ... 5+ more CSS imports -->
```

**After:**
```html
<!-- Production (recommended) -->
<link rel="stylesheet" href="assets/css/minified/cortex-glass-system.min.css">
<link rel="stylesheet" href="assets/css/glass-performance.css">

<!-- OR Development -->
<link rel="stylesheet" href="assets/css/cortex-glass-system.css">
```

### Step 2: Update Class Names

Replace old glass classes with semantic panel names:

```html
<!-- Before -->
<div class="glass-card dashboard-metrics">
  <div class="metric-item">...</div>
</div>

<!-- After -->
<div class="panel-tetris">
  <div class="tile">...</div>
</div>
```

### Step 3: Test & Validate

1. Open page in browser
2. Verify glassmorphism renders correctly
3. Test responsive breakpoints (768px, 480px)
4. Check hover/focus states

---

## 🎴 Panel Migration Matrix

| Old Pattern | New Panel Class | Use Case |
|-------------|-----------------|----------|
| `.glass-card` (dashboard) | `.panel-tetris` | Metrics grids, KPIs |
| `.glass-card` (hero) | `.panel-intro` | Landing sections, CTAs |
| `.capability-cards` | `.panel-compact-cards` | Feature rows |
| `.analysis-grid` | `.panel-grid-cards` | 2x3/3x3 detailed grids |
| `.glass-card` (highlight) | `.panel-neon-glass` | Premium features |
| `.glass-modal` | `.panel-modal-glass` | Overlays, dialogs |
| `.glass-toast` | `.panel-toast-glass` | Notifications |
| `.glass-sidebar` | `.panel-sidebar-glass` | Navigation panels |
| `.hero-section` | `.panel-hero-glass` | Full-width heroes |
| `.decorative-blob` | `.panel-blob-glass` | Organic shapes |
| Agent cards | `.panel-agent-showcase` | Agent capabilities |

---

## 📄 Page-by-Page Migration

### Example 1: Dashboard (CORTEX Lens)

**File:** `docs/lens/index.html`

**Changes:**
1. Remove inline styles (lines 45-83)
2. Replace with `.panel-tetris`
3. Update tile structure

**Before (lines 45-83):**
```html
<div class="dashboard-panel" style="
  background: rgba(10, 15, 30, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 16px;
  padding: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
">
  <div class="metric-tile">
    <span class="icon">📊</span>
    <div class="value">42</div>
    <div class="label">Total Agents</div>
  </div>
  <!-- 5 more tiles -->
</div>
```

**After:**
```html
<div class="panel-tetris">
  <div class="tile">
    <span class="tile__icon">📊</span>
    <div class="tile__content">
      <div class="tile__value">42</div>
      <div class="tile__label">Total Agents</div>
    </div>
  </div>
  <!-- 5 more tiles -->
</div>
```

**CSS Removed:** 40+ lines of inline styles  
**CSS Added:** 1 class name  
**Savings:** ~1.2 KB per page

---

### Example 2: Feature Sections

**File:** `docs/index.html`

**Before:**
```html
<section class="capabilities">
  <div class="card glass-effect">
    <div class="icon">💡</div>
    <h3>Planning</h3>
    <p>Strategic project planning</p>
  </div>
  <div class="card glass-effect">
    <div class="icon">🔍</div>
    <h3>Analysis</h3>
    <p>Deep code analysis</p>
  </div>
  <!-- 3 more cards -->
</section>

<style>
.glass-effect {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  /* ... 10 more properties */
}
</style>
```

**After:**
```html
<section class="panel-compact-cards">
  <div class="card">
    <div class="card__icon">💡</div>
    <h3 class="card__title">Planning</h3>
    <p class="card__desc">Strategic project planning</p>
  </div>
  <div class="card">
    <div class="card__icon">🔍</div>
    <h3 class="card__title">Analysis</h3>
    <p class="card__desc">Deep code analysis</p>
  </div>
  <!-- 3 more cards -->
</section>
```

**CSS Removed:** Custom `.glass-effect` class (15+ properties)  
**CSS Added:** 1 class name (`.panel-compact-cards`)  
**Savings:** Reusable panel style across all pages

---

### Example 3: Modal Dialogs

**Before:**
```html
<div class="modal-overlay">
  <div class="modal-content glass-modal">
    <div class="modal-header">
      <h2>Confirm Action</h2>
      <button class="close">×</button>
    </div>
    <div class="modal-body">
      <p>Are you sure?</p>
    </div>
    <div class="modal-footer">
      <button class="cancel">Cancel</button>
      <button class="confirm">Confirm</button>
    </div>
  </div>
</div>

<style>
.glass-modal {
  background: rgba(20, 30, 50, 0.9);
  backdrop-filter: blur(25px) saturate(200%);
  /* ... 8 more properties */
}
</style>
```

**After:**
```html
<div class="panel-modal-glass">
  <div class="modal">
    <div class="modal__header">
      <h2 class="modal__title">Confirm Action</h2>
      <button class="modal__close">×</button>
    </div>
    <div class="modal__body">
      <p>Are you sure?</p>
    </div>
    <div class="modal__footer">
      <button class="modal__btn modal__btn--secondary">Cancel</button>
      <button class="modal__btn modal__btn--primary">Confirm</button>
    </div>
  </div>
</div>
```

**CSS Removed:** Custom modal styles  
**CSS Added:** BEM-structured panel class  
**Bonus:** Includes `.modal--success`, `.modal--error` variants

---

## 🔧 Common Migration Patterns

### Pattern 1: Inline Styles → Panel Class

**Find & Replace Strategy:**

```bash
# Step 1: Identify inline glassmorphism
grep -r "backdrop-filter" docs/*.html

# Step 2: Determine appropriate panel
# Dashboard metrics → .panel-tetris
# Hero sections → .panel-intro
# Feature cards → .panel-compact-cards

# Step 3: Replace markup
# Remove inline styles
# Add panel class
# Update child element classes (BEM naming)
```

### Pattern 2: Custom Glass Classes → Design Tokens

**Before:**
```css
.custom-glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

**After (use utility classes):**
```html
<div class="blur-md shadow-lg border-subtle">
  <!-- Content -->
</div>
```

Or create custom class using tokens:
```css
.custom-glass {
  background: var(--glass-bg-base);
  backdrop-filter: blur(var(--glass-blur-md));
  border: 1px solid var(--glass-border-subtle);
  box-shadow: var(--shadow-glass-md);
}
```

### Pattern 3: Multiple CSS Files → Single Import

**Before (main.css):**
```css
@import 'variables.css';
@import 'glass-patterns.css';
@import 'glass-effects.css';
@import 'micro-interactions.css';
@import 'responsive.css';
/* ... 10+ more imports */
```

**After (main.css):**
```css
@import 'cortex-glass-system.css';
/* OR for production: */
@import 'minified/cortex-glass-system.min.css';
@import 'glass-performance.css';
```

---

## ✅ Migration Checklist

Use this checklist for each page:

### Pre-Migration
- [ ] Backup original HTML file
- [ ] Document current glassmorphism usage
- [ ] Identify all glass elements on page
- [ ] Screenshot current rendering (reference)

### CSS Updates
- [ ] Replace CSS imports with cortex-glass-system.css
- [ ] Add glass-performance.css for mobile optimization
- [ ] Remove old glass-patterns.css imports
- [ ] Remove custom glass classes from page CSS

### HTML Updates
- [ ] Replace dashboard metrics with `.panel-tetris`
- [ ] Replace hero sections with `.panel-intro`
- [ ] Replace feature cards with `.panel-compact-cards`
- [ ] Replace grids with `.panel-grid-cards`
- [ ] Replace modals with `.panel-modal-glass`
- [ ] Replace toasts with `.panel-toast-glass`
- [ ] Update child element classes (BEM naming)
- [ ] Remove all inline glassmorphism styles

### Testing
- [ ] Visual comparison (before/after screenshots)
- [ ] Responsive breakpoints (768px, 480px)
- [ ] Hover/focus states
- [ ] Animations smooth (60fps)
- [ ] Mobile performance (reduced blur working)
- [ ] Browser compatibility (Chrome, Firefox, Safari)
- [ ] Accessibility (keyboard nav, reduced motion)

### Validation
- [ ] W3C HTML validation
- [ ] Lighthouse performance audit
- [ ] No console errors
- [ ] All glassmorphism rendering correctly

---

## 🐛 Troubleshooting

### Issue: Blur not rendering

**Cause:** Browser doesn't support backdrop-filter  
**Solution:** Add fallback detection

```html
<script>
if (!CSS.supports('backdrop-filter', 'blur(10px)')) {
  document.body.classList.add('glass-optimized');
}
</script>
```

### Issue: Performance degradation on mobile

**Cause:** Too many backdrop-filters  
**Solution:** Import glass-performance.css (reduces blur 30% on mobile)

```html
<link rel="stylesheet" href="assets/css/glass-performance.css">
```

### Issue: Panel not matching design

**Cause:** Custom overrides conflicting  
**Solution:** Remove custom CSS, use panel modifiers

```css
/* Instead of custom styles */
.custom-dashboard { /* ... */ }

/* Use panel with BEM modifiers */
.panel-tetris--large { /* ... */ }
```

### Issue: Missing webkit prefix (Safari)

**Cause:** Old CSS without vendor prefixes  
**Solution:** New system includes -webkit- prefixes automatically

```css
/* Automatically included */
backdrop-filter: blur(20px);
-webkit-backdrop-filter: blur(20px);
```

---

## 📊 Migration Progress Tracking

Track your migration using this template:

```markdown
# Migration Progress: [Project Name]

**Total Pages:** 15
**Migrated:** 8
**Remaining:** 7
**Progress:** 53%

## Completed
- [x] docs/index.html (1h)
- [x] docs/lens/index.html (45m)
- [x] docs/sts/index.html (30m)
- [x] docs/architecture/skull-protection.html (20m)
- [x] docs/architecture/knowledge-graph.html (20m)
- [x] docs/orchestrators/index.html (25m)
- [x] docs/design-system/panel-viewer.html (1h)
- [x] docs/design-system/glassmorphism-guide.html (30m)

## In Progress
- [ ] docs/technical/architecture.html

## Pending
- [ ] docs/agents/index.html
- [ ] docs/operations/index.html
- [ ] docs/brain/index.html
- [ ] docs/testing/index.html
- [ ] docs/deployment/index.html
- [ ] docs/api/index.html

## Issues
- None reported

## Notes
- All pages rendering correctly after migration
- Mobile performance improved (30% blur reduction)
- CSS bundle reduced from 100KB → 54KB
```

---

## 🎉 Post-Migration Benefits

After migrating all pages, you'll experience:

1. **Performance:** 45% smaller CSS (54 KB vs. 100 KB)
2. **Consistency:** Unified glassmorphism across all pages
3. **Maintenance:** Single design system to update
4. **Mobile:** Automatic 30% blur reduction on phones
5. **Accessibility:** Built-in reduced-motion support
6. **Browser Compatibility:** Tested on 5 browsers
7. **Developer Experience:** Semantic panel names
8. **CORTEX Integration:** "style X like Y" commands

---

## 📚 Additional Resources

- **Style Guide:** `docs/design-system/glassmorphism-guide.html`
- **Panel Viewer:** `docs/design-system/panel-viewer.html`
- **W3C Validation Report:** `cortex-brain/documents/reports/w3c-validation-report.md`
- **Performance Report:** `cortex-brain/documents/reports/phase7-github-pages-optimization.md`

---

## 💬 Need Help?

**Common Questions:**

**Q: Can I use custom glass styles alongside panels?**  
A: Yes! Use design tokens for consistency:

```css
.custom-panel {
  background: var(--glass-bg-base);
  backdrop-filter: blur(var(--glass-blur-md));
  border: 1px solid var(--glass-border-subtle);
}
```

**Q: What if I need a panel variant not in the 11-panel taxonomy?**  
A: Create BEM modifiers:

```css
.panel-tetris--compact {
  gap: 0.25rem;
  padding: var(--space-md);
}
```

**Q: How do I test browser compatibility?**  
A: Use @supports queries (already included):

```css
@supports (backdrop-filter: blur(10px)) {
  /* Modern browser styles */
}

@supports not (backdrop-filter: blur(10px)) {
  /* Fallback for IE11 */
}
```

---

**Migration Complete? Mark your progress in the master plan!**

See: `cortex-brain/documents/planning/active/glassmorphism-css-standardization/00-glassmorphism.md`
