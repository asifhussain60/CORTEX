# 🎨 Level 0 Glassmorphism Standardization - Master Implementation Plan

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Date:** January 1, 2026  
**Status:** 📋 READY FOR EXECUTION  
**Orchestrator:** Planning System v4.0  
**Design Standard:** glassmorphism-design-standard.md v4.0.0

---

## ⚠️ CRITICAL: SCOPE & CONSTRAINTS

### 🛡️ SKULL Protection Rules

**Enforced Rules:**
- ✅ **NO_INLINE_STYLES**: All styling MUST use CSS classes from `glassmorphism.css`
- ✅ **RESPONSIVE_MANDATORY**: Every phase ends with responsive/mobile verification task
- ✅ **HEADER_FOOTER_STANDARD**: Standardized header/footer across all views
- ✅ **TDD_ENFORCEMENT**: Tests before implementation (RED→GREEN→REFACTOR)
- ✅ **GIT_ISOLATION**: CORTEX code never commits to user repos

### ⛔ MANDATORY PRESERVATION RULE

**ONLY THE FOLLOWING CHANGES ARE AUTHORIZED:**

✅ **ALLOWED:**
- Add new multi-panel sections for Security, Orchestrators, and Sharpen The Saw
- Extract ALL inline styles to CSS classes
- Apply `.level0-*`, `.level1-*`, `.level2-*` classes from `glassmorphism.css`
- Standardize header/footer HTML across all views
- Add responsive breakpoints and mobile-friendly layouts

❌ **FORBIDDEN:**
- Modifying or removing the **robotic splash page** (loading overlay with animated brain logo)
- Changing any existing **hero section** content or layout
- Altering the **"Built With CORTEX"** panel
- Modifying the **"The Awakening Of CORTEX"** story button
- Changing existing tile behavior for 6 standard tiles (Architecture, Token Optimization, Best Practices, Toolkit Manager, CORTEX Lens, Get Started)
- Removing or altering any working functionality
- Changing navigation, footer, or header structures beyond standardization
- Adding ANY inline `style=""` attributes to HTML elements

**Implementation Principle:** Additive only - we're inserting new panels between existing elements, not replacing or modifying them.

---

## 📋 Executive Summary

### Context
After comprehensive discovery analysis of all 9 tiles in the KEY FEATURES panel, we've determined the optimal pattern for each based on complexity, page count, and categorization potential.

### Final Tile Classification

**Multi-Panel Treatment (3 tiles):**
1. **🛡️ Security**: 13 pages, 4 categories (Protection, Assessment, Compliance, Response)
2. **🎯 Orchestrators**: 19 pages, 5 categories (Planning, Execution, System, Analysis, Debug)
3. **🔧 Sharpen The Saw**: 6 pages, 6 categories (Security, SOLID, Quality, Performance, Testing, Documentation)

**Standard Tile Treatment (6 tiles):**
4. **📚 Best Practices**: 17 knowledge domains - Scrollable Level 1 hub with domain tabs
5. **🧠 Architecture**: 5 pages (4 concepts) - Simple Level 1 hub  
6. **💰 Token Optimization**: 1 comprehensive dashboard
7. **🛠️ Toolkit Manager**: 1 page (27 tools managed via toolkit-manager/ folder)
8. **🔍 CORTEX Lens**: 1 analytical dashboard
9. **🚀 Get Started**: 1 onboarding flow page

### Design Approach

**From:** Mega-menu overlay system (original 01-master-plan.md)  
**To:** Multi-panel expansion within home page (prototype-validated)

**Rationale:**
- ✅ Prototype `home-redesign-v2.html` proves multi-panel works elegantly
- ✅ No JavaScript required (CSS-only solution)
- ✅ Better visual hierarchy (panels visible on page load)
- ✅ Simpler implementation (no overlay, no modal behavior)
- ✅ Mobile-friendly (responsive grid, no full-screen takeover)
- ✅ **ALL styles in CSS classes** - zero inline styling

---

## 🎨 Design Standards Reference

### glassmorphism-design-standard.md v4.0.0 Requirements

**View Hierarchy:** 2-Level Maximum
```
Level 0 (Home) → Level 1 (Tile Overview) → Level 2 (Component Detail)
```

