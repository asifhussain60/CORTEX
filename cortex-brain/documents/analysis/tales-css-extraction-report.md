# Tales CSS Extraction Report

**Date:** 2025-11-18  
**Source:** workspace/Tales/Tales-3.3.6-v3/HTML  
**Target:** CORTEX MkDocs Documentation  
**Analyst:** CORTEX Enterprise Document Generator

---

## 🎨 Design Token Analysis

### Color Palette (Elegant Blue Theme)

**Primary Colors:**
- **Brand Blue:** `#425c75` (masthead, footer backgrounds)
- **Brand Blue Light:** `#57718a` (subheader, hover states)
- **Accent Blue:** `#425c75` (links primary)
- **Accent Blue Hover:** `#57718a` (links hover)

**Neutral Colors:**
- **Background:** `#fafafa` (page background, light grey)
- **Text Primary:** `#303233` (body text, dark grey)
- **Text Light:** `#f8f8f9` (masthead text, near white)
- **Text Muted:** `#dadada` (subheader text)
- **Border:** `#cbc8c2` (hr lines)
- **Selection:** `#494c4d` (text selection background)

**Shadow:**
- **Box Shadow:** `inset 1px 10px 8px -8px #d6d6d6` (top shadow for main content)

---

### Typography

**Font Families:**
- **Body:** `'Open Sans', sans-serif` (16px, line-height 27px)
- **Headings:** `'PT Serif', serif` (elegant serif for H1, logo)
- **H2-H3:** `'Open Sans', sans-serif` (consistency with body)

**Type Scale:**
- **H1:** 45px / 60px line-height (large titles)
- **H2:** 30px / 40px line-height (section headers)
- **H3:** 21px / 30px line-height (subsections)
- **Body:** 16px / 27px line-height (comfortable reading)
- **Footer:** 14px (smaller text)

**Font Awesome Icons:**
- Size: 24px default

---

### Spacing & Layout

**Masthead Padding:**
- Top: 55px
- Bottom: 55px

**Subheader Height:**
- Min-height: 63px

**Logo:**
- Font-size: 39px
- Margin-top: 10px (alignment)

---

### Component Styles

**Links:**
- Default: `#425c75`
- Hover/Focus: `#57718a`, no underline

**Selection:**
- Background: `#494c4d`
- Text: `#fafafa`

**Widewrappers (Full-width sections):**
- `.widewrapper.masthead` - Blue header (`#425c75`)
- `.widewrapper.subheader` - Light blue breadcrumb bar (`#57718a`)
- `.widewrapper.main` - Content area with top shadow
- `.widewrapper.footer` - Blue footer (`#425c75`)

**Navigation:**
- Float right in masthead
- Bootstrap nav pills
- Dropdown support
- Mobile nav toggle (hamburger icon)

---

## 🔄 Migration Strategy

### Phase 1: Extract & Adapt Core Design Tokens

**Create `tales-design-tokens.css`:**

```css
/* Tales Design Tokens - Adapted for CORTEX MkDocs */

:root {
  /* Color Palette */
  --tales-brand-blue: #425c75;
  --tales-brand-blue-light: #57718a;
  --tales-background: #fafafa;
  --tales-text-primary: #303233;
  --tales-text-light: #f8f8f9;
  --tales-text-muted: #dadada;
  --tales-border: #cbc8c2;
  --tales-selection-bg: #494c4d;
  --tales-selection-text: #fafafa;
  --tales-shadow: inset 1px 10px 8px -8px #d6d6d6;
  
  /* Typography */
  --tales-font-body: 'Open Sans', sans-serif;
  --tales-font-heading: 'PT Serif', serif;
  --tales-font-size-base: 16px;
  --tales-line-height-base: 27px;
  --tales-font-size-h1: 45px;
  --tales-line-height-h1: 60px;
  --tales-font-size-h2: 30px;
  --tales-line-height-h2: 40px;
  --tales-font-size-h3: 21px;
  --tales-line-height-h3: 30px;
  
  /* Spacing */
  --tales-spacing-xl: 55px;
  --tales-spacing-md: 30px;
  --tales-spacing-sm: 10px;
}
```

### Phase 2: Map to MkDocs Material Selectors

**Header/Navigation:**
- `.widewrapper.masthead` → `.md-header`
- `.tales-nav` → `.md-tabs`, `.md-nav--primary`

**Content:**
- `.widewrapper.main` → `.md-content`
- `.blog-teaser` → `.md-typeset article` (for story chapters)

**Footer:**
- `.widewrapper.footer` → `.md-footer`

**Links:**
- `a` → `.md-typeset a`

**Selection:**
- `::selection` → Keep as global

### Phase 3: Selective Style Application

**✅ Adopt from Tales:**
- Color palette (blue/grey professional look)
- Typography scale (PT Serif for headings adds elegance)
- Spacing system (55px padding feels generous)
- Box shadow on content area (subtle depth)
- Selection colors (nice contrast)

**❌ Preserve from CORTEX:**
- Comic Sans MS for story sections (brand identity)
- Ancient Rules styling with Cinzel font
- Gradient backgrounds (left/right brain visual)
- CORTEX color tokens (#6366F1 indigo, #8B5CF6 purple)

**🔀 Hybrid Approach:**
- Use Tales blue palette for technical docs
- Use CORTEX gradient/purple for story sections
- Tales typography for body text, CORTEX fonts for brand elements

---

## 📦 Implementation Files

### New Files to Create:
1. `docs/stylesheets/tales-tokens.css` (design tokens)
2. `docs/stylesheets/tales-adapted.css` (MkDocs-adapted styles)

### Files to Update:
1. `mkdocs.yml` - Add new stylesheets
2. `docs/stylesheets/custom.css` - Integrate Tales tokens
3. `docs/stylesheets/technical.css` - Apply Tales professional look
4. `docs/stylesheets/story.css` - Preserve CORTEX identity, use Tales spacing

---

## 🎯 Expected Results

**Before (Current CORTEX):**
- Gradient backgrounds (nice!)
- Mixed spacing values (inconsistent)
- Limited typography scale
- Custom colors (CORTEX brand)

**After (Tales Integration):**
- Elegant blue professional look for technical docs
- Consistent spacing system (55px, 30px, 10px grid)
- PT Serif headings add polish
- CORTEX brand preserved for story sections
- Better contrast and readability

**Performance Impact:**
- +200 lines of CSS (~15KB)
- New Google Fonts (Open Sans, PT Serif): ~50KB
- Total: ~65KB increase
- Trade-off: Professional look worth the cost

---

## ✅ Next Steps

1. **Create tales-tokens.css** with extracted design tokens
2. **Test color palette** on a sample page (verify contrast, accessibility)
3. **Apply to technical.css** first (low risk - preserve story.css)
4. **Update mkdocs.yml** to include new stylesheets
5. **Test on localhost** (verify no visual regressions)
6. **Iterate** based on feedback

**Estimated Time:** 3-4 hours for complete integration

---

**Generated:** 2025-11-18  
**Status:** Ready for Phase 1 implementation  
**Approval:** Pending user review
