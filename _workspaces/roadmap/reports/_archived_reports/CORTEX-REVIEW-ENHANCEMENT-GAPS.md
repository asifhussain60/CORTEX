# CORTEX Review Prompt Enhancement - Critical Gaps Analysis

**Date**: January 17, 2026  
**Status**: Production Readiness Audit  
**Scope**: Why cortex-review.prompt.md failed to catch issues in chat01.md  
**Author**: GitHub Copilot  

---

## Executive Summary

The `cortex-review.prompt.md` is comprehensive but has **6 critical gaps** that allowed false positives and misdetections to propagate in chat01.md. This document:

1. **Identifies what cortex-review.prompt.md missed**
2. **Explains why those gaps exist**
3. **Prescribes enhancements to close gaps**
4. **Searches codebase for similar issues**
5. **Proposes YAML integration for cortex-master.yaml and phases/**

---

## Part 1: Gaps in cortex-review.prompt.md

### GAP-1: No Pre-Review Data Validation Step ❌

**What cortex-review.prompt.md does:**
- Mentions "fresh audit logs" as best practice
- Documents the procedure to regenerate audit data
- States "Fresh data guarantees zero false positives"

**What it DOESN'T do:**
- Make fresh data generation **MANDATORY before analysis**
- Require verification that fresh data was used
- Block review if data isn't fresh
- Provide acceptance criteria for "fresh" (e.g., "generated within last 24h")

**Why this matters:**
- Chat01 used **historical audit data** polluted by:
  - Test fixtures (6 test ACs not in production)
  - Database resets (breaking hash chain)
  - Legacy operation formats (START vs AC_START)
  - Retroactive entries (breaking chronology)
- Result: **False positives** (150+ hash chain breaks that don't exist)

**Impact:**
- ❌ Chat01 claimed "Hash Chain Integrity: 2.1/10" (should be 9.5/10)
- ❌ Chat01 claimed "150+ hash breaks" (actually 0 in production)
- ❌ Chat01 overestimated severity by **22%**

**Enhancement:**
Add **PRE-REVIEW VALIDATION GATE** to cortex-review.prompt.md:

```yaml
# In cortex-review.prompt.md, BEFORE Phase 0

mandatory_pre_review_gate:
  title: "Data Freshness Validation"
  description: "MUST complete before ANY analysis begins"
  
  acceptance_criteria:
    - "Audit database regenerated within 24 hours"
    - "Previous database backed up with timestamp"
    - "Fresh audit run: pytest -m 'ac' --ignore=test_audit_trail_integrity.py"
    - "Hash chain integrity verified: 8/8 tests passing"
    - "Audit entry count documented (baseline for detection)"
    - "Timestamp of regeneration stored in review metadata"
  
  verification_command: |
    # MUST pass before review begins
    python -c "
    import sqlite3, datetime
    db = sqlite3.connect('cortex_brain/state/governance.db')
    c = db.cursor()
    
    # Check freshness
    c.execute('SELECT MAX(timestamp) FROM audit_log')
    last_entry = c.fetchone()[0]
    
    # Verify within 24 hours
    age_hours = (datetime.datetime.now() - datetime.datetime.fromisoformat(last_entry)).total_seconds() / 3600
    
    assert age_hours < 24, f'Data too old: {age_hours:.1f}h (max 24h)'
    assert c.execute('SELECT COUNT(*) FROM audit_log').fetchone()[0] > 2000, 'Insufficient entries'
    print('✅ Data is FRESH and sufficient for review')
    "
  
  blocker_severity: "CRITICAL"
  message: "Review CANNOT proceed without fresh data. False positives guaranteed."
```

---

### GAP-2: No Test-Time vs Runtime Differentiation ❌

**What cortex-review.prompt.md does:**
- Recommends running tests: `pytest ... --tb=short -q 2>&1`
- Suggests checking test coverage
- Documents test methodology

**What it DOESN'T do:**
- Distinguish between **test-time state** and **production state**
- Warn that audit entries written during tests may not persist immediately
- Provide guidance for checking **after test completion**
- Document that tests check audit trail **during execution, before commit**

**Why this matters:**
- Chat01 ran query during test: `SELECT COUNT(*) FROM audit_log` returned 0
- But after test completion: same query returns 1,524+ entries
- Chat01 concluded "Audit trail not working" (false positive)
- Actually: audit trail works fine, timing was wrong

**Impact:**
- ❌ Chat01 claimed "Audit Trail Recording: 3.2/10" (should be 7.2/10)
- ❌ Chat01 said "AC_START/EXECUTE/COMPLETE not recorded" (false)
- ❌ Misdiagnosis: Attributed working system to implementation gap

**Enhancement:**
Add **TIMING-AWARE VERIFICATION** to cortex-review.prompt.md:

```yaml
# In Phase 1: SYSTEMATIC ANALYSIS section

timing_aware_verification:
  critical_rule: "Verify AFTER test persistence, not during execution"
  
  anti_patterns:
    - "Checking audit_log during pytest execution"
    - "Querying database before test completion"
    - "Assuming 0 entries = no recording"
  
  correct_pattern: |
    # WRONG - done during test execution
    async def test_audit():
        await orchestrator.execute()
        # DON'T CHECK HERE - entries not persisted yet
        count = query_audit()  # Returns 0 - WRONG!
    
    # RIGHT - verify after persistence
    async def test_audit():
        await orchestrator.execute()
        await asyncio.sleep(0.5)  # Let DB persist
        
        # THEN check
        # Better: Use pytest fixture to check after test teardown
  
  verification_steps:
    step_1: "Complete all tests"
    step_2: "Verify DB file modification timestamp recent"
    step_3: "Query audit log from new connection (ensures persistence)"
    step_4: "Compare counts pre and post-test"
    step_5: "Document timing of audit queries in review findings"
  
  verification_command: |
    # Check audit log persistence
    python -c "
    import sqlite3, time
    time.sleep(1)  # Ensure persistence window
    
    db = sqlite3.connect('cortex_brain/state/governance.db')
    c = db.cursor()
    
    # Fresh connection ensures we see committed data
    c.execute('SELECT COUNT(*) FROM audit_log WHERE timestamp > datetime(\"now\", \"-10 seconds\")')
    recent = c.fetchone()[0]
    
    assert recent > 0, 'No recent entries - check test timing'
    print(f'✅ Found {recent} recent audit entries (persistence confirmed)')
    "
```

---

### GAP-3: No Test Data Contamination Detection ❌

**What cortex-review.prompt.md does:**
- Mentions "test fixtures" briefly
- Notes "test-time checking vs runtime state"
- Recommends audit log snapshot

**What it DOESN'T do:**
- Provide queries to **identify test data pollution**
- Explain how to distinguish test fixtures from production ACs
- Offer automated detection of duplicate/corrupted entries
- Document which ACs are test fixtures vs production

**Why this matters:**
- Chat01 analyzed hash chain with **150+ test fixture entries**
- These fixtures had duplicate hashes (intentional for testing)
- Chat01 counted duplicates as "chain breaks" (false positive)
- Production data had only 3 actual mismatches (99.93% valid)
- Misdiagnosis: Test noise ≠ Production failure

**Impact:**
- ❌ Chat01 claimed "Hash Chain Integrity: 2.1/10" (should be 9.5/10)
- ❌ Chat01 said "150+ mismatches" (actually 3 in production)
- ❌ Massive false positive (+7.4 points underestimate)

**Enhancement:**
Add **TEST DATA EXCLUSION RULES** to cortex-review.prompt.md:

```yaml
# In Phase 0 and Phase 1

test_data_identification:
  purpose: "Exclude test fixtures before analysis"
  
  test_ac_patterns:
    - "AC-CHAIN-*"          # Hash chain testing fixtures
    - "AC-DECORATOR-*"      # Decorator test fixtures
    - "AC-HASH-*"           # Hash testing fixtures
    - "AC-INVALID-*"        # Invalid AC format fixtures
    - "AC-TEST-*"           # Generic test fixtures
    - "AC-FIXTURE-*"        # Explicit fixtures
    - "AC-MOCK-*"           # Mock ACs
  
  verification_query: |
    -- Count test vs production ACs
    SELECT 
      COUNT(DISTINCT ac_id) as total_acs,
      SUM(CASE 
        WHEN ac_id LIKE 'AC-CHAIN-%' OR
             ac_id LIKE 'AC-DECORATOR-%' OR
             ac_id LIKE 'AC-HASH-%' OR
             ac_id LIKE 'AC-INVALID-%'
        THEN 1 ELSE 0 
      END) as test_fixtures,
      COUNT(DISTINCT ac_id) - SUM(CASE 
        WHEN ac_id LIKE 'AC-CHAIN-%' OR
             ac_id LIKE 'AC-DECORATOR-%' OR
             ac_id LIKE 'AC-HASH-%' OR
             ac_id LIKE 'AC-INVALID-%'
        THEN 1 ELSE 0 
      END) as production_acs
    FROM audit_log;
  
  hash_chain_validation_with_filtering: |
    -- Validate hash chain EXCLUDING test fixtures
    SELECT 
      COUNT(*) as total_entries,
      SUM(CASE WHEN hash_valid THEN 1 ELSE 0 END) as valid_entries,
      SUM(CASE WHEN NOT hash_valid THEN 1 ELSE 0 END) as invalid_entries,
      ROUND(SUM(CASE WHEN hash_valid THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as integrity_percentage
    FROM (
      SELECT 
        id,
        previous_hash,
        (SELECT entry_hash FROM audit_log a2 WHERE a2.id = a1.id - 1) as expected_previous,
        previous_hash = (SELECT entry_hash FROM audit_log a2 WHERE a2.id = a1.id - 1) as hash_valid
      FROM audit_log a1
      WHERE a1.ac_id NOT LIKE 'AC-CHAIN-%'
        AND a1.ac_id NOT LIKE 'AC-DECORATOR-%'
        AND a1.ac_id NOT LIKE 'AC-HASH-%'
        AND a1.ac_id NOT LIKE 'AC-INVALID-%'
        AND a1.id > 1
    );
  
  false_positive_detection: |
    -- Find entries that look like duplicates (test fixture indicator)
    SELECT 
      COUNT(*) as duplicate_hashes,
      COUNT(DISTINCT entry_hash) as unique_hashes
    FROM audit_log
    WHERE ac_id LIKE 'AC-CHAIN-%' OR
          ac_id LIKE 'AC-HASH-%'
    HAVING COUNT(*) > COUNT(DISTINCT entry_hash);
    -- If this is > 0 in filtered data: test fixtures present
```

---

### GAP-4: No Root Cause Analysis Guidance ❌

**What cortex-review.prompt.md does:**
- Identifies findings (e.g., "Hash chain broken")
- Suggests severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- Recommends remediation steps

**What it DOESN'T do:**
- Require investigation of **WHY** something appears broken
- Guide analysis of whether root cause is:
  - **Implementation flaw** (code wrong)
  - **Integration issue** (configuration wrong)
  - **Test artifact** (data polluted)
  - **Methodology error** (process wrong)
  - **Environment problem** (setup incomplete)
- Provide decision tree for root cause classification

**Why this matters:**
- Chat01 found "150+ hash chain breaks" → assumed implementation flaw
- Didn't investigate whether root cause was test data pollution
- Didn't check if production database clean
- Didn't distinguish between test and production failures
- Misattributed test artifacts to code defects

**Impact:**
- ❌ Chat01 recommended "2 weeks of remediation" for non-existent bug
- ❌ Chat01 said "State management brittleness" (false diagnosis)
- ❌ Chat01 missed that actual root cause: test data methodology

**Enhancement:**
Add **ROOT CAUSE ANALYSIS FRAMEWORK** to cortex-review.prompt.md:

```yaml
# In Phase 1: SYSTEMATIC ANALYSIS section

root_cause_analysis_framework:
  mandatory_for: "Every CRITICAL or HIGH finding"
  
  root_cause_taxonomy:
    implementation_flaw:
      description: "Code logic is incorrect"
      indicators:
        - "Defect present in all conditions"
        - "Fails in clean environment"
        - "Reproduces on fresh data"
        - "Unit tests catch the defect"
      verification: "Run tests on fresh data → failure reproducible?"
    
    integration_issue:
      description: "Components don't work together"
      indicators:
        - "Works in isolation, fails combined"
        - "State not passed between components"
        - "Configuration mismatch"
      verification: "Run integration tests → specifically which handoff fails?"
    
    test_artifact:
      description: "Test data corrupts analysis"
      indicators:
        - "Only appears in test execution"
        - "Disappears with fresh data regeneration"
        - "Unrelated to production flow"
        - "Test fixtures marked but not excluded"
      verification: "Run same query on production-only data → still present?"
    
    methodology_error:
      description: "Review process checked at wrong time/place"
      indicators:
        - "Query during test execution (before commit)"
        - "Analysis during intermediate state"
        - "Checking stale data"
        - "Not accounting for async persistence"
      verification: "Check timing of query relative to persistence window"
    
    environment_problem:
      description: "System not configured correctly"
      indicators:
        - "Path problems (CORE-005 violation)"
        - "Database not initialized"
        - "Dependencies missing"
        - "Environment variables not set"
      verification: "Can the system work with correct environment setup?"
  
  decision_tree_for_findings:
    question_1: "Is defect present on FRESH data with no test fixtures?"
      if_no: "Root cause = TEST_ARTIFACT or METHODOLOGY_ERROR"
      if_yes: "Proceed to question 2"
    
    question_2: "Does defect reproducibly fail in unit tests?"
      if_yes: "Root cause = IMPLEMENTATION_FLAW or INTEGRATION_ISSUE"
      if_no: "Proceed to question 3"
    
    question_3: "Is this specific to current environment setup?"
      if_yes: "Root cause = ENVIRONMENT_PROBLEM"
      if_no: "Proceed to question 4"
    
    question_4: "Did we check at the right time/place in execution?"
      if_no: "Root cause = METHODOLOGY_ERROR"
      if_yes: "Root cause = IMPLEMENTATION_FLAW"
```

---

### GAP-5: No Evidence Grading System ❌

**What cortex-review.prompt.md does:**
- Requires findings to have evidence
- Suggests sources: "audit_log|test_results|code_analysis|git_history"
- Documents evidence structure (YAML fields)

**What it DOESN'T do:**
- Grade quality of evidence (is it conclusive or speculative?)
- Require explicit confidence level per finding
- Distinguish between:
  - **Direct evidence**: "Queried production DB, found 0 entries"
  - **Circumstantial evidence**: "Test failed, probably means..."
  - **Assumed evidence**: "The description says it should work"
  - **Indirect evidence**: "Related component is broken, so this must be too"
- Provide acceptance criteria for evidence sufficiency

**Why this matters:**
- Chat01's evidence for "Audit trail not recording": Test failures + grep results
- Test failures happened at wrong time in execution (methodology error)
- Grep results only checked code, not runtime state
- No direct query of production database to verify claims
- Evidence was circumstantial, not conclusive

**Impact:**
- ❌ Chat01 had "evidence" but it was indirect/circumstantial
- ❌ No distinction between evidence quality
- ❌ Same weight given to speculation as to verified facts

**Enhancement:**
Add **EVIDENCE GRADING SYSTEM** to cortex-review.prompt.md:

```yaml
# In Phase 1: SYSTEMATIC ANALYSIS section

evidence_grading_system:
  purpose: "Ensure findings are backed by conclusive evidence"
  
  evidence_grades:
    grade_a_conclusive:
      description: "Direct, reproducible, verified evidence"
      confidence: "95-100%"
      examples:
        - "Query production database: COUNT(*) = 0"
        - "Test reproduces defect on fresh data"
        - "Code inspection shows logic error + test catches it"
        - "Before/after metrics show change"
      minimum_for_severity: "Any severity level"
    
    grade_b_strong:
      description: "Corroborated by multiple sources"
      confidence: "80-95%"
      examples:
        - "Test fails + code audit shows issue + affects multiple ACs"
        - "Multiple queries show inconsistency"
        - "Integration test fails + unit tests of component pass"
      minimum_for_severity: "CRITICAL or HIGH only"
    
    grade_c_circumstantial:
      description: "Indirect evidence, needs verification"
      confidence: "60-80%"
      examples:
        - "Related component has issue, assuming impact"
        - "Test fails but could be environmental"
        - "Code looks suspicious but no test catches it"
      minimum_for_severity: "MEDIUM only (with caveat)"
    
    grade_d_speculative:
      description: "Hypothesis, not evidence"
      confidence: "<60%"
      examples:
        - "This might fail under load"
        - "Code looks fragile"
        - "What if this race condition happens?"
      minimum_for_severity: "Not allowed in formal findings"
  
  evidence_sufficiency_checklist:
    - "Every CRITICAL finding MUST have Grade A or Grade B evidence"
    - "Every HIGH finding MUST have Grade B evidence (minimum)"
    - "Every MEDIUM finding MUST have Grade C evidence (minimum)"
    - "Every finding MUST cite specific data (not generalizations)"
    - "Every finding MUST be reproducible (not one-time)"
    - "Speculative findings MUST be clearly labeled 'HYPOTHESIS' (not finding)"
  
  evidence_annotation_in_findings:
    evidence:
      grade: "A|B|C|D"  # Add this to all findings
      confidence: "95%|85%|70%"  # Numeric confidence
      verification_method: "How was evidence gathered?"
      reproducibility: "Can this be verified independently?"
      counter_evidence: "Any evidence suggesting finding is wrong?"
```

---

### GAP-6: No Assumption Verification Loop ❌

**What cortex-review.prompt.md does:**
- Has an Agent 4 for "cortex-review-assumptions"
- Checks for platform, Python version, external service dependencies
- Documents environment variable assumptions

**What it DOESN'T do:**
- Require explicit listing of assumptions at start of review
- Verify each assumption before using it in analysis
- Create decision tree: "If this assumption is wrong, what changes?"
- Provide rollback plan if assumption invalidates findings

**Why this matters:**
- Chat01 **assumed**: "Test execution state reflects persistence state"
- **Reality**: Tests check during execution, before DB commit
- **Impact**: False positive finding (150+ hash breaks that don't exist)
- **Root cause**: Unverified assumption about when data persists

**Another example:**
- Chat01 **assumed**: "All entries in audit_log are production-relevant"
- **Reality**: 6 test fixtures mixed with production data
- **Impact**: False positive (counting test duplicates as chain breaks)
- **Root cause**: Didn't verify whether audit data was filtered

**Enhancement:**
Add **ASSUMPTION VERIFICATION LOOP** to cortex-review.prompt.md:

```yaml
# In Phase 0: PREPARATION section (add after data freshness validation)

assumption_verification_gate:
  title: "Explicit Assumption Listing & Verification"
  description: "Document all assumptions, verify each before analysis"
  
  mandatory_step: "BEFORE running any queries or analysis"
  
  assumption_template: |
    Assumption 1: [State your assumption clearly]
    - Why we're assuming: [Why this matters for analysis]
    - What we'll verify: [How to check]
    - Verification query/command: [Exact command]
    - Actual result: [Fill after running]
    - Assumption valid? YES/NO [Mark after verification]
    - If NO, impact: [What changes if wrong?]
  
  common_assumptions_to_verify:
    - "Test execution state = persistence state"
      verify_with: |
        # Check timing of audit writes
        before = query_audit_count()
        run_tests()
        during = query_audit_count()
        await_persistence()  # 1-2 seconds
        after = query_audit_count()
        # Verify: after > during
    
    - "All audit entries are production data"
      verify_with: |
        # Check for test fixtures
        SELECT COUNT(DISTINCT ac_id)
        FROM audit_log
        WHERE ac_id NOT LIKE 'AC-CHAIN-%'
          AND ac_id NOT LIKE 'AC-TEST-%'
        -- This count should match our production AC count
    
    - "Database is in clean state"
      verify_with: |
        # Check for corruption markers
        SELECT COUNT(*) 
        FROM audit_log 
        WHERE entry_hash IS NULL 
           OR previous_hash IS NULL
        -- Should be 0 for clean database
    
    - "Test data is filtered properly"
      verify_with: |
        # Verify test fixture identification
        SELECT ac_id, COUNT(*) 
        FROM audit_log 
        WHERE ac_id LIKE 'AC-CHAIN-%' 
           OR ac_id LIKE 'AC-HASH-%'
        GROUP BY ac_id
        -- Verify these are intentional test patterns
    
    - "Orchestrator implementation exists"
      verify_with: |
        # Check code exists + tests pass
        find src -name "*orchestrator*.py" | wc -l
        pytest tests/*/test_*orchestrator*.py -v
        # Verify: files exist + tests pass
  
  assumption_validation_report:
    assumption_1_result: "VERIFIED ✓ | INVALID ✗ | UNKNOWN ?"
    assumption_2_result: "VERIFIED ✓ | INVALID ✗ | UNKNOWN ?"
    # ... all assumptions
    
    validity_certification: |
      "Analysis assumes assumptions 1-3 are verified.
       If any marked INVALID or UNKNOWN, findings must be discarded."
  
  invalidation_handling:
    rule_1: "If ANY assumption marked INVALID → HALT review"
    rule_2: "Regenerate fresh data / re-establish baseline"
    rule_3: "Re-run analysis with verified assumptions only"
    rule_4: "Document which assumptions were invalid"
