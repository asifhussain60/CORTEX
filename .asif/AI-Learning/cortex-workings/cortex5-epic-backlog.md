# CORTEX 5 Enhancement Epic - Backlog & Gaps

**Date:** 2026-01-07  
**Epic:** cortex5-enhancement-epic-v2  
**Status:** Phase 0 + P00B Required Before Phase 1  
**Analysis:** Holistic review of missing features and architecture gaps

---

## 🔍 Gap Analysis Summary

### Documentation Orchestrator Gap (CRITICAL)

**Current State:**
- ✅ Manifest exists: `cortex-brain/manifests/orchestrators/documentation-orchestrator.yaml`
- ✅ Registered in master orchestrator: `cortex-brain/config/master-orchestrator.yaml` (2 patterns)
- ✅ Architecture docs exist: `docs/architecture/documentation-orchestrator-architecture.md`
- ✅ Old implementation exists: `cortex-brain/admin/documentation/generators/` (CORTEX-5.0)
- ❌ **NO Python implementation in `src/orchestrators/`** (not migrated from CORTEX-5.0)
- ❌ **Pattern registered but orchestrator cannot execute** (routing fails)
- ✅ **IMMEDIATE FIX APPLIED:** Disabled both routing patterns (commented out) to prevent errors

**Impact:**
- ~~Users requesting documentation standardization get routing errors~~ **FIXED: Patterns disabled**
- HTML glassmorphism standardization cannot be executed (deferred to BACKLOG-001)
- Documentation generation capabilities lost in CORTEX-5.5 migration

**Root Cause:**
- Documentation orchestrator tools NOT migrated during Phase 0 planning
- Admin tools (`cortex-brain/admin/documentation/`) are toolkit utilities, not orchestrator implementations
- Need Python orchestrator in `src/orchestrators/documentation/` to handle routing

---

## 🎯 Proposed Solution: Master Documentation Orchestrator

### Architecture Vision

**Master Documentation Orchestrator** with 3 specialized child orchestrators:

```
Master Documentation Orchestrator
├── 1. CORTEX GitHub Pages Orchestrator
│   ├── Purpose: Generate/maintain CORTEX project documentation
│   ├── Target: docs/ folder, GitHub Pages deployment
│   ├── Features: API docs, architecture diagrams, user guides
│   └── Tech: MkDocs, Mermaid, D3.js visualizations
│
├── 2. Application Documentation Orchestrator
│   ├── Purpose: Document user's application work (real-time)
│   ├── Target: User repos (not CORTEX)
│   ├── Features: Architecture docs, API references, changelogs
│   └── Integration: Captures CORTEX work done on user's application
│
└── 3. Learning Library Orchestrator
    ├── Purpose: Incremental knowledge library maintenance
    ├── Target: cortex-brain/tier2/knowledge/, tier3/
    ├── Features: Extract patterns, build knowledge graph, update library
    └── Triggers: After each orchestrator execution, learn from actions
```

### Master Orchestrator Responsibilities

1. **Route to Child Orchestrators** - Analyze request intent, delegate to appropriate child
2. **Coordinate Multi-Target Operations** - e.g., "document this feature" → updates both app docs + learning library
3. **Enforce Documentation Standards** - HTML glassmorphism, Markdown formatting, WCAG compliance
4. **State Management** - Track what's documented, prevent duplication
5. **Quality Assurance** - Validate cross-references, broken links, outdated content

---

## 📋 Backlog Items

### BACKLOG-001: Migrate Documentation Orchestrator from CORTEX-5.0

**Priority:** HIGH  
**Blocks:** Documentation standardization requests  
**Effort:** 2-3 days  

**Tasks:**
1. Pull `cortex-brain/admin/documentation/generators/` from CORTEX-5.0 (if needed)
2. Create `src/orchestrators/documentation/documentation_orchestrator.py`
3. Implement routing handler for patterns in `master-orchestrator.yaml`
4. Integrate with existing manifest (`documentation-orchestrator.yaml`)
5. Add tests: `tests/orchestrators/test_documentation_orchestrator.py`
6. Validate: Request "standardize architecture docs" → orchestrator executes

**Dependencies:**
- Phase 0 complete (clean branch established)
- Phase P00B complete (orchestrator instantiation fixed)

