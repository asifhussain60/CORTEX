# MkDocs Material Restyling - Feature Planning

**Feature:** Complete MkDocs documentation site restyling using Material Design CSS  
**Planning Date:** 2025-11-18  
**Status:** Active Planning  
**Complexity:** Medium  
**Estimated Duration:** 8-12 hours

---

## 🎯 Feature Overview

**Goal:** Restyle the CORTEX MkDocs documentation site (http://127.0.0.1:8000/) using Material Design CSS to create a modern, professional, and highly readable documentation experience.

**Current State Analysis:**
- **Theme:** Material theme already configured (primary: indigo, accent: purple)
- **Custom CSS:** 3 files identified:
  - `docs/stylesheets/custom.css` (753 lines) - Main custom styles
  - `docs/stylesheets/technical.css` (379 lines) - Technical sections
  - `docs/stylesheets/story.css` (458 lines) - Story sections with Comic font
- **Total Custom CSS:** ~1,590 lines of existing styles

---

## 📋 Current Configuration

### MkDocs Config (`mkdocs.yml`)
```yaml
theme:
  name: material
  palette:
    primary: indigo
    accent: purple
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.highlight
    - search.share
    - toc.follow
plugins:
  - search
  - mermaid2
markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.tabbed
  - admonition
  - attr_list
  - md_in_html
```

### Current Style Architecture

**1. Root Variables (Brand Colors)**
```css
--cortex-primary: #6366F1 (Indigo)
--cortex-accent: #8B5CF6 (Purple)
--cortex-left-brain: #3B82F6 (Blue - Tactical)
--cortex-right-brain: #A855F7 (Purple - Strategic)
```

**2. Typography Strategy**
- **Story Sections:** Comic Neue / Comic Sans MS (narrative, engaging)
- **Technical Sections:** Roboto (professional, readable)
- **Code Blocks:** Roboto Mono (monospace)

**3. Visual Hierarchy**
- **Story Sections:** White background, grey borders, clean
- **Technical Sections:** Light grey background (#F0F4F8), blue accents
- **Code Blocks:** Dark grey (#1F2937), white text

---

## 🔍 Site Structure Discovery

### Content Organization
```
docs/
├── index.md (Home page)
├── awakening-of-cortex.md (Story)
├── getting-started/ (Installation guides)
├── architecture/ (Technical architecture)
├── operations/ (Operation guides)
├── api/ (API reference)
├── reference/ (Technical references)
├── guides/ (User guides)
├── diagrams/ (Visual diagrams)
│   └── story/ (Story diagrams with Comic font)
├── plugins/ (Plugin documentation)
├── performance/ (Performance docs)
└── stylesheets/ (CSS files)
    ├── custom.css
    ├── technical.css
    └── story.css
```

---

## 🎨 CSS Files Inventory

### 1. **custom.css** (Main Stylesheet - 753 lines)

**Sections:**
- Root variables (brand colors)
- Global overrides (light Material theme)
- Typography (Comic for story, Roboto for technical)
- Story sections styling (white, clean)
- Technical sections styling (light grey, professional)
- Code blocks (dark grey background)
- Image styling (rounded, shadowed)
- Hemisphere badges (left/right brain visual identifiers)
- Admonitions (note, warning, success, info)
- Tables (clean, gradient header)
- Navigation (colorful sidebar, gradient backgrounds)
- Home page hero section
- Chapter markers
- Responsive design (mobile-friendly)
- Custom scrollbar
- Ancient rules styling (special serif fonts)
- **Recent Fix:** Sticky header padding to prevent logo cutoff

**Key Features:**
- Gradient backgrounds on navigation
- Colorful active states
- Smooth transitions
- Box shadows for depth
- Material Design influences already present

---

### 2. **technical.css** (Technical Sections - 379 lines)

**Purpose:** Professional, boxed technical content with clear visual separation

**Sections:**
- Technical typography (Roboto)
- Technical headers (blue theme)
- Code blocks (prominent, easy to scan)
- Structured lists
- Data tables
- Admonitions (call-outs)
- Technical diagrams
- API reference styling
- Parameter tables
- Technical sidebar
- Responsive design
- Print styles

**Color Scheme:**
- Headers: Deep blue (#1e40af), Blue (#3b82f6), Light blue (#60a5fa)
- Text: Dark grey (#1e293b)
- Backgrounds: Light greys (#f1f5f9, #f8fafc)

---

### 3. **story.css** (Story Sections - 458 lines)

**Purpose:** Comic font and engaging story presentation

**Sections:**
- Comic Neue font import
- Auto-apply to `/diagrams/story/` paths
- Story headers (grey theme)
- Story emphasis (italics, bold)
- Quotes (narrator voice, character dialogue)
- Story lists
- Part/chapter headers
- Interludes (technical recaps in story format)
- Fun fact callouts
- Story images
- Content transitions
- Responsive design
- Print styles
- Storybook enhancements (chapter openings, realizations, system birth, scene breaks, dialogue, pull quotes)

**Color Scheme:**
- Headers: Dark grey (#2c3e50), Medium grey (#34495e)
- Text: Dark grey (#333333)
- Backgrounds: White (#ffffff), Light grey (#f8f9fa)

---

## 🚨 Known Issues (From Current CSS)

### 1. **Sticky Header Logo Cutoff**
**Status:** Fixed in custom.css (lines 553-593)
- Added padding to prevent header content cutoff
- Ensured logo has proper spacing
- Added white space margin between header and content

### 2. **Sidebar Overlap (Mobile)**
**Status:** Fixed with responsive design (lines 526-551)
- Collapses sidebar on mobile
- Prevents content overlap

### 3. **Black Bar in Navigation**
**Status:** Removed (lines 348-364)
- Hidden repository source link area
- Hidden sidebar header

---

## 🎯 Material Design Enhancement Goals

### Phase 1: Material Design Foundation (4-5 hours)

**Objective:** Implement Material Design 3 principles while preserving existing functionality

**Tasks:**
1. ☐ **Material Design Tokens**
   - Define Material Design 3 color tokens
   - Update CSS custom properties
   - Maintain CORTEX brand identity (indigo/purple)

2. ☐ **Elevation System**
   - Implement Material elevation levels (0-5)
   - Replace box-shadows with Material elevation
   - Add elevation states (hover, active, focus)

3. ☐ **Typography Scale**
   - Implement Material typography scale
   - Maintain Comic font for story (unique CORTEX identity)
   - Ensure readability across devices

4. ☐ **Color System**
   - Primary: Keep indigo (#6366F1)
   - Secondary: Keep purple (#8B5CF6)
   - Surface colors: Update to Material Design 3
   - On-surface colors: Ensure contrast ratios

5. ☐ **Spacing System**
   - Implement 8dp grid system
   - Update padding/margin to multiples of 8
   - Ensure consistent spacing across components

**Material Design 3 References:**
- Color system: Surface, on-surface, surface-variant
- Elevation: 0 (flat), 1, 2, 3, 4, 5 (raised)
- Typography: Display, headline, title, body, label
- Spacing: 8dp grid (4dp, 8dp, 12dp, 16dp, 24dp, 32dp, 48dp, 64dp)

---

### Phase 2: Component Updates (3-4 hours)

**Objective:** Update individual components to Material Design standards

**Tasks:**
1. ☐ **Navigation Drawer**
   - Material elevation (level 1)
   - State layers (hover, active)
   - Ripple effects on items
   - Section dividers (Material style)

2. ☐ **Cards (Story/Technical Sections)**
   - Material card component
   - Elevation on hover
   - Action areas with state layers
   - Consistent card styling

3. ☐ **Buttons (Call-to-Action)**
   - Filled buttons (primary actions)
   - Outlined buttons (secondary actions)
   - Text buttons (tertiary actions)
   - State layers (hover, focus, active)

4. ☐ **Tables**
   - Material data table styling
   - Sortable headers (visual indicators)
   - Row hover states
   - Pagination styling (if applicable)

5. ☐ **Code Blocks**
   - Material surface-variant background
   - Maintain dark theme for code
   - Syntax highlighting colors
   - Copy button styling

6. ☐ **Admonitions**
   - Material callout styling
   - Icon integration
   - Color-coded by type (info, warning, danger, success)
   - Elevation level 1

---

### Phase 3: Animations & Interactions (2-3 hours)

**Objective:** Add Material motion and micro-interactions

**Tasks:**
1. ☐ **Transitions**
   - Duration tokens (short: 150ms, medium: 250ms, long: 400ms)
   - Easing functions (standard, emphasized, decelerated)
   - Navigation transitions
   - Card hover transitions

2. ☐ **State Layers**
   - Hover state (8% opacity)
   - Focus state (12% opacity)
   - Press state (12% opacity)
   - Apply to interactive elements

3. ☐ **Scroll Behaviors**
   - Smooth scrolling
   - Scroll-triggered animations (fade-in)
   - Sticky header behavior
   - Back-to-top button with Material FAB styling

4. ☐ **Loading States**
   - Skeleton screens for content loading
   - Progress indicators (linear, circular)
   - Material shimmer effect

---

### Phase 4: Accessibility & Refinement (1-2 hours)

**Objective:** Ensure WCAG 2.1 AA compliance and polish

**Tasks:**
1. ☐ **Contrast Ratios**
   - Verify all text meets 4.5:1 (normal text)
   - Verify large text meets 3:1
   - Update colors if needed

2. ☐ **Focus Indicators**
   - Material focus ring (3px, primary color)
   - Visible on all interactive elements
   - Keyboard navigation support

3. ☐ **ARIA Labels**
   - Add aria-labels to icon buttons
   - Add aria-current to active navigation
   - Semantic HTML structure

4. ☐ **Dark Mode Support** (Optional)
   - Define dark theme tokens
   - Toggle mechanism
   - Preserve dark code blocks

5. ☐ **Performance**
   - Minimize CSS file sizes
   - Remove unused styles
   - Optimize animations (GPU acceleration)

---

## 📦 Material Design CSS Resources

### Official Material Design 3
- **Material Design 3:** https://m3.material.io/
- **Color System:** https://m3.material.io/styles/color/overview
- **Typography:** https://m3.material.io/styles/typography/overview
- **Elevation:** https://m3.material.io/styles/elevation/overview

### Material Components Web (MDC)
- **GitHub:** https://github.com/material-components/material-components-web
- **CSS Framework:** Can import specific components
- **Customize:** Use CSS custom properties

### MkDocs Material Theme Extensions
- **Current Theme:** Already uses Material theme
- **Customization:** Override via extra_css
- **Components:** Navigation, search, content areas

---

## 🔧 Implementation Strategy

### Approach 1: Incremental Enhancement (Recommended)

**Pros:**
- Low risk (preserve existing functionality)
- Test changes incrementally
- Easier debugging
- Rollback if issues

**Cons:**
- Slower overall progress
- May have inconsistent styling during transition

**Process:**
1. Phase 1 → Test → Commit
2. Phase 2 → Test → Commit
3. Phase 3 → Test → Commit
4. Phase 4 → Test → Final commit

---

### Approach 2: Full Rewrite

**Pros:**
- Clean slate (consistent from start)
- Remove legacy styles
- Optimize for Material Design 3

**Cons:**
- High risk (may break existing layout)
- Difficult debugging
- Requires extensive testing
- Longer rollback if issues

**Process:**
1. Backup current CSS
2. Rewrite all CSS with Material Design 3
3. Extensive testing phase
4. Single large commit

---

## 🎨 Material Design Best Practices

### 1. **Color Usage**
- **Primary:** Main brand color (indigo) - use sparingly for key actions
- **Secondary:** Accent color (purple) - use for less prominent actions
- **Surface:** Background colors - use extensively
- **On-Surface:** Text colors - ensure contrast

### 2. **Elevation**
- **Level 0:** Default surface (no shadow)
- **Level 1:** Cards, navigation drawer
- **Level 2:** Raised buttons, app bar (scrolled)
- **Level 3:** Modal dialogs
- **Level 4:** Navigation drawer (modal)
- **Level 5:** Snackbar (highest)

### 3. **Typography**
- **Display:** Largest, most prominent (hero titles)
- **Headline:** Section titles
- **Title:** Card titles, list headers
- **Body:** Paragraph text (most common)
- **Label:** Buttons, tabs, small UI elements

### 4. **Spacing**
- Use 8dp grid (4, 8, 12, 16, 24, 32, 48, 64)
- Consistent padding/margin across components
- Whitespace for visual breathing room

---

## ⚠️ Risks & Mitigation

### Risk 1: Breaking Existing Layout
**Probability:** Medium  
**Impact:** High  
**Mitigation:**
- Use incremental approach (Phase by Phase)
- Test on localhost before committing
- Keep backup of current CSS
- Use Git branches for experimentation

---

### Risk 2: Comic Font Loss for Story Sections
**Probability:** Low  
**Impact:** High (unique CORTEX identity)  
**Mitigation:**
- Explicitly preserve Comic font in story.css
- Test story pages after each phase
- Add CSS comments marking "DO NOT REMOVE"

---

### Risk 3: Performance Degradation
**Probability:** Low  
**Impact:** Medium  
**Mitigation:**
- Monitor CSS file sizes
- Remove unused styles
- Optimize animations (use transform/opacity only)
- Test on mobile devices

---

### Risk 4: Accessibility Regression
**Probability:** Low  
**Impact:** High  
**Mitigation:**
- Verify contrast ratios with tools
- Test keyboard navigation
- Use semantic HTML
- Add ARIA labels where needed

---

## 📊 Success Criteria

### Phase 1 Complete When:
- ✅ Material Design tokens defined
- ✅ Elevation system implemented
- ✅ Typography scale applied
- ✅ Color system updated
- ✅ Spacing system consistent
- ✅ All pages render correctly
- ✅ No visual regressions

---

### Phase 2 Complete When:
- ✅ Navigation drawer uses Material styling
- ✅ Cards (story/technical) are Material cards
- ✅ Buttons use Material button styles
- ✅ Tables use Material data table styling
- ✅ Code blocks maintain readability
- ✅ Admonitions are Material callouts
- ✅ All interactive elements have state layers

---

### Phase 3 Complete When:
- ✅ Transitions use Material duration tokens
- ✅ Easing functions applied
- ✅ State layers on all interactive elements
- ✅ Smooth scroll behaviors
- ✅ Loading states implemented
- ✅ Animations perform well (60fps)

---

### Phase 4 Complete When:
- ✅ WCAG 2.1 AA contrast ratios verified
- ✅ Focus indicators visible on all elements
- ✅ ARIA labels added
- ✅ Keyboard navigation works
- ✅ CSS optimized (unused styles removed)
- ✅ Performance benchmarks met

---

## 🔍 Next Steps

### Immediate Actions

**1. Verify Site Accessibility**
```bash
# Check if MkDocs server is running
curl http://127.0.0.1:8000/
```

**2. Backup Current CSS**
```bash
# Create backup before making changes
cp -r docs/stylesheets docs/stylesheets-backup-2025-11-18
```

**3. Create Material Design Tokens File**
```bash
# New file for Material Design 3 tokens
touch docs/stylesheets/material-tokens.css
```

**4. Update mkdocs.yml**
```yaml
extra_css:
  - stylesheets/material-tokens.css  # NEW: Material Design tokens
  - stylesheets/custom.css
  - stylesheets/technical.css
  - stylesheets/story.css
```

---

### Vision API Crawl Plan (For Detailed Analysis)

**Note:** Vision API analysis requires MkDocs server running and accessible at http://127.0.0.1:8000/

**Pages to Crawl:**
1. **Home Page** (`/`) - Hero section, navigation, overall layout
2. **Story Pages** (`/diagrams/story/*`) - Comic font, narrative styling
3. **Technical Pages** (`/architecture/*`, `/api/*`) - Professional styling
4. **Operations Pages** (`/operations/*`) - Guides and references
5. **Getting Started** (`/getting-started/*`) - Installation, setup

**Vision Analysis Focus:**
- Layout consistency across page types
- Color usage and brand consistency
- Typography hierarchy
- Interactive element styling
- Mobile responsiveness
- Accessibility concerns (contrast, focus states)

**To Enable Vision Crawl:**
```bash
# 1. Start MkDocs server (if not running)
mkdocs serve

# 2. Verify accessibility
curl http://127.0.0.1:8000/

# 3. Request CORTEX vision analysis
# (User will request vision crawl separately)
```

---

## 📝 Manual CSS Update Checklist

If updating CSS files manually, follow this order:

### custom.css Updates
- [ ] Update root variables with Material Design tokens
- [ ] Replace box-shadows with elevation classes
- [ ] Update typography to Material scale
- [ ] Apply 8dp spacing system
- [ ] Add state layers to interactive elements
- [ ] Update navigation drawer styling
- [ ] Apply Material button styles
- [ ] Update card styling
- [ ] Ensure responsive design maintained

---

### technical.css Updates
- [ ] Update headers with Material typography
- [ ] Apply Material data table styling
- [ ] Update code block styling (preserve dark theme)
- [ ] Apply Material admonition styles
- [ ] Ensure API reference sections use Material components
- [ ] Update sidebar styling

---

### story.css Updates
- [ ] **PRESERVE Comic font** (critical for CORTEX identity)
- [ ] Update story headers with Material typography scale
- [ ] Apply Material card styling to story sections
- [ ] Update blockquote styling
- [ ] Ensure transitions use Material motion tokens
- [ ] Preserve narrative, engaging feel

---

## 🎯 Recommended Starting Point

**Best Way to Begin:**

1. **Phase 1.1: Material Design Tokens**
   - Create `material-tokens.css`
   - Define Material Design 3 color tokens
   - Define elevation tokens
   - Define typography tokens
   - Define spacing tokens

2. **Phase 1.2: Apply Tokens to custom.css**
   - Replace hardcoded colors with tokens
   - Replace box-shadows with elevation
   - Update typography to use scale
   - Apply spacing system

3. **Phase 1.3: Test on localhost**
   - Visual regression check
   - Verify Comic font preserved
   - Check mobile responsiveness
   - Validate accessibility

4. **Phase 1.4: Commit**
   - Git commit with descriptive message
   - Document changes in commit message

---

## 📚 Additional Resources

### Material Design Documentation
- **Material Design 3 Guidelines:** https://m3.material.io/
- **Components:** https://m3.material.io/components
- **Foundations:** https://m3.material.io/foundations

### Tools
- **Color Tool:** https://m3.material.io/theme-builder (Generate Material theme)
- **Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **Lighthouse:** Chrome DevTools (Accessibility audit)

### MkDocs Material
- **Customization Guide:** https://squidfunk.github.io/mkdocs-material/customization/
- **CSS Variables:** https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/

---

## 🏁 Approval & Sign-Off

**Planning Status:** Complete ✅  
**Ready for Implementation:** Pending user approval  
**Estimated Total Time:** 8-12 hours (across 4 phases)

**Next Action:** 
- User reviews plan
- User approves phases or requests modifications
- User initiates Phase 1 implementation
- Optional: User requests Vision API crawl for detailed page analysis

---

**Document Created:** 2025-11-18  
**Last Updated:** 2025-11-18  
**Version:** 1.0  
**Status:** Active Planning
