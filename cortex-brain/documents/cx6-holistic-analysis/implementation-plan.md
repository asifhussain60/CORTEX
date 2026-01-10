# CORTEX 6.0 Implementation Plan

**Version:** 6.0.0 | **Status:** READY FOR EXECUTION  
**Author:** Asif Hussain | **Created:** 2026-01-10  
**Target Completion:** 2026-02-28 (7 weeks)  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## Executive Summary

This plan executes CORTEX 6.0 rebuild using **snowball implementation strategy** with **4 phases**, **57 AC-IDs**, and **37.5% efficiency gain** through progressive complexity. Each orchestrator registers with `CORTEX.prompt.md` routing table upon completion, enabling **live wiring** and immediate production use.

**Key Metrics:**
- **Total AC-IDs:** 57 (14 Phase 1, 34 Phase 2, 23 Phase 3, 8 Phase 4)
- **Implementation Weeks:** 7 (target: 2026-01-10 to 2026-02-28)
- **Critical Path:** Audit → Governance → State → MasterOrch → TDD-Master
- **Snowball Acceleration:** 37.5% efficiency gain (Phase 1: 100% baseline → Phase 4: 62.5% complexity)

---

## 1. Snowball Implementation Philosophy

### 1.1 Core Principle

**"Build infrastructure first; features compound on infrastructure."**

```
Phase 1 (Foundation) → Lays groundwork for all others
         ↓
Phase 2 (Core) → Reuses Phase 1 (audit, governance, state)
         ↓
Phase 3 (Features) → Reuses Phase 1 + Phase 2 (orchestrator patterns)
         ↓
Phase 4 (Intelligence) → Reuses Phase 1-3 (everything)
```

### 1.2 Acceleration Metrics

| Phase | AC-IDs | Complexity | Efficiency Gain | Rationale |
|-------|--------|------------|-----------------|-----------|
| **Phase 1** | 14 | 100% baseline | 0% (groundwork) | Build from scratch: audit, governance, state |
| **Phase 2** | 34 | 80% baseline | 20% gain | Reuse Phase 1: logging, rules, persistence ready |
| **Phase 3** | 23 | 70% baseline | 30% gain | Reuse orchestrator patterns, TDD infrastructure |
| **Phase 4** | 8 | 62.5% baseline | 37.5% gain | Plug-and-play intelligence on proven foundation |

**Cumulative Effect:** Each phase builds faster than the last, with infrastructure reuse compounding velocity.

### 1.3 Live Wiring Protocol

**Every orchestrator completion triggers:**
1. ✅ AC validation (test coverage ≥80%, quality ≥80)
2. ✅ Update `CORTEX.prompt.md` routing table
3. ✅ Register patterns with MasterOrchestrator
4. ✅ Add knowledge files (if tier 2/tier 3 updates needed)
5. ✅ Audit trail complete
6. ✅ **Orchestrator immediately available for production use**

**Example:**
```yaml
# After AC-PLAN-001 to AC-PLAN-008 complete:
1. Tests pass: coverage 85%, quality 87
2. Update CORTEX.prompt.md:
   | `plan`, `create a plan` | Planning v5 | 10 | autonomous | AC-PLAN-* |
3. Register: @register_with_master(patterns=["plan"], priority=10)
4. Knowledge: No updates needed (uses existing tier2/tier3)
5. Audit: All AC-PLAN-* validated
6. Result: "plan" requests now route to Planning v5
```

---

## 2. Phase Breakdown

### Phase 1: Foundation (Week 1-2, 14 AC-IDs)

**Critical Path:** These MUST complete before ANY feature work.

#### 2.1.1 Audit Infrastructure (AC-AUDIT-001 to AC-AUDIT-006)

**Why First:** Every orchestrator logs to audit. No audit = blind execution.

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-AUDIT-001 | SQLite schema + indexes | `enhanced_audit_logger.py` | `test_audit_schema.py` | Schema created, WAL enabled |
| AC-AUDIT-002 | Buffered async logging | `enhanced_audit_logger.py` | `test_async_logging.py` | 100ms flush, buffer overflow handling |
| AC-AUDIT-003 | Category-based logging | `enhanced_audit_logger.py` | `test_categories.py` | 7 categories (GOVERNANCE, ORCHESTRATOR, etc.) |
| AC-AUDIT-004 | Context propagation | `enhanced_audit_logger.py` | `test_correlation_ids.py` | Correlation ID propagated across calls |
| AC-AUDIT-005 | Retention policy | `audit_log_manager.py` | `test_retention.py` | CRITICAL=90d, ERROR=90d, WARNING=60d, INFO=30d, DEBUG=7d |
| AC-AUDIT-006 | Query interface | `audit_log_manager.py` | `test_query.py` | Query by: correlation_id, ac_id, category, level, time range |

**Live Wiring:** None (infrastructure, not routable)

**Dependencies:** None (Phase 1 starts here)

