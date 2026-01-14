# CORTEX 7.0 Master Roadmap

**Date:** 2026-01-14  
**Version:** 1.0.0-DRAFT  
**Status:** APPROVED FOR IMPLEMENTATION  
**Total Requirements:** 84 (10 AR + 6 FR + 4 NFR + 25 SKULL rules + 39 enhancements/fixes)

---

## 📊 Quick Statistics

| Metric | Count | Status |
|--------|-------|--------|
| **Architecture Decisions** | 10 | ✅ APPROVED |
| **Functional Requirements** | 6 | ✅ APPROVED |
| **Non-Functional Requirements** | 4 | ✅ APPROVED |
| **Governance Rules (SKULL)** | 25 | 🔴 ENFORCED (15 active, 10 to wire) |
| **Hallucination Prevention** | 25 | 🟡 SCHEDULED (Phase 2+4) |
| **Brittleness Fixes** | 14 | 🟠 HIGH PRIORITY (Phase 9.4+10) |
| **Total Consolidated** | 84 | ✅ READY |

---

## 🎯 Executive Summary

CORTEX 7.0 builds on proven CORTEX 6.0 infrastructure with a **3-tier governance model**, **declarative auto-wired rules**, and **optional custom response templates**. The architecture eliminates brittleness through:

1. **Immutable Tier 0** - 25 CORTEX CORE SKULL rules that cannot be bypassed
2. **Mutable Tier 1** - Business rules in YAML with SQLite indexing for production performance
3. **Auto-Wired Governance** - GovernanceRegistry auto-instantiates enforcement at startup
4. **Hallucination Prevention** - Input validation, semantic checking, cross-file coherence
5. **Brittleness Prevention** - 14 targeted fixes for database, audit, tracking, testing issues

**Implementation Timeline:** 5 weeks + 2 parallel enhancements  
**Start Date:** 2026-01-15  
**Team:** Cross-platform (MAC + WIN) development

---

## 🏗️ Part 1: Architecture Decisions (10 AR-IDs)

### AR-001: 3-Tier Governance Model ✅
- **Status:** APPROVED (100% confidence)
- **Phase:** Week 1 Days 1-2
- **Effort:** 2 days
- **What:** Tier 0 (CORTEX CORE, 25 SKULL rules), Tier 1 (Business Rules, YAML + SQLite), Tier 2 (Engineering Standards)
- **Why:** Separates governance layers for scalability, compliance, and extension
- **Key Benefit:** Tier 0 never changes; Tier 1 mutable for business rules
- **Implementation:** GovernanceRegistry auto-instantiates from YAML

### AR-002: Business Rules SQLite Index Architecture ✅
- **Status:** APPROVED (95% confidence)
- **Phase:** Week 1 Days 1-2
- **Effort:** 1.5 days
- **What:** YAML files (human-readable) + SQLite index (high-performance queries)
- **Why:** Version-controllable source + production query speed
- **Performance:** <1ms per rule query, <100ms for all rules in category
- **Schema:** governance_rules table with rule_id, category, severity, domain, enforcement_trigger
- **Scalability:** Supports 10,000+ rules without bloat

### AR-003: Declarative Auto-Wired Governance ✅
- **Status:** APPROVED (100% confidence)
- **Phase:** Week 1 Days 1-3
- **Effort:** 2 days
- **What:** Rules in YAML with enforcement metadata; auto-instantiation via reflection
- **Why:** Eliminates manual wiring brittleness; "once configured, stays configured"
- **Key Guarantee:** New rule in YAML → auto-enforced on next startup
- **Portability:** git clone → enforcement active (no manual wiring needed)
- **Extensibility:** Adding new rule = YAML + middleware class (both auto-discovered)

### AR-004: Tiered Logging Architecture ✅
- **Status:** APPROVED (95% confidence)
- **Phase:** Week 1 Days 2-3
- **Effort:** 1.5 days
- **Three Logging Systems:**
  1. **Tier 1 (CORTEX Internal):** AC-ID tracking, 7-year retention, <5ms latency, SQLite + hash chain
  2. **Tier 2 (User Application):** General events, user-defined retention, <0.1ms latency, user backend (CloudWatch/file)
  3. **Tier 3 (Compliance Audit):** HIPAA/SOX/PCI-DSS events, 7-year retention, opt-in, <5ms latency
