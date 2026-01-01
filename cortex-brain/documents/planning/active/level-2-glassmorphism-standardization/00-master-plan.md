# 🎨 Level 0-2 Glassmorphism Standardization - Master Implementation Plan

**Version:** 4.1.0 AUTONOMOUS-READY  
**Author:** Asif Hussain  
**Date:** January 1, 2026  
**Status:** 🛡️ READY FOR AUTONOMOUS EXECUTION  
**Orchestrator:** Planning System v4.0  
**Design Standard:** glassmorphism-design-standard.md v4.0.0  
**Scope:** ALL Level 0, Level 1, Level 2 views (NO Level 3)

---

## ⚠️ CRITICAL: SCOPE & CONSTRAINTS

### 🎯 View Hierarchy Enforcement

**MANDATORY STRUCTURE:**
```
Level 0 (Home: docs/index.html) 
    ↓
Level 1 (Tile Index: 13 hub pages)
    ↓
Level 2 (Detail Pages: 137 component pages)
    ↓
⛔ NO LEVEL 3 (Use expandable sections, tabs, or modals instead)
```

**Level 0:** Single home page (`docs/index.html`)
- 9 tiles (3 multi-panel, 6 standard)
- Standardized header with CORTEX logo
- Standardized footer with copyright

**Level 1:** 13 hub/index pages
- Security, Orchestrators, Architecture, Token Optimization, STS, Best Practices, etc.
- MUST have standardized header (beginning at Level 1)
- MUST have standardized footer
- T1 subtle animations ONLY

**Level 2:** 137 detail pages
- Specific components, guidelines, orchestrators
- MUST have standardized header
- MUST have standardized footer
- T1 subtle animations ONLY
- NO Level 3 navigation

### 🛡️ SKULL Protection Rules

**Enforced Rules:**
- ✅ **NO_INLINE_STYLES**: All styling MUST use CSS classes from `glassmorphism.css`
- ✅ **RESPONSIVE_MANDATORY**: Every phase ends with responsive/mobile verification task
- ✅ **HEADER_FOOTER_STANDARD**: Standardized header (beginning at Level 1) and footer across ALL views
- ✅ **TDD_ENFORCEMENT**: Tests before implementation (RED→GREEN→REFACTOR)
- ✅ **GIT_ISOLATION**: CORTEX code never commits to user repos
- ✅ **NO_LEVEL_3**: All navigation stops at Level 2, use expandable sections for deeper content
- ✅ **CREATE_FROM_SCRATCH**: All Level 1 & Level 2 views rebuilt from scratch (avoid modification/duplication)

### ⛔ MANDATORY PRESERVATION & CREATION RULES

**LEVEL 0 CHANGES (Additive Only):**

✅ **ALLOWED:**
- Add new multi-panel sections for Security, Orchestrators, and Sharpen The Saw
- Extract ALL inline styles to CSS classes
- Apply `.level0-*`, `.level1-*`, `.level2-*` classes from `glassmorphism.css`
- Standardize header/footer HTML (header begins at Level 1, footer on all levels)
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

**LEVEL 1 & LEVEL 2 IMPLEMENTATION (Create from Scratch):**

✅ **REQUIRED APPROACH:**
- **CREATE NEW:** All Level 1 and Level 2 views MUST be created from scratch
- **DISCOVERY FIRST:** Each phase begins with discovery to capture enhancements and existing content
- **AVOID MODIFICATION:** Do NOT attempt to modify existing views (prevents duplication and breakage)
- **TEMPLATE-BASED:** Use standardized HTML templates with glass header/footer
- **CSS CLASSES ONLY:** Zero inline styles in new views
- **NO LEVEL 3:** All detail content fits within Level 2, use tabs/accordions for depth

**Implementation Principle:** 
- Level 0: Additive only - insert new panels between existing elements
- Level 1 & 2: Rebuild from scratch - ensure clean, standardized structure without legacy issues

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

### Phase 0: Discovery & CSS Foundation

**Duration:** 3 hours | **Complexity:** MEDIUM

**Objectives:**
- **DISCOVERY FIRST:** Audit all existing HTML views to capture enhancements and structure
- Audit `glassmorphism.css` for completeness
- Add missing CSS classes for Level 0-2 patterns
- Create header/footer standard CSS classes
- Ensure responsive breakpoints defined

**Tasks:**

#### 0.1 Comprehensive View Discovery
1. [ ] Scan all `docs/**/*.html` files and categorize by level
2. [ ] Identify existing Level 1 hub pages (13 expected)
3. [ ] Identify existing Level 2 detail pages (137 expected)
4. [ ] Document any Level 3 views that need to be collapsed into Level 2
5. [ ] Capture content structure, navigation patterns, and unique features
6. [ ] Generate discovery report: `context/view-hierarchy-audit.md`