**Deliverables:**
```
src/infrastructure/enhanced_audit_logger.py
scripts/audit_log_manager.py
cortex-brain/tier0/database/audit_logs.db (SQLite)
tests/infrastructure/test_audit_*.py (≥80% coverage)
```

---

#### 2.1.2 Governance Merger (AC-GOV-001 to AC-GOV-005)

**Why Second:** All orchestrators enforce governance. No merger = no rule enforcement.

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-GOV-001 | Load tier 0-3 rules | `governance_merger.py` | `test_load_rules.py` | Loads 22 SKULL rules + tier1/2/3 |
| AC-GOV-002 | Precedence algorithm | `governance_merger.py` | `test_precedence.py` | Tier 0 > Tier 1 > Tier 2 > Tier 3 |
| AC-GOV-003 | Conflict resolution | `governance_merger.py` | `test_conflicts.py` | Tier 0 always wins conflicts |
| AC-GOV-004 | Final Instruction (F) | `governance_merger.py` | `test_final_instruction.py` | Merged ruleset returned |
| AC-GOV-005 | Cache invalidation | `governance_merger.py` | `test_cache.py` | Cache refreshes on file changes |

**Live Wiring:** None (infrastructure, used by MasterOrchestrator)

**Dependencies:** AC-AUDIT-* (logs governance decisions)

**Deliverables:**
```
src/orchestrators/core/governance_merger.py
tests/orchestrators/core/test_governance_merger.py
cortex-brain/tier0/governance/core-rules.yaml (SKULL rules)
cortex-brain/tier1/company-practices.yaml (business rules)
cortex-brain/tier2/engineering-standards.yaml (practices)
cortex-brain/tier3/domain-patterns.yaml (learned)
```

---

#### 2.1.3 State Manager (AC-STATE-001 to AC-STATE-003)

**Why Third:** All orchestrators persist state. No state = lost progress on failure.

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-STATE-001 | SQLite state storage | `state_manager.py` | `test_state_storage.py` | Schema with phases, tasks, orchestrators |
| AC-STATE-002 | Atomic transactions | `state_manager.py` | `test_transactions.py` | ACID guarantees, WAL mode |
| AC-STATE-003 | JSON export | `state_manager.py` | `test_json_export.py` | Exports progress-tracker.json (read-only snapshot) |

**Live Wiring:** None (infrastructure, used by all orchestrators)

**Dependencies:** AC-AUDIT-* (logs state changes)

**Deliverables:**
```
src/infrastructure/state_manager.py
tests/infrastructure/test_state_manager.py
cortex-brain/tier0/database/state.db (SQLite)
cortex-brain/tier1/tracking/progress-tracker.json (snapshot)
```

---

**Phase 1 Completion Criteria:**
- ✅ All 14 AC-IDs validated (tests ≥80% coverage, quality ≥80)
- ✅ Audit, governance, state infrastructure functional
- ✅ No orchestrator routing yet (infrastructure only)
- ✅ Foundation ready for Phase 2

**Phase 1 Duration:** 2 weeks (2026-01-10 to 2026-01-24)

---

### Phase 2: Orchestration Core (Week 3-4, 34 AC-IDs)

**Critical Path:** Establishes THE DEFAULT WORKING MECHANISM (MasterOrchestrator central control).

#### 2.2.1 MasterOrchestrator (AC-ORCH-001 to AC-ORCH-008)

**Why First:** Central controller for all requests. No MasterOrch = no routing.

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-ORCH-001 | Intake & context load | `master_orchestrator.py` | `test_intake.py` | Loads progress-tracker, AC-INDEX, core-rules |
| AC-ORCH-002 | Intent classification | `master_orchestrator.py` | `test_classify.py` | Matches patterns from routing table |
| AC-ORCH-003 | Orchestrator registry | `registry.py` | `test_registry.py` | Stores orchestrators with patterns, priority |
| AC-ORCH-004 | Registration decorator | `decorators.py` | `test_decorator.py` | @register_with_master(patterns, priority, ac_prefix) |
| AC-ORCH-005 | Routing logic | `master_orchestrator.py` | `test_routing.py` | Routes to highest-priority matching orchestrator |
| AC-ORCH-006 | Evaluation (request → actions) | `master_orchestrator.py` | `test_evaluation.py` | Uses GovernanceMerger, produces RequiredActions |
| AC-ORCH-007 | RequiredAction → Task mapping | `master_orchestrator.py` | `test_action_mapping.py` | 1:1 mapping with TodoManager |
| AC-ORCH-008 | Execution & delegation | `master_orchestrator.py` | `test_execution.py` | Delegates to TodoManager, awaits completion |

**Live Wiring:**
```yaml
# CORTEX.prompt.md (no user-facing patterns yet - infrastructure)
# MasterOrchestrator called internally by src/main.py
```

**Dependencies:**
- AC-AUDIT-* (logs intake, routing, execution)
- AC-GOV-* (evaluates against merged rules)
- AC-STATE-* (persists orchestrator state)

