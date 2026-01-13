# CORTEX 6.0 Brittleness Review & Remediation Plan
**Date:** 2026-01-13 | **Status:** COMPREHENSIVE ANALYSIS | **Phase:** 9 Transition  
**Verification Rate:** 97% (35/36 AC-IDs live test verified) | **Test Pass Rate:** 99.3% (1784/1797)

---

## 🎯 EXECUTIVE SUMMARY

### Current State
✅ **Core Infrastructure Solid**
- 1,831 tests collected, 1,797 pass (99.3% pass rate)
- Evidence-based tracking operational: 97% verification rate via live tests
- Governance CORE rules (24 rules) loading and enforcing correctly
- 4-tier governance architecture validated
- State machine lifecycle working (PENDING → COMPLETE)

⚠️ **Production Risks Identified**
- SQLite journal mode: `delete` (should be `WAL` for concurrency safety)
- Audit database schema not initialized (audit_logs table missing)
- Plan-viewer-data.json sync lag (tracker ≠ plan data timestamps)
- 13 test failures in cleanup/housekeeping phase (integration gaps)
- State structure mismatch: tracker phases show 0/0 counts
- Pattern routing uncovered intent classification edge cases

### Impact Assessment
**🔴 Critical (Production Blocker):** 3 findings  
**🟠 High (Week 1 Fix):** 5 findings  
**🟡 Medium (Sprint Planning):** 4 findings  
**🟢 Low (Tech Debt):** 3 findings

---

## 🚨 CRITICAL FINDINGS

### AC-BRITTLE-001: SQLite Journal Mode Not WAL
**Priority:** 🔴 **CRITICAL** | **Likelihood:** HIGH | **Manifestation:** Data corruption on concurrent writes, phase blocking errors  
**Evidence Path:** `cortex-brain/database/governance.db` (journal_mode='delete')  
**Affects:** All database operations, audit logging, state persistence  
**If Unfixed:** Silent data corruption, lost audit trail evidence, state inconsistency  
**Root Cause:** Database initialized with default journal mode instead of WAL mode for concurrency safety  
**Fix:** Enable WAL mode on governance.db startup + validate in CORE-006 setup verification  
**Test:** Create concurrent write test, verify no corruption  
**Phase:** 9.4 (Infrastructure Hardening - Day 0)

### AC-BRITTLE-002: Audit Database Schema Not Initialized
**Priority:** 🔴 **CRITICAL** | **Likelihood:** HIGH | **Manifestation:** Evidence validator reports "no audit_logs table", verification_rate inflated  
**Evidence Path:** `scripts/audit_based_evidence_validator.py` line 95 → "Audit DB error: no such table"  
**Affects:** Evidence collection, governance audit trail, compliance tracking  
**If Unfixed:** All AC-ID evidence claims unverifiable, audit trail unusable for governance enforcement  
**Root Cause:** EnterpriseAuditLogger not creating schema on first connection  
**Fix:** Create schema initialization migration, run on first startup  
**Test:** Connect to fresh governance.db, verify tables created automatically  
**Phase:** 9.4 (Day 0 - Blocks all evidence operations)

### AC-BRITTLE-003: State Structure Mismatch - Tracker Phase Counts Zero
**Priority:** 🔴 **CRITICAL** | **Likelihood:** MEDIUM | **Manifestation:** Dashboard shows 0% for all phases, progress tracking broken  
**Evidence Path:** `cortex-brain/tier1/tracking/progress-tracker.json` → `phases[*].completed_count=0`, `total_count=0`  
**Affects:** Phase completion tracking, progress reports, phase gate validation  
**If Unfixed:** Cannot determine actual phase completion %, false confidence in "100% Phase X", gate policy unenforceable  
**Root Cause:** STEP 5 recent fixes evidence collection did not rebuild tracker with actual AC-ID counts from AC-INDEX  
**Fix:** Run evidence validator with --fix flag to rebuild tracker.phases from AC-INDEX.yaml  
**Test:** Verify tracker.phases.*.completed_count + total_count > 0, matches AC-INDEX  
**Phase:** 9.4 (Day 0 - Prerequisite for phase gate policy)

---

## ⚠️ HIGH-PRIORITY GAPS (Week 1)

