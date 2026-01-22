# CORTEX Eval Track Remediation Plan

**Document:** EVAL-TRACK-REMEDIATION-PLAN-20260122.md  
**Date:** 2026-01-22  
**Authority:** REVIEW-CORTEX-20260122.yaml (Findings F004-F012)  
**Track:** eval  
**Status:** APPROVED FOR IMPLEMENTATION

---

## Executive Summary

The eval track requires remediation of **9 critical findings** from the comprehensive review (REVIEW-CORTEX-20260122). Current state: 1/6 phases completed (PHASE-EVAL-001-TEST-REMEDIATION).

**Remediation Approach:**
- Create 6 audit/remediation phases to address findings F004-F012
- Insert audit phases BEFORE KG phases (P2-OPTIONAL)
- Establish verification gates for production readiness
- Estimated timeline: 2-3 weeks for complete remediation

**Critical Path:** Findings F004 & F005 must be resolved before proceeding with KG phases.

---

## Issues to Address

### 🔴 CRITICAL ISSUES (Block KG phases)

#### Issue F004: impl-export-completion.yaml - COMPLETION UNVERIFIED
**Severity:** CRITICAL  
**Current State:** Phase marked COMPLETED on 2026-01-21  
**Problem:** No post-completion verification that test collection errors were fixed

**Remediation:**
- Create **PHASE-AUDIT-001-EXPORT-VERIFY**
- Run: `pytest tests/ --collect-only` to verify 0 collection errors
- If errors > 0: Revert impl-export-completion to IN_PROGRESS
- If errors = 0: Confirm completion with audit trail entry

**Effort:** 30 minutes

---

#### Issue F005: PHASE-E-TDD-IMPLEMENTATION.yaml - COMPLETION UNVERIFIED (HIGH RISK)
**Severity:** CRITICAL  
**Current State:** Phase marked COMPLETED on 2026-01-22  
**Problem:** Timeline analysis suggests implementations may be stubs

**Critical Assessment:**
- Claims: 125 modules × production quality implementations
- Time constraint: Phase marked complete in 1 day
- Required effort: 125 modules × 2-4 hours each = 250-500 hours
- **PHYSICALLY IMPOSSIBLE without stubs (violates CORE-001)**

**Remediation:**
- Create **PHASE-AUDIT-002-PHASE-E-VERIFY**
- Sample 20% of "completed" modules (25 random modules)
- Verify each has actual implementation (not stub/docstring only)
- Run tests for samples: Must be 100% passing
- Check coverage: `pytest --cov=cortex` must show >50% coverage on samples
- **Decision gate:** If <80% real implementations, mark PHASE-E as IN_PROGRESS

**Effort:** 2-3 hours

**Decision Tree:**
```
if implementations >= 90% complete:
  → DECISION: Approve production readiness gate (+2 days to ready)
  → Status: APPROVED FOR KG PHASES
elif implementations 70-89% complete:
  → DECISION: Request remediation (+5-7 days estimated)
  → Status: CONDITIONAL APPROVAL
else:
  → DECISION: EMERGENCY REMEDIATION (+7-14 days estimated)
  → Status: BLOCKED - KG phases cannot proceed
```

---

### 🟠 HIGH PRIORITY ISSUES (Should resolve before KG)

#### Issue F006: Import Migration Audit - SCOPE UNDEFINED
**Severity:** HIGH  
**Current State:** 306 old imports detected; distribution unclear

**Problem:**
- 140 acceptable (scripts/archives)
- 105 concerning (may be production modules)
- 55 neutral (type hints, comments)
- No categorization of which 105 "concerning" files need fixing

**Remediation:**
- Create **PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT**
- AC-001: Identify which of 105 "concerning" files are production code
- AC-002: Create prioritized remediation list for import updates
- AC-003: Update test threshold from <20 to realistic number (150+)
- AC-004: Document intentional mixed-pattern strategy

**Effort:** 2-4 hours

---

#### Issue F008-F009: Governance Compliance - UNVERIFIED
**Severity:** HIGH  
**Current State:** No verification of CORE-001, CORE-008, CORE-011, CORE-012