**Deliverables:**
```
src/orchestrators/core/master_orchestrator.py
src/orchestrators/core/registry.py
src/orchestrators/core/decorators.py
tests/orchestrators/core/test_master_orchestrator.py
```

---

#### 2.2.2 TodoManager (AC-TODO-001 to AC-TODO-004)

**Why Second:** Executes tasks from MasterOrchestrator. No TodoManager = no automation.

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-TODO-001 | Task schema & storage | `todo_manager.py` | `test_task_schema.py` | 10 fields (id, name, status, priority, dependencies, etc.) |
| AC-TODO-002 | Dependency resolution | `todo_manager.py` | `test_dependencies.py` | Topological sort, circular detection |
| AC-TODO-003 | Execution engine | `todo_manager.py` | `test_execution.py` | Runs tasks in dependency order |
| AC-TODO-004 | Progress persistence | `todo_manager.py` | `test_persistence.py` | Saves to SQLite, exports progress-tracker.json |

**Live Wiring:** None (called by MasterOrchestrator, not directly routable)

**Dependencies:**
- AC-STATE-* (persists tasks)
- AC-AUDIT-* (logs task lifecycle)

**Deliverables:**
```
src/orchestrators/core/todo_manager.py
tests/orchestrators/core/test_todo_manager.py
cortex-brain/tier1/tracking/progress-tracker.json (updated with tasks)
```

---

#### 2.2.3 TDD-Master v1 (AC-TDD-001 to AC-TDD-010)

**Why Third:** Quality gateway for ALL development. No TDD-Master = untested code.

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-TDD-001 | Requirement extraction | `tdd_master.py` | `test_extraction.py` | Parses AC criteria into test specs |
| AC-TDD-002 | Test generation (unit/integration) | `tdd_master.py` | `test_generation.py` | Generates pytest files |
| AC-TDD-003 | Security test generation | `tdd_master.py` | `test_security_gen.py` | AST detects user input → security tests |
| AC-TDD-004 | RED phase execution | `tdd_master.py` | `test_red_phase.py` | Runs tests, expects failures |
| AC-TDD-005 | Clean Code Score | `code_quality_checker.py` | `test_clean_code.py` | Radon + Pylint + Pydocstyle + Mypy (≥80) |
| AC-TDD-006 | Validation report | `validation_reporter.py` | `test_validation.py` | Markdown report with coverage, quality, security |
| AC-TDD-007 | AC validation | `ac_validator.py` | `test_ac_validation.py` | Verifies all AC criteria met |
| AC-TDD-008 | Documentation generation | `doc_generator.py` | `test_doc_gen.py` | Auto-generates usage docs |
| AC-TDD-009 | Audit trail integration | `tdd_master.py` | `test_audit.py` | Logs validation with correlation IDs |
| AC-TDD-010 | User confirmation flow | `tdd_master.py` | `test_confirmation.py` | Asks "Proceed?" before final commit |

**Live Wiring:**
```yaml
# CORTEX.prompt.md routing table update:
| `tdd`, `test driven` | TDD-Master v1 | 20 | autonomous | AC-TDD-* |
| `implement`, `build`, `create`, `fix` | TDD-Master v1 | 15 | autonomous | AC-TDD-* |
```

**Dependencies:**
- AC-AUDIT-* (logs TDD lifecycle)
- AC-GOV-* (enforces CORE-019)
- AC-STATE-* (persists TDD state)

**Deliverables:**
```
src/orchestrators/tdd/tdd_master.py
src/orchestrators/tdd/code_quality_checker.py
src/orchestrators/tdd/validation_reporter.py
src/orchestrators/tdd/ac_validator.py
tests/orchestrators/tdd/test_tdd_master.py
templates/validation-report.md.jinja2
```

---

#### 2.2.4 Planning v5 (AC-PLAN-001 to AC-PLAN-008)

**Why Fourth:** Generates implementation plans. Reuses TDD-Master for validation.

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-PLAN-001 | Context loading | `planning_orchestrator.py` | `test_context_load.py` | Loads progress-tracker, AC-INDEX, core-rules |
| AC-PLAN-002 | Requirement analysis | `planning_orchestrator.py` | `test_analysis.py` | Extracts features, constraints, dependencies |
| AC-PLAN-003 | Incremental planning | `planning_orchestrator.py` | `test_incremental.py` | <500 lines per increment |
| AC-PLAN-004 | Phase decomposition | `planning_orchestrator.py` | `test_phases.py` | Breaks work into phases with AC-IDs |
| AC-PLAN-005 | Risk assessment | `planning_orchestrator.py` | `test_risk.py` | Identifies risks with probability/impact |
| AC-PLAN-006 | DoD criteria generation | `planning_orchestrator.py` | `test_dod.py` | Creates completion checklists |
| AC-PLAN-007 | Markdown plan generation | `plan_generator.py` | `test_plan_gen.py` | Outputs to cortex-brain/documents/planning/ |
| AC-PLAN-008 | Validation via TDD-Master | `planning_orchestrator.py` | `test_validation.py` | Routes validation through AC-TDD-007 |