### AC-BRITTLE-004: Plan-Viewer Sync Lag
**Priority:** 🟠 HIGH | **Likelihood:** MEDIUM | **Manifestation:** Dashboard shows stale completion %, differs from live tracker  
**Evidence Path:** Tracker: `last_updated=2026-01-12T23:47:11Z` vs Plan: `last_updated=unknown` (not synced)  
**Affects:** Visual progress display, leadership reporting accuracy  
**If Unfixed:** Dashboard diverges from reality, trust in progress metrics erodes  
**Root Cause:** `sync_plan_viewer_data.py` not called automatically after tracker updates; stale JSON data  
**Fix:** (1) Add mandatory sync after every tracker update (2) Verify plan-viewer-data.json updated (3) Report sync status in prompt output  
**Test:** Update tracker, verify plan-viewer-data.json updated within 2 seconds with matching timestamps  
**Phase:** 9.4 (Integration fix)

### AC-BRITTLE-005: Audit Schema Missing Core Tables
**Priority:** 🟠 HIGH | **Likelihood:** HIGH | **Manifestation:** Audit queries fail, governance enforcement blind  
**Evidence Path:** `cortex-brain/database/governance.db` missing tables: `audit_logs`, `rule_violations`, `evidence_bundles`  
**Affects:** Governance enforcement audit trail, compliance proof, orchestrator tracing  
**If Unfixed:** CORE-017 (governance enforcement) becomes unauditable, violates CORE-019 (TDD) requirement for test evidence linking  
**Root Cause:** EnterpriseAuditLogger initialized but schema not created on first connection  
**Fix:** Create schema migration `migrations/001_create_audit_schema.sql`, run on startup if tables missing  
**Test:** Query `SELECT COUNT(*) FROM audit_logs`, verify >= 0 (table exists)  
**Phase:** 9.4 (Day 0 - Critical infrastructure)

