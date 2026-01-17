# CORTEX Remediation Roadmap & Action Items
## January 17, 2026

**Review Date:** 2026-01-17  
**Findings:** 12 gaps identified (3 CRITICAL, 3 HIGH, 4 MEDIUM, 2 LOW)  
**Estimated Effort:** 20-28 hours  
**Timeline to Production:** 2-3 weeks

---

## EXECUTIVE RECOMMENDATIONS

### 1. IMMEDIATE (Today/Tomorrow)

**Action:** Triage findings and assign ownership

**Tasks:**
- [ ] Team review of full findings report
- [ ] Consensus on severity/priority
- [ ] Assign owner for each AC
- [ ] Create tickets in project management

**Owner:** Project Lead  
**Effort:** 1-2 hours  
**Deadline:** EOD Jan 18

---

### 2. THIS WEEK (Jan 18-24)

**Action:** Implement HIGH/CRITICAL fixes (7-10 hours)

**Ticket 1: Database Connection Lifecycle (CRITICAL)**
- **AC ID:** AC-FIX-008-01
- **Owner:** [Assign: Infrastructure Team]
- **Tasks:**
  - [ ] Audit all `sqlite3.connect()` calls in src/
  - [ ] Wrap in context managers (with statements)
  - [ ] Add exception handling with cleanup
  - [ ] Implement test fixture isolation (one DB per test)
  - [ ] Run full test suite: expect ~81 tests to pass
  - [ ] Performance test: 5-minute load test
- **Files to Modify:**
  - `src/infrastructure/database.py`
  - `src/infrastructure/audit_logger.py`
  - `tests/conftest.py`
  - `src/infrastructure/database_transaction_manager.py`
- **Tests to Add:**
  - `tests/unit/infrastructure/test_connection_lifecycle.py` (new)
  - Add concurrent DB access tests
- **Verification:**
  - [ ] All 81 previously failing tests pass
  - [ ] New tests for concurrent access pass
  - [ ] No connection leaks detected
  - [ ] Load test clean (no hangs)
- **Effort:** 3-4 hours
- **Deadline:** Jan 22

**Ticket 2: Telemetry Thread Safety (CRITICAL)**
- **AC ID:** AC-BRITTLENESS-001
- **Owner:** [Assign: Infrastructure Team]
- **Tasks:**
  - [ ] Replace `self.running` boolean with `threading.Event()`
  - [ ] Use event for atomic state transitions
  - [ ] Add `running_event.wait()` in worker thread
  - [ ] Add graceful shutdown with timeout
  - [ ] Add unit test for startup/shutdown race
  - [ ] Add stress test (high metric throughput + shutdown)
- **Files to Modify:**
  - `src/infrastructure/metrics_exporter.py` (lines 146-253)
- **Tests to Add:**
  - `tests/unit/infrastructure/test_telemetry_concurrency.py` (new)
  - Test concurrent startup scenarios
  - Test shutdown under load
- **Verification:**
  - [ ] All metrics exported before shutdown
  - [ ] No race condition on startup
  - [ ] Stress test passes
- **Effort:** 2-3 hours
- **Deadline:** Jan 21

**Ticket 3: Boundary Enforcement Integration (HIGH)**
- **AC ID:** AC-HALLUCINATION-001
- **Owner:** [Assign: Architecture Team]
- **Tasks:**
  - [ ] Review MasterOrchestrator delegation flow
  - [ ] Integrate BoundaryEnforcer check before delegation
  - [ ] Add error handling for boundary violations
  - [ ] Create integration test showing orchestrator→boundary
  - [ ] Document expected behavior in architecture guide
- **Files to Modify:**
  - `src/orchestrators/core/master_orchestrator.py`
  - `src/core/hallucination_prevention/behavioral_boundaries.py` (if needed)
- **Tests to Add:**
  - `tests/integration/test_orchestrator_boundary_enforcement.py` (new)
  - Test invalid phase transitions blocked
  - Test AC deletion without approval blocked
  - Test governance rules enforced
