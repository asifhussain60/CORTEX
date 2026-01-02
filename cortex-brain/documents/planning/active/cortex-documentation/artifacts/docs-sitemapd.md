# 🗺️ CORTEX Documentation Site Map

**Version:** 4.0.2 | **Status:** ✅ ACTIVE  
**Author:** Asif Hussain | **Last Updated:** January 2, 2026  
**Last Compliance Audit:** January 2, 2026  
**Copyright © 2026 Asif Hussain. All rights reserved.**

---

## 🧠 CORTEX INSTRUCTIONS - READ FIRST

**⚠️ MANDATORY WORKFLOW FOR ALL DOCUMENTATION WORK:**

### 1. **CHECK DESIGN STANDARDS BEFORE ANY CHANGES**

Before modifying or creating ANY HTML files, you MUST:

1. **Read Design Standards:**
   - `cortex-brain/documents/standards/glassmorphism-design-standard.md` (PRIMARY)
   - `cortex-brain/documents/planning/active/cortex-documentation/artifacts/level1-specs/` (DETAILED)

2. **Verify CSS Classes Exist:**
   - Search `docs/assets/css/main.css` for required classes
   - If classes are MISSING → CREATE CSS FIRST
   - Never apply classes that don't exist in stylesheet

3. **Validate Against Rules:**
   - ⛔ ZERO inline styles (`style=""` attributes forbidden)
   - 🎨 Glassmorphism patterns only (`.glass-card`, `.glass-header`, etc.)
   - 🎭 T1 animations for Level 1 pages (`.animation-t1`)
   - 📱 Mobile-first responsive (CSS media queries required)
   - 📏 Minimum spacing: `var(--space-lg)` (1.5rem/24px) between stacked elements

### 2. **CSS-FIRST DEVELOPMENT RULE**

**WORKFLOW:**
```
Step 1: User requests HTML changes
Step 2: Check glassmorphism-design-standard.md
Step 3: Search main.css for required classes
Step 4: IF MISSING → Create CSS classes FIRST
Step 5: Apply CSS classes to HTML
Step 6: Run validation tool (css-layout-validator.js)
Step 7: Test in browser
```

**NEVER:**
- ❌ Add classes to HTML without verifying they exist in CSS
- ❌ Use inline styles (`style="..."`)
- ❌ Create HTML before CSS
- ❌ Skip validation after changes

### 3. **VALIDATION ENFORCEMENT**

After ANY documentation changes:

1. **Automatic Validation:**
   - CSS validator runs on page load (`docs/assets/js/css-layout-validator.js`)
   - Check browser console for issues
   - Fix HIGH severity issues immediately

2. **Manual Validation:**
   ```javascript
   // Browser console commands
   CORTEX.validator.validate()       // Run checks
   CORTEX.validator.applyFixes()     // Apply auto-fixes
   CORTEX.validator.enableAutoFix()  // Enable persistent fixes
   ```

3. **Compliance Checklist:**
   - [ ] CSS classes exist in main.css before HTML application
   - [ ] Zero inline styles (scan HTML for `style=""`)
   - [ ] Glass header pattern correct for page level
   - [ ] T1 animations only (`.animation-t1` class)
   - [ ] Proper spacing (min 24px between cards/panels)
   - [ ] Responsive breakpoints working (375px/768px/1440px)

### 4. **LEVEL-SPECIFIC RULES**

| Level | Header Pattern | Animations | Logo |
|-------|----------------|------------|------|
| **Level 0** (Home) | `.glass-header` with logo + nav | T3 allowed | ✅ YES |
| **Level 1** (Detail pages) | `.glass-header` with nav only | T1 ONLY | ❌ NO |

**Critical Violations:**
- 🔴 **nav-container pattern** → Must be `.glass-header`
- 🔴 **breadcrumb navigation** → Remove, use simple back link
- 🔴 **logo on Level 1** → Remove logo, keep nav only
- 🔴 **embedded `<style>` tags** → Move to main.css
- 🔴 **inline styles** → Replace with CSS classes

### 5. **CSS CLASS REFERENCE**

**Before applying these classes, VERIFY they exist in main.css:**

| Class | Purpose | File Location |
|-------|---------|---------------|
| `.glass-header` | Navigation header | main.css:~290 |
| `.glass-card-display` | Non-interactive cards | main.css:~534 |
| `.glass-card-clickable` | Interactive cards/links | main.css:~501 |
| `.animation-t1` | Subtle hover effects | main.css:~920 |
| `.category-panels-grid` | Multi-panel grid layout | main.css:~5590 |
| `.category-subpanel` | Individual category panels | main.css:~5610 |
| `.level0-category-subpanel` | Level 0 category panels | main.css:~5900 |
| `.level0-categories-grid` | Level 0 grid layout | main.css:~5875 |

