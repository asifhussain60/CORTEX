---
# AUDIT LOGGING STANDARD FOR PHASE VALIDATION
# Applies to all roadmap phases in /roadmap/phases/*.yaml
# Authority: CORE-027 (AC_START → AC_EXECUTE → AC_COMPLETE audit trail)

metadata:
  standard_id: "AUDIT-LOG-STANDARD-v1"
  effective_date: "2026-01-20"
  authority: "cortex-builder.prompt.md § CORE-027"
  applies_to: "All phases in _workspaces/roadmap/phases/"
  purpose: "Ensure every phase has meaningful audit logging with test validation proof"

---

## PART 1: AUDIT LOG STRUCTURE (Required in all phase YAML files)

Every phase YAML file MUST include:

```yaml
# At the end of the file, before sign-off section:

audit_and_validation:
  
  # Audit trail tracking AC progression
  audit_trail:
    phase_start:
      timestamp: "To be recorded at phase start"
      baseline_metrics:
        collection_errors: "Number before phase"
        test_count: "Total tests collected"
        module_count: "Modules affected"
    
    ac_start_events:
      # For each AC, record when it was STARTED
      - ac_id: "AC-PHASE-001"
        ac_title: "First acceptance criterion"
        started: "YYYY-MM-DD HH:MM:SS"
        started_by: "[Engineer name]"
        test_command: "pytest path/to/test.py -v"
      
      - ac_id: "AC-PHASE-002"
        ac_title: "Second acceptance criterion"
        started: "YYYY-MM-DD HH:MM:SS"
        started_by: "[Engineer name]"
        test_command: "pytest path/to/test.py -v"
    
    ac_execute_events:
      # For each AC, record EXECUTION data with test results
      - ac_id: "AC-PHASE-001"
        execution_timestamp: "YYYY-MM-DD HH:MM:SS"
        test_output: "N passed, M failed, K skipped"
        test_file: "tests/unit/.../test_module.py"
        pytest_output_snippet: |
          test_function_1 PASSED
          test_function_2 PASSED
          N passed in X.XXs
        pass_percentage: 100%
        verification_method: "pytest"
        verified_by: "[Engineer name]"
      
      - ac_id: "AC-PHASE-002"
        execution_timestamp: "YYYY-MM-DD HH:MM:SS"
        test_output: "N passed, M failed, K skipped"
        test_file: "tests/unit/.../test_module.py"
        pytest_output_snippet: |
          test_function_1 PASSED
          test_function_2 PASSED
          N passed in X.XXs
        pass_percentage: 100%
        verification_method: "pytest"
        verified_by: "[Engineer name]"
    
    ac_complete_events:
      # For each AC, record COMPLETION with evidence
      - ac_id: "AC-PHASE-001"
        ac_title: "First acceptance criterion"
        completion_timestamp: "YYYY-MM-DD HH:MM:SS"
        completion_status: "✅ COMPLETE"
        evidence:
          - "All tests passing (from execute_events above)"
          - "Git commit: [hash] with message"
          - "No collection errors from this AC's modules"
        completed_by: "[Engineer name]"
      
      - ac_id: "AC-PHASE-002"
        ac_title: "Second acceptance criterion"
        completion_timestamp: "YYYY-MM-DD HH:MM:SS"
        completion_status: "✅ COMPLETE"
        evidence:
          - "All tests passing (from execute_events above)"
          - "Git commit: [hash] with message"
          - "No collection errors from this AC's modules"
        completed_by: "[Engineer name]"
    
    phase_end:
      timestamp: "When all ACs complete"
      final_metrics:
        collection_errors: "Final error count"
        test_count: "Total tests passing"
        module_count: "Modules successfully implemented"
        error_reduction: "Start errors → End errors (-X, Y%)"
      phase_duration: "X days, Y hours"
      git_checkpoints: "[List of key commits]"
  
  # Validation evidence supporting test completion
  validation_evidence:
    
    test_results_summary:
      total_acceptance_criteria: N
      criteria_complete: N
      criteria_failed: 0
      criteria_pending: 0
      overall_pass_rate: "100%"
    
    pytest_collection:
      command: "pytest --collect-only _workspaces/roadmap/phases/[this-phase]"
      result: "X tests collected, 0 errors"
      timestamp: "YYYY-MM-DD HH:MM:SS"
    
    test_execution_report:
      command: "pytest tests/unit/[affected-modules]/ -v --tb=short"
      result: "X passed in Y.XXs"
      timestamp: "YYYY-MM-DD HH:MM:SS"
      failure_count: 0
      skip_count: 0
      pass_count: X
    
    type_checking_validation:
      command: "mypy cortex/[affected-modules]/ --strict"
      result: "0 errors"
      timestamp: "YYYY-MM-DD HH:MM:SS"
    
    docstring_coverage:
      command: "pydocstyle cortex/[affected-modules]/"
      result: "100% coverage"
      timestamp: "YYYY-MM-DD HH:MM:SS"
    
    governance_compliance:
      core_008_tests_first: "✅ VERIFIED - Tests run before code"
      core_011_type_hints: "✅ VERIFIED - 100% type hints"
      core_012_docstrings: "✅ VERIFIED - 100% docstrings"
      core_013_no_bare_except: "✅ VERIFIED - No bare except clauses"
      all_governance_rules: "✅ COMPLIANT"
  
  # Git commit trail for this phase
  git_commit_trail:
    summary: "X commits implementing this phase"
    checkpoints:
      - commit_hash: "abc123def456"
        message: "Phase [ID] AC-001: Implementation with N tests passing"
        date: "YYYY-MM-DD HH:MM:SS"
        files_changed: N
        lines_added: N
      
      - commit_hash: "def456ghi789"
        message: "Phase [ID] AC-002: Implementation with N tests passing"
        date: "YYYY-MM-DD HH:MM:SS"
        files_changed: N
        lines_added: N
    
    final_checkpoint: "Phase [ID] COMPLETE - All ACs verified"

```

