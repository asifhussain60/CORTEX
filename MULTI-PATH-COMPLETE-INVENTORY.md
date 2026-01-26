# 📊 CORTEX Multi-Path Architecture Problems - Complete Inventory

**Generated:** 2026-01-26 | **Authority:** CORE-035 Analysis | **Format:** Tabular Inventory

---

## Summary Statistics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Multi-Path Issues** | 40+ | Identified |
| **Duplicate Enum Classes** | 154 | 🔴 Critical |
| **Duplicate Functions** | 101 | 🟡 High |
| **Duplicate Orchestrators** | 6+ | 🔴 Critical |
| **Complete Code Duplication** | 2 modules | 🟡 High |
| **CORE-035 Violations** | 285+ | ❌ Non-compliant |

---

## TABLE 1: Duplicate Orchestrator Execution Paths (CRITICAL)

| # | Orchestrator | Path A | Path B | Path C | Status | Fix Time | Risk |
|---|---|---|---|---|---|---|---|
| 1 | **Master** ✅ | execute_operation() | coordinate_operation() | — | FIXED | Complete | ✅ LOW |
| 2 | **Handler Coordination** | HandlerCoordinator | OrchestrationCoordinator | — | Active/Active | 2h | 🟡 LOW |
| 3 | **Documentation** | execute() | execute_operation() | execute_on_domain() | Active/Active | 3h | 🔴 MED |
| 4 | **Refactoring** | Base orchestrator | Enhanced orchestrator | — | Active/Active | 2h | 🟡 LOW |
| 5 | **Planning** | Base orchestrator | Enhanced orchestrator | — | Active/Active | 2h | 🟡 LOW |
| 6 | **Documentation** | documentation/orchestrator.py | domain/enhanced_doc_orchestrator.py | — | Active/Active | 2h | 🟡 LOW |
| 7 | **Intent Router** | Route method A | Route method B | Detect method | Active/Active | 2h | 🟡 MED |

**Total:** 7 instances | **Combined Fix Time:** 15 hours | **Pattern:** Parallel active execution paths

---

## TABLE 2: Duplicate Enum Classes (154 Total)

### Top 20 by Instance Count

| # | Enum Class | Instances | Defined In | Severity | Fix Strategy |
|---|---|---|---|---|---|
| 1 | ComplexityLevel | 8 | core/, orch/, brain/ | 🔴 Critical | → common_enums.py |
| 2 | SeverityLevel | 5 | core/, orch/, brain/ | 🟡 High | → common_enums.py |
| 3 | ToolCategory | 5 | mcp/, orch/, brain/ | 🟡 High | → common_enums.py |
| 4 | ValidationSeverity | 5 | core/, domain/, brain/ | 🟡 High | → common_enums.py |
| 5 | AlertSeverity | 4 | brain/core/, infra/ | 🟡 High | → common_enums.py |
| 6 | ViolationType | 4 | orch/, brain/, testing/ | 🟡 High | → common_enums.py |
| 7 | CircuitBreakerState | 3 | orch/, brain/ | 🟡 High | → common_enums.py |
| 8 | ChallengeType | 3 | core/, orch/, domain/ | 🟡 High | → common_enums.py |
| 9 | ChallengeCategory | 3 | core/, orch/, brain/ | 🟡 High | → common_enums.py |
| 10 | ChangeType | 3 | core/, devx/, brain/ | 🟡 High | → common_enums.py |
| 11 | AlertPriority | 2 | brain/core/, infra/ | 🟡 High | → common_enums.py |
| 12 | AlertState | 2 | brain/tier2/, infra/ | 🟡 High | → common_enums.py |
| 13 | ApprovalStatus | 3 | orch/core/, dor/, brain/ | 🟡 High | → common_enums.py |
| 14 | AuditEventType | 4 | confirm/, orch/, brain/ | 🟡 High | → common_enums.py |
| 15 | BrainTier | 2 | orch/core/, brain/core/ | 🟡 High | → common_enums.py |
| 16 | CheckpointStatus | 2 | core/, brain/core/ | 🟡 High | → common_enums.py |
| 17 | CoherenceType | 2 | brain/tier2/, cortex_brain/ | 🟡 High | → common_enums.py |
| 18 | CommandType | 2 | govern_tools/, cli/ | 🟡 High | → common_enums.py |
| 19 | ComponentType | 3 | orch/core/, testing/, infra/ | 🟡 High | → common_enums.py |
| 20 | TransitionType | 2 | core/, brain/core/ | 🟡 High | → common_enums.py |