**Live Wiring:**
```yaml
# CORTEX.prompt.md routing table update:
| `plan`, `create a plan` | Planning v5 | 10 | autonomous | AC-PLAN-* |
```

**Dependencies:**
- AC-TDD-* (validates plans)
- AC-AUDIT-* (logs planning)
- AC-STATE-* (persists plans)

**Deliverables:**
```
src/orchestrators/planning/planning_orchestrator.py
src/orchestrators/planning/plan_generator.py
tests/orchestrators/planning/test_planning.py
cortex-brain/documents/planning/{project-name}-plan.md
```

---

#### 2.2.5 Knowledge Files (AC-KNOW-001 to AC-KNOW-003)

**Why Fifth:** Enables Final Instruction (F) generation for all orchestrators.

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-KNOW-001 | Engineering standards (Tier 2) | `engineering-standards.yaml` | `test_tier2_load.py` | Code style, testing, docs, security |
| AC-KNOW-002 | Domain patterns (Tier 3) | `domain-patterns.yaml` | `test_tier3_load.py` | Auth, DB, API, security patterns |
| AC-KNOW-003 | Company practices (Tier 1) | `company-practices.yaml` | `test_tier1_load.py` | Review, deployment, compliance |

**Live Wiring:** None (knowledge files loaded by GovernanceMerger)

**Dependencies:** AC-GOV-* (loads and merges knowledge)

**Deliverables:**
```
cortex-brain/tier1/company-practices.yaml
cortex-brain/tier2/engineering-standards.yaml
cortex-brain/tier3/domain-patterns.yaml
tests/governance/test_knowledge_files.py
```

---

**Phase 2 Completion Criteria:**
- ✅ All 34 AC-IDs validated (tests ≥80% coverage, quality ≥80)
- ✅ MasterOrchestrator + TodoManager + TDD-Master functional
- ✅ `CORTEX.prompt.md` routing table includes TDD-Master, Planning v5
- ✅ Knowledge files loaded by GovernanceMerger
- ✅ Core workflow operational (request → MasterOrch → TodoManager → execute)

**Phase 2 Duration:** 2 weeks (2026-01-25 to 2026-02-07)

**Efficiency Gain:** 20% (reuses Phase 1 audit, governance, state infrastructure)

---

### Phase 3: Feature Orchestrators (Week 5-6, 23 AC-IDs)

**Parallel Development Enabled:** MasterOrchestrator routes to multiple feature orchestrators.

#### 2.3.1 ADO v2 (AC-ADO-001 to AC-ADO-006)

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-ADO-001 | Azure DevOps API client | `ado_client.py` | `test_ado_client.py` | Authenticates, queries work items |
| AC-ADO-002 | Work item creation | `ado_orchestrator.py` | `test_create_workitem.py` | Creates user stories, bugs, tasks |
| AC-ADO-003 | Work item queries | `ado_orchestrator.py` | `test_query_workitems.py` | WIQL queries for sprint work |
| AC-ADO-004 | Git integration | `ado_orchestrator.py` | `test_git_integration.py` | Links commits to work items |
| AC-ADO-005 | Contract tests | `test_ado_contracts.py` | `test_contracts.py` | Detects API drift |
| AC-ADO-006 | Error handling | `ado_orchestrator.py` | `test_error_handling.py` | Timeout, retry, fallback |

**Live Wiring:**
```yaml
# CORTEX.prompt.md routing table update:
| `ado`, `azure devops` | ADO v2 | 30 | autonomous | AC-ADO-* |
```

**Dependencies:** AC-ORCH-* (registers with MasterOrchestrator)

---

#### 2.3.2 Investigation (AC-INV-001 to AC-INV-003)

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-INV-001 | Evidence collection | `investigation_orchestrator.py` | `test_evidence.py` | Gathers file paths, git history, errors |
| AC-INV-002 | Pattern analysis | `investigation_orchestrator.py` | `test_patterns.py` | Identifies common failure patterns |
| AC-INV-003 | Report generation | `investigation_orchestrator.py` | `test_report.py` | Markdown report with findings |

**Live Wiring:**
```yaml
# CORTEX.prompt.md routing table update:
| `investigate` | Investigation | 60 | autonomous | AC-INV-* |
```

**Dependencies:** AC-ORCH-* (registers with MasterOrchestrator)

---

#### 2.3.3 Crawler Orchestrator (AC-CRAWLER-001 to AC-CRAWLER-005)

