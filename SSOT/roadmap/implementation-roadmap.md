# Implementation Roadmap: Weeks 1-5

**Date:** 2026-01-14  
**Total Duration:** 5 weeks  
**Status:** Ready for Kickoff  
**Team Size:** 1 (GitHub Copilot) + Code Review (User)

---

## Phase 1: Foundation (Week 1) - Mon 1/13 to Fri 1/17

**Goal:** Build immutable core infrastructure that other phases depend on

**Deliverables:** 6 core systems, 100+ unit tests, 0 CRITICAL risks

---

### Week 1 Pre-Tasks (Mon 1/13 Morning) - Folder Structure & Templates Setup
**Time Budget:** 4 hours | **Tests Required:** 0 (structural)

#### Pre-Task 1: Create Nested Folder Structure
**Acceptance Criteria:**
- [ ] All directories created (no files moved yet)
- [ ] cortex-brain/tier2/response-templates/ with sub-folders (_schema, core, domain, custom)
- [ ] src/orchestrators/core/, domain/, custom/, middleware/, registry/, response/
- [ ] src/infrastructure/audit-logger/, governance/, state/, execution/
- [ ] src/mcp/tools/
- [ ] tests/unit/, integration/, fixtures/
- [ ] scripts/admin/, generate/, tools/
- [ ] Verify no conflicts with existing folders
- [ ] Ready for file migration (Phase 3)

**Implementation:**
- Use: PowerShell mkdir commands (provided in folder-structure-design.md)
- Duration: 30 minutes
- Verification: Tree command shows complete structure

---

#### Pre-Task 2: Create Standard Response Template Schema
**Acceptance Criteria:**
- [ ] File: cortex-brain/tier2/response-templates/_schema/standard-schema.yaml
- [ ] Content: CORTEX 4.0 schema (extracted from response-templates-v4.yaml)
- [ ] Includes: mandatory_header, executive_summary, custom_sections sections
- [ ] Version: 4.6.0
- [ ] Documentation: Schema comments explaining each field

**Implementation:**
- Extract from: __backup/cortex-brain/response-templates-v4.yaml
- Lines: ~150-200 lines
- Files: standard-schema.yaml (new)

---

#### Pre-Task 3: Create Template Files for Core Orchestrators
**Acceptance Criteria:**
- [ ] File: cortex-brain/tier2/response-templates/core/master-orch.yaml (standard template)
- [ ] File: cortex-brain/tier2/response-templates/core/tdd-master.yaml (custom with test metrics)
- [ ] File: cortex-brain/tier2/response-templates/core/planning-orch.yaml (standard)
- [ ] File: cortex-brain/tier2/response-templates/core/governance-orch.yaml (standard)
- [ ] All reference standard schema
- [ ] All conform to CORTEX 4.0 mandatory header format

**Implementation:**
- Create: 4 YAML files (~40 lines each)
- Content: From custom-response-templates.md examples
- Verification: YAML validation passes

---

### Week 1 Day 1 (Mon 1/13) - Governance Foundation
**Time Budget:** 8 hours | **Tests Required:** 20

#### Task 1.1: Create Governance Registry
**Acceptance Criteria:**
- [ ] GovernanceRegistry class loads YAML via reflection
- [ ] Auto-imports middleware classes from src/orchestrators/middleware/
- [ ] Auto-instantiates with config from YAML
- [ ] In-memory cache loaded at startup
- [ ] Unit tests: 100% coverage (load, instantiate, query)

**Implementation:**
- File: `src/orchestrators/core/governance_registry.py` (200 lines max)
- Dependencies: yaml (stdlib), importlib (stdlib), dataclasses (stdlib)
- Test file: `tests/test_governance_registry.py` (400 lines)

---

#### Task 1.2: Create Governance Types
**Acceptance Criteria:**
- [ ] GovernanceRule dataclass (YAML-mappable)
- [ ] GovernanceEvaluation dataclass (registry output)
- [ ] GovernanceViolation dataclass (per-rule result)
- [ ] Serializable to JSON (for audit logging)
- [ ] Unit tests: 30 serialization scenarios

**Implementation:**
- File: `src/infrastructure/governance_types.py` (100 lines)
- Test file: `tests/test_governance_types.py` (300 lines)

---

### Week 1 Day 2 (Tue 1/14) - Audit Infrastructure
**Time Budget:** 8 hours | **Tests Required:** 50

#### Task 2.1: Extract CortexAuditLogger (Tier 1)
**Acceptance Criteria:**
- [ ] CortexAuditLogger from `__backup/src/infrastructure/enhanced_audit_logger.py`
- [ ] AC-ID field mandatory (first-class)
- [ ] Hash chain integrity maintained
- [ ] SQLite backend configured
- [ ] Unit tests: All 1,862 assertions from original pass

**Implementation:**
- File: `src/infrastructure/cortex_audit_logger.py` (200 lines)
- Database: `cortex-brain/database/cortex-audit.db`
- Test file: `tests/test_cortex_audit_logger.py` (use original assertions)

---

#### Task 2.2: Create ApplicationLogger (Tier 2)
**Acceptance Criteria:**
- [ ] Python logging wrapper (stdlib compatible)
- [ ] No AC-ID field (not applicable)
- [ ] Pluggable backends (CloudWatch, file, etc.)
- [ ] <0.1ms latency (no hash chain)
- [ ] Unit tests: 10 backend scenarios

**Implementation:**
- File: `src/infrastructure/application_logger.py` (150 lines)
- Test file: `tests/test_application_logger.py` (200 lines)

---

#### Task 2.3: Create ComplianceAuditLogger (Tier 3)
**Acceptance Criteria:**
- [ ] Opt-in via CORTEX_COMPLIANCE_LOGGING env var
- [ ] Hash chain integrity (HIPAA/SOX requirement)
- [ ] Filtered events (deploy, review, test, merge, delete, access)
- [ ] 7-year retention policy
- [ ] Unit tests: 15 filtering scenarios