**Remaining:** 134 enums with 2-3 instances each  
**Total Fix:** Consolidate all to **cortex_brain/tier3/common_enums.py**

---

## TABLE 3: Duplicate Functions (101 Total)

### By Category

#### A. Decorator Functions (3-3 instances each)

| Function | Instance 1 | Instance 2 | Instance 3 | Status | Fix |
|---|---|---|---|---|---|
| `orchestrator()` | core/decorators/ | brain/core/decorators/ | brain/core/ | 🟡 Duplicate | Canonical: core/decorators/ |
| `mcp_tool()` | mcp/decorator.py | mcp/decorators.py | brain/mcp/ | 🟡 Duplicate | Canonical: mcp/decorator.py |
| `get_registered_tools()` | mcp/decorator.py | mcp/decorators.py | brain/mcp/ | 🟡 Duplicate | Unified registry |

#### B. Validator Functions (2-2 instances each)

| Function | Instance A | Instance B | Impact | Fix |
|---|---|---|---|---|
| `validate_llm_output()` | core/hallucination_prevention/ | core/safety/ | Inconsistent validation | Canonical: safety/ |
| `validate_schema()` | mcp/domain_operations.py | common/validators.py | Schema conflicts | Canonical: common/ |
| `validate_ac_id()` | brain/core/response_header_injector.py | brain/mcp/tools/governance_tools.py | AC-ID inconsistency | Canonical: governance/ |

#### C. Registry/Discovery Functions (2-3 instances each)

| Function | Instances | Paths | Impact | Fix |
|---|---|---|---|---|
| `get_registered_orchestrators()` | 2 | core/decorators/, brain/core/ | Registry state divergence | Canonical registry |
| `clear_orchestrator_registry()` | 2 | core/decorators/, brain/core/ | Cleanup inconsistency | Unified clearer |
| `get_orchestrator_by_domain()` | 2 | core/decorators/, brain/core/ | Domain lookup conflicts | Canonical lookup |
| `get_platform()` | 3 | scripts-root-archive/, brain/dashboard/ | Platform detection errors | Canonical detector |

#### D. MCP Tools Functions (2-3 instances each)

| Function | Instances | Paths | Impact | Fix |
|---|---|---|---|---|
| `search_knowledge_base()` | 2 | mcp/tools/knowledge/, brain/mcp/ | Knowledge search conflicts | Canonical search |
| `analyze_knowledge_gap()` | 2 | mcp/tools/knowledge/, brain/mcp/ | Gap analysis divergence | Canonical analyzer |
| `generate_knowledge_summary()` | 2 | mcp/tools/knowledge/, brain/mcp/ | Summary conflicts | Canonical generator |
| `get_operation_status()` | 2 | mcp/tools/orch/, brain/mcp/ | Status reporting errors | Canonical status |
| `monitor_orchestrator_health()` | 2 | mcp/tools/orch/, brain/mcp/ | Health check divergence | Canonical monitor |
| `diagnose_orchestrator_issues()` | 2 | mcp/tools/orch/, brain/mcp/ | Diagnostics conflicts | Canonical diagnostics |
| `optimize_orchestrator_config()` | 2 | mcp/tools/orch/, brain/mcp/ | Config optimization conflicts | Canonical optimizer |

#### E. Dashboard Extensibility Functions (20+ identical pairs)

| Function | Set A | Set B | Status | Fix |
|---|---|---|---|---|
| `get_business_context()` | observability/ | brain/observability/ | 🟡 100% dup | Delete Set B |
| `get_cache_status()` | observability/ | brain/observability/ | 🟡 100% dup | Delete Set B |
| `is_domain_available()` | observability/ | brain/observability/ | 🟡 100% dup | Delete Set B |
| `enrich_dashboard_context()` | observability/ | brain/observability/ | 🟡 100% dup | Delete Set B |
| `enrich_batch_context()` | observability/ | brain/observability/ | 🟡 100% dup | Delete Set B |
| `invalidate_cache()` | observability/ | brain/observability/ | 🟡 100% dup | Delete Set B |
| `check_domain_health()` | observability/ | brain/observability/ | 🟡 100% dup | Delete Set B |
| `⋮ 13 more identical functions` | observability/ | brain/observability/ | 🟡 100% dup | Delete Set B |