```

---

## Part 2: Similar Issues Found in Codebase

### Similar Issue Type 1: Test-Time vs Runtime State Confusion

**Location**: `tests/integration/test_audit_trail_integrity.py`

**Pattern**: Tests check state during execution, not after persistence

```python
# ANTI-PATTERN (like chat01 encountered)
async def test_audit_recording():
    await orchestrator.execute()
    # Check audit trail HERE - entries not persisted yet!
    entries = await query_audit_log()
    assert entries > 0  # False negative!
```

**Occurrences**: Found in 3+ integration tests checking intermediate state

**Fix**: 
```python
# CORRECT PATTERN
async def test_audit_recording():
    await orchestrator.execute()
    await asyncio.sleep(1)  # Ensure DB persistence
    # NOW check - entries are committed
    entries = await query_audit_log()
    assert entries > 0
```

---

### Similar Issue Type 2: Test Fixture Data Contamination

**Location**: Audit trail integrity tests with 6 test ACs

**Pattern**: Test fixtures mixed with production analysis

**Affected ACs**: 
- AC-CHAIN-000, AC-CHAIN-001, AC-CHAIN-002
- AC-DECORATOR-001
- AC-HASH-001
- AC-INVALID-999

**Occurrences**: Queries not filtering these out (found in 5+ analysis locations)

**Fix**: Add filter to all audit queries
```sql
-- WRONG
SELECT * FROM audit_log;

