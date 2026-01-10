# CORTEX 6.0 Phase Activation Checklist

**Version:** 6.0.0 | **Status:** READY FOR EXECUTION  
**Author:** Asif Hussain | **Created:** 2026-01-10  
**Target Completion:** 2026-02-28 (7 weeks)  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## Executive Summary

This checklist provides **week-by-week activation timeline** for CORTEX 6.0 orchestrator registration, routing table updates, knowledge file additions, and progressive testing. Use this as the **operational playbook** during implementation.

**Key Activities:**
- **Orchestrator Registration:** When each orchestrator completes AC validation
- **Routing Table Updates:** Patterns added to `CORTEX.prompt.md`
- **Knowledge File Updates:** Tier 1-3 YAML updates
- **Testing Requirements:** Integration tests per activation

---

## Week 1-2: Phase 1 - Foundation

### Week 1 (2026-01-10 to 2026-01-17)

#### Day 1-3: Audit Infrastructure
**AC-IDs:** AC-AUDIT-001 to AC-AUDIT-003

**Tasks:**
- [ ] Implement `EnterpriseAuditLogger` with SQLite schema
- [ ] Enable WAL mode: `PRAGMA journal_mode=WAL`
- [ ] Create indexes on: `timestamp`, `correlation_id`, `ac_id`, `category`
- [ ] Implement buffered async logging (100ms flush interval)
- [ ] Add 7 categories: GOVERNANCE, ORCHESTRATOR, VALIDATION, INFRASTRUCTURE, BRAIN, INTEGRATION, MCP
- [ ] Write tests: `test_audit_schema.py`, `test_async_logging.py`, `test_categories.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/infrastructure/enhanced_audit_logger.py
cortex-brain/tier0/database/audit_logs.db
tests/infrastructure/test_audit_schema.py
tests/infrastructure/test_async_logging.py
tests/infrastructure/test_categories.py
```

**Routing Table Update:** None (infrastructure only)

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/infrastructure/test_audit_*.py --cov=src/infrastructure/enhanced_audit_logger
python3 -m src.main "validate AC-AUDIT-001 AC-AUDIT-002 AC-AUDIT-003"
```

---

#### Day 4-5: Audit Infrastructure (Continued)
**AC-IDs:** AC-AUDIT-004 to AC-AUDIT-006

**Tasks:**
- [ ] Implement context propagation (correlation IDs)
- [ ] Implement retention policy (CRITICAL=90d, ERROR=90d, WARNING=60d, INFO=30d, DEBUG=7d)
- [ ] Implement query interface (by: correlation_id, ac_id, category, level, time range)
- [ ] Create `scripts/audit_log_manager.py` for querying
- [ ] Write tests: `test_correlation_ids.py`, `test_retention.py`, `test_query.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
scripts/audit_log_manager.py
tests/infrastructure/test_correlation_ids.py
tests/infrastructure/test_retention.py
tests/infrastructure/test_query.py
```

**Routing Table Update:** None

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/infrastructure/test_audit_*.py --cov=src/infrastructure/enhanced_audit_logger
python3 -m src.main "validate AC-AUDIT-004 AC-AUDIT-005 AC-AUDIT-006"
```

---

### Week 2 (2026-01-18 to 2026-01-24)

#### Day 1-2: Governance Merger
**AC-IDs:** AC-GOV-001 to AC-GOV-003

**Tasks:**
- [ ] Implement `GovernanceMerger` class
- [ ] Load tier 0-3 rules from YAML files
- [ ] Implement precedence algorithm (Tier 0 > Tier 1 > Tier 2 > Tier 3)
- [ ] Implement conflict resolution (Tier 0 always wins)
- [ ] Write tests: `test_load_rules.py`, `test_precedence.py`, `test_conflicts.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/core/governance_merger.py
tests/orchestrators/core/test_governance_merger.py
```

**Routing Table Update:** None (used internally by MasterOrchestrator)