#### F. Utility Functions (multiple instances)

| Function | Instances | Paths | Fix |
|---|---|---|---|
| `main()` | 76 | Various scripts/ | Consolidate entry points |
| `get_thread_join_timeout()` | 2 | core/config/, infra/ | Canonical timeout config |
| `get_project_root()` | 2 | core/, brain/core/ | Canonical path resolver |
| `resolve_path()` | 2 | core/, brain/core/ | Canonical path resolver |
| `log_ac_audit_trail()` | 2 | scripts-root-archive/ | Audit consolidation |
| `log_ac_lifecycle()` | 2 | brain/intent_router/ | Lifecycle consolidation |
| `pytest_configure()` | 2 | testing/, devx/ | Test configuration |

**Total Functions:** 101 | **Fix Strategy:** Consolidate to canonical locations + update all imports

---

## TABLE 4: Duplicate Handler/Validator Classes

| # | Class | Instance A | Instance B | Conflict Type | Priority | Fix |
|---|---|---|---|---|---|---|
| 1 | HandlerCoordinator | handlers/handler_implementations.py | orchestrators/coordinator.py | Sequential vs concurrent | 🔴 HIGH | Unify via composition |
| 2 | AnalysisHandler | domain_orchestrators/ | brain/domain_orchestrators/ | Duplicate logic | 🟡 MED | Single base handler |
| 3 | CreateHandler | domain_orchestrators/ | brain/domain_orchestrators/ | Duplicate logic | 🟡 MED | Single base handler |
| 4 | DocumentationOrch | documentation/orchestrator.py | domain/enhanced_doc_orchestrator.py | Parallel docs ops | 🔴 HIGH | Consolidate paths |
| 5 | RefactoringOrch | domain/refactoring_orchestrator.py | domain/enhanced_refactoring_orchestrator.py | Base vs enhanced | 🟡 MED | Merge enhanced into base |
| 6 | PlanningOrch | domain/planning_orchestrator.py | domain/enhanced_planning_orchestrator.py | Base vs enhanced | 🟡 MED | Merge enhanced into base |

---

## TABLE 5: 100% Code Duplication (Dashboard Extensibility)

| Module | Path | Status | Functions | Lines | Fix |
|---|---|---|---|---|---|
| Dashboard Set A | cortex/observability/dashboard_extensibility.py | ACTIVE | 20+ | ~600 | KEEP |
| Dashboard Set B | cortex/brain/observability/dashboard_extensibility.py | ACTIVE | 20+ | ~600 | 🗑️ DELETE |
| **Duplication Level** | — | **100% IDENTICAL** | **20 identical functions** | **0% diff** | **30 min to fix** |

---

## TABLE 6: Decorator Function Duplicates

| Decorator | Path 1 | Path 2 | Path 3 | Status | Fix |
|---|---|---|---|---|---|
| `@orchestrator` | cortex/core/decorators/orchestrator_decorator.py | cortex/brain/core/decorators/orchestrator_decorator.py | cortex/brain/core/decorators/orchestrator.py | 3-way | Canonical: core/decorators/ |
| `@mcp_tool` | cortex/mcp/decorator.py | cortex/mcp/decorators.py | cortex/brain/mcp/decorator.py | 3-way | Canonical: mcp/decorator.py |

**Impact:** Registry registration conflicts, inconsistent decorator behavior  
**Fix:** Consolidate to one location, delete others, update all imports

---

## TABLE 7: MCP Tools Registry Duplication

| Tool Category | Path A | Path B | Path C | Path D | Path E | Fix |
|---|---|---|---|---|---|---|
| ToolCategory enum | mcp/registry.py | mcp/tool_governance.py | mcp/unified_tool_discovery.py | orchestrators/mcp_tools_registry.py | orch/core/tool_discovery_enhanced.py | Canonical: tier3/common_enums.py |
| Tool registration | mcp/decorator.py | mcp/decorators.py | brain/mcp/decorator.py | — | — | Unified registry |

