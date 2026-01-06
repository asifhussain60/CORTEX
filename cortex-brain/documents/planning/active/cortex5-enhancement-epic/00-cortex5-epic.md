# CORTEX5 Enhancement Epic - Complete Architecture Overhaul

**Plan ID:** `cortex5-enhancement-epic-v2`  
**Version:** 2.0.0  
**Status:** 🟢 ACTIVE  
**Created:** 2026-01-06  
**Timeline:** 9 weeks (3 parallel tracks)  
**Complexity:** Tier 5 (Architectural Transformation)

---

## 📋 Executive Summary

**Vision:** Transform CORTEX from single-purpose orchestration system to extensible business intelligence platform with pluggable company knowledge, custom orchestrators, and intelligent governance layering.

### Strategic Objectives

1. **Business Extensibility:** Enable companies to plugin domain-specific knowledge without corrupting CORTEX core
2. **Custom Orchestrators:** Allow registration of business-specific orchestrators (e.g., Selenium→Playwright)
3. **Intelligent Override:** Company knowledge intelligently overrides CORTEX defaults while preserving best practices
4. **Autonomous Execution:** Maximize snowball effect with parallel tracks and self-executing orchestrators
5. **Quality & Performance:** Comprehensive testing, optimization, and documentation

### Key Innovations

**🆕 Knowledge Extension Layer:**
- Company knowledge stored in `cortex-brain/tier2/company-knowledge/{company-id}/`
- Query priority: CORTEX Core → Company Override → Merge
- File-based (Markdown/YAML), no new databases
- Version-controlled, easily rollbackable

**🆕 Orchestrator Registry System:**
- Central registry at `cortex-brain/tier0/orchestrator-registry.yaml`
- Custom orchestrators isolated in `src/orchestrators/custom/{company-id}/`
- Manifest-based registration with inheritance support
- Master Orchestrator routes via registry (no hardcoded patterns)

**🆕 Rule Layering Architecture:**
- Core Rules (TDD, Git Isolation) - highest priority, cannot override
- Company Rules (coding standards, tech stack) - extends core
- Domain Rules (PCI-DSS, HIPAA) - scoped to specific orchestrators
- Conflict resolution via priority system

**🆕 Intermittent Thoughts Capture System:**
- User-facing `intermittent-thoughts.txt` for capturing ideas during autonomous execution
- System tracks via `cortex-brain/tier1/intermittent-thoughts.yaml`
- Checked at phase transitions, auto-incorporated if impact ≤15%
- Visual feedback via shield icon (🛡️) in chat + plan viewer integration
- Incorporated thoughts replaced with concise confirmation messages

---

## 🏗️ Architecture Overview

### Current State (CORTEX 5.1)

```
User Request
    ↓
Master Orchestrator (hardcoded patterns)
    ↓
10 Core Orchestrators (Planning, TDD, ADO, Vacuum, etc.)
    ↓
CORTEX Knowledge Library (Python-focused)
    ↓
4-Tier Brain System (Governance, Working Memory, Knowledge Graph, Dev Context)
```

**Limitations:**
- ❌ Cannot add custom orchestrators without code changes
- ❌ No company-specific knowledge integration
- ❌ Hardcoded routing patterns (not extensible)
- ❌ Single knowledge source (CORTEX only)

### Target State (CORTEX 5.2)

```
User Request
    ↓
Master Orchestrator v7 (registry-based routing)
    ↓
    ├─ Core Orchestrators (10)
    │   └─ Query: CORTEX Knowledge → Company Knowledge → Merge
    │
    └─ Custom Orchestrators (unlimited)
        └─ Query: Company Knowledge → CORTEX Knowledge → Merge
            └─ Enforce: Core Rules + Company Rules + Domain Rules
    ↓
Knowledge Extension Layer
    ├─ CORTEX Core Knowledge (immutable)
    └─ Company Knowledge (pluggable, per company-id)
    ↓
4-Tier Brain System (extended with company brains)
```

**Capabilities:**
- ✅ Custom orchestrators via manifest registration
- ✅ Company knowledge overrides CORTEX intelligently
- ✅ Registry-based routing (extensible)
- ✅ Multi-source knowledge with merge logic
- ✅ Rule layering (Core + Company + Domain)

---

## 📊 Epic Breakdown

### Track 1: Core Intelligence (Weeks 1-4) - Foundation

| Phase | Name | Duration | Dependencies | Deliverables |
|-------|------|----------|--------------|--------------|
| **1** | **Knowledge Extension Layer** | 2 weeks | None | `CompanyKnowledgeProvider`, folder structure, merge logic |
| **2** | **Orchestrator Registry System** | 1 week | Phase 1 | `orchestrator-registry.yaml`, `RegistryManager` |
| **3** | **Intelligent Goal Detection** | 1 week | Phase 2 | LLM-based analysis, dependency graph, goal inheritance |
| **4** | **Knowledge Merge & Override** | 1 week | Phase 1-2 | Priority system, conflict resolution, validation |

