# CORTEX Review Process Quality Gates - YAML Integration Guide
# For inclusion in cortex-master.yaml and phases/*.yaml

# This file provides the YAML structures to incorporate the review enhancements
# into the master configuration and individual phase YAMLs.

---

## PART 1: ADD TO cortex-master.yaml METADATA SECTION

```yaml
# In cortex-master.yaml, add to metadata:

review_process_quality_gates:
  version: "2.0"
  date_created: "2026-01-17"
  reason: "Enhanced from v1.0 after chat01.md review analysis"
  
  # Pre-review validation gates (MANDATORY - must all pass)
  pre_review_validation_gates:
    gate_0a_data_freshness:
      name: "Data Freshness Validation"
      description: "Ensures audit data is regenerated within 24 hours"
      requirement_level: "CRITICAL - BLOCKS REVIEW IF FAILED"
      acceptance_criteria:
        - "Fresh database backup created"
        - "Total audit entries >= 2000"
        - "Data age < 24 hours"
        - "Hash chain integrity: 8/8 tests PASSING"
        - "All operation types present (START/EXECUTE/COMPLETE)"
      implementation_script: |
        # See cortex-review-enhanced.prompt.md Stage 0 Gate 0A
      verification_query: |
        SELECT 
          COUNT(*) as total_entries,
          COUNT(DISTINCT ac_id) as unique_acs,
          ROUND((julianday('now') - julianday(MAX(timestamp))) * 24, 1) as age_hours
        FROM audit_log
        WHERE timestamp NOT NULL;
        -- Expected: entries >= 2000, age_hours < 24
    
    gate_0b_test_fixture_filtering:
      name: "Test Fixture Identification & Filtering"
      description: "Filters 6 known test ACs before analysis"
      requirement_level: "CRITICAL - BLOCKS REVIEW IF FAILED"
      known_test_fixtures:
        - "AC-CHAIN-*"
        - "AC-HASH-*"
        - "AC-DECORATOR-*"
        - "AC-INVALID-*"
        - "AC-TEST-*"
        - "AC-MOCK-*"
      acceptance_criteria:
        - "6 test fixtures identified by ac_id pattern"
        - "Test fixture count documented (baseline)"
        - "Production AC count >= 240 (after filtering)"
        - "All future queries use filtering rules"
        - "Test fixtures NOT counted in production metrics"
      implementation_query: |
        -- Identify test fixtures
        SELECT DISTINCT ac_id, COUNT(*) as entries
        FROM audit_log
        WHERE ac_id LIKE 'AC-CHAIN-%' 
           OR ac_id LIKE 'AC-HASH-%'
           OR ac_id LIKE 'AC-DECORATOR-%'
           OR ac_id LIKE 'AC-INVALID-%'
           OR ac_id LIKE 'AC-TEST-%'
           OR ac_id LIKE 'AC-MOCK-%'
        GROUP BY ac_id;
        
        -- Get production AC count
        SELECT 
          (SELECT COUNT(DISTINCT ac_id) FROM audit_log 
           WHERE ac_id LIKE 'AC-CHAIN-%' OR ac_id LIKE 'AC-HASH-%'
              OR ac_id LIKE 'AC-DECORATOR-%' OR ac_id LIKE 'AC-INVALID-%'
              OR ac_id LIKE 'AC-TEST-%' OR ac_id LIKE 'AC-MOCK-%') as test_fixtures,
          COUNT(DISTINCT ac_id) as total_acs
        FROM audit_log;
      filter_clause_for_all_queries: |
        WHERE ac_id NOT LIKE 'AC-CHAIN-%'
          AND ac_id NOT LIKE 'AC-HASH-%'
          AND ac_id NOT LIKE 'AC-DECORATOR-%'
          AND ac_id NOT LIKE 'AC-INVALID-%'
          AND ac_id NOT LIKE 'AC-TEST-%'
          AND ac_id NOT LIKE 'AC-MOCK-%'
    
    gate_0c_assumption_verification:
      name: "Assumption Verification Loop"
      description: "Lists and verifies all assumptions before analysis"
      requirement_level: "CRITICAL - BLOCKS REVIEW IF ASSUMPTIONS INVALID"
      required_assumptions:
        - "Audit database reflects production state (within 24h)"
        - "Test execution state = persistence state (after 1-2s wait)"
        - "All audit entries (filtered) are production data"
        - "Hash chain integrity test is comprehensive"
        - "Orchestrator implementations exist (not stubbed)"
        - "Environment is configured correctly (CORE-028 paths)"
      acceptance_criteria:
        - "All 6 assumptions listed explicitly"
        - "Each assumption verified with command/query"
        - "Actual results documented"
        - "All marked as 'YES' (valid) or caveated"
        - "NO assumptions marked 'INVALID' (blocking)"
        - "NO critical assumptions marked 'UNKNOWN'"
      implementation_template: |
        # See cortex-review-enhanced.prompt.md Stage 0 Gate 0C
        # Document each assumption with: statement, why_it_matters, verification_command, actual_result, valid_yes_no, if_invalid_impact
  
  # Evidence grading system (NEW - for all findings)
  evidence_grading_system:
    description: "Grades evidence quality; prevents speculation in formal findings"
    grades:
      grade_a_conclusive:
        description: "Direct, reproducible, verified evidence"
        confidence: "95-100%"
        examples:
          - "Query production database: COUNT(*) = X"
          - "Test reproduces on fresh data"
          - "Code inspection + test verification"
        allowed_severity:
          - "CRITICAL"
          - "HIGH"
          - "MEDIUM"
          - "LOW"
      
      grade_b_strong:
        description: "Corroborated by multiple sources"
        confidence: "80-95%"
        examples:
          - "Test fails + code audit shows issue + multiple ACs affected"
          - "Multiple independent queries show inconsistency"
          - "Integration test fails + unit tests pass"
        allowed_severity:
          - "CRITICAL (if reproducible)"
          - "HIGH"
          - "MEDIUM"
          - "LOW"
      
      grade_c_circumstantial:
        description: "Indirect evidence"
        confidence: "60-80%"
        examples:
          - "Related component has issue"
          - "Test fails but could be environmental"
          - "Code looks suspicious but untested"
        allowed_severity:
          - "MEDIUM (with caveat)"
          - "LOW"
      
      grade_d_speculative:
        description: "Hypothesis, not evidence"
        confidence: "<60%"
        allowed_severity: []  # NONE - must be labeled HYPOTHESIS
    
    sufficiency_rules:
      critical_findings: "Grade A or B required"
      high_findings: "Grade B required (minimum)"
      medium_findings: "Grade C required (minimum)"
      low_findings: "Grade C or better"
  
  # Root cause analysis framework (NEW - for CRITICAL/HIGH)
  root_cause_analysis_framework:
    requirement: "Every CRITICAL/HIGH finding must have root cause type determined"
    root_cause_types:
      implementation_flaw:
        description: "Code logic is incorrect"
        decision_tree_indicators: ["Fails on fresh data", "Unit tests catch it", "All conditions affected"]
      
      integration_issue:
        description: "Components don't work together"
        decision_tree_indicators: ["Works in isolation", "Fails combined", "State not passed"]
      
      test_artifact:
        description: "Test data corrupts analysis"
        decision_tree_indicators: ["Only in test execution", "Test fixtures present", "Production-only data clean"]
      
      methodology_error:
        description: "Review process checked at wrong time"
        decision_tree_indicators: ["Query during test", "Before persistence", "Intermediate state"]
      
      environment_problem:
        description: "System not configured correctly"
        decision_tree_indicators: ["Path problems", "DB not accessible", "Only in this environment"]
    
    decision_tree_questions:
      q1: "Is defect present on FRESH data, clean environment?"
      q2: "Does unit test for component reproducibly fail?"
      q3: "Is this specific to current environment setup?"
      q4: "Does component work in isolation but fail combined?"
      q5: "Are test fixtures (AC-CHAIN-, AC-HASH-, etc) present?"
      q6: "Was query executed during test (before DB commit)?"
  
  # Timing-aware verification (NEW - for all data queries)
  timing_aware_verification:
    requirement: "Verify AFTER persistence window, not during execution"
    critical_rule: "Wait 1-2 seconds after operation before querying"
    anti_patterns:
      - "Querying audit_log DURING pytest execution"
      - "Testing intermediate state as final state"
      - "Using stale database connections"
      - "Checking before async operations complete"
    correct_pattern: |
      1. Complete operation
      2. Wait for persistence (1-2 seconds)
      3. Create fresh database connection
      4. Query from fresh connection
      5. Document timing in finding
  
  # Review quality metrics (NEW - for tracking)
  review_quality_metrics:
    false_positive_rate:
      target: "< 2%"
      measurement: "Unverified findings / Total findings"
      baseline: "To be established"
      tracked: true
    
    evidence_grade_distribution:
      target_critical: "Grade A/B: 100%"
      target_high: "Grade B: 90%+"
      target_medium: "Grade C+: 95%+"
      tracked: true
    
    assumption_verification_rate:
      target: "100%"
      measurement: "Verified assumptions / Total assumptions"
      tracked: true
    
    root_cause_accuracy:
      target: "95%+"
      measurement: "Root causes confirmed by implementation"
      tracked: true
  
  # Mandatory review checklist (NEW)
  final_review_checklist:
    pre_review_gates:
      - "Gate 0A (Data Freshness): PASSED"
      - "Gate 0B (Test Fixture Filtering): PASSED"
      - "Gate 0C (Assumption Verification): PASSED"
    
    critical_findings_checks:
      - "Grade A or B evidence: YES"
      - "Root cause determined: YES"
      - "Timing documented: YES"
      - "Test fixtures excluded: YES"
    
    high_findings_checks:
      - "Grade B evidence: YES"
      - "Root cause analysis: YES"
      - "Timing verified: YES"
    
    all_findings_checks:
      - "No D-grade speculation: YES"
      - "Reproducible findings only: YES"
      - "AC-ID or file reference: YES"
    
    overall_report_checks:
      - "False positive rate < 2%: YES"
      - "No unverified assumptions: YES"
      - "Test artifacts filtered: YES"
      - "Severity calibrated: YES"
```