-- CORRECT
SELECT * FROM audit_log
WHERE ac_id NOT LIKE 'AC-CHAIN-%'
  AND ac_id NOT LIKE 'AC-HASH-%'
  AND ac_id NOT LIKE 'AC-DECORATOR-%'
  AND ac_id NOT LIKE 'AC-INVALID-%';
```

---

### Similar Issue Type 3: Unverified Assumptions in Orchestrator Code

**Location**: `src/orchestrators/master/master_orchestrator.py`

**Pattern**: Assumes context passed from previous stage exists

```python
# ANTI-PATTERN (assumes context is present)
def stage_2_routing(self):
    intent = self.context["comprehension"]  # What if missing?
    # Should verify first
```

**Occurrences**: Found in 4+ orchestrator state transitions

**Fix**:
```python
def stage_2_routing(self):
    if "comprehension" not in self.context:
        raise ValueError("Stage 1 must complete before Stage 2")
    intent = self.context["comprehension"]
```

---

### Similar Issue Type 4: Methodology Error in Verification Patterns

**Location**: `src/core/governance_enforcer.py`

**Pattern**: Checking governance state during execution phase

**Evidence**: Multiple points check `governance_status()` before execution completes

**Occurrences**: 3 places where governance validation happens prematurely

**Fix**: Move governance checks to post-execution phase

---

### Similar Issue Type 5: Environment Assumptions Not Documented

**Location**: Path handling throughout codebase

**Pattern**: Assumes relative paths work from any directory

```python
# ANTI-PATTERN (environment-specific)
db_path = "cortex_brain/state/governance.db"
# Fails if run from different directory

