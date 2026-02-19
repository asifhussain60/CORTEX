# CORTEX Master Plan Comparison
## cortex-master.yaml (Historical) vs. cortex-refactor-master.yaml (New Plan)

**Author:** CORTEX Architect | **Date:** 2026-02-19 | **Authority:** CortexMasterPlanOrchestrator ✅

---

## Executive Summary

The **cortex-refactor-master.yaml** represents a fundamental **architectural transformation** from CORTEX's current fragmented state (51 completed phases) into a **single cohesive brain** through a focused 10-phase refactor plan. This is not an incremental update—it's a **consolidation and rationalization** that reduces complexity by 60-70% while maintaining backward compatibility and test coverage.

**Key Outcome:** Transform from 3 packages + 120 orchestrators + 34+ MCP tools into **1 unified package + 44 orchestrators + 22 MCP tools** with canonical directory structure.

---

## 📊 Comparison Matrix

| Dimension | cortex-master.yaml | cortex-refactor-master.yaml | Delta | Impact |
|-----------|-------------------|---------------------------|-------|--------|
| **Phases** | 51 completed | 10 planned (pending) | -41 | Focused execution |
| **Scope** | Historical record of all work | Focused transformation only | Narrower | Clarity |
| **Packages** | 3 (cortex/, cortex_intelligence/, cortex_lens/) | 1 (cortex/ only) | -66% | Maintainability ⬆️ |
| **Orchestrators** | 120 total | 44 active (~44 reduction) | -64% | Reduced dead code |
| **MCP Tools** | 34+ (fragmented) | 22 consolidated | -35% | Focused API surface |
| **Top-Level Dirs** | 59 | ~15 canonical | -75% | Mental model clarity |
| **Governance Dirs** | 9 scattered | 1 unified | -88% | SSOT for compliance |
| **LENS Dirs** | 3 fragmented | 1 unified | -66% | Code intelligence cohesion |
| **Domain Brain Dirs** | 3 scattered | 1 unified | -66% | Single brain architecture |
| **Status** | ✅ PRODUCTION READY | ⏳ APPROVED (pending execution) | In transition | Strategic upgrade |
| **Test Baseline** | 428 golden tests passing | 428 golden tests (zero regression) | ✓ maintained | Quality guarantee |
| **Authority** | Passive record | Active orchestrator-managed | Active governance | Real-time tracking |

---

## 🎯 Strategic Improvements

### 1. **Package Consolidation (Phase 3)**
**Current State:** Three separate packages create import ambiguity and duplicate logic
```
cortex/                  — Main domain code
cortex_intelligence/     — Governance, audit, memory (often imports cortex/ + cortex_lens/)
cortex_lens/             — Code analysis (imports both cortex/ and cortex_intelligence/)
```

**New State:**
```
cortex/
  ├── intelligence/      — ALL intelligence unified (no external deps)
  │   ├── memory/        — Governance audit, persistence
  │   └── lens/          — Code analysis (canonical)
  └── [other domains]
```

**Benefits:**
- ✅ Eliminates circular dependency risks
- ✅ Single import path: `from cortex.intelligence import ...`
- ✅ Reduces accidental coupling between intelligence layers
- ✅ Accelerates onboarding: one package to understand

---

### 2. **Brain Deduplication (Phase 4)**
**Current State:** `brain/` directory (261 files, 28 subdirs) coexists with canonical domains
```
brain/core/                    ← Duplicates cortex/core/
brain/governance/              ← Duplicates cortex/governance/
brain/domain_orchestrators/    ← Duplicates cortex/orchestrators/domain/
```

**New State:** `brain/` dissolved into proper domains
```
cortex/core/                   ← SINGLE canonical location
cortex/governance/             ← SINGLE canonical location
cortex/orchestrators/domain/   ← SINGLE canonical location
_archive/brain/                ← Historical reference only
```

**Benefits:**
- ✅ Eliminates 261-file duplication (memory + code complexity)
- ✅ Single source of truth for each capability
- ✅ Faster `grep`, code search, and refactoring
- ✅ Clear authority for every file (zero "which version is canonical?")

---

### 3. **Orchestrator Rationalization (Phase 5)**
**Current State:** 120 orchestrators scattered across codebase
- ~76 dormant/dead (zombie code consuming mental bandwidth)
- ~40 active (actual productive orchestrators)
- 5 known duplicates (enforcement, rollback, hot_reload, dashboard, tdd)

**New State:** Ruthless pruning to ~44 active orchestrators
```
Before:  120 total (40 active + 76 dead) = 63% waste
After:   44 active (100% accountability)
Reduction: 76 dead files archived + 0 duplicates
```

