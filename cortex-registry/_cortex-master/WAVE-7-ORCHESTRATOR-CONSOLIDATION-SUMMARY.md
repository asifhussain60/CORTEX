# WAVE-7: Orchestrator Consolidation - High-ROI Architecture Redesign

**Status:** READY  
**ROI:** 9.2/10 (SECOND HIGHEST - tied with Wave 6)  
**Duration:** 10-18 days (parallelizable: 4 tracks)  
**Priority:** P1-HIGH-ROI  

---

## 📊 Executive Summary

### **The Problem**
CORTEX suffers from **4.4x orchestration bloat**:
- **Registered**: 26 orchestrators (wiring.yaml)
- **Physical files**: 114 files
- **Total classes**: 201+ orchestrator classes
- **Duplication**: 87% (175+ orphaned orchestrators)

### **The Solution**
**Behavior-Driven Consolidation (BDC)** via multi-cycle TDD:
- Consolidate to **15 core orchestrators** (42% reduction)
- Eliminate **78-83% of code** (45k → 12k LOC)
- Implement **zero-friction debugging** (auto-marker injection)
- Enable **master plan execution** (registry plans → automated workflow)

### **The Innovation**
1. **Multi-Cycle TDD**: Iterative RED→GREEN→REFACTOR until 85%+ coverage + <200ms latency
2. **EventBus-Driven Debugging**: Test fails → markers auto-injected → developer opens file → markers present
3. **Master Plan Execution**: MasterOrchestrator reads cortex-registry → delegates to enhanced orchestrators

---

## 🎯 Three Enhancement Package

| ID | Title | Duration | ROI | Value |
|----|-------|----------|-----|-------|
| **ENH-087** | Orchestrator Consolidation | 10-14 days | 9.2 | 78% code reduction, EventBus decoupling, Strategy Pattern |
| **ENH-088** | Multi-Cycle TDD | 8-12 days | 9.0 | Iterative quality refinement, holistic refactor gate |
| **ENH-089** | EventBus Debugger | 13-18 days | 9.3 | Zero-friction debugging, 260 hours/year saved |

**Combined ROI**: 9.2/10 (architecture transformation + developer productivity)

---

## 🏗️ Four Parallel Tracks (ENH-087)

### **Track 1: Core Layer** (P0-CRITICAL, 10-14 days)
**Target**: 4 consolidated orchestrators

| Before | After | Method |
|--------|-------|--------|
| `MasterOrchestrator` + `CentralBrainOrchestrator` + `ResponseAssemblyOrchestrator` | `MasterOrchestrator` | Absorb + StageExecutionStrategy |
| `IntentRouter` + `FuzzyIntentMatcher` | `IntentRouter` | Absorb + plugin pattern |
| `TDDOrchestrator` + `WrappedTDDOrchestrator` | `TDDOrchestrator` | Absorb + multi-cycle capability |
| `InteractionOrchestrator` + `ConversationOrchestrator` + `ComprehensionSession` | `InteractionOrchestrator` | Mixin composition |

**Enhancement**: Multi-cycle TDD + EventBus decoupling (12 dependencies eliminated)

---

### **Track 2: Domain Layer** (P1-HIGH, 8-12 days)
**Target**: 4 consolidated + 1 new orchestrator (DebuggerOrchestrator)

| Consolidation | Capability Gained |
|---------------|-------------------|
| `EnhancedRefactoringOrchestrator` ← 3 orchestrators | Debugger integration hooks |
| `EnhancedPlanningOrchestrator` ← 2 orchestrators | Master plan execution |
| `EnhancedDocumentationOrchestrator` ← 1 | None (already canonical) |
| `AutonomousExecutionEngine` | Multi-step TDD capability |
| **NEW: DebuggerOrchestrator** | Zero-friction debugging via EventBus |

**Innovation**: EventBus-driven debugging workflow
```
Test fails → TDDOrchestrator emits TEST_FAILURE
→ DebuggerOrchestrator subscribes → auto-injects markers
→ Developer opens file → markers already present
```

---

### **Track 3: Support Layer** (P1-MEDIUM, 6-8 days)
**Target**: 15 orchestrators → utility modules

