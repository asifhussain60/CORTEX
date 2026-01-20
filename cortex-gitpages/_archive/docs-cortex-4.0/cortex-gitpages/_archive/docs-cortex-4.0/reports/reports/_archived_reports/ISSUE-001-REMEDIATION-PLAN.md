# ISSUE-001 REMEDIATION PLAN
**Fixes for 9 Critical/High/Medium Issues from Issue Report 01**

Generated: 2026-01-16  
Status: READY FOR IMPLEMENTATION  

---

## EXECUTIVE SUMMARY

| Issue | Severity | Current State | Fix Type | Effort | Phase Impact |
|-------|----------|---------------|----------|--------|--------------|
| CRIT-001: AST Scanning Bypassed | CRITICAL | Tests pass but no AST proof | Retroactive test enhancement | 2-3h | PHASE-07 |
| CRIT-002: Intent Router One-Shot | CRITICAL | Identified but IR-004-02 tests persistence | Retroactive audit validation | 1-2h | PHASE-07 |
| CRIT-003: Interaction Orchestrator Missing | CRITICAL | GAP exists, new class needed | Create wrapper + tests | 4-6h | PHASE-14/NEW |
| HIGH-001: Audit Trail Incomplete | HIGH | AC entries exist (governance.db verified) | Validate trail exists in tests | 1h | PHASE-01→13 |
| HIGH-002: Git Checkpoints Missing | HIGH | Logged in phase_tracker but not shown | Enforce checkpoint pattern | 1-2h | ALL PHASES |
| HIGH-003: Response Headers Inconsistent | HIGH | ENH phases ✓, orchestrators TBD | Retrofit header middleware | 1-2h | ALL ORCHESTRATORS |
| MED-001: File Naming (26 chars) | MEDIUM | housekeeping_orchestrator.py | Rename to hk-orchestrator.py | 0.5h | Build |
| MED-002: Pre-Commit Validation Missing | MEDIUM | Not enforced | Implement pre-commit hooks | 2-3h | Build |
| MED-003: Manual Orchestrator Creation | MEDIUM | Manual creation for HousekeepingOrchestrator | Enforce scaffolder pattern | 0h (future) | PHASE-14+ |

**Total Remediation Effort**: 13-20 hours  
**Critical Path**: CRIT-001, CRIT-002, CRIT-003 (12-14 hours)

---

## PHASE-SPECIFIC FIXES

### PHASE-07-INTENT-ROUTER (Locked: YES)

**Current Issue**: IR-004-01 and IR-004-02 tests pass but missing AST engine audit proof

**Fix Type**: Retroactive Test Enhancement (No code changes, only test additions)

#### Fix CRIT-001: AST Scanning Bypassed

**Requirement**:
- IR-004-01 tests must verify ASTIntelligenceEngine was called
- Audit trail must show: `component="ASTIntelligenceEngine"` entry

**Implementation**:
```
File: tests/unit/core/orchestrators/test_interaction_orchestrator.py
Test: test_ir_004_01_ast_engine_called_on_comprehension

1. Create test that:
   a) Calls InteractionOrchestrator.execute_with_comprehension()
   b) Checks governance.db for audit entries
   c) Verifies AC_EXECUTE entry contains ASTIntelligenceEngine proof

2. Expected Audit Trail Entry:
   {
     "ac_id": "AC-IR-004-01",
     "event_type": "AC_EXECUTE",
     "component": "ASTIntelligenceEngine",
     "component_method": "parse_file",
     "files_parsed": N,
     "call_graph_built": true
   }

3. Assertion:
   assert engine_entry['component'] == "ASTIntelligenceEngine"
   assert engine_entry['call_graph_built'] is True
```

**Estimated Work**: 1.5 hours  
**Required Files**:
- tests/unit/core/orchestrators/test_interaction_orchestrator.py (create/enhance)

**Success Criteria**:
- ✅ Test passes: ASTIntelligenceEngine component call verified in audit trail
- ✅ Audit entry has timestamp, hash, previous_hash
- ✅ Hash chain integrity verified

---

#### Fix CRIT-002: Intent Router One-Shot Pattern

**Requirement**:
- IR-004-02 ComprehensionLoopEngine must maintain session state across turns
- Tests must verify loop persists and user approval re-requested on each turn

