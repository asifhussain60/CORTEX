# Phase 5: Analysis Consolidation Work Document

**Date:** 2026-01-14  
**Status:** IN PROGRESS - Task A (Analysis)  
**Purpose:** Internal working document for consolidating all requirements holistically

---

## A1: SSOT/analysis Review Complete ✅

### Files in SSOT/analysis/reqs/ (9 files):
1. 00-consolidation-summary.md - Consolidation report (331 lines)
2. consolidated-requirements.md - Requirements index (510 lines) ✅ ANALYZED
3. custom-response-templates.md - AR-009 design (350+ lines)
4. folder-structure-design.md - AR-010 design (520+ lines)
5. framework-arch-spec.md - Technical spec (670+ lines)
6. implementation-roadmap.md - 5-week roadmap (1,350+ lines)
7. IMPLEMENTATION-SUMMARY.md - Phase 3 summary (337 lines)
8. prod-readiness-analysis.md - Risks/safety (400+ lines)
9. README.md - Navigation (355 lines)

### Total Consolidated Requirements from SSOT/roadmap:

#### Architecture Requirements (10 AR-IDs):
- AR-001: 3-Tier Governance Model
- AR-002: Business Rules SQLite Index Architecture
- AR-003: Declarative Auto-Wired Governance
- AR-004: Tiered Logging Architecture (3 tiers: CORTEX Internal, User App, Compliance)
- AR-005: Production Mode Control (env var: CORTEX_AUDIT_MODE)
- AR-006: Orchestrator Architecture (composite, strategy, plugin system)
- AR-007: MCP Integration Strategy (standard + custom tools)
- AR-008: Adaptation from CORTEX 6.0 (74% code reduction to 6.5K LOC)
- AR-009: Custom Response Templates (fallback chain: custom → parent → standard)
- AR-010: Nested Folder Organization (kebab-case, max 25 chars)

#### Functional Requirements (6 FR-IDs):
- FR-001: Audit-First Pattern (every operation captures audit context)
- FR-002: Governance Evaluation (pre/post execution)
- FR-003: State Management (7-state FSM)
- FR-004: Evidence Capture (test results, code changes, audit logs)
- FR-005: Intent Clarification (knowledge graph for disambiguation)
- FR-006: Autonomous Continuation (TodoManager execution loops)

#### Non-Functional Requirements (4 NFR-IDs):
- NFR-001: Performance (<5ms governance, <1ms SQLite query, <10ms state transition)
- NFR-002: Reliability (98% test pass rate, 95% uptime, graceful degradation)
- NFR-003: Security (secrets redacted, enforcement mandatory, HIPAA/SOX/PCI-DSS support)
- NFR-004: Observability (correlation_id tracing, orchestrator graphs, governance audit)

#### Core Governance Rules: 25 SKULL Rules
- From consolidated-requirements.md (referenced as CORE-001 through CORE-025, though specific titles need to be extracted)
- CORTEX CORE rules (immutable, enforcement via registry)
- Organized by category (TDD, governance, portability, documentation, etc.)

---

## A2: Hallucination Prevention Requirements

### Source Documents:
- __backup/cortex-brain/documents/execution-summaries/hallucination-prevention-integration-2026-01-13.md (302 lines) ✅ REVIEWED

### Extracted Enhancement AC-IDs (25 total):

#### Phase 2 WIN Machine (15 AC-IDs, +3.5 days → 17.5 days total):

**Input Validation (AC-VALIDATE-001 to AC-VALIDATE-010):**
- AC-VALIDATE-001: Intent canonicalization
- AC-VALIDATE-002: AC-ID existence check
- AC-VALIDATE-003: Evidence bundle pre-check
- AC-VALIDATE-004: Cross-reference coherence
- AC-VALIDATE-005: Semantic output validation
- AC-VALIDATE-006: AC-ID format validation
- AC-VALIDATE-007: Phase alignment enforcement
- AC-VALIDATE-008: Request contradiction detection
- AC-VALIDATE-009: Schema validation (requests match orchestrator input schema)
- AC-VALIDATE-010: Backward compatibility checks

**Health Metrics (AC-METRICS-001 to AC-METRICS-005):**
- AC-METRICS-001: Input validation success rate
- AC-METRICS-002: Semantic validation accuracy
- AC-METRICS-003: Cross-reference success rate
- AC-METRICS-004: Phase alignment enforcement rate
- AC-METRICS-005: Anomaly detection (triggers alerts on unusual patterns)

#### Phase 4 MAC Machine (10 AC-IDs, +5.25 days → 19.25 days total):