**CRITICAL:** MUST complete BEFORE Vacuum (dependency graph requirement).

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-CRAWLER-001 | AST parsing (Python) | `ast_parser.py` | `test_ast_parsing.py` | Extracts imports, functions, classes |
| AC-CRAWLER-002 | Dependency mapping | `dependency_mapper.py` | `test_dependencies.py` | Builds import graph |
| AC-CRAWLER-003 | Knowledge graph build | `knowledge_graph_builder.py` | `test_graph_build.py` | Neo4j or SQLite graph schema |
| AC-CRAWLER-004 | File usage tracking | `file_usage_tracker.py` | `test_file_usage.py` | Identifies actively used files |
| AC-CRAWLER-005 | Orphan detection | `orphan_detector.py` | `test_orphan_detection.py` | Finds unused files |

**Live Wiring:**
```yaml
# CORTEX.prompt.md routing table update:
| `crawl`, `scan code`, `analyze codebase`, `knowledge graph` | Crawler Orchestrator | 35 | autonomous | AC-CRAWLER-* |
```

**Dependencies:**
- AC-ORCH-* (registers with MasterOrchestrator)
- BLOCKS: AC-VAC-* (Vacuum requires knowledge graph)

---

#### 2.3.4 Vacuum v2 (AC-VAC-001 to AC-VAC-006)

**CRITICAL:** MUST run AFTER Crawler (knowledge graph dependency).

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-VAC-001 | Pre-checks (graph exists, <7d old) | `vacuum_orchestrator.py` | `test_prechecks.py` | Aborts if unsafe |
| AC-VAC-002 | Safe deletion (.bak, .tmp) | `vacuum_orchestrator.py` | `test_safe_deletion.py` | Deletes without graph check |
| AC-VAC-003 | Medium risk deletion (duplicates) | `vacuum_orchestrator.py` | `test_medium_deletion.py` | Uses graph for verification |
| AC-VAC-004 | High risk deletion (orphans) | `vacuum_orchestrator.py` | `test_high_deletion.py` | Deep analysis + user confirmation |
| AC-VAC-005 | Dry-run mode | `vacuum_orchestrator.py` | `test_dry_run.py` | Shows what WOULD delete |
| AC-VAC-006 | Report generation | `vacuum_orchestrator.py` | `test_report.py` | Markdown report with results |

**Live Wiring:**
```yaml
# CORTEX.prompt.md routing table update:
| `vacuum`, `deep clean` | Vacuum v2 | 45 | autonomous | AC-VAC-* |
```

**Dependencies:**
- AC-CRAWLER-* (BLOCKS - requires knowledge graph)
- AC-ORCH-* (registers with MasterOrchestrator)

---

#### 2.3.5 Cleanup v2 (AC-CLEAN-001 to AC-CLEAN-004)

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-CLEAN-001 | Root-level file detection | `cleanup_orchestrator.py` | `test_root_detection.py` | Finds files violating CORE-009 |
| AC-CLEAN-002 | Categorization | `cleanup_orchestrator.py` | `test_categorization.py` | Plans, summaries, docs |
| AC-CLEAN-003 | Move to tier folders | `cleanup_orchestrator.py` | `test_move_files.py` | Moves to appropriate tier |
| AC-CLEAN-004 | Report generation | `cleanup_orchestrator.py` | `test_report.py` | Markdown report with moves |

**Live Wiring:**
```yaml
# CORTEX.prompt.md routing table update:
| `cleanup` | Cleanup v2 | 55 | autonomous | AC-CLEAN-* |
```

**Dependencies:** AC-ORCH-* (registers with MasterOrchestrator)

---

**Phase 3 Completion Criteria:**
- ✅ All 23 AC-IDs validated (tests ≥80% coverage, quality ≥80)
- ✅ ADO, Investigation, Crawler, Vacuum, Cleanup operational
- ✅ `CORTEX.prompt.md` routing table includes all 5 orchestrators
- ✅ Knowledge graph built (prerequisite for Vacuum)
- ✅ Orchestrator patterns established (reusable for Phase 4)

**Phase 3 Duration:** 2 weeks (2026-02-08 to 2026-02-21)

**Efficiency Gain:** 30% (reuses orchestrator patterns, TDD infrastructure)

---

### Phase 4: Intelligence Layer (Week 7, 8 AC-IDs)

**Optional Enhancement:** Enhances user experience, not critical path.

#### 2.4.1 LLM Intent Classifier (AC-LLM-001 to AC-LLM-004)

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-LLM-001 | Fuzzy pattern matching | `llm_intent_classifier.py` | `test_fuzzy_matching.py` | Handles typos, variations |
| AC-LLM-002 | Intent confidence scoring | `llm_intent_classifier.py` | `test_confidence.py` | 0-100 score per orchestrator |
| AC-LLM-003 | Fallback to MasterOrch | `llm_intent_classifier.py` | `test_fallback.py` | If confidence <70, ask MasterOrch |
| AC-LLM-004 | Learning from corrections | `llm_intent_classifier.py` | `test_learning.py` | Updates tier3/domain-patterns.yaml |

**Live Wiring:** None (called internally by MasterOrchestrator for ambiguous requests)

**Dependencies:** AC-ORCH-* (fallback mechanism)

---