---

## PART 2: ADD TO EACH phase/*.yaml FILE

```yaml
# In each phase YAML file (e.g., phase-01.yaml, phase-02.yaml, etc.):

# Add to the phase metadata section:

review_process_integration:
  # Review gates specific to this phase
  phase_completion_review_gates:
    requirement: "Must pass before phase marked complete"
    
    gate_1_fresh_data_validation:
      name: "Phase-Specific Data Validation"
      requirement: "Audit entries for this phase verified on fresh data"
      verification_query: |
        SELECT COUNT(DISTINCT ac_id) 
        FROM audit_log 
        WHERE ac_id LIKE 'PHASE-XX-%'  -- Replace XX with phase number
          AND ac_id NOT LIKE 'AC-CHAIN-%'
          AND ac_id NOT LIKE 'AC-TEST-%'
        -- Should match AC-IDs defined in phase
      status: "PENDING"  # Updated by review process
    
    gate_2_AC_lifecycle_verification:
      name: "AC Lifecycle Completion"
      requirement: "All AC-IDs have AC_START/EXECUTE/COMPLETE"
      verification_query: |
        SELECT ac_id, 
               SUM(CASE WHEN operation = 'AC_START' THEN 1 ELSE 0 END) as starts,
               SUM(CASE WHEN operation = 'AC_EXECUTE' THEN 1 ELSE 0 END) as executes,
               SUM(CASE WHEN operation = 'AC_COMPLETE' THEN 1 ELSE 0 END) as completes
        FROM audit_log 
        WHERE ac_id LIKE 'PHASE-XX-%'
        GROUP BY ac_id
        HAVING starts >= 1 AND executes >= 1 AND completes >= 1
        -- All ACs should appear in results
      status: "PENDING"
    
    gate_3_hash_chain_integrity:
      name: "Hash Chain Integrity for Phase ACs"
      requirement: "No hash breaks for this phase's ACs"
      verification_query: |
        SELECT COUNT(*) as hash_breaks
        FROM audit_log a1
        WHERE a1.ac_id LIKE 'PHASE-XX-%'
          AND a1.previous_hash != (SELECT entry_hash FROM audit_log WHERE id = a1.id - 1)
          AND a1.id > 1
        -- Should return 0
      status: "PENDING"
    
    gate_4_evidence_grading:
      name: "Findings Evidence Quality"
      requirement: "All findings graded A/B/C; no speculation"
      acceptance_criteria:
        - "CRITICAL findings: Grade A or B"
        - "HIGH findings: Grade B minimum"
        - "No D-grade findings in report"
      status: "PENDING"
  
  # Review artifacts for this phase
  review_artifacts:
    location: ".github/roadmap/reviews/phase-XX-review-YYYY-MM-DD.yaml"
    contents:
      - "Fresh audit snapshot (YAML or JSON)"
      - "Assumption verification report"
      - "Evidence grading for all findings"
      - "Root cause analysis"
      - "Timing documentation"
    retention: "Permanent (for longitudinal analysis)"
    usage: "Track false positive rates and improvement over time"
  
  # Quality metrics for this phase
  phase_review_metrics:
    false_positive_count: 0  # Target: 0 per phase
    evidence_grade_a_percentage: 0  # Target: 80%+ for CRITICAL
    evidence_grade_b_percentage: 0  # Target: 20%- for CRITICAL
    root_cause_accuracy_percent: 0  # Target: 95%+
    assumption_verification_rate: 0  # Target: 100%
```