**Animation Tiers:**
- **T1 (Subtle)**: ALL Level 1 & Level 2 pages - `0.2-0.3s` transitions only
- **T2 (Accent)**: Interactive element feedback - `0.1-0.2s`
- **T3 (Dramatic)**: ONLY Level 0 (docs/index.html hero) - `2-10s` keyframe animations

**Clickable vs Non-Clickable:**
- **Clickable**: Glowing border + lift (`translateY(-2px)`) + `cursor: pointer`
- **Non-Clickable**: Glass reflection (8s animation) + `cursor: default` + NO glow

**Pattern Usage:**
- **Pattern 15**: Level 0 Multi-Panel (Security, Orchestrators, STS)
- **Pattern 8-14**: Level 2 tile-specific patterns (Architecture, Orchestrators, STS, Best Practices, Toolkit, Lens, Get Started)

### Header/Footer Standardization

**All views MUST include:**

**Header (`<header class="glass-header">`):**
```html
<header class="glass-header">
    <div class="header-content">
        <h1><i class="fas fa-brain"></i> CORTEX</h1>
        <nav class="header-nav">
            <a href="index.html" class="nav-link">Home</a>
            <a href="#" class="nav-link">Documentation</a>
        </nav>
    </div>
</header>
```

**Footer (`<footer class="glass-footer">`):**
```html
<footer class="glass-footer">
    <div class="footer-content">
        <p>© 2025 Asif Hussain. All rights reserved.</p>
        <p>CORTEX v4.0 | <a href="https://github.com/asifhussain60/CORTEX">GitHub</a></p>
    </div>
</footer>
```

**CSS Classes (glassmorphism.css):**
```css
.glass-header {
    background: rgba(10, 14, 39, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
}

.glass-footer {
    background: rgba(10, 14, 39, 0.8);
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2rem;
    text-align: center;
    margin-top: 4rem;
}
```

---

## 🔍 Discovery Analysis Summary

**Methodology:** Comprehensive semantic_search + file_search analysis

**Discovery Commands Executed:**
```bash
semantic_search("architecture brain tiers SKULL protection knowledge graph")
semantic_search("security threat modeling compliance OWASP risk assessment vulnerability")
semantic_search("orchestrators planning TDD execution system cleanup debug rollback")
semantic_search("token optimization input reduction savings annual metrics")
semantic_search("sharpen the saw code quality SOLID testing performance security")
semantic_search("best practices guidelines implementation principles templates")
semantic_search("toolkit manager tool orchestration layer discovery integration")
file_search("docs/**/*.html") # 150 HTML files discovered
```

**Key Statistics:**
- Total docs/ HTML files: **150+**
- Security folder files: **13** (compliance.html, threat-modeling.html, etc.)
- Orchestrators folder files: **19** (planning-system.html, tdd-orchestrator.html, etc.)
- STS folder files: **6** (security.html, solid.html, code-quality.html, etc.)
- Knowledge library domains: **17** (engineering/, security/, testing/, performance/, etc.)
- Best practices guidelines: **35+** rules across all knowledge files

---

## 📊 Phase Breakdown

### Phase 0: CSS Foundation & Standards

**Duration:** 2 hours | **Complexity:** LOW

**Objectives:**
- Audit `glassmorphism.css` for completeness
- Add missing CSS classes for Level 0-2 patterns
- Create header/footer standard CSS classes
- Ensure responsive breakpoints defined

**Tasks:**
1. [ ] Audit existing `.level0-*`, `.level1-*`, `.level2-*` classes in `glassmorphism.css`
2. [ ] Add `.glass-header` and `.glass-footer` CSS classes
3. [ ] Add Pattern 15 (Multi-Panel) classes if missing:
   - `.level0-main-panel-wrapper`
   - `.level0-category-subpanel`
   - `.level0-category-tags` (Tetris grid)
   - `.level0-category-tag` (individual clickable link)
4. [ ] **🎨 ADD RANDOMIZED COLOR VARIATIONS:** Add 7-color system (cyan/purple/teal/indigo/pink/emerald/amber) using nth-of-type and nth-child selectors for pseudo-random distribution (see glassmorphism-design-standard.md + glass-patterns.css reference)
5. [ ] Define responsive breakpoints (768px, 640px) for all new classes
6. [ ] **VERIFY:** Zero inline styles in CSS file itself
7. [ ] **TEST:** Responsive breakpoints on mobile (375px), tablet (768px), desktop (1440px)