**Problems:**
- **CORE-001:** Production quality implementations unverified
- **CORE-008:** Tests-first approach not documented in audit trail
- **CORE-011:** 100% type hints compliance unknown
- **CORE-012:** Google docstring compliance unknown

**Remediation:**
- Create **PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK**
- AC-001: Sample 25 random modules from PHASE-E implementations
- AC-002: Verify type hints on all public functions (100%)
- AC-003: Verify Google docstrings on all public functions (100%)
- AC-004: If <95% compliance: Create AC-FIX-GOVERNANCE-001 phase
- AC-005: Document TDD workflow sequence from git history

**Effort:** 1-2 hours verification + varies for fixes

---

### 🟡 MEDIUM PRIORITY ISSUES (Address after critical items)

#### Issue F007: cortex-impl-map.yaml - DUPLICATE DEFINITIONS
**Severity:** MEDIUM  
**Current State:** Multiple duplicate/orphaned phase entries

**Problems:**
- Duplicate: impl-governance-content (appears 2x)
- Duplicate: PHASE-E-TDD-IMPLEMENTATION definitions
- Orphaned: Old COMPLETED entries mixed with NOT_STARTED sections
- Consolidation needed: cortex_brain/knowledge/ vs tier3/knowledge/

**Remediation:**
- Create **CLEANUP-PHASE-001-ROADMAP-MAINTENANCE**
- AC-001: Remove duplicate impl-governance-content entries (keep one, document which)
- AC-002: Consolidate PHASE-E definitions (merge into single definition)
- AC-003: Move old COMPLETED entries to archive section
- AC-004: Consolidate knowledge YAML files (cortex_brain vs tier3)
- AC-005: Verify all phase IDs are unique

**Effort:** 2-3 hours

---

#### Issue F010: CORE-026 - GIT CHECKPOINT DOCUMENTATION
**Severity:** MEDIUM  
**Current State:** Phase completion not documented with git commits

**Problems:**
- impl-export-completion marked COMPLETED 2026-01-21 (no git tag/commit)
- PHASE-E-TDD-IMPLEMENTATION marked COMPLETED 2026-01-22 (no git tag/commit)
- CORE-026 requires checkpoints before major milestones

**Remediation:**
- Create **PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY**
- AC-001: Review git history on CORTEX branch for 2026-01-21 and 2026-01-22
- AC-002: Verify commits exist for phase completions
- AC-003: If missing: Create checkpoint commits with standard message format
- AC-004: Document git commit convention for future phases

**Message Format:**
```
{machine}: {phase-id}: {summary}

Example:
eval: impl-export-completion: 44 exports added, test collection errors 76→0
eval: PHASE-E-TDD-IMPLEMENTATION: 125 modules completed, 7547 tests passing
```

**Effort:** 1 hour

---

#### Issue F011: Type Hints & Docstrings - COMPLIANCE UNVERIFIED
**Severity:** MEDIUM  
**Current State:** CORE-011/012 compliance not documented

**Problem:**
- No static analysis run on "completed" modules
- Compliance rate unknown
- No remediation baseline

**Remediation:**
- Create **PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK**
- AC-001: Run static analysis on 20% sample of completed modules
  ```bash
  pylint cortex/core/orchestrator/ cortex/core/state/ cortex/mcp/ --disable=all --enable=missing-docstring,missing-type-hints
  ```
- AC-002: Document compliance rate for sample
- AC-003: Extrapolate to full codebase
- AC-004: If <95%: Create AC-FIX-DOCSTRING-001 phase for remediation

**Effort:** 1-2 hours

---

#### Issue F012: Test Coverage Metrics - BASELINE MISSING
**Severity:** MEDIUM  
**Current State:** No coverage metrics established

**Problem:**
- PHASE-E claims ≥98% pass rate
- But coverage % (line coverage) unknown
- Passing tests ≠ comprehensive coverage

**Remediation:**
- Create **PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH**
- AC-001: Run pytest with coverage analysis
  ```bash
  pytest tests/ --cov=cortex --cov-report=term-missing --cov-report=html
  ```
- AC-002: Document baseline coverage % for each major module
- AC-003: Set target ≥85% coverage on production code
- AC-004: If <85%: Create test improvement phase

