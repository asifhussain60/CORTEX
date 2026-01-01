# 🎨 Level 0-2 Glassmorphism Standardization - Master Implementation Plan (CORRECTED)

**Version:** 6.0.0 LEVEL-BASED-RECURSIVE  
**Author:** Asif Hussain  
**Date:** January 1, 2026  
**Status:** 📋 READY FOR EXECUTION  
**Orchestrator:** CORTEX AI Assistant  
**Design Standard:** glassmorphism-design-standard.md v4.0.1  
**Scope:** ALL Level 0, Level 1, Level 2 views (NO Level 3)  
**Validation Authority:** Toolkit Manager

---

## 🎯 Executive Summary

**Objective:** Implement glassmorphism design standard v4.0.1 across ALL CORTEX documentation using **level-based recursive phasing**, ensuring complete implementation of each hierarchy level before proceeding to the next.

**Strategy:** Horizontal level completion (all tiles at same level) with micro-batch validation (2-3 files per batch) to prevent token limit errors.

**Scope:** 9 major tiles × 3 hierarchy levels = comprehensive standardization with validation gates at every level.

**Critical Change from v5.0.0:** Phases now organized by VIEW LEVEL (not tile), completing all tiles at Level 0 first, then all Level 1 hubs, then all Level 2 detail pages.

---

## 🛡️ SKULL Protection Rules (MANDATORY)

**Enforced Throughout ALL Phases:**

- **HOLISTIC_DISCOVERY:** Each phase starts with discovery (phase X.0)
- **NO_INLINE_STYLES:** Zero tolerance - all styling via CSS classes
- **RESPONSIVE_MANDATORY:** Every batch validated at 3 breakpoints (375px/768px/1440px)
- **HEADER_FOOTER_STANDARD:** Standardized header (Level 1+) and footer (all levels)
- **NO_LEVEL_3:** All navigation stops at Level 2, use tabs/accordions for depth
- **CREATE_FROM_SCRATCH:** All files rebuilt, not modified (prevents duplication/legacy issues)
- **GIT_ISOLATION:** CORTEX code never commits to user repos
- **REFACTOR_CODE_CLEANUP_ENFORCEMENT:** Final phase requires ≥18 tasks across 5 categories
- **MICRO_BATCH_STRATEGY:** 2-3 files per batch to prevent "Sorry, response too long" errors
- **TOOLKIT_MANAGER_VALIDATION:** All phases validated by Toolkit Manager for adherence to glassmorphism-design-standard.md

---

## ⚠️ CRITICAL: View Hierarchy Enforcement

**MANDATORY STRUCTURE:**
```
Level 0 (Home: docs/index.html) 
    ↓
Level 1 (Hub Pages: 13 files - each tile's index)
    ↓
Level 2 (Detail Pages: 137+ files - specific components)
    ↓
⛔ NO LEVEL 3 (Use expandable sections, tabs, or modals instead)
```

**Level 0:** Single home page (`docs/index.html`)
- 9 tiles (3 multi-panel, 6 standard clickable)
- Hero section with glassmorphism
- Standardized footer

**Level 1:** 13 hub/index pages (tile entry points)
- Security, Orchestrators, STS, Architecture, Token Optimization, Best Practices, Toolkit Manager, CORTEX Lens, Get Started
- MUST have standardized header (beginning at Level 1)
- MUST have standardized footer
- T1 subtle animations ONLY

**Level 2:** 137+ detail pages (specific components)
- MUST have standardized header
- MUST have standardized footer
- T1 subtle animations ONLY
- NO Level 3 navigation

---

## 📊 Tile Inventory & Classification

### Multi-Panel Treatment (3 tiles)
1. **🛡️ Security**: 13 pages, 4 categories (Protection, Assessment, Compliance, Response) - **2×2 grid**
2. **🎯 Orchestrators**: 19 pages, 5 categories (Planning, Execution, System, Analysis, Debug) - **2×3 grid**
3. **🔧 Sharpen The Saw**: 6 pages, 6 categories (single-tag compact) - **3×2 grid**

