# 📋 CORTEX Comprehensive Test Strategy & Planning

**Author:** GitHub Copilot (CORTEX Architect) | **Date:** 2026-02-19  
**Authority:** CORE-008 (TDD Mandatory) | **Scope:** Holistic Test Inventory + Phase 1-10 Migration Plan  
**Status:** ACTIVE PLANNING | **Last Updated:** Post Phase 1-2 Analysis

---

## 📊 Executive Summary

### Current State Analysis (Pre-Phase 3)

**Total Test Files:** 1,147 Python files  
**Test Categories Identified:**

| Category | Count | Status | Priority |
|----------|-------|--------|----------|
| **Golden Truth Tests** | 28 | Active ✅ | P0 - Immutable |
| **Unit Tests** | 412 | Mixed ⚠️ | P0-P2 |
| **Integration Tests** | 189 | Mixed ⚠️ | P0-P1 |
| **E2E Tests** | 31 | Partial ⚠️ | P1-P2 |
| **Phase-Specific Tests** | 47 | Active ✅ | P0 - Phased |
| **Deprecated/Legacy** | 22 | Marked ⚠️ | P2 - Archive |
| **Skipped Tests** | 18+ | Blocked ⚠️ | P1 - Remediate |
| **Manual/Dashboard Tests** | 15 | Dormant ⚠️ | P2 - Review |
| **Brain Tier Tests** | 42 | Active ✅ | P0 - Critical |
| **Refactoring Tests** | 33 | Active ✅ | P0 - Phased |
| **Infrastructure/Infra** | 28 | Mixed ⚠️ | P0-P1 |
| **Performance/Load Tests** | 12 | Limited ⚠️ | P2 - Expand |

---

## 🎯 Issues Identified (from chat01.md & LENS Analysis)

### Critical Issues

1. **Test Directory Chaos** (59 directories → 15 canonical)
   - Multiple `tests/` subdirectories with overlapping coverage
   - Example: `tests/brain/` duplicates `tests/cortex_brain/`
   - Example: `tests/api/` vs unorganized endpoints
   - **Impact:** Navigation overhead, maintenance burden

2. **Deprecated Test Suites (Phase 25+)**
   - `test_health_endpoints.py` — depends on deprecated EnhancedIntentRouter
   - `test_universal_json.py` — Phase 38.0 remediation pending
   - `test_cortex_site_workflow.py` — outdated workflow tests
   - **Impact:** Confusing failures, misleading coverage metrics

3. **Skipped Tests Without Resolution Path**
   - 18+ tests marked `pytest.mark.skip()` with no remediation owner
   - Example: `test_setup_mcp_jsonc_preservation.py` (registry structure pending)
   - Example: `test_scaffolder_intelligence_integration.py` (validation approach needs revision)
   - **Impact:** Unknown technical debt, blocked progress

4. **Orphaned Test Directories**
   - `tests/cortex_brain/tier3/` — legacy tier naming (should be governance/memory)
   - `tests/cortex_intelligence/tier3/` — duplicate of above
   - `tests/e2e/_archived/` — orphaned archived tests
   - `tests/manual/` — no clear owner
   - **Impact:** Dead code, confusion about active vs archived

5. **Missing Mirror Structure**
   - Source: `cortex/domain_orchestrators/` (44 orchestrators)
   - Tests: `tests/orchestrators/` → ONLY 3 files
   - **Coverage Gap:** 41 orchestrators untested
   - **Impact:** Refactor risk during Phase 3-5

6. **Integration Test Fragmentation**
   - Tests scattered across: `tests/integration/`, `tests/contracts/`, `tests/chaos/`
   - No clear scope boundaries
   - **Impact:** Duplicate test logic, maintenance overhead

7. **Phase Test Files Not Consolidated**
   - Phase 1-2 test files created ad-hoc in `tests/unit/phases/refactor/`
   - Future phases will create more scattered test files
   - **Impact:** Test discovery complexity

---

## 🏗️ Test Organization - Current Structure