**Deliverables:**
- Working documentation orchestrator in `src/orchestrators/documentation/`
- 100% test coverage
- Integration with master orchestrator registry

---

### BACKLOG-002: Implement Child Orchestrator 1 - CORTEX GitHub Pages

**Priority:** MEDIUM  
**Depends On:** BACKLOG-001  
**Effort:** 1 week  

**Scope:**
- Generate CORTEX project documentation (API, architecture, guides)
- MkDocs integration for GitHub Pages deployment
- Mermaid diagram generation for architecture
- D3.js interactive visualizations for class hierarchies
- Auto-update on code changes (CI/CD integration)

**Deliverables:**
- `src/orchestrators/documentation/github_pages_orchestrator.py`
- MkDocs configuration templates
- Diagram generation pipeline
- CI/CD workflow for auto-deployment

---

### BACKLOG-003: Implement Child Orchestrator 2 - Application Documentation

**Priority:** HIGH  
**Depends On:** BACKLOG-001  
**Effort:** 1 week  

**Scope:**
- Real-time documentation of user application work
- Architecture diagrams for user's codebase
- API reference generation (from AST analysis)
- Changelog generation (from git commits + CORTEX actions)
- Integration with Planning v5 (document deliverables)

**Use Case Example:**
```
User: "Plan OAuth2 authentication for my app"
Planning v5: Creates plan, executes phases
App Doc Orchestrator: 
  - Documents OAuth2 architecture (diagrams)
  - Generates API reference (endpoints, models)
  - Creates implementation guide (step-by-step)
  - Updates changelog (features added)
```

**Deliverables:**
- `src/orchestrators/documentation/app_documentation_orchestrator.py`
- AST-based API reference generator
- Architecture diagram templates (Mermaid)
- Changelog automation

---

### BACKLOG-004: Implement Child Orchestrator 3 - Learning Library

**Priority:** HIGH  
**Depends On:** BACKLOG-001  
**Effort:** 2 weeks  

**Scope:**
- Incremental knowledge library maintenance
- Extract patterns from orchestrator executions
- Build knowledge graph (relationships, dependencies)
- Update `cortex-brain/tier2/knowledge/` automatically
- Learning from user feedback and edits

**Knowledge Extraction Examples:**
```
After Planning v5 execution:
  - Extract: "User prefers FastAPI over Flask for APIs"
  - Update: cortex-brain/tier2/knowledge/python/frameworks.md
  - Preference: FastAPI (confidence: 0.9)

After TDD execution:
  - Extract: "User uses pytest fixtures for database mocks"
  - Update: cortex-brain/tier2/knowledge/testing/patterns.md
  - Pattern: pytest fixtures (usage count: 15)

After ADO v2 execution:
  - Extract: "User follows Azure DevOps naming: US-{id}"
  - Update: cortex-brain/tier3/user-preferences.yaml
  - Naming convention: azure_devops_format
```

**Deliverables:**
- `src/orchestrators/documentation/learning_library_orchestrator.py`
- Pattern extraction engine (AST + NLP)
- Knowledge graph builder
- Auto-update pipeline for tier2/tier3 brain

---

### BACKLOG-005: Add Documentation Orchestrator to CORTEX5 Epic

**Priority:** MEDIUM  
**Depends On:** BACKLOG-001, 002, 003, 004  
**Effort:** 1 day (planning)  

**Tasks:**
1. Create new phase in epic: **Phase 12: Documentation Orchestrator System**
2. Define success criteria (3 child orchestrators operational)
3. Integration with Phase 11 (end-to-end testing)
4. Update timeline (add 2-3 weeks to epic)
5. Update `tracking/progress-tracker.json`

**Phase 12 Structure:**
```
Phase 12: Documentation Orchestrator System (2-3 weeks)
├── Task 1: Master orchestrator implementation (BACKLOG-001)
├── Task 2: GitHub Pages child orchestrator (BACKLOG-002)
├── Task 3: Application documentation child orchestrator (BACKLOG-003)
├── Task 4: Learning library child orchestrator (BACKLOG-004)
└── Task 5: Integration testing (all 3 children)
```

**Epic Timeline Impact:**
- Original: 9 weeks (Phases 1-11)
- Updated: 11-12 weeks (Phases 1-12)
- Parallel execution possible: Phase 12 can run alongside Phase 11

---

## 🏗️ Architecture Integration