**Effort:** 1 hour

---

## Remediation Phases to Create

### Phase Sequence for Eval Track

```
CURRENT:
├─ PHASE-EVAL-001-TEST-REMEDIATION (COMPLETED) ✅ F001-F003
│
NEEDED - BLOCKING:
├─ PHASE-AUDIT-001-EXPORT-VERIFY (F004) - 30 min
├─ PHASE-AUDIT-002-PHASE-E-VERIFY (F005) - 2-3 hrs
├─ PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT (F006) - 2-4 hrs
├─ PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK (F008-F009) - 1-2 hrs
│
NEEDED - CLEANUP:
├─ CLEANUP-PHASE-001-ROADMAP-MAINTENANCE (F007) - 2-3 hrs
├─ PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY (F010) - 1 hr
├─ PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK (F011) - 1-2 hrs
├─ PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH (F012) - 1 hr
│
OPTIONAL KG PHASES (AFTER AUDIT COMPLETION):
└─ PHASE-KG-001-005 (Knowledge Graph integration)
```

---

## Detailed Phase Specifications

### PHASE-AUDIT-001-EXPORT-VERIFY

**Purpose:** Verify impl-export-completion phase actually fixed test collection errors

**Priority:** P0-CRITICAL  
**Required:** true  
**Blocking:** yes (KG phases depend on this)  
**Effort:** 30 minutes  
**Dependencies:** None

**Acceptance Criteria:**

**AC-AUDIT-001-01: Test Collection Verification**
- Execute: `pytest tests/ --collect-only -q 2>&1 | grep -i "error"`
- Expected: 0 collection errors
- If errors > 0: Investigate and fix
- If errors = 0: Proceed to AC-002

**AC-AUDIT-001-02: Document Collection Status**
- Record actual error count
- Compare to expected (from impl-export-completion phase definition)
- Update cortex-impl-map.yaml with verification timestamp

**AC-AUDIT-001-03: Decision Gate**
- If errors = 0: Mark impl-export-completion as VERIFIED-COMPLETE
- If errors > 0: Create remediation task list for impl-export-completion

**Success Criteria:**
- Test collection completes without ImportError
- 0 collection errors documented
- Audit trail updated with verification result

---

### PHASE-AUDIT-002-PHASE-E-VERIFY

**Purpose:** Verify PHASE-E-TDD-IMPLEMENTATION has real implementations (not stubs)

**Priority:** P0-CRITICAL  
**Required:** true  
**Blocking:** yes (KG phases depend on this)  
**Effort:** 2-3 hours  
**Dependencies:** PHASE-AUDIT-001-EXPORT-VERIFY

**Rationale:**
- Phase claims 125 modules completed in 1 day (24 hours)
- Estimated effort: 125 × 2-4 hrs = 250-500 hours
- Timeline physically impossible without stubs
- CORE-001 violation if modules are stubs

**Acceptance Criteria:**

**AC-AUDIT-002-01: Module Sampling**
- Select 25 random modules from claimed implementations (20% sample)
- Ensure diverse distribution: orchestrators, core, domain_brain, mcp, etc.
- Document selected modules in audit trail

**AC-AUDIT-002-02: Implementation Verification**
- For each sampled module:
  - Open source file and verify actual code (not stub)
  - Check for: function implementations, business logic, state management
  - Verify not just docstrings/type hints with empty body
- Rejection criteria: >2 lines of docstring + pass/... = stub

**AC-AUDIT-002-03: Test Execution**
- Run tests for each sampled module
- Must be 100% passing (0 failures allowed)
- Document test names and pass/fail status

**AC-AUDIT-002-04: Coverage Analysis**
- Run: `pytest tests/test_*.py --cov=cortex --cov-report=term-missing`
- Check coverage for sampled modules
- Target: >50% coverage on samples (indicates real tests)