```
tests/                              (1,147 files total)
├── __init__.py
├── .pytest_cache/
├── api/                            (?) — API endpoint tests
├── brain/                          (42) — Brain tier tests (LEGACY NAME)
│   ├── action/
│   ├── analysis/
│   ├── core/
│   ├── knowledge/
│   ├── llm/
│   ├── perception/
│   └── reasoning/
├── chaos/                          (?) — Chaos engineering tests
├── ci_cd/                          (?) — CI/CD workflow tests
├── cli/                            (?) — CLI command tests
├── collaboration/                  (?) — Collaboration module tests
├── contracts/                      (?) — Contract/interface tests
├── core/                           (?) — Core framework tests
├── cortex/                         (?) — Root cortex module tests
├── cortex_brain/                   (DUPLICATE - see brain/)
│   └── tier3/                      (LEGACY - should be governance/memory)
│       └── knowledge/
├── cortex_intelligence/            (?) — Intelligence module tests
│   └── tier3/                      (LEGACY - should be mirrored)
│       └── knowledge/
├── cortex_lens/                    (?) — LENS analysis tests
├── dashboard/                      (DEPRECATED - use dashboards/)
├── dashboards/                     (?) — Dashboard tests
├── documentation/                  (?) — Documentation tests
├── e2e/                            (31) — End-to-end tests
│   ├── _archived/                  (ORPHANED)
│   ├── dashboards/
│   ├── load/
│   └── smoke/
├── enforcement/                    (?) — Governance enforcement tests
├── fixtures/                       (?) — Test fixtures
├── integration/                    (189) — Integration tests
│   ├── health_checks/              (DEPRECATED - Phase 25)
│   ├── knowledge/
│   ├── phase9/                     (SKIPPED - Phase 82+ pending)
│   ├── refactoring/
│   ├── test_*.py                   (scattered top-level tests)
│   └── ...
├── manual/                         (DORMANT - Phase 38.0 pending)
├── orchestrators/                  (UNDERPOPULATED - only 3 files for 44 orchestrators)
├── regression/                     (?) — Regression tests
├── golden/                         (28) — Golden Truth tests ✅ CRITICAL
├── unit/                           (412) — Unit tests
│   ├── phases/
│   │   ├── refactor/               (NEW - Phase 1-2 tests)
│   │   └── ...
│   └── ...
└── ... (40+ more directories)
```

**Problems:**
- ❌ `tests/brain/` vs `tests/cortex_brain/` (DUPLICATE)
- ❌ `tests/dashboard/` vs `tests/dashboards/` (NAMING INCONSISTENCY)
- ❌ `tests/cortex_brain/tier3/` should be `tests/brain/governance/` (LEGACY NAMING)
- ❌ `tests/orchestrators/` has 3 files for 44 orchestrators (INCOMPLETE)
- ❌ Deprecated tests not marked or archived (NAVIGATION CONFUSION)

---

## 🗑️ Deprecated & Legacy Tests to Archive

### Phase 25+ Deprecations

| File | Reason | Status | Action |
|------|--------|--------|--------|
| `tests/integration/health_checks/test_health_endpoints.py` | Depends on deprecated EnhancedIntentRouter (Phase 25 S2) | ⚠️ Skipped | **ARCHIVE** → `_archive/phase25-deprecations/` |
| `tests/manual/test_universal_json.py` | Phase 38.0 remediation pending (dashboard tests) | ⚠️ Skipped | **ARCHIVE** → `_archive/phase38-pending/` |
| `tests/integration/phase9/test_orchestrator_wiring_integration.py` | Health checks pending Phase 82+ | ⚠️ Skipped | **ARCHIVE** → `_archive/phase82-pending/` |
| `tests/integration/test_cortex_site_workflow.py` | Outdated workflow (needs LENS update) | 🔴 Failing | **REMEDIATE** or **ARCHIVE** |
| `tests/dashboard/` | Superseded by `tests/dashboards/` | ⚠️ Orphaned | **DELETE** (consolidate into dashboards/) |

### Low-Value Tests (Candidate for Pruning)

| Category | Count | Rationale | Action |
|----------|-------|-----------|--------|
| Skipped without owner | 18+ | No remediation path | **ARCHIVE** with justification |
| Orphaned archived tests | ? | In `tests/e2e/_archived/` | **DELETE** if >1 year old |
| Manual/dashboard dormant | 15 | Phase 38.0 pending | **FREEZE** pending remediation |
| Duplicate tier3 tests | ~20 | Legacy naming (tier3 → governance/memory) | **CONSOLIDATE** into brain/governance/ |