#### 0.2 CSS Audit & Enhancement
7. [ ] Audit existing `.level0-*`, `.level1-*`, `.level2-*` classes in `glassmorphism.css`
8. [ ] Add `.glass-header` and `.glass-footer` CSS classes (if missing)
9. [ ] Add Pattern 15 (Multi-Panel) classes if missing:
   - `.level0-main-panel-wrapper`
   - `.level0-category-subpanel`
   - `.level0-category-tags` (Tetris grid)
   - `.level0-category-tag` (individual clickable link)
10. [ ] **🎨 ADD RANDOMIZED COLOR VARIATIONS:** Add 7-color system (cyan/purple/teal/indigo/pink/emerald/amber) using nth-of-type and nth-child selectors for pseudo-random distribution
11. [ ] Define responsive breakpoints (768px, 640px) for all new classes
12. [ ] **VERIFY:** Zero inline styles in CSS file itself
13. [ ] **TEST:** Responsive breakpoints on mobile (375px), tablet (768px), desktop (1440px)

**Deliverables:**
- `context/view-hierarchy-audit.md` (NEW - discovery report)
- `docs/technical/assets/styles/glassmorphism.css` (updated)
- `context/css-audit.md` (CSS completeness report)

**Validation Gate:**
- ✅ Discovery report documents all 150 HTML files with level classification
- ✅ All Level 3 views identified for consolidation
- ✅ All Pattern 15 classes present
- ✅ Randomized 7-color variation rules added
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

### Phase 2: Level 1 Views - Create from Scratch

**Duration:** 8 hours | **Complexity:** HIGH

**Objectives:**
- **CREATE NEW:** Build all 13 Level 1 hub/index pages from scratch
- **DISCOVERY-DRIVEN:** Use Phase 0 discovery to ensure no content loss
- Add standardized glass header (beginning at Level 1) and footer to ALL Level 1 views
- Apply T1 subtle animations only
- **ZERO inline styles** on all new Level 1 views
- Ensure NO Level 3 navigation exists

**Tasks:**

#### 2.1 Discovery Review
1. [ ] Review `context/view-hierarchy-audit.md` for Level 1 content requirements
2. [ ] Identify enhancement opportunities for each Level 1 hub
3. [ ] Document navigation structure for each hub

#### 2.2 Create Level 1 Template
4. [ ] Create standardized Level 1 HTML template with:
   - Glass header (`.glass-header`) with CORTEX logo
   - Glass footer (`.glass-footer`)
   - T1 animation classes only
   - Responsive grid structure
   - Zero inline styles
5. [ ] **VERIFY:** Template validated against glassmorphism-design-standard.md

#### 2.3 Build Level 1 Hub Pages (Create from Scratch)

**Security Level 1:**
6. [ ] **CREATE NEW:** `docs/security/index.html` (hub for 13 detail pages, 4 categories)
   - Header with CORTEX logo
   - Category navigation (Protection, Assessment, Compliance, Response)
   - Links to all 13 Level 2 pages
   - Footer
   - Zero inline styles

**Orchestrators Level 1:**
7. [ ] **CREATE NEW:** `docs/orchestrators/index.html` (hub for 19 detail pages, 5 categories)
   - Header with CORTEX logo
   - Category navigation (Planning, Execution, System, Analysis, Debug)
   - Links to all 19 Level 2 pages
   - Footer
   - Zero inline styles

**STS Level 1:**
8. [ ] **CREATE NEW:** `docs/sts/index.html` (hub for 6 detail pages)
   - Header with CORTEX logo
   - Category navigation (Security, SOLID, Quality, Performance, Testing, Docs)
   - Links to all 6 Level 2 pages
   - Footer
   - Zero inline styles

**Other Level 1 Hubs (10 pages):**
9. [ ] **CREATE NEW:** `docs/architecture/index.html` (hub for 4 concept pages)
10. [ ] **CREATE NEW:** `docs/token-optimization/index.html` (hub for 3 pages)
11. [ ] **CREATE NEW:** `docs/knowledge/index.html` (hub for 50+ domain pages)
12. [ ] **CREATE NEW:** `docs/toolkit-manager/index.html` (hub for toolkit catalog)
13. [ ] **CREATE NEW:** `docs/lens/index.html` (hub for CORTEX Lens features)
14. [ ] **CREATE NEW:** `docs/roi-calculator/index.html` (if separate hub needed)
15. [ ] **CREATE NEW:** `docs/best-practices/index.html` (hub for 35 guidelines)
16. [ ] **CREATE NEW:** `docs/get-started/index.html` (onboarding hub)
17. [ ] **CREATE NEW:** `docs/story/index.html` (Awakening story hub)