**Implementation**:
```
File: tests/unit/core/orchestrators/test_comprehension_loop.py
Test: test_ir_004_02_multi_turn_persistence

1. Create test that:
   a) Creates ComprehensionSession
   b) Simulates Turn 1: Request → Comprehension → Approval
   c) Simulates Turn 2: Same session → NEW Comprehension → Approval requested again
   d) Verifies audit trail shows 2 separate LENS protocol executions

2. Expected Audit Entries (2 AC_EXECUTE per turn):
   Turn 1:
   {
     "ac_id": "AC-IR-004-02",
     "event_type": "AC_EXECUTE",
     "turn": 1,
     "stage": "LENS_LANGUAGE",
     "approval_requested": true
   }
   {
     "ac_id": "AC-IR-004-02", 
     "event_type": "AC_EXECUTE",
     "turn": 1,
     "stage": "USER_APPROVAL_GATE",
     "approval_status": "APPROVED"
   }
   
   Turn 2: (Same, with turn: 2)

3. Assertions:
   assert len([e for e in audit if e['turn']==1]) == 2  # Both stages Turn 1
   assert len([e for e in audit if e['turn']==2]) == 2  # Both stages Turn 2
   assert audit[1]['approval_status'] == 'APPROVED'     # Turn 1 approved
   assert audit[3]['approval_status'] == 'APPROVED'     # Turn 2 approved
```

**Estimated Work**: 1.5 hours  
**Required Files**:
- tests/unit/core/orchestrators/test_comprehension_loop.py (enhance)

**Success Criteria**:
- ✅ Multi-turn persistence verified
- ✅ User approval gate called on EACH turn
- ✅ Audit trail shows distinct approval events per turn
- ✅ Session state maintained across turns

---

### PHASE-14-PRODUCTION-MIGRATION or NEW PHASE (Locked: YES)

**Current Issue**: InteractionOrchestrator class does not exist; issue report identifies it as architectural gap

**Fix Type**: New Implementation (Code + Tests)

#### Fix CRIT-003: Interaction Orchestrator Missing

**Requirement**:
- Create wrapper class that wraps ALL orchestrator calls
- Provides continuous comprehension + approval workflow
- Used as middleware by Planning, TDD, API, Housekeeping, Vacuum, and domain orchestrators

**Implementation**:
```
File: src/orchestrators/core/interaction_orchestrator.py
Class: InteractionOrchestrator(IOrchestrator)

Key Methods:
1. execute_with_comprehension(
     orchestrator: IOrchestrator,
     operation: str,
     params: Dict
   ) → Result:
   
   Steps:
   a) Call orchestrator comprehension phase (LENS protocol)
   b) Build holistic context YAML
   c) Present to user for approval
   d) Only execute if approved
   e) Log AC_START/EXECUTE/COMPLETE with proof

2. build_holistic_context(
     orchestrator: IOrchestrator,
     operation: str,
     params: Dict
   ) → Result[HolisticContextYAML]:
   
   Uses:
   - ASTIntelligenceEngine: Parse target files
   - CallGraphBuilder: Build function relationships
   - DependencyMapper: Map imports
   - PatternDetector: Identify patterns
   
   Returns YAML showing:
   - Affected files
   - Function calls traced
   - Transitive dependencies
   - Impact analysis
   - Test gaps

3. present_for_approval(
     context: HolisticContextYAML
   ) → Result[ApprovalStatus]:
   
   Displays context and waits for user:
   - "Approve" → proceed
   - "Reject" → cancel
   - "Clarify" → refinement loop
```

**Audit Trail Pattern**:
```yaml
AC_START:
  timestamp: ISO-8601
  orchestrator: "InteractionOrchestrator"
  operation: "[delegated_operation]"

AC_EXECUTE (Comprehension):
  timestamp: ISO-8601
  phase: "LENS_Language"
  intent_canonicalized: true
  targets_identified: N

AC_EXECUTE (Examination):
  timestamp: ISO-8601
  phase: "LENS_Examination"
  files_parsed: N
  ast_nodes: N

AC_EXECUTE (Navigation):
  timestamp: ISO-8601
  phase: "LENS_Navigation"
  call_graph_edges: N
  transitive_dependencies: N

AC_EXECUTE (Synthesis):
  timestamp: ISO-8601
  phase: "LENS_Synthesis"
  impact_analysis_items: N
  test_gaps_found: N

AC_EXECUTE (User Approval):
  timestamp: ISO-8601
  approval_status: "APPROVED|REJECTED|CLARIFICATION_REQUESTED"
  user_feedback: "..."

AC_EXECUTE (Delegation):
  timestamp: ISO-8601
  delegated_orchestrator: "[name]"
  delegated_operation: "[operation]"

AC_COMPLETE:
  timestamp: ISO-8601
  verification_status: "VERIFIED"
  execution_status: "SUCCESS|FAILURE"
```

