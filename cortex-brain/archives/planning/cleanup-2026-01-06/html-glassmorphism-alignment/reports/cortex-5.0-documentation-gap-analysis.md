# 📊 CORTEX-5.0 Documentation Gap Analysis Report

**Analysis Date:** 2026-01-04  
**Analyst:** GitHub Copilot  
**Plan:** html-glassmorphism-alignment (Phase 7a)  
**Scope:** docs/ folder alignment with CORTEX-5.0 implementation

---

## 🎯 Executive Summary

**Status:** **7 CRITICAL GAPS + 9 MISSING DIAGRAMS IDENTIFIED**

### Key Findings

| Gap Category | Count | Priority | Impact |
|--------------|-------|----------|--------|
| **Missing HTML Pages** | 3 | 🚨 CRITICAL | Plan Viewer, Epic/Feature guide, CORTEX-LENS integration |
| **Missing Orchestrator Docs** | 2 | 🔴 HIGH | Refinement + Debug (stub pages exist, no content) |
| **Missing Feature Docs** | 7 | 🟡 MEDIUM | Phase -1, AST, Context, Visual Progress, REFACTOR, Plan Viewer, Epic/Feature |
| **Missing Diagrams** | 9 | 🟡 MEDIUM | Architecture diagrams, decision trees, data flow |
| **Outdated Content** | 7 | 🟠 LOW | Index pages, navigation, cross-references |

**Total Remediation Effort:** +9 hours (expanded Phase 7 from 7h to 9h)

---

## 🆕 CRITICAL GAP #1: Plan Viewer HTML Page (NEW DISCOVERY)

### Problem Statement

**Sub-Plan 11** (CORTEX-LENS Admin Dashboard) defines a static HTML plan viewer that **does not exist** in the docs/ folder.

### Required Page

**Location:** `cortex-lens-output/views/plan-viewer.html`

**Purpose:** Interactive dashboard for plan progress tracking

**Features Required:**
1. **Plan List Sidebar**
   - Search bar (fuzzy matching with Fuse.js)
   - Filter buttons (Active, Completed, All)
   - Dynamically populated from `data/plans-index.json`

2. **Plan Detail View**
   - Plan title + status badge
   - Phase timeline (horizontal swimlanes)
   - Progress bars per phase (color-coded: green/blue/gray)
   - Acceptance criteria checklist (✅⚡⏸️❌)
   - Time tracking (estimated vs. actual with variance)

3. **Cross-Linking to Repository Lens**
   - "View in Repository Lens" buttons
   - Click → Switch tabs + highlight file in AST tree
   - Reverse linking (code → plans)

4. **Glassmorphism Compliance**
   - Must use `.glass-card-clickable`, `.glass-card-display`
   - Must use `.panel-tetris` for metrics
   - Must use `.token-metrics-tetris` for progress tiles
   - Smooth animations (`.animation-t1`)

### Data Schema

**Input:** `cortex-lens-output/data/plans-index.json`

```json
{
  "plans": [
    {
      "id": "html-glassmorphism-alignment",
      "title": "HTML View Glassmorphism Alignment",
      "status": "ACTIVE",
      "created": "2026-01-04",
      "author": "Asif Hussain",
      "duration_estimate": 42,
      "duration_actual": 11,
      "progress": 44,
      "phases": [
        {
          "id": 0,
          "name": "Context Discovery",
          "status": "COMPLETE",
          "progress": 100,
          "duration_estimate": 1,
          "duration_actual": 1,
          "tasks_completed": 5,
          "tasks_total": 5
        }
      ],
      "acceptance_criteria": [
        {
          "id": "AC-1",
          "description": "All HTML files use glassmorphism classes",
          "status": "IN_PROGRESS",
          "validation_method": "Compliance checker script"
        }
      ],
      "linked_files": [
        "docs/index.html",
        "docs/architecture/index.html"
      ]
    }
  ]
}
```

### Implementation Priority

**🚨 CRITICAL** - This is a **new user-facing page** that will be the primary interface for plan monitoring.

### Remediation Steps

1. **Phase 7b: Create `plan-viewer.html`** (1 hour)
   - Build HTML structure (sidebar + detail view)
   - Apply glassmorphism design system
   - Wire up JavaScript (plan-viewer.js)
   - Implement search + filter
   - Add cross-linking buttons