#### 2.4 Level 3 Elimination
18. [ ] Review all Level 1 hubs for any Level 3 links
19. [ ] Consolidate Level 3 content into Level 2 using tabs/accordions
20. [ ] **VERIFY:** No navigation exists beyond Level 2

#### 2.5 Validation
21. [ ] **VERIFY:** All 13 Level 1 hubs have standardized header with CORTEX logo
22. [ ] **VERIFY:** All 13 Level 1 hubs have standardized footer
23. [ ] **VERIFY:** Zero inline styles on ALL Level 1 pages
24. [ ] **VERIFY:** T1 animations only (no T3 dramatic animations)
25. [ ] **TEST:** Navigation functional from Level 0 to Level 1 to Level 2
26. [ ] **TEST:** Responsive on mobile (375px), tablet (768px), desktop (1440px)

**Deliverables:**
- 13 new Level 1 HTML files created from scratch
- Level 1 template in `templates/level1-template.html`
- Level 1 creation report in `reports/level1-creation.md`

**Validation Gate:**
- ✅ All 13 Level 1 hubs created from scratch (not modified)
- ✅ Glass header present with CORTEX logo on ALL Level 1 pages
- ✅ Glass footer present on ALL Level 1 pages
- ✅ Zero inline styles on ANY Level 1 page
- ✅ Navigation functional from home → Level 1 → Level 2
- ✅ NO Level 3 navigation exists
- ✅ Responsive layout functional: 1-column (mobile), 2-3 column (tablet/desktop)

---

### Phase 3: Level 2 Views - Create from Scratch

**Duration:** 16 hours | **Complexity:** VERY HIGH

**Objectives:**
- **CREATE NEW:** Build all 137 Level 2 detail pages from scratch
- **DISCOVERY-DRIVEN:** Use Phase 0 discovery to ensure content completeness
- Add standardized glass header and footer to ALL Level 2 views
- Apply T1 subtle animations only
- **ZERO inline styles** on all new Level 2 views
- Ensure content depth uses tabs/accordions, NOT Level 3 pages

**Tasks:**

#### 3.1 Discovery Review
1. [ ] Review `context/view-hierarchy-audit.md` for Level 2 content requirements
2. [ ] Identify Level 3 content that needs consolidation into Level 2
3. [ ] Document tab/accordion structure for complex Level 2 pages

#### 3.2 Create Level 2 Template
4. [ ] Create standardized Level 2 HTML template with:
   - Glass header (`.glass-header`) with CORTEX logo
   - Glass footer (`.glass-footer`)
   - T1 animation classes only
   - Tab/accordion structure for deep content
   - Responsive layout
   - Zero inline styles
5. [ ] **VERIFY:** Template validated against glassmorphism-design-standard.md

#### 3.3 Build Level 2 Detail Pages by Category (Create from Scratch)

**Security Level 2 (13 files):**
6. [ ] **CREATE NEW:** `docs/security/data-protection.html`
7. [ ] **CREATE NEW:** `docs/security/access-control.html`
8. [ ] **CREATE NEW:** `docs/security/audit-logging.html`
9. [ ] **CREATE NEW:** `docs/security/threat-modeling.html`
10. [ ] **CREATE NEW:** `docs/security/risk-assessment.html`
11. [ ] **CREATE NEW:** `docs/security/vulnerability-assessment.html`
12. [ ] **CREATE NEW:** `docs/security/penetration-testing.html`
13. [ ] **CREATE NEW:** `docs/security/owasp.html`
14. [ ] **CREATE NEW:** `docs/security/compliance.html`
15. [ ] **CREATE NEW:** `docs/security/security-training.html`
16. [ ] **CREATE NEW:** `docs/security/incident-response.html`
17. [ ] **CREATE NEW:** `docs/security/threat-intelligence.html`
18. [ ] **CREATE NEW:** `docs/security/dashboard.html`