**Benefits:**
- ✅ Faster CI/CD (fewer files to scan)
- ✅ Clearer orchestrator catalog (CORE-035 single implementations)
- ✅ Reduced MCP tool surface area (34→22)
- ✅ Every orchestrator bound to workflow template (governance)

---

### 4. **MCP Consolidation (Phase 5 integration)**
**Current State:** 34+ MCP tools with unclear boundaries
- Toolkit tools absorbed separately
- Versioned tools duplicated (e.g., `cortex_health_check_v1`, `cortex_health_check_v2`)
- Governance tools scattered (challenge, validation, etc.)

**New State:** 22 consolidated tools with clear responsibilities
```
Removed:
- cortex_challenge (→ absorbed into MasterOrchestrator.governance_gate)
- Duplicate versioned tools (→ merged into single canonical)
- Toolkit utilities (→ integrated into cortex/core/toolkit)

Added:
- SQLite audit integration (every orchestrator traces)
- Infrastructure catalog tool (cortex_onboard_infrastructure)
```

**Benefits:**
- ✅ Smaller MCP API surface (easier to document)
- ✅ Faster tool discovery and invocation
- ✅ Unified versioning strategy (no v1/v2 confusion)
- ✅ SQLite audit wired into every operation (compliance automation)

---

### 5. **Directory Simplification (Phases 6–7)**
**Current State:** 59 top-level cortex/ directories
```
cortex/
  ├── automation/           ← Consolidate into core
  ├── capacity/             ← Consolidate into core
  ├── collaboration/        ← Consolidate into core
  ├── confirmation/         ← Consolidate into core
  ├── devx/                 ← Consolidate into core
  ├── phase_38/             ← Delete (historical)
  ├── phase_executors/      ← Delete (historical)
  ├── phase_management/     ← Delete (historical)
  ... 50+ more directories
```

**New State:** ~15 canonical domains
```
cortex/
  ├── core/               ← Factories, validators, base classes
  ├── intelligence/       ← Governance, memory, LENS, domain brain
  ├── orchestrators/      ← Master, domain, support orchestrators
  ├── mcp/               ← MCP tool implementations
  ├── governance/        ← Rules, compliance, audit
  ├── observability/     ← Logging, tracing, metrics
  ├── infrastructure/    ← Platform APIs, deployment
  ├── security/          ← Auth, secrets, validation
  ├── knowledge/         ← Knowledge bases, reasoning
  ├── interaction/       ← Human-AI interaction patterns
  ├── storage/           ← Databases, caching, persistence
  ├── testing/           ← Test utilities, fixtures, runners
  ├── templates/         ← Workflow/config templates
  ├── config/            ← Runtime configuration
  └── validation/        ← Schema validation, linting
```

**Benefits:**
- ✅ Developers can locate any capability in <30 seconds
- ✅ Directory tree is self-documenting (no guessing game)
- ✅ Test structure mirrors source (confidence in coverage)
- ✅ Removes 44+ historical phase directories (mental clutter)

---

### 6. **Test Consolidation (Phase 7)**
**Current State:** 55 test directories, many orphaned
```
tests/
  ├── phase_23/               ← Orphaned historical phase
  ├── phase_49/               ← Orphaned historical phase
  ├── phase_52-56_a, etc./    ← 7+ historical phase dirs
  ├── dashboard/ + dashboards/ ← Duplicate directories
  ├── cortex/ + cortex_brain/  ← Duplicate coverage
```

**New State:** ~15 test directories mirroring source
```
tests/
  ├── orchestrators/
  ├── intelligence/
  ├── governance/
  ├── mcp/
  ├── infrastructure/
  ├── integration/
  ├── golden/                  ← High-value scenario tests (428+)
  └── fixtures/
```

**Benefits:**
- ✅ Developers immediately know where to add tests
- ✅ Low-value tests pruned (test value scorer < 0.3)
- ✅ Coverage remains ≥95% with 30% fewer test files
- ✅ CI/CD time reduced (fewer paths to execute)

---

### 7. **Governance Alignment (Phase 2)**
**Current State:** Governance rules scattered
```
cortex-registry/
  ├── governance/
  │   ├── skull-rules.yaml       ← MAIN location
  ├── cortex/governance/         ← DUPLICATE location
  ├── _cortex-master/governance/ ← ANOTHER DUPLICATE
  └── ... multiple skull-rules.yaml copies
```

**New State:** Single source of truth
```
cortex-registry/governance/
  ├── skull-rules.yaml           ← SINGLE canonical location
  ├── enhancement-actions.yaml   ← New CORE-058 through CORE-063 rules
  └── tier-alignment.yaml        ← Tier 1 & 2 alignment (zero stale refs)
```

