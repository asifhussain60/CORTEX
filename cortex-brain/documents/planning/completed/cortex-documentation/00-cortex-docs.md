# 🛡️ 🗺️ CORTEX Documentation Site - Master Specifications (INDEX) (V5 Migration)

**Plan ID:** cortex-documentation  
**Feature:** 🗺️ CORTEX Documentation Site - Master Specifications (INDEX)  
**Created:** January 03, 2026 | **Migrated to V5:** January 03, 2026  
**Complexity:** TIER 3 (MODERATE)  
**Strategy:** Implementation with Master Orchestrator integration (Phase 4 LIVE)  
**Estimated Duration:** TBD (to be refined during Phase 0)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ MIGRATED - READY TO START

### Implementation Phases

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| -1 | Knowledge Library Review | `░░░░░░░░░░` | 2h | ⏸️ Not Started |
| 0 | Foundation & AST Scan | `░░░░░░░░░░` | TBD | ⏸️ Not Started |

**📝 Note:** This plan was migrated from V4 to V5 architecture. Original phases preserved below.

---

## 🎯 Executive Summary

### Migration Context

This plan was automatically migrated from Planning System V4 to V5. Key enhancements:

1. **Master Orchestrator Integration** (✅ LIVE - Phase 4): Pattern-based routing and state coordination
2. **Cross-Session Context** (✅ LIVE - Phase 4.5): Automatic continuation from Tier 1 Working Memory (<200 tokens)
3. **AST-Based Analysis**: Phase 0 code scanning for comprehensive discovery
4. **Governance Integration**: Tier 0 brain-protection-rules.yaml compliance (61 rules)
5. **Knowledge Graph Queries**: Tier 2 knowledge reuse and pattern matching

### Master Orchestrator Status (Phase 4 Complete)

**OPERATIONAL FEATURES:**
- ✅ Pattern Router: Machine-readable intent routing (90%+ accuracy)
- ✅ State Manager: Cross-phase state persistence via PlanningStateDB
- ✅ Execution Engine: Autonomous phase execution with monitoring
- ✅ Context Middleware: Tier 1 integration for "continue" commands

**USAGE:**
- Say "continue cortex-documentation" → Master Orch routes automatically
- Say "cortex-documentation status" → Query current phase/progress
- Pattern matching handles plan names, phase numbers, common variations

### Original Plan Content

The original V4 plan content has been preserved below for reference. During Phase 0 execution, the Master Orchestrator will:

- Analyze the original phases and tasks
- Generate V5-compliant phase breakdown with proper structure
- Add Foundation (Phase 0) and Knowledge Library (Phase -1)
- Integrate REFACTOR phase (final phase)
- Update progress tracking with visual bars

---

## 🔄 Migration Status

**Migrated:** 2026-01-03 11:02:53  
**Original Structure:** V4 (4 subfolders)  
**New Structure:** V5 (6 subfolders + architecture/ + phases/)  
**Backup Location:** `backups/cortex-documentation_v4_backup_*`

---

## 📋 V4 Original Content (PRESERVED FOR REFERENCE)

# 🗺️ CORTEX Documentation Site - Master Specifications (INDEX)

**Version:** 4.2.4 | **Status:** 🎯 EFFICIENCY-OPTIMIZED + ICON-FIX-COMPLETE  
**Author:** Asif Hussain | **Last Updated:** January 3, 2026 (Font Awesome Icon Fix)  
**Copyright © 2026 Asif Hussain. All rights reserved.**

**🔒 CSS BACKUP:** `backups/css-backup-20260103_093835/` - Restore missing styles from here!
**🎨 ICON FIX:** 1,392 icons fixed across 213 files (Font Awesome 6.x compliance)

---

## 🚨 MANDATORY DESIGN COMPLIANCE (READ FIRST)

**⛔ CRITICAL: ALL implementations MUST follow glassmorphism-design-standard.md v4.2.3**

**Reference File:** `cortex-brain/documents/standards/glassmorphism-design-standard.md`

### 100% Compliance Requirements (NON-NEGOTIABLE)

| Rule | Requirement | Enforcement |
|------|-------------|-------------|
| **1. Zero Inline Styles** | NO `style=""` attributes anywhere | ❌ FORBIDDEN |
| **2. Animation Tier** | Level 0 (Home) → T3 allowed / Level 1+ → T1 ONLY | 🎯 MANDATORY |
| **3. Clickable Elements** | `.glass-card-clickable` + `.animation-t1` + glow + lift + pointer | ✅ REQUIRED |
| **4. Display Elements** | `.glass-card-display` + static reflection + default cursor | ✅ REQUIRED |
| **5. Multi-Panel Grids** | 4 categories → 2x2 / 5 categories → 2x3 / 6 categories → 3x2 | 📐 STRICT |
| **6. Spacing** | Cards: `var(--space-lg)` / Grids: `var(--space-lg)` gap / Sections: `var(--space-2xl)` | 📏 MANDATORY |
| **7. Responsive** | 375px mobile / 768px tablet / 1440px desktop breakpoints | 📱 REQUIRED |
| **8. Accessibility** | WCAG 2.1 AA / ARIA labels / keyboard navigation / reduced motion | ♿ MANDATORY |
| **9. Font Awesome 6.x** | All icons require style prefix (`fas`/`far`/`fab`/`fal`/`fad`) + icon name | 🎨 REQUIRED |

### Quick Reference Decision Tree