**Knowledge File Update:** None (loads existing files)

**Validation:**
```bash
pytest tests/orchestrators/core/test_governance_merger.py --cov=src/orchestrators/core/governance_merger
python3 -m src.main "validate AC-GOV-001 AC-GOV-002 AC-GOV-003"
```

---

#### Day 3-4: Governance Merger (Continued)
**AC-IDs:** AC-GOV-004 to AC-GOV-005

**Tasks:**
- [ ] Implement Final Instruction (F) generation (merged ruleset)
- [ ] Implement cache with file change detection
- [ ] Cache invalidation on YAML file updates
- [ ] Write tests: `test_final_instruction.py`, `test_cache.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
tests/orchestrators/core/test_final_instruction.py
tests/orchestrators/core/test_cache.py
```

**Routing Table Update:** None

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/core/test_governance_merger.py --cov=src/orchestrators/core/governance_merger
python3 -m src.main "validate AC-GOV-004 AC-GOV-005"
```

---

#### Day 5: State Manager
**AC-IDs:** AC-STATE-001 to AC-STATE-003

**Tasks:**
- [ ] Implement `StateManager` class
- [ ] Create SQLite schema for state (phases, tasks, orchestrators)
- [ ] Enable WAL mode: `PRAGMA journal_mode=WAL`
- [ ] Implement atomic transactions (ACID guarantees)
- [ ] Implement JSON export to `progress-tracker.json`
- [ ] Write tests: `test_state_storage.py`, `test_transactions.py`, `test_json_export.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/infrastructure/state_manager.py
cortex-brain/tier0/database/state.db
tests/infrastructure/test_state_manager.py
```

**Routing Table Update:** None (infrastructure only)

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/infrastructure/test_state_manager.py --cov=src/infrastructure/state_manager
python3 -m src.main "validate AC-STATE-001 AC-STATE-002 AC-STATE-003"
```

---

**Phase 1 Milestone (End of Week 2):**
- ✅ Audit infrastructure operational (6 AC-IDs complete)
- ✅ Governance merger operational (5 AC-IDs complete)
- ✅ State manager operational (3 AC-IDs complete)
- ✅ Foundation ready for Phase 2 (14 AC-IDs total)
- ✅ No orchestrator routing yet (infrastructure only)

---

## Week 3-4: Phase 2 - Orchestration Core

### Week 3 (2026-01-25 to 2026-01-31)

#### Day 1-2: MasterOrchestrator (Intake & Classification)
**AC-IDs:** AC-ORCH-001 to AC-ORCH-002

**Tasks:**
- [ ] Implement `MasterOrchestrator` class extending `BaseOrchestratorV4`
- [ ] Implement `intake()` method (context loading)
- [ ] Load `progress-tracker.json`, `AC-INDEX.yaml`, `core-rules.yaml` on startup
- [ ] Implement `classify_intent()` method (pattern matching)
- [ ] Write tests: `test_intake.py`, `test_classify.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/core/master_orchestrator.py
tests/orchestrators/core/test_master_orchestrator.py
```

**Routing Table Update:** None (internal routing controller)

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/core/test_master_orchestrator.py --cov=src/orchestrators/core/master_orchestrator
python3 -m src.main "validate AC-ORCH-001 AC-ORCH-002"
```

---

#### Day 3-4: MasterOrchestrator (Registry & Routing)
**AC-IDs:** AC-ORCH-003 to AC-ORCH-005

**Tasks:**
- [ ] Implement `OrchestratorRegistry` class
- [ ] Store orchestrators with patterns, priority, AC prefix
- [ ] Implement `@register_with_master` decorator
- [ ] Implement routing logic (highest priority matching orchestrator)
- [ ] Write tests: `test_registry.py`, `test_decorator.py`, `test_routing.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/core/registry.py
src/orchestrators/core/decorators.py
tests/orchestrators/core/test_registry.py
tests/orchestrators/core/test_decorator.py
```

**Routing Table Update:** None (registry infrastructure)

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/core/test_registry.py --cov=src/orchestrators/core/registry
pytest tests/orchestrators/core/test_decorator.py --cov=src/orchestrators/core/decorators
python3 -m src.main "validate AC-ORCH-003 AC-ORCH-004 AC-ORCH-005"
```

