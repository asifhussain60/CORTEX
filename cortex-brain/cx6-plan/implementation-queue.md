# CORTEX 6.0 Implementation Queue
**Status:** Phase 1.5 Complete (100%) | Phase 1 In Progress (64%)  
**Updated:** 2026-01-11T09:40:00Z  
**Next:** Implement remaining 12 Phase 1 AC-IDs for foundation completion

---

## Phase 1.5 (STS) ✅ COMPLETE
- **AC-STS-001 to AC-STS-003:** System Testing Suite implemented
- **Test Results:** 6/6 tests passing (100%)
- **Evidence:** All 5 test suites operational (governance, policy, routing, security, unicode)
- **Verification:** pytest execution 2026-01-11T09:35:00Z

---

## Phase 1 Remaining Work (12 AC-IDs)

### Priority 1: Hash Chain & Lifecycle (4 AC-IDs)
**These enable evidence generation and state tracking**

#### AC-AUDIT-007: Hash Chain Audit Trail
- **Purpose:** Cryptographic provenance for plan execution
- **Implementation:**
  - Add `hash` field to audit log entries (SHA-256 of previous entry)
  - Chain verification on log rotation
  - Tamper detection via hash mismatch
- **Files:**
  - `src/infrastructure/enhanced_audit_logger.py` (add `_compute_hash()`)
  - `tests/unit/audit/test_hash_chain.py`
- **Dependencies:** AC-AUDIT-001 (complete)
- **Estimated:** 2-3 hours

#### AC-LIFECYCLE-001: Planned State
- **Purpose:** Track AC-IDs before implementation starts
- **Implementation:**
  - Add `PLANNED` state to lifecycle enum
  - Update AC-INDEX schema to support `status: planned`
  - Progress tracker query for planned AC-IDs
- **Files:**
  - `src/orchestrators/core/lifecycle_manager.py` (new)
  - `tests/unit/orchestrators/test_lifecycle_manager.py`
- **Dependencies:** AC-STATE-001 (complete)
- **Estimated:** 1-2 hours

#### AC-LIFECYCLE-002: In Progress State
- **Purpose:** Track AC-IDs during active implementation
- **Implementation:**
  - Add `IN_PROGRESS` state to lifecycle enum
  - State transition validation (planned → in_progress → completed)
  - Duration tracking for in-progress AC-IDs
- **Files:**
  - Extend `src/orchestrators/core/lifecycle_manager.py`
  - `tests/unit/orchestrators/test_lifecycle_transitions.py`
- **Dependencies:** AC-LIFECYCLE-001
- **Estimated:** 1 hour

#### AC-LIFECYCLE-003: Completed State with Validation
- **Purpose:** Mark AC-IDs complete only when tests pass
- **Implementation:**
  - Add `COMPLETED` state with validation gate
  - Require evidence bundle + passing tests before completion
  - Automatic rollback if validation fails
- **Files:**
  - Extend `src/orchestrators/core/lifecycle_manager.py`
  - `tests/integration/orchestrators/test_lifecycle_validation.py`
- **Dependencies:** AC-LIFECYCLE-002, AC-EVIDENCE-001
- **Estimated:** 2 hours

---

### Priority 2: Evidence Bundles (3 AC-IDs)
**Enable proof of AC-ID completion**

#### AC-EVIDENCE-001: Evidence Bundle Schema
- **Purpose:** Standardized YAML schema for AC completion proof
- **Implementation:**
  - Define schema: ac_id, title, status, test_results, artifacts, validation_date
  - YAML validation with jsonschema
  - Template generation for new AC-IDs
- **Files:**
  - `src/tools/evidence_bundle_generator.py` (enhance)
  - `cortex-brain/tier0/schemas/evidence-bundle-schema.yaml` (new)
  - `tests/unit/tools/test_evidence_schema.py`
- **Dependencies:** AC-AUDIT-001
- **Estimated:** 2 hours

#### AC-EVIDENCE-002: Automatic Bundle Generation
- **Purpose:** Auto-generate evidence when tests pass
- **Implementation:**
  - Hook into test execution (pytest plugin)
  - Collect: test results, code coverage, file changes, duration
  - Write bundle to `cortex-brain/tier1/evidence-bundles/{AC-ID}/`
- **Files:**
  - Extend `src/tools/evidence_bundle_generator.py`
  - `tests/conftest.py` (add pytest hook)
- **Dependencies:** AC-EVIDENCE-001
- **Estimated:** 3 hours

#### AC-EVIDENCE-003: Bundle Validation
- **Purpose:** Verify evidence bundles are complete and valid
- **Implementation:**
  - Schema validation (AC-EVIDENCE-001)
  - File artifact existence checks
  - Test result verification (must have passes)
  - Timestamp recency check (< 7 days old)
- **Files:**
  - Extend `src/tools/evidence_bundle_generator.py` (add `validate_bundle()`)
  - `tests/unit/tools/test_evidence_validation.py`
- **Dependencies:** AC-EVIDENCE-001
- **Estimated:** 2 hours

---

### Priority 3: Partial Implementations (3 AC-IDs)
**Complete existing partial work**

