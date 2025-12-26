# Phase 8 Test Expansion Plan

**Date:** December 23, 2025  
**Status:** 🔄 IN PROGRESS  
**Current Coverage:** 10.05%  
**Target Coverage:** 95%+  
**Tests Passing:** 1,678 / 1,678 (100% pass rate)

---

## 🎯 Strategic Approach

Given the 85% coverage gap (10% → 95%), we'll use **high-leverage testing** rather than brute-force expansion:

### Philosophy
1. **Focus on ACTIVE code** (CORTEX 4.0, not legacy 3.0)
2. **Test critical paths** (orchestrators, brain, agents)
3. **Defer low-value code** (utilities, collectors, archived modules)
4. **Accept 90%** for non-critical modules (vs 95% everywhere)

### Revised Targets (Pragmatic)
- **Orchestrators (16 core):** 95%+ (currently 88% avg for tested ones)
- **Agents (7 active):** 95%+ (currently varies)
- **Brain Tiers (0-3):** 90%+ (currently <20% avg)
- **DI Container:** 95%+ (currently 85%)
- **Utilities (critical):** 90%+ (currently varies)
- **Legacy/Archived:** 50%+ acceptable (will be deleted in Phase 14)

### Realistic Phase 8 Goal
- **Overall Coverage:** 10% → **75%** (not 95%)
- **Critical Modules:** 95%+ (orchestrators, agents, brain core)
- **Supporting Modules:** 80%+ (utilities, frameworks)
- **Legacy Modules:** Accept low coverage (deletion planned)

---

## 📋 Task 8.2: Unit Test Expansion (24h)

### Autonomous Execution Strategy

Rather than manually writing 200+ tests, we'll use **TDD Orchestrator** to auto-generate tests for priority modules.

#### Step 1: TDD Orchestrator Self-Improvement (2h)
**Current:** 88.62% coverage (30 missing lines)  
**Target:** 98%+

**Approach:** Use TDD Orchestrator to test itself (recursive meta-testing)

```bash
# Generate tests for TDD Orchestrator's missing coverage
pytest --cov=src/orchestrators/tdd/tdd_orchestrator.py --cov-report=term-missing
# Identify missing lines (982-991, 995, 1025-1026, etc.)
# Use TDD Orchestrator to generate tests for these lines
```

**Expected Output:** 20 new tests, 2 hours

#### Step 2: Planning System Enhancement (4h)
**Modules:**
- plan_executor.py (83.33% → 97%)
- session_manager.py (84.55% → 97%)
- git_checkpoint_integration.py (93.39% → 97%)

**Approach:** Auto-generate tests using TDD Orchestrator

**Expected Output:** 40 new tests, 4 hours

#### Step 3: Brain Tier Testing (8h)
**Priority:**
- Tier 1: conversation_manager.py, session_manager.py, queue_manager.py
- Tier 2: knowledge_graph.py
- Tier 0: hybrid_brain_manager.py, brain_template_loader.py

**Approach:** Manual test creation (complex state management)

**Expected Output:** 60 new tests, 8 hours

#### Step 4: Orchestrator Batch Testing (6h)
**Targets:**
- Sanitization (86.59% → 95%)
- Autonomous Execution (91% → 95%)
- DevOps (87.27% → 95%)
- Documentation modules (84-94% → 95%)

**Approach:** TDD Orchestrator batch generation

**Expected Output:** 50 new tests, 6 hours

#### Step 5: DI Container & Utilities (4h)
**Targets:**
- service_container.py (85.79% → 95%)
- decorators.py (80.95% → 95%)
- Progress Synchronizer (need baseline)
- Unified Entry Point (need baseline)

**Approach:** Mix of auto-generation + manual

**Expected Output:** 30 new tests, 4 hours

---

## 🚀 Autonomous Execution Commands

### Generate Tests for Specific Module

```bash
# Use TDD Orchestrator to generate missing tests
pytest --cov=src/orchestrators/tdd/tdd_orchestrator.py --cov-report=term-missing

# Extract missing lines
# Lines: 982-991, 995, 1025-1026, 1050-1051, 1068, 1113-1147

# Generate tests via TDD workflow
# (Manual intervention: identify test scenarios for missing lines)
```

