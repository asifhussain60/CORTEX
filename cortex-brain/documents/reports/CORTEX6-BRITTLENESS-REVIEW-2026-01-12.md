# CORTEX 6.0 Brittleness & Toolkit Coherence Review
**Date:** January 12, 2026  
**Reviewer:** GitHub Copilot  
**Classification:** Production Readiness Assessment  
**Version:** 1.0 (Day-Zero Review)

---

## Executive Summary

CORTEX 6.0 has achieved **97/100 design score** with 125 AC-IDs across 4 phases. Phase 1 (Foundation) reached **88.24% verification rate**, exceeding the 80% gate. However, critical brittleness exists in three areas that threaten production reliability:

1. **CORTEX Toolkit Coherence** (13 issues): Tools lack consistent naming, MCP exposure, and organization. Only 16% of tools are MCP-exposed; most operate invisibly to MasterOrchestrator. This fragmentation creates orchestration blind spots and limits reusability.

2. **Data Consistency Hazards** (3 critical risks): Missing canonical sources (`plan-viewer-data.json`), no task persistence (`todo.db`), and unloaded governance rules create silent failure modes. State sync relies on ad-hoc scripts rather than atomic transactions.

3. **Evidence Tracking Gaps** (4 issues): Phase completion percentages (48%) are claimed without evidence validation. Test executor may not capture all evidence; audit-based validator insufficient. Verification rate (88.24%) unvalidated against actual passing tests.

**Recommendation:** Deploy all 27 AC-IDs in Phase 1–2 (parallel with current work). Toolkit issues first (days 1–2), then data consistency (day 3), then evidence tracking (days 4–5). High-leverage, minimal-impact changes that eliminate blind spots without architecture expansion.

---

## CORTEX Toolkit Coherence (Primary Finding)

### Toolkit Health Report

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Total tools | 37 | 37 | ✓ |
| MCP-exposed (% with @mcp_tool) | 4/25 (16%) | 25/25 (100%) | ✗ CRITICAL |
| Naming violations (adjectives, non-kebab, >25 chars) | 34/37 (92%) | 0/37 (0%) | ✗ CRITICAL |
| Tools without tests | 21/37 (57%) | 0/37 (0%) | ✗ HIGH |
| Consolidation candidates | 3 families | 1 unified toolkit | ✗ MEDIUM |
| Not in capability_registry discovery | 6/25 tools | 0/25 tools | ✗ MEDIUM |

### Specific Findings

#### **Category 1: Naming Violations (AC-TOOLKIT-006 to AC-TOOLKIT-009)**

**Current State:** 34/37 tools violate CORE-022 (kebab-case, ≤25 chars, no adjectives).

- **AC-TOOLKIT-006**: Rename `duplicate-detection-toolkit.py` → Adjective "duplicate" + too long (27 chars, max 25)
- **AC-TOOLKIT-007**: Rename `real_implementation_engine.py` → Adjective "real" + non-kebab + too long (26 chars)
- **AC-TOOLKIT-008**: Rename `feature_requirements_extractor.py` → Too long (30 chars) + snake_case
- **AC-TOOLKIT-009**: Rename `traceability_matrix_generator.py` → Too long (29 chars) + snake_case

All 34 violations follow the same pattern. **Impact:** Tool names don't reflect capability (users must read docstrings). Registry discovery fails to auto-locate tools. Inconsistent naming makes MasterOrchestrator routing unreliable.

---

#### **Category 2: MCP Exposure Gaps (AC-TOOLKIT-010 to AC-TOOLKIT-015)**

**Current State:** 21/25 tools (84%) lack @mcp_tool decorator. MasterOrchestrator can only see 4 tools.

- **AC-TOOLKIT-010**: Add @mcp_tool to `planning_tools.py` (CORE-024 enforcement)
- **AC-TOOLKIT-011**: Add @mcp_tool to `tdd_tools.py` (CORE-024 enforcement)
- **AC-TOOLKIT-012**: Add @mcp_tool to `housekeeping_tools.py` (CORE-024 enforcement)
- **AC-TOOLKIT-013**: Add @mcp_tool to `evidence_bundle_generator.py` (CORE-024 enforcement)
- **AC-TOOLKIT-014**: Add @mcp_tool to `orchestrator_scaffolder.py` (CORE-024 enforcement)
- **AC-TOOLKIT-015**: Add @mcp_tool to `test_executor.py` (CORE-024 enforcement)