- **Key Feature:** Single import, three loggers auto-routed by event type
- **Security:** Automatic PII masking in all logs

### AR-005: Production Mode Control ✅
- **Status:** APPROVED (100% confidence)
- **Phase:** Week 1 Days 1-2
- **Effort:** 0.5 days
- **What:** CORTEX_AUDIT_MODE env var (development|production|hybrid) controls log verbosity
- **What It Doesn't Do:** Does NOT disable audit capture (AuditContext always active)
- **Guarantee:** Critical events (errors, violations, security) ALWAYS logged regardless of mode
- **Metadata:** operation, AC-ID, correlation_id, timestamp ALWAYS captured

### AR-006: Orchestrator Architecture ✅
- **Status:** APPROVED (95% confidence)
- **Phase:** Week 2 Days 1-3
- **Effort:** 2 days
- **Pattern:** Composite (parent-child tree) + Strategy (can_handle) + Chain of Responsibility
- **Plugin System:** Auto-discovery from custom/ directory; custom orchestrators in separate process
- **Error Handling:** Child exceptions caught at boundary; don't propagate to parent
- **Circular Dependency Detection:** Detected at startup (startup fails if cycle exists)

### AR-007: MCP Integration Strategy ✅
- **Status:** APPROVED (90% confidence)
- **Phase:** Week 2 Days 2-3
- **Effort:** 1.5 days
- **Standard Tools:** Filesystem, Git, SQLite (for common operations)
- **Custom Tools:** 5 CORTEX-specific tools (Audit, Governance, Orchestrator, Evidence, State)
- **Security:** Tool invocation sandboxed; no arbitrary code execution
- **Extensibility:** New tools registered via schema validation

### AR-008: Adaptation from CORTEX 6.0 ✅
- **Status:** APPROVED (95% confidence)
- **Phase:** Week 1 Days 1-2
- **Effort:** 1 day
- **Reuse:** EnhancedAuditLogger, LifecycleManager, ProgressTracker, HashChain, EvidenceBundle, 18 MCP tools
- **Remove:** response_header_footer_manager, brittleness_ambiguity_validator, 14+ unused orchestrators
- **Code Reduction:** 25K → 6.5K LOC (74% reduction)
- **Quality:** Maintain 98%+ test pass rate from CORTEX 6.0

### AR-009: Custom Response Templates (NEW) ✅
- **Status:** APPROVED (95% confidence)
- **Phase:** Week 2 Day 4
- **Effort:** 1.5 days
- **What:** Optional per-orchestrator custom templates; fallback chain (Custom → Parent → Standard)
- **Why:** Domain-specific formats without breaking consistency
- **Fallback Guarantee:** Standard template always available (no broken responses)
- **Inheritance:** Child orchestrators inherit parent template unless explicitly overridden
- **Performance:** <5ms cached template resolution

### AR-010: Nested Folder Organization (NEW) ✅
- **Status:** APPROVED (95% confidence)
- **Phase:** Week 1 Pre-Tasks + Phase 3.5 (parallel, non-blocking)
- **Effort:** 16 hours Phase 3.5 migration
- **Structure:**
  - `cortex-brain/` (tiers 0-3)
  - `src/orchestrators/` (core/, domain/, custom/, response/, registry/)
  - `src/infrastructure/` (audit, governance, state, execution)
  - `tests/` (unit/, integration/, fixtures/)
  - `scripts/` (admin/, generate/, tools/)
- **Naming:** Kebab-case, max 25 characters (e.g., `tdd-master-orchestrator.py`)
- **Cross-Platform:** pathlib.Path for all file operations (no hardcoded /Users/ or C:\\ paths)

---

## 🔄 Part 2: Functional Requirements (6 FR-IDs)

### FR-001: Audit-First Pattern ✅
- **Phase:** Week 1 Days 1-2
- **Requirement:** Every operation captures audit context BEFORE executing
- **Metadata Captured:** operation, AC-ID, correlation_id, timestamp
- **Storage:** SQLite + hash chain for tamper-proof trail
- **Guarantee:** No operation executes without audit entry
- **Performance:** <5ms audit capture latency
- **Mapped AC-IDs:** AC-AUDIT-001 through AC-AUDIT-006

