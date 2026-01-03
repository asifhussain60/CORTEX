# Phase -1.2: Pattern Extraction

**Plan:** Glassmorphism Documentation Standardization  
**Version:** 7.0.0 | **Date:** January 1, 2026  
**Author:** Asif Hussain

---

## 🎨 Extracted CSS Patterns

### 1. CSS Variables (from variables.css)

**✅ REUSE - Already Production Ready:**

```css
/* Spacing System */
--space-xs: 0.5rem;    /* 8px */
--space-sm: 1rem;      /* 16px */
--space-md: 1.5rem;    /* 24px */
--space-lg: 1.5rem;    /* 24px - DEFAULT */
--space-xl: 3rem;      /* 48px */
--space-2xl: 4rem;     /* 64px */

/* Glass Effects */
--glass-bg: rgba(26, 31, 58, 0.6);
--glass-bg-dark: rgba(26, 31, 58, 0.8);
--glass-border: rgba(255, 255, 255, 0.1);
--glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.37), inset 0 1px 0 rgba(255, 255, 255, 0.2);
--glass-shadow-hover: 0 16px 48px rgba(0, 0, 0, 0.5), inset 0 2px 0 rgba(255, 255, 255, 0.3), 0 0 0 1px rgba(0, 212, 255, 0.5);

/* Blur Levels */
--blur-xs: 5px;
--blur-sm: 10px;
--blur-md: 20px;
--blur-lg: 30px;

/* Transitions */
--transition-base: 200ms ease-in-out;
--transition-normal: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* Border Radius */
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 24px;

/* Glow Effects */
--glow-sm: 0 0 10px rgba(0, 212, 255, 0.3);
--glow-md: 0 0 20px rgba(0, 212, 255, 0.3);
--glow-lg: 0 0 40px rgba(0, 212, 255, 0.4);
```

---

### 2. Glass Card Patterns (from glass-patterns.css)

**Pattern 1: Multi-Layer Glass Card (PRIMARY)**
```css
.glass-card {
    background: linear-gradient(135deg, rgba(26, 31, 58, 0.7) 0%, rgba(26, 31, 58, 0.4) 100%);
    backdrop-filter: blur(var(--blur-md, 20px)) saturate(180%);
    border: 1px solid;
    border-image: linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.05)) 1;
    box-shadow: var(--glass-shadow);
    border-radius: var(--radius-lg, 16px);
    padding: var(--space-lg, 2rem);
    transform: translateZ(0);
    will-change: transform, opacity;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    backdrop-filter: blur(25px) saturate(200%);
    transform: translateY(-4px) scale(1.01);
    box-shadow: var(--glass-shadow-hover);
}
```

**Pattern Variant: No Hover (Non-Clickable)**
```css
.glass-card--no-hover {
    transform: none !important;
}

.glass-card--no-hover:hover {
    transform: none !important;
    box-shadow: var(--glass-shadow);
}
```

---

### 3. Multi-Panel Grid Patterns (from index.html inline styles)

**Existing Grid CSS (needs extraction):**
```css
.category-panels-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;  /* Should use --space-lg */
}

@media (min-width: 768px) {
    .category-panels-grid {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .category-panels-grid.grid-3x2 {
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: repeat(2, 1fr);
    }
}

@media (min-width: 1024px) {
    .category-panels-grid {
        gap: 2.5rem;
    }
}

@media (min-width: 1440px) {
    .category-panels-grid {
        gap: 3rem;
    }
}
```

**Category Subpanel (needs extraction):**
```css
.category-subpanel {
    background: linear-gradient(135deg, rgba(10, 14, 39, 0.8), rgba(26, 31, 58, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 2rem 1.5rem;
    min-height: 380px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.category-subpanel.single-tag {
    min-height: 280px;
    padding: 1.5rem 1.25rem;
}
```

---

### 4. Animation Patterns (from glass-patterns.css)

**Border Glow Sweep (T3 - Level 0 Only):**
```css
@keyframes borderGlowSweep {
    0%, 100% { background-position: -200% 0; }
    50% { background-position: 200% 0; }
}
```