### Standard Tile Treatment (6 tiles)
4. **🏛️ Architecture**: 1 hub + 4 detail pages (Brain Tiers, Knowledge Graph, Dev Context, SKULL)
5. **💰 Token Optimization**: 1 hub + 3 detail pages (Analysis, Strategies, Savings)
6. **📚 Best Practices**: 1 hub + 3 detail pages (35 guidelines organized)
7. **🛠️ Toolkit Manager**: 1 hub + 3 detail pages (Discovery, Orchestration, Integration)
8. **🔍 CORTEX Lens**: 1 hub + 3 detail pages (AST, Reverse Engineering, Intelligence)
9. **🚀 Get Started**: 1 hub + 3 detail pages (Installation, Configuration, First Steps)

**Total Files:** 1 (L0) + 13 (L1) + 137+ (L2) = 151+ files

---

## 🔄 Level-Based Recursive Phase Architecture

### Phase 1: Level 0 - Complete Home Page Implementation

**Target:** Complete ALL 9 tiles on `docs/index.html` with mobile-friendliness

#### 1.0: Discovery & Validation Setup
- Read glassmorphism-design-standard.md v4.0.1
- Audit existing `docs/index.html` structure
- Document current state of all 9 tiles
- **Toolkit Manager Validation:** Discovery completeness check
- **Deliverable:** `reports/phase1.0-discovery-report.md`

#### 1.1: Multi-Panel Tiles Implementation (Batch 1)

**Files:** 1 (`docs/index.html` - Security, Orchestrators, STS panels)

**Security Panel (2×2 Grid):**
- 4 subpanels: Protection, Assessment, Compliance, Response
- 7-color randomized palette using nth-child selectors
- Extract ALL inline styles to CSS classes
- Non-clickable subpanels + clickable tags within

**Orchestrators Panel (2×3 Grid):**
- 5 subpanels: Planning, Execution, System, Analysis, Debug
- 7-color randomized palette (different distribution)
- Extract ALL inline styles to CSS classes
- Non-clickable subpanels + clickable tags within

**Sharpen The Saw Panel (3×2 Grid):**
- 6 subpanels: Code Quality, SOLID, Testing, Performance, Security, Docs
- Single-tag compact design (full-width links)
- Extract ALL inline styles to CSS classes
- Non-clickable subpanels + clickable tags within

**Validation:**
- Visual check at 375px/768px/1440px
- CORTEX verifies ZERO inline styles
- **Toolkit Manager:** Validates against glassmorphism-design-standard.md
- **Deliverable:** `reports/phase1.1-multi-panel-validation.md`

#### 1.2: Standard Tiles Implementation (Batch 2)

**Files:** 1 (`docs/index.html` - Architecture, Token Optimization, Best Practices, Toolkit Manager, CORTEX Lens, Get Started)

**All 6 Standard Tiles:**
- Single clickable card per tile
- Icon, title, caption layout
- Hover glow + lift effect (`translateY(-2px)`)
- Glowing border on hover
- Extract ALL inline styles to CSS classes

**Validation:**
- Visual check at 375px/768px/1440px
- CORTEX verifies ZERO inline styles
- **Toolkit Manager:** Validates against glassmorphism-design-standard.md
- **Deliverable:** `reports/phase1.2-standard-tiles-validation.md`

#### 1.3: Hero Section & Footer Standardization

**Files:** 1 (`docs/index.html`)

**Hero Section:**
- Glassmorphism header with logo
- T3 dramatic animations (ONLY on Level 0)
- Responsive typography (16px → 48px scaling)

**Footer:**
- Standardized footer (all levels)
- Copyright © 2026 Asif Hussain
- CORTEX v4.0 + GitHub link

**Validation:**
- Visual check at 375px/768px/1440px
- CORTEX verifies header/footer compliance
- **Toolkit Manager:** Validates against glassmorphism-design-standard.md
- **Deliverable:** `reports/phase1.3-hero-footer-validation.md`

#### 1.4: Level 0 Comprehensive Validation

**All Checks:**
- Link validation (all 9 tiles navigable)
- Mobile-friendliness (375px/768px/1440px)
- ZERO inline styles
- Animation tier compliance (T3 only)
- Cross-browser testing (Chrome, Firefox, Safari, Edge)

**Validation:**
- **Toolkit Manager:** Final Level 0 compliance check
- **Deliverable:** `reports/phase1.4-level0-final-validation.md`

---

### Phase 2: Level 1 - All Hub/Index Pages Implementation

**Target:** Create ALL 13 Level 1 hub pages with mobile-friendliness

#### 2.0: Discovery & Validation Setup
- Re-read glassmorphism-design-standard.md (detect updates)
- Plan Level 1 page structures for all 13 hubs
- Document navigation patterns
- **Toolkit Manager Validation:** Discovery completeness check
- **Deliverable:** `reports/phase2.0-discovery-report.md`