**Implementation:**
- File: `src/infrastructure/compliance_logger.py` (180 lines)
- Test file: `tests/test_compliance_logger.py` (250 lines)

---

#### Task 2.4: Create TieredAuditSystem (Router)
**Acceptance Criteria:**
- [ ] Unified interface: logger.cortex(), logger.info(), logger.compliance()
- [ ] Automatic routing based on context
- [ ] Cross-tier correlation via correlation_id
- [ ] Unit tests: All routing paths

**Implementation:**
- File: `src/infrastructure/tiered_audit_system.py` (120 lines)
- Test file: `tests/test_tiered_audit_system.py` (200 lines)

---

### Week 1 Day 3 (Wed 1/15) - State Management
**Time Budget:** 8 hours | **Tests Required:** 30

#### Task 3.1: Extract LifecycleManager
**Acceptance Criteria:**
- [ ] 7-state FSM (PENDING → RUNNING → PAUSED → COMPLETED/FAILED/CANCELLED)
- [ ] State transitions atomic (distributed lock)
- [ ] Callbacks on state enter/exit
- [ ] Cancel operation supported
- [ ] Unit tests: All transitions + locks

**Implementation:**
- File: `src/infrastructure/lifecycle_manager.py` (adapted from __backup/)
- Test file: `tests/test_lifecycle_manager.py` (400 lines, original coverage)

---

#### Task 3.2: Create ExecutionRequest / ExecutionResult Types
**Acceptance Criteria:**
- [ ] ExecutionRequest dataclass (correlation_id, operation, context)
- [ ] ExecutionResult dataclass (success, message, evidence)
- [ ] Serializable to JSON
- [ ] Unit tests: 20 serialization scenarios

**Implementation:**
- File: `src/infrastructure/execution_types.py` (100 lines)
- Test file: `tests/test_execution_types.py` (200 lines)

---

### Week 1 Day 4 (Thu 1/16) - Evidence & Progress
**Time Budget:** 8 hours | **Tests Required:** 25

#### Task 4.1: Extract EvidenceBundleStructure
**Acceptance Criteria:**
- [ ] EvidenceBundle dataclass (test_results, code_changes, audit_logs)
- [ ] Directory structure: cortex-brain/evidence/{ac_id}/
- [ ] Platform metadata captured (Windows/macOS/Linux)
- [ ] Serializable to JSON
- [ ] Unit tests: All bundle types

**Implementation:**
- File: `src/infrastructure/evidence_bundle_structure.py` (adapted)
- Test file: `tests/test_evidence_bundle.py` (250 lines)

---

#### Task 4.2: Extract ProgressTrackerManager
**Acceptance Criteria:**
- [ ] Tracks active epic and current phase
- [ ] Records AC-ID status (planned, implemented, tested)
- [ ] Percentage completion calculated
- [ ] YAML file format
- [ ] Unit tests: 287 operations from original

**Implementation:**
- File: `src/infrastructure/progress_tracker_manager.py` (adapted)
- Test file: `tests/test_progress_tracker.py` (use original tests)

---

### Week 1 Day 5 (Fri 1/17) - Integration & Validation
**Time Budget:** 8 hours | **Tests Required:** 50

#### Task 5.1: Integration Tests (All Tier 1 Systems)
**Acceptance Criteria:**
- [ ] All 5 systems work together
- [ ] Audit trail has chain integrity
- [ ] Governance violations logged
- [ ] Evidence captured
- [ ] Progress tracked
- [ ] Unit tests: 50 integration scenarios

**Implementation:**
- Test file: `tests/integration/test_tier1_integration.py` (500 lines)

---

#### Task 5.2: Production Readiness Validation
**Acceptance Criteria:**
- [ ] No CRITICAL risks remain (per prod-readiness-analysis.md)
- [ ] All Risk 1-7 have mitigations in place
- [ ] Code coverage ≥95% (critical path)
- [ ] Cross-platform validation (Windows + macOS)
- [ ] Performance targets met (<5ms governance, <0.1ms app logger)

**Validation:**
- Run all tests on Windows + macOS
- Measure performance (governance eval time, logging latency)
- Verify governance enforcement (try violating CORE-002, should block)

---

#### Task 5.3: Documentation
**Acceptance Criteria:**
- [ ] API documentation (docstrings)
- [ ] Architecture diagram
- [ ] Usage examples (how to use each tier)
- [ ] Troubleshooting guide

**Implementation:**
- Files: `docs/tier1-architecture.md`, `docs/logging-guide.md`

---

### Week 1 Success Criteria
- ✅ All 6 core systems implemented (Governance Registry, 3 Loggers, Router, Lifecycle Manager, Execution Types, Evidence, Progress Tracker)
- ✅ 100+ unit tests passing
- ✅ 95%+ code coverage (critical path)
- ✅ 0 CRITICAL production risks
- ✅ Cross-platform tested (Windows + macOS)
- ✅ Performance targets validated

**Gate:** User approval before Phase 2 (if any risks remain, fix before proceeding)

---

## Phase 2: Orchestration Core (Week 2) - Mon 1/20 to Fri 1/24

**Goal:** Implement orchestrator framework and MasterOrchestrator

**Deliverables:** Orchestrator framework, MasterOrchestrator, TodoManager, 4 core orchestrators, 100+ tests

---

### Week 2 Day 1 (Mon 1/20) - Orchestrator Framework
**Time Budget:** 8 hours | **Tests Required:** 30

#### Task 1.1: Create BaseOrchestrator Interface
**Acceptance Criteria:**
- [ ] Abstract base class with execute(), can_handle(), delegate()
- [ ] OrchestratorMetadata dataclass
- [ ] OrchestratorState enum (PENDING, RUNNING, COMPLETED, etc.)
- [ ] Child orchestrator support
- [ ] Unit tests: All lifecycle states

**Implementation:**
- File: `src/orchestrators/base/base_orchestrator.py` (150 lines)
- Test file: `tests/test_base_orchestrator.py` (300 lines)

---