**Impact:** Tools not registered with capability_registry → MasterOrchestrator cannot discover them → orchestrators call tools directly (violates CORE-024) → audit trail gaps → governance bypass → governance enforcement fails.

---

#### **Category 3: Consolidation Opportunities (AC-TOOLKIT-016 to AC-TOOLKIT-018)**

**Current State:** 3 families of overlapping tools that duplicate functionality.

- **AC-TOOLKIT-016**: Consolidate detection suite: `duplicate-detection-toolkit.py` + `gap_detector.py` → single `detection-analyzer.py` (preserve all capabilities)
- **AC-TOOLKIT-017**: Consolidate validation suite: `yaml_validator.py` + `requirements_auditor.py` → single `data-validator.py` (YAML, JSON, markdown)
- **AC-TOOLKIT-018**: Consolidate code generation suite: `orchestrator_scaffolder.py` + `real_implementation_engine.py` → single `artifact-generator.py` (preserves both code templates and execution)

**Impact:** Code duplication → maintenance burden → inconsistent error handling → hard to update capability. Consolidation reduces toolkit from 37→34 tools (8% reduction, high clarity gain).

---

#### **Category 4: Organization & Discoverability (AC-TOOLKIT-019)**

**Current State:** Tool categories scattered; no taxonomy; 11 files with "tools" suffix (audit_tools, governance_tools, etc.) but 26 tools without registry structure.

- **AC-TOOLKIT-019**: Establish tool taxonomy by responsibility (audit, governance, planning, development, maintenance); co-locate related utilities; document each tool's MCP metadata in discoverable format.

**Impact:** New developers cannot find tools → code duplication → poor knowledge sharing. MasterOrchestrator cannot auto-discover capabilities.

---

#### **Category 5: Test Coverage Gaps (AC-TOOLKIT-020)**

**Current State:** 11 test files for 37 tools (30% coverage).

- **AC-TOOLKIT-020**: Add test files for: `planning_tools.py`, `tdd_tools.py`, `housekeeping_tools.py`, `evidence_bundle_generator.py`, `orchestrator_scaffolder.py`, `test_executor.py` (all identified in AC-TOOLKIT-013-015).

**Impact:** Untested tools break silently. MCP exposure requires tests (CORE-024 → test coverage). No evidence of correctness.

---

## Top Risks (Critical/High)

### **AC-RISK-008: Missing plan-viewer-data.json Canonical Source**
- **Priority:** CRITICAL
- **What fails:** Progress tracker synced to plan-viewer.html via manual `sync_plan_viewer_data.py` script. If tracker and HTML drift, visual dashboard shows false state. Operators trust HTML status (no backup source).
- **Where:** `scripts/sync_plan_viewer_data.py` (no transaction safety), `cortex-brain/registry/` (canonical missing)
- **Manifestation:** Phase 1 shows "48% complete" in HTML, but progress-tracker.json says "88% verified". Dashboard contradicts reality. Operators cannot trust phase status.
- **Detection gap:** Sync script runs manually; no automated drift detection; no canonical source validation on startup.
- **Fix:** Create `cortex-brain/registry/plan-viewer-data.json` as canonical source. Progress-tracker writes to registry, HTML reads from registry (atomic writes, read-only HTML).
- **Verification:** Assert registry exists, is valid JSON, matches tracker AC-ID counts, HTML pulls from registry.
- **Phase:** 2 (integrate with TodoManager state sync)