#### 2.1: Multi-Panel Tile Hubs (Batch 1 - 3 files)

**Micro-Batch 2.1.1: Security Hub**
- `docs/security/index.html`
- 4 category sections (Protection, Assessment, Compliance, Response)
- Standardized header (Level 1 style - NO logo)
- Standardized footer
- T1 subtle animations only
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 2.1.2: Orchestrators Hub**
- `docs/orchestrators/index.html`
- 5 category sections (Planning, Execution, System, Analysis, Debug)
- Standardized header (Level 1 style - NO logo)
- Standardized footer
- T1 subtle animations only
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 2.1.3: STS Hub**
- `docs/sts/index.html`
- 6 category sections (Code Quality, SOLID, Testing, Performance, Security, Docs)
- Standardized header (Level 1 style - NO logo)
- Standardized footer
- T1 subtle animations only
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase2.1-multi-panel-hubs-validation.md`

#### 2.2: Standard Tile Hubs (Batch 2 - 6 files in 3 micro-batches)

**Micro-Batch 2.2.1: Architecture + Token Optimization (2 files)**
- `docs/architecture/index.html` (4 component cards)
- `docs/token-optimization/index.html` (3 workflow cards)
- Standardized headers (Level 1 style - NO logo)
- Standardized footers
- T1 subtle animations only
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 2.2.2: Best Practices + Toolkit Manager (2 files)**
- `docs/best-practices/index.html` (35 guidelines, 3 category cards)
- `docs/toolkit-manager/index.html` (3 workflow cards)
- Standardized headers (Level 1 style - NO logo)
- Standardized footers
- T1 subtle animations only
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 2.2.3: CORTEX Lens + Get Started (2 files)**
- `docs/lens/index.html` (3 analysis cards)
- `docs/getting-started/index.html` (3 onboarding cards)
- Standardized headers (Level 1 style - NO logo)
- Standardized footers
- T1 subtle animations only
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase2.2-standard-hubs-validation.md`

#### 2.3: Level 1 Link Validation
- Verify all 13 hubs link back to Level 0 correctly
- Test navigation from Level 0 to each hub
- Validate breadcrumb navigation (if implemented)
- **Toolkit Manager:** Navigation integrity check
- **Deliverable:** `reports/phase2.3-level1-link-validation.md`

#### 2.4: Level 1 Mobile Validation
- Test all 13 hubs at 375px (mobile)
- Test all 13 hubs at 768px (tablet)
- Test all 13 hubs at 1440px (desktop)
- **Toolkit Manager:** Responsive design compliance
- **Deliverable:** `reports/phase2.4-level1-mobile-validation.md`

#### 2.5: Level 1 Comprehensive Validation
- ZERO inline styles across all 13 hubs
- Header/footer standardization (Level 1 pattern)
- Animation tier compliance (T1 only)
- Cross-browser testing
- **Toolkit Manager:** Final Level 1 compliance check
- **Deliverable:** `reports/phase2.5-level1-final-validation.md`

---

### Phase 3: Level 2 - All Detail Pages Implementation

**Target:** Create ALL 137+ Level 2 detail pages with mobile-friendliness

**Strategy:** Organize by domain, implement in micro-batches of 2-3 files per batch

#### 3.0: Discovery & Validation Setup
- Re-read glassmorphism-design-standard.md (detect updates)
- Audit all 137+ Level 2 files (content preservation)
- Plan detail page layouts (Process Flow, Card Grid, etc.)
- **Toolkit Manager Validation:** Discovery completeness check
- **Deliverable:** `reports/phase3.0-discovery-report.md`

---

#### 3.1: Security Detail Pages (13 files in 5 micro-batches)