**Deliverables:**
- `docs/technical/assets/styles/glassmorphism.css` (updated)
- CSS audit report in `context/css-audit.md`

**Validation Gate:**
- ✅ All Pattern 15 classes present
- ✅ Randomized 7-color variation rules added (cyan/purple/teal/indigo/pink/emerald/amber)
- ✅ Header/footer classes defined
- ✅ Responsive breakpoints functional on 3 screen sizes
- ✅ Zero inline styles in CSS file

---

### Phase 1: Level 0 Multi-Panel Implementation

**Duration:** 4 hours | **Complexity:** MEDIUM

**Objectives:**
- Implement multi-panel structure for Security, Orchestrators, and STS tiles
- Replace existing single tiles with multi-panel HTML
- **ZERO inline styles** - all styling via CSS classes

**Tasks:**

#### 1.1 Security Panel (13 pages, 4 categories)
1. [ ] Remove existing Security tile HTML from `docs/index.html`
2. [ ] Add `.level0-main-panel-wrapper` container
3. [ ] Create 4 category sub-panels (`.level0-category-subpanel`):
   - **Protection** (3 pages): data-protection.html, access-control.html, audit-logging.html
   - **Assessment** (4 pages): threat-modeling.html, risk-assessment.html, vulnerability-assessment.html, penetration-testing.html
   - **Compliance** (3 pages): owasp.html, compliance.html, security-training.html
   - **Response** (3 pages): incident-response.html, threat-intelligence.html, dashboard.html
4. [ ] Add Tetris grid (`.level0-category-tags`) for each category
5. [ ] Style tags with `.level0-category-tag` class (NO inline styles)
6. [ ] **🎨 APPLY RANDOMIZED COLOR VARIATIONS:** Distribute 7 colors (cyan/purple/teal/indigo/pink/emerald/amber) pseudo-randomly across tags using nth-child selectors (see glassmorphism-design-standard.md "7-Color Anti-Monotony Pattern")
7. [ ] **VERIFY:** Zero `style=""` attributes in Security panel HTML
8. [ ] **TEST:** Security panel renders correctly on mobile (1-column), tablet (2-column), desktop (2-column)

#### 1.2 Orchestrators Panel (19 pages, 5 categories)
1. [ ] Remove existing Orchestrators tile HTML from `docs/index.html`
2. [ ] Add `.level0-main-panel-wrapper` container
3. [ ] Create 5 category sub-panels:
   - **Planning** (4 pages): planning-system.html, ado-orchestrator.html, ado-operations.html, ado-planning.html
   - **Execution** (2 pages): tdd-orchestrator.html, execution-orchestrator.html
   - **System** (4 pages): cleanup-orchestrator.html, sanitization-orchestrator.html, system-integrity.html, git-checkpoint.html
   - **Analysis** (3 pages): refinement-orchestrator.html, cortex-lens.html, architectural-review.html
   - **Debug** (2 pages): debug-orchestrator.html, rollback-orchestrator.html
4. [ ] Add Tetris grid for each category
5. [ ] Style with `.level0-category-tag` class (NO inline styles)
6. [ ] **🎨 APPLY RANDOMIZED COLOR VARIATIONS:** Use different 7-color distribution than Security panel to maximize visual variety (all 7 colors: cyan/purple/teal/indigo/pink/emerald/amber)
7. [ ] **VERIFY:** Zero `style=""` attributes in Orchestrators panel HTML
8. [ ] **TEST:** Orchestrators panel responsive on 3 screen sizes

#### 1.3 Sharpen The Saw Panel (6 pages, 6 categories)
1. [ ] Remove existing STS tile HTML from `docs/index.html`
2. [ ] Add `.level0-main-panel-wrapper` container
3. [ ] Create 6 category sub-panels (1 page each):
   - **Security**: sts/security.html
   - **SOLID**: sts/solid.html
   - **Code Quality**: sts/code-quality.html
   - **Performance**: sts/performance.html
   - **Testing**: sts/testing.html
   - **Documentation**: sts/documentation.html
4. [ ] Add Tetris grid with 1 tag per category
5. [ ] Style with `.level0-category-tag` class (NO inline styles)
6. [ ] **🎨 APPLY RANDOMIZED COLOR VARIATIONS:** Assign different color variant from 7-color palette to each of the 6 categories using pseudo-random distribution (cyan/purple/teal/indigo/pink/emerald/amber)
7. [ ] **VERIFY:** Zero `style=""` attributes in STS panel HTML
8. [ ] **TEST:** STS panel responsive on 3 screen sizes