#### Task 1.2: Create OrchestratorRegistry (Plugin System)
**Acceptance Criteria:**
- [ ] Register orchestrators by name
- [ ] Auto-discovery from custom/ directory
- [ ] Look up orchestrator by can_handle() predicate
- [ ] Dependency resolution
- [ ] Unit tests: Registration, lookup, discovery

**Implementation:**
- File: `src/orchestrators/base/orchestrator_registry.py` (200 lines)
- Test file: `tests/test_orchestrator_registry.py` (350 lines)

---

### Week 2 Day 2 (Tue 1/21) - MasterOrchestrator
**Time Budget:** 8 hours | **Tests Required:** 40

#### Task 2.1: Create MasterOrchestrator
**Acceptance Criteria:**
- [ ] Root orchestrator (composite pattern)
- [ ] Loads GovernanceRegistry at startup
- [ ] Calls governance.evaluate() pre/post execution
- [ ] Delegates to child orchestrators
- [ ] Handles exceptions (no cascade failures)
- [ ] Auto-logs operations to audit trail
- [ ] Unit tests: 40 execution scenarios

**Implementation:**
- File: `src/orchestrators/core/master_orchestrator.py` (300 lines)
- Test file: `tests/test_master_orchestrator.py` (500 lines)

---

#### Task 2.2: Create TodoManager Orchestrator
**Acceptance Criteria:**
- [ ] Manages task queue (dependency ordering)
- [ ] Executes tasks sequentially
- [ ] Tracks progress (which AC-IDs done)
- [ ] Autonomous continuation (runs until phase complete)
- [ ] Unit tests: Queue ordering, progress tracking

**Implementation:**
- File: `src/orchestrators/core/todo_manager.py` (250 lines)
- Adapt from: `__backup/src/orchestrators/core/todo_manager.py`
- Test file: `tests/test_todo_manager.py` (400 lines)

---

### Week 2 Day 3 (Wed 1/22) - Core Orchestrators
**Time Budget:** 8 hours | **Tests Required:** 50

#### Task 3.1: Create TDD-Master Orchestrator
**Acceptance Criteria:**
- [ ] Orchestrates RED → GREEN → REFACTOR workflow
- [ ] Creates test file, implements code, refactors
- [ ] Evidence captured (test results, code diff)
- [ ] All tests must pass before completion
- [ ] Unit tests: RED/GREEN/REFACTOR states

**Implementation:**
- File: `src/orchestrators/domain/tdd_master.py` (250 lines)
- Test file: `tests/test_tdd_master.py` (400 lines)

---

#### Task 3.2: Create Planning Orchestrator
**Acceptance Criteria:**
- [ ] Generates implementation plan from intent
- [ ] Output: 5-10 step list with effort estimates
- [ ] Evidence: Plan document
- [ ] Unit tests: Various AC-ID types

**Implementation:**
- File: `src/orchestrators/domain/planning_orchestrator.py` (200 lines)
- Test file: `tests/test_planning_orchestrator.py` (300 lines)

---

#### Task 3.3: Create Governance Orchestrator
**Acceptance Criteria:**
- [ ] Evaluates operation against all rules
- [ ] Returns detailed violation list
- [ ] Produces audit log entry
- [ ] Unit tests: All rule violations

**Implementation:**
- File: `src/orchestrators/domain/governance_orchestrator.py` (150 lines)
- Test file: `tests/test_governance_orchestrator.py` (250 lines)

---

#### Task 3.4: Create Evidence Orchestrator
**Acceptance Criteria:**
- [ ] Captures test results
- [ ] Captures code changes
- [ ] Links to audit trail
- [ ] Bundles everything in evidence/{ac_id}/
- [ ] Unit tests: Bundle creation

**Implementation:**
- File: `src/orchestrators/domain/evidence_orchestrator.py` (150 lines)
- Test file: `tests/test_evidence_orchestrator.py` (250 lines)

---

### Week 2 Day 4 (Thu 1/23) - Custom Response Templates & Rendering
**Time Budget:** 8 hours | **Tests Required:** 40

#### Task 4.1: Create TemplateResolver (Custom Template System)
**Acceptance Criteria:**
- [ ] Load response templates from YAML files
- [ ] Validate schema (must match CORTEX 4.0 schema version 4.6.0)
- [ ] Implement fallback chain: custom → parent → standard
- [ ] Cache templates in memory (<5ms resolution time)
- [ ] Handle missing/invalid templates gracefully (fallback to standard)
- [ ] Unit tests: All fallback scenarios, schema validation, caching

**Implementation:**
- File: `src/orchestrators/response/template-resolver.py` (200 lines)
- Dependencies: yaml, pathlib, logging
- Test file: `tests/unit/test-template-resolver.py` (350 lines)
- Test coverage: Custom template, fallback chain, invalid schema, missing file

---

#### Task 4.2: Update ResponseRenderer for Custom Templates
**Acceptance Criteria:**
- [ ] ResponseRenderer calls TemplateResolver before rendering
- [ ] Supports custom sections defined in template
- [ ] Enforces mandatory header and executive summary (CORTEX 4.0)
- [ ] Custom fields substituted from ExecutionResult metadata
- [ ] Unit tests: Render success/error/partial with custom template

**Implementation:**
- File: `src/orchestrators/response/response-renderer.py` (updated, 250 lines)
- Dependencies: template-resolver, jinja2 (for template rendering)
- Test file: `tests/unit/test-response-renderer.py` (400 lines)
- Test coverage: All response types, custom sections, mandatory validation

---

