# Design Standards - CORTEX Documentation Site

**Version:** 4.0.0 | **Last Updated:** January 2, 2026  
**Copyright © 2026 Asif Hussain. All rights reserved.**

---

## 📐 Design Hierarchy

**Architecture:** `Level 0 (index.html) → Level 1 Detail Pages (docs/*/*.html)`

- **Level 0:** Home page with multi-panel masonry tiles
- **Level 1:** Detail pages with T1 animations, no logo header, embedded visualizations
- **NO Level 2:** All content fits in Level 1 with expandable sections/tabs

---

## 🎨 Glassmorphism v4.0.1 Standards

### ⛔ ZERO INLINE STYLES POLICY

**CRITICAL REQUIREMENT:** All pages MUST use CSS classes exclusively for styling.

**FORBIDDEN:**
```html
<!-- ❌ NEVER USE INLINE STYLES -->
<div style="color: red; margin: 20px;">Content</div>
<article style="background: rgba(26, 31, 58, 0.7);">Card</article>
<h2 style="font-size: 2rem;">Title</h2>
```

**✅ REQUIRED:**
```html
<!-- ✅ ALWAYS USE CSS CLASSES -->
<div class="error-text">Content</div>
<article class="glass-card-display">Card</article>
<h2 class="section-title">Title</h2>
```

**Enforcement:**
- **Pre-commit validation:** Scan all HTML files for `style="` attributes
- **Code review checklist:** Zero inline styles verified
- **Automated testing:** CI/CD pipeline rejects commits with inline styles

---

## 🎭 Animation Standards

**T1 Animations Only** (Subtle, Professional)

| Animation | Duration | Easing | Use Case |
|-----------|----------|--------|----------|
| **Fade In** | 0.3s | ease-in-out | Page load, card reveal |
| **Slide Up** | 0.2s | ease-out | Scroll animations |
| **Scale** | 0.2s | ease-in-out | Hover effects |
| **Color Shift** | 0.3s | ease | Interactive elements |

**CSS Classes:**
```css
.animation-t1-fade { animation: fadeIn 0.3s ease-in-out; }
.animation-t1-slide { animation: slideUp 0.2s ease-out; }
.animation-t1-scale { animation: scaleIn 0.2s ease-in-out; }
```

**⛔ FORBIDDEN:**
- T2/T3 animations (too aggressive)
- Animations > 0.5s duration
- Infinite loops (except loading spinners)
- Animation on every interaction

---

## 📱 Responsive Design Standards

**Mobile-First Breakpoints:**

| Breakpoint | Width | Target Devices |
|------------|-------|----------------|
| **XS** | 375px | iPhone SE, small phones |
| **SM** | 768px | Tablets, iPad |
| **MD** | 1024px | Laptops, small desktops |
| **LG** | 1440px | Desktops, large screens |
| **XL** | 1920px | 4K displays |

**Layout Requirements:**
- ✅ **Minimum touch target:** 44x44px (Apple HIG)
- ✅ **Minimum spacing:** 1.5rem between stacked cards
- ✅ **Maximum content width:** 1200px (readability)
- ✅ **Fluid typography:** `clamp()` for responsive font sizing

---

## 🎨 CSS Variable Standards

**All colors/spacing MUST use CSS variables:**

```css
/* ✅ CORRECT */
.glass-card {
    background: var(--glass-background);
    color: var(--text-primary);
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
}

/* ❌ WRONG */
.glass-card {
    background: rgba(26, 31, 58, 0.7);
    color: #ffffff;
    padding: 2rem;
    border-radius: 12px;
}
```

**Required CSS Variables:**
```css
:root {
    /* Colors */
    --glass-background: rgba(26, 31, 58, 0.7);
    --text-primary: #ffffff;
    --accent-purple: #7b61ff;
    --accent-cyan: #00d4ff;
    --accent-pink: #ff6b9d;
    
    /* Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 1.5rem;
    --spacing-lg: 2rem;
    --spacing-xl: 3rem;
    
    /* Borders */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    
    /* Animation */
    --transition-fast: 0.2s;
    --transition-normal: 0.3s;
}
```

---

## 📊 Visualization Standards

### Mermaid.js Configuration

```javascript
mermaid.initialize({
    theme: 'dark',
    themeVariables: {
        primaryColor: '#7b61ff',
        primaryTextColor: '#fff',
        primaryBorderColor: '#fff',
        lineColor: '#00d4ff',
        secondaryColor: '#00d4ff',
        tertiaryColor: '#ff6b9d'
    },
    startOnLoad: true,
    securityLevel: 'loose'
});
```

### D3.js Standards

- **Color Schemes:** Use CORTEX brand colors (purple, cyan, pink)
- **Interactivity:** Tooltips, zoom, pan where appropriate
- **Responsive:** SVG viewBox for scalability
- **Accessibility:** ARIA labels, keyboard navigation

---

## ✅ Validation Checklist

**Pre-Deployment Validation:**

```bash
# 1. Check for inline styles (MUST return 0)
grep -r 'style="' docs/**/*.html | wc -l

# 2. Check for hardcoded colors in HTML (MUST return 0)
grep -rE '#[0-9a-fA-F]{6}' docs/**/*.html | grep -v 'href=' | grep -v 'content=' | wc -l

# 3. Validate CSS variable usage (SHOULD find multiple)
grep -r 'var(--' docs/**/*.html | wc -l

# 4. Check for glassmorphism classes
grep -rE 'class="[^"]*glass-card' docs/**/*.html | wc -l

# 5. Check for T1 animation classes
grep -rE 'class="[^"]*animation-t1' docs/**/*.html | wc -l
```

**Expected Results:**
- Inline styles: 0
- Hardcoded colors: 0
- CSS variables: >50
- Glass card classes: >13
- T1 animations: >13
