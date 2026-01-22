# EVAL Track - Autonomous Execution Configuration

**Updated:** 2026-01-22  
**Authority:** cortex-builder.prompt.md §ZERO OUTPUT MODE  
**Scope:** Eval track phases for silent, autonomous execution with real implementations

## Executive Summary

The eval track (machine:eval) has been configured for **fully autonomous, silent execution** with mandatory real implementations (no mocks). All 8 audit/cleanup phases now include:

1. ✅ **Execution mode markers** - silent_autonomous flag on all phases
2. ✅ **No-mocks mandate** - no_mocks_mandate field enforced
3. ✅ **Minimal verbosity** - single-line output per phase completion
4. ✅ **Real implementation requirement** - comprehensive implementation_mandate in execution_config

---

## Updated Configuration in cortex-impl-map.yaml

### execution_config.eval_track_mode

```yaml
eval_track_mode:
  enabled: true
  description: "Silent, autonomous execution for eval track phases"
  machine: "eval"
  execution_style: "silent"
  verbosity: "minimal"  # Only output phase completion lines
  output_per_phase: "single_line_only"
  output_on_error: "error_detail_only"
  no_intermediate_output: true
  no_status_updates: true
  no_progress_reporting: true
  
  implementation_mandate: |
    ✅ REAL IMPLEMENTATIONS REQUIRED - NO MOCKS
    
    ALL eval track phases MUST deliver:
    1. Real code that solves the actual problem (not mock/stub solutions)
    2. Production-ready quality (error handling, logging, type hints, docstrings)
    3. Comprehensive tests that verify real behavior (not just "passes test assertions")
    4. Zero mock implementations - if tests can't be satisfied by real code, redesign tests
    5. Full AC completion - all acceptance criteria truly satisfied
    6. Governance compliance - CORE-001/008/011/012/013/017/026/027 enforced
    
    FORBIDDEN in eval track:
    - Mock objects designed only to pass tests
    - Stub implementations with empty method bodies
    - Hardcoded return values that don't represent real behavior
    - Tests that check for mock presence instead of real functionality
    - Governance rule violations to speed up implementation
    - Incomplete AC implementations
    - Deferred "TODO" work to later phases
```

---

## Updated Eval Track Phases

All eval track phases now include:

### 1. PHASE-EVAL-001-TEST-REMEDIATION (COMPLETED)
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: true
- ✅ implementation_type: "real_code_required"

### 2. PHASE-AUDIT-001-EXPORT-VERIFY
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: true
- ✅ implementation_type: "audit_verification"
- **Purpose:** Verify test collection errors fixed (real verification, not mock data)

### 3. PHASE-AUDIT-002-PHASE-E-VERIFY
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: true
- ✅ implementation_type: "code_quality_audit"
- **Purpose:** Verify Phase E has real implementations (≥90% must be production code)

### 4. PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: true
- ✅ implementation_type: "code_audit"
- **Purpose:** Real categorization of 105 import patterns (not mock analysis)

### 5. PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: true
- ✅ implementation_type: "governance_audit"
- **Purpose:** Real governance compliance verification (actual type hints/docstrings checked)

### 6. CLEANUP-PHASE-001-ROADMAP-MAINTENANCE
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: false (maintenance task)
- ✅ implementation_type: "maintenance"
- **Purpose:** Real cleanup and consolidation (actual YAML modifications)

### 7. PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: false (verification task)
- ✅ implementation_type: "git_verification"
- **Purpose:** Real git verification (actual commits checked/created)

### 8. PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: true
- ✅ implementation_type: "static_analysis"
- **Purpose:** Real static analysis (actual code scanned for compliance)

### 9. PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: true
- ✅ implementation_type: "metrics_analysis"
- **Purpose:** Real coverage analysis (actual pytest coverage run)

### 10. PHASE-KG-001-foundation
- ✅ execution_mode: "silent_autonomous"
- ✅ no_mocks_mandate: true
- ✅ implementation_type: "feature_implementation"
- **Purpose:** Real knowledge graph foundation (production code, not stubs)

---

## Execution Protocol for track:eval

When executing `track:eval` phases:

### Required Behavior
```
✓ phase-id: brief-one-sentence-summary → Next: next-phase-id
✓ next-phase-id: brief-summary → Next: following-phase-id
[continues without pause until all phases complete or blocker encountered]
```