- **Verification:**
  - [ ] Integration test passes
  - [ ] Boundary violations prevented
  - [ ] Clean error messages returned
- **Effort:** 2-3 hours
- **Deadline:** Jan 23

**Check-in:** Friday Jan 24, 2pm (verify all HIGH/CRITICAL fixes complete)

---

### 3. NEXT WEEK (Jan 25-31)

**Action:** Implement MEDIUM fixes (6-9 hours)

**Ticket 4: ExecutionSandbox Locking (MEDIUM)**
- **AC ID:** AC-BRITTLENESS-002
- **Owner:** [Assign: Hallucination Prevention Team]
- **Tasks:**
  - [ ] Add `self.history_lock = threading.RLock()` to __init__
  - [ ] Protect `execute()` append: `with self.history_lock: self.execution_history.append()`
  - [ ] Protect `get_execution_history()` read: `with self.history_lock: return copy.deepcopy(...)`
  - [ ] Add concurrent access test (10+ threads)
  - [ ] Verify history integrity under concurrency
- **Files to Modify:**
  - `src/core/hallucination_prevention/execution_sandbox.py`
- **Tests to Add:**
  - Add test to existing test files
  - `test_concurrent_history_access()` with 10 threads
- **Verification:**
  - [ ] History integrity maintained under concurrency
  - [ ] No race condition detected
  - [ ] Performance acceptable (<10ms overhead)
- **Effort:** 1-2 hours
- **Deadline:** Jan 27

**Ticket 5: Timeout Configuration (MEDIUM)**
- **AC ID:** AC-BRITTLENESS-004
- **Owner:** [Assign: Infrastructure Team]
- **Tasks:**
  - [ ] Add timeout configuration class (or use config file)
  - [ ] Audit all `thread.join()` calls
  - [ ] Add timeout to all blocking operations
  - [ ] Document timeout rationale
  - [ ] Add test for timeout enforcement
- **Files to Modify:**
  - `src/infrastructure/config.py` (new or existing)
  - `src/infrastructure/metrics_exporter.py`
  - `src/core/hallucination_prevention/execution_sandbox.py`
  - Multiple test files
- **Configuration:**
  ```yaml
  timeouts:
    thread_join: 5.0  # seconds
    db_operation: 10.0
    external_api: 30.0
    sandbox_execution: 30000  # milliseconds
  ```
- **Verification:**
  - [ ] All operations have timeouts
  - [ ] Tests verify timeout enforcement
  - [ ] No indefinite hangs possible
- **Effort:** 2-3 hours
- **Deadline:** Jan 28

**Ticket 6: Sandbox Isolation Documentation (MEDIUM)**
- **AC ID:** AC-HALLUCINATION-002
- **Owner:** [Assign: Hallucination Prevention Team]
- **Tasks:**
  - [ ] Document sandbox isolation boundaries
  - [ ] Clarify: in-process only, no external API interception (yet)
  - [ ] Add warning about external calls in documentation
  - [ ] Implement request patching for future enhancement
  - [ ] Add test showing external calls blocked in sandbox
  - [ ] Create "Sandbox Usage Guide"
- **Files to Modify:**
  - `src/core/hallucination_prevention/execution_sandbox.py` (docstrings)
  - New doc: `docs/sandbox-isolation-guide.md`
  - New test: `tests/integration/test_sandbox_external_calls.py`
- **Tests to Add:**
  - Test external API calls attempted in sandbox
  - Verify calls blocked/intercepted
  - Test committed mode allows external calls
- **Verification:**
  - [ ] Documentation clear on boundaries
  - [ ] External call test passes
  - [ ] Developers understand limitations
- **Effort:** 3-4 hours
- **Deadline:** Jan 29

**Check-in:** Friday Jan 31, 2pm (verify all MEDIUM fixes complete)

---

### 4. FOLLOWING WEEK (Feb 1-7)

**Action:** Final reviews and production prep