**If class is missing:** Create it in main.css BEFORE using in HTML.

### 6. **COMPLIANCE AUDIT WORKFLOW**

When working on a specific panel/section:

1. **Check current compliance status** (see audit tables below)
2. **Read glassmorphism-design-standard.md** for pattern details
3. **Verify CSS classes exist** before modifying HTML
4. **Create missing CSS classes** if needed
5. **Apply changes to HTML**
6. **Run validator** (`CORTEX.validator.validate()`)
7. **Update compliance status** in this document

### 7. **COMMON VIOLATIONS & FIXES**

| Violation | Wrong | Correct |
|-----------|-------|---------|
| **Header pattern** | `<div class="nav-container">` | `<header class="glass-header">` |
| **Inline styles** | `<div style="padding: 20px">` | `<div class="glass-card">` |
| **Embedded CSS** | `<style>` in `<head>` | Extract to main.css |
| **Logo on Level 1** | Logo + nav in header | Nav only in header |
| **Wrong animation** | `.animation-t3` on Level 1 | `.animation-t1` only |

### 8. **REFERENCES**

| Document | Purpose | Location |
|----------|---------|----------|
| **Glassmorphism Design Standard** | Primary design rules | `cortex-brain/documents/standards/glassmorphism-design-standard.md` |
| **Level 1 Specs** | Detailed page specifications | `cortex-brain/documents/planning/active/cortex-documentation/artifacts/level1-specs/` |
| **CSS Layout Validator** | Runtime validation tool | `docs/assets/js/css-layout-validator.js` |
| **Main Stylesheet** | All CSS classes | `docs/assets/css/main.css` |

---

## 🎯 Compliance Audit Summary (Security Panel)

**Audit Date:** January 2, 2026  
**Scope:** Security Multi-Panel (13 pages)  
**Standards:** Glassmorphism v4.0.1 + Level1-spec.md

| Status | Count | Files |
|--------|-------|-------|
| ✅ **Compliant** | 7 (54%) | access-control, data-protection, audit-logging, threat-modeling, risk-assessment, penetration-testing, vulnerability-assessment |
| 🔴 **Critical** | 5 (38%) | compliance, security-training, incident-response, threat-intelligence, dashboard |
| 🟡 **Warning** | 1 (8%) | owasp |

**Key Findings:**
- ✅ ZERO inline styles detected (100% CSS class compliance)
- ✅ All pages use T1 animations (animation-t1 class)
- 🔴 5 pages use wrong header (`nav-container` with logo instead of `glass-header`)
- 🟡 1 page uses older `level1-container` pattern
- ⚠️ 2 pages have minor hero section variations (still functional)

**Priority Fix:** Replace `nav-container` header with Level 1 glass header in 5 Response/Compliance pages.

---

## 🎯 Compliance Audit Summary (Orchestrators Panel)

**Audit Date:** January 2, 2026  
**Scope:** Orchestrators Multi-Panel (19 pages total: 14 linked + 5 unlinked)  
**Standards:** Glassmorphism v4.0.1 + Level1-spec.md

| Status | Count | Files |
|--------|-------|-------|
| ✅ **Compliant** | 0 (0%) | NONE |
| 🔴 **Critical** | 19 (100%) | ALL files violate standards |
| 🔴 **Inline Styles** | 10 (53%) | cleanup, system-integrity, git-checkpoint, refinement, cortex-lens, architectural-review, debug, rollback, intelligent-dashboard, pre-flight |