#### Task 4.3: Create Template Registry (Auto-Discovery)
**Acceptance Criteria:**
- [ ] Auto-load all templates from tier2/response-templates/ at startup
- [ ] Register template for each orchestrator
- [ ] Detect missing/invalid templates at startup (log, don't crash)
- [ ] Provide template introspection API: get_template(orchestrator_name)
- [ ] Unit tests: Discovery, validation, retrieval

**Implementation:**
- File: `src/orchestrators/registry/template-registry.py` (200 lines)
- Test file: `tests/unit/test-template-registry.py` (300 lines)
- Startup integration: Called from MasterOrchestrator.__init__()

---

#### Task 4.4: Integrate Custom Templates into BaseOrchestrator
**Acceptance Criteria:**
- [ ] OrchestratorMetadata extended with custom_template: CustomTemplateConfig
- [ ] CustomTemplateConfig: enabled, path, schema_version, fallback_on_error
- [ ] BaseOrchestrator.get_metadata() includes custom_template
- [ ] render_response() uses TemplateResolver
- [ ] Child orchestrators inherit parent template (if not explicitly overridden)
- [ ] Unit tests: Metadata, template resolution, inheritance

**Implementation:**
- File: `src/orchestrators/core/base-orchestrator.py` (updated, 200 lines)
- Test file: `tests/unit/test-base-orchestrator.py` (updated, 400 lines)
- Test coverage: Template resolution, inheritance, fallback

---

### Week 2 Day 5 (Fri 1/24) - MCP Integration & Validation
**Time Budget:** 8 hours | **Tests Required:** 40

#### Task 5.1: Create MCP Tool Decorators
**Acceptance Criteria:**
- [ ] @mcp_tool decorator for tool registration
- [ ] Schema validation (input type checking)
- [ ] Sandbox execution (timeout, memory limits)
- [ ] Error wrapping (exceptions → error response)
- [ ] Unit tests: Decorator behavior

**Implementation:**
- File: `src/mcp/mcp_decorator.py` (150 lines)
- Test file: `tests/test_mcp_decorator.py` (300 lines)

---

#### Task 5.2: Create Audit Tools (MCP)
**Acceptance Criteria:**
- [ ] audit_query(filter, correlation_id) - Query audit log
- [ ] audit_export(format) - Export logs as JSON/CSV
- [ ] audit_verify_chain(start, end) - Verify hash chain integrity
- [ ] Unit tests: All 3 tools

**Implementation:**
- File: `src/mcp/audit_tools.py` (200 lines)
- Test file: `tests/test_audit_tools.py` (300 lines)

---

#### Task 5.3: Create Governance Tools (MCP)
**Acceptance Criteria:**
- [ ] governance_evaluate(rules, context) - Evaluate rules
- [ ] governance_status() - Show loaded rules + violations
- [ ] governance_add_rule(yaml) - Add rule to registry
- [ ] Unit tests: All 3 tools

**Implementation:**
- File: `src/mcp/governance_tools.py` (200 lines)
- Test file: `tests/test_governance_tools.py` (300 lines)

---

#### Task 5.4: Integration Tests (Phase 2)
**Acceptance Criteria:**
- [ ] End-to-end orchestrator execution
- [ ] Governance blocking violated operations
- [ ] Evidence captured
- [ ] MCP tools callable
- [ ] Integration tests: 50+ scenarios

**Implementation:**
- Test file: `tests/integration/test_phase2_integration.py` (600 lines)

---

### Week 2 Success Criteria
- ✅ All orchestrator framework implemented
- ✅ MasterOrchestrator + 4 core orchestrators working
- ✅ MCP tools callable
- ✅ 100+ tests passing (phase 1 + 2)
- ✅ 95%+ code coverage
- ✅ All HIGH risks from prod-readiness analysis in progress of mitigation

**Gate:** User approval before Phase 3

---

## Phase 3: Safety & Scalability (Week 3) - Mon 1/27 to Fri 1/31

**Goal:** Address production risks and add observability

**Deliverables:** Distributed lock, circuit breaker, exception isolation, OpenTelemetry, 50+ tests

---

### Week 3 Day 1 (Mon 1/27) - Distributed Lock & Circuit Breaker
**Time Budget:** 8 hours | **Tests Required:** 25

#### Task 1.1: Implement Distributed Lock (Fix Risk 2 & 7)
**Acceptance Criteria:**
- [ ] SQLite EXCLUSIVE lock during state transitions
- [ ] Timeout: 30s max (fail if locked > 30s)
- [ ] Atomic compare-and-swap (UPDATE WHERE)
- [ ] Unit tests: Concurrent transitions (10 threads)

**Implementation:**
- File: `src/infrastructure/distributed_lock.py` (150 lines)
- Test file: `tests/test_distributed_lock.py` (300 lines)

---

#### Task 1.2: Implement Circuit Breaker (Fix Risk 3)
**Acceptance Criteria:**
- [ ] Circuit states: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing)
- [ ] Fail fast after 3 failures
- [ ] Retry backoff: exponential (1s → 2s → 4s)
- [ ] Unit tests: State transitions, backoff

**Implementation:**
- File: `src/infrastructure/circuit_breaker.py` (150 lines)
- Test file: `tests/test_circuit_breaker.py` (300 lines)

---

### Week 3 Day 2 (Tue 1/28) - Exception Isolation & Graceful Degradation
**Time Budget:** 8 hours | **Tests Required:** 30

#### Task 2.1: Process Sandboxing for Custom Orchestrators (Fix Risk 5)
**Acceptance Criteria:**
- [ ] Custom orchestrators run in separate process
- [ ] Exception in child doesn't crash parent
- [ ] Communication via IPC (queue)
- [ ] Timeout: 30s max per orchestrator
- [ ] Unit tests: Exception handling

**Implementation:**
- File: `src/orchestrators/base/sandbox.py` (200 lines)
- Test file: `tests/test_sandbox.py` (300 lines)

---

#### Task 2.2: Graceful Degradation Mode (Fix Risk 3)
**Acceptance Criteria:**
- [ ] If orchestrator fails, skip it and continue
- [ ] Mark operation as "partial" in response
- [ ] Log what was skipped and why
- [ ] Continue with remaining orchestrators
- [ ] Unit tests: All failure scenarios

**Implementation:**
- File: `src/orchestrators/core/graceful_degradation.py` (150 lines)
- Test file: `tests/test_graceful_degradation.py` (300 lines)

---

### Week 3 Day 3 (Wed 1/29) - Observability & Monitoring
**Time Budget:** 8 hours | **Tests Required:** 25