**Track Priority:** CRITICAL (blocks Tracks 2-3)

---

### Track 2: Business Extensibility (Weeks 3-6) - Parallel Execution

| Phase | Name | Duration | Dependencies | Deliverables |
|-------|------|----------|--------------|--------------|
| **5** | **Custom Orchestrator Framework** | 2 weeks | Phase 2 | Base classes, manifest schema, lifecycle hooks |
| **6** | **Selenium→Playwright Reference** | 1 week | Phase 5 | Complete custom orchestrator, AST parsing, code generation |
| **7** | **Rule Layering System** | 1 week | Phase 4 | 3-layer governance, conflict resolution, exemption workflow |

**Track Priority:** HIGH (enables business adoption)

---

### Track 3: Quality & UX (Weeks 5-8) - Parallel Execution

| Phase | Name | Duration | Dependencies | Deliverables |
|-------|------|----------|--------------|--------------|
| **8** | **TDD Test Harness** | 1 week | Phase 5 | Autonomous test generation, RED→GREEN→REFACTOR enforcement |
| **9** | **Plan Viewer Modernization** | 1 week | None | CSS standardization, responsive design, phase navigation |
| **10** | **Response Template Optimization** | 1 week | None | INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE modes |

**Track Priority:** MEDIUM (quality improvements)

---

### Track 4: Integration & Validation (Weeks 8-9) - Final Validation

| Phase | Name | Duration | Dependencies | Deliverables |
|-------|------|----------|--------------|--------------|
| **11** | **End-to-End Integration** | 1 week | All phases | Integration tests, performance benchmarks, validation reports |

**Track Priority:** CRITICAL (go/no-go decision)

---

## 🎯 Success Criteria

### Phase-Level Success Metrics

**Phase 1 (Knowledge Extension):**
- ✅ Company knowledge folder structure created
- ✅ `CompanyKnowledgeProvider` queries company knowledge after CORTEX
- ✅ Merge logic: Company overrides CORTEX where explicitly defined
- ✅ Validation: Query "API architecture" returns company-specific override

**Phase 2 (Orchestrator Registry):**
- ✅ `orchestrator-registry.yaml` created with 10 core orchestrators
- ✅ `RegistryManager` routes requests via registry (not hardcoded)
- ✅ Adding new orchestrator = YAML edit (no code changes)
- ✅ Validation: Add test orchestrator, verify routing works

**Phase 5 (Custom Orchestrator Framework):**
- ✅ `BaseCustomOrchestrator` class with lifecycle hooks
- ✅ Manifest schema validates orchestrator metadata
- ✅ Custom orchestrators inherit CORTEX rules automatically
- ✅ Validation: Create minimal custom orchestrator, verify execution

**Phase 6 (Selenium→Playwright):**
- ✅ Complete working orchestrator converts Selenium→Playwright
- ✅ Follows TDD (inherits from CORTEX TDD orchestrator)
- ✅ Applies company coding standards (from `rules.yaml`)
- ✅ Validation: Convert sample Selenium test, verify Playwright output

**Phase 11 (Integration):**
- ✅ All 10 core orchestrators + 1 custom orchestrator tested
- ✅ Knowledge merge validated (CORTEX + company)
- ✅ Performance: <50ms overhead for knowledge queries
- ✅ Zero regression: All existing tests pass

### Epic-Level Success Metrics

**Functional:**
- ✅ 3+ companies registered with independent knowledge libraries
- ✅ 2+ custom orchestrators operational (Selenium→Playwright + 1 other)
- ✅ Knowledge merge accuracy >95% (correct overrides)
- ✅ Zero CORTEX core corruption (all changes isolated)

**Performance:**
- ✅ Knowledge query overhead <50ms (95th percentile)
- ✅ Custom orchestrator routing <100ms
- ✅ No performance regression on core orchestrators

**Quality:**
- ✅ 100% test coverage on new components
- ✅ Zero critical bugs in integration testing
- ✅ All SKULL rules enforced (TDD, Git Isolation, etc.)

**Adoption:**
- ✅ 2+ developers trained on custom orchestrator development
- ✅ Documentation complete (architecture, API, deployment)
- ✅ 1+ production custom orchestrator deployed

---

## 🌊 Snowball Effect Strategy

### Phase Dependencies (Visual)