#### 2.4.2 Vision API (AC-VIS-001 to AC-VIS-003)

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-VIS-001 | Image analysis | `vision_api.py` | `test_image_analysis.py` | Extracts text, diagrams, code |
| AC-VIS-002 | Timeout fallback | `vision_api.py` | `test_timeout.py` | 500ms timeout, graceful degradation |
| AC-VIS-003 | Integration with Planning | `vision_api.py` | `test_planning_integration.py` | Planning v5 can use visual inputs |

**Live Wiring:** None (enhancement to existing orchestrators)

**Dependencies:** AC-PLAN-* (Planning uses Vision for diagram analysis)

---

#### 2.4.3 Knowledge Practices (AC-KNOW-PRAC-001 to AC-KNOW-PRAC-005)

| AC-ID | Description | Files | Tests | DoD |
|-------|-------------|-------|-------|-----|
| AC-KNOW-PRAC-001 | Pattern extraction | `knowledge_practices.py` | `test_pattern_extraction.py` | Learns from successful AC validations |
| AC-KNOW-PRAC-002 | Tier 3 updates | `knowledge_practices.py` | `test_tier3_updates.py` | Auto-updates domain-patterns.yaml |
| AC-KNOW-PRAC-003 | Anti-pattern detection | `knowledge_practices.py` | `test_antipatterns.py` | Identifies repeated failures |
| AC-KNOW-PRAC-004 | Recommendation engine | `knowledge_practices.py` | `test_recommendations.py` | Suggests better patterns |
| AC-KNOW-PRAC-005 | Continuous learning | `knowledge_practices.py` | `test_continuous_learning.py` | Learns from every validation |

**Live Wiring:** None (background learning, updates knowledge files)

**Dependencies:** AC-TDD-* (learns from validation outcomes)

---

**Phase 4 Completion Criteria:**
- ✅ All 8 AC-IDs validated (tests ≥80% coverage, quality ≥80)
- ✅ LLM classifier, Vision API, Knowledge Practices operational
- ✅ User experience enhanced with fuzzy matching, visual input
- ✅ System learns continuously from validations

**Phase 4 Duration:** 1 week (2026-02-22 to 2026-02-28)

**Efficiency Gain:** 37.5% (plug-and-play intelligence on proven foundation)

---

## 3. Live Wiring: CORTEX.prompt.md Updates

### 3.1 Update Protocol

**When:** Immediately after AC-ID validation complete.

**How:**
1. Run validation: `python3 -m src.main "validate AC-{CATEGORY}-*"`
2. Verify tests pass (≥80% coverage, quality ≥80)
3. Update routing table in `.github/copilot-instructions.md` (Intent Routing Table section)
4. Commit with message: `feat(orchestrator): Register {Orchestrator} with patterns [{pattern1}, {pattern2}]`
5. Audit trail: Log registration with correlation ID

**Example Update:**
```markdown
# Before (Phase 2, no TDD-Master yet):
| Pattern | Orchestrator | Priority | Mode | AC-ID Prefix |
|---------|--------------|----------|------|--------------|
| `plan`, `create a plan` | Planning v5 | 10 | autonomous | AC-PLAN-* |

# After (Phase 2, TDD-Master complete):
| Pattern | Orchestrator | Priority | Mode | AC-ID Prefix |
|---------|--------------|----------|------|--------------|
| `tdd`, `test driven` | TDD-Master v1 | 20 | autonomous | AC-TDD-* |
| `implement`, `build`, `create`, `fix` | TDD-Master v1 | 15 | autonomous | AC-TDD-* |
| `plan`, `create a plan` | Planning v5 | 10 | autonomous | AC-PLAN-* |
```

### 3.2 Progressive Activation Timeline

| Week | Phase | Orchestrators Registered | Patterns Added | Total Patterns |
|------|-------|-------------------------|----------------|----------------|
| **1-2** | Phase 1 | None (infrastructure only) | 0 | 0 |
| **3** | Phase 2a | TDD-Master v1 | `tdd`, `implement`, `build`, `create`, `fix` | 5 |
| **4** | Phase 2b | Planning v5 | `plan`, `create a plan` | 7 |
| **5** | Phase 3a | ADO v2, Investigation, Crawler | `ado`, `investigate`, `crawl`, `scan code` | 11 |
| **6** | Phase 3b | Vacuum v2, Cleanup v2 | `vacuum`, `deep clean`, `cleanup` | 14 |
| **7** | Phase 4 | LLM Classifier (internal) | None (internal enhancement) | 14 |

---

## 4. Definition of Done (DoD) Criteria

### 4.1 Per AC-ID

**Required for EVERY AC-ID:**
- ✅ Implementation complete (all acceptance criteria met)
- ✅ Unit tests passing (≥80% line coverage)
- ✅ Integration tests passing (if applicable)
- ✅ Security tests passing (if user input handling)
- ✅ Clean Code Score ≥80 (radon + pylint + pydocstyle + mypy)
- ✅ Documentation generated (docstrings, usage examples)
- ✅ Audit trail complete (all operations logged with correlation IDs)
- ✅ Validation report generated (markdown, visual progress bars)
- ✅ User confirmation received (if interactive orchestrator)