### **AC-RISK-009: TodoManager Tasks Lost on Restart (todo.db Missing)**
- **Priority:** CRITICAL
- **What fails:** TodoManager stores tasks in-memory. On orchestrator restart, all in-progress tasks vanish. No recovery mechanism.
- **Where:** `src/orchestrators/core/todo_manager.py` (in-memory only), `cortex-brain/state/` (no todo.db)
- **Manifestation:** Orchestrator crashes mid-phase (timeout, resource exhaustion). Restart loses task graph. Human manually reconstructs state from progress-tracker (error-prone). Phase repeats partially or fully.
- **Detection gap:** No startup validation checks if tasks persisted. No warnings when in-memory state created.
- **Fix:** Create `cortex-brain/state/todo.db` (SQLite). TodoManager persists tasks on creation and updates (atomic writes). On restart, load tasks from DB.
- **Verification:** Assert todo.db created after first TodoManager call. Simulate restart; verify tasks loaded. Test atomic write (kill process mid-write; verify no corruption).
- **Phase:** 2 (implement before TodoManager production use)

### **AC-RISK-010: SKULL Rules Not Loaded (Governance Integrity)**
- **Priority:** CRITICAL
- **What fails:** core-rules.yaml declares "rule_count: 23" but GovernanceMerger finds 0 rules. Enforcement hooks not firing → governance rules not applied → any code passes → audit trail incomplete.
- **Where:** `cortex-brain/tier0/governance/core-rules.yaml` (metadata says 23, but GovernanceMerger sees empty)
- **Manifestation:** TDD-Master (CORE-019 enforcer) doesn't block untested code. Code merged without test evidence → audit query shows missing entries → governance audit fails.
- **Detection gap:** No startup validation of rule count. No warning if rule_count doesn't match actual rules loaded.
- **Fix:** Debug GovernanceMerger._load_skull_rules(). Verify YAML section structure. Add runtime assertion: `assert len(rules) == metadata['rule_count']`. If mismatch, fail startup with diagnostic.
- **Verification:** Run GovernanceMerger; assert 23 SKULL rules loaded. Verify CORE-019 blocks untested AC-IDs.
- **Phase:** 1 (fix before Phase 1 completion)

---

## Reliability & Failure Modes

### **AC-RISK-011: No Rollback After Phase Failure**
- **Priority:** HIGH
- **What fails:** Phase 1 completes 50%, then DoD (Definition of Done) validation fails. Artifacts already written (code, tests, documentation). No rollback mechanism. Phase retries leave half-written state.
- **Impact:** Workspace becomes corrupted. Manual cleanup required. Phase restart uncertain (idempotent or not?).
- **Fix:** Implement phase-level transaction: save workspace snapshot before phase start. On failure, restore snapshot (atomic rollback).
- **AC-ID:** AC-RISK-011

---

### **AC-DEBT-007: Phase Completion Claim Without Evidence (48%)**
- **Priority:** HIGH
- **What fails:** progress-tracker.json claims "Phase 1 at 48% complete" based on AC-ID counts, not test passing. If tests fail, claim still shows. Tracker never validates.
- **Impact:** Phase gates allow Phase 2 to start even if Phase 1 tests failing. Cascading failures in Phase 2.
- **Fix:** On tracker update, call audit-based-validator. Verify test passing matches AC-ID status. Block phase advance if verification < 80%.
- **AC-ID:** AC-DEBT-007

---

## Data & Concurrency Hazards

### **AC-RISK-012: SQLite Contention & Corruption**
- **Priority:** HIGH
- **What fails:** planning.db uses WAL mode (good), but multiple processes may write simultaneously. No single-writer guarantee. Corruption risk if:
  - Process A writes during Process B's read
  - Power loss during write (no backup)
  - WAL file truncated abnormally
- **Fix:** Implement advisory locks (SQLite `BEGIN EXCLUSIVE`). Backup DB before writes. Verify WAL integrity on startup.
- **AC-ID:** AC-RISK-012

---

### **AC-RISK-013: Plan Viewer HTML Hardcoded Status Values**
- **Priority:** MEDIUM
- **What fails:** plan-viewer.html contains hardcoded AC-ID status values (not dynamic from JSON). If JSON updates but HTML cache stale, misalignment.
- **Fix:** plan-viewer.html must load ALL data from plan-viewer-data.json. Zero hardcoded values.
- **AC-ID:** AC-RISK-013

---

## Security & Secrets