**Orchestrators Level 2 (19 files):**
19. [ ] **CREATE NEW:** `docs/orchestrators/planning-system.html`
20. [ ] **CREATE NEW:** `docs/orchestrators/ado-orchestrator.html`
21. [ ] **CREATE NEW:** `docs/orchestrators/ado-operations.html`
22. [ ] **CREATE NEW:** `docs/orchestrators/ado-planning.html`
23. [ ] **CREATE NEW:** `docs/orchestrators/tdd-orchestrator.html`
24. [ ] **CREATE NEW:** `docs/orchestrators/execution-orchestrator.html`
25. [ ] **CREATE NEW:** `docs/orchestrators/cleanup-orchestrator.html`
26. [ ] **CREATE NEW:** `docs/orchestrators/sanitization-orchestrator.html`
27. [ ] **CREATE NEW:** `docs/orchestrators/system-integrity.html`
28. [ ] **CREATE NEW:** `docs/orchestrators/git-checkpoint.html`
29. [ ] **CREATE NEW:** `docs/orchestrators/refinement-orchestrator.html`
30. [ ] **CREATE NEW:** `docs/orchestrators/cortex-lens.html`
31. [ ] **CREATE NEW:** `docs/orchestrators/architectural-review.html`
32. [ ] **CREATE NEW:** `docs/orchestrators/debug-orchestrator.html`
33. [ ] **CREATE NEW:** `docs/orchestrators/rollback-orchestrator.html`
34. [ ] **CREATE NEW:** `docs/orchestrators/maintenance-orchestrator.html`
35. [ ] **CREATE NEW:** `docs/orchestrators/token-optimization-orchestrator.html`
36. [ ] **CREATE NEW:** `docs/orchestrators/doc-generation-orchestrator.html`
37. [ ] **CREATE NEW:** `docs/orchestrators/vision-orchestrator.html`

**STS Level 2 (6 files):**
38. [ ] **CREATE NEW:** `docs/sts/security.html`
39. [ ] **CREATE NEW:** `docs/sts/solid.html`
40. [ ] **CREATE NEW:** `docs/sts/code-quality.html`
41. [ ] **CREATE NEW:** `docs/sts/performance.html`
42. [ ] **CREATE NEW:** `docs/sts/testing.html`
43. [ ] **CREATE NEW:** `docs/sts/documentation.html`

**Architecture Level 2 (4 files):**
44. [ ] **CREATE NEW:** `docs/architecture/skull.html`
45. [ ] **CREATE NEW:** `docs/architecture/knowledge-graph.html`
46. [ ] **CREATE NEW:** `docs/architecture/brain-tiers.html`
47. [ ] **CREATE NEW:** `docs/architecture/context-management.html`

**Token Optimization Level 2 (3 files):**
48. [ ] **CREATE NEW:** `docs/token-optimization/analysis.html`
49. [ ] **CREATE NEW:** `docs/token-optimization/strategies.html`
50. [ ] **CREATE NEW:** `docs/token-optimization/savings.html`

**Best Practices Level 2 (3 files):**
51. [ ] **CREATE NEW:** `docs/best-practices/engineering.html` (12 guidelines)
52. [ ] **CREATE NEW:** `docs/best-practices/security.html` (8 guidelines)
53. [ ] **CREATE NEW:** `docs/best-practices/quality.html` (15 guidelines)

**Toolkit Manager Level 2 (3 files):**
54. [ ] **CREATE NEW:** `docs/toolkit-manager/discovery.html`
55. [ ] **CREATE NEW:** `docs/toolkit-manager/orchestration.html`
56. [ ] **CREATE NEW:** `docs/toolkit-manager/integration.html`

**CORTEX Lens Level 2 (3 files):**
57. [ ] **CREATE NEW:** `docs/lens/ast-analysis.html`
58. [ ] **CREATE NEW:** `docs/lens/reverse-engineering.html`
59. [ ] **CREATE NEW:** `docs/lens/intelligence.html`

**Get Started Level 2 (3 files):**
60. [ ] **CREATE NEW:** `docs/get-started/installation.html`
61. [ ] **CREATE NEW:** `docs/get-started/configuration.html`
62. [ ] **CREATE NEW:** `docs/get-started/first-steps.html`

**Knowledge Library Level 2 (50+ files):**
63. [ ] **CREATE NEW:** All knowledge domain pages in `docs/knowledge/` using template
   - Engineering domains (10 files)
   - Security domains (8 files)
   - Testing domains (6 files)
   - Performance domains (5 files)
   - Frontend domains (8 files)
   - Backend domains (10 files)
   - Database domains (5 files)

**Story Level 2 (13 chapters):**
64. [ ] **CREATE NEW:** All story chapter pages in `docs/story/` using template

#### 3.4 Level 3 Content Consolidation
65. [ ] Review all Level 2 pages for deep content needs
66. [ ] Implement tabs/accordions for multi-section content (NO Level 3)
67. [ ] **VERIFY:** Zero Level 3 navigation links exist

#### 3.5 Validation
68. [ ] **VERIFY:** All 137 Level 2 pages have standardized header with CORTEX logo
69. [ ] **VERIFY:** All 137 Level 2 pages have standardized footer
70. [ ] **VERIFY:** Zero inline styles on ALL Level 2 pages
71. [ ] **VERIFY:** T1 animations only (no T3 dramatic animations)
72. [ ] **VERIFY:** All deep content uses tabs/accordions (NO Level 3)
73. [ ] **TEST:** Navigation functional Level 0 → Level 1 → Level 2 (stops)
74. [ ] **TEST:** Responsive on mobile (375px), tablet (768px), desktop (1440px)