---

#### Day 5: MasterOrchestrator (Evaluation & Execution)
**AC-IDs:** AC-ORCH-006 to AC-ORCH-008

**Tasks:**
- [ ] Implement `evaluate()` method (request → RequiredActions)
- [ ] Integrate GovernanceMerger for rule enforcement
- [ ] Implement RequiredAction → Task mapping
- [ ] Implement `execute()` method (delegates to TodoManager)
- [ ] Write tests: `test_evaluation.py`, `test_action_mapping.py`, `test_execution.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
tests/orchestrators/core/test_evaluation.py
tests/orchestrators/core/test_action_mapping.py
tests/orchestrators/core/test_execution.py
```

**Routing Table Update:** None (internal controller)

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/core/test_master_orchestrator.py --cov=src/orchestrators/core/master_orchestrator
python3 -m src.main "validate AC-ORCH-006 AC-ORCH-007 AC-ORCH-008"
```

---

### Week 4 (2026-02-01 to 2026-02-07)

#### Day 1-2: TodoManager
**AC-IDs:** AC-TODO-001 to AC-TODO-004

**Tasks:**
- [ ] Implement `TodoManager` class
- [ ] Define task schema (10 fields: id, name, status, priority, dependencies, etc.)
- [ ] Implement dependency resolution (topological sort, circular detection)
- [ ] Implement execution engine (runs tasks in dependency order)
- [ ] Implement progress persistence (SQLite + JSON export)
- [ ] Write tests: `test_task_schema.py`, `test_dependencies.py`, `test_execution.py`, `test_persistence.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/core/todo_manager.py
tests/orchestrators/core/test_todo_manager.py
```

**Routing Table Update:** None (called by MasterOrchestrator)

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/core/test_todo_manager.py --cov=src/orchestrators/core/todo_manager
python3 -m src.main "validate AC-TODO-001 AC-TODO-002 AC-TODO-003 AC-TODO-004"
```

---

#### Day 3-5: TDD-Master v1 (Part 1)
**AC-IDs:** AC-TDD-001 to AC-TDD-005

**Tasks:**
- [ ] Implement `TDDMaster` class extending `BaseOrchestratorV4`
- [ ] Implement requirement extraction (AC criteria → test specs)
- [ ] Implement test generation (unit/integration via pytest)
- [ ] Implement security test generation (AST detects user input)
- [ ] Implement RED phase execution (run tests, expect failures)
- [ ] Implement Clean Code Score (radon + pylint + pydocstyle + mypy ≥80)
- [ ] Write tests: `test_extraction.py`, `test_generation.py`, `test_security_gen.py`, `test_red_phase.py`, `test_clean_code.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/tdd/tdd_master.py
src/orchestrators/tdd/code_quality_checker.py
tests/orchestrators/tdd/test_tdd_master.py
tests/orchestrators/tdd/test_clean_code.py
```