2. **Phase 7b: Update `cortex-lens-output/index.html`** (15 min)
   - Add Plan Viewer tab to navigation
   - Wire up tab switching

3. **Phase 7d: Create architecture diagram** (30 min)
   - Mermaid diagram showing Plan Viewer → data flow
   - Document integration with Repository Lens

---

## 🆕 CRITICAL GAP #2: Epic vs. Feature Planning Workflow Guide

### Problem Statement

**WorkDecomposer** (`src/agents/estimation/work_decomposer.py`) has sophisticated Epic/Feature logic, but **no user documentation exists** explaining when to use Epic planning vs. Feature planning.

### Current Implementation

**Epic Trigger:** `total_story_points >= 21`

```python
# Determine if we need Epic level
needs_epic = total_points >= 21
```

**Epic Structure:** Hierarchical breakdown
- Epic (top level)
  └── Features (2-5 features)
      └── Stories (3-7 stories per feature)
          └── Tasks (2-4 tasks per story)

**Feature Structure:** Flat breakdown
- Feature (top level)
  └── Stories (2-4 stories)
      └── Tasks (2-3 tasks per story)

### Documentation Gap

**Users need guidance on:**
1. When to request Epic planning (large initiatives > 21 SP)
2. When to use Feature planning (smaller work ≤ 21 SP)
3. How story point complexity triggers the decision
4. Examples of Epic vs. Feature use cases

### Required Page

**Location:** `docs/orchestrators/planning-v5-epic-vs-feature.html`

**Sections:**
1. **Epic vs. Feature Decision Tree**
   - Mermaid flowchart with >21 SP threshold
   - Complexity score → Story points mapping
   - Examples at each tier

2. **Epic Planning Workflow**
   - When to use (major features, multi-sprint initiatives)
   - Hierarchical structure breakdown
   - Example: E-commerce platform (Epic with 5 features)

3. **Feature Planning Workflow**
   - When to use (single features, tactical work)
   - Flat structure breakdown
   - Example: User login feature (5 stories)

4. **Story Points Fibonacci Scale**
   - 1, 2, 3, 5, 8, 13, 21, 34, 55 mapping
   - Complexity score → Story points conversion table
   - Guidance on estimation

### Implementation Priority

**🔴 HIGH** - Users currently don't understand when Epic planning activates.

### Remediation Steps

1. **Phase 7b: Create `planning-v5-epic-vs-feature.html`** (1 hour)
   - Write decision tree section with Mermaid diagram
   - Document Epic workflow with examples
   - Document Feature workflow with examples
   - Add story point estimation guide

2. **Phase 7b: Update `docs/orchestrators/planning-v5.html`** (15 min)
   - Add link to Epic vs. Feature guide
   - Reference >21 SP threshold in main docs

3. **Phase 7d: Create decision tree diagram** (30 min)
   - Mermaid flowchart: Complexity → SP → Epic/Feature choice

---

## 📋 GAP CLASSIFICATION BY PRIORITY

### 🚨 PRIORITY 1: CRITICAL (New User-Facing Pages)

| Gap | Type | File | Estimated Time |
|-----|------|------|----------------|
| Plan Viewer HTML | NEW PAGE | `cortex-lens-output/views/plan-viewer.html` | 1h |
| Epic vs. Feature Guide | NEW PAGE | `docs/orchestrators/planning-v5-epic-vs-feature.html` | 1h |
| CORTEX-LENS Nav Update | PAGE UPDATE | `cortex-lens-output/index.html` | 15min |

**Total P1 Time:** 2h 15min

---

### 🔴 PRIORITY 2: HIGH (Orchestrator Documentation)

| Gap | Type | File | Estimated Time |
|-----|------|------|----------------|
| Refinement Orchestrator | CONTENT FILL | `docs/orchestrators/refinement-orchestrator.html` | 1h |
| Debug Orchestrator | CONTENT FILL | `docs/orchestrators/debug-orchestrator.html` | 1h |
| Orchestrators Index | UPDATE | `docs/orchestrators/index.html` (add 2 tiles) | 30min |
| Ecosystem Diagram | UPDATE | Update 8 → 10 orchestrators | 30min |

**Total P2 Time:** 3h

---