**Deliverables:**
- 137 new Level 2 HTML files created from scratch
- Level 2 template in `templates/level2-template.html`
- Level 2 creation report in `reports/level2-creation.md`

**Validation Gate:**
- ✅ All 137 Level 2 pages created from scratch (not modified)
- ✅ Glass header present with CORTEX logo on ALL Level 2 pages
- ✅ Glass footer present on ALL Level 2 pages
- ✅ Zero inline styles on ANY Level 2 page
- ✅ Navigation stops at Level 2 (NO Level 3 links)
- ✅ Deep content uses tabs/accordions appropriately
- ✅ Responsive layout functional across all breakpoints
### Phase 4: Inline Styles Cleanup & Level 0 Finalization

**Duration:** 4 hours | **Complexity:** MEDIUM

**Objectives:**
- Complete Level 0 multi-panel implementation
- Scan ALL HTML files for inline `style=""` attributes
- Extract inline styles to appropriate CSS classes
- Add standardized header/footer to Level 0 if missing

**Tasks:**

#### 4.1 Level 0 Multi-Panel Finalization
1. [ ] Review existing `docs/index.html` for inline styles
2. [ ] Complete Security multi-panel implementation (if not in Phase 1)
3. [ ] Complete Orchestrators multi-panel implementation (if not in Phase 1)
4. [ ] Complete STS multi-panel implementation (if not in Phase 1)
5. [ ] Add standardized footer to Level 0 (header NOT required at Level 0)
6. [ ] **VERIFY:** Zero inline styles in Level 0 multi-panels
7. [ ] **TEST:** Multi-panels responsive on 3 breakpoints

#### 4.2 Inline Style Detection
8. [ ] Run grep search for `style="` across `docs/**/*.html`
9. [ ] Generate inline styles inventory in `context/inline-styles-inventory.json`
10. [ ] Categorize inline styles by type (color, layout, typography, animation)
11. [ ] Identify high-frequency inline style patterns

#### 4.3 CSS Class Migration
12. [ ] For each unique inline style pattern:
   - [ ] Create appropriate CSS class in `glassmorphism.css`
   - [ ] Document class purpose and usage
   - [ ] Update HTML to use new class
13. [ ] Replace all color inline styles with CSS variables (`--accent-primary`, etc.)
14. [ ] Replace all layout inline styles with utility classes (`.flex-row`, `.grid-2col`, etc.)
15. [ ] Replace all animation inline styles with animation classes (`.fade-in`, `.slide-up`, etc.)

#### 4.4 Validation
16. [ ] Re-run grep search to confirm zero inline styles
17. [ ] Visual regression test: compare before/after screenshots for 10 sample pages
18. [ ] **VERIFY:** `grep -r 'style="' docs/` returns zero results
19. [ ] **TEST:** All pages render identically after inline style removal

**Deliverables:**
- `docs/index.html` (finalized with multi-panels, zero inline styles)
- `glassmorphism.css` (updated with new utility classes)
- Inline styles migration report in `reports/inline-styles-cleanup.md`
- Before/after screenshots in `artifacts/visual-regression/`

**Validation Gate:**
- ✅ All 3 multi-panels complete on Level 0
- ✅ Standardized footer on Level 0 (header not required)
- ✅ **ZERO** inline `style=""` attributes in ANY HTML file
- ✅ All new CSS classes documented
- ✅ Visual regression tests pass (no visual differences)
- ✅ Page load times unchanged (<3s on 3G)

---

### Phase 5: Responsive & Mobile Verification

**Duration:** 4 hours | **Complexity:** MEDIUM

**Objectives:**
- Test ALL views on mobile, tablet, and desktop breakpoints
- Fix responsive layout issues
- Ensure mobile-friendly interactions

**Tasks:**

#### 5.1 Level 0 Multi-Panel Responsive Testing
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

#### 5.2 Level 1 Pages Responsive Testing
13. [ ] Test ALL 13 Level 1 pages at 375px, 768px, 1440px
14. [ ] Fix navigation menu on mobile (hamburger if needed)
15. [ ] Ensure card grids stack properly on mobile
16. [ ] **VERIFY:** All text readable without horizontal scroll

#### 5.3 Level 2 Pages Responsive Testing
17. [ ] Sample test 40 Level 2 pages (30% of 137 files)
18. [ ] Identify common responsive issues
19. [ ] Apply fixes systematically to ALL Level 2 pages
20. [ ] **VERIFY:** Code blocks don't overflow on mobile
21. [ ] **VERIFY:** Mermaid diagrams scale on mobile
22. [ ] **VERIFY:** Tabs/accordions functional on touch devices