### FR-002: Governance Evaluation ✅
- **Phase:** Week 1 Days 1-3
- **Requirement:** All operations evaluated against loaded ruleset before AND after execution
- **Pre-Execution:** Evaluate all Tier 0 + Tier 1 rules
- **Blocking:** Violations with severity='blocked' stop operation
- **Logging:** Violations logged; warnings allow execution
- **Performance:** <125ms for all Tier 0 rules (<5ms per rule)
- **Mapped AC-IDs:** AC-GOV-001 through AC-GOV-005

### FR-003: State Management ✅
- **Phase:** Week 1 Days 2-3
- **Requirement:** Orchestrator execution modeled as 7-state FSM
- **States:** PENDING → RUNNING → PAUSED → COMPLETED/FAILED/CANCELLED
- **Atomic Transitions:** Distributed lock prevents race conditions
- **Callbacks:** on_enter, on_exit fired for each state (diagnostics)
- **Performance:** <10ms state transition time
- **Mapped AC-IDs:** AC-LIFECYCLE-001 through AC-LIFECYCLE-003

### FR-004: Evidence Capture ✅
- **Phase:** Week 1 Days 4-5
- **Requirement:** Every AC-ID implementation captured with proof
- **Evidence Types:** Test results (pass/fail, coverage %), code changes (diffs, commits), audit logs
- **Storage:** cortex-brain/evidence/{ac_id}/ (tests/, code/, audit/ subdirectories)
- **Performance:** <500ms capture latency
- **Guarantee:** 100% of completed AC-IDs have evidence bundle
- **Mapped AC-IDs:** AC-EVIDENCE-001 through AC-EVIDENCE-003

### FR-005: Intent Clarification ✅
- **Phase:** Week 2 Days 3-4
- **Requirement:** Temporary knowledge graph for disambiguating intent
- **Timing:** Loaded on startup or on-demand
- **Performance:** <1 second per query, queries <100ms
- **Graceful Degradation:** Continues without intent clarity if KG fails
- **Lifecycle:** Auto-destroyed at operation end
- **Mapped AC-IDs:** AC-INTENT-001 (future)

### FR-006: Autonomous Continuation ✅
- **Phase:** Week 2 Days 2-3
- **Requirement:** TodoManager enables autonomous loops without user intervention
- **Pattern:** Plan → AC-ID 1 → AC-ID 2 → AC-ID 3 (user provides single command)
- **Audit Trail:** Each step logged with operation, AC-ID, result
- **Interruption:** User can cancel via cancel_flag
- **Performance:** <100ms between AC-ID steps
- **Mapped AC-IDs:** AC-TODO-001 through AC-TODO-004

---

## ⚙️ Part 3: Non-Functional Requirements (4 NFR-IDs)

### NFR-001: Performance 📊
- **Governance evaluation:** <5ms per rule, <125ms all Tier 0 (25 rules)
- **SQLite query:** <1ms per rule lookup (via B-tree index)
- **State transition:** <10ms (distributed lock timeout)
- **Evidence capture:** <500ms (async write to disk)
- **Audit logging:** <5ms (SQLite + hash chain)
- **Orchestrator timeout:** 30s hard limit (fail gracefully)
- **Measurement:** Performance tests for each operation; p50/<target, p95/<1.5x target, p99/<2x target
- **Dashboard:** Real-time latency monitoring

### NFR-002: Reliability 🛡️
- **Test pass rate:** ≥98% (from CORTEX 6.0 baseline)
- **Uptime target:** 95% during development
- **Graceful degradation:** Failed component doesn't stop others
- **No cascade failures:** One broken orchestrator doesn't crash parent
- **Error recovery:** Automatic retry with exponential backoff
- **Circuit breaker:** Failing services short-circuit after N errors
- **Failure handling:** 4 CRITICAL + 10 HIGH priority brittleness fixes identified