**Ticket 7: Path Resolution Audit (MEDIUM)**
- **AC ID:** AC-BRITTLENESS-005
- **Owner:** [Assign: DevOps/Infra]
- **Tasks:**
  - [ ] Audit all hardcoded paths in src/
  - [ ] Convert to Path(__file__).parent-relative paths
  - [ ] Test from multiple working directories
  - [ ] Verify CI/CD paths work
- **Effort:** 1-2 hours
- **Deadline:** Feb 3

**Ticket 8: AC Status Tracking (MEDIUM)**
- **AC ID:** GAP-001
- **Owner:** [Assign: DevOps/Governance]
- **Tasks:**
  - [ ] Investigate FIX category 0% completion anomaly
  - [ ] Reconcile audit_log vs roadmap.yaml
  - [ ] Fix logging for AC-FIX completions
  - [ ] Verify all ~250 ACs properly logged
- **Effort:** 2 hours
- **Deadline:** Feb 4

**Ticket 9: Pytest Configuration (LOW)**
- **AC ID:** GAP-002
- **Owner:** [Assign: Any]
- **Tasks:**
  - [ ] Add custom marks to pytest.ini
  - [ ] Register dashboard, phase15, tdd_red, ac marks
  - [ ] Run tests to verify no warnings
- **Effort:** <1 hour
- **Deadline:** Feb 5

**Ticket 10: TestFramework Naming (LOW)**
- **AC ID:** GAP-003
- **Owner:** [Assign: Any]
- **Tasks:**
  - [ ] Rename TestFramework to IntentFramework
  - [ ] Or add __test__ = False
  - [ ] Verify pytest collection clean
- **Effort:** <1 hour
- **Deadline:** Feb 5

**Ticket 11: Confidence Scoring Review (LOW)**
- **AC ID:** HALLUCINATION-003
- **Owner:** [Assign: Data Science/ML]
- **Tasks:**
  - [ ] Review scoring algorithm
  - [ ] Compare against calibration data
  - [ ] Add edge case tests
  - [ ] Document scoring model
- **Effort:** 2 hours
- **Deadline:** Feb 6

**Ticket 12: Intent Parsing Fuzzing (LOW)**
- **AC ID:** HALLUCINATION-004
- **Owner:** [Assign: QA/Testing]
- **Tasks:**
  - [ ] Document loose format grammar
  - [ ] Add fuzzing tests
  - [ ] Identify and fix parsing gaps
  - [ ] Validate numeric limits
- **Effort:** 1-2 hours
- **Deadline:** Feb 7

---

## TESTING STRATEGY

### Pre-Remediation Baseline
- [ ] Run full test suite: document baseline (should be 100%)
- [ ] Note any intermittent failures
- [ ] Capture current timings

### During Remediation
- [ ] Each fix includes unit tests
- [ ] Each fix includes integration tests (if applicable)
- [ ] Run full suite after each fix: verify no regressions

### Post-Remediation Verification
- [ ] Full test suite: must be 100% passing
- [ ] Load test: 5-minute duration, 10x normal throughput
- [ ] Concurrency test: all findings validated for thread safety
- [ ] Performance test: no regressions vs baseline
- [ ] Staging deployment: 24-hour monitoring

---

## SIGN-OFF CRITERIA

### Each Fix Must Have:
- ✅ Implementation code reviewed (peer review)
- ✅ Unit tests passing
- ✅ Integration tests passing
- ✅ Load test passing (if applicable)
- ✅ Documentation updated
- ✅ No performance regression
- ✅ Owner sign-off

### Final Production Sign-Off:
- ✅ All 12 gaps addressed
- ✅ All tests passing (100%)
- ✅ Code review complete
- ✅ Security audit complete
- ✅ Performance baseline verified
- ✅ Architecture review approved
- ✅ Team sign-off complete

---

## RISK MITIGATION

### If Fix Takes Longer Than Estimated
**Escalation Path:**
1. Report at daily standup (day 1 of delay)
2. Request scope reduction or timeline adjustment
3. Alternative: defer LOW priority items
4. Never compromise on CRITICAL/HIGH fixes