**Micro-Batch 3.1.1: Protection Category (3 files)**
- `docs/security/access-control.html` (Card Grid - access models)
- `docs/security/data-protection.html` (Card Grid - encryption methods)
- `docs/security/audit-logging.html` (Card Grid - log categories)
- Standardized headers (Level 2 style - NO logo)
- Standardized footers
- T1 subtle animations only
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.1.2: Assessment Category (3 files)**
- `docs/security/threat-modeling.html` (Process Flow - STRIDE methodology)
- `docs/security/risk-assessment.html` (Visual Matrix - risk scoring)
- `docs/security/vulnerability-assessment.html` (Interactive Checklist - CVE tracking)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.1.3: Testing Category (2 files)**
- `docs/security/penetration-testing.html` (Process Flow - pen-test phases)
- `docs/security/owasp.html` (Comparison Table - OWASP Top 10)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.1.4: Compliance Category (3 files)**
- `docs/security/compliance.html` (Interactive Checklist - GDPR/SOC2)
- `docs/security/security-training.html` (Tabbed Panels - training modules)
- `docs/security/incident-response.html` (Timeline - IR playbook)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.1.5: Intelligence Category (2 files)**
- `docs/security/threat-intelligence.html` (Metrics Dashboard - CTI feeds)
- `docs/security/dashboard.html` (Metrics Dashboard - security posture)
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase3.1-security-detail-validation.md`

---

#### 3.2: Orchestrators Detail Pages (19 files in 7 micro-batches)

**Micro-Batch 3.2.1: Planning Category (3 files)**
- `docs/orchestrators/planning-system.html` (Process Flow - 4-tier planning)
- `docs/orchestrators/ado-operations.html` (Process Flow - work item generation)
- `docs/orchestrators/architectural-review.html` (Interactive Checklist - ADR templates)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.2.2: Development Category (3 files)**
- `docs/orchestrators/tdd-mastery.html` (Process Flow - RED→GREEN→REFACTOR)
- `docs/orchestrators/debug-orchestrator.html` (Process Flow - debug pipeline)
- `docs/orchestrators/code-generation.html` (Card Grid - generation patterns)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.2.3: Quality Category (3 files)**
- `docs/orchestrators/refactoring.html` (Interactive Checklist - refactoring catalog)
- `docs/orchestrators/code-review.html` (Interactive Checklist - review criteria)
- `docs/orchestrators/sanitization.html` (Process Flow - 5-phase sanitization)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.2.4: Intelligence Category (3 files)**
- `docs/orchestrators/cortex-lens.html` (Metrics Dashboard - AST analysis)
- `docs/orchestrators/discovery.html` (Process Flow - discovery pipeline)
- `docs/orchestrators/analytics.html` (Metrics Dashboard - usage analytics)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.2.5: Cleanup Category (2 files)**
- `docs/orchestrators/vacuum.html` (Process Flow - deep cleanup)
- `docs/orchestrators/cleanup.html` (Process Flow - cache/bloat removal)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.2.6: Documentation Category (3 files)**
- `docs/orchestrators/documentation.html` (Tabbed Panels - doc types)
- `docs/orchestrators/onboarding.html` (Timeline - 6-phase onboarding)
- `docs/orchestrators/training.html` (Card Grid - training modules)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.2.7: Integration Category (2 files)**
- `docs/orchestrators/integration.html` (Card Grid - integration patterns)
- `docs/orchestrators/system-integrity.html` (Interactive Checklist - integrity checks)
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase3.2-orchestrators-detail-validation.md`

---

#### 3.3: STS Detail Pages (6 files in 3 micro-batches)

**Micro-Batch 3.3.1: Code Quality + SOLID (2 files)**
- `docs/sts/code-quality.html` (Interactive Checklist - quality metrics)
- `docs/sts/solid-principles.html` (Card Grid - 5 principles)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.3.2: Testing + Performance (2 files)**
- `docs/sts/testing-strategies.html` (Process Flow - test pyramid)
- `docs/sts/performance-optimization.html` (Metrics Dashboard - perf benchmarks)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.3.3: Security + Documentation (2 files)**
- `docs/sts/security-best-practices.html` (Comparison Table - security patterns)
- `docs/sts/documentation-guidelines.html` (Tabbed Panels - doc standards)
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase3.3-sts-detail-validation.md`

---

#### 3.4: Architecture Detail Pages (4 files in 2 micro-batches)

**Micro-Batch 3.4.1: Brain + Knowledge (2 files)**
- `docs/architecture/brain-tiers.html` (Hierarchy Diagram - 4-tier brain)
- `docs/architecture/knowledge-graph.html` (Interactive D3.js - graph visualization)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.4.2: Context + SKULL (2 files)**
- `docs/architecture/development-context.html` (Code Examples - context structure)
- `docs/architecture/skull-protection.html` (Interactive Checklist - SKULL rules)
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase3.4-architecture-detail-validation.md`

---

#### 3.5: Token Optimization Detail Pages (3 files in 2 micro-batches)