### NFR-003: Security 🔒
- **Secrets redacted:** PII masking automatic in all logs
- **Governance enforcement:** Mandatory (not optional); bypasses trigger alerts
- **SSOT Tier 0 immutable:** Write-protected at runtime (filesystem + code)
- **Hash chain integrity:** Verifiable end-to-end audit trail
- **Compliance support:** HIPAA/SOX/PCI-DSS via tiered logging
- **Key rotation:** Automatic secret rotation policy
- **Audit retention:** 7-year retention for compliance
- **Mapped AC-IDs:** AC-SECURITY-001 through AC-SECURITY-006

### NFR-004: Observability 👁️
- **Correlation IDs:** Unique per operation, traced throughout
- **Orchestrator graph:** Visualization of execution tree
- **Governance timing:** Each rule evaluated and timing recorded
- **Alerting:** Automated on governance inconsistency, slow rules, broken chains
- **OpenTelemetry:** Standard instrumentation for all components
- **Dashboard:** Real-time view of orchestrator executions
- **Tracing:** Full request/response trace available for each operation

---

## 🛡️ Part 4: Governance Rules (25 SKULL Rules - CORTEX CORE)

### Rules Overview

| Rule ID | Title | Severity | Category | Status |
|---------|-------|----------|----------|--------|
| CORE-001 | Incremental Execution | BLOCKED | Performance | ENFORCED |
| CORE-002 | No Summary Files | BLOCKED | Documentation | ENFORCED |
| CORE-005 | Path Portability | BLOCKED | Portability | ENFORCED |
| CORE-008 | TDD Enforcement | BLOCKED | Testing | ENFORCED |
| CORE-009 | Plan File Organization | BLOCKED | Organization | ENFORCED |
| CORE-017 | Governance Enforcement | BLOCKED | Governance | ENFORCED |
| CORE-019 | TDD-Master Required | BLOCKED | Testing | ENFORCED |
| CORE-010 | AC-ID Format Validation | WARNING | Quality | ENFORCED |
| CORE-011 | Governance Completeness | WARNING | Governance | ENFORCED |
| CORE-012 | Test Coverage Minimum | WARNING | Testing | ENFORCED |
| CORE-013 | Evidence Bundle Required | BLOCKED | Testing | ENFORCED |
| CORE-014 | Audit Trail Integrity | BLOCKED | Security | ENFORCED |
| CORE-015 | Secret Redaction | WARNING | Security | ENFORCED |
| CORE-016 | Cross-Platform Testing | WARNING | Portability | ENFORCED |
| CORE-018 | MCP Tool Schema | WARNING | Integration | ENFORCED |
| CORE-020 | Graceful Degradation | WARNING | Reliability | ENFORCED |
| CORE-021 | Performance SLA | WARNING | Performance | ENFORCED |
| CORE-022 | Governance Immutability | BLOCKED | Governance | ENFORCED |
| CORE-023 | AC-ID Uniqueness | BLOCKED | Quality | ENFORCED |
| CORE-024 | Audit Context Required | BLOCKED | Audit | ENFORCED |
| CORE-025 | Evidence Verification | WARNING | Quality | ENFORCED |

### Key Rules Explained

**CORE-001 (Incremental Execution):** Operations must be <500 lines per iteration. Prevents HTTP 502 token overflow.

**CORE-005 (Path Portability):** All file operations use pathlib.Path (no hardcoded /Users/ or C:\\ paths). Ensures cross-platform support.

**CORE-008 (TDD Enforcement):** All code must have tests. Untested code is blocked.

**CORE-017 (Governance Enforcement):** Bypassing governance rules triggers alert and blocks operation.

**CORE-019 (TDD-Master Required):** Direct coding without TDD is blocked (must use TDD-Master orchestrator).

**CORE-022 (Governance Immutability):** Tier 0 CORTEX CORE rules cannot be modified at runtime.

---

## 🧠 Part 5: Hallucination Prevention (25 AC-IDs)

### Phase 2 WIN Machine Enhancement (15 AC-IDs, +3.5 days)