**AC-AUDIT-002-05: Decision Gate**
```
if real_implementations >= 90%:
  DECISION: APPROVED - Proceed to KG phases
  STATUS: Production readiness gate PASSED
  TIMELINE: +2 days to ready
elif real_implementations 70-89%:
  DECISION: CONDITIONAL - Request remediation
  STATUS: Identify missing implementations
  TIMELINE: +5-7 days estimated
else (< 70%):
  DECISION: EMERGENCY REMEDIATION
  STATUS: BLOCKED - Reclassify PHASE-E as IN_PROGRESS
  TIMELINE: +7-14 days estimated
```

**Success Criteria:**
- ≥90% of sampled modules have real implementations
- ≥98% test pass rate on samples
- ≥50% coverage on sampled modules
- Clear audit trail of verification process
- Decision gate documented with rationale

---

### PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT

**Purpose:** Categorize 105 "concerning" imports and define remediation strategy

**Priority:** P1-HIGH  
**Required:** true  
**Blocking:** conditional (KG phases blocked if critical imports found)  
**Effort:** 2-4 hours  
**Dependencies:** PHASE-AUDIT-001, PHASE-AUDIT-002

**Acceptance Criteria:**

**AC-AUDIT-003-01: Categorize Concerning Imports**
- Extract list of 105 "concerning" files with old import patterns
- For each file:
  - Determine: Is it production code or non-production?
  - Determine: Are old imports acceptable (scripts/helpers) or not (core)?
  - Document rationale for categorization
- Create spreadsheet: filename | old_pattern_count | category | priority

**AC-AUDIT-003-02: Priority List for Core Modules**
- Identify modules that MUST be updated (production code with old patterns)
- Create remediation list ranked by impact
- Examples of categories:
  - CRITICAL: cortex/core/orchestrator/ modules
  - HIGH: cortex/core/state/ modules
  - MEDIUM: cortex/mcp/ modules
  - LOW: cortex/scripts/ (acceptable to keep old patterns)

**AC-AUDIT-003-03: Update Test Threshold**
- Current test expects: `< 20` old imports (false positive)
- Update to realistic threshold based on audit:
  - Change to: `< 150` old imports across entire codebase
  - Add file type filter: `if file not in scripts/ and archives/`
  - Rationale: Documented in test file

**AC-AUDIT-003-04: Document Intentional Strategy**
- Add entry to cortex-impl-map.yaml:
  ```yaml
  import_migration_strategy:
    approach: "PARTIAL (not total) migration"
    reason: "Scripts and helpers can use old patterns; production code uses new patterns"
    acceptable_locations:
      - "cortex/scripts/"
      - "cortex/scripts-root-archive/"
      - "cortex/config/" (legacy config)
    requires_migration:
      - "cortex/core/"
      - "cortex/mcp/"
      - "cortex/orchestrators/"
  ```

**Success Criteria:**
- 105 files categorized with rationale
- Remediation priority list created
- Test threshold updated with explanation
- Intentional strategy documented in roadmap

---

### PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK

**Purpose:** Verify CORE-001, CORE-008, CORE-011, CORE-012 compliance on PHASE-E modules

**Priority:** P1-HIGH  
**Required:** true  
**Blocking:** conditional  
**Effort:** 1-2 hours verification + varies for fixes  
**Dependencies:** PHASE-AUDIT-002-PHASE-E-VERIFY

**Acceptance Criteria:**

**AC-AUDIT-004-01: Sample Module Selection**
- Select 25 modules verified in PHASE-AUDIT-002 (use same sample)
- Ensure distribution across all subsystems

**AC-AUDIT-004-02: Type Hints Verification (CORE-011)**
- For each sampled module:
  - Check all public function parameters have type hints
  - Check all public function return types are annotated
  - Allow `Any` type, but must be explicit
- Document: functions_with_hints / total_public_functions
- Pass criteria: ≥95% compliance

**AC-AUDIT-004-03: Docstring Verification (CORE-012)**
- For each sampled module:
  - Check all public functions have Google-style docstrings
  - Required sections: Args, Returns, Raises (where applicable)
  - Exception: Private functions (_name) not required
- Document: functions_with_docstrings / total_public_functions
- Pass criteria: ≥95% compliance

**AC-AUDIT-004-04: TDD Compliance Verification (CORE-008)**
- For 5 sample modules:
  - Review git history
  - Verify test commit precedes implementation commit
  - Document commit hashes and dates