#### 5.4 Touch-Friendly Interactions
23. [ ] Ensure all clickable elements have `min-height: 44px` (touch target size)
24. [ ] Test hover effects translate to tap on mobile
25. [ ] Remove `:hover` CSS for touch devices using `@media (hover: none)`
26. [ ] **TEST:** Navigation functional on iOS Safari and Android Chrome

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

### Phase 6: Documentation Update

**Duration:** 2 hours | **Complexity:** LOW

**Objectives:**
- Update `glassmorphism-design-standard.md` with new patterns
- Document header/footer standards
- Add NO inline styles rule to standard

**Tasks:**

#### 6.1 Design Standard Updates
1. [ ] Update `glassmorphism-design-standard.md` with:
   - Header structure (begins at Level 1, not Level 0)
   - Footer structure (all levels)
   - NO Level 3 navigation rule
   - Create from scratch principle for Level 1 & 2
2. [ ] Add header/footer HTML structure to Pattern Library section
3. [ ] Add header/footer CSS classes documentation
4. [ ] Add "NO Inline Styles" rule to Core Principles section
5. [ ] Update responsive breakpoints table with actual values used
6. [ ] Add mobile-first design section

#### 6.2 Pattern 15 Documentation
7. [ ] Add usage examples for each multi-panel category structure
8. [ ] Add Tetris grid layout documentation with `nth-child` patterns
9. [ ] Document when to use multi-panel vs standard tile (10+ pages threshold)

#### 6.3 Implementation Guide
10. [ ] Create `cortex-brain/documents/standards/glassmorphism-implementation-guide.md`
11. [ ] Include step-by-step instructions for adding new views
12. [ ] Include CSS class reference table
13. [ ] Include common patterns (header, footer, card, button, link)
14. [ ] Document Level 1 and Level 2 templates
15. [ ] Document NO Level 3 enforcement strategy

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

### Phase 7: Final Validation & Testing

**Duration:** 3 hours | **Complexity:** MEDIUM

**Objectives:**
- Comprehensive validation of all requirements
- Cross-browser testing
- Performance verification
- **VERIFY NO Level 3 navigation exists**

**Tasks:**

#### 7.1 SKULL Rule Compliance
1. [ ] Run grep search: `grep -r 'style="' docs/` → expect ZERO results
2. [ ] Verify all CSS classes exist in `glassmorphism.css`
3. [ ] Check for unused CSS classes
4. [ ] **VERIFY:** NO inline styles anywhere in HTML files
5. [ ] **VERIFY:** NO Level 3 navigation links in any view
6. [ ] **VERIFY:** All deep content uses tabs/accordions, not Level 3 pages

#### 7.2 View Hierarchy Validation
7. [ ] Audit Level 0: 1 home page with standardized footer (no header)
8. [ ] Audit Level 1: 13 hub pages with standardized header+footer
9. [ ] Audit Level 2: 137 detail pages with standardized header+footer
10. [ ] **VERIFY:** Zero navigation beyond Level 2
11. [ ] **VERIFY:** All Level 1 & Level 2 pages created from scratch (not modified legacy)

#### 7.3 Visual Regression Testing
12. [ ] Take screenshots of 20 sample pages (Level 0, Level 1, Level 2 mix)
13. [ ] Document visual improvements from scratch rebuild
14. [ ] Fix any unintended visual regressions

#### 7.4 Cross-Browser Testing
**Chrome:**
15. [ ] Test multi-panels rendering
16. [ ] Test animations (T1 subtle transitions)
17. [ ] Test responsive breakpoints

**Firefox:**
18. [ ] Test backdrop-filter support
19. [ ] Test multi-panel layout
20. [ ] Test responsive breakpoints

**Safari:**
21. [ ] Test `-webkit-backdrop-filter` support
22. [ ] Test multi-panel rendering
23. [ ] Test iOS Safari mobile view

**Edge:**
24. [ ] Test multi-panel layout
25. [ ] Test animations

#### 7.5 Performance Testing
26. [ ] Measure page load time for `docs/index.html` (<3s on 3G target)
27. [ ] Measure FPS for animations (≥60fps target)
28. [ ] Check GPU memory usage (<50MB target)
29. [ ] Run Lighthouse audit (target: >90 performance score)
30. [ ] **VERIFY:** No performance regression from rebuild

