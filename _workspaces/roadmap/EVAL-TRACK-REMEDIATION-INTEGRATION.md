# Eval Track Remediation - Implementation Guide

**Date:** 2026-01-22  
**Reference:** EVAL-TRACK-REMEDIATION-PLAN-20260122.md  
**Action:** Integrate 8 new audit phases into cortex-impl-map.yaml

---

## Overview

**9 Review Findings to Remediate:** F004-F012  
**Audit Phases to Create:** 8  
**Current State:** PHASE-EVAL-001-TEST-REMEDIATION COMPLETED (F001-F003)  
**Next State:** Add PHASE-AUDIT-001-007 + CLEANUP-PHASE-001

---

## Phase Specifications (Ready to Add to cortex-impl-map.yaml)

### 1. PHASE-AUDIT-001-EXPORT-VERIFY

```yaml
- phase_id: "PHASE-AUDIT-001-EXPORT-VERIFY"
  track: "eval"
  machine: "eval"
  sequence: 1
  priority: "P0-CRITICAL"
  required: true
  blocking: true
  status: "NOT_STARTED"
  
  purpose: "Verify impl-export-completion phase actually fixed test collection errors"
  estimated_effort: "30 minutes"
  depends_on: []
  
  acceptance_criteria:
    - ac_id: "AC-AUDIT-001-01"
      description: "Test Collection Verification"
      requirement: "Execute `pytest tests/ --collect-only -q` and verify 0 collection errors"
      success_criteria: "0 ImportError or collection errors reported"
    
    - ac_id: "AC-AUDIT-001-02"
      description: "Document Collection Status"
      requirement: "Record actual error count and compare to expected"
      success_criteria: "Collection status documented in audit trail"
    
    - ac_id: "AC-AUDIT-001-03"
      description: "Decision Gate"
      requirement: "If errors=0: mark verified; If errors>0: create remediation task"
      success_criteria: "Clear decision documented with next steps"
  
  completion_verification:
    success_criteria:
      - "Test collection completes without ImportError"
      - "0 collection errors documented"
      - "Audit trail updated with verification timestamp"
    
    blocking_on_failure: true
    gate_decision: "Can PHASE-E-TDD-IMPLEMENTATION be trusted?"
```

---

### 2. PHASE-AUDIT-002-PHASE-E-VERIFY

```yaml
- phase_id: "PHASE-AUDIT-002-PHASE-E-VERIFY"
  track: "eval"
  machine: "eval"
  sequence: 1
  priority: "P0-CRITICAL"
  required: true
  blocking: true
  status: "NOT_STARTED"
  
  purpose: "Verify PHASE-E-TDD-IMPLEMENTATION has real implementations (not stubs)"
  estimated_effort: "2-3 hours"
  depends_on: ["PHASE-AUDIT-001-EXPORT-VERIFY"]
  
  rationale: |
    Phase E claims 125 modules completed in 1 day (24 hours).
    Estimated effort: 125 modules × 2-4 hours each = 250-500 hours.
    Timeline physically impossible without stubs (CORE-001 violation risk).
  
  acceptance_criteria:
    - ac_id: "AC-AUDIT-002-01"
      description: "Module Sampling"
      requirement: "Select 25 random modules (20% of 125) with diverse distribution"
      success_criteria: "Sample modules documented with distribution analysis"
    
    - ac_id: "AC-AUDIT-002-02"
      description: "Implementation Verification"
      requirement: "Verify each module has actual code (not stub/docstring only)"
      success_criteria: "≥90% of sampled modules have real implementations"
    
    - ac_id: "AC-AUDIT-002-03"
      description: "Test Execution"
      requirement: "Run tests for sampled modules; must be 100% passing"
      success_criteria: "All sampled module tests passing (0 failures)"
    
    - ac_id: "AC-AUDIT-002-04"
      description: "Coverage Analysis"
      requirement: "Run `pytest --cov=cortex` on samples; target >50% coverage"
      success_criteria: "Coverage >50% on sampled modules"
    
    - ac_id: "AC-AUDIT-002-05"
      description: "Decision Gate"
      requirement: "If ≥90% real: APPROVED; 70-89%: CONDITIONAL; <70%: BLOCKED"
      success_criteria: "Clear decision with rationale documented"
  
  completion_verification:
    success_criteria:
      - "≥90% of sampled modules have real implementations"
      - "≥98% test pass rate on samples"
      - "≥50% coverage on sampled modules"
      - "Decision gate documented with timeline impact"
    
    blocking_on_failure: true
    gate_decision: |
      Is PHASE-E actually production-ready?
      
      ≥90% real: APPROVED (+2 days to ready)
      70-89%: CONDITIONAL (+5-7 days)
      <70%: EMERGENCY REMEDIATION (+7-14 days)
```