**New Governance Rules Added:**
- **CORE-058:** SQLite WAL mode mandatory
- **CORE-059:** MCP footprint auditing
- **CORE-060:** SDLC brain governance
- **CORE-061:** Convergence Crystal Language (CCL) integration
- **CORE-062:** Plan-first execution requirement
- **CORE-063:** Challenge-first governance gate

**Benefits:**
- ✅ Single source of truth (no conflicting rule versions)
- ✅ New rules cover emerging patterns (SQLite audit, CCL)
- ✅ Automatic compliance checking via EnforcementOrchestrator
- ✅ 36 rules aligned to refactored architecture

---

### 8. **Registry & Documentation Alignment (Phase 8)**
**Current State:** Stale YAML references in registry
```
cortex-registry/workflows/
  ├── References to deleted orchestrators
  ├── Paths pointing to archived components
  ├── Duplicate workflow templates
  └── Incomplete infrastructure catalog
```

**New State:** Clean, verified registry
```
cortex-registry/
  ├── workflows/
  │   └── Every active orchestrator has template (1:1 mapping)
  ├── infrastructure-catalog.yaml
  │   └── Company platforms, APIs, applications (NEW)
  ├── mcp-consolidation-matrix.yaml
  │   └── 34→22 tool migration decisions
  └── All YAML references verified green
```

**Benefits:**
- ✅ Zero broken references (registry integrity verified)
- ✅ Infrastructure-as-code ready (external system onboarding)
- ✅ MCP tool decisions documented (audit trail)
- ✅ Workflow templates used by CortexMasterPlanOrchestrator (automation)

---

## 🛡️ Risk Mitigation & Guarantees

### Zero Regression Guarantee
| Area | Verification | Method |
|------|--------------|--------|
| **Tests** | 428 golden tests passing | Pre/post test run comparison |
| **Functionality** | Every deliverable has integration test | Regression test suite |
| **Performance** | MCP <200ms p95, LENS scan <5s | Chaos testing + benchmarks |
| **Governance** | CORE rules enforced at commit | EnforcementOrchestrator |

### Phase Dependencies Ensure Safety
```
Phase 1 (Foundation) → Phase 2 (Governance) → Phase 3 (Packages) → ... → Phase 10 (Production)
  ↓
Each phase tests the previous phase's guarantees before proceeding
  ↓
MANDATORY validation loop at end of each phase
```

### SQLite Audit Integration
Every orchestrator's teardown step writes to unified SQLite audit database:
- Timestamp, orchestrator ID, status, errors, duration
- WAL mode for concurrent access (safe)
- Automated cleanup of stale entries (no bloat)
- One unified audit source (cortex/infrastructure/audit_db.py)

---

## 📈 Impact Timeline

| Phase | Duration | Key Outcomes | Risk |
|-------|----------|------------|------|
| **Phase 1** | ~2 days | Foundation safety net, manifest | Low |
| **Phase 2** | ~1 day | Governance alignment, 6 new rules | Low |
| **Phase 3** | ~2 days | Package consolidation, zero regression | Medium |
| **Phase 4** | ~3 days | Brain deduplication (261 files) | High (requires careful migration) |
| **Phase 5** | ~3 days | Orchestrator rationalization (76 dead archived) | High (consolidation + testing) |
| **Phase 6** | ~2 days | Directory cleanup (59→15) | Medium |
| **Phase 7** | ~2 days | Test consolidation (55→15 dirs) | Medium |
| **Phase 8** | ~1 day | Registry alignment | Low |
| **Phase 9** | ~2 days | Final verification, archive deletion | Medium |
| **Phase 10** | ~2 days | Production hardening, chaos testing | Low |
| **TOTAL** | **~20 days** | **v2.0.0-cohesive-brain** | Managed |

---

## 🎯 Success Metrics

### Baseline → Target Transformation

| Metric | Baseline | Target | Improvement |
|--------|----------|--------|-------------|
| **Packages** | 3 | 1 | -66% (single namespace) |
| **Orchestrators** | 120 | 44 | -63% (active only) |
| **Dead Code** | 76 files | 0 active | Archived safely |
| **MCP Tools** | 34+ | 22 | -35% focused API |
| **Top-Level Dirs** | 59 | 15 | -75% clarity |
| **Governance Dirs** | 9 | 1 | SSOT |
| **Test Dirs** | 55 | 15 | -73% focus |
| **Golden Tests Passing** | 428 | 428 | ✅ zero regression |
| **Test Coverage** | ~90% | 95%+ | Enhanced |
| **Time to Find Capability** | ~2-5 min | ~30 sec | 6-10x faster |
| **CI/CD Cycle Time** | Variable | <5 min | Faster |
| **Code Mental Model** | Fragmented | Cohesive | Developer velocity ⬆️ |

---

## 💡 Improvements Summary (8 Major Categories)