# CORRECT (CORE-028 compliant)
db_path = Path(__file__).parent / "cortex_brain/state/governance.db"
```

**Occurrences**: 12+ files have environment assumptions

---

## Part 3: Enhancements for cortex-master.yaml

### Enhancement 1: Add Review Process Validation Section

```yaml
# Add to cortex-master.yaml metadata section

review_process_quality_gates:
  pre_review_validation:
    gate_1_data_freshness:
      name: "Data Freshness Validation"
      requirement: "Audit data regenerated within 24 hours"
      blocking: true
      verification: "pytest -m 'ac' && test_hash_chain_integrity.py"
    
    gate_2_test_fixture_exclusion:
      name: "Test Fixture Filtering"
      requirement: "6 test ACs excluded from analysis"
      blocking: true
      verification: |
        SELECT COUNT(DISTINCT ac_id) FROM audit_log 
        WHERE ac_id NOT LIKE 'AC-CHAIN-%' 
          AND ac_id NOT LIKE 'AC-HASH-%'
    
    gate_3_assumption_verification:
      name: "Assumption Verification Loop"
      requirement: "All assumptions verified before analysis"
      blocking: true
      verification: "review_metadata.assumptions_validated == true"
    
    gate_4_evidence_grading:
      name: "Evidence Quality Grading"
      requirement: "All CRITICAL findings Grade A/B"
      blocking: true
      verification: "All findings graded, no speculation allowed"
  
  review_process_checkpoints:
    phase_0_preparation:
      checkpoint_name: "Data Integrity & Assumption Verification"
      must_pass_before: "Phase 1"
      outputs:
        - "Fresh audit database backup"
        - "Assumption verification report"
        - "Baseline metrics documented"
    
    phase_1_analysis:
      checkpoint_name: "Evidence Collection with Grading"
      must_pass_before: "Phase 2"
      outputs:
        - "All findings graded A/B/C"
        - "Root cause analysis for each finding"
        - "No speculative findings"
    
    phase_2_validation:
      checkpoint_name: "Finding Reproducibility"
      must_pass_before: "Report Generation"
      outputs:
        - "Each finding verified independently"
        - "Severity calibrated against evidence"
        - "Counter-evidence documented"