| Orchestrator | Converts To | Rationale |
|--------------|-------------|-----------|
| `ToolDiscoveryOrchestrator` | `orchestrator_utils.discover_tools()` | Single method, no state |
| `UpgradeOrchestrator` | `lifecycle_utils.upgrade_system()` | Configuration script |
| `RollbackOrchestrator` | `lifecycle_utils.rollback_to_checkpoint()` | Lifecycle utility |
| `SetupOrchestrator` | `setup_utils.configure_environment()` | One-time setup |

**Time Savings**: Single-cycle TDD (utilities are simple) → 50% faster

---

### **Track 4: Orphan Cleanup** (P2-LOW, 4-6 days)
**Target**: Delete 58-68 orphaned orchestrators

| Category | Count | Action |
|----------|-------|--------|
| Test mocks | 20 | **KEEP** (test infrastructure) |
| Legacy/deprecated | 30 | **DELETE** |
| Experimental | 15 | **DELETE** or promote to wiring.yaml |
| Adapter wrappers | 23 | Convert to adapter pattern |

**TDD Pattern**: Reverse TDD (assert no imports → delete → clean up)

---

## 🧪 Multi-Cycle TDD Pattern (ENH-088)

### **Cycle 1: Behavioral Parity**
```
RED:    Test 16 core capabilities (from wiring.yaml)
        Harness existing functions
        Result: 16/16 FAIL (expected - not consolidated yet)

GREEN:  Minimal consolidation
        Preserve behavior via adapters
        Result: 16/16 PASS (behavioral parity achieved)
        Coverage: 78%

REFACTOR: Extract strategies
          Apply EventBus decoupling
          Result: 16/16 PASS + 4 integration tests
          Coverage: 89%

GATE:   Coverage ≥ 85%? → YES (proceed to Cycle 2)
```

### **Cycle 2: Performance + Extensibility**
```
RED:    Add 4 new tests (concurrency, latency, extensibility)
        Result: 4/4 FAIL (performance gaps exist)

GREEN:  EventBus async execution
        Stage registry pattern
        Result: ALL tests PASS
        Coverage: 92%, Latency: 145ms avg

REFACTOR: Optimize hot paths
          Extract more strategies
          Result: ALL tests PASS, coverage 92%

GATE:   All criteria met? → YES (SUCCESS - exit loop)
```

**Success Criteria**:
- ✅ Coverage ≥ 85%
- ✅ Latency < 200ms
- ✅ Extensibility (plugin pattern works)

---

## 🐛 Zero-Friction Debugging (ENH-089)

### **Current Workflow** (5-10 minutes)
1. Run tests → test fails
2. Manually run: `cortex_debug inject`
3. Specify file path, line range
4. Open file, locate markers
5. Debug issue
6. Manually run: `cortex_debug cleanup`

### **New Workflow** (<1 minute)
1. Run tests → test fails
2. **Markers auto-injected** (500ms)
3. Open file → **markers already present with context**
4. Debug issue
5. Fix → tests pass → **markers auto-removed**

### **EventBus Integration**
```yaml
TDDOrchestrator:
  publishes: TEST_FAILURE
  payload:
    - test_name: str
    - file_path: str
    - line_number: int
    - failure_reason: str

DebuggerOrchestrator:
  subscribes_to: TEST_FAILURE
  action: |
    1. Parse traceback → identify user code
    2. Inject CORTEX_DEBUG markers
    3. Capture local variables
    4. Emit DEBUG_MARKERS_INJECTED

Developer:
  experience: |
    Opens file → sees:
    # CORTEX_DEBUG_START: session-20260211-143052
    # Trigger: TEST_FAILURE (test_master_orchestrator_stage_2)
    # Issue: stage2_result is None (expected IntentVerificationResult)
    # Context: operation_name='implement', stage1_result=<ComprehensionResult>
    # CORTEX_DEBUG_END
```

**ROI**: 260 hours/year saved × $100/hour = **$26,000 annual value**

---

## 🎯 Success Criteria (Measurable)

| Metric | Target | Validation |
|--------|--------|------------|
| **Orchestrator Count** | 26 → 15 | wiring.yaml audit |
| **Behavioral Parity** | 100% capability coverage | Contract test suite |
| **Quality** | 85%+ coverage per orchestrator | pytest --cov |
| **Performance** | <200ms avg latency | Prometheus metrics |
| **Extensibility** | <2 hours to add capability | Plugin pattern test |
| **Plan Execution** | 95%+ success rate | End-to-end tests (20 plans) |
| **Auto-Debugging** | 100% marker injection | EventBus audit log |