**Routing Table Update:** ⚠️ PENDING (complete AC-TDD-006 to AC-TDD-010 first)

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/tdd/test_tdd_master.py --cov=src/orchestrators/tdd/tdd_master
python3 -m src.main "validate AC-TDD-001 AC-TDD-002 AC-TDD-003 AC-TDD-004 AC-TDD-005"
```

---

**Week 4 Continuation (2026-02-08 to 2026-02-07) - TDD-Master Part 2:**

#### Day 1-2 (Week 5 Start): TDD-Master v1 (Part 2)
**AC-IDs:** AC-TDD-006 to AC-TDD-010

**Tasks:**
- [ ] Implement validation report generator (markdown with progress bars)
- [ ] Implement AC validator (verifies all criteria met)
- [ ] Implement documentation generator (auto-generates usage docs)
- [ ] Implement audit trail integration (logs with correlation IDs)
- [ ] Implement user confirmation flow ("Proceed?" before commit)
- [ ] Write tests: `test_validation.py`, `test_ac_validation.py`, `test_doc_gen.py`, `test_audit.py`, `test_confirmation.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/tdd/validation_reporter.py
src/orchestrators/tdd/ac_validator.py
src/orchestrators/tdd/doc_generator.py
templates/validation-report.md.jinja2
tests/orchestrators/tdd/test_validation.py
```

**Routing Table Update:** ✅ ADD TO CORTEX.prompt.md
```markdown
| `tdd`, `test driven` | TDD-Master v1 | 20 | autonomous | AC-TDD-* |
| `implement`, `build`, `create`, `fix` | TDD-Master v1 | 15 | autonomous | AC-TDD-* |
```

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/tdd/ --cov=src/orchestrators/tdd
python3 -m src.main "validate AC-TDD-006 AC-TDD-007 AC-TDD-008 AC-TDD-009 AC-TDD-010"
```

**Decorator Registration:**
```python
@register_with_master(
    patterns=["tdd", "test driven", "implement", "build", "create", "fix"],
    priority=15,  # "implement" patterns
    ac_prefix="AC-TDD"
)
class TDDMaster(BaseOrchestratorV4):
    pass
```

---

#### Day 3-5 (Week 5): Planning v5
**AC-IDs:** AC-PLAN-001 to AC-PLAN-008

**Tasks:**
- [ ] Implement `PlanningOrchestrator` class extending `BaseOrchestratorV4`
- [ ] Implement context loading (progress-tracker, AC-INDEX, core-rules)
- [ ] Implement requirement analysis (features, constraints, dependencies)
- [ ] Implement incremental planning (<500 lines per increment)
- [ ] Implement phase decomposition (breaks work into phases with AC-IDs)
- [ ] Implement risk assessment (probability/impact matrix)
- [ ] Implement DoD criteria generation (completion checklists)
- [ ] Implement markdown plan generation (outputs to cortex-brain/documents/planning/)
- [ ] Implement validation via TDD-Master (routes through AC-TDD-007)
- [ ] Write tests: `test_context_load.py`, `test_analysis.py`, `test_incremental.py`, `test_phases.py`, `test_risk.py`, `test_dod.py`, `test_plan_gen.py`, `test_validation.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/planning/planning_orchestrator.py
src/orchestrators/planning/plan_generator.py
tests/orchestrators/planning/test_planning.py
cortex-brain/documents/planning/ (output directory)
```

**Routing Table Update:** ✅ ADD TO CORTEX.prompt.md
```markdown
| `plan`, `create a plan` | Planning v5 | 10 | autonomous | AC-PLAN-* |
```

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/planning/ --cov=src/orchestrators/planning
python3 -m src.main "validate AC-PLAN-001 AC-PLAN-002 AC-PLAN-003 AC-PLAN-004 AC-PLAN-005 AC-PLAN-006 AC-PLAN-007 AC-PLAN-008"
```

**Decorator Registration:**
```python
@register_with_master(
    patterns=["plan", "create a plan"],
    priority=10,
    ac_prefix="AC-PLAN"
)
class PlanningOrchestrator(BaseOrchestratorV4):
    pass