---

## PART 2: VALIDATION REPORT (Required end-of-phase deliverable)

Each completed phase MUST have an audit report file:

**File naming:** `_workspaces/roadmap/reports/[PHASE-ID]-AUDIT-COMPLETE.yaml`

**File structure:**

```yaml
---
# Phase Audit Report - Final Validation
# Phase: [Phase ID and Title]
# Date: YYYY-MM-DD

metadata:
  phase_id: "[PHASE-E-TDD-IMPLEMENTATION]"
  phase_title: "[Full phase title]"
  completion_date: "YYYY-MM-DD"
  status: "✅ COMPLETE"
  all_acs_verified: true

# Executive Summary
executive_summary: |
  [2-3 sentence summary of what was accomplished]
  
  Starting State:
  - Collection errors: X
  - Test count: Y
  - Module count: Z
  
  Ending State:
  - Collection errors: 0 (reduction: X → 0)
  - Test count: Y (all passing)
  - Module count: Z (all implemented)

# Acceptance Criteria Completion Matrix
acceptance_criteria_matrix:
  ac_count: N
  complete_count: N
  failed_count: 0
  pending_count: 0
  pass_rate: "100%"
  
  details:
    - ac_id: "AC-PHASE-001"
      ac_title: "[Title]"
      requirement: "[What had to be done]"
      status: "✅ COMPLETE"
      tests_passed: "N/N"
      git_commit: "[hash] - [message]"
      verification_date: "YYYY-MM-DD"
      verified_by: "[Name]"
    
    - ac_id: "AC-PHASE-002"
      ac_title: "[Title]"
      requirement: "[What had to be done]"
      status: "✅ COMPLETE"
      tests_passed: "N/N"
      git_commit: "[hash] - [message]"
      verification_date: "YYYY-MM-DD"
      verified_by: "[Name]"

# Test Execution Summary
test_execution:
  total_tests_collected: Y
  total_tests_passed: Y
  total_tests_failed: 0
  pass_rate: "100%"
  test_files: "Z files"
  execution_time: "X.XXs"
  
  test_commands_executed:
    - "pytest tests/unit/[modules]/ -v"
    - "pytest tests/integration/[modules]/ -v"
  
  pytest_output: |
    [Actual pytest summary from final run]
    Y passed in X.XXs

# Validation Results
validation_results:
  
  pytest_collection:
    status: "✅ PASS"
    command: "pytest --collect-only"
    result: "Y tests collected, 0 errors"
    timestamp: "YYYY-MM-DD HH:MM:SS"
  
  pytest_execution:
    status: "✅ PASS"
    command: "pytest tests/unit/ -v"
    result: "Y passed, 0 failed, 0 skipped"
    timestamp: "YYYY-MM-DD HH:MM:SS"
  
  type_checking:
    status: "✅ PASS"
    command: "mypy cortex/ --strict"
    result: "0 errors, 0 warnings"
    timestamp: "YYYY-MM-DD HH:MM:SS"
  
  docstring_coverage:
    status: "✅ PASS"
    command: "pydocstyle cortex/"
    result: "100% of public functions documented"
    timestamp: "YYYY-MM-DD HH:MM:SS"
  
  governance_compliance:
    status: "✅ PASS"
    rules_verified:
      - "CORE-008: Tests before code (verified via git log)"
      - "CORE-011: 100% type hints (verified via mypy --strict)"
      - "CORE-012: Google docstrings (verified via pydocstyle)"
      - "CORE-013: No bare except (verified via grep)"
    timestamp: "YYYY-MM-DD HH:MM:SS"

# Metrics and Impact
metrics:
  
  error_reduction:
    baseline_collection_errors: X
    final_collection_errors: 0
    reduction_count: X
    reduction_percentage: "100%"
  
  code_coverage:
    modules_implemented: Z
    test_coverage: "Y tests"
    average_tests_per_module: "Y/Z"
  
  implementation_velocity:
    phase_duration: "X days, Y hours"
    average_modules_per_day: "Z/X"
    average_loc_per_day: "W"
    average_tests_per_day: "V"
  
  quality_metrics:
    type_hint_coverage: "100%"
    docstring_coverage: "100%"
    governance_compliance: "100%"
    test_pass_rate: "100%"

# Git Commit Summary
git_summary:
  total_commits: N
  commits_by_ac:
    - ac_id: "AC-PHASE-001"
      commits: ["hash1", "hash2"]
    - ac_id: "AC-PHASE-002"
      commits: ["hash3", "hash4"]
  
  key_checkpoints:
    - commit: "[hash]"
      message: "Phase kickoff checkpoint"
      date: "YYYY-MM-DD"
    
    - commit: "[hash]"
      message: "Phase midpoint verification"
      date: "YYYY-MM-DD"
    
    - commit: "[hash]"
      message: "Phase complete - All ACs verified"
      date: "YYYY-MM-DD"

# Phase Sign-Off
sign_off:
  phase_complete: true
  all_acceptance_criteria: "✅ MET"
  test_validation: "✅ PASSED"
  governance_compliance: "✅ VERIFIED"
  
  sign_off_authority: "[Name/Title]"
  sign_off_date: "YYYY-MM-DD"
  
  ready_for_next_phase: true
  blocks_removed: "[List of items that were blocking]"
  
  final_certification: |
    This phase has been completed successfully with:
    - All Y tests passing (Y/Y, 100%)
    - All Z modules implemented
    - 0 collection errors
    - 100% governance compliance
    - Complete git audit trail
    
    PHASE [ID] is CERTIFIED COMPLETE on YYYY-MM-DD

```