### How Documentation Orchestrators Fit CORTEX5 Epic

**Phase 1 (Knowledge Extension):**
- Learning Library Orchestrator uses `CompanyKnowledgeProvider` to merge CORTEX + company knowledge

**Phase 2 (Orchestrator Registry):**
- Master Documentation Orchestrator registers 3 child orchestrators in registry
- Child orchestrators inherit CORTEX rules (TDD, Git Isolation)

**Phase 5 (Custom Orchestrator Framework):**
- Documentation orchestrators demonstrate custom orchestrator patterns
- Serve as reference implementation for Phase 6 (Selenium→Playwright)

**Phase 8 (TDD Harness):**
- Documentation orchestrators follow RED→GREEN→REFACTOR
- Tests validate documentation quality, broken links, outdated content

**Phase 11 (Integration):**
- Documentation orchestrators tested alongside all other orchestrators
- End-to-end validation: Generate docs for epic itself (meta-documentation)

---

## 🎯 Success Criteria (When Documentation Gap Closed)

### BACKLOG-001 Success (Master Orchestrator)
- ✅ Request "standardize docs" routes to documentation orchestrator
- ✅ Orchestrator instantiates without errors
- ✅ Integration tests pass (100% coverage)
- ✅ No routing errors in master orchestrator

### BACKLOG-002 Success (GitHub Pages)
- ✅ CORTEX documentation generated and deployed to GitHub Pages
- ✅ MkDocs navigation auto-updates on code changes
- ✅ Mermaid diagrams render correctly
- ✅ D3.js visualizations interactive and responsive

### BACKLOG-003 Success (Application Docs)
- ✅ User's application documented in real-time (architecture + API)
- ✅ Changelogs auto-generated from CORTEX actions
- ✅ Documentation lives in user's repo (not CORTEX)
- ✅ Integration with Planning v5 (deliverables documented)

### BACKLOG-004 Success (Learning Library)
- ✅ Knowledge library auto-updates after orchestrator executions
- ✅ Patterns extracted and stored in tier2/tier3 brain
- ✅ User preferences learned and applied (e.g., framework choices)
- ✅ Knowledge graph built and queryable

### BACKLOG-005 Success (Epic Integration)
- ✅ Phase 12 added to epic with 2-3 week timeline
- ✅ All 4 backlog items tracked in `progress-tracker.json`
- ✅ Documentation orchestrators tested in Phase 11 integration
- ✅ Epic timeline updated (11-12 weeks total)

---

## 🚀 Recommended Execution Order

### Immediate (After Phase P00B Complete)

1. **BACKLOG-001** (HIGH priority) - Migrate master documentation orchestrator
   - Unblocks documentation standardization requests
   - Required for Phase 12 to start

### Phase 12 Execution (Weeks 9-11)