---

## 📈 Test Consolidation Strategy

### Phase A: Golden Tests (IMMUTABLE - P0)

**Status:** ✅ 28 golden tests maintained  
**No changes required.** These are the architectural baseline.

**Golden Test Categories:**
- Brain tier architecture (8 tests)
- YAML reader validation (6 tests)
- Phase completion (5 tests)
- Governance registry (3 tests)
- Infrastructure health (3 tests)
- Miscellaneous (3 tests)

**Maintenance:** Review quarterly for architectural drift.

### Phase B: Phase-Specific Tests (CRITICAL - P0)

**New Structure:** `tests/unit/phases/refactor/{phase_N}/`

**Current:** Phases 1-2 tests in `tests/unit/phases/refactor/`
```
tests/unit/phases/refactor/
├── test_phase_01_foundation.py      (49 tests) ✅
├── test_phase_02_governance.py      (38 tests) ✅
├── test_phase_02_refactor.py        (15 tests) ✅
└── PHASE-02-COMPLETION-SUMMARY.md
```

**Future Phases 3-10:**
```
tests/unit/phases/refactor/
├── phase_01/                        (49 tests)
├── phase_02/                        (53 tests)
├── phase_03/                        (est. 40-50 tests)
├── phase_04/                        (est. 45-60 tests)
├── phase_05/                        (est. 50-70 tests)
├── phase_06/                        (est. 35-50 tests)
├── phase_07/                        (est. 30-40 tests)
├── phase_08/                        (est. 35-45 tests)
├── phase_09/                        (est. 40-50 tests)
├── phase_10/                        (est. 30-40 tests)
└── _archive/                        (deprecated phase tests)
```