**Deliverables:**
- `docs/index.html` (updated with 3 multi-panels)
- Inline styles report in `context/inline-styles-removed.md`

**Validation Gate:**
- ✅ All 3 panels use Pattern 15 structure
- ✅ Zero inline `style=""` attributes across all 3 panels
- ✅ All category tags link to correct Level 2 pages
- ✅ Responsive layout functional: 1-column (mobile), 2-column (tablet/desktop)
- ✅ Hover effects work: tags glow on hover, sub-panels do NOT

---

### Phase 2: Header/Footer Standardization

**Duration:** 3 hours | **Complexity:** LOW

**Objectives:**
- Add standardized glass header and footer to ALL HTML views (Level 0-2)
- Remove any existing custom headers/footers
- **ZERO inline styles** on header/footer elements

**Tasks:**

#### 2.1 Audit Existing Headers/Footers
1. [ ] Scan all 150 HTML files for existing header/footer patterns
2. [ ] Identify files with inline styles on headers/footers
3. [ ] Document custom header/footer variations in `context/header-footer-audit.md`

#### 2.2 Level 0 (Home Page)
1. [ ] Add `.glass-header` to `docs/index.html` (if missing)
2. [ ] Add `.glass-footer` to `docs/index.html` (if missing)
3. [ ] **VERIFY:** No inline styles on header/footer elements
4. [ ] **TEST:** Header sticky behavior on scroll

#### 2.3 Level 1 Pages (13 files)
**Security Level 1:**
1. [ ] Add glass header/footer to `docs/security/index.html`

**Orchestrators Level 1:**
2. [ ] Add glass header/footer to `docs/orchestrators/index.html`
3. [ ] Add glass header/footer to `docs/technical/orchestrators/index.html`

**STS Level 1:**
4. [ ] Add glass header/footer to `docs/sts/index.html`

**Other Level 1 pages:**
5. [ ] Add glass header/footer to `docs/architecture/index.html`
6. [ ] Add glass header/footer to `docs/token-optimization/index.html`
7. [ ] Add glass header/footer to `docs/knowledge/index.html`
8. [ ] Add glass header/footer to `docs/toolkit-manager/index.html`
9. [ ] Add glass header/footer to `docs/lens/index.html`
10. [ ] Add glass header/footer to `docs/roi-calculator/index.html`

**Verify:**
- [ ] **VERIFY:** Zero inline styles on ALL Level 1 headers/footers
- [ ] **TEST:** Navigation links functional across all Level 1 pages

#### 2.4 Level 2 Pages (137 files)
**Security Level 2 (13 files):**
1. [ ] Batch add glass header/footer to `docs/security/*.html` (13 files)

**Orchestrators Level 2 (19 files):**
2. [ ] Batch add glass header/footer to `docs/orchestrators/*.html` (19 files)
3. [ ] Batch add glass header/footer to `docs/technical/orchestrators/*.html`

**STS Level 2 (6 files):**
4. [ ] Batch add glass header/footer to `docs/sts/*.html` (6 files)

**Knowledge Library Level 2 (50+ files):**
5. [ ] Batch add glass header/footer to `docs/knowledge/**/*.html`

**Architecture Level 2 (4 files):**
6. [ ] Batch add glass header/footer to `docs/architecture/*.html`

**Story Pages (13 chapters):**
7. [ ] Batch add glass header/footer to `docs/story/**/index.html`

**Verify:**
- [ ] **VERIFY:** Zero inline styles on ALL Level 2 headers/footers
- [ ] **TEST:** Footer links functional across all Level 2 pages
- [ ] **TEST:** Header responsive on mobile (hamburger menu behavior if applicable)

**Deliverables:**
- All 150 HTML files updated with standardized header/footer
- Header/footer implementation report in `reports/header-footer-standardization.md`

**Validation Gate:**
- ✅ Glass header present on ALL 150 HTML files
- ✅ Glass footer present on ALL 150 HTML files
- ✅ Zero inline styles on ANY header/footer elements
- ✅ Navigation links functional
- ✅ Header sticky behavior working
- ✅ Footer copyright text accurate (© 2025 Asif Hussain)

---

### Phase 3: Inline Styles Cleanup