2. **BACKLOG-003** (HIGH priority) - Application documentation orchestrator
   - Highest business value (documents user's work)
   - Can run parallel to Phase 11 integration testing

3. **BACKLOG-004** (HIGH priority) - Learning library orchestrator
   - Strategic value (auto-improves CORTEX knowledge)
   - Feeds into Phase 1 (Knowledge Extension) validation

4. **BACKLOG-002** (MEDIUM priority) - GitHub Pages orchestrator
   - CORTEX project documentation (internal value)
   - Can be deferred to post-epic maintenance

### Epic Planning (After Phase 11)

5. **BACKLOG-005** (MEDIUM priority) - Add Phase 12 to epic
   - Formalizes documentation orchestrator work
   - Updates tracking and timeline

---

## 📊 Pull Budget Impact

**Estimated Pulls from CORTEX-5.0:**
- BACKLOG-001: 5-8 files (`cortex-brain/admin/documentation/generators/`)
- BACKLOG-002: 2-3 files (MkDocs templates, diagram generators)
- BACKLOG-003: 3-4 files (AST analysis, changelog utilities)
- BACKLOG-004: 4-5 files (pattern extraction, knowledge graph tools)

**Total:** ~15-20 files (near pull budget limit of 20)

**Alternatives to Pulling:**
- Rewrite from scratch using modern libraries (2025-2026 best practices)
- Use lightweight alternatives (simpler implementations)
- Defer to post-epic work (not in critical path)

**Recommendation:** Pull only BACKLOG-001 files (master orchestrator), rewrite children from scratch

---

## 🔗 Related Documentation

**Architecture:**
- `docs/architecture/documentation-orchestrator-architecture.md` (existing design)
- `cortex-brain/manifests/orchestrators/documentation-orchestrator.yaml` (manifest)
- `cortex-brain/config/master-orchestrator.yaml` (routing config)

**Implementation Reference (CORTEX-5.0):**
- `cortex-brain/admin/documentation/generators/base_generator.py`
- `cortex-brain/admin/documentation/generators/executive_summary_generator.py`
- `cortex-brain/admin/documentation/generators/intelligent_navigation_generator.py`

**CORTEX5 Epic:**
- `cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-epic.md`
- `cortex-brain/documents/planning/active/cortex5-enhancement-epic/tracking/progress-tracker.json`

---

---

## 📝 Required Epic Plan Updates

### Update 1: Add Phase P01 (Documentation Orchestrator Foundation)

**Location:** `cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-epic.md`

**Insert After:** Phase P00B (Critical Blocker Resolution)  
**Before:** Phase 1 (Knowledge Extension Layer)

**New Phase Structure:**
```
Phase P01: Documentation Orchestrator Foundation (2-3 days)
├── Priority: P1 (HIGH - Unblocks documentation requests)
├── Dependencies: Phase 0 ✅, Phase P00B ✅
├── Blocks: None (parallel with Phase 1)
├── Duration: 2-3 days
└── Deliverables:
    ├── Master documentation orchestrator (src/orchestrators/documentation/)
    ├── Re-enable routing patterns in master-orchestrator.yaml
    ├── Integration tests (100% coverage)
    └── Validation: "standardize docs" executes successfully
```

**Rationale:** Documentation orchestrator was registered but implementation missing. This phase restores basic functionality without extending epic timeline (runs parallel to Phase 1).

---

### Update 2: Add Phase 12 (Documentation Orchestrator System)

**Location:** Same file, after Phase 11 (End-to-End Integration)

**New Phase Structure:**
```
Phase 12: Documentation Orchestrator System (2-3 weeks)
├── Track: 5 (Documentation & Knowledge)
├── Dependencies: Phase P01 ✅, Phase 1 ✅
├── Parallel Execution: Can run alongside Phase 11 validation
├── Duration: 2-3 weeks (11-12 hours actual work)
└── Deliverables:
    ├── CORTEX GitHub Pages orchestrator (BACKLOG-002)
    ├── Application documentation orchestrator (BACKLOG-003)
    ├── Learning library orchestrator (BACKLOG-004)
    └── Integration testing (all 3 children)
```

**Success Criteria:**
- ✅ 3 child orchestrators operational and registered
- ✅ GitHub Pages auto-deploys CORTEX documentation
- ✅ Application docs capture user's work in real-time
- ✅ Learning library auto-updates from orchestrator patterns
- ✅ Integration with Planning v5 (documents deliverables)
- ✅ Knowledge graph queryable (tier2/tier3 brain)

---

### Update 3: Update Epic Timeline

**Location:** Section "📊 Timeline & Milestones"

**Changes:**
```
| Week | Milestone | Phases | Status |
|------|-----------|--------|--------|
| 0    | Phase 0 + P00B + P01 | Foundation Setup | 🔴 NOT STARTED |
| 1-2  | Foundation Complete | Phase 1 | 🟡 Blocked by P00B+P01 |
| 3    | Registry & Goals | Phases 2-3 | 🟡 Not Started |
| 4    | Merge Logic | Phase 4 | 🟡 Not Started |
| 5-6  | Framework + TDD + Viewer | Phases 5, 8-9 | 🟡 Not Started |
| 7    | Playwright + Rules | Phases 6-7, 10 | 🟡 Not Started |
| 8-9  | Integration + Docs System | Phases 11-12 | 🟡 Not Started |
```

**Total Duration Updated:**
- **Original:** 15 min (Phase 0) + 1 day (P00B) + 9 weeks (Phases 1-11)
- **Updated:** 15 min (Phase 0) + 1 day (P00B) + 2-3 days (P01) + 9-10 weeks (Phases 1-12)
- **Total:** ~10-11 weeks (Phase 12 runs parallel to Phase 11)

---

### Update 4: Update Pull Budget Tracking

**Location:** `tracking/pulls-from-cortex-5.0.json`

**Add Phase P01 Entry:**
```json
"phase_p01": {
  "pulls": 5,
  "files": [
    "cortex-brain/admin/documentation/generators/base_generator.py",
    "cortex-brain/admin/documentation/generators/executive_summary_generator.py",
    "cortex-brain/admin/documentation/generators/intelligent_navigation_generator.py",
    "cortex-brain/admin/documentation/config/",
    "cortex-brain/admin/documentation/README.md"
  ],
  "justification": "Master documentation orchestrator requires base generators for HTML standardization",
  "category": "documentation_tools"
}
```

**Add Phase 12 Entry:**
```json
"phase_12": {
  "pulls": 0,
  "files": [],
  "justification": "Child orchestrators rewritten from scratch (modern patterns)",
  "category": "documentation_tools",
  "alternatives_used": "Rewrite using 2026 best practices instead of pulling legacy code"
}
```

**Budget Impact:**
- Phase P01: 5 files (25% of budget)
- Phase 12: 0 files (rewrite approach)
- **Remaining Budget:** 15/20 files available for Phases 1-11

---

### Update 5: Update Progress Tracker

**Location:** `tracking/progress-tracker.json`

**Add Phase P01:**
```json
{
  "phase_number": "P01",
  "name": "Documentation Orchestrator Foundation",
  "track": 0,
  "status": "NOT_STARTED",
  "priority": "P1_HIGH",
  "progress_percentage": 0,
  "duration": "2-3 days",
  "dependencies": ["Phase 0", "Phase P00B"],
  "blocks_phases": [],
  "parallel_with": ["Phase 1"],
  "deliverables": [
    {"name": "Master documentation orchestrator", "status": "NOT_STARTED"},
    {"name": "Re-enable routing patterns", "status": "NOT_STARTED"},
    {"name": "Integration tests (100%)", "status": "NOT_STARTED"},
    {"name": "Validation: standardize docs works", "status": "NOT_STARTED"}
  ]
}
```

**Add Phase 12:**
```json
{
  "phase_number": 12,
  "name": "Documentation Orchestrator System",
  "track": 5,
  "status": "NOT_STARTED",
  "progress_percentage": 0,
  "duration": "2-3 weeks",
  "dependencies": ["Phase P01", "Phase 1"],
  "parallel_with": ["Phase 11"],
  "deliverables": [
    {"name": "GitHub Pages orchestrator", "status": "NOT_STARTED"},
    {"name": "Application docs orchestrator", "status": "NOT_STARTED"},
    {"name": "Learning library orchestrator", "status": "NOT_STARTED"},
    {"name": "Integration testing (3 children)", "status": "NOT_STARTED"}
  ]
}
```

---

### Update 6: Create Phase Documents

**Required Files:**
1. `phases/phase-p01-documentation-foundation.md` (detailed implementation plan for BACKLOG-001)
2. `phases/phase-12-documentation-system.md` (detailed plan for BACKLOG-002/003/004)

**Content Structure (Phase P01):**
- Background: Why documentation orchestrator was lost in CORTEX-5.5 migration
- Objective: Restore basic documentation functionality
- Technical Approach: Pull base generators, create orchestrator wrapper
- Testing Strategy: Integration tests, routing validation
- Success Criteria: "standardize docs" executes without errors

**Content Structure (Phase 12):**
- Background: Expand documentation capabilities with 3 specialized children
- Objective: Auto-document CORTEX project, user applications, and build knowledge library
- Technical Approach: Master/child orchestrator pattern
- Architecture: Routing logic, state management, knowledge extraction
- Testing Strategy: Unit tests, integration tests, end-to-end validation
- Success Criteria: All 3 children operational, integrated with existing orchestrators

---

### Update 7: Update Snowball Strategy

**Location:** Section "🌊 Snowball Effect Strategy"

**Add Documentation Track:**
```
Phase P01 (Doc Foundation) ────────┐
    ↓                              │
Phase 1 (Knowledge Extension) ─────┼───→ Phase 12 (Doc System)
    ↓                              │         ↓
Phase 2 (Registry) ────────────────┤     ╔═══════════════════════╗
    ↓                              │     ║ 3 Child Orchestrators ║
Phase 4 (Merge Logic) ─────────────┘     ║ - GitHub Pages        ║
                                         ║ - App Docs            ║
Phase 11 (Integration) ←─────────────────║ - Learning Library    ║
                                         ╚═══════════════════════╝
```

**Parallel Windows Updated:**
- **Week 0:** Phase 0 + P00B + P01 (foundation setup)
- **Weeks 1-2:** Phase 1 (knowledge extension) - P01 validates in parallel
- **Weeks 8-10:** Phase 11 + Phase 12 (3-way parallel: integration + doc system)

---

### Update 8: Update Risk Assessment

**Location:** Section "⚠️ Risks & Mitigations"

**Add New Risks:**

**Risk 7: Documentation orchestrator pull budget exhaustion**
- **Impact:** 5 files from CORTEX-5.0 reduces available budget to 15/20
- **Mitigation:** Rewrite child orchestrators from scratch (Phase 12)
- **Contingency:** Defer Phase 12 to post-epic if budget critical

**Risk 8: Knowledge extraction accuracy <80%**
- **Impact:** Learning library orchestrator provides incorrect knowledge
- **Mitigation:** Supervised learning mode (user approval required)
- **Contingency:** Manual knowledge curation, disable auto-updates

---

### Update 9: Update Success Metrics

**Location:** Section "🎯 Success Criteria - Epic-Level"

**Add Documentation Metrics:**

**Functional:**
- ✅ Documentation orchestrator operational (P01 complete)
- ✅ 3 child orchestrators registered and functional (Phase 12)
- ✅ GitHub Pages auto-deploys on code changes
- ✅ User applications documented in real-time (architecture + API)
- ✅ Knowledge library auto-updates (>80% accuracy)

**Quality:**
- ✅ Documentation orchestrator: 100% test coverage
- ✅ Cross-reference validation: 0 broken links
- ✅ WCAG AA compliance: all generated HTML

**Adoption:**
- ✅ 10+ CORTEX documentation pages generated
- ✅ 2+ user applications documented by app orchestrator
- ✅ 50+ knowledge patterns extracted by learning library

---

## 📋 Summary of Epic Plan Changes

### Critical Path Impact
- **Phase P01 added** (2-3 days) - Runs parallel to Phase 1, no timeline impact
- **Phase 12 added** (2-3 weeks) - Runs parallel to Phase 11, extends timeline by 1-2 weeks
- **Total Timeline:** 10-11 weeks (vs. original 9 weeks)

### Pull Budget Impact
- **Phase P01:** 5 files pulled (25% of budget)
- **Phase 12:** 0 files pulled (rewrite approach)
- **Remaining:** 15/20 files for Phases 1-11

### Track Structure Impact
- **New Track 5:** Documentation & Knowledge (Phase 12)
- **Parallel Execution:** Phase 12 runs alongside Phase 11 (weeks 8-10)

### Scope Impact
- **+2 phases** (P01, 12)
- **+3 child orchestrators** (GitHub Pages, App Docs, Learning Library)
- **+5 backlog items** (001-005)
- **+2 phase documents** required
- **+100 lines** of epic documentation

---

## ✅ Next Actions for Plan Update

### Immediate (Before Phase P00B Complete)
1. **Update `00-cortex5-epic.md`** - Add Phase P01 and Phase 12 sections
2. **Create `phases/phase-p01-documentation-foundation.md`** - BACKLOG-001 implementation plan
3. **Create `phases/phase-12-documentation-system.md`** - BACKLOG-002/003/004 plan
4. **Update `tracking/progress-tracker.json`** - Add P01 and Phase 12 entries
5. **Update `tracking/pulls-from-cortex-5.0.json`** - Add phase_p01 and phase_12 entries

### After Phase P00B Complete
6. **Execute Phase P01** (2-3 days) - Migrate master documentation orchestrator
7. **Validate Phase P01** - Re-enable routing patterns, test "standardize docs"
8. **Begin Phase 1** (parallel) - Knowledge extension layer

### After Phase 11 Complete
9. **Execute Phase 12** (2-3 weeks) - Implement 3 child orchestrators
10. **Final validation** - End-to-end testing, integration with all orchestrators

---

**Status:** 🟢 READY FOR PLAN UPDATE  
**Owner:** Asif Hussain  
**Impact:** +1-2 weeks to epic timeline, +25% pull budget usage  
**Last Updated:** 2026-01-07