### Batch Test Generation Pattern

```python
# Create test generation script
target_modules = [
    ('src/orchestrators/planning/plan_executor.py', 83.33, 97),
    ('src/orchestrators/planning/session_manager.py', 84.55, 97),
    ('src/orchestrators/sanitization/sanitization_orchestrator.py', 86.59, 95),
    # ... more modules
]

for module_path, current_coverage, target_coverage in target_modules:
    # 1. Run coverage analysis
    # 2. Identify missing lines
    # 3. Analyze code to determine test scenarios
    # 4. Generate test file
    # 5. Run tests and verify coverage increase
    pass
```

---

## 📊 Progress Tracking

### Week 14 Goals (Current)

| Day | Task | Target | Status |
|-----|------|--------|--------|
| Day 1 | Task 8.1: Coverage Audit | Baseline: 10.05% | ✅ COMPLETE |
| Day 2 | Task 8.2: TDD Self-Test | TDD: 98%+ | 🔄 IN PROGRESS |
| Day 3 | Task 8.2: Planning Tests | Planning: 95%+ | ⏳ PENDING |
| Day 4 | Task 8.2: Brain Tests | Brain: 90%+ | ⏳ PENDING |
| Day 5 | Task 8.2: Orchestrator Batch | Various: 95%+ | ⏳ PENDING |
| Day 6 | Task 8.3: Integration Tests | 50 tests | ⏳ PENDING |

### Coverage Milestones

| Milestone | Target | Current | Progress |
|-----------|--------|---------|----------|
| Baseline | 10% | 10.05% | ✅ |
| Quick Wins | 30% | 10.05% | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0% |
| Core Modules | 50% | 10.05% | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0% |
| Phase 8.2 Target | 75% | 10.05% | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0% |
| Phase 8 Final | 95% | 10.05% | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0% |

---

## 🔍 Quality Gates

### Per-Module Acceptance Criteria

Before marking module "complete":
- [ ] Coverage ≥ target (95% for critical, 90% for supporting)
- [ ] All new tests passing (100% pass rate)
- [ ] No flaky tests (run 3x, all pass)
- [ ] Edge cases covered (null, empty, boundary, invalid)
- [ ] Error paths tested (exceptions, validation failures)

### Phase-Level Acceptance Criteria

Before completing Task 8.2:
- [ ] 200+ new tests created
- [ ] Overall coverage: 10% → 75%
- [ ] Critical modules (orchestrators/agents): 95%+
- [ ] Brain tiers: 90%+
- [ ] DI container: 95%+
- [ ] Test execution time: <5 minutes
- [ ] Zero test failures

---

## 🚨 Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Auto-generation produces low-quality tests | HIGH | MEDIUM | Manual review all generated tests |
| Complex modules too hard to test | HIGH | MEDIUM | Accept lower coverage for complex state machines |
| Test execution time exceeds 5 minutes | MEDIUM | HIGH | Parallelize tests, optimize fixtures |
| Coverage tool inaccurate for certain code | LOW | LOW | Manual code review supplement |

---

## 📝 Next Actions

**Immediate (Day 2):**
1. ✅ Remove placeholder tests (DONE - 4 files deleted)
2. ✅ Confirm clean baseline (DONE - 10.05%, 1,678 passing)
3. 🔄 Begin TDD Orchestrator self-testing
4. 🔄 Generate 20 tests for missing coverage in TDD Orchestrator

**This Week (Days 3-6):**
- Generate Planning System tests (40 tests)
- Create Brain Tier tests manually (60 tests)
- Batch-generate orchestrator tests (50 tests)
- Complete DI + utilities tests (30 tests)

**Next Week (Week 15):**
- Task 8.3: Integration tests (50 tests)
- Task 8.4: Performance benchmarks
- Task 8.5: Quality gates
- Task 8.6: Backward compatibility

---

**Last Updated:** December 23, 2025 14:30 UTC  
**Status:** Task 8.1 ✅ | Task 8.2 🔄 IN PROGRESS  
**Next Milestone:** TDD Orchestrator 98% coverage (2 hours)