```
Creating a page?
├── Is it Level 0 (Home)?
│   ├── YES → T3 animations allowed (dramatic effects OK)
│   └── NO → T1 animations ONLY (subtle lift + glow)
├── Is element clickable?
│   ├── YES → .glass-card-clickable + .animation-t1 + cursor: pointer
│   └── NO → .glass-card-display + cursor: default
└── Multi-panel needed (4+ categories)?
    ├── 4 categories → .grid-2x2 (Security)
    ├── 5 categories → .grid-2x3 (Orchestrators)
    └── 6 categories → .grid-3x2 (Sharpen The Saw)
```

### Pre-Implementation Checklist

**BEFORE writing ANY HTML/CSS, confirm:**
- [ ] Read `glassmorphism-design-standard.md` sections relevant to page type
- [ ] Identified correct pattern (Standard Tile vs Multi-Panel)
- [ ] Selected correct CSS classes (`.glass-card-clickable` vs `.glass-card-display`)
- [ ] Confirmed animation tier (T1 for Level 1+, T3 for Level 0 only)
- [ ] Planned responsive breakpoints (375px, 768px, 1440px)
- [ ] Verified zero inline styles policy

**AFTER implementation, validate:**
- [ ] Zero inline `style=""` attributes (search codebase)
- [ ] All clickable elements have `.animation-t1` + pointer cursor
- [ ] All display elements have `.glass-card-display` + default cursor
- [ ] Spacing uses CSS variables (`var(--space-lg)`, etc.)
- [ ] Responsive design tested at all 3 breakpoints
- [ ] ARIA labels on all interactive elements

**Validation Command:**
```bash
# Check for forbidden inline styles
grep -r 'style="' docs/**/*.html

# Expected output: No matches (clean)
```

---

## 🎯 Purpose

Master specification for CORTEX documentation site across Level 1 pages and Level 2 phase deep-dives.

**OLD (v3.3.0):** Single file (1,682 lines) ❌ BLOAT  
**NEW (v4.2.0):** Index + 10 modular specs (180 lines) + efficiency-based priorities ✅ OPTIMIZED

**Current State (v4.2.2):** 318 HTML files total (151 active + 167 stubs)
- **Documentation Cleanup (Jan 3, 2026):** 42 orphaned files archived, 7 new stub pages created
- **Broken Links:** Reduced from 181 → 129 (28% improvement)
- **Link Quality:** Most remaining broken links are legitimate WIP (stub → future content)

**🚀 NEW: Efficiency-First Prioritization:**
- **QUICK WINS** (10h): Orchestrators cleanup → Immediate 73% → 91% completion
- **HIGH VALUE** (58 pages): Learning Hub → Junior developer training platform
- **HIGH EFFORT** (54h): Security pages → Deferred for strategic planning

**Key Benefits:**
- ✅ **89% size reduction** in main index file
- ✅ **Modular loading** - Load only what you need
- ✅ **Faster performance** - 3.4s faster load time
- ✅ **Easier maintenance** - Edit concerns independently
- ✅ **Zero breaking changes** - Entry point path unchanged

---

## 📊 EFFICIENCY-BASED PRIORITY MATRIX (v4.2.0)

**Ranking Criteria:** Value/Effort Ratio + Strategic Impact

| Rank | Initiative | Effort | Value | Ratio | Status | Next Action |
|------|-----------|--------|-------|-------|--------|-------------|
| **🥇 #1** | **Orchestrators Cleanup** | 10h | HIGH | **9.0** | 🟡 73% → 91% | Integrate 5 orphan pages + add Master Orchestrator Hub |
| **🥈 #2** | **Learning Hub (Phase 1)** | 20h | VERY HIGH | **8.5** | 🚧 28% → 50% | Implement 22 high-impact Level 2 modules (Python, Testing, Security) |
| **🥉 #3** | **Learning Hub (Phase 2)** | 35h | HIGH | **7.2** | 🚧 50% → 100% | Complete remaining 36 stub modules |
| **#4** | **Security Pages** | 54h | MEDIUM | **4.6** | 🔴 54% → 100% | Create 6 missing pages (Threat Modeling, Incident Response, etc.) |