#### 7.6 Accessibility Testing
31. [ ] Run axe DevTools scan on all 3 multi-panels
32. [ ] Check keyboard navigation (Tab, Enter, Escape)
33. [ ] Check screen reader compatibility (NVDA/JAWS)
34. [ ] **VERIFY:** WCAG 2.1 AA compliance maintained

**Deliverables:**
- Cross-browser test matrix in `reports/cross-browser-testing.md`
- Performance test results in `reports/performance-benchmarks.md`
- Accessibility audit in `reports/accessibility-audit.md`
- Final validation checklist in `reports/final-validation.md`

**Validation Gate:**
- ✅ **ZERO inline styles** across entire docs/ folder
- ✅ **ZERO Level 3 navigation** links in any view
- ✅ All Level 1 & Level 2 pages created from scratch
- ✅ All browsers render multi-panels correctly
- ✅ Page load time <3s on 3G
- ✅ Animation FPS ≥60
- ✅ Lighthouse performance score >90
- ✅ WCAG 2.1 AA compliance verified

---

### Phase 8: REFACTOR - Whole-File Cleanup (SKULL Enforcement)

**Duration:** 4 hours | **Complexity:** MEDIUM

**Objectives:**
- **MANDATORY FINAL PHASE:** Complete whole-file cleanup of all modified/created files
- Enforce SKULL NO_INLINE_STYLES rule across entire codebase
- Clean up any temporary files, comments, or debug code
- Ensure consistent formatting and structure

**Tasks:**

#### 8.1 Whole-File Review
1. [ ] Review ALL 150 HTML files for consistency
2. [ ] Remove any TODO comments or debug code
3. [ ] Standardize indentation (2 spaces) across all HTML files
4. [ ] Verify CSS class naming consistency
5. [ ] Remove any unused CSS classes from `glassmorphism.css`

#### 8.2 Final Inline Style Purge
6. [ ] Run comprehensive grep: `grep -r 'style="' docs/` → MUST return ZERO
7. [ ] Run grep for style variations: `grep -ri 'style\s*=' docs/` → MUST return ZERO
8. [ ] Manually spot-check 20 random HTML files for inline styles
9. [ ] **VERIFY:** Absolute zero inline styles in any HTML file

#### 8.3 Code Quality
10. [ ] Validate all HTML files (W3C validator)
11. [ ] Check for broken internal links
12. [ ] Verify all images have alt text
13. [ ] Ensure all headings follow proper hierarchy (h1 → h2 → h3)
14. [ ] Check for duplicate IDs across all pages

#### 8.4 Documentation Cleanup
15. [ ] Update all planning documents with actual completion dates
16. [ ] Archive any obsolete documentation
17. [ ] Create final implementation summary
18. [ ] Document lessons learned

#### 8.5 Git Checkpoint
19. [ ] Create git checkpoint per SKULL GIT_ISOLATION rule
20. [ ] Commit all changes with descriptive messages
21. [ ] Tag release: `glassmorphism-standardization-v4.1.0`
22. [ ] **VERIFY:** No CORTEX internal code in user repo commits

**Deliverables:**
- Final cleanup report in `reports/final-refactor.md`
- Git checkpoint documentation
- Lessons learned in `cortex-brain/lessons-learned.yaml`

**Validation Gate:**
- ✅ **ABSOLUTE ZERO** inline styles (verified 3 ways)
- ✅ All HTML files W3C valid
- ✅ Zero broken links
- ✅ All images have alt text
- ✅ Git checkpoint created
- ✅ SKULL rules enforced throughout
- ✅ Implementation documentation complete

---

## 📊 Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Inline Styles Removed | 100% (ZERO remaining) | `grep -r 'style="' docs/` |
| Level 1 Views Created from Scratch | 100% (13/13 files) | File creation audit |
| Level 2 Views Created from Scratch | 100% (137/137 files) | File creation audit |
| Header/Footer Standardization | 100% (150/150 files) | File count audit |
| Level 3 Elimination | 100% (ZERO Level 3 links) | Navigation audit |
| Responsive Breakpoints Functional | 100% (all views) | Manual testing at 375px, 768px, 1440px |
| Multi-Panel Implementation | 100% (3/3 tiles) | Visual inspection |
| Cross-Browser Compatibility | 100% (4/4 browsers) | Manual testing |
| Page Load Time | <3s on 3G | Lighthouse audit |
| WCAG AA Compliance | 100% | axe DevTools |

---

## 🎯 Definition of Done