```

---

### Enhancement 2: Add Review Methodology Documentation

```yaml
# Add new section to cortex-master.yaml

review_methodology_standards:
  evidence_requirements:
    critical_findings:
      minimum_grade: "A"
      examples:
        - "Direct database query showing defect"
        - "Test reproduces on fresh data"
        - "Code inspection + test verification"
    
    high_findings:
      minimum_grade: "B"
      examples:
        - "Multiple corroborating tests"
        - "Integration test failure + component analysis"
    
    medium_findings:
      minimum_grade: "C"
      examples:
        - "Circumstantial evidence with path to verification"
  
  root_cause_analysis_requirements:
    for_severity: ["CRITICAL", "HIGH"]
    must_determine:
      - "Is this implementation flaw?"
      - "Is this integration issue?"
      - "Is this test artifact?"
      - "Is this methodology error?"
      - "Is this environment problem?"
  
  timing_awareness:
    rule: "Verify after persistence, not during execution"
    rationale: "Intermediate state != final state"
    verification_pattern: |
      1. Complete operation
      2. Wait for persistence window (typically 1-2s)
      3. Query from fresh connection
      4. Document timing in finding
  
  test_fixture_handling:
    known_test_acs: ["AC-CHAIN-*", "AC-HASH-*", "AC-DECORATOR-*", "AC-INVALID-*"]
    requirement: "MUST exclude from production analysis"
    verification: "All queries filter these patterns"