**Micro-Batch 3.5.1: Analysis + Strategies (2 files)**
- `docs/token-optimization/analysis.html` (Metrics Dashboard - token usage)
- `docs/token-optimization/strategies.html` (Card Grid - optimization techniques)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.5.2: Savings (1 file)**
- `docs/token-optimization/savings.html` (Metrics Dashboard - savings report)
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase3.5-token-optimization-detail-validation.md`

---

#### 3.6: Best Practices Detail Pages (3 files in 2 micro-batches)

**Micro-Batch 3.6.1: Planning + Coding (2 files)**
- `docs/best-practices/planning-guidelines.html` (Interactive Checklist - 35 guidelines subset)
- `docs/best-practices/coding-standards.html` (Comparison Table - language standards)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.6.2: Collaboration (1 file)**
- `docs/best-practices/collaboration-patterns.html` (Process Flow - collaboration workflow)
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase3.6-best-practices-detail-validation.md`

---

#### 3.7: Toolkit Manager Detail Pages (3 files in 2 micro-batches)

**Micro-Batch 3.7.1: Discovery + Integration (2 files)**
- `docs/toolkit-manager/discovery.html` (Process Flow - toolkit discovery)
- `docs/toolkit-manager/integration.html` (Code Examples - integration patterns)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.7.2: Orchestration (1 file)**
- `docs/toolkit-manager/orchestration.html` (Hierarchy Diagram - toolkit orchestration)
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase3.7-toolkit-manager-detail-validation.md`

---

#### 3.8: CORTEX Lens Detail Pages (3 files in 2 micro-batches)

**Micro-Batch 3.8.1: AST + Reverse Engineering (2 files)**
- `docs/lens/ast-analysis.html` (Metrics Dashboard - AST metrics)
- `docs/lens/reverse-engineering.html` (Process Flow - RE pipeline)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.8.2: Intelligence Dashboard (1 file)**
- `docs/lens/intelligence-dashboard.html` (Metrics Dashboard - intelligence aggregation)
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase3.8-cortex-lens-detail-validation.md`

---

#### 3.9: Get Started Detail Pages (3 files in 2 micro-batches)

**Micro-Batch 3.9.1: Installation + Configuration (2 files)**
- `docs/getting-started/installation.html` (Process Flow - install steps)
- `docs/getting-started/configuration.html` (Code Examples - config templates)
- **Validation:** Visual + Toolkit Manager check

**Micro-Batch 3.9.2: First Steps (1 file)**
- `docs/getting-started/first-steps.html` (Timeline - onboarding journey)
- **Validation:** Visual + Toolkit Manager check

**Deliverable:** `reports/phase3.9-get-started-detail-validation.md`

---

#### 3.10: Level 2 Link Validation
- Verify all 137+ detail pages link back to Level 1 correctly
- Test navigation from Level 1 to each detail page
- Validate breadcrumb navigation
- **Toolkit Manager:** Navigation integrity check
- **Deliverable:** `reports/phase3.10-level2-link-validation.md`

#### 3.11: Level 2 Mobile Validation
- Test all 137+ detail pages at 375px (mobile)
- Test all 137+ detail pages at 768px (tablet)
- Test all 137+ detail pages at 1440px (desktop)
- **Toolkit Manager:** Responsive design compliance
- **Deliverable:** `reports/phase3.11-level2-mobile-validation.md`

#### 3.12: Level 2 Comprehensive Validation
- ZERO inline styles across all 137+ detail pages
- Header/footer standardization (Level 2 pattern)
- Animation tier compliance (T1 only)
- Cross-browser testing
- **Toolkit Manager:** Final Level 2 compliance check
- **Deliverable:** `reports/phase3.12-level2-final-validation.md`

---

### Phase 4: Final Validation & Comprehensive REFACTOR (SKULL Enforcement)

**Enforcement Rule:** `REFACTOR_CODE_CLEANUP_ENFORCEMENT`

**Minimum Tasks Required:** 18 (across 5 categories)

#### 4.0: Toolkit Manager Comprehensive Audit
- **Toolkit Manager:** Validates ALL 151+ files against glassmorphism-design-standard.md v4.0.1
- Generates compliance report with violations (if any)
- **Acceptance Criteria:** ZERO violations
- **Deliverable:** `reports/phase4.0-toolkit-manager-audit.md`