```

---

#### Day 5 (Week 5): Knowledge Files
**AC-IDs:** AC-KNOW-001 to AC-KNOW-003

**Tasks:**
- [ ] Create `engineering-standards.yaml` (Tier 2)
- [ ] Sections: code_style, testing_requirements, documentation_standards, security_checklist
- [ ] Create `domain-patterns.yaml` (Tier 3)
- [ ] Sections: auth_patterns, database_patterns, api_patterns, security_patterns
- [ ] Create `company-practices.yaml` (Tier 1)
- [ ] Sections: review_requirements, deployment_procedures, compliance_rules
- [ ] Write tests: `test_tier1_load.py`, `test_tier2_load.py`, `test_tier3_load.py`
- [ ] Validate GovernanceMerger loads all files

**Files Created:**
```
cortex-brain/tier1/company-practices.yaml
cortex-brain/tier2/engineering-standards.yaml
cortex-brain/tier3/domain-patterns.yaml
tests/governance/test_knowledge_files.py
```

**Routing Table Update:** None (loaded by GovernanceMerger)

**Knowledge File Update:** ✅ ALL THREE FILES CREATED

**Validation:**
```bash
pytest tests/governance/test_knowledge_files.py
python3 -m src.main "validate AC-KNOW-001 AC-KNOW-002 AC-KNOW-003"
```

---

**Phase 2 Milestone (End of Week 4-5):**
- ✅ MasterOrchestrator operational (8 AC-IDs complete)
- ✅ TodoManager operational (4 AC-IDs complete)
- ✅ TDD-Master v1 operational (10 AC-IDs complete)
- ✅ Planning v5 operational (8 AC-IDs complete)
- ✅ Knowledge files created (3 AC-IDs complete)
- ✅ Routing table includes TDD-Master, Planning v5 (2 orchestrators, 7 patterns)
- ✅ Core workflow operational (request → MasterOrch → TodoManager → execute)

---

## Week 5-6: Phase 3 - Feature Orchestrators

### Week 5-6 (2026-02-08 to 2026-02-21)

#### Day 1-2: ADO v2
**AC-IDs:** AC-ADO-001 to AC-ADO-006

**Tasks:**
- [ ] Implement `ADOClient` (Azure DevOps API client)
- [ ] Implement authentication (PAT token)
- [ ] Implement work item creation (user stories, bugs, tasks)
- [ ] Implement WIQL queries (sprint work)
- [ ] Implement git integration (link commits to work items)
- [ ] Write contract tests (detect API drift)
- [ ] Implement error handling (timeout, retry, fallback)
- [ ] Write tests: `test_ado_client.py`, `test_create_workitem.py`, `test_query_workitems.py`, `test_git_integration.py`, `test_contracts.py`, `test_error_handling.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/ado/ado_client.py
src/orchestrators/ado/ado_orchestrator.py
tests/orchestrators/ado/test_ado_*.py
tests/integration/test_ado_contracts.py
```

**Routing Table Update:** ✅ ADD TO CORTEX.prompt.md
```markdown
| `ado`, `azure devops` | ADO v2 | 30 | autonomous | AC-ADO-* |
```

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/ado/ --cov=src/orchestrators/ado
python3 -m src.main "validate AC-ADO-001 AC-ADO-002 AC-ADO-003 AC-ADO-004 AC-ADO-005 AC-ADO-006"
```

**Decorator Registration:**
```python
@register_with_master(
    patterns=["ado", "azure devops"],
    priority=30,
    ac_prefix="AC-ADO"
)
class ADOOrchestrator(BaseOrchestratorV4):
    pass
```

---

#### Day 3: Investigation
**AC-IDs:** AC-INV-001 to AC-INV-003

**Tasks:**
- [ ] Implement `InvestigationOrchestrator` class
- [ ] Implement evidence collection (file paths, git history, errors)
- [ ] Implement pattern analysis (identifies common failures)
- [ ] Implement report generation (markdown with findings)
- [ ] Write tests: `test_evidence.py`, `test_patterns.py`, `test_report.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/investigation/investigation_orchestrator.py
tests/orchestrators/investigation/test_investigation.py
```