---

## PART 3: IMPLEMENTATION GUIDANCE FOR EACH AC

When executing an acceptance criterion, follow this audit trail:

### AC_START Event
```yaml
Before starting work on AC:
- Record: AC ID, title, start timestamp, engineer name
- Command: pytest --collect-only [affected-module]
- Record baseline: "X tests collected, Y errors"
- Record test command for later verification
```

### AC_EXECUTE Event
```yaml
During work on AC:
- Regularly run: pytest [test-file] -v
- After each significant change, capture:
  - Number of tests passing
  - Number of tests failing
  - Specific test names
  - Execution timestamp
- Continue until: All tests for this AC are passing
```

### AC_COMPLETE Event
```yaml
After all tests pass for AC:
- Final test run: pytest [test-file] -v
- Capture: "N passed, 0 failed" output
- Git commit: "Module: [name] - [what implemented]; N tests passing"
- Record: Commit hash, timestamp, what was implemented
- Mark AC status: ✅ COMPLETE
```

---

## PART 4: QUICK CHECKLIST FOR PHASE COMPLETION

Before marking a phase COMPLETE:

```
☐ All acceptance criteria have execution evidence
☐ All ACs show test results (N passed, 0 failed)
☐ pytest --collect-only shows 0 errors for this phase's modules
☐ mypy --strict shows 0 errors for this phase's modules
☐ pydocstyle shows 100% documentation coverage
☐ No bare except: clauses in phase's code
☐ All public functions/classes have type hints
☐ All public functions/classes have docstrings
☐ Git log shows progression from AC_START to AC_COMPLETE
☐ Git commit messages include "N tests passing"
☐ AUDIT-COMPLETE report created in _workspaces/roadmap/reports/
☐ phase YAML file has audit_and_validation section populated
☐ Error count changed (baseline → final shown)
☐ Ready for sign-off section completed
```