```
Phase 1 (Knowledge Extension) ────────┐
    ↓                                 │
Phase 2 (Orchestrator Registry) ──────┼───→ Phase 5 (Custom Framework)
    ↓                                 │         ↓
Phase 3 (Goal Detection)              │     Phase 6 (Selenium→Playwright)
    ↓                                 │         ↓
Phase 4 (Knowledge Merge) ────────────┘     Phase 7 (Rule Layering)

Phase 8 (TDD Harness) ─────┐
Phase 9 (Plan Viewer) ──────┼─→ Phase 11 (Integration)
Phase 10 (Response Templates)─┘
```

### Parallel Execution Windows

**Weeks 1-2:** Phase 1 only (foundation)  
**Week 3:** Phase 2 + Phase 3 (parallel)  
**Week 4:** Phase 4 only (critical merge logic)  
**Weeks 5-6:** Phase 5 + Phase 8 + Phase 9 (3-way parallel)  
**Week 7:** Phase 6 + Phase 7 + Phase 10 (3-way parallel)  
**Week 8:** Integration prep (all phases complete)  
**Week 9:** Phase 11 (final validation)

### Snowball Momentum

**Week 1-2:** Foundation laid (Knowledge Extension)  
**Week 3-4:** Acceleration (Registry + Goal Detection + Merge Logic)  
**Week 5-7:** Peak velocity (3 tracks parallel execution)  
**Week 8-9:** Validation & stabilization

---

## 🛡️ Brain Protection (SKULL) Compliance

| Rule | How Epic Complies |
|------|-------------------|
| **TDD_ENFORCEMENT** | Phase 8 creates TDD test harness, all code follows RED→GREEN→REFACTOR |
| **HOLISTIC_DISCOVERY** | Phase 1-2 search existing knowledge before creating new structures |
| **GIT_ISOLATION** | Custom orchestrators isolated in `src/orchestrators/custom/`, never modify core |
| **PLANNING_ISOLATION** | This epic creates plan structure, implementation deferred to execution |
| **HAND_OFF_PROTOCOL** | All orchestrators (core + custom) execute autonomously via Python |
| **AUTONOMOUS_ONLY** | Phase 5-6 ensure custom orchestrators follow autonomous execution model |

**Full compliance:** 61 SKULL rules enforced across all phases

---

## 📁 Plan Structure

```
cortex5-enhancement-epic-v2/
├── 00-cortex5-epic.md                    # This master plan
├── README.md                              # Quick start guide
│
├── analysis/
│   ├── gap-analysis.md                    # Current vs. target state gaps
│   ├── architectural-impact.md            # System-wide impact assessment
│   └── risk-assessment.md                 # Risk identification & mitigation
│
├── context/
│   ├── discovery.md                       # Workspace context discovery
│   ├── architecture-analysis.md           # Current architecture deep dive
│   └── dependency-mapping.md              # Phase dependencies & constraints
│
├── phases/
│   ├── phase-01-knowledge-extension.md    # Track 1: Foundation
│   ├── phase-02-orchestrator-registry.md
│   ├── phase-03-goal-detection.md
│   ├── phase-04-knowledge-merge.md
│   ├── phase-05-custom-framework.md       # Track 2: Business Extensibility
│   ├── phase-06-selenium-playwright.md
│   ├── phase-07-rule-layering.md
│   ├── phase-08-tdd-harness.md            # Track 3: Quality & UX
│   ├── phase-09-plan-viewer.md
│   ├── phase-10-response-templates.md
│   └── phase-11-integration.md            # Track 4: Validation
│
├── tracking/
│   ├── progress-tracker.json              # Real-time progress tracking
│   ├── snowball.md                        # Snowball effect tracking
│   └── CONTINUATION-PROMPT.md             # Resume guidance for GitHub Copilot
│
├── artifacts/
│   ├── implementation/                    # Generated code
│   ├── tests/                             # Test suites
│   └── docs/                              # Generated documentation
│
└── reports/
    ├── validation/                        # Validation reports per phase
    ├── performance/                       # Performance benchmark results
    └── integration/                       # Integration test reports
```

---

## 🚀 Getting Started

### For Implementers

1. **Read Phase 1:** Start with `phases/phase-01-knowledge-extension.md`
2. **Check Context:** Review `context/discovery.md` for workspace understanding
3. **Follow Sequence:** Complete phases in order (1→2→3→4, then parallelize)
4. **Track Progress:** Update `tracking/progress-tracker.json` after each task
5. **Validate:** Run validation checks after each phase completion

### For Reviewers

1. **Read Analysis:** Start with `analysis/gap-analysis.md` for high-level understanding
2. **Review Risks:** Check `analysis/risk-assessment.md` for concerns
3. **Validate Snowball:** Ensure `tracking/snowball.md` shows proper momentum
4. **Check Compliance:** Verify SKULL rules enforced in each phase