**Routing Table Update:** ✅ ADD TO CORTEX.prompt.md
```markdown
| `investigate` | Investigation | 60 | autonomous | AC-INV-* |
```

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/investigation/ --cov=src/orchestrators/investigation
python3 -m src.main "validate AC-INV-001 AC-INV-002 AC-INV-003"
```

**Decorator Registration:**
```python
@register_with_master(
    patterns=["investigate"],
    priority=60,
    ac_prefix="AC-INV"
)
class InvestigationOrchestrator(BaseOrchestratorV4):
    pass
```

---

#### Day 4-5 (Week 5) + Day 1-2 (Week 6): Crawler Orchestrator
**AC-IDs:** AC-CRAWLER-001 to AC-CRAWLER-005

**Tasks:**
- [ ] Implement `ASTPparser` (Python AST parsing)
- [ ] Extract imports, functions, classes
- [ ] Implement `DependencyMapper` (builds import graph)
- [ ] Implement `KnowledgeGraphBuilder` (Neo4j or SQLite graph schema)
- [ ] Implement `FileUsageTracker` (identifies actively used files)
- [ ] Implement `OrphanDetector` (finds unused files)
- [ ] Write tests: `test_ast_parsing.py`, `test_dependencies.py`, `test_graph_build.py`, `test_file_usage.py`, `test_orphan_detection.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/crawler/ast_parser.py
src/orchestrators/crawler/dependency_mapper.py
src/orchestrators/crawler/knowledge_graph_builder.py
src/orchestrators/crawler/file_usage_tracker.py
src/orchestrators/crawler/orphan_detector.py
tests/orchestrators/crawler/test_*.py
cortex-brain/tier1/knowledge-graph.db
```

**Routing Table Update:** ✅ ADD TO CORTEX.prompt.md
```markdown
| `crawl`, `scan code`, `analyze codebase`, `knowledge graph` | Crawler Orchestrator | 35 | autonomous | AC-CRAWLER-* |
```

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/crawler/ --cov=src/orchestrators/crawler
python3 -m src.main "validate AC-CRAWLER-001 AC-CRAWLER-002 AC-CRAWLER-003 AC-CRAWLER-004 AC-CRAWLER-005"
```

**Decorator Registration:**
```python
@register_with_master(
    patterns=["crawl", "scan code", "analyze codebase", "knowledge graph"],
    priority=35,
    ac_prefix="AC-CRAWLER"
)
class CrawlerOrchestrator(BaseOrchestratorV4):
    pass
```

---

#### Day 3-4 (Week 6): Vacuum v2
**AC-IDs:** AC-VAC-001 to AC-VAC-006

**Tasks:**
- [ ] Implement `VacuumOrchestrator` class
- [ ] Implement pre-checks (knowledge graph exists, <7d old, no uncommitted git changes)
- [ ] Implement safe deletion (.bak, .tmp files)
- [ ] Implement medium risk deletion (duplicates, requires graph verification)
- [ ] Implement high risk deletion (orphans, deep analysis + user confirmation)
- [ ] Implement dry-run mode (shows what WOULD delete)
- [ ] Implement report generation (markdown with results)
- [ ] Write tests: `test_prechecks.py`, `test_safe_deletion.py`, `test_medium_deletion.py`, `test_high_deletion.py`, `test_dry_run.py`, `test_report.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/vacuum/vacuum_orchestrator.py
tests/orchestrators/vacuum/test_vacuum.py
```

**Routing Table Update:** ✅ ADD TO CORTEX.prompt.md
```markdown
| `vacuum`, `deep clean` | Vacuum v2 | 45 | autonomous | AC-VAC-* |
```

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/vacuum/ --cov=src/orchestrators/vacuum
python3 -m src.main "validate AC-VAC-001 AC-VAC-002 AC-VAC-003 AC-VAC-004 AC-VAC-005 AC-VAC-006"
```

**Decorator Registration:**
```python
@register_with_master(
    patterns=["vacuum", "deep clean"],
    priority=45,
    ac_prefix="AC-VAC"
)
class VacuumOrchestrator(BaseOrchestratorV4):
    pass