---

### 3. PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT

```yaml
- phase_id: "PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT"
  track: "eval"
  machine: "eval"
  sequence: 2
  priority: "P1-HIGH"
  required: true
  blocking: false
  status: "NOT_STARTED"
  
  purpose: "Categorize 105 'concerning' imports and define remediation strategy"
  estimated_effort: "2-4 hours"
  depends_on: ["PHASE-AUDIT-001-EXPORT-VERIFY", "PHASE-AUDIT-002-PHASE-E-VERIFY"]
  
  context: "306 old import patterns detected; 140 acceptable, 105 concerning, 55 neutral"
  
  acceptance_criteria:
    - ac_id: "AC-AUDIT-003-01"
      description: "Categorize Concerning Imports"
      requirement: "Audit 105 files; determine if production code or non-production"
      success_criteria: "All 105 files categorized with rationale"
    
    - ac_id: "AC-AUDIT-003-02"
      description: "Priority List for Core Modules"
      requirement: "Identify which MUST be updated vs which are acceptable"
      success_criteria: "Remediation priority list ranked by impact"
    
    - ac_id: "AC-AUDIT-003-03"
      description: "Update Test Threshold"
      requirement: "Change test from '<20' to realistic number (150+) with filters"
      success_criteria: "Test threshold updated, old pattern documented"
    
    - ac_id: "AC-AUDIT-003-04"
      description: "Document Intentional Strategy"
      requirement: "Add entry explaining PARTIAL (not total) migration"
      success_criteria: "Import strategy documented in cortex-impl-map.yaml"
  
  completion_verification:
    success_criteria:
      - "105 files categorized with documented rationale"
      - "Remediation priority list created (CRITICAL/HIGH/MEDIUM/LOW)"
      - "Test threshold updated with explanation"
      - "Intentional mixed-pattern strategy documented"
    
    blocking_on_failure: false
    gate_decision: |
      Which imports need fixing immediately?
      
      0 critical imports: CLEAR (proceed)
      1-10 critical imports: MINOR (quick fix)
      >10 critical imports: MAJOR (longer remediation)
```

---

### 4. PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK

```yaml
- phase_id: "PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK"
  track: "eval"
  machine: "eval"
  sequence: 2
  priority: "P1-HIGH"
  required: true
  blocking: false
  status: "NOT_STARTED"
  
  purpose: "Verify CORE-001/008/011/012 compliance on Phase E modules"
  estimated_effort: "1-2 hours verification + varies for fixes"
  depends_on: ["PHASE-AUDIT-002-PHASE-E-VERIFY"]
  
  governance_rules_checked:
    - "CORE-001: Production quality implementations"
    - "CORE-008: Tests-first approach (TDD)"
    - "CORE-011: 100% type hints on public APIs"
    - "CORE-012: Google docstrings on public APIs"
  
  acceptance_criteria:
    - ac_id: "AC-AUDIT-004-01"
      description: "Sample Module Selection"
      requirement: "Select 25 modules verified in PHASE-AUDIT-002"
      success_criteria: "Sample distribution across all subsystems documented"
    
    - ac_id: "AC-AUDIT-004-02"
      description: "Type Hints Verification (CORE-011)"
      requirement: "Verify ≥95% of public functions have type hints"
      success_criteria: "Type hints compliance rate ≥95%"
    
    - ac_id: "AC-AUDIT-004-03"
      description: "Docstring Verification (CORE-012)"
      requirement: "Verify ≥95% of public functions have Google docstrings"
      success_criteria: "Docstring compliance rate ≥95%"
    
    - ac_id: "AC-AUDIT-004-04"
      description: "TDD Compliance (CORE-008)"
      requirement: "Verify ≥80% of samples follow test-first workflow"
      success_criteria: "TDD workflow compliance ≥80% (verified via git history)"
    
    - ac_id: "AC-AUDIT-004-05"
      description: "Production Quality (CORE-001)"
      requirement: "Check for code smells, hardcoded data, error handling"
      success_criteria: "No critical violations; warnings documented"
    
    - ac_id: "AC-AUDIT-004-06"
      description: "Decision Gate"
      requirement: "≥95%: APPROVED; 85-94%: CONDITIONAL; <85%: REMEDIATION"
      success_criteria: "Clear compliance decision with remediation plan (if needed)"
  
  completion_verification:
    success_criteria:
      - "Type hints compliance ≥95% documented"
      - "Docstring compliance ≥95% documented"
      - "TDD workflow ≥80% verified"
      - "CORE-001 violations (if any) with remediation plan"
      - "Specific file/function references for all findings"
    
    blocking_on_failure: false
    gate_decision: "Does code meet CORTEX governance standards?"
```

---

### 5. CLEANUP-PHASE-001-ROADMAP-MAINTENANCE

```yaml
- phase_id: "CLEANUP-PHASE-001-ROADMAP-MAINTENANCE"
  track: "eval"
  machine: "eval"
  sequence: 3
  priority: "P2-MEDIUM"
  required: false
  blocking: false
  status: "NOT_STARTED"
  
  purpose: "Remove duplicate and orphaned phase definitions from cortex-impl-map.yaml"
  estimated_effort: "2-3 hours"
  depends_on: ["PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK"]
  
  acceptance_criteria:
    - ac_id: "AC-CLEANUP-001-01"
      description: "Identify Duplicates"
      requirement: "Find all duplicate phase definitions (e.g., impl-governance-content 2x)"
      success_criteria: "All duplicates listed with line numbers"
    
    - ac_id: "AC-CLEANUP-001-02"
      description: "Remove Duplicate Entries"
      requirement: "Keep one canonical definition per phase; remove others cleanly"
      success_criteria: "Only one definition per phase remains; YAML valid"
    
    - ac_id: "AC-CLEANUP-001-03"
      description: "Archive Old Entries"
      requirement: "Move old COMPLETED entries to archive section"
      success_criteria: "Historical entries moved; no broken references"
    
    - ac_id: "AC-CLEANUP-001-04"
      description: "Consolidate Knowledge Domains"
      requirement: "Merge cortex_brain/knowledge/ and tier3/knowledge/ references"
      success_criteria: "Single canonical knowledge location referenced"
    
    - ac_id: "AC-CLEANUP-001-05"
      description: "Verify File Integrity"
      requirement: "Verify YAML is valid after all changes"
      success_criteria: "File loads without YAML errors; all references valid"
  
  completion_verification:
    success_criteria:
      - "All duplicates consolidated (1 definition per phase)"
      - "Orphaned entries archived"
      - "File remains valid YAML"
      - "All phase IDs unique"
      - "No broken references"
```

---

### 6. PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY

```yaml
- phase_id: "PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY"
  track: "eval"
  machine: "eval"
  sequence: 3
  priority: "P2-MEDIUM"
  required: false
  blocking: false
  status: "NOT_STARTED"
  
  purpose: "Verify git commits exist for phase completions per CORE-026"
  estimated_effort: "1 hour"
  depends_on: ["CLEANUP-PHASE-001-ROADMAP-MAINTENANCE"]
  
  core_rule: "CORE-026: Git checkpoints required before major milestones"
  
  acceptance_criteria:
    - ac_id: "AC-AUDIT-005-01"
      description: "Review Git History"
      requirement: "Check CORTEX branch for commits on 2026-01-21 and 2026-01-22"
      success_criteria: "All phase completion commits found or missing commits identified"
    
    - ac_id: "AC-AUDIT-005-02"
      description: "Verify Commit Messages"
      requirement: "Check format: `{machine}: {phase-id}: {summary}`"
      success_criteria: "All commits follow standard format"
    
    - ac_id: "AC-AUDIT-005-03"
      description: "Create Missing Checkpoints"
      requirement: "If commits missing, create checkpoint commits for completed phases"
      success_criteria: "All phase completions have git commits"
    
    - ac_id: "AC-AUDIT-005-04"
      description: "Document Convention"
      requirement: "Add commit format convention to cortex-impl-map.yaml"
      success_criteria: "Convention documented with examples"
  
  completion_verification:
    success_criteria:
      - "All phase completions have corresponding git commits"
      - "Commits follow standard message format"
      - "Convention documented for future phases"
      - "Commit hashes recorded in phase_execution_tracking"
```

---

### 7. PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK

```yaml
- phase_id: "PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK"
  track: "eval"
  machine: "eval"
  sequence: 4
  priority: "P2-MEDIUM"
  required: false
  blocking: false
  status: "NOT_STARTED"
  
  purpose: "Verify type hints and docstring compliance across codebase"
  estimated_effort: "1-2 hours"
  depends_on: ["PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK"]
  
  governance_rules_checked:
    - "CORE-011: Type hints on all public functions"
    - "CORE-012: Google docstrings on all public functions"
  
  acceptance_criteria:
    - ac_id: "AC-AUDIT-006-01"
      description: "Static Analysis"
      requirement: "Run pylint on 20% sample; document violations"
      success_criteria: "Compliance rate calculated and documented"
    
    - ac_id: "AC-AUDIT-006-02"
      description: "Sample Coverage"
      requirement: "Analyze sample for missing docstrings/type hints"
      success_criteria: "Specific violations documented with file/function names"
    
    - ac_id: "AC-AUDIT-006-03"
      description: "Compliance Report"
      requirement: "Generate report: {module}: {compliance%}"
      success_criteria: "Per-module compliance report created"
    
    - ac_id: "AC-AUDIT-006-04"
      description: "Decision Gate"
      requirement: "≥95%: APPROVED; 85-94%: CONDITIONAL; <85%: REMEDIATION"
      success_criteria: "Remediation plan (if needed) created"
  
  completion_verification:
    success_criteria:
      - "Compliance rate calculated for sample"
      - "Specific violations identified with locations"
      - "Remediation plan (if needed) documented"
      - "Extrapolation to full codebase provided"
```

---

### 8. PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH

```yaml
- phase_id: "PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH"
  track: "eval"
  machine: "eval"
  sequence: 4
  priority: "P2-MEDIUM"
  required: false
  blocking: false
  status: "NOT_STARTED"
  
  purpose: "Establish test coverage baseline and metrics"
  estimated_effort: "1 hour"
  depends_on: ["PHASE-AUDIT-002-PHASE-E-VERIFY"]
  
  acceptance_criteria:
    - ac_id: "AC-AUDIT-007-01"
      description: "Run Coverage Analysis"
      requirement: "Execute `pytest --cov=cortex --cov-report=term-missing` and document results"
      success_criteria: "Overall coverage % and per-module coverage documented"
    
    - ac_id: "AC-AUDIT-007-02"
      description: "Document Baseline"
      requirement: "Record coverage for major subsystems; set target ≥85%"
      success_criteria: "Baseline recorded in cortex-impl-map.yaml"
    
    - ac_id: "AC-AUDIT-007-03"
      description: "Identify Coverage Gaps"
      requirement: "Document files with <50% coverage; identify critical gaps"
      success_criteria: "Coverage gaps list created with priority"
    
    - ac_id: "AC-AUDIT-007-04"
      description: "Decision Gate"
      requirement: "≥85%: APPROVED; 70-84%: IMPROVEMENT_PLAN; <70%: REMEDIATION"
      success_criteria: "Coverage improvement plan (if needed) documented"
  
  completion_verification:
    success_criteria:
      - "Coverage % documented for overall and by module"
      - "Coverage report generated and archived"
      - "Baseline recorded in cortex-impl-map.yaml"
      - "Coverage gaps identified with specific files"
      - "Improvement plan (if needed) created"
```