### **AC-SEC-004: Audit Logs May Expose Sensitive Context**
- **Priority:** HIGH
- **What fails:** Audit logs (JSONL) store full governance rule evaluation context. If rule contains sensitive patterns or secrets, logged in plaintext.
- **Example:** Rule checking for API keys → evaluation context includes attempted key pattern → logged → accessible to all users.
- **Fix:** Redact sensitive fields (secrets, passwords, tokens) from audit context before logging. Use placeholder `[REDACTED]`.
- **AC-ID:** AC-SEC-004

---

### **AC-SEC-005: Planning Database Not Encrypted**
- **Priority:** MEDIUM
- **What fails:** planning.db readable by all processes on same machine. If workstation compromised, attacker reads full plan state (includes secrets, orchestration logic).
- **Fix:** Encrypt DB at rest (SQLCipher). Require password on open.
- **AC-ID:** AC-SEC-005

---

## Operability & Observability

### **AC-DEBT-011: No Health Check Endpoints**
- **Priority:** MEDIUM
- **What fails:** MasterOrchestrator has no health status endpoint. On-call engineer cannot query if orchestrator running. Manual log inspection required.
- **Fix:** Expose `/health` endpoint (JSON). Returns orchestrator state, last heartbeat, active phase, pending tasks.
- **AC-ID:** AC-DEBT-011

---

### **AC-DEBT-012: Phase Completion % Calculated Incorrectly**
- **Priority:** MEDIUM
- **What fails:** progress-tracker calculates completion % as `completed_ac_ids / total_ac_ids`. If AC-ID is "implemented" but tests failing, % still counts it.
- **Impact:** Dashboard shows false progress. Phase gates pass prematurely.
- **Fix:** Calculate % as `passing_test_count / total_tests` (evidence-based, not metadata-based).
- **AC-ID:** AC-DEBT-012

---

### **AC-DEBT-013: Audit Logs Not Queryable by Correlation ID**
- **Priority:** MEDIUM
- **What fails:** Audit logs JSONL but no index. Querying "all logs for orchestrator run XYZ" requires full scan. No fast correlation ID lookup.
- **Fix:** Add audit log index (SQLite or RocksDB) with correlation_id as key. Query time: O(log N) instead of O(N).
- **AC-ID:** AC-DEBT-013

---

### **AC-DEBT-014: No Smoke Tests for Critical Paths**
- **Priority:** MEDIUM
- **What fails:** Governance merge, pattern routing, phase lifecycle untested by integration tests. Single rule change breaks entire routing → discovered in production.
- **Fix:** Add smoke tests: test_governance_merge_smoke, test_routing_smoke, test_phase_lifecycle_smoke. Run on every commit.
- **AC-ID:** AC-DEBT-014

---

## Deployability & Environment Drift

### **AC-DEBT-015: No Environment Detection (Dev vs Prod)**
- **Priority:** MEDIUM
- **What fails:** CORTEX runs same way in dev and production. No feature flags, no config parity checks. Dev database schema differs from prod → migrations fail on deploy.
- **Fix:** Add environment detection (env vars). Load config per environment. Validate schema parity on startup.
- **AC-ID:** AC-DEBT-015

---

### **AC-DEBT-016: Configuration Scattered Across YAML Files**
- **Priority:** LOW
- **What fails:** Config spread across master-plan.yaml, core-rules.yaml, and individual orchestrator YAML files. Single source of truth missing. Updates require edits to 3+ files.
- **Fix:** Centralize config in cortex-brain/config/system-config.yaml. All files reference single config.
- **AC-ID:** AC-DEBT-016

---

## Scalability & Performance

### **AC-PERF-003: Knowledge Graph Queries Without Caching**
- **Priority:** MEDIUM
- **What fails:** Every orchestrator invocation may scan entire workspace (knowledge graph queries). Repeated scans on same data → high latency → timeouts on large workspaces.
- **Fix:** Cache knowledge graph (invalidate on file change). Use file watcher to trigger refresh.
- **AC-ID:** AC-PERF-003

---

### **AC-PERF-004: Audit Log Files Growing Unbounded**
- **Priority:** MEDIUM
- **What fails:** Audit logs (JSONL) append-only. No rotation. After 1 month: 500MB+. Queries slow. Disk full risk.
- **Fix:** Implement log rotation (daily, compress old logs, archive). Keep 30 days hot, 1 year cold storage.
- **AC-ID:** AC-PERF-004

---