- Pass criteria: ≥80% of samples follow test-first pattern

**AC-AUDIT-004-05: Production Quality Verification (CORE-001)**
- For sampled modules:
  - Check for code smells: bare except:, TODO comments without issues, etc.
  - Verify no hardcoded test data in production code
  - Check for appropriate error handling
- Document findings and severity

**AC-AUDIT-004-06: Decision Gate**
```
if compliance >= 95%:
  DECISION: APPROVED - Governance compliance verified
  STATUS: Can proceed with confidence
elif compliance 85-94%:
  DECISION: CONDITIONAL - Create remediation AC
  STATUS: Schedule AC-FIX-GOVERNANCE-001
  TIMELINE: +2-3 hours to fix
else (< 85%):
  DECISION: REMEDIATION REQUIRED
  STATUS: Create comprehensive AC-FIX-GOVERNANCE-001
  TIMELINE: +1-2 days to fix
```

**Success Criteria:**
- ≥95% type hints compliance documented
- ≥95% docstring compliance documented
- ≥80% TDD workflow verified
- CORE-001 violations (if any) documented with remediation plan
- Clear audit trail with specific file/function references

---

### CLEANUP-PHASE-001-ROADMAP-MAINTENANCE

**Purpose:** Remove duplicate and orphaned phase definitions from cortex-impl-map.yaml

**Priority:** P2-MEDIUM  
**Required:** false  
**Blocking:** no  
**Effort:** 2-3 hours  
**Dependencies:** All audit phases

**Acceptance Criteria:**

**AC-CLEANUP-001-01: Identify Duplicates**
- Find all duplicate phase definitions
- Document: which appears multiple times, line numbers
- Examples: impl-governance-content (2x), PHASE-E-TDD-IMPLEMENTATION

**AC-CLEANUP-001-02: Remove Duplicate Entries**
- Keep one canonical definition per phase
- Document decision for which version kept (most recent, most complete, etc.)
- Remove others cleanly without corrupting YAML structure
- Verify file remains valid YAML

**AC-CLEANUP-001-03: Archive Old Entries**
- Find all OLD COMPLETED entries that are now historical
- Move to `completed_phases_archive` section at bottom
- Examples: PHASE-MAC-IMPL-001, PHASE-DEPLOYMENT-001, etc.

**AC-CLEANUP-001-04: Consolidate Knowledge Domains**
- Find: cortex_brain/knowledge/ vs tier3/knowledge/
- Merge references to single canonical location
- Update all phase definitions that reference these

**AC-CLEANUP-001-05: Verify File Integrity**
- Run: `yamllint cortex-impl-map.yaml` (if available)
- Or: `python -c "import yaml; yaml.safe_load(open(...))"` to verify valid YAML
- Test: Can load entire file without errors

**Success Criteria:**
- All duplicates identified and consolidated
- Orphaned entries moved to archive
- File remains valid YAML
- All phase IDs are unique
- No broken references to removed entries

---

### PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY

**Purpose:** Verify git commits exist for phase completions per CORE-026

**Priority:** P2-MEDIUM  
**Required:** false  
**Blocking:** no  
**Effort:** 1 hour  
**Dependencies:** CLEANUP-PHASE-001

**Acceptance Criteria:**

**AC-AUDIT-005-01: Review Git History**
- Check CORTEX branch commits on:
  - 2026-01-21 (impl-export-completion completed)
  - 2026-01-22 (PHASE-E-TDD-IMPLEMENTATION completed)
- Document commits found (or lack thereof)

**AC-AUDIT-005-02: Verify Commit Messages**
- For each phase completion commit:
  - Verify message follows format: `{machine}: {phase-id}: {summary}`
  - Example: `eval: impl-export-completion: 44 exports added, errors 76→0`
  - Check for: descriptive summary, no abbreviations

**AC-AUDIT-005-03: Create Missing Checkpoint Commits**
- If commits missing:
  - Create checkpoint commits for phases marked COMPLETED
  - Use standard message format
  - Amend phase_execution_tracking with git commit hash