---

## 📋 Test Priorities (High-Value Only)

### **P0-CRITICAL** (5/5 value)
1. `test_behavioral_contract_refactoring_detects_smells` - Ensures consolidation doesn't break functionality
2. `test_debugger_auto_injects_on_test_failure` - Validates zero-friction debugging
3. `test_tdd_multi_cycle_iterates_until_coverage_85` - Proves multi-cycle works
4. `test_master_executes_phase_81_plan_end_to_end` - Ultimate integration test

### **P1-HIGH** (4/5 value)
5. `test_operation_latency_under_200ms` - Production readiness SLA
6. `test_refactor_rolls_back_on_regression` - Safety net
7. `test_eventbus_decouples_12_dependencies` - Architectural validation

**Total High-Value Tests**: 162 (85 capability + 32 integration + 45 utility)

---

## 📊 Expected Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Registered Orchestrators** | 26 | 15 | **42% reduction** |
| **Physical Files** | 114 | 25 | **78% reduction** |
| **Total Classes** | 201+ | 45 | **78% reduction** |
| **Lines of Code** | 45,000 | 12,000 | **73% reduction** |
| **Maintenance Burden** | HIGH | LOW | **85% less complexity** |
| **Onboarding Time** | 8 hours | 2 hours | **75% faster** |
| **Debug Time/Session** | 5-10 min | <1 min | **90% faster** |

---

## ⏱️ Timeline

### **Week 1-2: Cycle 1 (All Tracks)**
- Red Phase: Behavioral contract tests (4 parallel test suites)
- Green Phase: Minimal consolidation (behavioral parity)
- Refactor Phase: Holistic analysis + Strategy Pattern
- **Duration**: 8-10 days

### **Week 2-3: Cycle 2 (Tracks 1-2)**
- Performance + extensibility tests
- Debugger integration (Track 2)
- Master plan execution (Track 1)
- **Duration**: 4-6 days

### **Week 3: Cleanup & Integration**
- Merge 4 tracks into main
- Update wiring.yaml (15 orchestrators)
- Dashboard sync
- **Duration**: 2-3 days

**Total**: 10-18 days (parallelizable)

---

## 🏛️ Architectural Patterns

| Pattern | Purpose | Benefit |
|---------|---------|---------|
| **Strategy Pattern** | Replace 88+ orchestrators with pluggable strategies | Add capabilities without core changes |
| **Event-Driven** | Decouple orchestrators via OrchestratorEventBus | 15 dependencies eliminated |
| **Mixin Composition** | Replace inheritance hierarchies | Multiple capabilities, single inheritance |
| **Behavior-Driven Consolidation** | Test capabilities, not methods | 95% less test creation time |

---

## 🚨 Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Breaking changes | HIGH | Adapter pattern + feature flags + incremental rollout |
| Test coverage loss | MEDIUM | Behavioral contracts before consolidation + 85%+ requirement |
| Performance regression | LOW | EventBus tested at 1000+ req/sec + <200ms SLA |
| Integration issues | MEDIUM | MCP adapter layer isolates changes |

---

## 🎯 Authority & Compliance

**Authority**:
- Phase 81 (Agent Architecture Redesign - Strategy Pattern spec)
- CORE-035 (Single Canonical Implementation)
- CORE-041 (Event-Driven Architecture)
- WAVE-7 Enhanced Vision (chat01.md)

**Governance**:
- CORE-008: TDD (multi-cycle pattern)
- CORE-011: Type hints (all new methods)
- CORE-012: Google-style docstrings
- CORE-027: Audit trail (AC markers)

---

## 🚀 Next Steps

1. **Immediate**: Create 4 GitHub branches (track-1-core, track-2-domain, track-3-support, track-4-cleanup)
2. **Week 1**: Kickoff Cycle 1 (all tracks in parallel)
3. **Week 2**: Cycle 2 (tracks 1-2) + debugger integration
4. **Week 3**: Merge + wiring.yaml update + production deployment

**Ready to execute? This is the highest-ROI architecture transformation available (9.2/10).**