**All phases complete when:**
1. ✅ **ZERO** inline `style=""` attributes in ANY HTML file (verified 3 ways)
2. ✅ **ZERO** Level 3 navigation links in any view
3. ✅ All 13 Level 1 hub pages created from scratch with standardized header (beginning at Level 1) and footer
4. ✅ All 137 Level 2 detail pages created from scratch with standardized header and footer
5. ✅ Level 0 home page has standardized footer (NO header required at Level 0)
6. ✅ Security, Orchestrators, and STS use multi-panel Pattern 15
7. ✅ All views responsive on mobile (375px), tablet (768px), desktop (1440px)
8. ✅ All new CSS classes documented in glassmorphism-design-standard.md
9. ✅ Cross-browser testing passed (Chrome, Firefox, Safari, Edge)
10. ✅ Performance benchmarks met (<3s load, ≥60fps, <50MB GPU)
11. ✅ WCAG 2.1 AA accessibility compliance verified
12. ✅ Visual regression tests passed (improvements documented)
13. ✅ Git commits follow SKULL rule (no CORTEX code in user repos)
14. ✅ Phase 8 REFACTOR complete (whole-file cleanup)

---

## 📁 Deliverable Structure

```
cortex-brain/documents/planning/active/level-2-glassmorphism-standardization/
├── 00-master-plan.md                           # This file (v4.1.0 AUTONOMOUS-READY)
├── context/
│   ├── view-hierarchy-audit.md                 # Phase 0 discovery
│   ├── css-audit.md                            # Phase 0 CSS audit
│   ├── inline-styles-inventory.json            # Phase 4 inline styles found
│   ├── inline-styles-removed.md                # Phase 4 inline styles extracted
│   └── responsive-fixes.md                     # Phase 5 responsive issues fixed
├── templates/
│   ├── level1-template.html                    # Phase 2 Level 1 template
│   └── level2-template.html                    # Phase 3 Level 2 template
├── reports/
│   ├── level1-creation.md                      # Phase 2 Level 1 creation report
│   ├── level2-creation.md                      # Phase 3 Level 2 creation report
│   ├── inline-styles-cleanup.md                # Phase 4 cleanup report
│   ├── responsive-testing-matrix.md            # Phase 5 test results
│   ├── design-standard-updates.md              # Phase 6 change log
│   ├── cross-browser-testing.md                # Phase 7 browser compatibility
│   ├── performance-benchmarks.md               # Phase 7 performance results
│   ├── accessibility-audit.md                  # Phase 7 WCAG compliance
│   ├── final-validation.md                     # Phase 7 final checklist
│   └── final-refactor.md                       # Phase 8 cleanup report
├── artifacts/
│   ├── visual-regression/                      # Before/after screenshots
│   │   ├── before/
│   │   └── after/
│   └── mobile-screenshots/                     # Phase 5 mobile testing
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
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml` (SKULL)
- **Prototype Reference:** `docs/prototypes/home-redesign-v2.html`
- **Current Home Page:** `docs/index.html`
- **Response Templates:** `cortex-brain/response-templates-v4.yaml` (line 863: autonomous_execution_progress)

---

## 📝 Notes

**Implementation Philosophy:**
- **Discovery-First**: Each phase begins with discovery to capture enhancements
- **Create from Scratch**: All Level 1 & Level 2 views rebuilt (avoid modification/duplication)
- **CSS-First**: All styling through classes, zero inline styles
- **Mobile-First**: Design for 375px, enhance for larger screens
- **2-Level Maximum**: NO Level 3 navigation, use tabs/accordions for depth
- **Header from Level 1**: Standardized header begins at Level 1, NOT Level 0
- **Progressive Enhancement**: Core functionality without JavaScript
- **Accessibility-First**: WCAG 2.1 AA from the start, not as afterthought

**Quality Gates:**
- Each phase MUST pass validation gate before proceeding
- No phase can be marked complete with failing tests
- Git commits only after phase validation passes
- SKULL rules enforced throughout (TDD, NO_INLINE_STYLES, NO_LEVEL_3, CREATE_FROM_SCRATCH, RESPONSIVE_MANDATORY)
- **Phase 8 REFACTOR MANDATORY**: Whole-file cleanup per SKULL enforcement

**Risk Mitigation:**
- Discovery phase prevents content loss during rebuild
- Create-from-scratch approach eliminates legacy issues
- Cross-browser testing prevents browser-specific bugs
- Performance testing ensures no degradation
- Accessibility audit maintains compliance
- Phase 8 ensures long-term code quality

**Autonomous Execution Requirements:**
1. ✅ Response Template: `autonomous_execution_progress` (response-templates-v4.yaml:863)
2. ✅ Visual Progress Tracking: Progress bars for all 8 phases
3. ✅ TDD Enforcement: Tests before implementation where applicable
4. ✅ Final REFACTOR Phase: SKULL rule enforcement (whole-file cleanup)
5. ✅ copilot_instructions Block: All execution metadata documented

---

**End of Master Plan v4.1.0 AUTONOMOUS-READY**