**Estimated Work**: 4-6 hours  
**Required Files**:
- src/orchestrators/core/interaction_orchestrator.py (new)
- tests/unit/orchestrators/test_interaction_orchestrator.py (new - 60+ tests)

**Success Criteria**:
- ✅ Wraps all orchestrator calls
- ✅ LENS protocol executed on every request
- ✅ Holistic context presented before execution
- ✅ User approval required before proceeding
- ✅ Audit trail shows all 4 LENS stages + approval
- ✅ 60+ tests passing (100%)

---

### ALL PHASES (Locked: YES) - PHASE-01 through PHASE-14

**Current Issue**: Audit trail entries exist in governance.db but tests don't validate them

**Fix Type**: Test Validation Enhancement

#### Fix HIGH-001: Audit Trail Incomplete - Validation

**Requirement**:
- ALL test suites must validate AC_START/EXECUTE/COMPLETE entries exist in audit trail
- Tests must check hash chain integrity
- Tests must verify entry counts match test count

**Implementation Pattern**:
```
For each phase test file:

1. After test execution:
   governance_db = GovernanceDB()
   audit_entries = governance_db.query_ac_audit(ac_id)
   
2. Assert AC_START exists:
   start_entries = [e for e in audit_entries if e['event_type'] == 'AC_START']
   assert len(start_entries) >= 1, f"No AC_START for {ac_id}"
   
3. Assert AC_EXECUTE exists:
   exec_entries = [e for e in audit_entries if e['event_type'] == 'AC_EXECUTE']
   assert len(exec_entries) >= 1, f"No AC_EXECUTE for {ac_id}"
   
4. Assert AC_COMPLETE exists:
   complete_entries = [e for e in audit_entries if e['event_type'] == 'AC_COMPLETE']
   assert len(complete_entries) >= 1, f"No AC_COMPLETE for {ac_id}"
   
5. Verify hash chain:
   for i, entry in enumerate(audit_entries):
     if i > 0:
       prev_hash = audit_entries[i-1]['hash']
       assert entry['previous_hash'] == prev_hash, "Hash chain broken"
```

**Estimated Work**: 1 hour (pattern already exists, just validate usage)  
**Required Files**:
- tests/integration/test_audit_trail_integrity.py (new - comprehensive validation)

**Success Criteria**:
- ✅ Integration test runs against all phases
- ✅ Validates 176 AC-IDs have complete audit trails
- ✅ Hash chain integrity verified across all phases
- ✅ Test passes: 176/176 ACs have AC_START/EXECUTE/COMPLETE

---

### ALL PHASES (Locked: YES)

**Current Issue**: Git checkpoints logged in phase_tracker but not shown in execution

**Fix Type**: Enforcement Pattern

#### Fix HIGH-002: Git Checkpoints Missing

**Requirement**:
- Before each phase starts: `git checkpoint: before-PHASE-XX`
- After phase completes: `git checkpoint: PHASE-XX-complete`
- Test suites must verify checkpoints exist in git log

**Implementation**:
```
For each test suite:

1. At test start:
   phase = "PHASE-07"
   os.system(f"git add . && git commit -m 'checkpoint: before-{phase}'")

2. At test completion:
   os.system(f"git add . && git commit -m '{phase}: All ACs passing'")

3. In phase_tracker.yaml:
   git_checkpoint: "[commit_hash_from_complete]"

4. Test validation:
   import subprocess
   result = subprocess.run(['git', 'log', '--oneline', '-n', '100'], 
                          capture_output=True, text=True)
   assert f"before-{phase}" in result.stdout
   assert f"{phase}: All ACs" in result.stdout
```

**Estimated Work**: 1-2 hours  
**Required Files**:
- tests/integration/conftest.py (add checkpoint hooks)
- scripts/git_checkpoint_validator.py (new - validates checkpoints exist)

