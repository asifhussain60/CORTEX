# Inline CSS Prohibition - Quick Reference

**Rule:** INLINE_CSS_PROHIBITION  
**Tier:** 0 (Cannot be bypassed)  
**Severity:** BLOCKED  
**Phase:** REFACTOR (Planning System)

---

## ⚡ 30-Second Summary

**NO inline CSS allowed. All styles MUST be in CSS files.**

```
GREEN Phase: Rapid prototyping (inline OK temporarily)
REFACTOR Phase: Migrate to CSS files (MANDATORY)
```

---

## 🚫 Blocked Patterns

### 1. HTML Style Attributes
```html
<!-- ❌ BLOCKED -->
<div style="color: blue; margin: 10px;">

<!-- ✅ CORRECT -->
<div class="content-box">
```

### 2. JSX Inline Styles
```jsx
// ❌ BLOCKED
<div style={{ color: 'blue', margin: '10px' }}>

// ✅ CORRECT
<div className="content-box">
```

### 3. JavaScript Style Manipulation
```javascript
// ❌ BLOCKED
element.style.color = 'red';
element.style.display = 'none';

// ✅ CORRECT
element.classList.add('text-danger');
element.classList.add('hidden');
```

### 4. Embedded `<style>` Tags
```html
<!-- ❌ BLOCKED -->
<style>.header { color: red; }</style>

<!-- ✅ CORRECT -->
<link rel="stylesheet" href="styles.css">
```

---

## 📁 CSS Organization

### Component-Scoped (Recommended)
```
components/
├── Header/
│   ├── Header.jsx
│   └── Header.module.css    ← Styles here
└── Button/
    ├── Button.jsx
    └── Button.module.css    ← Styles here
```

### Atomic/Utility
```
styles/
├── variables.css    ← CSS variables
├── utilities.css    ← .flex, .hidden, .text-center
└── components.css   ← .btn, .card, .modal
```

---

## 🔄 Migration Steps

1. **Detect:** `grep -r 'style=' src/`
2. **Extract:** Move styles to `.css` file
3. **Replace:** Change `style="..."` to `class="..."`
4. **Verify:** Visual regression test
5. **Test:** Run test suite
6. **Commit:** Only if zero inline styles

---

## 🎨 CSS Variables for Theming

```css
/* variables.css */
:root {
  --color-primary: #007bff;
  --color-danger: #dc3545;
  --spacing-md: 16px;
  --font-size-md: 16px;
}

[data-theme="dark"] {
  --color-primary: #0d6efd;
}
```

Usage:
```css
.btn-primary {
  background: var(--color-primary);
  padding: var(--spacing-md);
  font-size: var(--font-size-md);
}
```

---

## ⚠️ Exceptions (Document with Comment)

```jsx
{/* INLINE_CSS_PROHIBITION exception: Dynamic color from API */}
<div style={{ backgroundColor: user.themeColor }}>
```

**Better:** Use CSS variables
```javascript
element.style.setProperty('--user-color', user.themeColor);
```

---

## 🔍 REFACTOR Phase Validation

Planning System automatically checks:
```python
def validate_refactor_phase():
    return (
        validate_no_orphaned_code() and
        validate_no_duplicates() and
        validate_no_inline_css() and    # ← NEW
        validate_tests_pass()
    )
```

---

## 💡 Why This Matters

**Without Centralization:**
- ❌ Styles scattered across 100+ files
- ❌ Same color defined 50+ times
- ❌ Can't theme (no dark mode)
- ❌ Can't cache (performance hit)

**With Centralization:**
- ✅ Single source of truth
- ✅ Define once, use everywhere
- ✅ Easy theming (swap CSS file)
- ✅ Browser caching (faster)

---

## 📚 Full Documentation

See: `cortex-brain/documents/implementation-guides/css-centralization-rule.md`

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