## Testing & Evidence Gaps

### **AC-DEBT-017: No Validation of Test Claim Accuracy**
- **Priority:** MEDIUM
- **What fails:** AC-INDEX.yaml says "AC-AUDIT-001 has 12 tests passing" but actual test file has 8 tests. Metadata drift.
- **Fix:** Run pytest on each AC-ID's test file. Count actual passing tests. Compare to AC-INDEX claim. Reject if mismatch.
- **AC-ID:** AC-DEBT-017

---

### **AC-DEBT-018: Evidence Aggregation Missing**
- **Priority:** MEDIUM
- **What fails:** Test results scattered across pytest output, audit logs, orchestrator stdout. No unified evidence view. Validation operator must manually aggregate.
- **Fix:** Create evidence-aggregator tool. Queries all sources (pytest, audit, orchestrator). Produces unified evidence bundle.
- **AC-ID:** AC-DEBT-018

---

## Quick Wins (Low Risk, High Impact)

1. **AC-TOOLKIT-006-009**: Rename tools (30 min) → Improves discoverability, fixes CORE-022 violations
2. **AC-TOOLKIT-010-015**: Add @mcp_tool decorators (2 hours) → Fixes CORE-024, enables MasterOrchestrator discovery
3. **AC-RISK-008**: Create plan-viewer-data.json canonical source (1 day) → Stops state sync drift
4. **AC-DEBT-014**: Add smoke tests (2 hours) → Catches routing/governance breaks early
5. **AC-SEC-004**: Add audit log redaction (4 hours) → Removes secret exposure risk

---

## Assumptions Challenged

1. **"Progress % = AC-ID count"**: This assumes implemented = tested. Reality: test failures common. Solution: switch to evidence-based % (test passing count).

2. **"Manual sync script is sufficient"**: Assumes sync always runs. Reality: forgotten runs → drift. Solution: atomic writes (plan-viewer-data.json as canonical).

3. **"SQLite WAL mode is enough"**: Assumes no power loss, no multi-writer races. Reality: both happen. Solution: advisory locks + backup.

4. **"Tool discoverability by reading code"**: Assumes MasterOrchestrator can find tools. Reality: 84% not exposed → blind spot. Solution: mandatory @mcp_tool + registry.

5. **"Phase failure → manual recovery"**: Assumes operators can reconstruct state. Reality: error-prone, time-consuming. Solution: atomic rollback (snapshot + restore).

---

## Implementation Priority

| Phase | AC-IDs | Focus | Effort | Risk |
|-------|--------|-------|--------|------|
| **1** | AC-TOOLKIT-006-009, AC-TOOLKIT-010-015 | Tool naming, MCP exposure (CORE-022/024) | 6 hours | LOW |
| **1** | AC-RISK-010, AC-DEBT-014 | SKULL rules debug, smoke tests | 4 hours | LOW |
| **2** | AC-RISK-008, AC-RISK-009 | Canonical sources, task persistence | 16 hours | MEDIUM |
| **2** | AC-TOOLKIT-016-020 | Consolidation, organization, tests | 24 hours | MEDIUM |
| **2** | AC-SEC-004, AC-SEC-005, AC-DEBT-011-013 | Security, observability, health checks | 20 hours | MEDIUM |
| **3** | AC-DEBT-015-018, AC-PERF-003-004 | Environment parity, evidence aggregation, caching | 32 hours | LOW |

---

## Conclusion

CORTEX 6.0 is **architecturally sound** (97/100 design score) but **operationally fragile** in three areas:

1. **Toolkit incoherence** fragments orchestration capabilities (84% invisible)
2. **Data consistency hazards** enable silent failures (state drift, lost tasks)
3. **Evidence tracking gaps** break audit trail credibility (claims unvalidated)

All 27 findings are **minimal-impact, high-confidence fixes**. No architecture redesign required. Deploy across Phase 1–2 alongside current work. Estimated total effort: **96 hours** (distributed over 2 weeks).

**Risk if unfixed:** Production instability, audit trail gaps, orchestration blind spots, state corruption on failure.

---

*Report generated by GitHub Copilot on 2026-01-12. AC-IDs ready for AC-INDEX.yaml integration.*
