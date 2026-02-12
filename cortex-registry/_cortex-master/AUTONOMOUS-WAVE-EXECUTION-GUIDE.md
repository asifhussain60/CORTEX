# Autonomous Wave Execution Guide
**Version:** 1.0 | **Created:** 2026-02-12 | **Authority:** Implementation Reality Sync v2.0 | **Mode:** Silent Autonomous ✅

---

## 🎯 Purpose

This guide provides ready-to-execute commands for autonomous wave completion within single GitHub Copilot Chat sessions. Each wave is designed for end-to-end TDD execution (RED→GREEN→REFACTOR→COMMIT→VERIFY) in 2-4 hours with <200k tokens.

---

## 📋 Quick Reference Matrix

| Wave | Priority | Duration | Status | Command Reference |
|------|----------|----------|--------|-------------------|
| **WAVE-A** | P0-CRITICAL | 2-3h | ⚪ READY | [§ WAVE-A](#wave-a-critical-blockers) |
| **WAVE-B** | P0-CRITICAL | 2-3h | ⚪ BLOCKED | [§ WAVE-B](#wave-b-operability-monitoring) |
| **WAVE-C** | P0-CRITICAL | 2-3h | ⚪ BLOCKED | [§ WAVE-C](#wave-c-configuration-scalability) |
| **WAVE-D** | P0-CRITICAL | 1-2h | ⚪ BLOCKED | [§ WAVE-D](#wave-d-mcp-architecture-lens) |
| **WAVE-E** | P0-CRITICAL | 2-3h | ⚪ BLOCKED | [§ WAVE-E](#wave-e-validation-gates) |
| **WAVE-F** | P1-HIGH-ROI | 2-3h | ⚪ BLOCKED | [§ WAVE-F](#wave-f-response-templates) |
| **WAVE-G** | P1-HIGH-ROI | 2-3h | ⚪ BLOCKED | [§ WAVE-G](#wave-g-cleanup-alignment) |

---

## 🔥 WAVE-A: Critical Blockers

### Quick Reference
- **Session ID:** WAVE-A-20260212-01
- **Duration:** 2-3 hours
- **Token Budget:** ~150k tokens
- **Dependencies:** None (READY NOW)
- **Deliverables:** 4 test fixes + 15 new tests + 2 commits

### Autonomous Execution Command

Copy and paste into GitHub Copilot Chat:

```
/implement WAVE-A: Critical Blockers Resolution

Authority: cortex-registry/_cortex-master/AUTONOMOUS-WAVE-EXECUTION-GUIDE.md
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-A-20260212-01
Token Budget: <150k tokens

Scope:
1. Fix 4 test import errors (SharedContext from phase_context_resolver.py)
   - tests/unit/agents/test_master_plan_auditor_integration.py
   - tests/unit/agents/test_meta_auditor_integration.py
   - tests/unit/infrastructure/test_prometheus_metrics.py
   - tests/unit/orchestrators/core/test_phase_resolver_collaboration.py

2. ENH-063 Phase 2: Reliability & Performance (3 fixes)
   - Circuit breakers for git operations (cortex/repositories/git_operations.py)
   - Async git operations (non-blocking asyncio.subprocess)
   - Debug orchestrator race condition fix (asyncio.Lock for shared state)

3. TDD Requirements (RED→GREEN→REFACTOR)
   - tests/unit/repositories/test_git_circuit_breaker.py (5+ tests)
   - tests/unit/repositories/test_git_async.py (5+ tests)
   - tests/unit/orchestrators/support/test_debug_race_condition.py (5+ tests)
   - Total: 15+ new tests (all must pass)

4. Documentation Updates
   - cortex-registry/_cortex-master/index.yaml (ENH-063 progress)
   - cortex-registry/_cortex-master/enhancements/ENH-063.yaml (Phase 2 complete)

Success Criteria:
- [ ] All 21,456 tests passing (0 failures, 0 errors)
- [ ] 2 commits: AC-WAVE-A-001 (test fixes), AC-WAVE-A-002 (ENH-063 Phase 2)
- [ ] Git operations non-blocking (integration test verified)
- [ ] Master plan updated (index.yaml + ENH-063.yaml)

Expected Output:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WAVE-A: Critical Blockers Resolution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[████████░░] 80% Task 2: ENH-063 Phase 2
├─ ✅ Task 1: Test import fixes (4 files)
├─ ✅ Circuit breakers (5 tests passing)
├─ ✅ Async git operations (5 tests passing)
├─ 🔵 Race condition fix (3/5 tests)
└─ ⚪ Documentation updates (pending)

Tests: 14/15 | Coverage: 87%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Commit Templates

**Commit 1: Test Import Fixes**
```
AC-WAVE-A-001: Fix test imports (SharedContext)

- Fixed 4 test files importing SharedContext from phase_context_resolver.py
- Verified: 21,441 tests collected, 0 errors
- Files:
  * test_master_plan_auditor_integration.py
  * test_meta_auditor_integration.py
  * test_prometheus_metrics.py
  * test_phase_resolver_collaboration.py

AC_COMPLETE: AC-WAVE-A-001 ✅
```

**Commit 2: ENH-063 Phase 2**
```
AC-WAVE-A-002: ENH-063 Phase 2 complete (Reliability)

Phase 2: Reliability & Performance (3 fixes)
- Circuit breakers for git operations (open after 3 failures)
- Async git operations (non-blocking asyncio.subprocess)
- Debug orchestrator race condition fix (asyncio.Lock)

Tests: 15 new (5 circuit breaker, 5 async, 5 race condition)
Files: git_operations.py, debug_orchestrator.py

ENH-063 Progress: 2/6 phases complete (33%)

AC_COMPLETE: AC-WAVE-A-002 ✅ 15/15 passing
```

### Verification Checklist

After autonomous execution completes:

```bash
# 1. Verify test count
pytest tests/ --co -q | grep "tests collected"
# Expected: 21456 tests collected

# 2. Verify zero errors
pytest tests/ -v --tb=short | grep -E "(FAILED|ERROR)"
# Expected: No output (all passing)

# 3. Verify commits
git log --oneline -2
# Expected: AC-WAVE-A-002, AC-WAVE-A-001

# 4. Verify documentation
grep -A 5 "phase_2:" cortex-registry/_cortex-master/enhancements/ENH-063.yaml
# Expected: status: "complete", completion_date: "2026-02-12"
```

---

## 🔥 WAVE-B: Operability & Monitoring

### Quick Reference
- **Session ID:** WAVE-B-20260212-02
- **Duration:** 2-3 hours
- **Token Budget:** ~180k tokens
- **Dependencies:** WAVE-A complete
- **Deliverables:** 80+ file updates + 15 tests + 2 commits

### Autonomous Execution Command

```
/implement WAVE-B: Operability & Monitoring

Authority: cortex-registry/_cortex-master/AUTONOMOUS-WAVE-EXECUTION-GUIDE.md
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-B-20260212-02
Token Budget: <180k tokens

Prerequisites:
- WAVE-A complete (verify: git log | grep "AC-WAVE-A-002")
- All tests passing (verify: pytest tests/ -v --tb=short)

Scope:
1. ENH-063 Phase 3: Operability & Monitoring (3 fixes)
   - Structured logging (JSON format, 80+ files across cortex/*/*.py)
   - Distributed tracing (OpenTelemetry + Jaeger integration)
   - Liveness probe verification (cortex/mcp/health.py functional test)

2. ENH-063 Phase 4: Authorization & Security (2 fixes)
   - RBAC for MCP endpoints (role-based access control)
   - MCP gateway authorization layer (JWT validation)

3. TDD Requirements (RED→GREEN→REFACTOR)
   - tests/unit/observability/test_structured_logging.py (5+ tests)
   - tests/unit/observability/test_distributed_tracing.py (4+ tests)
   - tests/unit/mcp/test_health_liveness.py (3+ tests)
   - tests/unit/mcp/test_rbac.py (5+ tests)
   - tests/unit/mcp/test_gateway_authorization.py (5+ tests)
   - Total: 22+ new tests (all must pass)

4. Documentation Updates
   - cortex-registry/_cortex-master/index.yaml (ENH-063 progress)
   - cortex-registry/_cortex-master/enhancements/ENH-063.yaml (Phase 3+4 complete)

Success Criteria:
- [ ] All 21,478 tests passing (21,456 + 22 new)
- [ ] 80+ files with structured logging (JSON format)
- [ ] OpenTelemetry spans captured (Jaeger backend)
- [ ] RBAC functional (role-based endpoint access)
- [ ] 2 commits: AC-WAVE-B-001 (Phase 3), AC-WAVE-B-002 (Phase 4)

Expected Timeline:
- Task 1: Structured logging (60 min, 80+ files)
- Task 2: Distributed tracing (30 min, OpenTelemetry)
- Task 3: RBAC + authorization (45 min, JWT validation)
- Task 4: Tests + docs (45 min, 22 tests)
```

### Commit Templates

**Commit 1: Phase 3**
```
AC-WAVE-B-001: ENH-063 Phase 3 complete (Operability)

Phase 3: Operability & Monitoring (3 fixes)
- Structured logging (JSON format, correlation IDs, 80+ files)
- Distributed tracing (OpenTelemetry + Jaeger)
- Liveness probe verification (/health/liveness functional)

Tests: 12 new (5 logging, 4 tracing, 3 health)
Files: cortex/*/*.py (80+ files), opentelemetry_tracing.py, health.py

ENH-063 Progress: 3/6 phases complete (50%)

AC_COMPLETE: AC-WAVE-B-001 ✅ 12/12 passing
```

**Commit 2: Phase 4**
```
AC-WAVE-B-002: ENH-063 Phase 4 complete (Authorization)

Phase 4: Authorization & Security (2 fixes)
- RBAC for MCP endpoints (role-based access control)
- MCP gateway authorization layer (JWT validation)

Tests: 10 new (5 RBAC, 5 gateway authorization)
Files: cortex/mcp/rbac.py (new), cortex/mcp/gateway.py (enhanced)

ENH-063 Progress: 4/6 phases complete (67%)

AC_COMPLETE: AC-WAVE-B-002 ✅ 10/10 passing
```

---

## 🔥 WAVE-C: Configuration & Scalability

### Quick Reference
- **Session ID:** WAVE-C-20260212-03
- **Duration:** 2-3 hours
- **Token Budget:** ~160k tokens
- **Dependencies:** WAVE-B complete
- **Deliverables:** ENH-063 COMPLETE (15/15 fixes) + 25 tests + 2 commits

### Autonomous Execution Command

```
/implement WAVE-C: Configuration & Scalability + ENH-063 Integration

Authority: cortex-registry/_cortex-master/AUTONOMOUS-WAVE-EXECUTION-GUIDE.md
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-C-20260212-03
Token Budget: <160k tokens

Prerequisites:
- WAVE-B complete (verify: git log | grep "AC-WAVE-B-002")
- ENH-063 4/6 phases complete (verify: grep "progress:" ENH-063.yaml)

Scope:
1. ENH-063 Phase 5: Configuration & State (2 fixes)
   - Config drift detection (10s alerts for environment changes)
   - Session management (Redis backend, distributed sessions)

2. ENH-063 Phase 6: Scalability & Resources (1 fix)
   - MCP server connection pooling (10x throughput improvement)

3. ENH-063 Integration Testing & Verification (20+ tests)
   - E2E security tests (authentication + authorization)
   - E2E reliability tests (circuit breakers + async operations)
   - E2E observability tests (logging + tracing)
   - Production readiness verification

4. Documentation Updates
   - cortex-registry/_cortex-master/index.yaml (ENH-063 complete)
   - cortex-registry/_cortex-master/enhancements/ENH-063.yaml (all 6 phases)
   - ENH-063-COMPLETION-REPORT.md (summary document)

Success Criteria:
- [ ] All 21,503 tests passing (21,478 + 25 new)
- [ ] ENH-063 status: "complete" (15/15 fixes)
- [ ] Config drift detection functional (<10s response)
- [ ] Session management operational (Redis)
- [ ] Connection pooling deployed (measured 10x improvement)
- [ ] 2 commits: AC-WAVE-C-001 (Phase 5+6), AC-WAVE-C-002 (Integration)

Expected Timeline:
- Task 1: Config drift + sessions (60 min)
- Task 2: Connection pooling (30 min)
- Task 3: Integration tests (60 min, 20+ tests)
- Task 4: Completion report (30 min)
```

### Commit Templates

**Commit 1: Phase 5+6**
```
AC-WAVE-C-001: ENH-063 Phase 5+6 complete (Config + Scalability)

Phase 5: Configuration & State (2 fixes)
- Config drift detection (10s alerts)
- Session management (Redis backend)

Phase 6: Scalability & Resources (1 fix)
- MCP server connection pooling (10x throughput)

Tests: 10 new (5 config drift, 3 session, 2 pooling)
Files: cortex/config/drift_detection.py, cortex/mcp/session_manager.py,
       cortex/mcp/connection_pool.py

ENH-063 Progress: 6/6 phases complete (100%)

AC_COMPLETE: AC-WAVE-C-001 ✅ 10/10 passing
```

**Commit 2: Integration**
```
AC-WAVE-C-002: ENH-063 Integration complete (Production Ready)

ENH-063: Production Architecture Remediation COMPLETE
- 15 P0/P1 fixes deployed (security + reliability + observability)
- 6 phases: Security → Reliability → Observability → Authorization → Config → Scalability

Integration Tests: 15 new (5 E2E security, 5 E2E reliability, 5 E2E observability)
Total Tests Added: 62 tests (ENH-063 complete)
Files: tests/integration/test_enh_063_e2e_*.py

ENH-063 Status: COMPLETE ✅

Success Metrics:
- MCP authentication: JWT enabled
- Command injection: 4 vulnerabilities eliminated
- Git operations: Non-blocking with circuit breakers
- Logging: JSON structured (80+ files)
- Tracing: OpenTelemetry + Jaeger
- RBAC: Role-based access control
- Config drift: <10s detection
- Session management: Redis distributed
- Connection pooling: 10x throughput
- Production score: 3.6/10 → 8.5/10

AC_COMPLETE: AC-WAVE-C-002 ✅ 15/15 passing
```

---

## 🔥 WAVE-D: MCP Architecture + LENS

### Quick Reference
- **Session ID:** WAVE-D-20260212-04
- **Duration:** 1-2 hours
- **Token Budget:** ~100k tokens
- **Dependencies:** WAVE-C complete
- **Deliverables:** ENH-066 verified + phase-54 complete + 10 tests

### Autonomous Execution Command

```
/implement WAVE-D: MCP Architecture Docs + LENS Phase 2 Stub

Authority: cortex-registry/_cortex-master/AUTONOMOUS-WAVE-EXECUTION-GUIDE.md
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-D-20260212-04
Token Budget: <100k tokens

Prerequisites:
- WAVE-C complete (verify: git log | grep "AC-WAVE-C-002")
- ENH-063 complete (verify: grep "status: complete" ENH-063.yaml)

Scope:
1. ENH-066: MCP Pylance-Style Architecture Validation
   - Verify .github/prompts/MCP-SETUP-GUIDE.md accuracy
   - Test cross-platform setup script (scripts/setup-mcp.py)
   - Validate Pylance-style auto-start documentation
   - Create validation test suite

2. phase-54: LENS Phase 2 Stub Removal
   - Remove hardcoded relationships (cortex/brain/lens/pipeline.py:259-260)
   - Connect to real RelationshipTraversalEngine
   - Integration test with cortex/intelligence/ layer
   - Verify 90% dynamic codebase understanding

3. TDD Requirements (RED→GREEN→REFACTOR)
   - tests/integration/test_mcp_setup_validation.py (5+ tests)
   - tests/integration/test_lens_phase2_dynamic.py (5+ tests)
   - Total: 10+ new tests (all must pass)

4. Documentation Updates
   - cortex-registry/_cortex-master/index.yaml (phase-54 complete)
   - ENH-066 status: "verified" (documentation accuracy confirmed)

Success Criteria:
- [ ] All 21,513 tests passing (21,503 + 10 new)
- [ ] ENH-066 verified (Pylance docs accurate)
- [ ] LENS Phase 2 stub removed (fully dynamic)
- [ ] 1 commit: AC-WAVE-D-001 (ENH-066 + phase-54)

Expected Timeline:
- Task 1: MCP docs validation (30 min, 5 tests)
- Task 2: LENS stub removal (45 min, 5 tests)
- Task 3: Integration tests (30 min)
- Task 4: Documentation (15 min)
```

---

## 🔥 WAVE-E: Validation Gates

### Quick Reference
- **Session ID:** WAVE-E-20260212-05
- **Duration:** 2-3 hours
- **Token Budget:** ~180k tokens
- **Dependencies:** WAVE-D complete
- **Deliverables:** phase-51 + phase-48 S1-S3 + 25 tests

### Autonomous Execution Command

```
/implement WAVE-E: Validation Gates (Environment + Holistic + Challenge)

Authority: cortex-registry/_cortex-master/AUTONOMOUS-WAVE-EXECUTION-GUIDE.md
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-E-20260212-05
Token Budget: <180k tokens

Prerequisites:
- WAVE-D complete (verify: git log | grep "AC-WAVE-D-001")
- Foundation complete (ENH-063, ENH-066, phase-54 all done)

Scope:
1. phase-51: Environment Integrity Agent
   - MCP pre-flight validation (3-method detection)
   - Tool availability checking
   - Environment variable verification
   - Network port checking
   - Integration with IntentRouter

2. phase-48 S1-S3: Holistic Validation Gate Foundation
   - Stage 1: Challenge generation engine (LENS-based)
   - Stage 2: Disagreement detection (compare alternatives)
   - Stage 3: DoR confidence scoring (readiness assessment)

3. TDD Requirements (RED→GREEN→REFACTOR)
   - tests/unit/governance/enforcement/test_environment_integrity_agent.py (8+ tests)
   - tests/unit/validation/test_challenge_generation.py (8+ tests)
   - tests/unit/validation/test_disagreement_detection.py (5+ tests)
   - tests/unit/validation/test_dor_confidence.py (4+ tests)
   - Total: 25+ new tests (all must pass)

4. Documentation Updates
   - cortex-registry/_cortex-master/index.yaml (phase-51 + phase-48 S1-S3)
   - phase-51-completion-report.md
   - phase-48-s1-s3-completion-report.md

Success Criteria:
- [ ] All 21,538 tests passing (21,513 + 25 new)
- [ ] MCP pre-flight checks functional (3 detection methods)
- [ ] Challenge gate operational (LENS-based alternatives)
- [ ] DoR confidence scoring deployed
- [ ] 2 commits: AC-WAVE-E-001 (phase-51), AC-WAVE-E-002 (phase-48 S1-S3)

Expected Timeline:
- Task 1: Environment integrity (75 min, 8 tests)
- Task 2: Challenge generation (60 min, 8 tests)
- Task 3: Disagreement + DoR (45 min, 9 tests)
- Task 4: Integration + docs (30 min)
```

---

## 🔥 WAVE-F: Response Templates

### Quick Reference
- **Session ID:** WAVE-F-20260212-06
- **Duration:** 2-3 hours
- **Token Budget:** ~170k tokens
- **Dependencies:** WAVE-E complete
- **Deliverables:** ENH-082 S1 + ENH-084 S1 + 30 tests

### Autonomous Execution Command

```
/implement WAVE-F: Response Templates + Phase Standards

Authority: cortex-registry/_cortex-master/AUTONOMOUS-WAVE-EXECUTION-GUIDE.md
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-F-20260212-06
Token Budget: <170k tokens

Prerequisites:
- WAVE-E complete (verify: git log | grep "AC-WAVE-E-002")
- Foundation + Gates complete (Waves A-E)

Scope:
1. ENH-082 Stage 1: Unified Response Engine Integration
   - Integrate 72 orchestrators with UnifiedResponseEngine
   - Standardize response headers across all orchestrators
   - ASCII progress bars for all long-running operations
   - Status icons (🟢✅⚪🔴🔵🟡) consistency

2. ENH-084 Stage 1: Standard Phase Creation Template
   - Create phase-creation-template.yaml (SSOT)
   - Develop phase-create CLI tool
   - Auto-generate test stubs + directory structure
   - Governance enforcement (CORE-042 terminology)

3. TDD Requirements (RED→GREEN→REFACTOR)
   - tests/integration/test_unified_response_engine_orchestrators.py (15+ tests)
   - tests/unit/tools/test_phase_create_cli.py (10+ tests)
   - tests/integration/test_phase_template_validation.py (5+ tests)
   - Total: 30+ new tests (all must pass)

4. Documentation Updates
   - cortex-registry/_cortex-master/index.yaml (ENH-082/084 S1 complete)
   - ENH-082-S1-completion-report.md
   - ENH-084-S1-completion-report.md

Success Criteria:
- [ ] All 21,568 tests passing (21,538 + 30 new)
- [ ] 72/72 orchestrators using UnifiedResponseEngine
- [ ] Phase creation CLI functional (template-based)
- [ ] 50% faster phase creation (measured)
- [ ] 2 commits: AC-WAVE-F-001 (ENH-082 S1), AC-WAVE-F-002 (ENH-084 S1)

Expected Timeline:
- Task 1: Response engine integration (90 min, 72 orchestrators)
- Task 2: Phase creation template + CLI (60 min)
- Task 3: Tests (45 min, 30 tests)
- Task 4: Documentation (25 min)
```

---

## 🔥 WAVE-G: Cleanup & Alignment

### Quick Reference
- **Session ID:** WAVE-G-20260212-07
- **Duration:** 2-3 hours
- **Token Budget:** ~160k tokens
- **Dependencies:** WAVE-F complete
- **Deliverables:** ENH-085 S1-S2 + ENH-086 S1 + 30 tests

### Autonomous Execution Command

```
/implement WAVE-G: Cleanup Audit + Architecture Alignment

Authority: cortex-registry/_cortex-master/AUTONOMOUS-WAVE-EXECUTION-GUIDE.md
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-G-20260212-07
Token Budget: <160k tokens

Prerequisites:
- WAVE-F complete (verify: git log | grep "AC-WAVE-F-002")
- Response templates + phase standards deployed

Scope:
1. ENH-085 S1-S2: Completed Phase Cleanup Audit
   - Stage 1: Scan cortex-registry/phases/completed/ (50+ phases)
   - Stage 2: Identify orphaned files, dead references, unused code
   - Cleanup execution: Archive + delete (15-25% reduction)
   - Verification: All references resolved

2. ENH-086 S1: Architecture Alignment Verification
   - CORE rules compliance audit (30/30 rules)
   - MCP-FIRST violations detection (0 target)
   - Test coverage verification (≥80% target)
   - Architecture documentation sync

3. TDD Requirements (RED→GREEN→REFACTOR)
   - tests/integration/test_cleanup_audit_phase_files.py (10+ tests)
   - tests/integration/test_cleanup_verification.py (5+ tests)
   - tests/unit/governance/test_core_rules_compliance.py (10+ tests)
   - tests/integration/test_mcp_first_violations.py (5+ tests)
   - Total: 30+ new tests (all must pass)

4. Documentation Updates
   - cortex-registry/_cortex-master/index.yaml (ENH-085/086 S1 complete)
   - ENH-085-S1-S2-completion-report.md
   - ENH-086-S1-completion-report.md
   - CLEANUP-AUDIT-SUMMARY.md

Success Criteria:
- [ ] All 21,598 tests passing (21,568 + 30 new)
- [ ] Codebase reduced 15-25% (measured LOC diff)
- [ ] 100% CORE rules compliance (30/30)
- [ ] 0 MCP-FIRST violations detected
- [ ] Test coverage ≥80% across all modules
- [ ] 2 commits: AC-WAVE-G-001 (ENH-085 S1-S2), AC-WAVE-G-002 (ENH-086 S1)

Expected Timeline:
- Task 1: Cleanup audit (60 min, scan + identify)
- Task 2: Cleanup execution (45 min, archive + delete)
- Task 3: Alignment verification (60 min, compliance audit)
- Task 4: Tests + docs (45 min, 30 tests)
```

---

## 📊 Progress Tracking Dashboard

### Session Completion Matrix

| Wave | Start Date | End Date | Duration | Tests Added | Commits | Status |
|------|------------|----------|----------|-------------|---------|--------|
| WAVE-A | TBD | TBD | - | 0/15 | 0/2 | ⚪ PENDING |
| WAVE-B | TBD | TBD | - | 0/22 | 0/2 | ⚪ BLOCKED |
| WAVE-C | TBD | TBD | - | 0/25 | 0/2 | ⚪ BLOCKED |
| WAVE-D | TBD | TBD | - | 0/10 | 0/1 | ⚪ BLOCKED |
| WAVE-E | TBD | TBD | - | 0/25 | 0/2 | ⚪ BLOCKED |
| WAVE-F | TBD | TBD | - | 0/30 | 0/2 | ⚪ BLOCKED |
| WAVE-G | TBD | TBD | - | 0/30 | 0/2 | ⚪ BLOCKED |

**Total Tests to Add:** 157 tests  
**Total Commits:** 13 commits  
**Total Duration:** 12-18 hours (7 sessions)

### Cumulative Test Count Progression

| After Wave | Test Count | Delta | Cumulative |
|------------|------------|-------|------------|
| Baseline | 21,441 | - | 21,441 |
| WAVE-A | 21,456 | +15 | 21,456 |
| WAVE-B | 21,478 | +22 | 21,478 |
| WAVE-C | 21,503 | +25 | 21,503 |
| WAVE-D | 21,513 | +10 | 21,513 |
| WAVE-E | 21,538 | +25 | 21,538 |
| WAVE-F | 21,568 | +30 | 21,568 |
| WAVE-G | 21,598 | +30 | 21,598 |

**Target:** 21,598 tests (100% passing, 0 errors)

---

## 🎯 Quick Start Commands

### For Session-by-Session Execution

**Start WAVE-A immediately:**
```
/implement WAVE-A: Critical Blockers Resolution

See: cortex-registry/_cortex-master/AUTONOMOUS-WAVE-EXECUTION-GUIDE.md § WAVE-A
```

**After WAVE-A completes, start WAVE-B:**
```
/implement WAVE-B: Operability & Monitoring

Prerequisites: WAVE-A complete
See: cortex-registry/_cortex-master/AUTONOMOUS-WAVE-EXECUTION-GUIDE.md § WAVE-B
```

**Continue the sequence:**
```
WAVE-C → WAVE-D → WAVE-E → WAVE-F → WAVE-G
```

### For Batch Verification

**Check current wave status:**
```bash
# Current wave
grep -A 10 "waves:" cortex-registry/_cortex-master/index.yaml | grep -E "(wave: |status: )"

# Test count
pytest tests/ --co -q | grep "tests collected"

# Recent commits
git log --oneline -10 | grep "AC-WAVE"
```

---

## 📝 Notes

1. **Silent Execution:** All waves execute autonomously with ASCII progress bars only
2. **Token Budget:** Each wave designed to stay <200k tokens (monitored during execution)
3. **TDD Enforcement:** Every wave follows RED→GREEN→REFACTOR (no code before tests)
4. **Dependency Chain:** Must execute in order (A→B→C→D→E→F→G)
5. **Session Scope:** Each wave = 1 GitHub Copilot Chat session (2-4 hours)
6. **Exit Criteria:** Tests passing + commits pushed + docs updated = wave complete

---

**Authority:** cortex-architect.prompt.md v15.3 + Implementation Reality Sync 2026-02-12  
**Orchestrator:** MasterOrchestrator → IntentRouter → TDDOrchestrator (per wave)  
**Governance:** CORE-008 (TDD), CORE-049 (Silent Autonomous), CORE-048 (Holistic Validation)