---

## PART 3: IMPLEMENTATION GUIDE FOR cortex-master.yaml

### Step 1: Locate the metadata section

```yaml
# Find this section in cortex-master.yaml:
metadata:
  title: "CORTEX Implementation Roadmap"
  # ... other fields ...
```

### Step 2: Add review quality gates section after metadata

```yaml
metadata:
  # ... existing metadata ...

# NEW SECTION - Add right after metadata:
review_process_quality_gates:
  # Use PART 1 content above
```

### Step 3: Update phase_tracker to reference review gates

```yaml
phase_tracker:
  PHASE-01:
    # ... existing phase info ...
    
    # ADD these new fields:
    review_gates_required: true
    review_gates_status: "PENDING"  # Updated by review process
    review_artifacts_location: ".github/roadmap/reviews/phase-01-review-YYYY-MM-DD.yaml"
```

---

## PART 4: IMPLEMENTATION GUIDE FOR phase/*.yaml FILES

### For each phase file (phase-01.yaml, phase-02.yaml, etc.):

```yaml
# At end of file, add:

review_integration:
  phase_review_gates:
    # Use PART 2 content above, updating phase numbers
    requirement: "All gates must pass before phase completion"
    status: "PENDING"
  
  next_review_date: "2026-02-17"  # One month from today
  reviewer_notes: ""  # Filled by review process
```