**Duration:** 4 hours | **Complexity:** MEDIUM

**Objectives:**
- Scan ALL HTML files for inline `style=""` attributes
- Extract inline styles to appropriate CSS classes
- Update HTML to use CSS classes instead

**Tasks:**

#### 3.1 Inline Style Detection
1. [ ] Run grep search for `style="` across `docs/**/*.html`
2. [ ] Generate inline styles inventory in `context/inline-styles-inventory.json`
3. [ ] Categorize inline styles by type (color, layout, typography, animation)
4. [ ] Identify high-frequency inline style patterns

#### 3.2 CSS Class Migration
1. [ ] For each unique inline style pattern:
   - [ ] Create appropriate CSS class in `glassmorphism.css`
   - [ ] Document class purpose and usage
   - [ ] Update HTML to use new class
2. [ ] Replace all color inline styles with CSS variables (`--accent-primary`, etc.)
3. [ ] Replace all layout inline styles with utility classes (`.flex-row`, `.grid-2col`, etc.)
4. [ ] Replace all animation inline styles with animation classes (`.fade-in`, `.slide-up`, etc.)

#### 3.3 Validation
1. [ ] Re-run grep search to confirm zero inline styles
2. [ ] Visual regression test: compare before/after screenshots for 10 sample pages
3. [ ] **VERIFY:** `grep -r 'style="' docs/` returns zero results
4. [ ] **TEST:** All pages render identically after inline style removal

**Deliverables:**
- `glassmorphism.css` (updated with new utility classes)
- Inline styles migration report in `reports/inline-styles-cleanup.md`
- Before/after screenshots in `artifacts/visual-regression/`

**Validation Gate:**
- ✅ **ZERO** inline `style=""` attributes in ANY HTML file
- ✅ All new CSS classes documented in glassmorphism-design-standard.md
- ✅ Visual regression tests pass (no visual differences)
- ✅ Page load times unchanged (<3s on 3G)

---

### Phase 4: Responsive & Mobile Verification

**Duration:** 3 hours | **Complexity:** LOW

**Objectives:**
- Test ALL views on mobile, tablet, and desktop breakpoints
- Fix responsive layout issues
- Ensure mobile-friendly interactions

**Tasks:**

#### 4.1 Multi-Panel Responsive Testing
**Security Panel:**
1. [ ] Test Security panel at 375px (mobile) - expect 1-column layout
2. [ ] Test Security panel at 768px (tablet) - expect 2-column layout
3. [ ] Test Security panel at 1440px (desktop) - expect 2-column layout
4. [ ] Fix any overflow or layout break issues

**Orchestrators Panel:**
5. [ ] Test Orchestrators panel at 375px - 1-column
6. [ ] Test Orchestrators panel at 768px - 2-column
7. [ ] Test Orchestrators panel at 1440px - 2-column
8. [ ] Fix layout issues

**STS Panel:**
9. [ ] Test STS panel at 375px - 1-column
10. [ ] Test STS panel at 768px - 2-column
11. [ ] Test STS panel at 1440px - 2-column
12. [ ] Fix layout issues

#### 4.2 Level 1 Pages Responsive Testing
1. [ ] Test 13 Level 1 pages at 375px, 768px, 1440px
2. [ ] Fix navigation menu on mobile (hamburger if needed)
3. [ ] Ensure card grids stack properly on mobile
4. [ ] **VERIFY:** All text readable without horizontal scroll

#### 4.3 Level 2 Pages Responsive Testing
1. [ ] Sample test 30 Level 2 pages (20% of 150 files)
2. [ ] Identify common responsive issues
3. [ ] Apply fixes systematically to ALL Level 2 pages
4. [ ] **VERIFY:** Code blocks don't overflow on mobile
5. [ ] **VERIFY:** Mermaid diagrams scale on mobile

#### 4.4 Touch-Friendly Interactions
1. [ ] Ensure all clickable elements have `min-height: 44px` (touch target size)
2. [ ] Test hover effects translate to tap on mobile
3. [ ] Remove `:hover` CSS for touch devices using `@media (hover: none)`
4. [ ] **TEST:** Navigation functional on iOS Safari and Android Chrome

**Deliverables:**
- Responsive test matrix in `reports/responsive-testing-matrix.md`
- Mobile screenshots in `artifacts/mobile-screenshots/`
- Responsive fixes summary in `context/responsive-fixes.md`