**Decision Rationale:**
- **Orchestrators (#1):** QUICK WIN - 10 hours for 18% completion gain + unlocks v5.0 Master Hub
- **Learning Hub (#2-3):** HIGHEST VALUE - Junior developer training, 80 interactive modules, 55 learning hours
- **Security (#4):** HIGH EFFORT - Deferred until Learning Hub complete (better ROI)

---

## 📚 Specification Modules (Load on Demand - REORDERED BY PRIORITY)

### Core Specifications (REQUIRED)

**1. Executive Summary** → `level1-specs/core/executive-summary.md`
- Multi-panel status tables
- Implementation priorities  
- Quick reference metrics
- Cross-panel insights

**2. Design Standards** → `level1-specs/core/design-standards.md`
- Glassmorphism v4.0.1 compliance
- Zero inline styles policy
- T1 animation standards
- CSS variable requirements
- Responsive design breakpoints
- Validation checklist

**3. Validation Checklist** → `level1-specs/core/validation-checklist.md`
- Pre-deployment validation scripts
- Success metrics
- Testing procedures
- Automated validation script

---

### Multi-Panel Specifications (PRIORITY ORDER)

**🚨 ALL MULTI-PANEL IMPLEMENTATIONS:** Must follow `glassmorphism-design-standard.md` Multi-Panel Pattern
- **Reference:** Lines 105-158 (Multi-Panel Pattern section)
- **Grid Rules:** 4 categories → 2x2 / 5 categories → 2x3 / 6 categories → 3x2
- **CSS Structure:** `.main-panel-wrapper` (display card) + `.category-panels-grid` + grid modifier
- **Animation:** T1 ONLY for Level 1 pages (`.animation-t1` on `.category-tag` links)

---

**🥇 PRIORITY #1: Orchestrators Multi-Panel** → `level1-specs/multi-panels/orchestrators-panel-spec.md`

**🎨 Glassmorphism Compliance:**
- **Pattern:** Multi-Panel (2x3 grid) - `glassmorphism-design-standard.md` lines 105-158
- **Grid Class:** `.grid-2x3` (5 categories: Planning, Execution, System, Analysis, Debug)
- **Wrapper:** `.glass-card-display .main-panel-wrapper` (non-clickable outer card)
- **Links:** `.category-tag .animation-t1` (clickable with T1 hover effects)
- **Spacing:** `gap: var(--space-lg)` between all panels

**Technical Details:**
- **Pages:** 22 (20 active, 2 stubs) - includes Master Orchestrator Hub (NEW v5.0)
- **Categories:** 5 (Planning, Execution, System, Analysis, Debug)
- **Orphans:** 5 pages need integration (cortex-debug.html, cortex-onboarding.html, etc.)
- **Status:** 🟡 73% → 91% (target)
- **Effort:** 10 hours (QUICK WIN)
- **Value/Effort:** **9.0** (HIGHEST)
- **Next:** Integrate orphans + add Master Hub visualizations

---

**🥈 PRIORITY #2: Best Practices Learning Hub** → `level1-specs/learning-hub/best-practices-learning-spec.md`

**🎨 Glassmorphism Compliance:**
- **Pattern:** Standard Tile + Guideline Cards - `glassmorphism-design-standard.md` lines 1415-1497
- **Tile Class:** `.glass-card-clickable .animation-t1` (domain hub navigation)
- **Guideline Cards:** `.guideline-card` (display cards with glass reflection)
- **Code Blocks:** `background: rgba(0, 0, 0, 0.3)` with proper padding
- **Spacing:** `margin-bottom: var(--space-lg)` between stacked guideline cards

**Technical Details:**
- **Level 1 Pages:** 17 (domain hubs)
- **Level 2 Pages:** 80 (interactive learning modules) - 22 implemented, 58 stubs
- **Structure:** 3-6 modules per domain (Beginner → Expert)
- **Features:** D3.js visualizations, code playgrounds, quizzes, challenges
- **Total Learning Hours:** 55 hours
- **Status:** 🚧 28% → 100% (target)
- **Effort:** Phase 1 (20h) + Phase 2 (35h) = 55 hours total
- **Value/Effort:** **8.5** (Phase 1), **7.2** (Phase 2)
- **Strategic Value:** Junior developer training platform, onboarding acceleration

---

**#3: Security Multi-Panel** → `level1-specs/multi-panels/security-panel-spec.md`

**🎨 Glassmorphism Compliance:**
- **Pattern:** Multi-Panel (2x2 grid) - `glassmorphism-design-standard.md` lines 105-158
- **Grid Class:** `.category-panels-grid` (default 2x2 for 4 categories)
- **Categories:** Protection, Assessment, Compliance, Response
- **Wrapper:** `.glass-card-display .main-panel-wrapper`
- **Links:** `.category-tag .animation-t1`

**Technical Details:**
- **Pages:** 16 (10 active, 6 stubs) - includes stub index
- **Categories:** 4 (Protection, Assessment, Compliance, Response)
- **Visualizations:** 26+ (Mermaid + D3.js)
- **Status:** 🔴 54% → 100% (target)
- **Effort:** 54 hours (HIGH EFFORT)
- **Value/Effort:** **4.6** (DEFERRED)
- **Next:** Strategic planning after Learning Hub complete

---

**#4: Sharpen The Saw Multi-Panel** → `level1-specs/multi-panels/sharpen-saw-panel-spec.md`

**🎨 Glassmorphism Compliance:**
- **Pattern:** Multi-Panel (3x2 grid) - `glassmorphism-design-standard.md` lines 160-168
- **Grid Class:** `.grid-3x2` (6 categories in 3 columns × 2 rows)
- **Single-Link Optimization:** `.single-tag` compact styling (each category has 1 link)
- **Categories:** Security, SOLID, Code Quality, Performance, Testing, Documentation
- **Spacing:** `row-gap: var(--space-lg)` to prevent cramped rows

**Technical Details:**
- **Pages:** 6 (6 existing, 100% complete)
- **Categories:** 6 (Security, SOLID, Code Quality, Performance, Testing, Documentation)
- **Status:** 🟢 100% complete - MAINTENANCE ONLY
- **Priority:** LOW (no work needed)

---

### Implementation Guides (OPTIONAL - Planned v4.1.0)

**7. Page Creation Guide** → `level1-specs/implementation/page-creation-guide.md` *(Planned)*
**8. Visualization Guide** → `level1-specs/implementation/visualization-guide.md` *(Planned)*
**9. CSS Integration Guide** → `level1-specs/implementation/css-integration-guide.md` *(Planned)*

---

### Metadata (REFERENCE)

**10. Version History** → `level1-specs/metadata/version-history.md`
**11. References** → `level1-specs/metadata/references.md`

---

## 🔗 Load Order (EFFICIENCY-OPTIMIZED)

### Priority #1: Orchestrators Cleanup (QUICK WIN - 10h)

**Goal:** 73% → 91% completion in 10 hours

**🚨 DESIGN COMPLIANCE:** Follow `glassmorphism-design-standard.md` v4.1.1
- **Pattern:** Multi-Panel (2x3 grid for 5 categories)
- **CSS Classes:** `.main-panel-wrapper`, `.category-panels-grid`, `.grid-2x3`
- **Animation:** T1 ONLY (clickable: glow + lift / display: static)
- **Spacing:** `gap: var(--space-lg)` (24px between panels)
- **Zero inline styles:** ALL styling via CSS classes

**Workflow:**
1. **READ FIRST:** `glassmorphism-design-standard.md` (Multi-Panel Pattern section)
2. Load Executive Summary → Orchestrators Panel Spec
3. Integrate 5 orphan pages into navigation
4. Add Master Orchestrator Hub (v5.0) with Pattern Router, State Manager, Execution Engine
5. **VALIDATE:** Zero inline styles, T1 animations, responsive design (375px/768px/1440px)
6. Run automated validation script

**Expected Outcome:** Fully navigable 22-page orchestrator ecosystem with v5.0 Master Hub

### Priority #2: Learning Hub Phase 1 (HIGH VALUE - 20h)

**Goal:** 28% → 50% completion (implement 22 high-impact modules)

**🚨 DESIGN COMPLIANCE:** Follow `glassmorphism-design-standard.md` v4.1.1
- **Pattern:** Standard Tile + Best Practices Guideline Cards
- **CSS Classes:** `.glass-card-clickable`, `.animation-t1`, `.guideline-card`
- **Animation:** T1 ONLY (0.2-0.3s transitions, subtle lift on hover)
- **Spacing:** `margin-bottom: var(--space-lg)` between stacked cards
- **Accessibility:** ARIA labels, keyboard navigation, WCAG 2.1 AA

**Workflow:**
1. **READ FIRST:** `glassmorphism-design-standard.md` (Pattern 11: Best Practices Guideline Cards)
2. Load Executive Summary → Best Practices Learning Spec
3. Identify 22 highest-value modules (Python, Testing, Security, Performance)
4. Implement D3.js visualizations + code playgrounds (following design standard patterns)
5. Add quizzes + challenges with `.glass-card-clickable` styling
6. **VALIDATE:** Responsive design, zero inline styles, T1 animations only

**Expected Outcome:** Functional junior developer training platform (50% coverage)

### Priority #3: Learning Hub Phase 2 (COMPLETION - 35h)

**Goal:** 50% → 100% completion (implement remaining 36 modules)

**🚨 DESIGN COMPLIANCE:** Follow `glassmorphism-design-standard.md` v4.1.1
- **Consistency:** Match Phase 1 patterns (Standard Tile + Guideline Cards)
- **Advanced Visuals:** D3.js charts following glassmorphism patterns
- **Performance:** <2s render, <100ms interaction, GPU acceleration
- **Mobile-first:** 375px base with responsive breakpoints

**Workflow:**
1. **REFERENCE:** Phase 1 implementations for consistency
2. Complete remaining stub modules across all 17 domains
3. Add advanced visualizations (Sankey, Force Graphs, Heatmaps) with glassmorphism styling
4. Implement progress tracking + gamification (`.glass-card-clickable` for interactive elements)
5. **VALIDATE:** Full validation + performance testing + accessibility audit

**Expected Outcome:** Complete 80-module learning platform (55 learning hours)

### Priority #4: Security Pages (DEFERRED - 54h)

**Goal:** 54% → 100% completion

**🚨 DESIGN COMPLIANCE:** Follow `glassmorphism-design-standard.md` v4.1.1
- **Pattern:** Multi-Panel (2x2 grid for 4 categories)
- **CSS Classes:** `.main-panel-wrapper`, `.category-panels-grid` (default 2x2)
- **Categories:** Protection, Assessment, Compliance, Response

**Workflow:** Defer until Learning Hub complete (better ROI)

---

## 📊 Performance Metrics (v4.0.0 vs v3.3.0)

| Metric | v3.3.0 (Monolithic) | v4.0.0 (Modular) | Improvement |
|--------|---------------------|------------------|-------------|
| **Main file size** | 1,682 lines | 180 lines | **89% reduction** ✅ |
| **Context load (Security)** | ~1,682 lines | ~1,180 lines | **30% reduction** ✅ |
| **Context load (Orchestrators)** | ~1,682 lines | ~1,280 lines | **24% reduction** ✅ |
| **Load time (estimated)** | 5.2s | 1.8s | **3.4s faster** ✅ |
| **Maintainability** | Monolithic | Modular | **Isolated edits** ✅ |
| **Merge conflict risk** | HIGH | LOW | **90% reduction** ✅ |

---

## 📋 Invocation (Unchanged from v3.3.0)

**✅ ZERO BREAKING CHANGES**

All references to `00-master-plan.md` work identically - no consumer updates required.

**Entry Point:** `cortex-brain/documents/planning/active/cortex-documentation/artifacts/00-master-plan.md` (THIS FILE)

---

## ✅ Migration Notes (v3.3.0 → v4.0.0)

### What Changed
✅ **Structure:** Monolithic → Modular (10 files)  
✅ **Performance:** 89% smaller index file  
✅ **Load Strategy:** On-demand module loading  
✅ **Validation:** Comprehensive script added  

### What Stayed the Same
✅ **Entry Point:** Same file path (no breaking changes)  
✅ **Content:** 100% preserved (all sections intact)  
✅ **References:** No consumer updates needed  
✅ **Commands:** All invocations unchanged  

### Archive Location
Original v3.3.0 moved to: `cortex-brain/archives/Level1-spec-v3.3.0.md`

---

## 🚀 Quick Start

### For New Users
1. Read this index (you are here)
2. Load Executive Summary for overview
3. Load specific panel spec for your work
4. Reference Design Standards as needed

### For Implementers
1. Load Security/Orchestrators/Sharpen Saw spec
2. Follow page creation patterns
3. Validate with checklist before deployment
4. Run automated validation script

### For Maintainers
1. Edit only the relevant module file
2. No need to touch other modules
3. Reduced merge conflicts
4. Faster reviews

---

## 📚 Document Overview

**Current State:** 311 HTML files (151 active + 160 stubs) across 10 tiles (7 standard + 3 multi-panels)  
**Level 1 Status:** 62/62 complete (100%)  
**Level 2 Status:** 22/80 implemented (28%), 58 have stub pages (100% stub coverage)  
**v5.0 Architecture (NEW):** Master Orchestrator Hub + Planning v5 (10 Level 2 pages) + ADO v2 (13 Level 2 pages) - 24 pages total

**Standard Tiles (Level 1 + Level 2):**
- Architecture: 10 pages (Score: 45) - 3 active, 2 archived (brain-tiers, development-context), 5 stubs (four-tier-brain, orchestrator-ecosystem, agent-system, working-memory, multi-repo)
- Token Optimization: 1 page (Score: 25) - 97% reduction, $8.6K savings, Cross-Session Context integration
- Best Practices Hub: 17 Level 1 hubs + 80 Level 2 modules (Score: 35) - 22 implemented, 58 stubs (55 learning hours)
- Toolkit Manager: 1 page (Score: 20) - Master Orchestrator routing layer, Pattern Matching, LLM Fallback
- CORTEX Lens: 1 page (Score: 30) - AST analysis, reverse engineering
- Getting Started: 5 pages (Score: 15) - 2 active (index, tutorial), 3 stubs (multi-repo-setup, first-commands, deployment)
- Story: 15 pages - 1 viewer, 1 stub index, 14 chapters archived (pending navigation integration)

**Multi-Panel Tiles:**
- **Security:** 16 pages (Score: 55) - 10 active, 6 stubs, 1 stub for index (63% complete)
- **Orchestrators:** 22 pages (Score: 75) - 20 active, 2 stubs (91% complete) + **Master Orchestrator Hub (NEW - v5.0)**
- **Sharpen The Saw:** 6 pages (Score: 40) - 6/6 complete (100%)

**v5.0 Architecture Pages (NEW - High Priority):**
- **Master Orchestrator Hub:** 1 Level 1 page + 4 component deep-dives (Pattern Router, State Manager, Execution Engine, LLM Fallback) - Score: 120
- **Planning v5 (Level 2):** 1 Level 1 hub + 10 phase pages (Phase 0-4 Bootstrap, Phase 5-9 Migration, Phase 10 Refactor) - Score: 195
- **ADO v2 (Level 2):** 1 Level 1 hub + 13 feature pages (Wizard, Work Items, Sprints, Vision API, Templates, etc.) - Score: 178

**v5.0 Planned:** Planning v5 (10 Level 2 pages, Score: 195) + ADO v2 (13 Level 2 pages, Score: 178) with comprehensive visualizations

**Complexity Formula:** `Score = (Viz × 10) + (Mermaid × 5) + (D3.js × 1) + (Interactive × 3) + (Data × 8) + (Animations × 4)`

**Architecture Decision:** Level 2 required when scores >100 (Planning v5, ADO v2 with comprehensive D3.js/Mermaid). See `integrate-this.md` for full specifications.

**All details in modular files for efficient loading.**

---

## 🎯 Level 1/2 Specification Generation Methodology (v4.1.0)

**Purpose:** Standardize comprehensive specifications with D3.js/Mermaid visualizations and acceptance criteria.

**Reference:** `integrate-this.md` (1,625 lines - COMPLETE implementation guide)

**Required Per Level 1 Page (Score >50):**
- **6-12 D3.js Interactive Charts:** Timeline, Force Graph, Heatmap, Bar/Line, Sankey, Radial Tree
- **4-8 Mermaid Diagrams:** Sequence, Flowchart, State, C4 Context, ER Diagram, Gantt
- **Full Implementation Code:** 200+ lines D3.js classes with event handlers, data loading
- **Acceptance Criteria:** Success Conditions, Validation Gates, Rollback Triggers, Test Coverage
- **Performance Benchmarks:** <2s render, <100ms interaction, WCAG 2.1 AA compliance

**Architecture Decision (v4.1.0):**
- **Scores 0-99:** Level 1 only (basic/moderate visualizations)
- **Scores 100+:** Level 1 + Level 2 breakdown (Planning v5: 195, ADO v2: 178)

**Current State:** 9 basic tiles (scores 15-75) fit Level 1  
**v5.0 State:** Planning v5 (10 phase pages) + ADO v2 (13 pages) require Level 2

### Complexity Scoring Algorithm

**Formula:**
```
Complexity Score = (Visualization Containers × 10) + 
                   (Mermaid Diagrams × 5) + 
                   (D3.js Function Calls × 1) + 
                   (Interactive Elements × 3) + 
                   (Data Sources × 8) + 
                   (Animation Sequences × 4)
```

**Thresholds:**
- **0-49:** Simple feature (1-2 visualizations) → Level 1 appropriate
- **50-99:** Complex feature (3-5 visualizations) → Level 1 with rich content
- **100-199:** Very complex (6-10 visualizations) → Level 2 breakdown required
- **200+:** Extremely complex (10+ visualizations) → Level 2 + tabs/accordions

**CORTEX Tile Scores:**
| Tile | Score | Level 1? | Rationale |
|------|-------|----------|-----------|
| Getting Started | 15 | ✅ YES | Simple setup guide |
| Toolkit Manager | 20 | ✅ YES | Basic tool concepts |
| Token Optimization | 25 | ✅ YES | Metrics + 2 Mermaid |
| CORTEX Lens | 30 | ✅ YES | Dashboard concepts |
| Best Practices | 35 | ✅ YES | 17 domain pages, minimal viz |
| Sharpen The Saw | 40 | ✅ YES | 6 categories, simple content |
| Architecture | 45 | ✅ YES | 5 Mermaid diagrams |
| Security | 55 | ✅ YES | 4 categories, moderate Mermaid |
| Orchestrators | 75 | ✅ YES | 5 categories, borderline but acceptable |

**Design Pattern:** Use tabs, accordions, or expandable sections within Level 1 pages for phase details instead of Level 2 hierarchy.

### Required Specification Sections

Every Level 1 spec MUST include:

1. **Executive Summary** - Status tables, key insights, quick reference
2. **Architecture Overview** - Mermaid C4 Context or architecture diagram
3. **Feature Breakdown** - Component hierarchy, complexity analysis
4. **Visualization Specifications** - 6-12 D3.js charts + 4-8 Mermaid diagrams
5. **Acceptance Criteria** - Success metrics, validation gates, testing requirements
6. **Implementation Specification** - HTML structure, CSS requirements, JavaScript integration
7. **Metrics & Analytics** - Performance benchmarks, usage analytics
8. **Deployment Checklist** - Step-by-step verification
9. **References & Dependencies** - Related specs, manifests, code files

### D3.js Visualization Requirements

**Supported Chart Types:**
- Timeline (session history, event sequences)
- Force Graph (dependency networks, relationships)
- Heatmap (usage patterns, optimization)
- Bar/Line Charts (metrics, trends)
- Sankey Diagram (flow analysis)

**Standards:**
- D3.js v7.x required
- Container: `<div id="chart-name-viz"></div>`
- Responsive design (375px, 768px, 1440px breakpoints)
- Performance: <2s render, <100ms interaction
- Accessibility: ARIA labels, keyboard navigation, reduced motion support

### Mermaid Diagram Requirements

**Supported Types:**
- Sequence (workflow steps, API interactions)
- Flowchart (decision trees, process flows)
- State Machine (lifecycle, transitions)
- C4 Context (system architecture)
- ER Diagram (database schema)
- Gantt Chart (project timeline)

**Standards:**
- Container: `<div class="mermaid-container"><pre class="mermaid">...</pre></div>`
- Theme: CORTEX dark theme (colors from CSS variables)
- Responsive: Horizontal scroll for large diagrams

### Acceptance Criteria Template

**Required Categories:**

| Category | Requirements | Test Coverage | Validation Method |
|----------|--------------|---------------|-------------------|
| **Functional** | 5-10 per feature | Unit + Integration | Jest/Pytest |
| **Performance** | 3-5 per feature | Benchmark tests | Performance API |
| **Visual** | 6-8 per feature | Visual regression | Percy/Chromatic |
| **Accessibility** | 5-7 per feature | WCAG 2.1 AA | axe DevTools |

**Structure:**
```markdown
### Acceptance Criteria

#### Success Conditions
- [ ] **SC-1:** [Specific deliverable] exists and passes validation
- [ ] **SC-2:** [Performance metric] meets or exceeds target
- [ ] **SC-3:** [Integration test] passes with 100% success rate

#### Validation Gates
- **Gate 1 (Entry):** Prerequisites met, dependencies resolved
- **Gate 2 (Mid-Phase):** 50% tasks complete, no blocking issues
- **Gate 3 (Exit):** All tasks complete, all tests passing, documentation updated

#### Rollback Triggers
- **Critical:** [Condition requiring immediate rollback]
- **High Priority:** [Condition requiring fix within 24h]
- **Medium Priority:** [Condition requiring fix within 48h]
```

### Quick Start Checklist

**To generate a new Level 1 spec:**

1. [ ] **Identify Enhancement** - Feature name, component area, complexity estimate
2. [ ] **Discovery Analysis** - List visualizations, calculate complexity score
3. [ ] **Create Spec Structure** - Copy template, fill executive summary
4. [ ] **Design Visualizations** - 6-12 D3.js charts, 4-8 Mermaid diagrams
5. [ ] **Write Acceptance Criteria** - Functional, performance, visual, accessibility
6. [ ] **Add Validation Tests** - Jest/Pytest, benchmarks, visual regression
7. [ ] **Document Implementation** - HTML templates, CSS classes, JS initialization
8. [ ] **Define Success Metrics** - Adoption rates, interaction depth, completion rates
9. [ ] **Create Rollback Criteria** - Critical bugs, performance regressions
10. [ ] **Generate Deployment Checklist** - Prerequisites, validation, monitoring

### Validation Requirements

**Before deployment:**
- [ ] Complexity score calculated and documented
- [ ] All visualizations have full D3.js/Mermaid code
- [ ] Acceptance criteria include all 4 categories (functional, performance, visual, accessibility)
- [ ] Performance benchmarks specified (<2s render, <100ms interaction)
- [ ] **🚨 GLASSMORPHISM COMPLIANCE** validated (see checklist below)
- [ ] Responsive design tested (375px, 768px, 1440px)
- [ ] ARIA labels on all interactive elements
- [ ] Deployment checklist includes rollback procedure

---

## 🎨 GLASSMORPHISM VALIDATION CHECKLIST (MANDATORY)

**Reference:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` v4.1.1

### Pre-Deployment Validation (RUN BEFORE EVERY COMMIT)

#### 1. Zero Inline Styles (CRITICAL)
```bash
# Search for forbidden inline styles
grep -r 'style="' docs/**/*.html

# Expected: No matches found (0 results)
# If matches found: Remove ALL inline styles, use CSS classes instead
```

#### 2. CSS Class Validation

**Clickable Elements:**
- [ ] All navigational cards use `.glass-card-clickable`
- [ ] All clickable elements have `.animation-t1`
- [ ] All links in multi-panels use `.category-tag .animation-t1`
- [ ] Hover effects: glow border + `translateY(-2px)` lift
- [ ] Cursor: `pointer` on hover

**Display Elements:**
- [ ] All info panels use `.glass-card-display`
- [ ] Multi-panel wrappers use `.main-panel-wrapper`
- [ ] No hover lift effects on display cards
- [ ] Cursor: `default` (no pointer)

**Multi-Panel Grids:**
- [ ] 4 categories → `.category-panels-grid` (default 2x2)
- [ ] 5 categories → `.category-panels-grid .grid-2x3`
- [ ] 6 categories → `.category-panels-grid .grid-3x2`

#### 3. Animation Tier Compliance

**Level 0 (Home Page):**
- [ ] T3 animations allowed (borderGlowSweep, blobMorph OK)
- [ ] Dramatic effects on hero sections only

**Level 1+ (All Detail Pages):**
- [ ] T1 animations ONLY (0.2-0.3s transitions)
- [ ] NO borderGlowSweep animations
- [ ] NO infinite keyframe animations on clickable elements
- [ ] NO blobMorph effects
- [ ] Simple hover: `transform: translateY(-2px)` + border glow

#### 4. Spacing Validation

**Stacked Cards:**
- [ ] `margin-bottom: var(--space-lg)` between consecutive cards
- [ ] Minimum 24px vertical gap

**Multi-Panel Grids:**
- [ ] `gap: var(--space-lg)` between all panels
- [ ] `row-gap: var(--space-lg)` for 3x2 grids (prevents cramped rows)

**Sections:**
- [ ] `margin-bottom: var(--space-2xl)` after major sections
- [ ] `margin-bottom: var(--space-3xl)` after key features

#### 5. Responsive Design Validation

**Mobile (375px):**
- [ ] Single column layouts
- [ ] Touch-friendly 44px minimum tap targets
- [ ] Stacked navigation
- [ ] Reduced `gap: var(--space-md)` for tighter spacing

**Tablet (768px):**
- [ ] 2-column grids for multi-panels (or 3 columns for 3x2)
- [ ] Horizontal navigation
- [ ] Expanded spacing

**Desktop (1440px):**
- [ ] Full grid layouts (2x2, 2x3, 3x2)
- [ ] Maximum content width: 1400px
- [ ] Wider gaps: `var(--space-2xl)` or `var(--space-3xl)`

#### 6. Accessibility Validation

- [ ] ARIA labels on all interactive elements
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Focus states visible (2px solid accent outline)
- [ ] Reduced motion support: `@media (prefers-reduced-motion: reduce)`
- [ ] Color contrast ≥4.5:1 for text (WCAG 2.1 AA)
- [ ] Screen reader tested (NVDA/JAWS)

#### 7. Performance Validation

- [ ] D3.js visualizations render <2s
- [ ] Hover interactions respond <100ms
- [ ] GPU acceleration enabled (`will-change: transform`)
- [ ] Lazy loading for off-screen images
- [ ] No layout shift (CLS score <0.1)

### Automated Validation Script

```bash
# Run from project root
cd d:/PROJECTS/CORTEX

# Check inline styles (must return 0 results)
echo "=== Checking for inline styles ==="
grep -r 'style="' docs/**/*.html | wc -l

# Check T1 animation usage on Level 1 pages
echo "=== Validating animation tiers ==="
grep -r "animation-t1" docs/**/*.html | grep -v "docs/index.html" | wc -l

# Check responsive breakpoints
echo "=== Validating responsive CSS ==="
grep -r "@media (min-width: 768px)" docs/assets/css/*.css | wc -l
grep -r "@media (min-width: 1440px)" docs/assets/css/*.css | wc -l

# Validate spacing variables
echo "=== Checking spacing variables ==="
grep -r "var(--space-lg)" docs/assets/css/*.css | wc -l
grep -r "var(--space-2xl)" docs/assets/css/*.css | wc -l

echo "=== Validation Complete ==="
```

### Common Violations & Fixes

| Violation | Wrong | Correct |
|-----------|-------|---------|
| Inline styles | `<div style="color: red">` | `<div class="text-error">` |
| Wrong animation tier | `.glass-card::after { animation: borderGlowSweep... }` (Level 1) | Remove animation, use T1 hover only |
| Wrong card class | `<div class="glass-card">` (ambiguous) | `<div class="glass-card-clickable">` or `.glass-card-display` |
| Missing grid modifier | `.category-panels-grid` (5 categories) | `.category-panels-grid .grid-2x3` |
| Hard-coded spacing | `margin-bottom: 24px` | `margin-bottom: var(--space-lg)` |
| Missing hover cursor | `.nav-link:hover {}` | `.nav-link:hover { cursor: pointer; }` |

---

**Next Action:** Load specific multi-panel spec to begin implementation.


---

## 🛡️ Master Orchestrator Integration

### V5 Architecture Components

This plan now integrates with:

1. **Pattern Router** (`src/orchestrators/pattern_router.py`) ✅ LIVE
   - Machine-readable pattern matching (exact + regex)
   - Intent classification for plan resumption
   - "continue" pattern detection
   - Confidence scoring (HIGH/MEDIUM/LOW thresholds)

2. **State Manager** (`src/orchestrators/state_manager.py`) ✅ LIVE
   - Cross-phase state persistence via PlanningStateDB
   - Checkpoint creation and restoration
   - Plan metadata tracking
   - Phase status management

3. **Execution Engine** (`src/orchestrators/execution_engine.py`) ✅ LIVE
   - Autonomous phase execution
   - Progress tracking and validation
   - Execution monitoring with metrics
   - Error handling and recovery

4. **Context Middleware** (`src/operations/utilities/cross_session_context_middleware.py`) ✅ LIVE
   - Tier 1 Working Memory integration
   - Last 3 sessions context injection (<200 tokens)
   - Continuation intelligence (auto-resume)
   - Session metadata tracking

### Cross-Session Continuation (Phase 4.5 LIVE)

When you say **"continue"**, the Master Orchestrator will:

1. Query Tier 1 for last session metadata (orchestrator_used, primary_intent)
2. Load this plan's current state from PlanningStateDB
3. Resume from last incomplete phase
4. Inject lightweight context (<200 tokens)

**Session Tracking Path:** `cortex-brain/tier1-working-memory/sessions/`

**Usage Examples:**
- `"continue"` → Auto-detects last plan from Tier 1
- `"continue cortex-documentation"` → Explicit plan selection
- `"cortex-documentation status"` → Check progress without executing

---

## ⛔ MANDATORY V5 Requirements

### Phase -1: Knowledge Library Review (NEW IN V5)

**REQUIRED BEFORE Phase 0:**

Review existing CORTEX knowledge for similar patterns:

- `cortex-brain/tier2-knowledge-graph/patterns/` - Established design patterns
- `cortex-brain/lessons-learned.yaml` - Historical insights
- `cortex-brain/tier2-knowledge-graph/code-patterns/` - Reusable implementations

**Deliverables:**
- `context/knowledge-library-review.md` - Relevant patterns found
- `context/reuse-opportunities.md` - Code/patterns to reuse

### Phase 0: Foundation & AST Scan (NEW IN V5)

**REQUIRED BEFORE original Phase 1:**

1. **AST Code Analysis:**
   - Scan all Python files in scope
   - Map imports, dependencies, function signatures
   - Identify potential conflicts or duplication

2. **Governance Compliance Check:**
   - Validate against brain-protection-rules.yaml (61 rules)
   - Check TDD_ENFORCEMENT, GIT_ISOLATION, PLANNING_ISOLATION

3. **Architecture Baseline:**
   - Document current state before changes
   - Identify integration points with Master Orchestrator

**Deliverables:**
- `context/ast-scan-results.json` - Full code analysis
- `context/governance-compliance.md` - SKULL rules validation
- `architecture/integration-points.md` - Master Orch touchpoints

### Final Phase: REFACTOR & Cleanup (NEW IN V5)

**REQUIRED AFTER all implementation phases:**

Comprehensive cleanup to prevent technical debt:

1. **Orphaned Code Detection:**
   - Find unused imports, functions, variables
   - AST-based dead code analysis

2. **Duplicate Code Removal:**
   - Identify copy-paste patterns
   - Consolidate into shared utilities

3. **≥18 Cleanup Tasks per File Category:**
   - Test files cleanup
   - Implementation files optimization
   - Configuration files validation

**SKULL Rule Enforcement:** `REFACTOR_CLEANUP` (brain-protection-rules.yaml)

---

## 📚 V5 Resources

| Resource | Path | Purpose |
|----------|------|---------|
| Master Plan (this file) | `00-MASTER-PLAN-V5.md` | Central coordination |
| Master Orchestrator Config | `cortex-brain/config/master-orchestrator.yaml` | Routing rules ✅ LIVE |
| Planning State DB | `cortex-brain/database/planning_state.db` | State persistence ✅ LIVE |
| Brain Protection Rules | `cortex-brain/brain-protection-rules.yaml` | Governance (61 rules) |
| Knowledge Graph | `cortex-brain/tier2-knowledge-graph/` | Pattern library |
| Continuation Prompt | `CONTINUATION-PROMPT-PHASE-*.md` | Session resumption ✅ LIVE |

---

## 🚀 Next Steps

1. **Review Migration**: Verify V5 structure is correct
2. **Execute Phase -1**: Review Knowledge Library for reusable patterns
3. **Execute Phase 0**: Run AST scan + governance check + baseline
4. **Resume Original Work**: Continue with original Phase 1 (now Phase 1 in V5)
5. **Execute REFACTOR Phase**: Final cleanup after all implementation

**To begin:** Say "start Phase -1" or "continue" in CORTEX Chat (Master Orch will route automatically)

---

## 📝 copilot_instructions

```yaml
response_template: "autonomous_execution_progress"
tdd_enforcement: true
final_refactor_required: true
master_orchestrator_enabled: true  # ✅ LIVE (Phase 4)
cross_session_context: true        # ✅ LIVE (Phase 4.5)
knowledge_graph_integration: true
governance_validation: true
```

**Template Reference:** `cortex-brain/response-templates-v4.yaml:863`  
**Planning System Manifest:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`  
**Master Orchestrator Status:** ✅ OPERATIONAL (Phase 4 Complete - routing, state, execution, context)