**Cross-File Coherence (AC-COHERENCE-001 to AC-COHERENCE-004):**
- AC-COHERENCE-001: File-to-file requirement coherence
- AC-COHERENCE-002: AC-ID naming consistency across files
- AC-COHERENCE-003: Reference validity (all references resolve)
- AC-COHERENCE-004: Contradiction detection (conflicting AC-IDs flagged)

**Provenance Tracking (AC-EXPLAIN-001 to AC-EXPLAIN-005):**
- AC-EXPLAIN-001: Requirement source tracking
- AC-EXPLAIN-002: Decision justification capture
- AC-EXPLAIN-003: Architecture decision rationale
- AC-EXPLAIN-004: Test coverage justification
- AC-EXPLAIN-005: Evidence bundle provenance

---

## A3: Brittleness Fix Requirements

### Source Documents:
- __backup/cortex-brain/documents/validation/brittleness-executive-briefing.md (122 lines) ✅ REVIEWED
- __backup/cortex-brain/documents/analysis/brittleness-fix-summary.md (292 lines) ✅ REVIEWED
- __backup/cortex-brain/documents/misc/brittleness-scorecard.md (510 lines) ✅ REVIEWED
- Additional: validate-prompt-brittleness.py, brittleness_ambiguity_validator.py, brittleness-review-2026-01-13.md, etc.

### Extracted Brittleness Problems & Solutions:

#### 4 CRITICAL Production Blockers (Phase 9.4, Day 0):
1. **Database Concurrency (Data Corruption Risk)**
   - Problem: SQLite journal mode = 'delete' (default) instead of WAL
   - Impact: Power failure during concurrent writes → silent data corruption
   - Solution: Enable WAL mode on startup (1 line: `conn.execute("PRAGMA journal_mode=WAL")`)
   - Prevention: AC-BRITTLE-001
   - Test: Verify governance.db has `-wal` and `-shm` files

2. **Audit Schema Missing (Evidence Validation Broken)**
   - Problem: "no such table: audit_logs" error in validator
   - Impact: 97% verification rate becomes 0%, evidence collection unusable
   - Solution: Create schema migration, auto-initialize on first connection
   - Prevention: AC-BRITTLE-002
   - Test: Query SELECT COUNT(*) FROM audit_logs (no error)

3. **Tracker Progress Broken (Phase Gates Unenforceable)**
   - Problem: progress-tracker.json shows 0/0 for all phases
   - Impact: Cannot determine actual progress, phase gates unenforceable
   - Solution: Rebuild from AC-INDEX using evidence validator --fix
   - Prevention: AC-BRITTLE-003
   - Test: Verify tracker.phases.*.completed_count > 0 (if phase has AC-IDs)

4. **Pytest Collection Warnings (Hidden Test Failures Risk)**
   - Problem: Dataclass naming (TestResult, TestExecutor) confuses pytest
   - Impact: Tests may be silently skipped, false confidence in coverage
   - Solution: Rename dataclasses to remove 'Test' prefix (3 renames, <5 min)
   - Prevention: AC-BRITTLE-004
   - Test: Run pytest --co -q, verify 0 warnings

#### 10 HIGH Priority Fixes (Phase 9.4 Week 1):
- AC-BRITTLE-005: Import brittleness (relative imports → absolute imports)
- AC-BRITTLE-006: Test collection brittleness
- AC-BRITTLE-007: Package path brittleness
- AC-BRITTLE-008: AC Completeness brittleness (11 missing AC implementations)
- AC-BRITTLE-009: Evidence generation brittleness
- AC-BRITTLE-010: Portability brittleness (0/100 cross-platform)
- AC-BRITTLE-011: State management brittleness
- AC-BRITTLE-012: Governance enforcement brittleness
- AC-BRITTLE-013: Test-AC linking brittleness
- AC-BRITTLE-014: Verification rate brittleness (0% → target 80%+)

### Import Brittleness Details:
- Relative imports assume incorrect package paths (../infrastructure/ when actually at src/infrastructure/)
- Created: scripts/validate_import_patterns.py
- Fixed: 8 import statements in src/orchestrators/core/master_orchestrator.py
- Test: 1498 tests now runnable (was 1476)
- Impact: Phase 4.5 integration testing unblocked

### Test Collection Brittleness Details:
- 11 of 46 test files fail to collect (24% failure rate)
- Syntax errors and missing modules
- AC-TEST-001/002: Implement AC-based discovery + execution system