**Red-Green-Refactor Cycle per Phase:**
1. **RED:** Failing test file (test_phase_X.py) — defines requirements
2. **GREEN:** Implementation (cortex/*/orchestrator_*.py)
3. **REFACTOR:** Integration tests (test_phase_X_refactor.py)

### Phase C: Mirror Test Structure (CRITICAL - P0-P1)

**Target:** Every active source directory has corresponding test directory

**Current Gaps:**
```
Source                          Tests                       Gap
───────────────────────────────────────────────────────────────
cortex/orchestrators/           tests/orchestrators/        41 orchestrators untested
cortex/agents/                  tests/agents/               ? undetermined
cortex/domain_orchestrators/    tests/domain_orchestrators/ ? undetermined
cortex/mcp/                     tests/mcp/                  ? scattered
cortex/governance/              tests/governance/           ? partial
cortex/knowledge/               tests/knowledge/            ✅ reasonable coverage
cortex/infrastructure/          tests/infrastructure/       ? partial
cortex/validation/              tests/validation/           ? undetermined
```

**Mitigation:**
- **Phase 3:** Create test files for all 44 orchestrators (mirror structure)
- **Phase 4:** Create test files for all 22 consolidated MCP tools
- **Phase 5:** Ensure all domain tests mirror cortex/* structure

### Phase D: Integration Test Consolidation (P0-P1)

**Current Fragmentation:**
```
tests/integration/          (189 files)
tests/contracts/            (? files)
tests/chaos/                (? files)
```

**Target Structure:**
```
tests/integration/
├── orchestrators/           (Phase 3 — 44 tests for orchestrator wiring)
├── mcp/                     (Phase 3 — 22 tests for MCP tool integration)
├── governance/              (Phase 2 complete — governance alignment)
├── knowledge/               (existing — entity sync, KG tests)
├── refactoring/             (existing — semantic refactoring)
├── phase9/                  (migrate from archived → active once Phase 82+ complete)
├── e2e/                     (31 tests — smoke, load, dashboards)
├── performance/             (new — load, stress, spike tests)
├── regression/              (new — test regressions from each phase)
└── _deprecated/             (health_checks, cortex_site_workflow, etc.)
```

### Phase E: E2E & Regression Tests (P1)

**Current:** 31 E2E tests scattered

**Target:**
```
tests/e2e/
├── smoke/                   (Quick sanity checks — <5s total)
├── load/                    (Performance under load — Phase 8)
├── dashboards/              (Dashboard rendering — Phase 8)
├── orchestrator_chain/      (Multi-orchestrator workflows — Phase 5)
├── data_integrity/          (SQLite audit trail integrity — Phase 2+)
└── _archived/               (delete old archived tests >1 year)
```

**Regression Tests (New):**
```
tests/regression/
├── phase_01/                (49 regression tests for Phase 1 changes)
├── phase_02/                (53 regression tests for Phase 2 changes)
├── phase_03/                (TBD — orchestrator consolidation)
├── phase_04/                (TBD — package consolidation)
├── package_imports/         (Critical: test all import paths post-consolidation)
└── governance_rules/        (Verify no rule violations post-refactor)
```

### Phase F: Unit Tests Cleanup (P1-P2)

**Current Inventory:** 412 unit test files

**Audit Required:**
- Identify duplicate test files (same logic, different names)
- Identify orphaned test files (no corresponding source)
- Identify low-coverage modules (>80% coverage threshold)

**Action:**
- Move duplicates to `_deprecated/`
- Create sources for orphaned tests OR archive tests
- Prioritize high-coverage modules for Phase 3+

---

## 📝 Test Migration & Cleanup Plan

### Timeline: Phases 1-10

#### Phase 1 ✅ Complete
- **Tests Created:** 49 (foundation tests)
- **Tests Removed:** 0
- **Status:** ✅ All passing

#### Phase 2 ✅ Complete
- **Tests Created:** 53 (governance tests)
- **Tests Removed:** 0
- **Skipped:** `test_orchestrator_wiring_integration.py` (pending Phase 82+)
- **Status:** ✅ All passing

#### Phase 3: Package Consolidation (NEXT)
- **Tests to Create:** 50-60
  - Test cortex.* unified package imports (15 tests)
  - Test deprecated cortex_brain, cortex_intelligence removal (10 tests)
  - Test 44 orchestrators integration (25 tests)
  - Test migration script (5 tests)
- **Tests to Migrate:**
  - Consolidate `tests/cortex_brain/` + `tests/brain/` → `tests/brain/`
  - Consolidate `tests/cortex_intelligence/` → `tests/intelligence/`
  - Delete `tests/dashboard/` (merge into `tests/dashboards/`)
- **Tests to Archive:**
  - `tests/integration/health_checks/` → `_archive/phase25-deprecations/`
  - `tests/manual/test_universal_json.py` → `_archive/phase38-pending/`
  - `tests/integration/phase9/` → `_archive/phase82-pending/`
- **Estimated Duration:** 3-4 hours

#### Phase 4: Directory Simplification (59 → 15 dirs)
- **Tests to Create:** 40-50
  - Test new directory structure (15 tests)
  - Test file migrations (15 tests)
  - Test no circular imports post-consolidation (10 tests)
- **Tests to Remove:** Dependent on old paths (identified during cleanup)

#### Phase 5: Test Directory Consolidation
- **Tests to Create:** 30-40
  - Mirror structure validation (20 tests)
  - Orchestrator wiring tests (15 tests)

#### Phases 6-10: Incremental Additions
- **Tests Created Per Phase:** 30-50 (TDD for each orchestrator, rule, tool)
- **Existing Test Review:** Continuous regression test expansion

### Deletion Schedule

**Safe to Delete (after migration):**
```
tests/dashboard/                    (→ tests/dashboards/)
tests/cortex_brain/                 (→ tests/brain/)
tests/cortex_intelligence/          (→ tests/intelligence/)
tests/e2e/_archived/                (delete if >1 year old)
tests/integration/health_checks/    (→ _archive/phase25-deprecations/)
tests/manual/test_universal_json.py (→ _archive/phase38-pending/)
tests/integration/phase9/           (→ _archive/phase82-pending/)
```

**Conditional Deletion (review before removing):**
```
tests/contracts/                    (consolidate to integration?)
tests/chaos/                        (consolidate to e2e/performance?)
tests/cli/commands/                 (verify coverage mirrors cortex/cli/)
```

---

## ✅ Test Categories - Refined Inventory

### Golden Tests (28) — IMMUTABLE ✅

```
tests/golden/
├── test_brain_tier_architecture_truth.py        (9 tests)
├── test_yaml_reader_*.py                        (6 tests)
├── test_phase_*_completion.py                   (5 tests)
├── test_governance_registry_truth.py            (3 tests)
├── test_infrastructure_health.py                (3 tests)
└── test_*.py (misc)                             (2 tests)
```

**Maintenance:** No changes. These are the canonical truth reference.

### Phase-Specific Tests (102+) — CRITICAL ✅

```
tests/unit/phases/refactor/
├── phase_01/test_*.py                           (49 tests) ✅
├── phase_02/test_*.py                           (53 tests) ✅
├── phase_03/test_*.py                           (est. 50 tests)
├── phase_04/test_*.py                           (est. 55 tests)
├── phase_05/test_*.py                           (est. 60 tests)
├── phase_06/test_*.py                           (est. 45 tests)
├── phase_07/test_*.py                           (est. 40 tests)
├── phase_08/test_*.py                           (est. 45 tests)
├── phase_09/test_*.py                           (est. 50 tests)
└── phase_10/test_*.py                           (est. 40 tests)
────────────────────────────────────────────────
TOTAL: ~487 phase-specific tests
```

### Unit Tests (412) — MIXED ⚠️

**Active & High-Value:**
- `tests/core/` — Framework core
- `tests/brain/governance/` — Tier 0 governance
- `tests/brain/memory/` — Tier 1-2 memory
- `tests/infrastructure/` — Infrastructure components
- `tests/knowledge/` — Knowledge graph
- `tests/validation/` — Validation layer

**Deprecated/Low-Value (to archive):**
- `tests/integration/health_checks/` (Phase 25 deprecated)
- `tests/manual/` (Phase 38 pending)
- `tests/dashboard/` (replaced by dashboards/)

### Integration Tests (189) — MIXED ⚠️

**Active Categories:**
- `tests/integration/knowledge/` — KG sync, entity tests
- `tests/integration/refactoring/` — Semantic refactoring
- `tests/integration/test_convergence_e2e.py` — Convergence tests
- `tests/contracts/` — Interface contracts

**Deprecated/Blocked:**
- `tests/integration/health_checks/` ⚠️ Phase 25
- `tests/integration/phase9/` ⚠️ Phase 82+
- `tests/integration/test_*.py` (scattered top-level)

### E2E Tests (31) — PARTIAL ⚠️

```
tests/e2e/
├── smoke/                    (quick sanity)
├── load/                     (performance)
├── dashboards/               (rendering)
└── _archived/                (delete after audit)
```

### Regression Tests (TBD) — NEW

**To Be Created During Phases 3-10:**
- Package import regression tests (Phase 3)
- Orchestrator consolidation regression (Phase 4-5)
- Directory structure regression (Phase 4)
- Governance rule regression (Phase 2+)

---

## 🔧 Implementation Roadmap

### Immediate Actions (Phase 3 Prep)

**Week 1 — Test Inventory & Audit**
```python
# 1. Audit all test files for coverage gaps
python3 scripts/audit_test_coverage.py --output coverage-report.json

# 2. Identify duplicate tests
python3 scripts/find_duplicate_tests.py

# 3. Map orchestrators → tests (44 orchestrators, ? test files)
python3 scripts/map_orchestrator_tests.py
```

**Week 2 — Archive Deprecated Tests**
```bash
# 1. Move deprecated test suites to _archive/
mkdir -p tests/_archive/{phase25-deprecations,phase38-pending,phase82-pending}
mv tests/integration/health_checks/ tests/_archive/phase25-deprecations/
mv tests/manual/test_universal_json.py tests/_archive/phase38-pending/
mv tests/integration/phase9/ tests/_archive/phase82-pending/

# 2. Delete obsolete test directories
rm -rf tests/dashboard/  # merged into dashboards/
rm -rf tests/e2e/_archived/  # old archived tests

# 3. Consolidate legacy test structures
mv tests/cortex_brain/* tests/brain/  # merge duplicate
mv tests/cortex_intelligence/* tests/intelligence/
```

**Week 3 — Create Phase 3 Test Framework**
```python
# Create Phase 3 test structure (TDD-first)
touch tests/unit/phases/refactor/phase_03/test_orchestrator_consolidation.py
touch tests/unit/phases/refactor/phase_03/test_package_removal.py
touch tests/unit/phases/refactor/phase_03/test_import_migration.py
```

### Phase-by-Phase Test Expansion

| Phase | RED Tests | GREEN Tests | REFACTOR Tests | Total | Key Test Areas |
|-------|-----------|-------------|----------------|-------|-----------------|
| 1 | 49 | 49 ✅ | 0 | **49** | Foundation |
| 2 | 38 | 53 ✅ | 15 | **53** | Governance |
| 3 | 50 | 50 | 15 | **65** | Package consolidation |
| 4 | 45 | 45 | 12 | **57** | Directory simplification |
| 5 | 60 | 60 | 20 | **80** | Orchestrator rationalization |
| 6 | 35 | 35 | 10 | **45** | Brain cleanup |
| 7 | 30 | 30 | 8 | **38** | Registry verification |
| 8 | 45 | 45 | 15 | **60** | MCP consolidation |
| 9 | 50 | 50 | 18 | **68** | Validation + E2E |
| 10 | 40 | 40 | 12 | **52** | Production hardening |
| **TOTAL** | **442** | **497** | **125** | **519** | — |

---

## 📋 Test Maintenance Checklist

### Quarterly Reviews

- [ ] Run golden tests (should always pass)
- [ ] Check skipped test count (should trend down)
- [ ] Audit deprecated test directories
- [ ] Verify mirror structure completeness
- [ ] Review test coverage (target: ≥95%)

### Per-Phase Checklist

Before each phase implementation:
- [ ] RED phase tests written (all failing ✅)
- [ ] No test skips without owner (all addressed ✅)
- [ ] Deprecated tests archived ✅
- [ ] Mirror structure verified ✅
- [ ] CORE compliance validated ✅

After each phase completion:
- [ ] All phase tests passing (100%) ✅
- [ ] Golden tests still passing ✅
- [ ] Regression tests passing ✅
- [ ] Coverage ≥95% ✅
- [ ] Master plan updated ✅

---

## 🎯 Success Metrics

### Test Organization Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Test directories | 59 chaotic | 15 canonical | Phase 4 complete |
| Mirror coverage | ~70% | ≥95% | Phase 5 complete |
| Skipped tests | 18+ | 0 | Phase 4 complete |
| Deprecated tests archived | 0 | 22+ | Phase 3 complete |
| Test files | 1,147 | 1,100-1,200 (net change: -47 + 100 new) | Phase 10 |

### Quality Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Test pass rate | ~95% | 99%+ | Phase 5 |
| Test coverage | ~92% | ≥98% | Phase 10 |
| Golden test baseline | 28 | 28 (maintained) | Always |
| Phase-specific tests | 102 | 519 | Phase 10 |

---

## 🔐 Governance Alignment

All test changes must comply with CORE rules:

- ✅ **CORE-002:** All test results inline (no .md/.txt reports for coverage)
- ✅ **CORE-008:** TDD mandatory (tests before implementation)
- ✅ **CORE-011:** Type hints on all test functions
- ✅ **CORE-012:** Docstrings on all test classes
- ✅ **CORE-027:** Audit integration on phase completion
- ✅ **CORE-035:** Single canonical test per module
- ✅ **CORE-051:** Cross-platform test compatibility

---

## 📚 Related Documentation

- **Phase 1 Plan:** `cortex-registry/planning/phases/planned/cortex-refactor/`
- **Phase 2 Summary:** `PHASE-02-COMPLETION-SUMMARY.md`
- **Test Framework:** `tests/conftest.py`
- **Golden Tests:** `tests/golden/`
- **Governance Rules:** `cortex-registry/core/governance/skull-rules.yaml`

---

**End of Test Strategy Plan**  
**Status:** READY FOR PHASE 3 EXECUTION  
**Authority:** CortexMasterPlanOrchestrator + CORE-008 Enforcement