### 🟡 PRIORITY 3: MEDIUM (Feature Documentation)

| Gap | Type | File/Section | Estimated Time |
|-----|------|--------------|----------------|
| Phase -1 Knowledge Library | NEW SECTION | `docs/orchestrators/planning-v5.html` | 30min |
| AST Scanning Integration | NEW SECTION | `docs/orchestrators/planning-v5.html` | 30min |
| Context Middleware | NEW PAGE | `docs/features/context-middleware.html` | 45min |
| Visual Progress | NEW SECTION | `docs/orchestrators/planning-v5.html` | 30min |
| REFACTOR Enforcement | NEW SECTION | `docs/governance/skull-rulebook.html` | 30min |

**Total P3 Time:** 2h 45min

---

### 🟠 PRIORITY 4: LOW (Diagrams & Cross-References)

| Gap | Type | Artifact | Estimated Time |
|-----|------|----------|----------------|
| Plan Viewer Architecture | NEW DIAGRAM | Mermaid (architecture + data flow) | 30min |
| Epic vs. Feature Decision Tree | NEW DIAGRAM | Mermaid flowchart | 30min |
| Plan ↔ Lens Cross-Linking | NEW DIAGRAM | Sequence diagram | 30min |
| Phase -1 Flow Diagram | NEW DIAGRAM | Mermaid flowchart | 20min |
| AST Scanning Flow | NEW DIAGRAM | Mermaid flowchart | 20min |
| Context Middleware Priority | NEW DIAGRAM | Sequence diagram | 20min |
| Update cross-references | LINK UPDATE | Multiple files | 20min |

**Total P4 Time:** 2h 50min

---

## 📊 TOTAL REMEDIATION TIME

| Priority | Time | Phases |
|----------|------|--------|
| P1 (Critical) | 2h 15min | Phase 7b |
| P2 (High) | 3h | Phase 7b |
| P3 (Medium) | 2h 45min | Phase 7c |
| P4 (Low) | 2h 50min | Phase 7d |
| **TOTAL** | **10h 50min** | **Phases 7b-7d** |

**Original Phase 7 Estimate:** 7h  
**Updated Phase 7 Estimate:** 9h  
**Actual Needed:** 10h 50min  

**Recommendation:** Phase 7 should be **11 hours** to accommodate Plan Viewer + Epic/Feature guide.

---

## ✅ ACCEPTANCE CRITERIA VALIDATION

### Phase 7a Goals (This Report)

- [x] All 12 CORTEX-5.0 sub-plans reviewed
- [x] 2 missing orchestrators identified (Refinement, Debug)
- [x] **7 feature gaps identified** (was 5: + Plan Viewer + Epic/Feature)
- [x] **9 diagram gaps identified** (was 4: + 5 new diagrams)
- [x] **7 outdated pages identified** (was 6: + cortex-lens-output/index.html)
- [x] Gaps classified by priority (P1-P4)
- [ ] Stub pages created (Phase 7b)
- [ ] Ready to proceed to Phase 7b

---

## 🚀 NEXT STEPS

### Phase 7b: Critical Orchestrator Docs (3 hours → **4 hours**)

**Tasks:**
1. ✅ Create `cortex-lens-output/views/plan-viewer.html` (Plan Viewer UI) - **1h**
2. ✅ Create `docs/orchestrators/planning-v5-epic-vs-feature.html` (Epic/Feature guide) - **1h**
3. ✅ Update `cortex-lens-output/index.html` (add Plan Viewer tab) - **15min**
4. ✅ Complete `docs/orchestrators/refinement-orchestrator.html` (7-phase workflow) - **1h**
5. ✅ Complete `docs/orchestrators/debug-orchestrator.html` (error analysis workflow) - **1h**
6. ✅ Update `docs/orchestrators/index.html` (add Refinement + Debug tiles) - **30min**
7. ✅ Update ecosystem diagram with all 10 orchestrators - **30min**

**Exit Criteria:**
- Plan Viewer page exists and uses glassmorphism design
- Epic vs. Feature guide complete with decision tree
- Orchestrator index shows 10 orchestrators (not 8)
- All critical pages glassmorphism compliant

---

## 📝 REVISION HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-04 | GitHub Copilot | Initial gap analysis with Plan Viewer + Epic/Feature discoveries |