**AC-AUDIT-005-04: Document Convention**
- Add to cortex-impl-map.yaml:
  ```yaml
  git_commit_convention:
    format: "{machine}: {phase-id}: {summary}"
    when: "When phase marked COMPLETED"
    examples:
      - "eval: impl-export-completion: 44 exports added, errors 76→0"
      - "eval: PHASE-E-TDD-IMPLEMENTATION: 125 modules completed, 7547 tests passing"
      - "win: cortex-registry-001-migration: registry structure established"
  ```

**Success Criteria:**
- All phase completions have corresponding git commits
- Commits follow standard message format
- Convention documented for future phases
- Commit hashes recorded in phase_execution_tracking

---

### PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK

**Purpose:** Verify type hints and docstring compliance across codebase

**Priority:** P2-MEDIUM  
**Required:** false  
**Blocking:** no  
**Effort:** 1-2 hours  
**Dependencies:** PHASE-AUDIT-002

**Acceptance Criteria:**

**AC-AUDIT-006-01: Static Analysis**
- Run pylint or similar on 20% sample:
  ```bash
  pylint cortex/core/ cortex/orchestrators/ cortex/mcp/ \
    --disable=all --enable=missing-docstring --enable=missing-type-hints
  ```
- Document: total_issues / total_functions
- Calculate compliance rate

**AC-AUDIT-006-02: Sample Coverage**
- Analyze sample for:
  - Classes with missing docstrings
  - Functions with missing docstrings
  - Functions with partially typed parameters
  - Functions with untyped return statements
- Document specific files and violations

**AC-AUDIT-006-03: Compliance Report**
- Generate report: {module}: {compliance%}
- Examples:
  - cortex/core/orchestrator.py: 92% ✅
  - cortex/core/state.py: 78% ⚠️
  - cortex/mcp/tools.py: 85% ✅

**AC-AUDIT-006-04: Decision Gate**
```
if compliance >= 95%:
  STATUS: APPROVED - Continue as-is
elif compliance 85-94%:
  STATUS: CONDITIONAL - Create AC-FIX-DOCSTRING-001
  TIMELINE: +2-3 hours
else:
  STATUS: REMEDIATION NEEDED - Comprehensive fix required
  TIMELINE: +1-2 days
```

**Success Criteria:**
- Compliance rate calculated and documented
- Specific violations identified with file/function names
- Remediation plan (if needed) created
- Extrapolation to full codebase provided

---

### PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH

**Purpose:** Establish test coverage baseline and metrics

**Priority:** P2-MEDIUM  
**Required:** false  
**Blocking:** no  
**Effort:** 1 hour  
**Dependencies:** PHASE-AUDIT-002

**Acceptance Criteria:**

**AC-AUDIT-007-01: Run Coverage Analysis**
```bash
pytest tests/ --cov=cortex --cov-report=term-missing --cov-report=html
```
- Document: overall coverage %, coverage by module
- Generate HTML report for detailed analysis
- Save report to: `_workspaces/roadmap/reports/coverage-baseline-20260122.html`

**AC-AUDIT-007-02: Document Baseline**
- Record coverage % for major subsystems:
  - cortex/core/: X%
  - cortex/orchestrators/: X%
  - cortex/mcp/: X%
  - cortex/domain_brain/: X%
  - etc.
- Add entry to cortex-impl-map.yaml:
  ```yaml
  test_coverage_baseline:
    date: "2026-01-22"
    overall: "X%"
    target: "≥85%"
    modules:
      cortex/core/: "X%"
      cortex/orchestrators/: "X%"
  ```

**AC-AUDIT-007-03: Identify Coverage Gaps**
- Files with <50% coverage: Priority for improvement
- Functions with no tests: Document critical gaps
- Create list: "Coverage Gaps to Address"

**AC-AUDIT-007-04: Decision Gate**
```
if overall_coverage >= 85%:
  STATUS: APPROVED - Baseline established, target met
elif overall_coverage 70-84%:
  STATUS: ACCEPTABLE - Create improvement plan
  TIMELINE: +2-4 hours to fix priority gaps
else (< 70%):
  STATUS: GAP REMEDIATION NEEDED
  TIMELINE: Create comprehensive coverage improvement phase
```