**Input Validation (AC-VALIDATE-001 through AC-VALIDATE-010):** 10 AC-IDs
- AC-VALIDATE-001: Intent canonicalization (resolve ambiguous intent)
- AC-VALIDATE-002: AC-ID existence check (verify AC-IDs are real)
- AC-VALIDATE-003: Evidence bundle pre-check (validate structure)
- AC-VALIDATE-004: Cross-reference coherence (verify references resolve)
- AC-VALIDATE-005: Semantic output validation (ensure semantic correctness)
- AC-VALIDATE-006: AC-ID format validation (AC-{CATEGORY}-{NNN})
- AC-VALIDATE-007: Phase alignment enforcement (request AC matches current phase)
- AC-VALIDATE-008: Request contradiction detection (conflicting AC-IDs flagged)
- AC-VALIDATE-009: Schema validation (request matches orchestrator schema)
- AC-VALIDATE-010: Backward compatibility checks (version compatibility)

**Health Metrics (AC-METRICS-001 through AC-METRICS-005):** 5 AC-IDs
- AC-METRICS-001: Input validation success rate (% requests passing)
- AC-METRICS-002: Semantic validation accuracy (% semantically valid)
- AC-METRICS-003: Cross-reference success rate (% references resolving)
- AC-METRICS-004: Phase alignment rate (% phase-aligned requests)
- AC-METRICS-005: Anomaly detection (alerts on unusual patterns)

**Phase 2 Timeline:** Extends from 14 → 17.5 days

### Phase 4 MAC Machine Enhancement (10 AC-IDs, +5.25 days)

**Cross-File Coherence (AC-COHERENCE-001 through AC-COHERENCE-004):** 4 AC-IDs
- AC-COHERENCE-001: File-to-file requirement coherence (no conflicts)
- AC-COHERENCE-002: AC-ID naming consistency (same AC-ID consistent)
- AC-COHERENCE-003: Reference validity (all references resolve)
- AC-COHERENCE-004: Contradiction detection (conflicts flagged)

**Provenance Tracking (AC-EXPLAIN-001 through AC-EXPLAIN-005):** 5 AC-IDs
- AC-EXPLAIN-001: Requirement source tracking (origin of requirement)
- AC-EXPLAIN-002: Decision justification (why this decision)
- AC-EXPLAIN-003: Architecture rationale (why this architecture)
- AC-EXPLAIN-004: Test coverage justification (why this coverage)
- AC-EXPLAIN-005: Evidence bundle provenance (what supports this AC-ID)

**Phase 4 Timeline:** Extends from 14 → 19.25 days

---

## 🐛 Part 6: Brittleness Fixes (14 AC-IDs)

### 4 CRITICAL Production Blockers (Phase 9.4 Day 0 - 2 hours)

| Problem | Impact | Solution | Effort |
|---------|--------|----------|--------|
| **AC-BRITTLE-001:** SQLite journal mode = 'delete' | Data corruption risk | Enable WAL mode (1 line) | 15 min |
| **AC-BRITTLE-002:** Audit schema missing | Evidence validation broken | Create migration + auto-init | 45 min |
| **AC-BRITTLE-003:** Tracker progress 0/0 | Phase gates unenforceable | Rebuild from AC-INDEX | 30 min |
| **AC-BRITTLE-004:** Pytest warnings (6 warnings) | Hidden test failures | Rename dataclasses (3 renames) | 5 min |

**Gate:** All 4 complete = Production readiness restored, Phase 10 unblocked

### 10 HIGH Priority Fixes (Phase 9.4 Week 1 - 5 days)

- **AC-BRITTLE-005:** Import brittleness (relative → absolute imports) - 2 hours
- **AC-BRITTLE-006:** Test collection brittleness (11 broken files) - 3 hours
- **AC-BRITTLE-007:** Package path brittleness (path assumptions) - 2 hours
- **AC-BRITTLE-008:** AC completeness brittleness (11 missing implementations) - 5 days
- **AC-BRITTLE-009:** Evidence generation brittleness (0% implemented) - 3 days
- **AC-BRITTLE-010:** Portability brittleness (no cross-platform support) - 2 days
- **AC-BRITTLE-011:** State management brittleness (50% complete) - 1.5 days
- **AC-BRITTLE-012:** Governance enforcement brittleness (10/25 rules active) - 2 days
- **AC-BRITTLE-013:** Test-AC linking brittleness (0% tests organized by AC-ID) - 2 hours
- **AC-BRITTLE-014:** Verification rate brittleness (0% vs 80% target) - 2 days