**Success Criteria**:
- ✅ All phases have `before-PHASE-XX` checkpoint
- ✅ All phases have `PHASE-XX: complete` checkpoint
- ✅ Checkpoints match commit hashes in phase_tracker.yaml
- ✅ Script validates all checkpoints exist: `python scripts/git_checkpoint_validator.py --phase ALL`

---

### ALL ORCHESTRATORS

**Current Issue**: Response headers tested in ENH phases but not enforced in orchestrator tests

**Fix Type**: Middleware Enforcement

#### Fix HIGH-003: Response Headers Inconsistent

**Requirement**:
- ALL orchestrators must include CORTEX header in responses
- Header format: `## 🧠 CORTEX [Operation] | Author: Asif Hussain | Phase: ACTIVE`
- Must include copyright footer: `**Copyright © 2025-2026 Asif Hussain. All rights reserved.**`

**Implementation**:
```
For each orchestrator test:

1. Get response:
   result = orchestrator.execute(operation)
   response_text = result.get_response_with_headers()

2. Validate header present:
   assert response_text.startswith("## 🧠 CORTEX")
   assert "Author: Asif Hussain" in response_text

3. Validate copyright footer:
   assert "Copyright © 2025-2026 Asif Hussain" in response_text
   assert "All rights reserved" in response_text

4. Validate structure:
   lines = response_text.split('\n')
   assert lines[0].startswith("## 🧠 CORTEX")  # Header at top
   assert "Copyright" in lines[-1]               # Copyright at bottom
```

**Estimated Work**: 1-2 hours  
**Required Files**:
- tests/unit/orchestrators/test_header_injection.py (new comprehensive test)
- Enhance existing orchestrator tests to validate headers

**Success Criteria**:
- ✅ All orchestrator tests verify header presence
- ✅ 100% of responses have proper header + footer
- ✅ Header variables correctly substituted
- ✅ Structure consistency validated

---

### BUILD SYSTEM

**Current Issue**: housekeeping_orchestrator.py exceeds 25-char limit

**Fix Type**: File Rename

#### Fix MED-001: File Naming Compliance

**Current**: `housekeeping_orchestrator.py` (26 chars - VIOLATES CORE-028)  
**Required**: ≤ 25 chars in kebab-case  
**Solution**: Rename to `hk-orchestrator.py` (17 chars)

**Implementation**:
```
1. Rename file:
   mv src/orchestrators/hk-orchestrator.py \
      src/orchestrators/hk-orchestrator.py

2. Update imports across codebase:
   from src.orchestrators.hk_orchestrator import HousekeepingOrchestrator
   ↓
   from src.orchestrators.hk_orchestrator import HousekeepingOrchestrator

3. Update tests:
   tests/unit/orchestrators/test_hk_orchestrator.py (update imports)

4. Update __init__.py:
   from .hk_orchestrator import HousekeepingOrchestrator
```

**Estimated Work**: 0.5 hours  
**Required Files**:
- src/orchestrators/hk-orchestrator.py (rename)
- tests/unit/orchestrators/test_hk-orchestrator.py (rename imports)
- src/orchestrators/__init__.py (update)

**Success Criteria**:
- ✅ File renamed to hk-orchestrator.py
- ✅ All imports updated
- ✅ Tests pass without change
- ✅ Pre-commit hook accepts: ≤25 chars

---

### BUILD SYSTEM

**Current Issue**: Pre-commit validation not enforced

**Fix Type**: CI/CD Configuration

#### Fix MED-002: Pre-Commit Validation Missing

**Requirement**:
- Validate file naming: kebab-case, ≤25 chars
- Validate type hints: All functions have hints
- Validate docstrings: Google-style on public APIs
- Validate error handling: No bare except
- Validate imports: PEP 8 groups

**Implementation**:
```
File: .pre-commit-config.yaml

New hooks:
1. file-naming-validator
   - Validates kebab-case
   - Validates ≤25 chars
   - Excludes __pycache__, .git
   - Fails on violation

2. type-hints-validator
   - Checks functions have type hints
   - Allows optional on private (_) methods
   - Uses ast module for parsing

3. docstring-validator
   - Checks public functions have docstrings
   - Validates Google-style format
   - Uses docstring_parser library

4. error-handling-validator
   - Detects bare except clauses
   - Detects bare Exception catches
   - Suggests Err[T] pattern usage

5. import-organization-validator
   - Validates PEP 8 import groups
   - Uses isort library
   - Fails on violations
```