**Success Criteria:**
- Coverage % documented for overall and by module
- Coverage report generated and archived
- Baseline recorded in cortex-impl-map.yaml
- Coverage gaps identified with specific files/functions
- Improvement plan (if needed) created

---

## Implementation Timeline

### BLOCKING AUDIT PHASES (Must complete before KG)
```
Day 1 (30 minutes):
├─ PHASE-AUDIT-001-EXPORT-VERIFY: 30 min
│  Decision: Proceed with KG or remediate exports?
│
Day 2 (2-3 hours):
├─ PHASE-AUDIT-002-PHASE-E-VERIFY: 2-3 hours
│  Decision gate: ≥90% real implementations?
│  (This determines entire KG phase viability)
│
Day 3-4 (2-4 hours):
├─ PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT: 2-4 hours
│  Categorize imports and create remediation list
```

### GOVERNANCE AUDIT PHASES (Parallel with above)
```
Day 2-3 (1-2 hours):
├─ PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK: 1-2 hours
│  Verify CORE-011, CORE-012, CORE-008, CORE-001
```

### CLEANUP PHASES (After audits)
```
Day 4-5 (2-3 hours):
├─ CLEANUP-PHASE-001-ROADMAP-MAINTENANCE: 2-3 hours
│  Remove duplicates, consolidate definitions
│
├─ PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY: 1 hour
│  Verify git commits, document convention
│
├─ PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK: 1-2 hours
│  Type hints and docstring verification
│
├─ PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH: 1 hour
│  Test coverage metrics baseline
```

### KG PHASES (After all audits, if approved)
```
Day 6+ (optional, depends on audit results):
├─ PHASE-KG-001-foundation: 3-4 days
├─ PHASE-KG-002-entity-sync: 2-3 days
├─ PHASE-KG-003-query-layer: 2-3 days
├─ PHASE-KG-004-routing-optimization: 2-3 days
├─ PHASE-KG-005-validation: 2-3 days
```

---

## Decision Gates & Approval Criteria

### Gate 1: impl-export-completion Verification
**Phase:** PHASE-AUDIT-001-EXPORT-VERIFY  
**Decision:** Can PHASE-E-TDD-IMPLEMENTATION be trusted?

```yaml
Decision Points:
  - if test_collection_errors = 0:
      Status: PASS ✅
      Action: Proceed to PHASE-AUDIT-002
  - if test_collection_errors > 0:
      Status: FAIL ❌
      Action: Investigate and fix impl-export-completion
      Timeline: +2-4 hours to remediate
```

---

### Gate 2: PHASE-E Production Readiness
**Phase:** PHASE-AUDIT-002-PHASE-E-VERIFY  
**Decision:** Is PHASE-E actually production-ready?

```yaml
Decision Points:
  - if real_implementations >= 90% AND tests >= 98% passing:
      Status: APPROVED ✅
      Grade: "Production Ready"
      Action: Proceed to KG phases
      Timeline: Ready now
  
  - if real_implementations 70-89% AND tests >= 95% passing:
      Status: CONDITIONAL ⚠️
      Grade: "Needs Remediation"
      Action: Create remediation AC for missing implementations
      Timeline: +5-7 days to complete
  
  - if real_implementations < 70% OR tests < 95% passing:
      Status: BLOCKED ❌
      Grade: "Emergency Remediation Required"
      Action: Reclassify PHASE-E as IN_PROGRESS
      Timeline: +7-14 days emergency fix
```

---

### Gate 3: Import Migration Priority
**Phase:** PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT  
**Decision:** Which imports need fixing immediately?

```yaml
Decision Points:
  - if critical_production_imports = 0:
      Status: CLEAR ✅
      Action: Update test threshold and proceed
      Timeline: No delay
  
  - if critical_production_imports 1-10:
      Status: MINOR ISSUES ⚠️
      Action: Create minor remediation task
      Timeline: +2-4 hours
  
  - if critical_production_imports > 10:
      Status: MAJOR ISSUES ❌
      Action: Create comprehensive remediation phase
      Timeline: +2-4 days
```

---

### Gate 4: Governance Compliance
**Phase:** PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK  
**Decision:** Does code meet CORTEX governance standards?