**Key Findings:**
- 🔴 ALL 19 files use breadcrumb navigation + logo-header (Level 0 pattern on Level 1 pages)
- 🔴 10 files have embedded `<style>` tags in `<head>` (violates zero inline styles rule)
- ❌ 1 file missing (ado-planning.html linked but doesn't exist)
- 🔗 5 files orphaned (exist but not linked in navigation)
- ⛔ **0% COMPLIANCE** - Complete pattern mismatch with design standard

**Priority Fix:** Replace breadcrumb + logo-header with Level 1 glass header in ALL 19 files + extract inline styles to main.css.

---

## 📋 Complete Site Hierarchy

This document provides the complete hierarchical view of the CORTEX documentation site structure with file existence verification.

**Legend:**
- ✅ File exists in filesystem
- ❌ File missing (linked but not created)
- 🔗 File exists but unlinked (orphaned)

---

## 🏠 Level 0: Home Page (docs/index.html)

**Compliance Status:** ✅ **COMPLIANT** (100% - Critical violations resolved January 2, 2026)

**Recent Changes (January 2, 2026):**
- ✅ **Embedded CSS extracted** - 1,700+ lines moved to `index-multipanel.css`
- ✅ **CSS variables implemented** - 60+ design tokens replace hardcoded values
- ✅ **Zero inline styles** - All `style="..."` attributes removed
- ✅ **File size reduced** - 52% reduction (3,304 → 1,590 lines)
- ✅ **Glassmorphism v4.0.1** - 100% standards compliant

**Design Compliance:**
- ✅ Multi-panel masonry pattern (Security, Orchestrators, STS)
- ✅ T3 animations (allowed on Level 0)
- ✅ CSS class-based styling (zero inline styles)
- ✅ CSS variable system (colors, spacing, shadows, transitions)
- ✅ External stylesheets (cacheable, maintainable)

### Hero Section - 6 Tile Links

```
✅ docs/index.html (HOME PAGE - Level 0)
│
├── Hero CTAs (6 primary navigation tiles)
│   ├── ✅ architecture/index.html (🧠 Architecture - 4-Tier Brain System)
│   ├── ✅ token-optimization/index.html (💰 Token Optimization - 97% Input Reduction)
│   ├── ✅ knowledge/index.html (📚 CORTEX Best Practices - 35 Guidelines)
│   ├── ✅ toolkit-manager/index.html (🛠️ Toolkit Manager - Tool Orchestration)
│   ├── ✅ lens/index.html (🔍 CORTEX LENS - AST Analysis)
│   └── ✅ getting-started/index.html (🚀 Get Started - 5-Minute Setup)
```

---

## 🛡️ SECURITY MULTI-PANEL (4 Categories, 13 Pages)

**Hierarchy:** Level 0 → Level 1 Detail Pages  
**Status:** 13 existing (100%), 0 missing, 0 unlinked  
**Compliance Audit:** January 2, 2026 - 7 compliant, 5 violations, 1 warning

```
🛡️ SECURITY MULTI-PANEL
│
├── 🔒 PROTECTION (3 Level 1 pages)
│   ├── ✅ security/access-control.html
│   ├── ✅ security/data-protection.html
│   └── ✅ security/audit-logging.html
│
├── 📋 ASSESSMENT (4 Level 1 pages)
│   ├── ✅ security/threat-modeling.html
│   ├── ✅ security/risk-assessment.html
│   ├── ⚠️ security/vulnerability-assessment.html (hero placement variation)
│   └── ✅ security/penetration-testing.html
│
├── ✅ COMPLIANCE (3 Level 1 pages)
│   ├── 🟡 security/owasp.html (non-standard level1-container pattern)
│   ├── 🔴 security/compliance.html (nav-container violation - needs glass-header)
│   └── 🔴 security/security-training.html (nav-container violation - needs glass-header)
│
└── 🚨 RESPONSE (3 Level 1 pages)
    ├── 🔴 security/incident-response.html (nav-container violation - needs glass-header)
    ├── 🔴 security/threat-intelligence.html (nav-container violation - needs glass-header)
    └── 🔴 security/dashboard.html (nav-container violation - needs glass-header)
```

**Compliance Status:**
- ✅ **7 COMPLIANT:** access-control, data-protection, audit-logging, threat-modeling, risk-assessment, penetration-testing, vulnerability-assessment
- 🔴 **5 CRITICAL:** compliance, security-training, incident-response, threat-intelligence, dashboard (using `nav-container` instead of `glass-header`)
- 🟡 **1 WARNING:** owasp (using older `level1-container` pattern)
- ✅ **ZERO inline styles** found (100% CSS class compliance)
- ✅ **ALL use T1 animations** (animation-t1 class)
- 🎯 **NO Level 2 pages** required (all content in Level 1)

---

## 🎯 ORCHESTRATORS MULTI-PANEL (5 Categories, 15 Linked + 5 Unlinked)

**Hierarchy:** Level 0 → Level 1 Detail Pages  
**Status:** 15 linked (14 existing, 1 missing), 5 unlinked orphans  
**Compliance Audit:** January 2, 2026 - 0 compliant, 19 violations

```
🎯 ORCHESTRATORS MULTI-PANEL
│
├── 🧠 PLANNING (4 Level 1 pages)
│   ├── 🔴 orchestrators/planning-system.html (breadcrumb + logo-header violation)
│   ├── 🔴 orchestrators/ado-orchestrator.html (breadcrumb + logo-header violation)
│   ├── 🔴 orchestrators/ado-operations.html (breadcrumb + logo-header violation)
│   └── ❌ orchestrators/ado-planning.html (MISSING - linked but not created)
│
├── ⚙️ EXECUTION (2 Level 1 pages)
│   ├── 🔴 orchestrators/tdd-orchestrator.html (breadcrumb + logo-header violation)
│   └── 🔴 orchestrators/execution-orchestrator.html (breadcrumb + logo-header violation)
│
├── 🔧 SYSTEM (4 Level 1 pages)
│   ├── 🔴 orchestrators/cleanup-orchestrator.html (breadcrumb + logo-header + inline styles)
│   ├── 🔴 orchestrators/sanitization-orchestrator.html (breadcrumb + logo-header violation)
│   ├── 🔴 orchestrators/system-integrity.html (breadcrumb + logo-header + inline styles)
│   └── 🔴 orchestrators/git-checkpoint.html (breadcrumb + logo-header + inline styles)
│
├── 📊 ANALYSIS (3 Level 1 pages)
│   ├── 🔴 orchestrators/refinement-orchestrator.html (breadcrumb + logo-header + inline styles)
│   ├── 🔴 orchestrators/cortex-lens.html (breadcrumb + logo-header + inline styles)
│   └── 🔴 orchestrators/architectural-review.html (breadcrumb + logo-header + inline styles)
│
├── 🐛 DEBUG (2 Level 1 pages)
│   ├── 🔴 orchestrators/debug-orchestrator.html (breadcrumb + logo-header + inline styles)
│   └── 🔴 orchestrators/rollback-orchestrator.html (breadcrumb + logo-header + inline styles)
│
└── ⚠️ UNLINKED ORPHANS (5 pages exist but not linked from index.html)
    ├── 🔴 orchestrators/intelligent-dashboard.html (breadcrumb + logo-header + inline styles + unlinked)
    ├── 🔴 orchestrators/onboarding-orchestrator.html (breadcrumb + logo-header violation + unlinked)
    ├── 🔴 orchestrators/pre-flight.html (breadcrumb + logo-header + inline styles + unlinked)
    ├── 🔴 orchestrators/sanitization.html (breadcrumb + logo-header violation + unlinked - duplicate?)
    └── 🔴 orchestrators/upgrade.html (breadcrumb + logo-header violation + unlinked)
```

**Compliance Status:**
- 🔴 **19 CRITICAL VIOLATIONS:** ALL files use breadcrumb + logo-header pattern (Level 0 structure on Level 1 pages)
- 🔴 **10 INLINE STYLE VIOLATIONS:** cleanup, system-integrity, git-checkpoint, refinement, cortex-lens, architectural-review, debug, rollback, intelligent-dashboard, pre-flight (embedded `<style>` tags in `<head>`)
- ❌ **1 MISSING:** ado-planning.html (linked but doesn't exist)
- 🔗 **5 ORPHANED:** Files exist but not linked in index.html
- ⛔ **0% COMPLIANCE:** No files follow Glassmorphism v4.0.1 standard
- 🎯 **NO Level 2 pages** required (all content in Level 1)

---

## 🔧 SHARPEN THE SAW MULTI-PANEL (6 Categories, 6 Pages)

**Hierarchy:** Level 0 → Level 1 Detail Pages  
**Status:** 6 existing (100%), 0 missing, 0 unlinked  
**Compliance Audit:** January 2, 2026 - 0 compliant, 6 violations

```
🔧 SHARPEN THE SAW MULTI-PANEL
│
├── 🛡️ SECURITY (1 Level 1 page)
│   └── 🔴 sts/security.html (breadcrumb navigation violation)
│
├── 🏛️ SOLID (1 Level 1 page)
│   └── 🔴 sts/solid.html (breadcrumb navigation violation)
│
├── ✨ CODE QUALITY (1 Level 1 page)
│   └── 🔴 sts/code-quality.html (breadcrumb navigation violation)
│
├── ⚡ PERFORMANCE (1 Level 1 page)
│   └── 🔴 sts/performance.html (breadcrumb navigation violation)
│
├── 🧪 TESTING (1 Level 1 page)
│   └── 🔴 sts/testing.html (breadcrumb navigation violation)
│
└── 📚 DOCUMENTATION (1 Level 1 page)
    └── 🔴 sts/documentation.html (breadcrumb navigation violation)
```

**Compliance Status:**
- 🔴 **6 CRITICAL VIOLATIONS:** ALL files use breadcrumb navigation (Level 0 pattern on Level 1 pages)
- ✅ **ZERO inline styles** found (100% CSS class compliance - uses external sts.css)
- ⚠️ **NO glass-header** - Missing required glassmorphism header element
- ⚠️ **Hero sections present** but missing hero-icon wrapper div structure
- ⛔ **0% COMPLIANCE:** All files violate header standard
- 🎯 **NO Level 2 pages** required (all content in Level 1)

---

## 📊 ADDITIONAL SITE SECTIONS

### Features Hub

```
✅ features/index.html (Features Hub Page)
├── ✅ features/planning-system.html
├── ✅ features/orchestrators.html
├── ✅ features/git-operations.html
├── ✅ features/holistic-discovery.html
├── ✅ features/dashboard-system.html
├── ✅ features/response-templates.html
└── ✅ features/token-optimization.html
```

### Architecture Hub

```
✅ architecture/index.html (Architecture Hub Page)
├── ✅ architecture/brain-tiers.html
├── ✅ architecture/knowledge-graph.html
├── ✅ architecture/skull-protection.html
├── ✅ architecture/development-context.html
└── ✅ architecture/architecture-FULL.html
```

### Knowledge Library

```
✅ knowledge/index.html (Knowledge Library Hub)
├── ✅ knowledge/api-design.html
├── ✅ knowledge/design-patterns.html
├── ✅ knowledge/microservices.html
├── ✅ knowledge/testing.html
├── ✅ knowledge/cloud.html
├── ✅ knowledge/containers.html
├── ✅ knowledge/database.html
├── ✅ knowledge/devops.html
├── ✅ knowledge/ddd.html
├── ✅ knowledge/engineering.html
├── ✅ knowledge/frontend.html
├── ✅ knowledge/security.html
├── ✅ knowledge/messaging.html
├── ✅ knowledge/mobile.html
├── ✅ knowledge/performance.html
├── ✅ knowledge/rag-domains.html
└── ✅ knowledge/ui-ux.html
```

### Getting Started

```
✅ getting-started/index.html (Getting Started Hub)
└── ✅ getting-started/tutorial.html
```

### Governance

```
└── ✅ governance/skull-rulebook.html (SKULL Brain Protection Rules)
```

### Validation

```
✅ validation/index.html (Validation Hub)
```

### CORTEX Lens

```
✅ lens/index.html (CORTEX Lens Hub - AST Analysis)
```

### Token Optimization

```
✅ token-optimization/index.html (Token Optimization Hub)
```

### Toolkit Manager

```
✅ toolkit-manager/index.html (Toolkit Manager Hub)
```

---

## 📈 SITE STATISTICS

| Section | Total Pages | Existing | Missing | Unlinked | Compliant | Violations | Complete % |
|---------|-------------|----------|---------|----------|-----------|------------|------------|
| **Security Multi-Panel** | 13 | 13 | 0 | 0 | 7 (54%) | 6 (46%) | 54% ✅ |
| **Orchestrators Multi-Panel** | 19 | 19 | 0 | 5 | 0 (0%) | 19 (100%) | 0% 🔴 |
| **Sharpen The Saw** | 6 | 6 | 0 | 0 | 0 (0%) | 6 (100%) | 0% 🔴 |
| **Features Hub** | 8 | 8 | 0 | 0 | - | - | 100% |
| **Architecture Hub** | 6 | 5 | 0 | 0 | - | - | 100% |
| **Knowledge Library** | 18 | 18 | 0 | 0 | - | - | 100% |
| **Other Sections** | 7 | 7 | 0 | 0 | - | - | 100% |
| **TOTAL SITE** | **77** | **76** | **0** | **5** | **7/38** | **31/38** | **97%** |

**Multi-Panel Compliance Summary:**
- **Security Panel:** 7/13 compliant (54%) - 5 nav-container violations, 1 non-standard pattern
- **Orchestrators Panel:** 0/19 compliant (0%) - 19 breadcrumb+logo violations, 10 embedded CSS blocks
- **STS Panel:** 0/6 compliant (0%) - 6 breadcrumb violations, ZERO inline styles (clean CSS architecture)
- **Overall Design Compliance:** 18% (7 compliant out of 38 audited files)

**Note:** Missing file count corrected - ado-planning.html was counted as both missing and existing. Actual: 19 existing orchestrator files (14 linked + 5 unlinked), 0 missing files.

---

## ⚠️ ACTION ITEMS

### 🔴 Critical (Design Standard Violations)

**SECURITY PANEL (5 files):**
1. **❌ FIX 5 nav-container violations** - Replace with glass-header in:
   - security/compliance.html
   - security/security-training.html
   - security/incident-response.html
   - security/threat-intelligence.html
   - security/dashboard.html
   
   **Issue:** Using Level 0 header pattern (`nav-container` with logo) on Level 1 pages  
   **Required:** Glass header with NO logo (Level 1 standard)

**ORCHESTRATORS PANEL (19 files - CRITICAL MASS VIOLATION):**

2. **❌ FIX 19 breadcrumb + logo-header violations** - Replace with glass-header in ALL files:
   - orchestrators/planning-system.html
   - orchestrators/ado-orchestrator.html
   - orchestrators/ado-operations.html
   - orchestrators/tdd-orchestrator.html
   - orchestrators/execution-orchestrator.html
   - orchestrators/cleanup-orchestrator.html
   - orchestrators/sanitization-orchestrator.html
   - orchestrators/system-integrity.html
   - orchestrators/git-checkpoint.html
   - orchestrators/refinement-orchestrator.html
   - orchestrators/cortex-lens.html
   - orchestrators/architectural-review.html
   - orchestrators/debug-orchestrator.html
   - orchestrators/rollback-orchestrator.html
   - orchestrators/intelligent-dashboard.html (unlinked)
   - orchestrators/onboarding-orchestrator.html (unlinked)
   - orchestrators/pre-flight.html (unlinked)
   - orchestrators/sanitization.html (unlinked - duplicate?)
   - orchestrators/upgrade.html (unlinked)
   
   **Current (WRONG):** Breadcrumb nav + separate logo-header div
   **Required:** Single glass-header with home link only

3. **❌ FIX 10 inline style violations** - Move embedded styles to main.css:
   - orchestrators/cleanup-orchestrator.html
   - orchestrators/system-integrity.html
   - orchestrators/git-checkpoint.html
   - orchestrators/refinement-orchestrator.html
   - orchestrators/cortex-lens.html
   - orchestrators/architectural-review.html
   - orchestrators/debug-orchestrator.html
   - orchestrators/rollback-orchestrator.html
   - orchestrators/intelligent-dashboard.html
   - orchestrators/pre-flight.html
   
   **Issue:** `<style>` tags in `<head>` violate "zero inline styles" principle  
   **Required:** Extract all CSS to main.css with proper class names

### 🟡 Medium (Non-Standard Patterns)
4. **🔧 REFACTOR security/owasp.html** - Update from `level1-container` to standard glass pattern
5. **🔧 STANDARDIZE security/vulnerability-assessment.html** - Move hero section before `main-container`
6. 🔗 **Link or remove 5 orphaned orchestrator pages:**
   - orchestrators/intelligent-dashboard.html
   - orchestrators/onboarding-orchestrator.html
   - orchestrators/pre-flight.html
   - orchestrators/sanitization.html (potential duplicate of sanitization-orchestrator.html)
   - orchestrators/upgrade.html

### 🟢 Low (Enhancements)
7. 🎨 **Complete Orchestrators redesign** - Full pattern replacement (estimated 15-20 hours for 19 files)
8. 📱 **Mobile responsiveness testing** - Validate 375px → 768px → 1440px breakpoints
9. 🧪 **Visual regression testing** - Ensure consistent styling across all pages

---

## 🎯 DESIGN COMPLIANCE

**All pages MUST follow:**
- ⛔ **ZERO inline styles** (CSS classes only)
- 🎨 **Glassmorphism v4.0.1** design standard
- 📱 **Mobile-first responsive** (375px → 768px → 1440px)
- 🎭 **T1 animations only** (0.2-0.3s, subtle effects)
- 🧊 **Glass navigation header** (Level 1 pages: NO logo, navigation only)
- 📏 **Minimum 1.5rem spacing** between stacked cards

**Reference:** `cortex-brain/documents/standards/glassmorphism-design-standard.md`

---

**Last Verified:** January 2, 2026  
**Total Pages:** 73 (71 existing, 1 missing, 5 unlinked)