---

## PART 5: PHASE YAML MODIFICATION CHECKLIST

For **each** phase/*.yaml file:

- [ ] Add `review_integration` section at end
- [ ] Replace `PHASE-XX` with actual phase number
- [ ] Verify `phase_completion_review_gates` queries are correct
- [ ] Update `location` in `review_artifacts` with correct phase number
- [ ] Commit changes: `git add phase-XX.yaml`

---

## PART 6: cortex-master.yaml MODIFICATION CHECKLIST

- [ ] Add `review_process_quality_gates` section after metadata
- [ ] Update `phase_tracker` to add review gate fields to all phases
- [ ] Add `review_quality_metrics` to metadata.final_status
- [ ] Add `final_review_checklist` section
- [ ] Verify all YAML syntax (use `yamllint` to check)
- [ ] Commit changes: `git add cortex-master.yaml`

---

## PART 7: VALIDATION & TESTING

### Before committing, validate:

```bash
# 1. Validate YAML syntax
yamllint .github/roadmap/cortex-master.yaml
yamllint .github/roadmap/phases/phase-*.yaml

# 2. Verify queries are correct SQL
sqlite3 cortex-brain/state/governance.db < <(
  echo "SELECT COUNT(DISTINCT ac_id) FROM audit_log WHERE ac_id NOT LIKE 'AC-CHAIN-%';"
)

# 3. Test fresh data process
cp cortex-brain/state/governance.db cortex-brain/state/governance.db.backup
sqlite3 cortex-brain/state/governance.db "DELETE FROM audit_log; VACUUM;"
pytest tests/ -m "ac" --ignore=tests/integration/test_audit_trail_integrity.py --tb=no -q
pytest tests/integration/test_audit_trail_integrity.py -v

# 4. Verify cortex-review-enhanced.prompt.md is accessible
ls -la .github/prompts/cortex-review-enhanced.prompt.md
```

---

## PART 8: QUICK REFERENCE - FILE CHANGES SUMMARY

| File | Change | Impact |
|------|--------|--------|
| `cortex-master.yaml` | Add `review_process_quality_gates` section | Defines review standards for all phases |
| `phase-XX.yaml` (all) | Add `review_integration` section | Each phase has specific review gates |
| `.github/prompts/cortex-review-enhanced.prompt.md` | NEW file | Enhanced review process (closes 6 gaps) |
| `.github/roadmap/reports/CORTEX-REVIEW-ENHANCEMENT-GAPS.md` | NEW file | Gap analysis and rationale |

---

## PART 9: DEPLOYMENT STEPS

### Phase 1: Documentation Update (1 hour)
1. Create enhanced review prompt: `cortex-review-enhanced.prompt.md` ✅
2. Create gap analysis: `CORTEX-REVIEW-ENHANCEMENT-GAPS.md` ✅
3. Create this integration guide

### Phase 2: YAML Integration (2 hours)
1. Update `cortex-master.yaml` with review quality gates
2. Add `review_integration` to all phase/*.yaml files
3. Validate YAML syntax with yamllint

### Phase 3: Process Validation (1 hour)
1. Run enhanced review on current codebase
2. Verify all gates pass
3. Document baseline metrics

### Phase 4: Team Training (2 hours)
1. Brief team on new review process
2. Share enhanced review prompt
3. Explain evidence grading and root cause analysis

### Total Effort: **6 hours**

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