**Validation Gate:**
- ✅ All 3 multi-panels responsive on 375px, 768px, 1440px
- ✅ No horizontal scroll on any page at any breakpoint
- ✅ All clickable elements ≥44px touch targets
- ✅ Navigation functional on mobile devices
- ✅ Mermaid diagrams scale correctly

---

### Phase 5: Documentation Update

**Duration:** 2 hours | **Complexity:** LOW

**Objectives:**
- Update `glassmorphism-design-standard.md` with new patterns
- Document header/footer standards
- Add NO inline styles rule to standard

**Tasks:**

#### 5.1 Design Standard Updates
1. [ ] Add header/footer HTML structure to Pattern Library section
2. [ ] Add header/footer CSS classes documentation
3. [ ] Add "NO Inline Styles" rule to Core Principles section:
   ```markdown
   8. **NO Inline Styles** - All styling via CSS classes (zero tolerance for `style=""` attributes)
   ```
4. [ ] Update responsive breakpoints table with actual values used
5. [ ] Add mobile-first design section

#### 5.2 Pattern 15 Documentation
1. [ ] Add usage examples for each multi-panel category structure
2. [ ] Add Tetris grid layout documentation with `nth-child` patterns
3. [ ] Document when to use multi-panel vs standard tile (10+ pages threshold)

#### 5.3 Implementation Guide
1. [ ] Create `cortex-brain/documents/standards/glassmorphism-implementation-guide.md`
2. [ ] Include step-by-step instructions for adding new views
3. [ ] Include CSS class reference table
4. [ ] Include common patterns (header, footer, card, button, link)

**Deliverables:**
- `glassmorphism-design-standard.md` v4.1.0 (updated)
- `glassmorphism-implementation-guide.md` (new)
- Change log in `reports/design-standard-updates.md`

**Validation Gate:**
- ✅ "NO Inline Styles" rule documented
- ✅ Header/footer standards documented with code examples
- ✅ Pattern 15 fully documented with all 3 implementations
- ✅ Responsive breakpoints table complete

---

### Phase 6: Final Validation & Testing

**Duration:** 2 hours | **Complexity:** LOW

**Objectives:**
- Comprehensive validation of all requirements
- Cross-browser testing
- Performance verification

**Tasks:**

#### 6.1 SKULL Rule Compliance
1. [ ] Run grep search: `grep -r 'style="' docs/` → expect ZERO results
2. [ ] Verify all CSS classes exist in `glassmorphism.css`
3. [ ] Check for unused CSS classes
4. [ ] **VERIFY:** NO inline styles anywhere in HTML files

#### 6.2 Visual Regression Testing
1. [ ] Take screenshots of 20 sample pages (before implementation)
2. [ ] Compare with current screenshots (after implementation)
3. [ ] Document visual differences (should be minimal)
4. [ ] Fix any unintended visual changes

#### 6.3 Cross-Browser Testing
**Chrome:**
1. [ ] Test multi-panels rendering
2. [ ] Test animations (T1 subtle transitions)
3. [ ] Test responsive breakpoints

**Firefox:**
4. [ ] Test backdrop-filter support
5. [ ] Test multi-panel layout
6. [ ] Test responsive breakpoints

**Safari:**
7. [ ] Test `-webkit-backdrop-filter` support
8. [ ] Test multi-panel rendering
9. [ ] Test iOS Safari mobile view

**Edge:**
10. [ ] Test multi-panel layout
11. [ ] Test animations

#### 6.4 Performance Testing
1. [ ] Measure page load time for `docs/index.html` (<3s on 3G target)
2. [ ] Measure FPS for animations (≥60fps target)
3. [ ] Check GPU memory usage (<50MB target)
4. [ ] Run Lighthouse audit (target: >90 performance score)
5. [ ] **VERIFY:** No performance regression from inline styles removal

#### 6.5 Accessibility Testing
1. [ ] Run axe DevTools scan on all 3 multi-panels
2. [ ] Check keyboard navigation (Tab, Enter, Escape)
3. [ ] Check screen reader compatibility (NVDA/JAWS)
4. [ ] **VERIFY:** WCAG 2.1 AA compliance maintained

**Deliverables:**
- Cross-browser test matrix in `reports/cross-browser-testing.md`
- Performance test results in `reports/performance-benchmarks.md`
- Accessibility audit in `reports/accessibility-audit.md`
- Final validation checklist in `reports/final-validation.md`