---

## Integration Steps

### Step 1: Identify insertion point in cortex-impl-map.yaml
Find the eval track section around line 301-380 and locate `phases_implementation_status.not_started` section.

### Step 2: Add new phase YAML blocks
Insert all 8 phase definitions in the `not_started` section (or create new section for audit phases).

### Step 3: Update eval_track_state.phase_states
Add 8 new entries (one per phase) with initial state: NOT_STARTED, no start_time, no completion data.

### Step 4: Update eval_track strategy
Modify machine_tracks.eval section to add audit phases before KG phases:
```yaml
eval:
  strategy: "test_remediation + audit_verification + knowledge_graph_integration + knowledge_base_semantic_engine"
  phases:
    - PHASE-EVAL-001-TEST-REMEDIATION (COMPLETED) ✅
    - PHASE-AUDIT-001-EXPORT-VERIFY (P0 blocking)
    - PHASE-AUDIT-002-PHASE-E-VERIFY (P0 blocking)
    - PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT (P1 high)
    - PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK (P1 high)
    - CLEANUP-PHASE-001-ROADMAP-MAINTENANCE (P2 medium)
    - PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY (P2 medium)
    - PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK (P2 medium)
    - PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH (P2 medium)
    - PHASE-KG-001-005 (P2 optional, after audits)
```

### Step 5: Verify YAML structure
After adding all phases, validate:
```bash
python -c "import yaml; yaml.safe_load(open('cortex-impl-map.yaml'))"
```

---

## Timeline Summary

| Phase | Effort | Priority | Blocking | Timeline |
|-------|--------|----------|----------|----------|
| PHASE-AUDIT-001-EXPORT-VERIFY | 30 min | P0 | YES | Day 1 |
| PHASE-AUDIT-002-PHASE-E-VERIFY | 2-3 hrs | P0 | YES | Day 2 |
| PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT | 2-4 hrs | P1 | NO | Day 3-4 |
| PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE | 1-2 hrs | P1 | NO | Day 2-3 |
| CLEANUP-PHASE-001-ROADMAP-MAINTENANCE | 2-3 hrs | P2 | NO | Day 4-5 |
| PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY | 1 hr | P2 | NO | Day 5 |
| PHASE-AUDIT-006-DOCSTRING-COMPLIANCE | 1-2 hrs | P2 | NO | Day 5-6 |
| PHASE-AUDIT-007-COVERAGE-BASELINE | 1 hr | P2 | NO | Day 6 |
| **TOTAL** | **12-18 hrs** | | | **6 days** |

---

## Success Metrics

✅ **All 8 remediation phases created in cortex-impl-map.yaml**  
✅ **All 9 review findings F004-F012 mapped to phases**  
✅ **Blocking gates established (AUDIT-001, AUDIT-002)**  
✅ **Decision trees documented for each gate**  
✅ **Timeline realistic and achievable**  
✅ **Production readiness criteria defined**  

---

## References

- **Remediation Plan:** `EVAL-TRACK-REMEDIATION-PLAN-20260122.md`
- **Review Findings:** `docs/REVIEW-CORTEX-20260122.yaml` (findings F004-F012)
- **Review Summary:** `docs/REVIEW-CORTEX-20260122-SUMMARY.md`
- **Findings Capture Status:** `_workspaces/roadmap/REVIEW-FINDINGS-CAPTURE-STATUS.md`