### Brittleness Scorecard (Before Fixes):
```
Test Execution:          0/100  🔴 (11 of 46 files fail to collect)
AC Completeness:        67/100  🟠 (11 AC-IDs missing implementation)
Evidence Generation:     0/100  🔴 (cannot capture test results)
Portability:             0/100  🔴 (no cross-platform support)
State Management:       50/100  🟠 (7-state FSM exists but incomplete)
Governance Enforce:     40/100  🟠 (25 rules, only 10 active)
Test-AC Linking:        0/100  🔴 (tests not organized by AC-ID)
Verification Rate:      0/100  🔴 (no evidence bundle generation)
─────────────────────────────────
OVERALL:               27/100  🔴 CRITICAL
```

---

## A4: Requirement-to-Component Mapping

### Components Identified from framework-arch-spec.md:

#### Core Framework Components:
1. **BaseOrchestrator** - Base interface for all orchestrators
2. **MasterOrchestrator** - Root orchestrator, governance evaluation, state management
3. **OrchestratorRegistry** - Plugin discovery and registration
4. **TemplateResolver** - Custom template resolution with fallback chain
5. **ResponseRenderer** - Response rendering and formatting
6. **EnhancedAuditLogger** - Audit logging across 3 tiers (from CORTEX 6.0)
7. **LifecycleManager** - 7-state FSM state management (from CORTEX 6.0)
8. **ProgressTracker** - Phase and AC-ID progress tracking
9. **GovernanceRegistry** - Rule instantiation and enforcement
10. **EvidenceBundle** - Test results, code changes, audit logs packaging

#### Domain Components:
- TDD-Master Orchestrator
- Planning Orchestrator
- ADO Orchestrator (Azure DevOps integration)
- Investigation Orchestrator
- Governance Orchestrator
- Evidence Orchestrator
- Todo-Manager Orchestrator
- Vacuum Orchestrator
- Cleanup Orchestrator

#### Infrastructure Components:
- SQLite Governance Index (business rules indexing)
- Hash Chain Integrity (tamper-proof audit trail)
- Knowledge Graph (intent disambiguation)
- MCP Tool Integration (5 custom tools)

#### Response Template Components (AR-009):
- CustomTemplateConfig (OrchestratorMetadata extension)
- TemplateRegistry (auto-discovery of custom templates)
- TemplateResolver (fallback chain: custom → parent → standard)
- ResponseSchema (CORTEX 4.0 v4.6.0)
- ResponseRenderer (updated for custom sections)

#### Folder Organization Components (AR-010):
- cortex-brain/tier0/ (CORTEX CORE rules)
- cortex-brain/tier1/ (business rules, tracking, AC registry)
- cortex-brain/tier2/ (response templates, engineering practices)
- cortex-brain/tier3/ (knowledge patterns)
- src/orchestrators/ (core, domain, custom subdirectories)
- src/orchestrators/response/ (template rendering)
- src/orchestrators/registry/ (discovery)
- src/infrastructure/ (audit, governance, state, execution)
- tests/ (unit, integration, fixtures)
- scripts/ (admin, generate, tools)

---

## Summary: Total Requirements for SSOT

### By Category:
- **Architecture Decisions:** 10 (AR-001 through AR-010)
- **Functional Requirements:** 6 (FR-001 through FR-006)
- **Non-Functional Requirements:** 4 (NFR-001 through NFR-004)
- **Governance Rules:** 25 SKULL rules (CORE-001 through CORE-025)
- **Hallucination Prevention:** 25 AC-IDs (AC-VALIDATE-001 through AC-EXPLAIN-005)
- **Brittleness Fixes:** 14 AC-IDs (AC-BRITTLE-001 through AC-BRITTLE-014)
- **Total Identified:** 84 items

### By Status:
- **Approved:** 20 (10 AR + 6 FR + 4 NFR)
- **Governance:** 25 SKULL rules
- **Enhancement:** 25 hallucination prevention AC-IDs
- **Bug Fix:** 14 brittleness fix AC-IDs

### By Phase (from implementation-roadmap.md):
- **Week 1 Pre-Tasks:** Folder structure, template schema (4 hours)
- **Week 1 Days 1-5:** Foundation (governance, audit, state, evidence, progress)
- **Week 2 Days 1-3:** Orchestrator framework
- **Week 2 Day 4:** Custom templates (AR-009) + hallucination validation (AC-VALIDATE-001 to 010)
- **Week 3:** Safety and scalability
- **Week 4:** Production hardening
- **Phase 3.5:** Folder migration (parallel, non-blocking, 16 hours)
- **Phase 2 Enhancement:** Hallucination prevention (15 AC-IDs, +3.5 days)
- **Phase 4 Enhancement:** Coherence validation (10 AC-IDs, +5.25 days)

---

## Next: Phase B - YAML Document Creation

Ready to create:
1. roadmap.yaml (machine-readable SSOT with all 84 items)
2. roadmap.md (human-readable roadmap from YAML)

