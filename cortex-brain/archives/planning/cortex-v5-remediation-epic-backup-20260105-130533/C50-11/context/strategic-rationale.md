# CORTEX-LENS Admin Dashboard - Strategic Context

**Date:** January 4, 2026  
**Author:** Asif Hussain

---

## 🤔 The Question: Should We Merge or Separate?

### Two Tools, Two Goals

**CORTEX-LENS (Existing):**
- **Goal:** Reverse-engineer repositories into knowledge bases
- **Users:** Developers understanding unfamiliar codebases
- **Technology:** AST parsing, dependency analysis, code metrics
- **Output:** Visual code maps, architecture diagrams

**Admin Tools (New Requirement):**
- **Goal:** Monitor CORTEX plan execution
- **Users:** Users tracking active planning sessions
- **Technology:** Plan metadata parsing, progress tracking
- **Output:** Plan dashboards, AC validation reports

### The Strategic Decision: MERGE ✅

**Why This is Superior:**

1. **Infrastructure Reuse** (40% dev time savings)
   - Single HTML/CSS/JS codebase
   - Shared Glass design system
   - Unified navigation
   - One deployment pipeline

2. **Cross-Tool Intelligence**
   - Plan phases → Link to affected files in AST view
   - Acceptance criteria → Map to test coverage heatmaps
   - Time estimates vs. actuals → Identify high-churn code
   - Knowledge Library queries → Display historical patterns

3. **User Mental Model**
   - "CORTEX-LENS = where I **see** what CORTEX knows and does"
   - Natural grouping: Repository + Plan intelligence
   - Single place for all visual admin tools

4. **Future-Proof Architecture**
   - Easy to add more tabs (Analytics, Knowledge Graph)
   - Shared components (search, filters, progress bars)
   - Consistent UX across all admin features

---

## 🏗️ How They Work Together

### Architectural Separation

**Concerns are SEPARATED:**
- Each tab is independent HTML view
- Repository Lens doesn't know about Plan Viewer
- Plan Viewer doesn't know about Repository Lens
- Communication via cross-link events only

**Code is SHARED:**
- `assets/css/components.css` - Buttons, cards, progress bars
- `assets/js/shared-utils.js` - Search, filters, data loading
- `assets/images/` - Logo, icons
- Glass design tokens

### Data Flow

```
┌─────────────────────────────────────────────────┐
│         CORTEX-LENS Dashboard (index.html)      │
└─────────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼────┐             ┌──────▼──────┐
   │   TAB   │             │     TAB     │
   │Repository│            │    Plan     │
   │  Lens   │             │   Viewer    │
   └────┬────┘             └──────┬──────┘
        │                         │
   ┌────▼────────┐         ┌──────▼────────┐
   │  Data       │         │  Data         │
   │  repo-ast   │         │  plans-index  │
   │  .json      │         │  .json        │
   └─────────────┘         └───────────────┘
        ▲                         ▲
        │                         │
   ┌────┴──────────┐     ┌────────┴─────────┐
   │  Sub-Plan 04  │     │   Sub-Plan 11    │
   │ AST Scanning  │     │ Plan Metadata    │
   └───────────────┘     └──────────────────┘
```

### Cross-Linking Intelligence

**Scenario 1: Plan → Code**
```
User clicks "Phase 3: Implement authentication"
  → Plan Viewer shows linked files: ["src/auth/jwt.py", "tests/test_auth.py"]
  → User clicks "View in Repository Lens"
  → Switches to Repository Lens tab
  → Highlights "src/auth/jwt.py" in file tree
  → Shows AST analysis, dependencies, test coverage
```

**Scenario 2: Code → Plans**
```
User browses Repository Lens, selects "src/auth/jwt.py"
  → Repository Lens queries plans-index.json
  → Shows "Referenced in Plans:" section
  → Lists: "CORTEX-5.0 Sub-Plan 11 - Phase 3"
  → User clicks plan reference
  → Switches to Plan Viewer tab
  → Shows plan detail with progress
```

---

## 💡 Additional Valuable Information

### From CORTEX-5.0 Plan Context

**What Makes This Sub-Plan Strategic:**