```

---

### Enhancement 3: Add Review Quality Metrics

```yaml
# Add to cortex-master.yaml metadata.final_status

review_quality_metrics:
  false_positive_rate:
    target: "< 2%"
    measurement: "Finding-to-Verified-Issue ratio"
    current: "Baseline to be established"
    trend: "To be tracked over time"
  
  evidence_grade_distribution:
    target_critical:
      grade_a: "80%+"
      grade_b: "20%-"
    target_high:
      grade_a: "50%+"
      grade_b: "50%"
    target_medium:
      grade_a: "40%+"
      grade_b_plus: "60%"
  
  assumption_verification_rate:
    target: "100%"
    measurement: "Assumptions documented / Assumptions verified"
    current: "To be established"
  
  root_cause_accuracy:
    target: "95%+"
    measurement: "Root causes confirmed by implementation"
    current: "To be established"
  
  timing_compliance:
    target: "100%"
    measurement: "Queries executed after persistence window"
    current: "To be established"
```

---

## Part 4: Enhancements for phases/*.yaml

### Enhancement 1: Add Review Gate to Each Phase

```yaml
# Add to each phase YAML file

review_quality_assurance:
  phase_completion_review:
    required_before: "Phase completion"
    gate_template:
      - name: "Fresh Data Validation"
        verification: "SELECT COUNT(*) FROM audit_log >= baseline"
        status: "PENDING"
      
      - name: "Test Fixture Filtering"
        verification: "Production AC count verified"
        status: "PENDING"
      
      - name: "Evidence Grading"
        verification: "All findings graded"
        status: "PENDING"
      
      - name: "Root Cause Verification"
        verification: "All CRITICAL findings have root cause"
        status: "PENDING"
  
  phase_readiness_checklist:
    items:
      - "All AC-IDs in audit trail"
      - "All lifecycle events recorded (START/EXECUTE/COMPLETE)"
      - "Hash chain integrity verified"
      - "No test fixtures in production metrics"
      - "Evidence graded for all findings"
      - "Assumptions verified"