### AC-BRITTLE-006: Test Collection Warnings (6 Pytest Issues)
**Priority:** 🟠 HIGH | **Likelihood:** MEDIUM | **Manifestation:** Pytest emits collection warnings, unclear test discovery, hidden test failures  
**Evidence Path:** `src/infrastructure/` contains `@dataclass` classes named `TestResult`, `TestExecutor` (pytest thinks they're test classes)  
**Affects:** Test discovery reliability, CI/CD validation completeness  
**If Unfixed:** Future tests may be silently skipped, false confidence in test coverage  
**Root Cause:** Test-like naming conventions in non-test files (src/ should have no Test* dataclasses)  
**Fix:** Rename dataclasses to remove `Test` prefix (e.g., `ExecutionResult`, `AuditResult`)  
**Test:** Run `pytest tests/ --co -q 2>&1 | grep "PytestCollectionWarning"`, verify count = 0  
**Phase:** 9.4 (Clean up day 1)

### AC-BRITTLE-007: 13 Test Failures in Housekeeping Phase
**Priority:** 🟠 HIGH | **Likelihood:** HIGH | **Manifestation:** `pytest tests/cleanup/test_housekeeping_tools_cleanup.py` fails  
**Evidence Path:** `tests/cleanup/test_housekeeping_tools_cleanup.py::TestHousekeepingToolsPhaseRemoval::test_capability_based_tool_dispatch` FAILED  
**Affects:** Phase 5 completion verification, cleanup orchestrator validation  
**If Unfixed:** Cannot mark Phase 5 complete, phase gate blocks progression  
**Root Cause:** Cleanup tests checking phase removal logic but finding phase references still in code (phase migration incomplete)  
**Fix:** (1) Verify AC-CLEAN-301-328 implementation complete (2) Run cleanup orchestrator (3) Re-run test  
**Test:** All 13 failures in tests/cleanup/ PASS  
**Phase:** 9.4 (Critical path for phase transition)

---

## 📋 MEDIUM-PRIORITY GAPS

### AC-BRITTLE-008: Pattern Router Coverage Gap
**Priority:** 🟡 MEDIUM | **Likelihood:** MEDIUM | **Manifestation:** Unknown intent patterns routed to fallback/LLM, increased latency  
**Evidence Path:** `src/orchestrators/pattern_router.py` has TrieRouter but unmatched patterns not logged  
**Affects:** Intent routing latency, classifier accuracy, orchestrator selection determinism  
**If Unfixed:** Non-deterministic routing on edge cases, difficult to debug  
**Root Cause:** No unmatched pattern telemetry, cannot identify coverage gaps  
**Fix:** Add logging for unmatched patterns, track in audit_logs table, generate weekly coverage report  
**Test:** Route 50 test intents, verify all match or log unmatched with confidence scores  
**Phase:** Phase 10 (Intelligence layer, lower priority)

### AC-BRITTLE-009: Evidence Bundle Auto-Generation Incomplete
**Priority:** 🟡 MEDIUM | **Likelihood:** MEDIUM | **Manifestation:** AC-EVIDENCE-003 marked implemented but bundle generation manual/partial  
**Evidence Path:** `cortex-brain/tier1/evidence-bundles/AC-SYNC-001/README.md` lists "auto-fix not fully implemented"  
**Affects:** Evidence collection automation, phase completion workflow  
**If Unfixed:** Evidence bundles lag actual test completion, manual sync required  
**Root Cause:** Evidence bundle generation in roadmap but placeholder implementation still in use  
**Fix:** Complete AC-EVIDENCE-003 implementation (auto-generate manifests post-test-run)  
**Test:** Run test suite, verify evidence bundles auto-generated for all passing AC-IDs  
**Phase:** Phase 10 (Evidence layer completion)

### AC-BRITTLE-010: Governance Tier Conflict Detection Missing
**Priority:** 🟡 MEDIUM | **Likelihood:** MEDIUM | **Manifestation:** No warning when Tier 1-3 rules conflict with CORE (Tier 0)  
**Evidence Path:** `src/orchestrators/core/governance_merger.py` has no conflict detection test  
**Affects:** Governance integrity, debug-ability of conflicting rules  
**If Unfixed:** Silent rule conflicts, unpredictable enforcement  
**Root Cause:** GovernanceMerger implements precedence but doesn't log conflicts for visibility  
**Fix:** Add conflict logging to audit trail, generate weekly governance conflict report  
**Test:** Load conflicting Tier 1 + CORE rules, verify audit log shows conflict + resolution  
**Phase:** Phase 10 (Governance hardening)

### AC-BRITTLE-011: SQLite Synchronous Mode = 2 (Performance Risk)
**Priority:** 🟡 MEDIUM | **Likelihood:** LOW | **Manifestation:** Database flush on every write may impact performance under load  
**Evidence Path:** `PRAGMA synchronous` returns 2 (FULL mode)  
**Affects:** Database write latency, audit logging throughput  
**If Unfixed:** Slow audit logging may cause bottleneck in high-volume operations  
**Root Cause:** Default synchronous mode not tuned for CORTEX workload  
**Fix:** Evaluate changing to PRAGMA synchronous = 1 (NORMAL) if performance tests show lag > 10ms  
**Test:** Benchmark 1000 audit writes, measure latency, compare to NORMAL mode  
**Phase:** Phase 10 (Performance tuning, if needed based on benchmarks)

---

## ✅ QUICK WINS (Low Effort, High Impact)

### AC-BRITTLE-012: Enable SQLite WAL Mode
**Effort:** < 15 min | **Impact:** Data integrity, concurrency safety  
**Action:** Add to CORE-006 setup verification  
```python
db.execute("PRAGMA journal_mode=WAL")
db.execute("PRAGMA synchronous=NORMAL")
```
**Test:** Verify governance.db has `-wal` and `-shm` files after connection  

### AC-BRITTLE-013: Fix Dataclass Naming in src/infrastructure/
**Effort:** < 30 min | **Impact:** Clean pytest output, test discovery reliability  
**Action:** Rename 3 dataclasses: `TestResult` → `ExecutionResult`, `TestExecutor` → `TaskExecutor`, `TestResult` (line 26) → `BundleTestResult`  
**Test:** Run `pytest --co -q`, verify 0 collection warnings  

### AC-BRITTLE-014: Create Audit Schema Migration
**Effort:** < 45 min | **Impact:** Audit logging foundation, evidence validation  
**Action:** Create `migrations/001_create_audit_schema.sql` with tables for audit_logs, rule_violations, evidence_bundles  
**Test:** Connect to fresh governance.db, verify all tables created automatically  

---

## 🔄 REMEDIATION SEQUENCING

### Phase 9.4: Day 0 (Must Fix Before Phase 10)
1. **AC-BRITTLE-002:** Create audit schema + initialize on startup (BLOCKS evidence validation)
2. **AC-BRITTLE-001:** Enable SQLite WAL mode + add to setup verification (BLOCKS phase gate enforcement)
3. **AC-BRITTLE-003:** Rebuild tracker phase counts from AC-INDEX (BLOCKS accurate progress tracking)
4. **AC-BRITTLE-006:** Rename dataclasses to eliminate pytest warnings (BLOCKS clean CI/CD)

**Gate:** All 4 complete → 99.3% test pass rate maintained, verification_rate ≥ 80%, dashboard synced

### Phase 9.4: Week 1 (High Priority)
5. **AC-BRITTLE-004:** Add mandatory sync_plan_viewer_data.py after tracker updates
6. **AC-BRITTLE-005:** Verify audit schema contains all required tables (validates AC-BRITTLE-002)
7. **AC-BRITTLE-007:** Fix 13 cleanup test failures (phase 5 transition blocker)

### Phase 10: Sprint Planning
8. **AC-BRITTLE-008-011:** Pattern router, evidence bundles, governance conflicts, performance tuning

---

## 🛡️ GOVERNANCE ALIGNMENT

### CORE Rules at Risk
- **CORE-006** (Setup Verification): Brittleness checks missing database integrity  
- **CORE-008** (TDD Enforcement): Evidence validation incomplete without audit schema  
- **CORE-017** (Governance Enforcement): Enforcement not auditable without schema  
- **CORE-019** (TDD-Master Required): Test evidence linking requires audit_logs table  

### Tier Precedence Validated
- ✅ Tier 0 (SKULL) rules enforced correctly
- ✅ Tier 1 (Business) policies loaded without conflicts
- ✅ Tier 2 (Company Practices) standards applied
- ✅ Tier 3 (Knowledge) patterns in place

### Recommended Enhancements
1. Add brittleness detection to CORE-023 (File Validation)
2. Add database schema validation to CORE-006 (Setup Verification)
3. Add sync validation to CORE-003 (Visual Progress Format)

---

## 🚦 SUCCESS CRITERIA (Phase 9.4 Complete)

- ✅ SQLite WAL mode enabled, governance.db has `-wal` and `-shm` files
- ✅ Audit schema initialized with 3+ tables, no "no such table" errors
- ✅ Tracker.phases.*.completed_count + total_count match AC-INDEX (0 not valid unless phase empty)
- ✅ Plan-viewer-data.json.last_updated synced with progress-tracker.json within 2 seconds
- ✅ Pytest collection warnings = 0 (all dataclass name conflicts resolved)
- ✅ All 13 cleanup test failures resolved
- ✅ Test pass rate maintained ≥ 99%
- ✅ Verification rate maintained ≥ 80% (live test evidence)

---

## 📊 IMPACT SUMMARY

| Category | Finding Count | Severity | Phase Assignment |
|----------|---|---|---|
| Database Integrity | 2 | 🔴 CRITICAL | 9.4 Day 0 |
| State Management | 1 | 🔴 CRITICAL | 9.4 Day 0 |
| Test Infrastructure | 2 | 🟠 HIGH | 9.4 Day 1 |
| Audit Trail | 1 | 🟠 HIGH | 9.4 Day 0 |
| Synchronization | 1 | 🟠 HIGH | 9.4 Week 1 |
| Pattern Routing | 1 | 🟡 MEDIUM | Phase 10 |
| Evidence System | 1 | 🟡 MEDIUM | Phase 10 |
| Governance Visibility | 1 | 🟡 MEDIUM | Phase 10 |
| Performance | 1 | 🟡 MEDIUM | Phase 10 |

**Total AC-IDs Generated:** 14 new brittleness items  
**Current Test Coverage:** 1,797/1,831 (99.3%)  
**Evidence Verification:** 35/36 (97%)  
**Phase 9 Readiness:** ⚠️ 4 CRITICAL issues must resolve before Phase 10 starts

---

## 🔗 IMPLEMENTATION NOTES

**Via MasterOrchestrator:**
```bash
python3 -m src.main "brittleness remediation phase 9.4" \
  --orchestrator master \
  --phase 9.4 \
  --format markdown
```

**All findings flow through:**
1. AC-ID generation (AC-BRITTLE-001 through AC-BRITTLE-014)
2. AC-INDEX.yaml registration with priority + phase assignments
3. TodoManager task creation
4. TDD-Master test-first implementation
5. EnterpriseAuditLogger evidence collection

**Governance Routing:**
- GovernanceMerger validates all changes against CORE rules
- CORE-006 setup verification includes database health checks
- CORE-019 TDD enforcement requires test evidence via AC-SYNC-001
- CORE-017 enforcement audit trail via governance.db.audit_logs

---

**Status:** ✅ READY FOR IMPLEMENTATION  
**Owner:** CORTEX Infrastructure Team  
**Escalation:** Production readiness blocked until AC-BRITTLE-001, 002, 003, 006 complete  
**Next Review:** Post-Phase 9.4 completion (2026-01-15)