---

## PART 5: EXCEPTION HANDLING

If an AC shows failures during audit:

```yaml
# DO NOT mark AC as COMPLETE if:
- ❌ Tests are not passing (any failures)
- ❌ Collection errors still exist
- ❌ mypy --strict shows errors
- ❌ Docstrings are incomplete
- ❌ Bare except: clauses exist
- ❌ Type hints are missing

# Instead:
1. Record the AC as "BLOCKED" in audit trail
2. Note the specific failure in verification_evidence
3. Include error output in audit log
4. Commit with message: "AC-XXX: WIP - N failed, needs work"
5. Continue fixing until all tests pass
6. Only then mark AC_COMPLETE
```

---

## PART 6: AUDIT LOG TEMPLATES FOR COMMON PHASES

Use these templates as starting points for adding audit logging to existing phase files:

### Template A: Infrastructure/Setup Phases (like PHASE-E1)
```yaml
audit_and_validation:
  audit_trail:
    phase_start:
      timestamp: "[To be filled during execution]"
      baseline_metrics:
        collection_errors: "[Count at phase start]"
        test_count: "[Tests affected by this phase]"
    ac_complete_events:
      - ac_id: "AC-PHASE-001"
        completion_status: "✅ COMPLETE"
        evidence:
          - "Infrastructure verified: [description]"
          - "pytest --collect-only: 0 errors"
          - "Git commit: [hash]"
  validation_evidence:
    test_results_summary:
      overall_pass_rate: "[X% after completion]"
```

### Template B: Implementation Phases (like PHASE-E2, E3, E4, E5)
```yaml
audit_and_validation:
  audit_trail:
    ac_execute_events:
      - ac_id: "AC-MODULE-001"
        test_output: "[N passed from pytest run]"
        pytest_output_snippet: |
          [Paste actual test output here]
          N passed in X.XXs
        verified_by: "[Engineer name]"
  validation_evidence:
    test_execution_report:
      command: "pytest tests/unit/[module]/ -v"
      result: "[N passed]"
    type_checking_validation:
      result: "0 errors"
```

### Template C: Validation/Hardening Phases (like PHASE-E6)
```yaml
audit_and_validation:
  validation_evidence:
    test_results_summary:
      total_acceptance_criteria: "[Total ACs in phase]"
      criteria_complete: "[All should equal total]"
      overall_pass_rate: "100%"
    pytest_collection:
      result: "[Total tests] tests collected, 0 errors"
    governance_compliance:
      core_008_tests_first: "✅ VERIFIED"
      core_011_type_hints: "✅ VERIFIED"
      core_012_docstrings: "✅ VERIFIED"
      core_013_no_bare_except: "✅ VERIFIED"
```

---

## PART 7: WHERE TO RECORD AUDIT LOGS

All phase YAML files must have `audit_and_validation` section at end:

| Phase Type | Location | File Name |
|---|---|---|
| Phase specification | `_workspaces/roadmap/phases/` | `PHASE-[ID]-[TITLE].yaml` |
| Final audit report | `_workspaces/roadmap/reports/` | `[PHASE-ID]-AUDIT-COMPLETE.yaml` |
| Execution tracking | `_workspaces/roadmap/` | `PHASE-[ID]-EXECUTION-LOG.md` |

---

## FINAL: VALIDATION THAT THIS STANDARD IS BEING FOLLOWED

To check if all phases have proper audit logging:

```bash
# Check all phases have audit_and_validation section
grep -l "audit_and_validation:" _workspaces/roadmap/phases/*.yaml

# Check all phases have acceptance_criteria_matrix in reports
ls -la _workspaces/roadmap/reports/*-AUDIT-COMPLETE.yaml

# Verify recent git commits mention test counts
git log --oneline | grep "tests passing"
```

---

**This standard ensures:**
1. Every phase has meaningful test validation
2. Audit trail shows AC progression from START → EXECUTE → COMPLETE
3. All validation evidence is recorded
4. No phase completes without test proof
5. Future reviewers can verify work was done correctly

**Authority:** CORE-027 - AC Audit Trail Enforcement