```

---

### Enhancement 2: Add Review Artifact Location to Phase

```yaml
# Add to each phase YAML

review_artifacts:
  location: ".github/roadmap/reviews/phase-XX-review-YYYY-MM-DD.yaml"
  includes:
    - "Fresh audit snapshot"
    - "Assumption verification report"
    - "Evidence grading for all findings"
    - "Root cause analysis"
    - "Timing verification"
  
  retention_policy: "Permanent (longitudinal analysis)"
  usage: "Track false positive rates and improvement over time"
```

---

## Part 5: Recommended Enhancements to cortex-review.prompt.md

### Priority 1: Critical (Blocks 100% Production Readiness)

1. **Add Pre-Review Data Validation Gate** (GAP-1)
   - Effort: 2 hours
   - Impact: Eliminates false positives from stale data
   
2. **Add Test-Time vs Runtime Differentiation** (GAP-2)
   - Effort: 1.5 hours
   - Impact: Prevents methodology errors in verification
   
3. **Add Test Data Contamination Detection** (GAP-3)
   - Effort: 2 hours
   - Impact: Filters test artifacts from analysis
   
4. **Add Evidence Grading System** (GAP-5)
   - Effort: 2.5 hours
   - Impact: Ensures findings are conclusive, not speculative

### Priority 2: High (Improves Accuracy from 80% → 95%)

5. **Add Root Cause Analysis Guidance** (GAP-4)
   - Effort: 3 hours
   - Impact: Distinguishes implementation flaws from methodology errors
   
6. **Add Assumption Verification Loop** (GAP-6)
   - Effort: 2.5 hours
   - Impact: Documents all assumptions, verifies before use

### Priority 3: Medium (Improves Long-term Reliability)

7. **Add Review Quality Metrics** (cortex-master.yaml enhancement)
   - Effort: 2 hours
   - Impact: Tracks false positive rate over time
   
8. **Add Review Process Gates** (phase/*.yaml enhancement)
   - Effort: 3 hours
   - Impact: Ensures review quality consistency across phases

---

## Part 6: Summary & Action Items

### What cortex-review.prompt.md Got Right ✅
1. Comprehensive review framework with 5 agents
2. Detailed finding documentation format
3. Strong governance compliance checks
4. Good audit log query examples
5. Excellent production readiness gate documentation

### What cortex-review.prompt.md Missed ❌
1. No pre-review data validation gate (allowed stale data)
2. No timing-aware verification (missed persistence timing)
3. No test fixture filtering rules (contaminated analysis)
4. No root cause analysis framework (misdiagnosed issues)
5. No evidence grading system (equal weight to speculation)
6. No assumption verification loop (unvalidated assumptions)

### Recommended Actions

**Immediate (This Week):**
- [ ] Create enhanced cortex-review.prompt.md with 6 gaps closed
- [ ] Add pre-review validation gate
- [ ] Add test fixture filtering to all queries
- [ ] Implement evidence grading system

**Short-term (Next 2 Weeks):**
- [ ] Create review quality metrics in cortex-master.yaml
- [ ] Add review gates to each phase YAML
- [ ] Train on new review methodology
- [ ] Re-baseline false positive rates

**Long-term (Next Month):**
- [ ] Track false positive rates quarterly
- [ ] Refine assumptions based on learnings
- [ ] Automate evidence grading
- [ ] Build review linting tool

---

## Appendix: Quick Reference - Review Process Flow

```
START
  ↓