---

## 📅 Implementation Timeline

### Week 1: Foundation (5 days + 4 pre-task hours)

| Day | Focus | Key Tasks | Duration |
|-----|-------|-----------|----------|
| **Pre** | Setup | Folder structure, template schema, template files | 4 hours |
| **Day 1** | Governance | AR-001: 3-Tier Model, AR-005: Production Mode, FR-001: Audit-First | 1 day |
| **Day 2** | SQLite & Logging | AR-002: SQLite Index, AR-003: Auto-Wiring, AR-004: Tiered Logging | 1 day |
| **Day 3** | State & Audit | FR-003: State Management, FR-001 continued | 1 day |
| **Day 4** | Evidence & Critical Fixes | FR-004: Evidence Capture, AC-BRITTLE-001-004 critical fixes | 1 day |
| **Day 5** | Automation | FR-006: Autonomous Continuation, AR-008: Adaptation | 1 day |

### Week 2: Orchestration Core (5 days)

| Day | Focus | Key Tasks | Duration |
|-----|-------|-----------|----------|
| **Day 1** | Framework | AR-006: Orchestrator Architecture | 1 day |
| **Day 2** | Integration | AR-007: MCP Integration, FR-006 continued | 1 day |
| **Day 3** | Registry | AR-006: Orchestrator Registry, FR-002: Governance Evaluation | 1 day |
| **Day 4** | Custom Templates | AR-009: Custom Response Templates, hallucination validation (Phase 2 WIN start) | 1 day |
| **Day 5** | Integration Testing | Week 1-2 AC-ID validation and testing | 1 day |

### Week 3: Safety & Observability (5 days)
- Error handling, graceful degradation
- OpenTelemetry instrumentation
- Dashboard implementation
- Alerting rules

### Week 4: Production Hardening (5 days)
- Secret redaction
- HIPAA/SOX/PCI-DSS compliance
- Performance optimization
- Load testing

### Phase 3.5: Folder Structure Migration (16 hours - PARALLEL, NON-BLOCKING)
- Create nested folder structure
- Migrate orchestrators, infrastructure, tests
- Update imports throughout
- Validate cross-platform support
- Final testing

---

## ✅ Success Metrics

### Completion
- ✅ All 10 AR decisions implemented
- ✅ All 6 FR requirements implemented
- ✅ All 4 NFR requirements met
- ✅ All 25 SKULL governance rules enforced
- ✅ All 14 brittleness fixes completed
- 🟡 25 hallucination prevention AC-IDs scheduled (Phase 2+4)

### Quality
- Test pass rate: ≥98%
- Code coverage: ≥80%
- Verification rate: ≥80% (from AC evidence)

### Performance
- Governance evaluation: <5ms per rule ✅
- SQLite query: <1ms ✅
- State transition: <10ms ✅
- Evidence capture: <500ms ✅
- Audit logging: <5ms ✅

### Security
- Zero governance bypass violations ✅
- Hash chain integrity: 100% ✅
- Secrets redaction: 100% ✅
- HIPAA/SOX/PCI-DSS compliance: Supported ✅

---

## 🔗 Related Documents

**Machine-Readable:**
- `roadmap.yaml` - Complete SSOT (100+ sections)

**Architecture Docs:**
- `architecture/00-EXECUTIVE-SUMMARY.md`
- `architecture/01-cortex-architecture.md`
- `architecture/02-governance-framework.md`
- `architecture/03-audit-infrastructure.md`
- `architecture/04-orchestrator-framework.md`
- `architecture/05-response-templates.md`
- `architecture/06-hallucination-prevention.md`
- `architecture/07-scalability-resilience.md`

**Problems Catalog:**
- `problems.yaml` - All brittleness, hallucination, previous CORTEX issues

**Implementation Details:**
- `consolidated-requirements.md`
- `framework-arch-spec.md`
- `implementation-roadmap.md`
- `custom-response-templates.md`
- `folder-structure-design.md`
- `prod-readiness-analysis.md`

---

## 📝 Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0-DRAFT | 2026-01-14 | Initial creation from analysis consolidation |

---

**Status:** ✅ READY FOR REVIEW AND APPROVAL