#### 4.1: Level 3 Consolidation
- Verify no Level 3 pages exist
- Consolidate any discovered Level 3 content into Level 2 using tabs/accordions
- **Toolkit Manager:** Hierarchy compliance check
- **Deliverable:** `reports/phase4.1-level3-consolidation.md`

#### 4.2: Inline Style Extraction
- Scan for any remaining inline styles
- Extract to CSS classes in `glassmorphism.css`
- **Toolkit Manager:** CSS class validation
- **Deliverable:** `reports/phase4.2-inline-style-cleanup.md`

#### 4.3: Orphaned Code Removal (Category 1 - 3+ tasks)
- **4.3.1:** Remove unused CSS classes (defined but never applied)
- **4.3.2:** Delete unused D3.js helper functions (defined but never called)
- **4.3.3:** Clean up orphaned SVG filters (defined but not referenced)
- **Detection Method:** Code analysis + visual inspection
- **Toolkit Manager:** Code usage validation
- **Deliverable:** `reports/phase4.3-orphaned-code.md`

#### 4.4: Code Duplication Elimination (Category 2 - 4+ tasks)
- **4.4.1:** Consolidate duplicate D3.js initialization code
- **4.4.2:** Extract common glassmorphism HTML structure to templates
- **4.4.3:** Remove redundant CSS rules (identical selectors)
- **4.4.4:** Deduplicate breadcrumb navigation HTML
- **Detection Method:** Pattern matching + code review
- **Toolkit Manager:** Duplication detection
- **Deliverable:** `reports/phase4.4-duplication-removal.md`

#### 4.5: Dead Code Removal (Category 3 - 3+ tasks)
- **4.5.1:** Remove commented-out code blocks
- **4.5.2:** Delete TODO comments older than 90 days (move to GitHub Issues)
- **4.5.3:** Clean up unused `<script>` tags
- **Detection Method:** Code parsing + date analysis
- **Toolkit Manager:** Dead code detection
- **Deliverable:** `reports/phase4.5-dead-code.md`

#### 4.6: Formatting Standardization (Category 4 - 3+ tasks)
- **4.6.1:** Standardize indentation (2 spaces across all files)
- **4.6.2:** Sort CSS properties alphabetically (readability)
- **4.6.3:** Verify all `<style>` blocks moved to external stylesheets
- **Detection Method:** Formatter tools
- **Toolkit Manager:** Formatting validation
- **Deliverable:** `reports/phase4.6-formatting.md`

#### 4.7: Documentation Cleanup (Category 5 - 2+ tasks)
- **4.7.1:** Update code comments (explain WHY, not WHAT)
- **4.7.2:** Ensure all visualizations have ARIA labels (WCAG 2.1 AA)
- **Toolkit Manager:** Documentation quality check
- **Deliverable:** `reports/phase4.7-documentation.md`

#### 4.8: Cross-Browser Testing
- Test in Chrome, Firefox, Safari, Edge
- Validate all responsive breakpoints (375px/768px/1440px)
- **Toolkit Manager:** Cross-browser compatibility report
- **Deliverable:** `reports/phase4.8-cross-browser.md`

#### 4.9: Performance Benchmarks
- Measure page load times (target <2s)
- Validate GPU acceleration for glassmorphism effects
- Check Lighthouse scores (>90 for Performance, Accessibility, SEO)
- **Toolkit Manager:** Performance validation
- **Deliverable:** `reports/phase4.9-performance.md`

#### 4.10: Accessibility Audit
- Run WCAG 2.1 AA compliance check
- Validate keyboard navigation
- Test screen reader compatibility
- **Toolkit Manager:** Accessibility compliance report
- **Deliverable:** `reports/phase4.10-accessibility.md`

#### 4.11: Whole-File REFACTOR (SKULL Rule - Final Sweep)
- Review every modified file for code quality
- Validate HTML5 compliance (W3C validator)
- Ensure consistent naming conventions
- Final validation sweep (all checks pass)
- **Toolkit Manager:** Final compliance certification
- **Deliverable:** `reports/phase4.11-refactor-final.md`

#### 4.12: Final Certification
- **Toolkit Manager:** Issues final compliance certificate
- All 151+ files meet glassmorphism-design-standard.md v4.0.1
- ZERO violations, ZERO warnings
- **Deliverable:** `reports/phase4.12-final-certification.md`

**Total Phase 4 Tasks:** 18+ (comprehensive cleanup)

---

## 🎉 Project Completion