```

---

#### Day 5 (Week 6): Cleanup v2
**AC-IDs:** AC-CLEAN-001 to AC-CLEAN-004

**Tasks:**
- [ ] Implement `CleanupOrchestrator` class
- [ ] Implement root-level file detection (finds files violating CORE-009)
- [ ] Implement categorization (plans, summaries, docs)
- [ ] Implement move to tier folders (appropriate tier based on content)
- [ ] Implement report generation (markdown with moves)
- [ ] Write tests: `test_root_detection.py`, `test_categorization.py`, `test_move_files.py`, `test_report.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/cleanup/cleanup_orchestrator.py
tests/orchestrators/cleanup/test_cleanup.py
```

**Routing Table Update:** ✅ ADD TO CORTEX.prompt.md
```markdown
| `cleanup` | Cleanup v2 | 55 | autonomous | AC-CLEAN-* |
```

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/cleanup/ --cov=src/orchestrators/cleanup
python3 -m src.main "validate AC-CLEAN-001 AC-CLEAN-002 AC-CLEAN-003 AC-CLEAN-004"
```

**Decorator Registration:**
```python
@register_with_master(
    patterns=["cleanup"],
    priority=55,
    ac_prefix="AC-CLEAN"
)
class CleanupOrchestrator(BaseOrchestratorV4):
    pass
```

---

**Phase 3 Milestone (End of Week 5-6):**
- ✅ ADO v2 operational (6 AC-IDs complete)
- ✅ Investigation operational (3 AC-IDs complete)
- ✅ Crawler operational (5 AC-IDs complete)
- ✅ Vacuum v2 operational (6 AC-IDs complete)
- ✅ Cleanup v2 operational (4 AC-IDs complete)
- ✅ Routing table includes 5 new orchestrators (14 patterns total)
- ✅ Knowledge graph built (prerequisite for Vacuum met)

---

## Week 7: Phase 4 - Intelligence Layer

### Week 7 (2026-02-22 to 2026-02-28)

#### Day 1-2: LLM Intent Classifier
**AC-IDs:** AC-LLM-001 to AC-LLM-004

**Tasks:**
- [ ] Implement `LLMIntentClassifier` class
- [ ] Implement fuzzy pattern matching (handles typos, variations)
- [ ] Implement intent confidence scoring (0-100 per orchestrator)
- [ ] Implement fallback to MasterOrchestrator (if confidence <70)
- [ ] Implement learning from corrections (updates tier3/domain-patterns.yaml)
- [ ] Write tests: `test_fuzzy_matching.py`, `test_confidence.py`, `test_fallback.py`, `test_learning.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/llm/llm_intent_classifier.py
tests/orchestrators/llm/test_llm_intent_classifier.py
```

**Routing Table Update:** None (internal enhancement, called by MasterOrchestrator)

**Knowledge File Update:** ✅ AUTO-UPDATES tier3/domain-patterns.yaml (learning)

**Validation:**
```bash
pytest tests/orchestrators/llm/ --cov=src/orchestrators/llm
python3 -m src.main "validate AC-LLM-001 AC-LLM-002 AC-LLM-003 AC-LLM-004"
```

---

#### Day 3: Vision API
**AC-IDs:** AC-VIS-001 to AC-VIS-003

**Tasks:**
- [ ] Implement `VisionAPI` class
- [ ] Implement image analysis (extracts text, diagrams, code)
- [ ] Implement timeout fallback (500ms timeout, graceful degradation)
- [ ] Implement integration with Planning v5 (diagram analysis)
- [ ] Write tests: `test_image_analysis.py`, `test_timeout.py`, `test_planning_integration.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/vision/vision_api.py
tests/orchestrators/vision/test_vision_api.py
```

**Routing Table Update:** None (enhancement to Planning v5)

**Knowledge File Update:** None