#### AC-STATE-002: State Persistence Layer
- **Status:** PARTIAL - basic SQLite exists, needs transaction support
- **Remaining Work:**
  - Add transaction rollback for failed operations
  - Multi-process locking (concurrent safety)
  - State migration system for schema changes
- **Files:**
  - `src/infrastructure/state_manager.py` (enhance)
  - `tests/unit/infrastructure/test_state_transactions.py`
- **Estimated:** 3 hours

#### AC-ORCH-003: Orchestrator Discovery
- **Status:** PARTIAL - registry exists, needs dynamic loading
- **Remaining Work:**
  - Hot-reload orchestrators without restart
  - Dependency resolution (AC-ORCH-006 depends on AC-ORCH-001)
  - Version compatibility checking
- **Files:**
  - `src/orchestrators/core/orchestrator_registry.py` (enhance)
  - `tests/unit/orchestrators/test_orchestrator_discovery.py`
- **Estimated:** 2 hours

#### AC-ORCH-004: Orchestrator Lifecycle
- **Status:** PARTIAL - basic init/execute exists, needs health checks
- **Remaining Work:**
  - Health check endpoint (heartbeat, resource usage)
  - Graceful shutdown (complete in-flight requests)
  - Crash recovery (resume from last checkpoint)
- **Files:**
  - `src/orchestrators/base/base_orchestrator.py` (enhance)
  - `tests/unit/orchestrators/test_orchestrator_lifecycle.py`
- **Estimated:** 3 hours

---

### Priority 4: Orchestration Core (2 AC-IDs)
**MasterOrchestrator production readiness**

#### AC-ORCH-006: MasterOrchestrator as Central Controller
- **Status:** PARTIAL - routing works, needs governance integration
- **Remaining Work:**
  - Integrate GovernanceMerger (4-tier rule evaluation)
  - Request validation against SKULL rules before routing
  - Blocked operation handling (CORE-001, CORE-017 enforcement)
- **Files:**
  - `src/orchestrators/master_orchestrator.py` (enhance)
  - `tests/integration/orchestrators/test_master_governance.py`
- **Dependencies:** AC-GOV-001 to AC-GOV-005 (complete)
- **Estimated:** 4 hours

#### AC-ORCH-007: Governance Evaluation Pipeline
- **Purpose:** Evaluate every request against merged governance before execution
- **Implementation:**
  - Pre-execution governance checkpoint
  - Rule violation detection with reason codes
  - Audit logging of governance decisions
- **Files:**
  - `src/orchestrators/core/governance_pipeline.py` (new)
  - `tests/integration/orchestrators/test_governance_pipeline.py`
- **Dependencies:** AC-ORCH-006
- **Estimated:** 3 hours

---

## Implementation Order (Dependency-Aware)

1. **AC-EVIDENCE-001** (no dependencies) → 2 hours
2. **AC-LIFECYCLE-001** (depends on AC-STATE-001 ✓) → 1-2 hours
3. **AC-LIFECYCLE-002** (depends on AC-LIFECYCLE-001) → 1 hour
4. **AC-AUDIT-007** (depends on AC-AUDIT-001 ✓) → 2-3 hours
5. **AC-EVIDENCE-002** (depends on AC-EVIDENCE-001) → 3 hours
6. **AC-EVIDENCE-003** (depends on AC-EVIDENCE-001) → 2 hours
7. **AC-LIFECYCLE-003** (depends on AC-LIFECYCLE-002, AC-EVIDENCE-001) → 2 hours
8. **AC-STATE-002** (partial, no blockers) → 3 hours
9. **AC-ORCH-003** (partial, no blockers) → 2 hours
10. **AC-ORCH-004** (partial, no blockers) → 3 hours
11. **AC-ORCH-006** (depends on AC-GOV-* ✓) → 4 hours
12. **AC-ORCH-007** (depends on AC-ORCH-006) → 3 hours

**Total Estimated Time:** 28-30 hours (3.5-4 days at 8 hours/day)

---

## Success Criteria

### Phase 1 Complete (100%)
- ✅ All 33 AC-IDs implemented with passing tests
- ✅ Evidence bundles generated for all 33 AC-IDs
- ✅ Hash chain audit trail operational
- ✅ Lifecycle state tracking functional
- ✅ MasterOrchestrator governance integration complete

### Phase 2 Ready
- Phase 1 provides foundation (audit, governance, state, evidence)
- Phase 2 builds orchestration (TodoManager, Planning v5, Feature orchestrators)
- Snowball strategy: each phase builds on previous infrastructure

---

## Notes

- **Stub implementations cleared:** 13 AC-IDs (AC-SECURITY-*, AC-TEST-*, AC-CLEAN-*) marked as stub, not counted as complete
- **LLM integration:** Real implementation requires OpenAI or Anthropic API key for code generation
- **Manual implementation:** All 12 AC-IDs can be implemented manually using TDD cycle (RED→GREEN→REFACTOR)
- **Evidence requirement:** Each AC-ID completion requires evidence bundle with passing tests (AC-EVIDENCE-001 to 003)