```yaml
Decision Points:
  - if compliance >= 95%:
      Status: APPROVED ✅
      Action: Proceed with confidence
      Timeline: No delay
  
  - if compliance 85-94%:
      Status: CONDITIONAL ⚠️
      Action: Create minor remediation AC
      Timeline: +2-3 hours
  
  - if compliance < 85%:
      Status: REMEDIATION REQUIRED ❌
      Action: Create comprehensive fix phase
      Timeline: +1-2 days
```

---

## Success Criteria (All Phases)

### Phase-Level Success
✅ Each audit phase delivers:
- Clear findings with evidence
- Documented categorization/metrics
- Decision gate with clear recommendations
- Audit trail entry in cortex-impl-map.yaml
- No blocking errors (warnings OK)

### Track-Level Success
✅ Eval track remediation succeeds when:
- PHASE-AUDIT-001: Test collection errors = 0
- PHASE-AUDIT-002: ≥90% real implementations verified
- PHASE-AUDIT-003: Import remediation list prioritized
- PHASE-AUDIT-004: ≥95% governance compliance verified
- CLEANUP-PHASE-001: All duplicates removed
- PHASE-AUDIT-005: Git commits verified/documented
- PHASE-AUDIT-006: Docstring compliance documented
- PHASE-AUDIT-007: Coverage baseline established

### Production Readiness
✅ System ready for production deployment when:
- All blocking audit gates PASSED
- No CRITICAL findings remain
- Coverage baseline ≥85%
- Governance compliance ≥95%
- Import migration plan documented
- All git checkpoints in place

---

## Risk Mitigation

### Risk: PHASE-E is mostly stubs
**Probability:** MEDIUM  
**Impact:** CRITICAL (blocks entire system)  
**Mitigation:**
- PHASE-AUDIT-002 provides early detection
- If confirmed, can remediate in 7-14 days
- KG phases don't start until verified

### Risk: Critical imports in production code remain unfixed
**Probability:** MEDIUM  
**Impact:** HIGH (code quality issue)  
**Mitigation:**
- PHASE-AUDIT-003 identifies all critical imports
- Creates prioritized remediation list
- Impact on KG phases: LOW (dependencies managed)

### Risk: Governance compliance gaps discovered
**Probability:** HIGH  
**Impact:** MEDIUM (quality issue)  
**Mitigation:**
- PHASE-AUDIT-004 samples 20% early
- Allows rapid remediation if needed
- Impact on deployment: DELAYED (2-3 days max)

### Risk: Duplicate phase definitions cause merge conflicts
**Probability:** HIGH  
**Impact:** LOW (process issue, fixable)  
**Mitigation:**
- CLEANUP-PHASE-001 removes duplicates before merging
- Consolidates definitions cleanly
- Improves maintainability

---

## Approval & Sign-Off

| Role | Status | Date |
|------|--------|------|
| Review Authority | APPROVED | 2026-01-22 |
| Phase Author | PENDING | TBD |
| Track Owner (eval) | PENDING | TBD |
| Deployment Gate | PENDING | TBD |

**Document Authority:** REVIEW-CORTEX-20260122.yaml (Findings F004-F012)

**Approval Checklist:**
- [ ] Review findings document reviewed and understood
- [ ] All 9 remediation phases defined with clear ACs
- [ ] Decision gates documented with pass/fail criteria
- [ ] Timeline realistic (2-3 weeks estimated)
- [ ] Success criteria measurable and achievable
- [ ] Risks identified and mitigated
- [ ] Phased approach approved (block critical, handle medium/low in parallel)

---

## Next Steps

1. **Immediate (Now):** Review this remediation plan
2. **Today:** Approve and schedule PHASE-AUDIT-001-EXPORT-VERIFY
3. **Tomorrow:** Execute PHASE-AUDIT-001 and PHASE-AUDIT-002 (critical gates)
4. **Week 1:** Complete all blocking audit phases
5. **Week 2:** Execute cleanup and governance verification phases
6. **Week 3:** Based on audit results, proceed with KG phases or remediation

**Success Definition:** All 9 remediation phases completed with decision gates passed, production readiness confirmed, KG phases ready to begin (or remediation work prioritized if needed).