### 4.2 Per Orchestrator

**Required for EVERY orchestrator:**
- ✅ Extends `BaseOrchestratorV4`
- ✅ Registered with `@register_with_master` decorator
- ✅ Patterns added to `CORTEX.prompt.md` routing table
- ✅ Manifest file created: `cortex-brain/manifests/{orchestrator-name}.yaml`
- ✅ Integration tests with MasterOrchestrator (routing validation)
- ✅ Timeout configured (default 5 min, override in manifest if needed)
- ✅ Error handling (timeout, failure, graceful degradation)

### 4.3 Per Phase

**Required for EVERY phase:**
- ✅ All AC-IDs in phase validated (DoD per AC-ID met)
- ✅ Phase-level integration tests passing
- ✅ Knowledge files updated (if tier1/tier2/tier3 changes)
- ✅ Documentation updated:
  - `docs/orchestrators/{orchestrator-name}.md` (usage guide)
  - `cortex-brain/documents/architecture/` (if architectural changes)
- ✅ Audit trail query confirms completeness:
  ```bash
  python3 -m src.main "audit query --ac-id AC-{PHASE}-* --level INFO"
  ```
- ✅ Phase closure report generated:
  ```
  cortex-brain/documents/phase-closure/phase-{N}-closure.md
  ```

### 4.4 Final Project Closure

**Required for CORTEX 6.0 v1.0.0 release:**
- ✅ All 57 AC-IDs validated
- ✅ All 4 phases complete
- ✅ All orchestrators registered in `CORTEX.prompt.md`
- ✅ Knowledge graph built (AC-CRAWLER-*)
- ✅ Audit database clean (retention policies applied)
- ✅ Performance benchmarks met:
  - MasterOrchestrator intake: <500ms
  - TDD-Master validation: <2s per AC
  - TodoManager execution: <100ms per task
- ✅ Security audit passed (no critical vulnerabilities)
- ✅ Documentation complete:
  - User guides
  - API reference
  - Architecture diagrams
  - Troubleshooting guides
- ✅ Git tags:
  - `v6.0.0-alpha` (Phase 1 complete)
  - `v6.0.0-beta` (Phase 2 complete)
  - `v6.0.0-rc1` (Phase 3 complete)
  - `v6.0.0` (Phase 4 complete)

---

## 5. Snowball Velocity Tracking

### 5.1 Metrics Dashboard

**Track these metrics weekly:**

| Metric | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Target |
|--------|---------|---------|---------|---------|--------|
| **AC-IDs/Week** | 7 | 17 | 11.5 | 8 | 14 avg |
| **Lines of Code/Week** | 2000 | 2500 | 2800 | 3000 | +25% by Phase 4 |
| **Test Coverage** | 82% | 84% | 86% | 88% | ≥80% |
| **Clean Code Score** | 81 | 83 | 85 | 87 | ≥80 |
| **Audit Logs Generated** | 500/week | 1200/week | 1800/week | 2000/week | Increasing |
| **Refactor Time Saved** | 0% | 15% | 25% | 37.5% | Cumulative gain |

### 5.2 Acceleration Indicators

**Green (Snowball Working):**
- ✅ Phase 2 AC-IDs/week > Phase 1 AC-IDs/week
- ✅ Code reuse increasing (fewer new files per orchestrator)
- ✅ Test suite passing faster (infrastructure stable)
- ✅ Fewer SKULL rule violations (governance internalized)

**Yellow (Velocity Plateau):**
- ⚠️ AC-IDs/week flat across phases
- ⚠️ Refactor time NOT decreasing
- ⚠️ New bugs increasing (technical debt)

**Red (Snowball Broken):**
- ❌ Phase 3 slower than Phase 2
- ❌ Infrastructure failures blocking features
- ❌ Test suite unstable
- ❌ Governance violations increasing

---

## 6. Risk Mitigation Strategies

### 6.1 Token Overflow (Probability: HIGH)

**Mitigation:**
```python
# AC-ORCH-006 (IncrementalExecutor)
class IncrementalExecutor:
    MAX_LINES = 500  # CORE-001 enforcement
    
    def execute(self, request: str) -> Result:
        chunks = self.chunk_by_lines(request, self.MAX_LINES)
        for i, chunk in enumerate(chunks):
            result = self.execute_chunk(chunk)
            if result.tokens_exceeded:
                self.persist_checkpoint(i)
                return PartialResult(resume_from=i)
        return CompleteResult()
```

### 6.2 Vacuum Premature Execution (Probability: HIGH)