**Validation:**
```bash
pytest tests/orchestrators/vision/ --cov=src/orchestrators/vision
python3 -m src.main "validate AC-VIS-001 AC-VIS-002 AC-VIS-003"
```

---

#### Day 4-5: Knowledge Practices
**AC-IDs:** AC-KNOW-PRAC-001 to AC-KNOW-PRAC-005 (Note: AC-KNOW-PRAC-005 listed but only 3 in registry)

**Tasks:**
- [ ] Implement `KnowledgePractices` class
- [ ] Implement pattern extraction (learns from successful AC validations)
- [ ] Implement Tier 3 updates (auto-updates domain-patterns.yaml)
- [ ] Implement anti-pattern detection (identifies repeated failures)
- [ ] Implement recommendation engine (suggests better patterns)
- [ ] Implement continuous learning (learns from every validation)
- [ ] Write tests: `test_pattern_extraction.py`, `test_tier3_updates.py`, `test_antipatterns.py`, `test_recommendations.py`, `test_continuous_learning.py`
- [ ] Validate coverage ≥80%, quality ≥80

**Files Created:**
```
src/orchestrators/knowledge/knowledge_practices.py
tests/orchestrators/knowledge/test_knowledge_practices.py
```

**Routing Table Update:** None (background learning)

**Knowledge File Update:** ✅ AUTO-UPDATES tier3/domain-patterns.yaml (continuous learning)

**Validation:**
```bash
pytest tests/orchestrators/knowledge/ --cov=src/orchestrators/knowledge
python3 -m src.main "validate AC-KNOW-PRAC-001 AC-KNOW-PRAC-002 AC-KNOW-PRAC-003"
```

---

**Phase 4 Milestone (End of Week 7):**
- ✅ LLM Intent Classifier operational (4 AC-IDs complete)
- ✅ Vision API operational (3 AC-IDs complete)
- ✅ Knowledge Practices operational (3 AC-IDs complete)
- ✅ Routing table complete (14 patterns, 9 orchestrators)
- ✅ Continuous learning enabled (tier3 auto-updates)
- ✅ User experience enhanced (fuzzy matching, visual input)

---

## Summary: Progressive Activation Timeline

| Week | Phase | Orchestrators Added | Patterns Added | Total Orchestrators | Total Patterns |
|------|-------|---------------------|----------------|---------------------|----------------|
| **1-2** | Phase 1 | None (infrastructure) | 0 | 0 | 0 |
| **3-4** | Phase 2a | TDD-Master v1 | `tdd`, `implement`, `build`, `create`, `fix` | 1 | 5 |
| **4-5** | Phase 2b | Planning v5 | `plan`, `create a plan` | 2 | 7 |
| **5** | Phase 3a | ADO v2 | `ado`, `azure devops` | 3 | 9 |
| **5** | Phase 3b | Investigation | `investigate` | 4 | 10 |
| **5-6** | Phase 3c | Crawler | `crawl`, `scan code`, `analyze codebase`, `knowledge graph` | 5 | 14 |
| **6** | Phase 3d | Vacuum v2 | `vacuum`, `deep clean` | 6 | 16 |
| **6** | Phase 3e | Cleanup v2 | `cleanup` | 7 | 17 |
| **7** | Phase 4 | LLM Classifier (internal) | None (internal) | 7 | 17 |

**Final State (End of Week 7):**
- **Total Orchestrators:** 7 user-facing + 2 internal (MasterOrchestrator, LLM Classifier)
- **Total Patterns:** 17 user-facing patterns
- **Total AC-IDs:** 57 (all validated)
- **Knowledge Files:** 3 (tier1, tier2, tier3) with continuous learning
- **Live Wiring:** 100% operational (all orchestrators registered)

---

**Document Status:** ✅ COMPLETE  
**Activation Ready:** ✅ YES  
**Review Required:** Technical Lead (Asif Hussain)  
**Next Document:** dod-matrix.md