### For GitHub Copilot

**To resume this plan:**
```
Continue CORTEX5 enhancement epic from phase {current_phase}
```

**To validate progress:**
```
Validate CORTEX5 epic progress for phase {phase_number}
```

**To generate artifacts:**
```
Generate {artifact_type} for CORTEX5 epic phase {phase_number}
```

---

## 📚 References

**Architecture Docs:**
- `cortex-brain/documents/cortex-architecture-quick-ref.md` - CORTEX architecture overview
- `cortex-brain/documents/orchestrators-quick-ref.md` - Orchestrator documentation

**Configuration:**
- `cortex-brain/config/master-orchestrator.yaml` - Orchestrator routing config
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules (61 rules)
- `cortex-brain/response-templates-v4.yaml` - Response formatting

**Implementation Guides:**
- `.github/prompts/CORTEX.prompt.md` - Master Orchestrator entry point
- `src/orchestrators/master_orchestrator.py` - Master Orchestrator implementation

---

## ⚠️ Risks & Mitigations

### Critical Risks

**Risk 1: Knowledge merge accuracy <95%**
- **Impact:** Company knowledge fails to override CORTEX correctly
- **Mitigation:** Phase 4 includes comprehensive merge logic testing
- **Contingency:** Fallback to explicit override flags if merge fails

**Risk 2: Custom orchestrator corruption of CORTEX core**
- **Impact:** Custom orchestrators modify core files
- **Mitigation:** Namespace isolation + Git pre-commit hooks
- **Contingency:** Rollback via Git, re-enforce isolation rules

**Risk 3: Performance degradation >50ms**
- **Impact:** Knowledge queries slow down all orchestrators
- **Mitigation:** Phase 11 benchmarks, implement caching if needed
- **Contingency:** Async knowledge loading, lazy evaluation

**Risk 4: Parallel execution conflicts (Weeks 5-7)**
- **Impact:** Phases 5-10 interfere with each other
- **Mitigation:** Clear module boundaries, integration tests
- **Contingency:** Serialize execution if conflicts detected

### Medium Risks

**Risk 5: Custom orchestrator manifest schema changes**
- **Impact:** Breaking changes force rewrite of registered orchestrators
- **Mitigation:** Version manifest schema, support backward compatibility
- **Contingency:** Migration scripts for schema updates

**Risk 6: Company knowledge format inconsistency**
- **Impact:** Different companies use incompatible formats
- **Mitigation:** Phase 1 defines strict Markdown/YAML schema
- **Contingency:** Validation layer rejects non-compliant knowledge

---

## 📊 Timeline & Milestones

| Week | Milestone | Phases | Status |
|------|-----------|--------|--------|
| **1-2** | Foundation Complete | Phase 1 | 🟡 Not Started |
| **3** | Registry & Goal Detection | Phases 2-3 | 🟡 Not Started |
| **4** | Merge Logic Validated | Phase 4 | 🟡 Not Started |
| **5-6** | Custom Framework + TDD + Viewer | Phases 5, 8-9 | 🟡 Not Started |
| **7** | Selenium→Playwright + Rule Layering | Phases 6-7, 10 | 🟡 Not Started |
| **8** | Integration Prep | All phases | 🟡 Not Started |
| **9** | Final Validation & Go-Live | Phase 11 | 🟡 Not Started |

**Total Duration:** 9 weeks  
**Parallel Execution:** Weeks 5-7 (3 tracks)  
**Critical Path:** Phases 1→2→4→5→6→11

---

## 🎉 Success Definition

**Epic is successful when:**

1. ✅ 3+ companies registered with working knowledge libraries
2. ✅ 2+ custom orchestrators deployed (including Selenium→Playwright)
3. ✅ Zero CORTEX core corruption (all changes isolated)
4. ✅ Knowledge merge accuracy >95%
5. ✅ Performance overhead <50ms (knowledge queries)
6. ✅ 100% SKULL rule compliance
7. ✅ Documentation complete (architecture + API + deployment)
8. ✅ 2+ developers trained on custom orchestrator development
9. ✅ All integration tests passing (Phase 11)
10. ✅ Production deployment successful (1+ custom orchestrator live)

**Go-live criteria:** All 10 checkboxes ✅ + stakeholder sign-off

---

**Version History:**
- v1.0.0 (2025-12): Original CORTEX5 epic (goal detection focus)
- v2.0.0 (2026-01-06): Complete rewrite with Knowledge Extension + Custom Orchestrator architecture

**Maintained By:** CORTEX Planning System v5  
**Epic Owner:** Asif Hussain  
**Status:** 🟢 ACTIVE - Ready for Phase 1 execution