### Forbidden Behavior
❌ Executive summaries  
❌ Multi-line explanations between phases  
❌ "Proceed to next phase?" confirmations  
❌ Status reports or completion documents  
❌ Any .md file creation (except docs/)  
❌ Mock implementations to pass tests  
❌ Stub code with empty method bodies  

### Required Implementation Quality
✅ Real code that actually solves problems  
✅ Production-ready error handling and logging  
✅ 100% type hints on public APIs (CORE-011)  
✅ Google docstrings on public APIs (CORE-012)  
✅ Comprehensive test coverage (not just "passes")  
✅ Full AC completion (not partial/deferred)  
✅ No bare except clauses (CORE-013)  

---

## Key Mandates

### NO MOCK IMPLEMENTATIONS

**FORBIDDEN:**
```python
# ❌ NOT ALLOWED - Mock to pass tests
class AuditVerifier:
    def verify_exports(self):
        return {"status": "passed", "errors": 0}  # Fake data
```

**REQUIRED:**
```python
# ✅ REQUIRED - Real implementation
class AuditVerifier:
    def verify_exports(self) -> AuditResult:
        """Verify exports by actually running pytest.
        
        Args:
            None
            
        Returns:
            AuditResult with actual pytest output parsed
            
        Raises:
            AuditError: If exports verification fails
        """
        result = subprocess.run(
            ["pytest", "tests/", "--collect-only", "-q"],
            capture_output=True,
            text=True
        )
        return self._parse_result(result)
```

### GOVERNANCE COMPLIANCE MANDATORY

All eval track phases MUST comply with:
- **CORE-001:** Production quality code only
- **CORE-008:** Tests-first approach (TDD)
- **CORE-011:** 100% type hints on public functions
- **CORE-012:** Google docstrings on public functions
- **CORE-013:** No bare except clauses
- **CORE-017:** Strict governance enforcement
- **CORE-026:** Git checkpoints before major work
- **CORE-027:** Audit trail (AC_START → AC_EXECUTE → AC_COMPLETE)

---

## Autonomous Execution Flow

```
User: "execute track:eval"

System:
1. Load cortex-impl-map.yaml execution_config
2. Filter phases: machine=="eval" && status!="COMPLETED"
3. Sort by priority + sequence
4. Loop through each phase:
   a. Check dependencies (all prerequisites must be COMPLETED)
   b. If dependency missing: output blocker, stop
   c. Set phase.status = "EXECUTING"
   d. Execute phase implementation (real code, real tests)
   e. Verify completion_verification.success_criteria all pass
   f. If all pass: Set phase.status = "COMPLETED"
      Output: "✓ {phase_id}: {brief_summary} → Next: {next_phase_id}"
      Git commit with eval marker
      Continue to next phase (NO PAUSE)
   g. If fail: Set phase.status = "BLOCKED"
      Output error detail
      Stop execution
5. When all phases complete: "✓ eval track complete (N/N phases)"
```

---

## Files Modified

### cortex-impl-map.yaml
- Added `execution_config.eval_track_mode` section
- Added `execution_mode`, `no_mocks_mandate`, `implementation_type` to all eval phases
- Updated all 8 audit/cleanup phases
- Updated PHASE-KG-001-foundation

### No Phase YAML Files Modified Yet
Individual phase YAML files remain unchanged; they reference these settings via cortex-impl-map.yaml

---

## Testing & Validation

After eval track execution completes:

1. **Verify implementation quality:** All code must be production-ready (not stubs)
2. **Verify test passing:** ≥98% test pass rate across all phases
3. **Verify governance:** No CORE-001/008/011/012/013 violations
4. **Verify git commits:** All phases have commits with "eval:" prefix for tracking

---

## Next Steps

1. **Ready for execution:** Execute `machine:eval` to start autonomous eval track
2. **Single-line output:** Phase completion will show only summary lines
3. **No interruptions:** All phases execute sequentially without user confirmation
4. **Real implementations:** All audits/analyses use real code (pytest, static analysis, git commands)
5. **Track results:** Git commits and updated cortex-impl-map.yaml status fields

---

## References

- **Authority:** cortex-builder.prompt.md §ZERO OUTPUT MODE + §AUTONOMOUS EXECUTION LOOP
- **Governance:** cortex_brain/tier0/governance/core-rules.yaml
- **Related:** REVIEW-CORTEX-20260122.yaml (Findings F001-F012)