#### Task 3.1: OpenTelemetry Instrumentation
**Acceptance Criteria:**
- [ ] Governance evaluation timing
- [ ] Orchestrator execution tracing
- [ ] State transition latency
- [ ] MCP tool invocation timing
- [ ] Unit tests: All spans exported

**Implementation:**
- File: `src/observability/otel_instrumentation.py` (200 lines)
- Test file: `tests/test_otel_instrumentation.py` (300 lines)

---

#### Task 3.2: Governance Consistency Monitor (Fix Risk 1)
**Acceptance Criteria:**
- [ ] Heartbeat: every 60s, publish governance hash
- [ ] Detect divergence across instances
- [ ] Alert if rule versions differ
- [ ] Unit tests: Consistency detection

**Implementation:**
- File: `src/observability/governance_monitor.py` (150 lines)
- Test file: `tests/test_governance_monitor.py` (250 lines)

---

#### Task 3.3: Audit Trail Integrity Monitor (Fix Risk 2)
**Acceptance Criteria:**
- [ ] Periodic check: every 1h, traverse hash chain end-to-end
- [ ] Alert if gap detected
- [ ] Validate all hashes match
- [ ] Unit tests: Gap detection

**Implementation:**
- File: `src/observability/audit_integrity_monitor.py` (150 lines)
- Test file: `tests/test_audit_integrity_monitor.py` (250 lines)

---

### Week 3 Day 4 (Thu 1/30) - Secret Detection & PII Masking
**Time Budget:** 8 hours | **Tests Required:** 25

#### Task 4.1: Secret Detection & Redaction (Fix Risk 6)
**Acceptance Criteria:**
- [ ] Scan all log payloads for secret patterns (API key prefixes, etc.)
- [ ] Redact credit cards (XXXX-XXXX-XXXX-1234 format)
- [ ] Redact API keys (sk_live_... → sk_live_****)
- [ ] Unit tests: 20 secret patterns

**Implementation:**
- File: `src/infrastructure/secret_detector.py` (150 lines)
- Test file: `tests/test_secret_detector.py` (300 lines)

---

#### Task 4.2: Integrated Secret Masking
**Acceptance Criteria:**
- [ ] CortexAuditLogger masks secrets before writing
- [ ] ComplianceAuditLogger masks secrets before writing
- [ ] ApplicationLogger allows opt-in masking
- [ ] Unit tests: Integration scenarios

**Implementation:**
- Update files: `src/infrastructure/cortex_audit_logger.py`, `src/infrastructure/compliance_logger.py`
- Test file: `tests/test_secret_masking_integration.py` (250 lines)

---

### Week 3 Day 5 (Fri 1/31) - Validation & Chaos Testing
**Time Budget:** 8 hours | **Tests Required:** 50

#### Task 5.1: Chaos Tests (Kill Random Components)
**Acceptance Criteria:**
- [ ] Kill governance registry, verify graceful degradation
- [ ] Kill audit database, verify error handling
- [ ] Kill orchestrator mid-execution, verify recovery
- [ ] Concurrent state transitions, verify no races
- [ ] Unit tests: 10+ chaos scenarios

**Implementation:**
- Test file: `tests/chaos/test_chaos_scenarios.py` (500 lines)

---

#### Task 5.2: Production Readiness Re-Assessment
**Acceptance Criteria:**
- [ ] All CRITICAL risks mitigated
- [ ] All HIGH risks in progress/mitigated
- [ ] Performance targets met
- [ ] Code coverage ≥95%
- [ ] Cross-platform tested

**Validation:**
- Re-run all tests on Windows + macOS
- Measure timing (governance, circuit breaker, sandbox overhead)
- Verify no regressions from Phase 2

---

### Week 3 Success Criteria
- ✅ Distributed lock prevents race conditions
- ✅ Circuit breaker prevents cascades
- ✅ Custom orchestrators isolated (sandboxed)
- ✅ Graceful degradation working
- ✅ OpenTelemetry instrumentation complete
- ✅ Governance/audit monitors active
- ✅ Secrets masked in all loggers
- ✅ All CRITICAL & HIGH risks mitigated
- ✅ Chaos tests pass (random failure scenarios)

**Gate:** User approval before Phase 4

---

## Phase 3.5: Folder Structure Migration (Mid-Week 2 → End of Week 3) - Parallel Track

**Goal:** Reorganize source code into clean nested structure while maintaining development continuity

**Deliverables:** All files migrated, imports updated, SSOT consolidated, 18 root files deleted

**Critical:** This is a PARALLEL track that can be done incrementally without blocking Phase 2-3

---

### Migration Task 1: Pre-Migration Validation (Mon 1/20)
**Time Budget:** 1 hour

**Acceptance Criteria:**
- [ ] Create feature branch: `git checkout -b feat/folder-restructure`
- [ ] Backup all code (git commit)
- [ ] List all files to be moved (dry-run)
- [ ] Identify all imports that need updating
- [ ] Document any dependencies

**Execution:**
- `git status` (clean)
- `find src -name "*.py" \| wc -l` (count files)
- `grep -r "from src\." tests/ \| wc -l` (count imports to update)

---

### Migration Task 2: Create Directory Structure (Tue 1/21)
**Time Budget:** 1 hour

**Acceptance Criteria:**
- [ ] All directories created (Phase 1 Pre-Tasks already done)
- [ ] No file moves yet
- [ ] Verify structure matches folder-structure-design.md
- [ ] Backup new structure in git

**Execution:**
- See folder-structure-design.md Part 3.1 for mkdir commands
- Run: `tree cortex-brain/`, `tree src/`, `tree tests/` (verify structure)
- `git add .` (stage empty directories with .gitkeep)

---

### Migration Task 3: Migrate Files by Category (Wed 1/22 - Fri 1/24)
**Time Budget:** 6 hours total (1-2 hours per category, parallel with Phase 2)