**Validation Gate:**
- ✅ **ZERO inline styles** across entire docs/ folder
- ✅ All browsers render multi-panels correctly
- ✅ Page load time <3s on 3G
- ✅ Animation FPS ≥60
- ✅ Lighthouse performance score >90
- ✅ WCAG 2.1 AA compliance verified

---

## 📊 Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Inline Styles Removed | 100% (ZERO remaining) | `grep -r 'style="' docs/` |
| Header/Footer Standardization | 100% (150/150 files) | File count audit |
| Responsive Breakpoints Functional | 100% (all views) | Manual testing at 375px, 768px, 1440px |
| Multi-Panel Implementation | 100% (3/3 tiles) | Visual inspection |
| Cross-Browser Compatibility | 100% (4/4 browsers) | Manual testing |
| Page Load Time | <3s on 3G | Lighthouse audit |
| WCAG AA Compliance | 100% | axe DevTools |

---

## 🎯 Definition of Done

**All phases complete when:**
1. ✅ **ZERO** inline `style=""` attributes in ANY HTML file
2. ✅ All 150 HTML files have standardized glass header and footer
3. ✅ Security, Orchestrators, and STS use multi-panel Pattern 15
4. ✅ All views responsive on mobile (375px), tablet (768px), desktop (1440px)
5. ✅ All new CSS classes documented in glassmorphism-design-standard.md
6. ✅ Cross-browser testing passed (Chrome, Firefox, Safari, Edge)
7. ✅ Performance benchmarks met (<3s load, ≥60fps, <50MB GPU)
8. ✅ WCAG 2.1 AA accessibility compliance verified
9. ✅ Visual regression tests passed (no unintended visual changes)
10. ✅ Git commits follow SKULL rule (no CORTEX code in user repos)

---

## 📁 Deliverable Structure

```
cortex-brain/documents/planning/active/level-2-glassmorphism-standardization/
├── 00-MASTER-PLAN.md                           # This file
├── context/
│   ├── css-audit.md                            # Phase 0 CSS audit
│   ├── inline-styles-inventory.json            # Phase 3 inline styles found
│   ├── inline-styles-removed.md                # Phase 1 inline styles extracted
│   ├── header-footer-audit.md                  # Phase 2 existing headers/footers
│   └── responsive-fixes.md                     # Phase 4 responsive issues fixed
├── reports/
│   ├── header-footer-standardization.md        # Phase 2 implementation report
│   ├── inline-styles-cleanup.md                # Phase 3 cleanup report
│   ├── responsive-testing-matrix.md            # Phase 4 test results
│   ├── design-standard-updates.md              # Phase 5 change log
│   ├── cross-browser-testing.md                # Phase 6 browser compatibility
│   ├── performance-benchmarks.md               # Phase 6 performance results
│   ├── accessibility-audit.md                  # Phase 6 WCAG compliance
│   └── final-validation.md                     # Phase 6 final checklist
├── artifacts/
│   ├── visual-regression/                      # Before/after screenshots
│   │   ├── before/
│   │   └── after/
│   └── mobile-screenshots/                     # Phase 4 mobile testing
│       ├── 375px/
│       ├── 768px/
│       └── 1440px/
└── tracking/
    └── progress-tracker.json                   # Real-time progress updates
```

---

## 🔗 References

- **Design Standard:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` v4.0.0
- **Planning Orchestrator:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Prototype Reference:** `docs/prototypes/home-redesign-v2.html`
- **Current Home Page:** `docs/index.html`

---

## 📝 Notes

**Implementation Philosophy:**
- **CSS-First**: All styling through classes, zero inline styles
- **Mobile-First**: Design for 375px, enhance for larger screens
- **Progressive Enhancement**: Core functionality without JavaScript
- **Accessibility-First**: WCAG 2.1 AA from the start, not as afterthought

**Quality Gates:**
- Each phase MUST pass validation gate before proceeding
- No phase can be marked complete with failing tests
- Git commits only after phase validation passes
- SKULL rules enforced throughout (TDD, NO_INLINE_STYLES, RESPONSIVE_MANDATORY)

**Risk Mitigation:**
- Visual regression testing catches unintended changes
- Cross-browser testing prevents browser-specific bugs
- Performance testing ensures no degradation
- Accessibility audit maintains compliance

---

**End of Master Plan**