**Mitigation:**
```python
# AC-VAC-001 (Pre-checks)
class VacuumOrchestrator(BaseOrchestratorV4):
    def validate_preconditions(self):
        graph = self.load_knowledge_graph()
        if not graph:
            raise GovernanceError("Knowledge graph missing - run Crawler first")
        if graph.age_days > 7:
            raise GovernanceError("Knowledge graph stale (>7 days) - refresh Crawler")
        if self.has_uncommitted_changes():
            raise GovernanceError("Uncommitted git changes - commit first")
```

### 6.3 State Corruption (Probability: MEDIUM)

**Mitigation:**
```python
# AC-STATE-002 (Atomic Transactions)
class StateManager:
    def save_state(self, key: str, value: Dict) -> None:
        with self.db:  # Automatic ACID transaction
            self.db.execute("INSERT OR REPLACE INTO state (key, value, updated_at) VALUES (?, ?, ?)",
                            (key, json.dumps(value), datetime.now()))
        # Either fully committed or fully rolled back - no partial writes
```

### 6.4 Governance Bypass (Probability: MEDIUM)

**Mitigation:**
```python
# AC-ORCH-001 (Decorator Enforcement)
def require_master_routing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not MasterOrchestrator.is_active():
            raise MasterBypassError("CORE-017 violated: MasterOrchestrator bypassed")
        return func(*args, **kwargs)
    return wrapper

# Applied to ALL orchestrator entry points
class PlanningOrchestrator(BaseOrchestratorV4):
    @require_master_routing
    def execute(self, request: str) -> Result:
        ...
```

---

## 7. Communication Plan

### 7.1 Daily Standups (Async)

**Format:** Slack/Teams message
**Timing:** 9 AM daily
**Content:**
- ✅ Completed AC-IDs (yesterday)
- ⏳ In-progress AC-IDs (today)
- 🚧 Blockers (need help)
- 📊 Metrics (coverage, quality, velocity)

### 7.2 Weekly Progress Reports

**Format:** Markdown document
**Location:** `cortex-brain/documents/progress-reports/week-{N}.md`
**Content:**
- AC-IDs completed (with links to validation reports)
- Orchestrators registered (with routing patterns)
- Metrics dashboard (current vs target)
- Risks identified (with mitigations)
- Next week's plan

### 7.3 Phase Closure Reviews

**Format:** Meeting + document
**Timing:** End of each phase
**Content:**
- Phase completion criteria validated
- DoD checklist reviewed
- Knowledge files updated
- Architectural decisions documented
- Lessons learned captured
- Next phase kickoff

---

## 8. Rollback Strategy

**If critical failure detected:**

### 8.1 Per AC-ID Rollback
```bash
# Revert code changes
git revert {commit-hash}

# Remove from routing table
# Edit .github/copilot-instructions.md, remove pattern entry

# Mark AC-ID as FAILED
python3 -m src.main "update ac-status AC-{ID} FAILED"

# Audit trail
python3 -m src.main "audit log CRITICAL 'AC-{ID} rolled back: {reason}'"
```

### 8.2 Per Phase Rollback
```bash
# Checkout previous phase branch
git checkout CORTEX-6.0-phase-{N-1}

# Restore database
cp cortex-brain/tier0/database/state.db.backup cortex-brain/tier0/database/state.db

# Re-export JSON snapshot
python3 -m src.main "export state-snapshot"

# Notify team
echo "Phase {N} rolled back - investigate {reason}"
```

---

## 9. Success Criteria

**CORTEX 6.0 is production-ready when:**

- ✅ All 57 AC-IDs validated (tests ≥80%, quality ≥80)
- ✅ All 4 phases complete (Foundation → Core → Features → Intelligence)
- ✅ Snowball acceleration demonstrated (37.5% efficiency gain by Phase 4)
- ✅ Live wiring operational (14 patterns registered in routing table)
- ✅ Knowledge graph built (prerequisite for Vacuum)
- ✅ Audit trail complete (all operations logged)
- ✅ Documentation complete (user guides, API reference, architecture)
- ✅ Performance benchmarks met (MasterOrch <500ms, TDD-Master <2s)
- ✅ Security audit passed (no critical vulnerabilities)
- ✅ Team onboarded (training complete, knowledge transfer done)

---

## 10. Summary

**Implementation Strategy:** Snowball (build infrastructure first, features compound)  
**Total Duration:** 7 weeks (2026-01-10 to 2026-02-28)  
**Total AC-IDs:** 57 (14 Phase 1, 34 Phase 2, 23 Phase 3, 8 Phase 4)  
**Efficiency Gain:** 37.5% (by Phase 4, infrastructure reuse compounds)  
**Live Wiring:** Progressive activation (orchestrators register upon completion)  
**Quality Gates:** TDD-Master enforces ≥80% coverage, ≥80 clean code score  
**Risk Level:** MEDIUM (acceptable with documented mitigations)

**Next Document:** phase-activation.md (week-by-week activation checklist)

---

**Document Status:** ✅ COMPLETE  
**Implementation Ready:** ✅ YES  
**Review Required:** Technical Lead (Asif Hussain)