**Brain Pulse (T3 - Level 0 Only):**
```css
@keyframes brainPulse {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.6)); }
    50% { transform: scale(1.05); filter: drop-shadow(0 0 30px rgba(0, 212, 255, 0.8)); }
}
```

**T1 Subtle Transitions (Level 1 & 2):**
```css
/* All Level 1 & 2 pages use these only */
transition: all 0.2s ease-in-out;  /* T1: 0.2-0.3s */
transition: opacity 0.3s ease-in-out;
transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

---

### 5. Header/Footer Templates (from index.html)

**Level 0 Header (WITH LOGO):**
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

**Level 1 & 2 Header (NO LOGO - Navigation Only):**
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

**Footer (All Levels):**
```html
<footer class="glass-footer">
    <div class="footer-content">
        <p>© 2026 Asif Hussain. All rights reserved.</p>
        <p>CORTEX v4.0 | <a href="https://github.com/asifhussain60/CORTEX">GitHub</a></p>
    </div>
</footer>
```

---

### 6. Clickable Tag Pattern (from index.html)

**Category Tag (Clickable):**
```html
<a href="security/access-control.html" class="category-tag" data-icon="🔐">
    <span>Access Control</span>
</a>
```

**CSS Pattern:**
```css
.category-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 8px;
    color: var(--accent-primary);
    text-decoration: none;
    font-size: 0.875rem;
    transition: all 0.2s ease-in-out;
    cursor: pointer;
}

.category-tag:hover {
    background: rgba(0, 212, 255, 0.2);
    border-color: rgba(0, 212, 255, 0.5);
    transform: translateY(-2px);
    box-shadow: var(--glow-sm);
}
```

---

## 📊 Pattern Summary

| Pattern | Source File | Lines | Status |
|---------|-------------|-------|--------|
| CSS Variables | `variables.css` | 258 | ✅ Ready |
| Glass Card | `glass-patterns.css` | 120 | ✅ Ready |
| Glass Card Variants | `glass-patterns.css` | 30 | ✅ Ready |
| Multi-Panel Grid | `index.html` (inline) | 80 | ⚠️ Extract to CSS |
| Category Subpanel | `index.html` (inline) | 50 | ⚠️ Extract to CSS |
| Animations T3 | `glass-patterns.css` | 40 | ✅ Ready |
| Transitions T1 | `variables.css` | 10 | ✅ Ready |
| Header/Footer | `index.html` | 40 | ⚠️ Extract to template |
| Category Tags | `index.html` (inline) | 30 | ⚠️ Extract to CSS |

---

## 🎯 Reusable Components Catalog

### Ready for Immediate Reuse (0 changes)

1. **CSS Variables** - Full design token system
2. **`.glass-card`** - Primary glass card pattern
3. **`.glass-card--no-hover`** - Non-clickable variant
4. **Blur levels** - `--blur-xs` through `--blur-xl`
5. **Spacing system** - `--space-xs` through `--space-2xl`
6. **Glow effects** - `--glow-sm` through `--glow-xl`

### Needs CSS Extraction (from index.html inline)

1. **`.category-panels-grid`** - Multi-panel grid layouts
2. **`.category-subpanel`** - Sub-panel styles
3. **`.category-tag`** - Clickable tag styles
4. **`.main-panel-wrapper`** - Panel wrapper styles
5. **`.panel-header-centered`** - Panel header styles

### Needs Template Creation

1. **`_header-level0.html`** - Level 0 header with logo
2. **`_header-level1-2.html`** - Level 1/2 header without logo
3. **`_footer.html`** - Universal footer

---

## ✅ Acceptance Criteria Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| CSS classes extracted | ✅ PASS | 10+ patterns documented |
| HTML structures documented | ✅ PASS | Header, footer, tags templates |
| Animation timing functions listed | ✅ PASS | T1 (0.2-0.3s), T3 (2-10s) patterns |
| Reuse vs create identified | ✅ PASS | Ready: 6, Extract: 5, Create: 3 |

---

**Phase -1.2 Complete** → Proceed to Phase -1.3: Gap Analysis