**Category 1: Response Templates (Wed 1/22, 30 min)**
- Move: cortex-brain/response-templates-v4.yaml → tier2/response-templates/_schema/standard-schema.yaml
- Create: tier2/response-templates/core/*.yaml (from custom-response-templates.md)
- Verify: No YAML syntax errors
- Commit: "chore(templates): move response templates to tier2"

**Category 2: Orchestrator Files (Wed 1/22 - 1/23, 2 hours)**
- Move: src/orchestrators/master.py → src/orchestrators/core/master-orchestrator.py
- Move: src/orchestrators/tdd/ files → src/orchestrators/core/tdd-master-orchestrator.py
- Move: src/orchestrators/planning/ → src/orchestrators/core/planning-orchestrator.py
- Move: src/orchestrators/ado/ → src/orchestrators/domain/ado-orchestrator.py
- Move: src/orchestrators/vacuum/ → src/orchestrators/domain/vacuum-orchestrator.py
- Commit: "chore(orchestrators): reorganize into core/domain/custom"

**Category 3: Infrastructure Files (Thu 1/23, 1 hour)**
- Move: src/infrastructure/audit-*.py → src/infrastructure/audit-logger/
- Move: src/infrastructure/governance-*.py → src/infrastructure/governance/
- Move: src/infrastructure/state-*.py → src/infrastructure/state/
- Move: src/infrastructure/execution-*.py → src/infrastructure/execution/
- Commit: "chore(infrastructure): organize by subdomain"

**Category 4: Test Files (Thu 1/23 - Fri 1/24, 1 hour)**
- Move: tests/test-*.py → tests/unit/test-*.py
- Move: tests/integration-*.py → tests/integration/
- Move: tests/fixtures/*.py → tests/fixtures/
- Commit: "chore(tests): organize by layer"

**Category 5: Scripts (Fri 1/24, 30 min)**
- Move: scripts/admin-*.py → scripts/admin/
- Move: scripts/gen-*.py → scripts/generate/
- Move: scripts/*.sh → scripts/tools/
- Commit: "chore(scripts): organize by purpose"

---

### Migration Task 4: Update All Imports (Fri 1/24 - Mon 1/27)
**Time Budget:** 4 hours

**Acceptance Criteria:**
- [ ] All Python imports point to new paths
- [ ] No "module not found" errors
- [ ] All tests still pass
- [ ] No circular imports

**Execution (Batch by Category):**

**Batch 1: Orchestrator Imports** (Fri 1/24, 1 hour)
```
Find: grep -r "from src\.orchestrators\.master" src/ tests/
Replace: from src.orchestrators.core.master_orchestrator
Similar for: tdd_master, planning, ado, vacuum, etc.
Test: python -m pytest tests/ -q --co (check imports load)
Commit: "refactor(imports): update orchestrator imports"
```

**Batch 2: Infrastructure Imports** (Sat 1/25, 1 hour)
```
Find: grep -r "from src\.infrastructure\.audit" src/ tests/
Replace: from src.infrastructure.audit_logger.logger (or appropriate submodule)
Similar for: governance, state, execution, etc.
Test: python -m pytest tests/ -q --co
Commit: "refactor(imports): update infrastructure imports"
```

**Batch 3: Test Imports** (Sun 1/26, 1 hour)
```
Find: grep -r "from tests\." tests/
Replace: Adjust based on new structure
Test: python -m pytest tests/ -q --co
Commit: "refactor(imports): update test imports"
```

**Batch 4: Validation** (Mon 1/27, 1 hour)
```
Run: python -m pytest tests/unit/ -v (all unit tests)
Run: python -m pytest tests/integration/ -v (all integration tests)
Verify: No import errors, all tests still pass
Commit: "refactor(imports): validate all imports working"
```

---

### Migration Task 5: SSOT Documentation Consolidation (Mon 1/27 - Tue 1/28)
**Time Budget:** 2 hours

**Acceptance Criteria:**
- [ ] All decision/analysis from SSOT/ root files verified in roadmap/
- [ ] 18 root files ready for deletion
- [ ] roadmap/ folder is now SSOT
- [ ] quick-reference.md, README.md, DOCUMENT-INDEX.md kept as reference

**Verification:**
- Read: Each SSOT root file
- Verify: Content consolidated in roadmap/ files
- Checklist: 00-START-HERE.md → covered in framework-arch-spec.md
- Checklist: cortex7-arch-decisions.md → covered in consolidated-requirements.md + framework-arch-spec.md
- Checklist: All 18 files accounted for

**Commit:** "docs(SSOT): verify all consolidation complete"

---

### Migration Task 6: Delete Consolidated SSOT Root Files (Tue 1/28)
**Time Budget:** 30 minutes

**Acceptance Criteria:**
- [ ] 18 root files deleted (listed below)
- [ ] 3 reference files kept (quick-reference.md, README.md, DOCUMENT-INDEX.md)
- [ ] roadmap/ is now the primary documentation folder
- [ ] Git diff shows clean deletion (no accidental changes)

**Delete These 18 Files:**
1. SSOT/00-START-HERE.md
2. SSOT/anti-breakage-executive-summary.md
3. SSOT/before-and-after.md
4. SSOT/cortex7-arch-decisions.md
5. SSOT/CORTEX7-DOR-ASSESSMENT.md
6. SSOT/cortex7-governance-spec.md
7. SSOT/cortex7-ssot-reqs.yaml
8. SSOT/executive-summary.md
9. SSOT/findings-and-design-decision.md
10. SSOT/governance-registry-implementation.md
11. SSOT/governance-rule-evaluation.md
12. SSOT/governance-wiring-solution.md
13. SSOT/SOLUTION-COMPLETE.md
14. SSOT/what-prevents-breakage.md
15. SSOT/safety-executive-summary.md

**Keep These 3 Files (Reference):**
- SSOT/quick-reference.md
- SSOT/README.md
- SSOT/DOCUMENT-INDEX.md

**Execution:**
```powershell
Remove-Item SSOT\00-START-HERE.md
Remove-Item SSOT\anti-breakage-executive-summary.md
# ... (repeat for all 15 files)

# Verify
Get-ChildItem SSOT\*.md  # Should show only 3 files
git status  # Should show 15 deletions
git add SSOT/
git commit -m "docs(SSOT): delete consolidated root files, roadmap/ now primary"
```

---

### Migration Task 7: Final Validation & Cleanup (Tue 1/28 - Wed 1/29)
**Time Budget:** 2 hours

**Acceptance Criteria:**
- [ ] All tests passing (unit, integration, platform)
- [ ] Code coverage ≥95%
- [ ] No import errors
- [ ] Git history clean (one commit per category + consolidation + cleanup)
- [ ] No unintended files deleted
- [ ] Cross-platform tested (Windows + macOS)

**Execution:**
```bash
# Run all tests
python -m pytest tests/ -v --cov=src/

# Check for broken imports
python -m py_compile src/**/*.py

