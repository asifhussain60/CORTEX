# MkDocs Restyling Feature Plan - COMPREHENSIVE

**Feature:** MkDocs Site Restyling with Material Design 3  
**Status:** Planning  
**Created:** 2025-11-18  
**Author:** Asif Hussain  
**Priority:** Medium  
**Estimated Effort:** 10-12 hours  
**Context:** Conversation from `.github/CopilotChats/mkdocs-restyling.md`

---

## 🧠 Executive Summary

Comprehensive plan to restyle the CORTEX MkDocs documentation site (http://127.0.0.1:8000/) using Material Design 3 principles while preserving the unique CORTEX brand identity, especially the beloved Comic Sans MS font for story sections.

**Key Challenge:** Balance Material Design consistency with CORTEX's distinctive personality (Comic font, gradient headers, Sacred Rules aesthetic).

---

## 📋 Current State Analysis

### MkDocs Configuration

**Theme:** Material for MkDocs  
**Primary Color:** Deep Purple (#6366F1)  
**Accent Color:** Purple (#8B5CF6)  
**Fonts:**
- Body: Roboto
- Code: Roboto Mono
- Special: Cinzel, IM Fell English (Sacred Rules)
- Story: Comic Sans MS (CRITICAL - DO NOT CHANGE)

**Features Enabled:**
- ✅ Navigation: instant, tracking, tabs, sections, expand, top
- ✅ TOC integration
- ✅ Search: suggest, highlight
- ✅ Content: code copy, tabs link

### Existing CSS Architecture (1,590 lines total)

#### 1. **custom.css** (753 lines)
**Purpose:** Main CORTEX brand styling

**What's Good:**
- ✅ Color tokens defined in `:root` (partial MD3 adoption)
- ✅ Gradient backgrounds (colorful CORTEX identity)
- ✅ Hemisphere badges (left/right brain visual)
- ✅ Hero section with CTA buttons
- ✅ Ancient rules styling (sacred text aesthetic)
- ✅ Responsive breakpoints (mobile/tablet)
- ✅ Navigation sidebar gradient
- ✅ Code blocks dark grey (#1F2937)

**What Needs Work:**
- ❌ Inconsistent token usage (hardcoded values mixed with variables)
- ❌ No comprehensive MD3 token system
- ❌ Arbitrary spacing (1rem, 2rem, 1.5rem mixed)
- ❌ No motion tokens (transitions are inconsistent)
- ❌ Elevation values not standardized
- ❌ Typography scale not following MD3 patterns

**Example Issues:**
```css
/* Current - hardcoded */
.story-section {
  background: #FFFFFF;
  padding: 2rem;
  border-radius: 12px;
}

/* Should be - tokenized */
.story-section {
  background: var(--md-sys-color-surface);
  padding: var(--md-sys-spacing-xl);
  border-radius: var(--md-sys-shape-corner-large);
}
```

#### 2. **technical.css** (379 lines)
**Purpose:** Professional technical documentation styling

**What's Good:**
- ✅ Blue theme for technical headers (#1e40af, #3b82f6, #60a5fa)
- ✅ API reference styling (endpoints, methods)
- ✅ Parameter tables (required/optional indicators)
- ✅ Technical admonitions (warning, danger, info, tip)

**What Needs Work:**
- ❌ Separate color system from custom.css
- ❌ No coordination with main token system
- ❌ Hardcoded values throughout

#### 3. **story.css** (458 lines)
**Purpose:** Comic font + engaging story presentation

**What's Good:**
- ✅ Comic Neue imported from Google Fonts
- ✅ Auto-applies to `/diagrams/story/` paths
- ✅ Clean grey theme for readability
- ✅ Dramatic elements (chapter openings, realization moments)
- ✅ Roomba & tea moment indicators 🤖☕
- ✅ **Comic Sans MS preserved** (CORTEX identity)

**What Needs Work:**
- ❌ Hardcoded spacing/colors
- ❌ Could benefit from MD3 elevation tokens

**CRITICAL PRESERVATION RULE:**
```css
/* DO NOT TOUCH - CORTEX Brand Identity */
body[data-md-path*="diagrams/story/"] .md-typeset {
    font-family: 'Comic Neue', 'Comic Sans MS', cursive, sans-serif !important;
}
```

---

## 🎯 Material Design 3 Gap Analysis

### What's Already Present (Partial MD3)

1. ✅ **Color Tokens (partial):** `:root` variables in custom.css
   ```css
   --cortex-primary: #6366F1;
   --cortex-accent: #8B5CF6;
   ```

2. ✅ **Elevation:** Box shadows on cards, buttons, tables
   ```css
   box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
   ```

3. ✅ **Border Radius:** 8px, 12px, 20px used consistently

4. ✅ **Responsive Design:** Mobile (768px), Tablet (1024px) breakpoints

5. ✅ **Gradient Backgrounds:** Headers, navigation, buttons

### What's Missing (Full MD3 Adoption)

1. ❌ **Comprehensive Token System**
   - No `--md-sys-color-*` tokens
   - No `--md-sys-spacing-*` tokens (4px/8px grid)
   - No `--md-sys-elevation-*` levels
   - No `--md-sys-typescale-*` system

2. ❌ **State Layers**
   - Hover/focus/press states not using MD3 opacity patterns
   - No `::before` pseudo-elements for state overlays

3. ❌ **Motion Tokens**
   - No consistent duration values
   - No easing curves defined
   - Transitions inconsistent (200ms, 0.2s mixed)

4. ❌ **Typography Scale**
   - Font sizes arbitrary (2.5rem, 1.8rem, 1.4rem)
   - Should use MD3 scale (display, headline, title, body)

5. ❌ **Surface System**
   - Background levels not using MD3 surface tokens
   - No surface-variant, surface-container hierarchy

---

## 🎨 Proposed Material Design 3 Token System

### File: `docs/stylesheets/material-tokens.css` (NEW)

```css
:root {
  /* ============================================
     MD3 COLOR TOKENS - CORTEX Edition
     ============================================ */
  
  /* Primary (Indigo - CORTEX brand) */
  --md-sys-color-primary: #6366F1;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #E0E7FF;
  --md-sys-color-on-primary-container: #1E1B4B;
  
  /* Secondary (Purple - CORTEX brand) */
  --md-sys-color-secondary: #8B5CF6;
  --md-sys-color-on-secondary: #FFFFFF;
  --md-sys-color-secondary-container: #F5F3FF;
  --md-sys-color-on-secondary-container: #3B0764;
  
  /* Tertiary (Left Brain - Blue / Right Brain - Purple) */
  --md-sys-color-tertiary: #3B82F6;
  --md-sys-color-on-tertiary: #FFFFFF;
  --md-sys-color-tertiary-container: #DBEAFE;
  --md-sys-color-tertiary-alt: #A855F7;  /* Right brain purple */
  
  /* Surface Hierarchy */
  --md-sys-color-surface: #FFFFFF;
  --md-sys-color-surface-dim: #F8F9FA;
  --md-sys-color-surface-bright: #FFFFFF;
  --md-sys-color-surface-container-lowest: #FFFFFF;
  --md-sys-color-surface-container-low: #FAFBFC;
  --md-sys-color-surface-container: #F3F4F6;
  --md-sys-color-surface-container-high: #E5E7EB;
  --md-sys-color-surface-container-highest: #D1D5DB;
  --md-sys-color-on-surface: #1F2937;
  --md-sys-color-on-surface-variant: #4B5563;
  
  /* ============================================
     MD3 ELEVATION TOKENS
     ============================================ */
  --md-sys-elevation-0: none;
  --md-sys-elevation-1: 0 1px 3px rgba(0, 0, 0, 0.05);
  --md-sys-elevation-2: 0 2px 8px rgba(0, 0, 0, 0.1);
  --md-sys-elevation-3: 0 4px 12px rgba(0, 0, 0, 0.15);
  --md-sys-elevation-4: 0 8px 24px rgba(0, 0, 0, 0.2);
  --md-sys-elevation-5: 0 12px 32px rgba(0, 0, 0, 0.25);
  
  /* ============================================
     MD3 TYPOGRAPHY SCALE
     ============================================ */
  --md-sys-typescale-display-large: 3.5rem;     /* 56px */
  --md-sys-typescale-display-medium: 2.8rem;    /* 45px */
  --md-sys-typescale-display-small: 2.25rem;    /* 36px */
  --md-sys-typescale-headline-large: 2rem;      /* 32px */
  --md-sys-typescale-headline-medium: 1.75rem;  /* 28px */
  --md-sys-typescale-headline-small: 1.5rem;    /* 24px */
  --md-sys-typescale-title-large: 1.375rem;     /* 22px */
  --md-sys-typescale-title-medium: 1rem;        /* 16px */
  --md-sys-typescale-title-small: 0.875rem;     /* 14px */
  --md-sys-typescale-body-large: 1rem;          /* 16px */
  --md-sys-typescale-body-medium: 0.875rem;     /* 14px */
  --md-sys-typescale-body-small: 0.75rem;       /* 12px */
  --md-sys-typescale-label-large: 0.875rem;     /* 14px */
  --md-sys-typescale-label-medium: 0.75rem;     /* 12px */
  --md-sys-typescale-label-small: 0.6875rem;    /* 11px */
  
  /* ============================================
     MD3 SPACING TOKENS (4px grid system)
     ============================================ */
  --md-sys-spacing-none: 0;
  --md-sys-spacing-xs: 0.25rem;   /* 4px */
  --md-sys-spacing-sm: 0.5rem;    /* 8px */
  --md-sys-spacing-md: 1rem;      /* 16px */
  --md-sys-spacing-lg: 1.5rem;    /* 24px */
  --md-sys-spacing-xl: 2rem;      /* 32px */
  --md-sys-spacing-xxl: 3rem;     /* 48px */
  --md-sys-spacing-xxxl: 4rem;    /* 64px */
  
  /* ============================================
     MD3 SHAPE TOKENS (Border Radius)
     ============================================ */
  --md-sys-shape-corner-none: 0;
  --md-sys-shape-corner-extra-small: 4px;
  --md-sys-shape-corner-small: 8px;
  --md-sys-shape-corner-medium: 12px;
  --md-sys-shape-corner-large: 16px;
  --md-sys-shape-corner-extra-large: 28px;
  --md-sys-shape-corner-full: 9999px;
  
  /* ============================================
     MD3 MOTION TOKENS
     ============================================ */
  /* Duration */
  --md-sys-motion-duration-short1: 50ms;
  --md-sys-motion-duration-short2: 100ms;
  --md-sys-motion-duration-short3: 150ms;
  --md-sys-motion-duration-short4: 200ms;
  --md-sys-motion-duration-medium1: 250ms;
  --md-sys-motion-duration-medium2: 300ms;
  --md-sys-motion-duration-medium3: 350ms;
  --md-sys-motion-duration-medium4: 400ms;
  --md-sys-motion-duration-long1: 450ms;
  --md-sys-motion-duration-long2: 500ms;
  --md-sys-motion-duration-long3: 550ms;
  --md-sys-motion-duration-long4: 600ms;
  --md-sys-motion-duration-extra-long1: 700ms;
  --md-sys-motion-duration-extra-long2: 800ms;
  --md-sys-motion-duration-extra-long3: 900ms;
  --md-sys-motion-duration-extra-long4: 1000ms;
  
  /* Easing Curves */
  --md-sys-motion-easing-emphasized: cubic-bezier(0.2, 0, 0, 1);
  --md-sys-motion-easing-emphasized-decelerate: cubic-bezier(0.05, 0.7, 0.1, 1);
  --md-sys-motion-easing-emphasized-accelerate: cubic-bezier(0.3, 0, 0.8, 0.15);
  --md-sys-motion-easing-standard: cubic-bezier(0.2, 0, 0, 1);
  --md-sys-motion-easing-standard-decelerate: cubic-bezier(0, 0, 0, 1);
  --md-sys-motion-easing-standard-accelerate: cubic-bezier(0.3, 0, 1, 1);
  --md-sys-motion-easing-legacy: cubic-bezier(0.4, 0, 0.2, 1);
  --md-sys-motion-easing-legacy-decelerate: cubic-bezier(0, 0, 0.2, 1);
  --md-sys-motion-easing-legacy-accelerate: cubic-bezier(0.4, 0, 1, 1);
  --md-sys-motion-easing-linear: cubic-bezier(0, 0, 1, 1);
  
  /* ============================================
     MD3 STATE LAYER OPACITIES
     ============================================ */
  --md-sys-state-hover-opacity: 0.08;
  --md-sys-state-focus-opacity: 0.12;
  --md-sys-state-pressed-opacity: 0.12;
  --md-sys-state-dragged-opacity: 0.16;
}
```

---

## 🚀 Implementation Plan

### Phase 1: Foundation (4-5 hours)

#### Task 1.1: Create Material Design Tokens File
**Estimated Time:** 1 hour

**Steps:**
1. Create `docs/stylesheets/material-tokens.css` with full MD3 token system (shown above)
2. Add to `mkdocs.yml` `extra_css`:
   ```yaml
   extra_css:
     - stylesheets/material-tokens.css  # NEW - Load first
     - stylesheets/custom.css
     - stylesheets/story.css
     - stylesheets/technical.css
   ```
3. Test that site still loads without errors
4. Git commit: "feat: Add Material Design 3 token system"

**Acceptance Criteria:**
- ✅ File created with all token categories
- ✅ Added to mkdocs.yml
- ✅ Site loads without CSS errors
- ✅ No visual changes yet (tokens defined but not used)

#### Task 1.2: Refactor custom.css - Colors
**Estimated Time:** 1 hour

**Changes:**
```css
/* BEFORE */
.story-section {
  background: #FFFFFF;
  color: #333333;
  border-left: 6px solid #666666;
}

/* AFTER */
.story-section {
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  border-left: 6px solid var(--md-sys-color-on-surface-variant);
}
```

**Scope:** Replace ~50 hardcoded color values in custom.css

**Acceptance Criteria:**
- ✅ 90%+ color values use tokens
- ✅ Visual appearance unchanged
- ✅ Git commit: "refactor: Replace hardcoded colors with MD3 tokens in custom.css"

#### Task 1.3: Refactor custom.css - Spacing
**Estimated Time:** 1 hour

**Changes:**
```css
/* BEFORE */
.story-section {
  padding: 2rem;
  margin: 2rem 0;
  margin-bottom: 1rem;
}

/* AFTER */
.story-section {
  padding: var(--md-sys-spacing-xl);
  margin: var(--md-sys-spacing-xl) 0;
  margin-bottom: var(--md-sys-spacing-md);
}
```

**Scope:** Replace ~40 hardcoded spacing values

**Acceptance Criteria:**
- ✅ Spacing follows 4px/8px grid
- ✅ Visual appearance unchanged
- ✅ Git commit: "refactor: Replace hardcoded spacing with MD3 tokens in custom.css"

#### Task 1.4: Refactor custom.css - Elevation & Shape
**Estimated Time:** 30 minutes

**Changes:**
```css
/* BEFORE */
.story-section {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

/* AFTER */
.story-section {
  box-shadow: var(--md-sys-elevation-2);
  border-radius: var(--md-sys-shape-corner-medium);
}
```

**Scope:** Replace ~30 elevation and border-radius values

**Acceptance Criteria:**
- ✅ Elevation uses tokens
- ✅ Border radius uses tokens
- ✅ Git commit: "refactor: Replace elevation and shape values with MD3 tokens in custom.css"

#### Task 1.5: Refactor custom.css - Typography
**Estimated Time:** 30 minutes

**Changes:**
```css
/* BEFORE */
.story-section h1 {
  font-size: 2.2rem;
}

.story-section h2 {
  font-size: 1.8rem;
}

/* AFTER */
.story-section h1 {
  font-size: var(--md-sys-typescale-headline-large);
}

.story-section h2 {
  font-size: var(--md-sys-typescale-headline-medium);
}
```

**Scope:** Replace ~20 font-size values

**Acceptance Criteria:**
- ✅ Typography follows MD3 scale
- ✅ Visual appearance unchanged
- ✅ Git commit: "refactor: Replace font sizes with MD3 typescale tokens in custom.css"

#### Task 1.6: Test Phase 1 Completion
**Estimated Time:** 30 minutes

**Testing:**
1. Run `mkdocs serve`
2. Visit http://127.0.0.1:8000
3. Test all pages:
   - Home (hero, CTA buttons, Sacred Rules)
   - Story pages (Comic font still there?)
   - Technical pages (blue theme intact?)
   - Architecture (diagrams render?)
4. Test responsive:
   - Mobile (768px)
   - Tablet (1024px)
   - Desktop (1920px)
5. Test dark mode toggle

**Acceptance Criteria:**
- ✅ Site loads without errors
- ✅ Comic Sans MS font on story pages ✓
- ✅ No visual regressions
- ✅ All navigation works
- ✅ Git commit: "test: Phase 1 complete - MD3 tokens applied to custom.css"

---

### Phase 2: Extend to Other CSS Files (2-3 hours)

#### Task 2.1: Refactor technical.css
**Estimated Time:** 1 hour

**Changes:**
- Replace blue theme colors with MD3 tokens
- Use primary/tertiary containers for headers
- Apply spacing tokens
- Apply elevation tokens

**Acceptance Criteria:**
- ✅ Coordinated with custom.css token system
- ✅ Blue theme preserved
- ✅ Git commit: "refactor: Apply MD3 tokens to technical.css"

#### Task 2.2: Refactor story.css
**Estimated Time:** 1 hour

**Changes:**
- Apply spacing tokens
- Apply elevation tokens
- **PRESERVE Comic Sans MS font** (DO NOT TOUCH)

**Critical Check:**
```css
/* MUST REMAIN UNCHANGED */
body[data-md-path*="diagrams/story/"] .md-typeset {
    font-family: 'Comic Neue', 'Comic Sans MS', cursive, sans-serif !important;
}
```

**Acceptance Criteria:**
- ✅ Comic Sans MS font still applied
- ✅ Spacing/elevation use tokens
- ✅ Git commit: "refactor: Apply MD3 tokens to story.css (Comic font preserved)"

#### Task 2.3: Test Phase 2
**Estimated Time:** 30 minutes

**Testing:** Same as Task 1.6

**Acceptance Criteria:**
- ✅ All 3 CSS files use MD3 tokens
- ✅ No visual regressions
- ✅ Comic font preserved

---

### Phase 3: Component Enhancements (3-4 hours)

#### Task 3.1: Add State Layers to Navigation
**Estimated Time:** 1 hour

**Implementation:**
```css
.md-nav__link {
  position: relative;
  transition: all var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard);
}

.md-nav__link::before {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--md-sys-color-primary);
  opacity: 0;
  transition: opacity var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard);
  border-radius: var(--md-sys-shape-corner-small);
}

.md-nav__link:hover::before {
  opacity: var(--md-sys-state-hover-opacity);
}

.md-nav__link:focus::before {
  opacity: var(--md-sys-state-focus-opacity);
}

.md-nav__link:active::before {
  opacity: var(--md-sys-state-pressed-opacity);
}
```

**Acceptance Criteria:**
- ✅ Hover/focus/press states visible
- ✅ Uses MD3 opacity values
- ✅ Smooth transitions with motion tokens
- ✅ Git commit: "feat: Add MD3 state layers to navigation"

#### Task 3.2: Add State Layers to Buttons
**Estimated Time:** 1 hour

**Scope:** CTA buttons, secondary buttons

**Acceptance Criteria:**
- ✅ State layers on all buttons
- ✅ Motion tokens for transitions
- ✅ Git commit: "feat: Add MD3 state layers to buttons"

#### Task 3.3: Add Motion to Cards & Content Blocks
**Estimated Time:** 1 hour

**Implementation:**
```css
.story-section,
.technical-section {
  transition: 
    transform var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-emphasized),
    box-shadow var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-emphasized);
}

.story-section:hover,
.technical-section:hover {
  transform: translateY(-2px);
  box-shadow: var(--md-sys-elevation-3);
}
```

**Acceptance Criteria:**
- ✅ Cards lift on hover
- ✅ Smooth motion with easing curves
- ✅ Git commit: "feat: Add hover motion to content cards"

#### Task 3.4: Test Phase 3
**Estimated Time:** 30 minutes

**Testing:**
- Test all interactive elements (links, buttons, cards)
- Verify motion timing feels natural
- Check accessibility (focus indicators visible)

**Acceptance Criteria:**
- ✅ All interactions feel polished
- ✅ No performance issues
- ✅ Keyboard navigation works

---

### Phase 4: Accessibility & Optimization (1-2 hours)

#### Task 4.1: Verify Color Contrast
**Estimated Time:** 30 minutes

**Tools:**
- Browser DevTools (Lighthouse)
- axe DevTools extension

**Check:**
- Text/background contrast (WCAG AA: 4.5:1)
- Link contrast
- Button contrast

**Acceptance Criteria:**
- ✅ All text meets WCAG AA
- ✅ Links distinguishable
- ✅ Document issues if any

#### Task 4.2: Add Focus Indicators
**Estimated Time:** 30 minutes

**Implementation:**
```css
:focus-visible {
  outline: 2px solid var(--md-sys-color-primary);
  outline-offset: 2px;
  border-radius: var(--md-sys-shape-corner-extra-small);
}
```

**Acceptance Criteria:**
- ✅ All interactive elements have focus ring
- ✅ Keyboard navigation clear
- ✅ Git commit: "a11y: Add focus indicators for keyboard navigation"

#### Task 4.3: Optimize CSS Performance
**Estimated Time:** 30 minutes

**Tasks:**
- Remove unused CSS rules
- Combine similar selectors
- Measure CSS file size before/after

**Acceptance Criteria:**
- ✅ CSS file size reduced 5-10%
- ✅ No unused token variables
- ✅ Git commit: "perf: Optimize CSS file size"

#### Task 4.4: Final Testing
**Estimated Time:** 30 minutes

**Testing:**
- Full site manual test
- Lighthouse audit (should be 90+ for accessibility)
- Mobile device testing
- Dark mode testing

**Acceptance Criteria:**
- ✅ All pages load correctly
- ✅ No regressions
- ✅ Lighthouse score good

---

## 📊 CSS Files Summary

### Files to Modify
1. ✅ `docs/stylesheets/custom.css` (753 lines) - Main refactoring
2. ✅ `docs/stylesheets/technical.css` (379 lines) - Token application
3. ✅ `docs/stylesheets/story.css` (458 lines) - Token application (preserve Comic font)

### Files to Create
1. ✅ `docs/stylesheets/material-tokens.css` (~200 lines) - MD3 design system

### Files to Update
1. ✅ `mkdocs.yml` - Add material-tokens.css to extra_css

### Total CSS Lines
- Before: 1,590 lines
- After: ~1,790 lines (added 200 for tokens)
- Net reduction from optimization: ~1,700 lines (5% reduction)

---

## 🎯 Best Way to Begin - Step-by-Step

### Week 1: Foundation (Phase 1)

**Day 1 (2 hours):**
- Create `material-tokens.css`
- Add to `mkdocs.yml`
- Test site loads

**Day 2 (2 hours):**
- Refactor custom.css colors
- Refactor custom.css spacing
- Test pages

**Day 3 (1 hour):**
- Refactor custom.css elevation/shape
- Refactor custom.css typography
- Full site test

### Week 2: Extension & Enhancement (Phases 2-3)

**Day 4 (2 hours):**
- Refactor technical.css
- Refactor story.css
- Test all pages

**Day 5 (3 hours):**
- Add state layers to navigation
- Add state layers to buttons
- Add motion to cards

### Week 3: Polish (Phase 4)

**Day 6 (2 hours):**
- Verify accessibility
- Add focus indicators
- Optimize CSS
- Final testing

---

## ⚠️ Critical Preservation Rules

### DO NOT CHANGE (CORTEX Brand Identity)

1. ❌ **Comic Sans MS font** for story sections
   ```css
   body[data-md-path*="diagrams/story/"] .md-typeset {
       font-family: 'Comic Neue', 'Comic Sans MS', cursive, sans-serif !important;
   }
   ```

2. ❌ **CORTEX logo** placement

3. ❌ **Navigation structure** (7 sections)

4. ❌ **Ancient rules** styling (Sacred text aesthetic)
   ```css
   .ancient-rules {
       font-family: 'Cinzel', 'IM Fell English', serif !important;
   }
   ```

5. ❌ **Gradient backgrounds** on headers (colorful CORTEX identity)
   ```css
   background: linear-gradient(135deg, var(--cortex-primary), var(--cortex-accent));
   ```

6. ❌ **Hemisphere badges** (left/right brain)
   ```css
   .left-brain { /* Blue */ }
   .right-brain { /* Purple */ }
   ```

### SAFE TO CHANGE (Token Migration)

1. ✅ Hardcoded color values → MD3 tokens
2. ✅ Hardcoded spacing → MD3 spacing grid
3. ✅ Hardcoded elevation → MD3 elevation tokens
4. ✅ Arbitrary font sizes → MD3 typescale
5. ✅ Inconsistent motion → MD3 motion tokens
6. ✅ Border radius values → MD3 shape tokens

---

## 🧪 Testing Strategy

### Manual Testing Checklist

**Every Phase:**
- [ ] Home page renders (hero, CTA, Sacred Rules)
- [ ] Story pages use Comic Sans MS font ✓
- [ ] Technical pages use Roboto font
- [ ] Navigation hover states work
- [ ] Code blocks readable (dark grey #1F2937)
- [ ] Tables render correctly
- [ ] Mobile responsive (768px breakpoint)
- [ ] Tablet responsive (1024px breakpoint)
- [ ] Dark mode toggle (if applicable)

**Phase-Specific:**
- Phase 1: Token values match hardcoded (pixel-perfect)
- Phase 2: All CSS files coordinated
- Phase 3: State layers visible, motion smooth
- Phase 4: Accessibility passes, performance good

### Automated Testing (Future Enhancement)

```bash
# Visual regression testing
npm run test:visual

# Accessibility testing
npm run test:a11y

# CSS linting
npm run lint:css
```

---

## 📈 Success Metrics

### Objective Metrics

1. ✅ **100% token adoption** across all CSS files
2. ✅ **Zero visual regressions** (pixel-perfect match before/after)
3. ✅ **WCAG AA compliance** (4.5:1 contrast ratio minimum)
4. ✅ **CSS file size** reduced 5-10% after optimization
5. ✅ **Lighthouse accessibility score** ≥ 90

### Subjective Metrics

1. ✅ **Design consistency** across all pages
2. ✅ **CORTEX brand preserved** (Comic font, gradients, logo)
3. ✅ **Polished interactions** (state layers, smooth motion)
4. ✅ **Professional appearance** (Material Design quality)

---

## 🚨 Risks & Mitigation

### Risk 1: Visual Regressions
**Probability:** Medium  
**Impact:** High  
**Mitigation:**
- Test incrementally after each task
- Use git commits for easy rollback
- Screenshot before/after for comparison
- Manual QA on all pages before phase completion

### Risk 2: Comic Font Accidentally Changed
**Probability:** Low  
**Impact:** **CRITICAL** (brand identity loss)  
**Mitigation:**
- Add CSS comments: `/* CRITICAL: DO NOT CHANGE - CORTEX Brand Identity */`
- Test story pages after every change
- Visual diff screenshots
- Automated test to verify font family (future)

### Risk 3: Performance Degradation
**Probability:** Low  
**Impact:** Medium  
**Mitigation:**
- Monitor CSS file size (should decrease after optimization)
- Remove unused rules in Phase 4
- Minify for production
- Lighthouse performance testing

### Risk 4: Mobile Breakpoints Break
**Probability:** Medium  
**Impact:** High  
**Mitigation:**
- Test on mobile after each phase
- Use browser DevTools responsive mode
- Test on real devices (iPhone, Android)
- Check media queries during refactor

### Risk 5: Token System Too Complex
**Probability:** Low  
**Impact:** Medium (maintenance burden)  
**Mitigation:**
- Document token usage in comments
- Create token reference guide
- Provide examples in comments
- Regular team review of token usage

---

## 📚 Token Usage Reference

### Quick Reference Guide

```css
/* COLORS */
background: var(--md-sys-color-surface);
color: var(--md-sys-color-on-surface);
border-color: var(--md-sys-color-primary);

/* SPACING */
padding: var(--md-sys-spacing-md);
margin: var(--md-sys-spacing-lg);
gap: var(--md-sys-spacing-sm);

/* ELEVATION */
box-shadow: var(--md-sys-elevation-2);

/* SHAPE */
border-radius: var(--md-sys-shape-corner-medium);

/* TYPOGRAPHY */
font-size: var(--md-sys-typescale-headline-large);

/* MOTION */
transition: all var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard);

/* STATE LAYERS */
opacity: var(--md-sys-state-hover-opacity);
```

---

## 🔄 Post-Implementation

### Documentation Tasks
1. Update README with token system explanation
2. Create token reference guide (separate doc)
3. Document preservation rules
4. Create "restyling guide" for future contributors

### Maintenance Tasks
1. Set up Stylelint with MD3 token rules
2. Add pre-commit hooks for CSS validation
3. Create visual regression test suite
4. Schedule quarterly design consistency reviews

---

## 📝 Notes

- This plan prioritizes **incremental changes** over big-bang refactoring
- Each phase can be completed independently
- Git commits after each task enable easy rollback
- **CORTEX brand identity** is the #1 priority
- Material Design 3 provides consistency, not a redesign
- Comic Sans MS font is **sacred** - DO NOT CHANGE

---

**Plan Status:** ✅ Ready for Approval  
**Total Estimated Time:** 10-12 hours  
**Risk Level:** Low (incremental approach)  
**Brand Preservation Priority:** **CRITICAL** ✅

---

## Appendix A: Git Commit Strategy

```bash
# Phase 1: Foundation
git commit -m "feat: Add Material Design 3 token system"
git commit -m "refactor: Replace hardcoded colors with MD3 tokens in custom.css"
git commit -m "refactor: Replace hardcoded spacing with MD3 tokens in custom.css"
git commit -m "refactor: Replace elevation and shape values with MD3 tokens in custom.css"
git commit -m "refactor: Replace font sizes with MD3 typescale tokens in custom.css"
git commit -m "test: Phase 1 complete - MD3 tokens applied to custom.css"

# Phase 2: Extension
git commit -m "refactor: Apply MD3 tokens to technical.css"
git commit -m "refactor: Apply MD3 tokens to story.css (Comic font preserved)"

# Phase 3: Enhancements
git commit -m "feat: Add MD3 state layers to navigation"
git commit -m "feat: Add MD3 state layers to buttons"
git commit -m "feat: Add hover motion to content cards"

# Phase 4: Polish
git commit -m "a11y: Add focus indicators for keyboard navigation"
git commit -m "perf: Optimize CSS file size"
git commit -m "docs: Update README with MD3 token documentation"
```

---

## Appendix B: Before/After Examples

### Example 1: Story Section Card

**Before:**
```css
.story-section {
  background: #FFFFFF;
  padding: 2rem;
  border-radius: 12px;
  border-left: 6px solid #666666;
  color: #333333;
  margin: 2rem 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

**After:**
```css
.story-section {
  background: var(--md-sys-color-surface);
  padding: var(--md-sys-spacing-xl);
  border-radius: var(--md-sys-shape-corner-medium);
  border-left: 6px solid var(--md-sys-color-on-surface-variant);
  color: var(--md-sys-color-on-surface);
  margin: var(--md-sys-spacing-xl) 0;
  box-shadow: var(--md-sys-elevation-2);
  transition: all var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-emphasized);
}
```

### Example 2: Navigation Link

**Before:**
```css
.md-nav__link {
  color: #374151;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.md-nav__link:hover {
  background: rgba(139, 92, 246, 0.15);
  color: #8B5CF6;
}
```

**After:**
```css
.md-nav__link {
  color: var(--md-sys-color-on-surface);
  padding: var(--md-sys-spacing-sm) var(--md-sys-spacing-md);
  border-radius: var(--md-sys-shape-corner-small);
  position: relative;
  transition: color var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard);
}

.md-nav__link::before {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--md-sys-color-primary);
  opacity: 0;
  transition: opacity var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard);
  border-radius: var(--md-sys-shape-corner-small);
}

.md-nav__link:hover::before {
  opacity: var(--md-sys-state-hover-opacity);
}

.md-nav__link:hover {
  color: var(--md-sys-color-primary);
}
```

---

**End of Plan**