### If New Issues Found During Fixes
**Process:**
1. Document with evidence grade
2. If same severity, add to current roadmap
3. If higher severity, adjust priorities
4. Never suppress findings; always escalate

### If Fixes Break Other Tests
**Process:**
1. Immediately revert change
2. Root cause analysis required
3. Redesign fix with broader testing
4. All fixes must pass 100% test suite

---

## COMMUNICATION PLAN

### Daily Standup (9:30 AM)
- 1 min per ticket: status, blockers, support needed
- Escalate any delays immediately

### Weekly Review (Friday 2 PM)
- Review progress on all tickets
- Adjust timeline if needed
- Plan next week's work

### Stakeholder Updates
- **Monday:** Week start summary
- **Wednesday:** Mid-week status
- **Friday:** Week recap + next week preview

### Final Sign-Off
- Team meeting: discuss all fixes, Q&A
- Stakeholder approval required before production

---

## DOCUMENTATION DELIVERABLES

### Each Fix Should Include:

1. **Implementation Report** (one per fix)
   - Problem statement
   - Solution approach
   - Code changes (diffs)
   - Testing approach
   - Results/metrics

2. **Architecture Updates**
   - Update AR-* documents if applicable
   - Update governance rules if applicable
   - Update API documentation

3. **Operational Guides**
   - If affects deployment: add to deployment guide
   - If affects monitoring: add to monitoring guide
   - If affects troubleshooting: add to runbook

### Final Deliverables

- [ ] Remediation Summary Report (all fixes)
- [ ] Updated Architecture Decision Records
- [ ] Updated Governance Rules
- [ ] Operator Runbook Updates
- [ ] Performance Baseline Documentation

---

## SUCCESS METRICS

### Before Remediation
| Metric | Baseline |
|--------|----------|
| Test Pass Rate | 100% |
| Failing Tests | 0 |
| Known Hangs | 0 |
| Critical Issues | 3 |
| High Issues | 3 |

### After Remediation (Target)
| Metric | Target |
|--------|--------|
| Test Pass Rate | 100% |
| Failing Tests | 0 |
| Known Hangs | 0 |
| Critical Issues | 0 |
| High Issues | 0 |
| Findings Resolution | 100% |

---

## GO/NO-GO CHECKLIST FOR PRODUCTION

**Go Criteria:**
- [ ] ALL gaps remediated (12/12)
- [ ] Test pass rate 100%
- [ ] No critical issues remaining
- [ ] Staging deployment 24hr+ stable
- [ ] Performance baseline verified
- [ ] Load test passed
- [ ] Security audit completed
- [ ] Team consensus to deploy

**No-Go Criteria:**
- ❌ ANY critical issue unresolved
- ❌ Test pass rate < 100%
- ❌ Performance regression > 10%
- ❌ Security issues found
- ❌ Staging unstable

---

## APPENDIX: RESOURCE ALLOCATION

### Recommended Team Size
- Infrastructure Team: 2 people (DB connections, telemetry, timeouts, path resolution)
- Architecture Team: 1 person (boundary enforcement integration)
- Hallucination Prevention Team: 2 people (sandbox locking, isolation documentation, scoring review)
- QA/Testing: 1 person (fuzzing, concurrency testing)
- DevOps: 1 person (AC tracking, pytest config, path audit)

**Total: 7 people, 20-28 hours = 3-4 days effort**

### Time Breakdown by Area
- Infrastructure: ~11 hours (connections 4h + telemetry 2h + timeouts 2h + paths 1.5h + config 1.5h)
- Architecture: ~2-3 hours (boundary enforcement 2-3h)
- Hallucination: ~6-7 hours (locking 1.5h + isolation 3.5h + scoring 1-1.5h)
- QA/Testing: ~1-2 hours (fuzzing 1-2h)
- DevOps: ~2 hours (AC tracking 1h + pytest 0.5h + config 0.5h)

---

**Report Generated:** 2026-01-17 19:30 UTC  
**Target Completion:** 2026-02-07  
**Production Deployment:** 2026-02-10 (estimated)

*For questions or clarifications on any item, contact the Architecture team.*