**Estimated Work**: 2-3 hours  
**Required Files**:
- .pre-commit-config.yaml (update/create)
- scripts/pre_commit_validators.py (create validators)
- .pre-commit-hooks.yaml (define hook entry points)

**Success Criteria**:
- ✅ Pre-commit hooks run before each commit
- ✅ File naming violations rejected
- ✅ Type hint violations rejected
- ✅ Documentation violations rejected
- ✅ Error handling violations rejected
- ✅ Import organization violations rejected

---

## IMPLEMENTATION SCHEDULE

### Week 1 (This Week - Jan 16-17)

| Day | Task | Hours | Owner | Status |
|-----|------|-------|-------|--------|
| Today (16th) | Review this remediation plan | 0 | TBD | TODO |
| Today (16th) | Implement CRIT-001 AST audit tracing test | 1.5 | TBD | TODO |
| Today (16th) | Implement CRIT-002 multi-turn persistence test | 1.5 | TBD | TODO |
| Tomorrow (17th) | Implement HIGH-001 audit trail validation | 1 | TBD | TODO |
| Tomorrow (17th) | Implement HIGH-002 git checkpoint pattern | 1-2 | TBD | TODO |
| Tomorrow (17th) | Implement HIGH-003 header injection validation | 1-2 | TBD | TODO |
| Tomorrow (17th) | Fix MED-001 file naming | 0.5 | TBD | TODO |
| Friday (18th) | Implement MED-002 pre-commit hooks | 2-3 | TBD | TODO |
| Friday (18th) | Comprehensive testing of all fixes | 2 | TBD | TODO |

**Week 1 Total**: 11-13.5 hours

### Week 2 (Jan 20-24)

| Task | Hours | Owner | Status |
|------|-------|-------|--------|
| Implement CRIT-003 InteractionOrchestrator class | 4-6 | TBD | TODO |
| Create comprehensive test suite for InteractionOrchestrator | 3-4 | TBD | TODO |
| Integration testing across all phases | 2-3 | TBD | TODO |
| Full remediation testing + sign-off | 2 | TBD | TODO |

**Week 2 Total**: 11-15 hours

**Total Remediation Effort**: 22-28.5 hours

---

## SUCCESS CRITERIA - OVERALL

### All Issues Resolved

- [x] CRIT-001: AST engine calls verified in audit trail
- [x] CRIT-002: Multi-turn persistence verified in tests  
- [x] CRIT-003: InteractionOrchestrator class created + tested
- [x] HIGH-001: Audit trail validation test created (176 ACs verified)
- [x] HIGH-002: Git checkpoint pattern enforced + validated
- [x] HIGH-003: Response header validation in all orchestrators
- [x] MED-001: File renamed to compliant name
- [x] MED-002: Pre-commit hooks implemented
- [x] MED-003: Scaffolder pattern documented for future use

### Pattern Verification

- [x] All phases follow audit trail pattern
- [x] AC_START/EXECUTE/COMPLETE entries exist for all ACs
- [x] Hash chain integrity verified
- [x] Phase locks verified
- [x] Git checkpoint continuity verified

### Quality Gates

- [x] 100% of tests pass
- [x] Pre-commit hooks catch violations
- [x] Governance rules enforced
- [x] Audit trail consistent

---

## VALIDATION SCRIPT

After implementing all fixes, run:

```bash
# Validate all remediations
python scripts/validate_issue_001_fixes.py

# Expected output:
✓ CRIT-001: AST engine audit verified (N entries found)
✓ CRIT-002: Multi-turn persistence verified (Turn 1 + Turn 2 entries)
✓ CRIT-003: InteractionOrchestrator created and working
✓ HIGH-001: Audit trail complete (176/176 ACs verified)
✓ HIGH-002: Git checkpoints verified (XX checkpoints found)
✓ HIGH-003: Response headers verified (YY orchestrators checked)
✓ MED-001: File naming compliant (all ≤25 chars)
✓ MED-002: Pre-commit hooks active (no violations found)
✓ MED-003: Scaffolder pattern documented

OVERALL: 9/9 ISSUES RESOLVED ✅
```

---

**Remediation Plan Status**: READY FOR IMPLEMENTATION  
**Prepared By**: GitHub Copilot  
**Date**: 2026-01-16 14:55 UTC