| Category | Before | After | Benefit |
|----------|--------|-------|---------|
| **1. Package Architecture** | 3 packages (circular deps) | 1 package (clean imports) | No more import confusion |
| **2. Brain Organization** | `brain/` + domains (duplicate) | Unified domains only | Single source of truth |
| **3. Orchestrators** | 120 (40% dead) | 44 (100% active) | Faster development |
| **4. MCP Tools** | 34+ (scattered) | 22 (consolidated) | Smaller API surface |
| **5. Directories** | 59 top-level (chaotic) | 15 canonical (clear) | Self-documenting structure |
| **6. Governance** | 9 locations (conflicts) | 1 location (SSOT) | Automatic compliance |
| **7. Tests** | 55 dirs (orphaned) | 15 dirs (mirrored) | Confident coverage |
| **8. Registry** | Stale references | Verified green | Automation-ready |

---

## 🚀 Execution Authority

### Current State (cortex-master.yaml)
- **Orchestrator:** Passive historical record
- **Authority:** Manual phase tracking
- **Status:** 51 phases complete, production ready
- **Update Frequency:** Manual (human-driven)

### New State (cortex-refactor-master.yaml)
- **Orchestrator:** CortexMasterPlanOrchestrator (active)
- **Authority:** Workflow template: `master-plan-execution.yaml`
- **Status:** 10 phases approved, pending execution
- **Update Frequency:** Automated (every phase completion)
- **Tracking:** Real-time via workflow engine

### Workflow Engine Integration
```
CortexMasterPlanOrchestrator.load_workflow_template("master-plan-execution.yaml")
  ├── Stage 0: LENS scan (code intelligence)
  ├── Stage 1-8: Execute phase (test-first)
  ├── Stage 9: Validation loop (regression check)
  └── Stage 10: Update cortex-refactor-master.yaml + commit
```

---

## ✅ Definition of Done (Phase 9 Checkpoint)

Phase 9 includes an **18-point Definition of Done** checklist:

1. ✅ Capability manifest: every item verified green
2. ✅ All 22 MCP tools respond correctly
3. ✅ Full regression suite: unit + integration + golden + e2e
4. ✅ SQLite verification: 3 DBs only, WAL mode, auto-cleanup
5. ✅ MCP consolidation verified: exactly 22 tools
6. ✅ `_archive/` safely deleted (permanent)
7. ✅ Zero imports from dissolved packages
8. ✅ All governance rules aligned (36/36)
9. ✅ 428 golden tests passing (zero regression)
10. ✅ Directory structure validated (15 canonical)
11. ✅ Test structure mirrored (all source dirs have tests)
12. ✅ Orchestrator classes rationalized (44 active)
13. ✅ Workflow templates linked (every orchestrator)
14. ✅ Infrastructure catalog populated
15. ✅ Documentation updated (cortex-docs reflects new structure)
16. ✅ LENS scans show zero deduplication risks
17. ✅ Architecture drift detection: green
18. ✅ Production SLOs defined and baselined

---

## 🎓 Key Takeaways

### For Architects
The refactor transforms CORTEX from a **multi-domain system with fragmented intelligence** into a **single cohesive brain** with clear responsibilities. This enables:
- Faster decision-making (single place to check rules/memory/LENS)
- Reduced cognitive load (fewer places to look)
- Automated governance (CORE rules embedded in workflow)

### For Engineers
The refactor **significantly reduces complexity** while maintaining test coverage:
- Smaller codebase to understand (59→15 dirs)
- Fewer orchestrators to manage (120→44)
- Clearer patterns (one package import style)
- Faster builds (fewer files to parse)

### For DevOps
The refactor **simplifies deployment** and **improves auditability**:
- Single package deployment (vs. 3)
- Unified SQLite audit trail
- Infrastructure catalog (external systems)
- Hardened SLOs (chaos tested)

### For Operations
The refactor **consolidates governance** and **automates compliance**:
- Single governance source (1 location, not 9)
- Automatic rule enforcement (EnforcementOrchestrator)
- Audit integration (every orchestrator traces)
- Zero manual governance overhead

---

## 🔗 Next Steps

1. **Review this comparison** ← You are here
2. **Approve Phase 1 execution** → Type `proceed` in CORTEX Architect chat
3. **Monitor via cortex-refactor-master.yaml** → Real-time progress tracking
4. **Schedule Phase 2 kickoff** → Governance alignment (CORE-058..063)
5. **Communicate to stakeholders** → Architecture transformation (v2.0.0-cohesive-brain)

---

**Authority:** CortexMasterPlanOrchestrator | **Status:** APPROVED | **Next Review:** Phase 1 completion | **Version:** 1.0 | **Date:** 2026-02-19