1. **Timing is Perfect**
   - Sub-Plan 03 (Knowledge Library) provides Tier 0/2 query APIs
   - Sub-Plan 04 (AST Scanning) generates repo-ast.json
   - Sub-Plan 11 consumes both → Creates synergy

2. **Enables Future Sub-Plans**
   - Sub-Plan 06 (Visual Progress) can reuse progress components
   - Sub-Plan 10 (Acceptance Validation) integrates AC checks
   - Analytics tab (future) gets foundation here

3. **Solves Real Pain Point**
   - Currently no way to visualize plan execution
   - Users manually check PLAN.md files
   - No effectiveness tracking (time estimates vs. actuals)

### Intelligence Features (Beyond Basic Viewer)

**What Makes This "Admin Intelligence" Not Just "Admin Viewer":**

1. **Predictive Insights**
   - "Phase 3 usually runs 50% over estimate for refactoring tasks"
   - "Files with >10 commits often indicate underestimated complexity"
   - "ACs with no linked test files have 80% failure rate"

2. **Risk Scoring**
   - High-churn files flagged in plan view
   - ACs without tests marked as risky
   - Phases blocked by dependencies highlighted

3. **Effectiveness Metrics**
   - Average variance: Estimated vs. actual time per phase type
   - Most accurate orchestrators (Planning vs. TDD vs. Debug)
   - Learning: "Debug orchestrator always takes 2x estimate"

4. **Knowledge Integration**
   - Query Tier 2: "Show similar plans from past 6 months"
   - Display lessons learned relevant to current phase
   - Suggest best practices based on historical data

### Why Glass Design System?

**Chosen for:**
- **Visual Hierarchy** - Overlapping glass panels = clear information layers
- **Modern Aesthetic** - Professional, clean, matches CORTEX brand
- **Accessibility** - High contrast, clear typography
- **Consistency** - Already used in response templates

**Design Tokens:**
- Primary gradient: `#667eea` → `#764ba2` (purple-blue)
- Glass panels: `rgba(255, 255, 255, 0.1)` backdrop blur
- Progress bars: Green (complete), Blue (active), Gray (pending)
- Status badges: Color-coded with icons

---

## 🎯 Success Metrics

**How We'll Know This Worked:**

### User Adoption
- 80%+ of plan creators check Plan Viewer during execution
- Average 3+ cross-links clicked per session (Plan ↔ Code)
- Knowledge Library queries used in 50%+ of plans

### Effectiveness Improvement
- Time estimate accuracy improves 20% (better learning from past plans)
- AC failure rate drops 30% (early risk detection via heatmaps)
- Rework reduces 25% (duplicate/orphan code detected via AST)

### Technical Success
- Page load <2 seconds
- Search results instant (<100ms)
- Zero security vulnerabilities
- WCAG AA accessibility compliance

---

## 🚧 Open Questions & Decisions

### Resolved:
- ✅ **Merge vs. Separate:** MERGE (infrastructure reuse)
- ✅ **Data Format:** JSON (plans-index.json, repo-ast.json)
- ✅ **Navigation:** Vertical tabs (clearer hierarchy)
- ✅ **Design System:** Glass (consistent with CORTEX brand)

### To Decide During Implementation:
- ⏳ **Auto-Refresh Frequency:** Poll every 30s or WebSocket?
- ⏳ **Pagination Threshold:** Show all plans or paginate at 50+?
- ⏳ **Mobile Strategy:** Responsive or separate mobile app?
- ⏳ **Offline Support:** Cache in local storage or always-online?

---

## 📚 References

**Source Documents:**
- Initial proposal: User request (January 4, 2026)
- Strategic analysis: GitHub Copilot analysis
- Architecture review: This document
- CORTEX-5.0 Master Plan: `00-MASTER-REMEDIATION-PLAN.md`

**Related Technologies:**
- Glass Design: https://glassmorphism.com/
- Fuzzy Search: https://fusejs.io/
- JSON Schema: https://json-schema.org/
- DOMPurify: https://github.com/cure53/DOMPurify

---

**Status:** Strategic planning complete  
**Next:** Phase 0 execution when Sub-Plans 03, 04 complete  
**Confidence:** VERY HIGH (clear architecture, proven approach)