# Validate git log
git log --oneline feat/folder-restructure | head -10

# Verify structure
tree src/ -L 3
tree cortex-brain/ -L 3
tree SSOT/ -L 2
```

---

### Migration Task 8: Merge & Close (Wed 1/29)
**Time Budget:** 30 minutes

**Acceptance Criteria:**
- [ ] Feature branch ready for merge
- [ ] Pull request created with description
- [ ] User review + approval
- [ ] Merged to main (CORTEX6)

**Execution:**
```bash
git push origin feat/folder-restructure
# Create PR on GitHub

# After approval:
git checkout main
git merge feat/folder-restructure
git push origin main
```

---

### Migration Success Criteria
- ✅ All directories created and organized
- ✅ All files migrated to new locations
- ✅ All imports updated and working
- ✅ All tests passing (500+)
- ✅ Code coverage ≥95%
- ✅ Cross-platform tested
- ✅ 18 SSOT root files deleted
- ✅ roadmap/ is now the primary documentation
- ✅ Git log shows clean incremental commits
- ✅ No files lost (checksum verification)

**Note:** This migration is a PARALLEL track. It doesn't block Phase 2-4 implementation. Can be done incrementally alongside other phases. Tests should be updated as files are migrated to avoid breaking anything.

---

## Phase 4: Production Hardening (Week 4) - Mon 2/3 to Fri 2/7

**Goal:** Docker deployment, health checks, monitoring, load testing

**Deliverables:** Docker setup, health check endpoint, monitoring dashboards, 50+ load tests

---

### Week 4 Day 1 (Mon 2/3) - Docker Deployment
**Time Budget:** 8 hours | **Tests Required:** 15

#### Task 1.1: Create Dockerfile & docker-compose.yml
**Acceptance Criteria:**
- [ ] Dockerfile builds image in <5 minutes
- [ ] docker-compose.yml includes app + SQLite + Redis (cache)
- [ ] Volumes mounted for persistence
- [ ] Environment variables configured (CORTEX_AUDIT_MODE, etc.)
- [ ] Health check endpoint defined
- [ ] Unit tests: Image builds, containers start

**Implementation:**
- Files: `Dockerfile`, `docker-compose.yml`
- Test file: `tests/docker/test_docker_deployment.py` (200 lines)

---

#### Task 1.2: Create Init Script & Health Check
**Acceptance Criteria:**
- [ ] Init script validates governance loaded
- [ ] Init script verifies audit DB accessible
- [ ] Health check endpoint: GET /health
- [ ] Response includes component status
- [ ] Unit tests: Health check responses

**Implementation:**
- Files: `scripts/init.sh`, `src/api/health_check.py`
- Test file: `tests/test_health_check.py` (200 lines)

---

### Week 4 Day 2 (Tue 2/4) - Monitoring & Alerting
**Time Budget:** 8 hours | **Tests Required:** 20

#### Task 2.1: Create Prometheus Metrics
**Acceptance Criteria:**
- [ ] Governance evaluation time (histogram)
- [ ] Orchestrator execution time (histogram)
- [ ] Audit log write latency (histogram)
- [ ] Circuit breaker state (gauge)
- [ ] Active operations (gauge)
- [ ] Test file: Metric exports correct values

**Implementation:**
- File: `src/observability/prometheus_metrics.py` (200 lines)
- Test file: `tests/test_prometheus_metrics.py` (300 lines)

---

#### Task 2.2: Create Alerting Rules
**Acceptance Criteria:**
- [ ] Alert if governance evaluation > 5ms (P99)
- [ ] Alert if orchestrator timeout > 30s
- [ ] Alert if hash chain gap detected
- [ ] Alert if governance inconsistency detected
- [ ] Alert if circuit breaker OPEN > 5min
- [ ] Test file: Rules fire correctly

**Implementation:**
- File: `monitoring/alerting-rules.yaml`
- Test file: `tests/test_alerting_rules.py` (200 lines)

---

### Week 4 Day 3 (Wed 2/5) - Load Testing & Scalability
**Time Budget:** 8 hours | **Tests Required:** 30

#### Task 3.1: Load Tests (10-100 Concurrent Operations)
**Acceptance Criteria:**
- [ ] 10 concurrent ops: baseline performance
- [ ] 50 concurrent ops: measure lock contention
- [ ] 100 concurrent ops: observe degradation
- [ ] Measure: throughput, latency (P50/P99), errors
- [ ] Verify: no race conditions, no audit trail gaps
- [ ] Test file: Load test scenarios

**Implementation:**
- Test file: `tests/load/test_load_scenarios.py` (500 lines)
- Metrics: throughput (ops/sec), latency (ms), error rate (%)

---

#### Task 3.2: Scalability Assessment
**Acceptance Criteria:**
- [ ] Governance rules: <500 is safe, <1000 is breaking point
- [ ] Concurrent ops: <10 is safe, >100 is problematic
- [ ] Temporary KG: <100k nodes is safe, >500k is OOM
- [ ] Audit log: <10M entries is fast, >100M is slow
- [ ] Document limits and recommendations

**Implementation:**
- Report: `docs/scalability-assessment.md`
- Test data: Generate worst-case scenarios

---

### Week 4 Day 4 (Thu 2/6) - Cross-Platform & Final Testing
**Time Budget:** 8 hours | **Tests Required:** 40

#### Task 4.1: Windows-Specific Testing
**Acceptance Criteria:**
- [ ] Path handling (backslashes, drive letters)
- [ ] Line endings (CRLF normalization)
- [ ] Case sensitivity (audit hash matching)
- [ ] Process isolation (multiprocessing on Windows)
- [ ] All tests pass on Windows

**Implementation:**
- Test file: `tests/platform/test_windows.py` (300 lines)

---

#### Task 4.2: macOS-Specific Testing
**Acceptance Criteria:**
- [ ] Docker Desktop compatibility
- [ ] Volume mount permissions
- [ ] Process isolation (multiprocessing)
- [ ] All tests pass on macOS

**Implementation:**
- Test file: `tests/platform/test_macos.py` (200 lines)

---

#### Task 4.3: Final Integration & Regression
**Acceptance Criteria:**
- [ ] All tests passing (Unit: 200+, Integration: 50+, Load: 30+, Platform: 40+)
- [ ] Code coverage ≥95%
- [ ] Performance targets met
- [ ] No regressions from earlier phases
- [ ] Documentation complete

**Implementation:**
- Test suite: `tests/final_integration/test_regression.py` (600 lines)

---

### Week 4 Day 5 (Fri 2/7) - Release & Documentation
**Time Budget:** 8 hours

#### Task 5.1: Final Documentation
**Acceptance Criteria:**
- [ ] API documentation (all orchestrators, MCP tools)
- [ ] Architecture documentation (design decisions, diagrams)
- [ ] User guide (how to use CORTEX 7.0)
- [ ] Troubleshooting guide (common failures, recovery)
- [ ] Deployment guide (Docker, health checks, monitoring)
- [ ] Examples (reference implementations)

**Implementation:**
- Files: `docs/api-reference.md`, `docs/architecture.md`, `docs/user-guide.md`, etc.

---

#### Task 5.2: Release Checklist
- [ ] Code review complete (user approval)
- [ ] All tests passing
- [ ] Code coverage ≥95%
- [ ] Security scan (secrets, hardcoded paths)
- [ ] Performance validated
- [ ] Cross-platform tested
- [ ] Documentation complete
- [ ] Docker image built and tested
- [ ] Health checks validated
- [ ] Monitoring configured

**Gate:** Production Release

---

### Week 4 Success Criteria
- ✅ Docker deployment working (<5 minute setup)
- ✅ Health check endpoint operational
- ✅ Prometheus metrics exported
- ✅ Alerting rules configured
- ✅ Load tests completed (measure throughput/latency)
- ✅ Cross-platform tests pass
- ✅ Final integration tests pass
- ✅ Documentation complete
- ✅ Production-ready (DoR ≥ 95%)

---

## Week 5: Contingency & Polish (Mon 2/10 to Fri 2/14)

**Purpose:** Address remaining edge cases, performance tuning, documentation polish

**Capacity:** Available for:
- Bug fixes discovered in Phase 4
- Performance optimization (if P99 latency > targets)
- Additional documentation
- Buffer for unexpected issues

---

## Success Metrics (Overall)

| Metric | Target | Status |
|--------|--------|--------|
| **Code Coverage** | ≥95% (critical path) | TBD |
| **Test Pass Rate** | 98%+ | TBD |
| **Unit Tests** | >200 | TBD |
| **Integration Tests** | >50 | TBD |
| **Governance Evaluation** | <5ms (P99) | TBD |
| **Audit Logging** | <5ms (P99) | TBD |
| **Application Logging** | <0.1ms | TBD |
| **Orchestrator Timeout** | 30s max | TBD |
| **Concurrency Tests** | 100+ ops | TBD |
| **Cross-Platform** | Windows + macOS + Linux | TBD |
| **Docker Build** | <5 minutes | TBD |
| **Health Check** | All components operational | TBD |
| **Production Readiness** | DoR ≥ 95% | TBD |

---

## Risk Mitigation Timeline

| Risk | Week Addressed | Mitigation |
|------|---|---|
| **Governance staleness** | Week 3 | File watcher, distributed cache invalidation |
| **Hash chain concurrency** | Week 3 | Distributed lock, serializable isolation |
| **Partial failures** | Week 3 | Sagas pattern, graceful degradation |
| **KG memory** | Week 1 | Lazy loading, sampling, memory limits |
| **Plugin isolation** | Week 3 | Process sandboxing |
| **Secrets in logs** | Week 3 | Secret detection + redaction |
| **State manager races** | Week 3 | Distributed lock |
| **Observability gaps** | Week 3-4 | OpenTelemetry, monitors, alerting |

---

## Approval Gate Checklist

**Before Proceeding to Phase 2:**
- [ ] Phase 1 code reviewed by user
- [ ] Phase 1 tests passing (100%)
- [ ] Phase 1 code coverage ≥95%
- [ ] No CRITICAL risks remain
- [ ] Documentation reviewed

**Before Proceeding to Phase 3:**
- [ ] Phase 2 code reviewed
- [ ] Phase 2 tests passing (100%)
- [ ] Phase 2 code coverage ≥95%
- [ ] No HIGH risks remain
- [ ] Integration tests successful

**Before Proceeding to Phase 4:**
- [ ] Phase 3 chaos tests pass
- [ ] Production readiness re-assessed
- [ ] All risk mitigations validated
- [ ] Code coverage maintained ≥95%

**Before Production Release:**
- [ ] Phase 4 load tests pass
- [ ] Cross-platform tests pass
- [ ] Docker deployment validated
- [ ] Documentation complete
- [ ] DoR ≥ 95%

---

## Summary

**Total Duration:** 5 weeks (4 weeks core + 1 week contingency)  
**Total Tests:** 500+ (unit + integration + load + chaos + platform)  
**Code Coverage:** ≥95% (critical path)  
**Team Size:** 1 (GitHub Copilot) + Code Review (User)  
**Status:** Ready for Kickoff (waiting for user approval to Phase 1)