**Status:** ✅ All 4 phases complete  
**Files Standardized:** 151+  
**Validation Authority:** Toolkit Manager  
**Compliance Score:** 10.0/10.0

---

## 📊 Success Metrics

**Target Outcomes:**
- **Pass Rate:** 100%
- **Critical Issues:** 0
- **Level 3 Files:** 0
- **Inline Styles:** 0
- **Mobile-Friendly:** 100% of pages (375px/768px/1440px)
- **Working Links:** 100% validation
- **Toolkit Manager Certification:** PASS

---

## 🎨 Design Standards Reference

### glassmorphism-design-standard.md v4.0.1 Requirements

**Animation Tiers:**
- **T1 (Subtle)**: ALL Level 1 & Level 2 pages - `0.2-0.3s` transitions only
- **T2 (Accent)**: Interactive element feedback - `0.1-0.2s`
- **T3 (Dramatic)**: ONLY Level 0 (docs/index.html hero) - `2-10s` keyframe animations

**Clickable vs Non-Clickable:**
- **Clickable**: Glowing border + lift (`translateY(-2px)`) + `cursor: pointer`
- **Non-Clickable**: Glass reflection (8s animation) + `cursor: default` + NO glow

**Pattern Usage:**
- **Pattern 15**: Level 0 Multi-Panel (Security, Orchestrators, STS)
- **Pattern 8-14**: Level 2 tile-specific patterns

### Header/Footer Standardization

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

**Level 1 & Level 2 Header (NO LOGO - Navigation Only):**
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

## 📋 Micro-Batch Strategy (Prevent Length Limit Errors)

**Per Batch:**
1. Create 2-3 files maximum
2. Validate immediately (visual + Toolkit Manager verification)
3. Fix any violations
4. Re-validate (must pass)
5. Document completion
6. Proceed to next batch

**Why 2-3 Files:**
- Single operation token limit ≈ 400-500 lines of code/content
- Prevents "Sorry, I can't assist with that" length limit errors
- Enables incremental validation and faster feedback loops
- Proven effective in Phase 1.1 CSS extraction (1,673 lines split into 4 batches)

---

## 🔗 Key References

- **Design Standard:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` v4.0.1
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml`
- **Response Templates:** `cortex-brain/response-templates-v4.yaml`
- **CORTEX Entry Point:** `.github/prompts/CORTEX.prompt.md`

---

## copilot_instructions

**Execution Metadata for CORTEX AI Assistant:**

```yaml
plan_type: level_based_recursive_implementation
response_template: guided_execution_progress
tdd_enforcement: false  # Visual validation instead
final_refactor_required: true
refactor_comprehensiveness:
  minimum_tasks: 18
  categories:
    - orphaned_code_removal: 3
    - code_duplication_elimination: 4
    - dead_code_removal: 3
    - formatting_standardization: 3
    - documentation_cleanup: 2
micro_batch_size: 2-3 files
validation_gate: per_batch
quality_gate: per_phase
validation_authority: toolkit_manager
autonomy_level: guided  # CORTEX executes, Toolkit Manager validates

skull_rules_enforced:
  - HOLISTIC_DISCOVERY
  - NO_INLINE_STYLES
  - RESPONSIVE_MANDATORY
  - HEADER_FOOTER_STANDARD
  - NO_LEVEL_3
  - CREATE_FROM_SCRATCH
  - GIT_ISOLATION
  - REFACTOR_CODE_CLEANUP_ENFORCEMENT
  - MICRO_BATCH_STRATEGY
  - TOOLKIT_MANAGER_VALIDATION

validation_requirements:
  baseline_established: true
  per_batch_validation: true
  per_phase_validation: true
  final_comprehensive_validation: true
  zero_violations_required: true
  visual_verification: true
  toolkit_manager_certification: true

level_based_execution:
  enabled: true
  phase_structure:
    phase1: level_0_complete  # All 9 tiles on home page
    phase2: level_1_complete  # All 13 hub pages
    phase3: level_2_complete  # All 137+ detail pages
    phase4: final_refactor_and_certification
  completion_criteria: toolkit_manager_certification_passes
  proceeding_criteria: zero_violations_per_level

governance_compliance:
  score_target: 10.0/10
  brain_protection_alignment: true
  toolkit_manager_validation: true
  planning_orchestrator_engaged: false  # Human-guided execution
```

---

**End of Master Plan v6.0.0 - Level-Based Recursive**