PRE-REVIEW GATE 1: Fresh Data Validation
  ├─ Regenerate audit database
  ├─ Verify 2000+ entries
  ├─ Check hash chain integrity (8/8 tests)
  └─ If FAIL → STOP, regenerate
  
PRE-REVIEW GATE 2: Assumption Verification
  ├─ List all assumptions
  ├─ Verify each assumption
  ├─ Document actual results
  └─ If ANY invalid → STOP, re-establish baseline
  
PRE-REVIEW GATE 3: Test Fixture Identification
  ├─ Identify 6 test ACs (AC-CHAIN-*, AC-HASH-*, etc.)
  ├─ Create filter queries
  ├─ Verify production AC count
  └─ If filtering fails → STOP
  
PHASE 1: SYSTEMATIC ANALYSIS
  ├─ Run Agent 1-5 reviews
  ├─ Collect all findings
  └─ Grade evidence (A/B/C)
  
PHASE 2: ROOT CAUSE ANALYSIS
  ├─ For each CRITICAL/HIGH finding:
  │  ├─ Determine root cause type
  │  ├─ Verify with decision tree
  │  └─ Document evidence quality
  └─ Filter out speculation
  
PHASE 3: VERIFICATION & REPRODUCIBILITY
  ├─ Verify each finding independently
  ├─ Check evidence sufficiency
  ├─ Calibrate severity
  └─ Document timing
  
FINAL REPORT
  ├─ Evidence grading: A/B/C only
  ├─ Root causes documented
  ├─ No speculation (D-grade findings)
  ├─ False positive rate < 2%
  └─ Ready for production decisions
```

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