---

## TABLE 8: Priority Consolidation Queue

| Priority | Issue | Effort | Risk | Impact | Status |
|---|---|---|---|---|---|
| **P0** | Dashboard deletion (brain/observability/) | 30m | 🟡 LOW | 🟢 HIGH | Ready |
| **P1** | Create canonical enum module | 1h | 🟢 LOW | 🟢 HIGH | Ready |
| **P2** | Handler coordination unification | 2h | 🟡 LOW | 🟡 MED | Ready |
| **P3** | Documentation orchestrator consolidation | 3h | 🔴 MED | 🟡 MED | Ready |
| **P4** | Refactoring orchestrator merge | 2h | 🟡 LOW | 🟢 LOW | Ready |
| **P5** | Planning orchestrator merge | 2h | 🟡 LOW | 🟢 LOW | Ready |
| **P6** | Decorator consolidation | 2h | 🔴 MED | 🟡 MED | Ready |
| **P7** | MCP registry unification | 2h | 🔴 MED | 🟡 MED | Ready |
| **P8** | Global import migration | 1d | 🔴 HIGH | 🟢 HIGH | Ready |
| **P9** | Full regression testing | 1d | 🟢 LOW | 🟢 HIGH | Ready |

**Total Time:** 18-20 hours | **Parallel Possible:** Yes | **Deployment Blocker:** Yes

---

## TABLE 9: Implementation Checklist

### Phase 1: Foundation (Day 1)
- [ ] Create cortex_brain/tier3/common_enums.py (all 154 enums)
- [ ] Delete cortex/brain/observability/dashboard_extensibility.py
- [ ] Update imports for deleted file (grep + sed)
- [ ] Run test suite verification
- [ ] Commit Phase 1

### Phase 2: Handlers & Coordinators (Day 2)
- [ ] Create UnifiedHandlerCoordinator
- [ ] Test sequential path
- [ ] Test concurrent path
- [ ] Update entry points
- [ ] Run integration tests
- [ ] Commit Phase 2

### Phase 3: Orchestrators (Day 2-3)
- [ ] Consolidate DocumentationOrchestrator (3 paths → 1)
- [ ] Consolidate RefactoringOrchestrator (enhanced → base)
- [ ] Consolidate PlanningOrchestrator (enhanced → base)
- [ ] Run full test suite
- [ ] Commit Phase 3

### Phase 4: Global Migration (Day 4-5)
- [ ] Codemod enum imports (154 classes)
- [ ] Delete all duplicate enum definitions
- [ ] Consolidate decorator functions
- [ ] Consolidate MCP tool registries
- [ ] Run full test suite
- [ ] Commit Phase 4

### Phase 5: Validation (Day 5)
- [ ] Run duplication_audit.py (verify 0 violations)
- [ ] Full 6,847+ test suite passing
- [ ] Performance benchmarking
- [ ] Documentation update
- [ ] Final commit
- [ ] Deployment ready

---

## TABLE 10: Compliance Gate

| Criteria | Before | After | Status |
|---|---|---|---|
| Duplicate classes | 154 | 0 | 🎯 Goal |
| Duplicate functions | 101 | 0 | 🎯 Goal |
| Multi-path orchestrators | 6+ | 0 | 🎯 Goal |
| CORE-035 violations | 285+ | 0 | 🎯 Goal |
| Test pass rate | 100% | 100% | ✅ Maintain |
| Deployment status | BLOCKED | UNBLOCKED | 🎯 Goal |

---

## Summary

**Total Multi-Path Issues:** 40+ across 6 pattern categories  
**Total Code Duplication:** 255+ class and function duplicates  
**Total CORE-035 Violations:** 285+  
**Fix Complexity:** LOW (composition pattern, backward compatible)  
**Estimated Fix Time:** 18-20 hours  
**Risk Level:** LOW  
**Status:** ✅ **READY FOR IMPLEMENTATION**

---

See full analysis in:
- **ARCHITECTURE-MULTI-PATH-ANALYSIS.md** (comprehensive details)
- **QUICK-REFERENCE-MULTI-PATH.md** (1-page summary)
