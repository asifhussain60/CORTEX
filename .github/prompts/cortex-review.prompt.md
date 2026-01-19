# CORTEX Review System - Unified & Surgical
## Complete Review Protocol with Investigation & Implementation Support

**Version:** 3.1 (Jan 18, 2026) - NOW WITH SYSTEMATIC GAP INTEGRATION ⭐  
**Status:** PRODUCTION READY ✅  
**Efficiency:** 4.5 hours (investigation + fix + review + delivery)  
**Confidence:** A-grade evidence (95%+)

**🆕 NEW (2026-01-18): Systematic Gap Identification & Remediation**

Every review AUTOMATICALLY produces actionable gaps that are:
- ✅ Extracted from findings (Phase 3A)
- ✅ Analyzed holistically (Phase 3B)
- ✅ Generated as structured YAML (Phase 3C)
- ✅ Integrated into cortex-master.yaml (cortex-builder.prompt.md automatic)
- ✅ No manual gap management needed

**Result:** From findings to master plan remediation in single workflow.

---

## ⚠️ FILE OUTPUT GUIDELINES (CRITICAL)

**ALL markdown (.md) files created by Copilot MUST go to `docs/` folder.**

**ALL Python scripts (.py) must be created in appropriate toolkit folders.**

**FORBIDDEN:** `docs_md/` folder (❌ NEVER create this)
- All documentation goes to `docs/` (not `docs_md`)
- If you see code trying to create `docs_md/`: REPORT & FIX IMMEDIATELY
- Phase YAMLs go ONLY to `_workspaces/roadmap/phases/` (not anywhere else)

**DO NOT create files in:**
- ❌ Root directory
- ❌ `.github/` directory  
- ❌ `_workspaces/` directory (except reports/, issues/, phases/, tools/)
- ❌ `docs_md/` folder (FORBIDDEN)
- ❌ Any other non-standard location

**File Placement Rules:**
| File Type | Location | Example |
|-----------|----------|---------|
| Markdown docs | `docs/` | `docs/AC-FIX-001-02.md` |
| Python utilities | `scripts/` | `scripts/analysis_tool.py` |
| MCP toolkit | `src/mcp/tools/` | `src/mcp/tools/analysis.py` |
| Python analysis | `cortex_brain/tierX/` | `cortex_brain/tier2/analysis.py` |
| Investigation YAML | `_workspaces/roadmap/issues/` | `REVIEW-INVESTIGATION-REPORT-*.yaml` |
| Consolidated findings | `_workspaces/roadmap/issues/` | `REVIEW-FINDINGS-CONSOLIDATED-*.yaml` |
| Phase reports | `_workspaces/roadmap/reports/` | `phase-remediation-*.yaml` |
| Phase YAML specs | `_workspaces/roadmap/phases/` | `phase-XX.yaml` (AUTHORITATIVE) |

**Markdown Creation Rule:** Create MD files ONLY when:
- ✅ Needed for CORTEX execution (test plans, investigation summaries)
- ✅ Needed for planning (phase roadmaps, remediation guides)
- ✅ Required by governance (audit trails, CORE compliance docs)
- ✅ ALWAYS in `docs/` folder (NOT in _workspaces/roadmap/)
- ❌ NOT for routine reporting (use YAML instead)
- ❌ NOT for exploratory analysis (inline in terminal only)
- ❌ NEVER in `docs_md/` (FORBIDDEN) or `_workspaces/roadmap/` root

**Python Script Handling:**
- ✅ Create in `scripts/`, `src/mcp/tools/`, or `cortex_brain/tierX/` as appropriate
- ❌ NEVER in `_workspaces/roadmap/tools/` (use `src/mcp/tools/` instead)
- ✅ Use in toolkit analysis and execution
- ❌ NEVER leave temporary .py scripts in root
- ❌ NEVER create exploratory scripts and abandon them
- Cleanup: Delete or archive to appropriate home location after session

**Minimalist Approach:**
- Default to YAML output (structured, queryable)
- Use MD only for human-readable execution guides
- Use .py only for reusable toolkit components
- Do NOT create separate "report" files unless explicitly requested
- Avoid: temporary scripts, exploratory MD files, analysis dumps

---

## 🎯 QUICK START

### For Root Cause Investigation
→ Jump to **PHASE 0.5: SURGICAL INVESTIGATION** (page ~50)

### For Review Execution  
→ Jump to **PHASE 1: SYSTEMATIC AGENT ANALYSIS** (page ~70)

### For Complete Workflow
→ Read sections in order: Phase 0 → 0.5 (if needed) → 1 → 2 → 3

### For Implementation After Findings
→ Reference **CORTEX-INTEGRATED-SYSTEM-v3.md** (companion doc)

---

## SYSTEM OVERVIEW

```
CORTEX Review System v3.0
├─ Phase 0 (15 min): Data quality validation gates
├─ Phase 0.5 (30-45 min): Surgical investigation (if Phase 0 fails)
├─ Phase 1 (2-3 hours): Parallel agent analysis (5 specialized agents)
├─ Phase 2 (30 min): Consolidate findings into YAML report
└─ Phase 3 (immediate): Handoff to CORTEX Builder for remediation

Efficiency vs v2:
- Surgical investigation: +30 min (prevents blind regeneration)
- Parallel agents: -30 min (5 agents parallel, not sequential)
- Root cause analysis: +15 min (prevents false positives)
- Net result: 4.5 hours total (vs 6-8 hours blind approach)

Key Innovation: Identify ROOT CAUSE before regenerating data
(Saves hours + prevents masking real issues)
```

---

## LESSONS LEARNED FROM PREVIOUS REVIEWS

### Chat01 Review Analysis (Critical Insights)

**What Happened:** Chat01 reviewed CORTEX and found:
- 150+ hash chain breaks (actual: 78 real breaks from 1 design defect)
- 0 audit entries (actual: 6590 entries)
- Audit readiness: 3.2/10 (actual: 8.5/10)

**Root Causes of False Positives:**
1. Checked audit state DURING test (before DB commit), not after
2. Didn't filter test fixtures (6 test ACs mixed with 279 production ACs)
3. Didn't classify defect type (test artifact vs code bug)
4. Didn't grade evidence (speculation treated as verified fact)
5. Didn't investigate root cause (jumped to severity estimates)
6. Didn't validate assumptions (about persistence timing)

**This Version Prevents These Errors:**
- ✅ Gate 0A: Data freshness check (< 24 hours)
- ✅ Gate 0B: Audit trail completeness (all AC_START/EXECUTE/COMPLETE)
- ✅ Gate 0C: Hash chain integrity (cryptographic verification)
- ✅ Gate 0D: Test isolation (known fixtures filtered)
- ✅ Phase 0.5: Surgical investigation with decision tree
- ✅ Evidence grading: A/B/C grades (no D-grade speculation)
- ✅ Root cause framework: Classifies defect type (test vs code vs timing)
- ✅ Assumption verification: All assumptions explicitly checked

---

## PHASE 0: PRE-REVIEW VALIDATION GATES (15 minutes)

### Overview

**Critical First Step:** Before ANY analysis, validate data quality with 4 mandatory gates.

**Why This Matters:** Chat01 checked data at wrong time (during execution) and got false positives. These gates check at correct time (after persistence) and filter test fixtures.

### MANDATORY Gate 0A: Data Freshness Validation

```sql
-- Check when audit log was last updated
SELECT MAX(timestamp) as latest_entry, 
       CURRENT_TIMESTAMP as now_time
FROM audit_log;

-- Acceptance Criteria:
-- Latest entry must be < 24 hours old
-- Otherwise: Data is stale, regenerate fresh audit log
```

**What This Catches:**
- Old audit logs from previous review cycles
- Stale test data that should be discarded
- Database snapshots that don't reflect current code

**If Fails:** Regenerate audit log from scratch and retry Phase 0

### MANDATORY Gate 0B: Audit Trail Completeness

```sql
-- Count entries with standard lifecycle operations
SELECT 
  SUM(CASE WHEN operation = 'AC_START' THEN 1 ELSE 0 END) as ac_starts,
  SUM(CASE WHEN operation = 'AC_EXECUTE' THEN 1 ELSE 0 END) as ac_executes,
  SUM(CASE WHEN operation = 'AC_COMPLETE' THEN 1 ELSE 0 END) as ac_completes,
  COUNT(*) as total_entries
FROM audit_log;

-- Acceptance Criteria:
-- total_entries >= 2000 (robust dataset)
-- Each AC should have AC_START, >= AC_EXECUTE, AC_COMPLETE
```

**What This Catches:**
- Missing audit entries (incomplete lifecycle)
- Audit logger not working
- Database corruption (missing records)

**If Fails:** Regenerate audit log and verify audit logger functioning

### MANDATORY Gate 0C: Hash Chain Integrity Validation

```bash
# Run integration test that validates hash chain
pytest tests/integration/test_audit_trail_integrity.py::test_hash_chain_integrity -v

# Expected: PASS ✅
# If FAIL: ❌ → Proceed to Phase 0.5 (Surgical Investigation)
```

**What This Catches:**
- Broken cryptographic linkage (tamper-evidence violated)
- Hash calculation defects
- Data corruption in hash fields

**If Fails:** Do NOT regenerate yet. → Go to Phase 0.5

### MANDATORY Gate 0D: Test Isolation Verification

```sql
-- Check how many test fixtures are in production audit log
SELECT 
  COUNT(DISTINCT ac_id) as test_fixture_count,
  GROUP_CONCAT(DISTINCT ac_id) as fixture_ids
FROM audit_log
WHERE ac_id IN ('AC-CHAIN-000', 'AC-CHAIN-001', 'AC-DECORATOR-001', 
                 'AC-HASH-001', 'AC-INVALID-999')
OR ac_id LIKE 'AC-TEST-%';

-- Acceptance Criteria:
-- <= 6 test fixtures (known fixtures only)
-- If > 6: Additional test data contamination detected
```

**What This Catches:**
- Test data mixed with production audit entries
- Test fixtures not being properly isolated
- Test suite creating unexpected entries

**If Fails:** Review test isolation and potentially regenerate

---

## PHASE 0 DECISION LOGIC

```yaml
decision_tree:
  all_4_gates_pass:
    action: "Proceed to Phase 1 (Agent Analysis)"
    timing: "~2-3 hours for full review"
    confidence: "High (clean data, ready for analysis)"
  
  gate_0c_fails_only:
    action: "Proceed to Phase 0.5 (Surgical Investigation)"
    timing: "~30-45 minutes to determine root cause"
    purpose: "Distinguish: test artifact vs design defect vs timing issue"
    outcome: "Create AC-FIX if needed, regenerate, resume Phase 1"
  
  gate_0a_0b_0d_fails:
    action: "HALT and Regenerate"
    timing: "~15 minutes to clean regen"
    then: "Retry Phase 0 from start"
```

**Key Principle:** If hash chain fails, INVESTIGATE before regenerating (Phase 0.5). Don't blindly regenerate without knowing why.

---

## PHASE 0.5: SURGICAL INVESTIGATION (Optional - 30-45 minutes)

### When to Use This Phase

**Triggered by:** Hash chain test failure in Phase 0 (Gate 0C)

**Purpose:** Determine ROOT CAUSE of hash chain break

**NOT Using This:** Wastes 2-3 hours analyzing broken data, discovers issue too late

**Output:** REVIEW-INVESTIGATION-REPORT-YYYYMMDD.yaml with classification

### Surgical Investigation Workflow

#### Step 1: Identify Problem AC-IDs

```sql
-- Find which AC-IDs have hash chain violations
SELECT 
  ac_id,
  COUNT(*) as violation_count,
  operation,
  MIN(id) as first_violation,
  MAX(id) as last_violation
FROM audit_log
WHERE [hash chain check fails]
GROUP BY ac_id, operation
ORDER BY violation_count DESC;

-- Document: Top 5 problem AC-IDs with entry counts
```

**Output:** List of AC-IDs with broken chains (example: AC-FIX-001-01 has 74 violations)

#### Step 2: Classify Defect Type (Decision Tree)

For each problem AC-ID, answer these questions:

```
Q1: Is AC-ID in TEST_FIXTURES?
    YES → Defect Type: TEST_ARTIFACT
    NO  → Continue to Q2

Q2: Does AC have custom operation names (not AC_START/EXECUTE/COMPLETE)?
    YES → Continue to Q3
    NO  → Continue to Q3

Q3: Does code have TODO/NotImplementedError for this operation?
    YES → Defect Type: INCOMPLETE_IMPL
    NO  → Continue to Q4

Q4: Were entries inserted during test execution (BEFORE persistence)?
    YES → Defect Type: TIMING_ISSUE
    NO  → Continue to Q5

Q5: Does code inspection show hash calculation bug?
    YES → Defect Type: HASH_CALC_BUG
    NO  → Continue to Q6

Q6: Is this legitimate production data (not test artifact)?
    YES → Flag for manual investigation
    NO  → Defect Type: TEST_ARTIFACT
```

**Example Classification:**
```
AC-FIX-001-01 Investigation:
  Q1: NOT in TEST_FIXTURES → Not test artifact
  Q2: Has coordinate_test_op, coordinate_validate, coordinate_enforce → Custom ops
  Q3: Code shows previous_hash = "" (hardcoded) → INCOMPLETE_IMPL
  Classification: IMPLEMENTATION_FLAW in DatabaseTransactionManager._log_audit_entry()
  Evidence Grade: A (95% confidence - direct code inspection)
```

#### Step 3: Determine Remediation Path

```yaml
remediation_paths:
  
  test_artifact:
    issue: "Test data incorrectly in production audit log"
    fix: "Add AC-ID to TEST_FIXTURES list + update SQL filters"
    verification: "Regenerate, test hash chain PASSES"
    timeline: "15 min"
    proceed_to_phase_1: "YES (immediately)"
  
  incomplete_impl:
    issue: "Code has TODO or incomplete implementation"
    fix: "Create AC-FIX-XXX-XX to complete implementation"
    verification: "Fix code, run unit test locally PASSES, regenerate"
    timeline: "1-2 hours (depending on fix complexity)"
    proceed_to_phase_1: "YES (after AC-FIX complete)"
  
  timing_issue:
    issue: "Test checks state during execution (before DB commit)"
    fix: "Add timing gate to test (wait for persistence window)"
    verification: "Regenerate, test passes"
    timeline: "30 min"
    proceed_to_phase_1: "YES (immediately)"
  
  hash_calc_bug:
    issue: "Hash calculation defect in code (wrong algorithm or missing input)"
    fix: "Create AC-FIX-XXX-XX to fix calculation"
    verification: "Fix code, unit test PASSES, regenerate"
    timeline: "1 hour"
    proceed_to_phase_1: "YES (after AC-FIX complete)"
```

#### Step 4: Document Investigation

**Create:** `_workspaces/roadmap/issues/REVIEW-INVESTIGATION-REPORT-YYYYMMDD.yaml`

```yaml
investigation:
  id: "INV-NNN"
  date: "2026-01-18"
  
  findings:
    - ac_id: "AC-FIX-001-01"
      violation_count: 74
      defect_type: "IMPLEMENTATION_FLAW"
      root_cause: "Hash chain calculation hardcoded to empty string"
      code_location: "src/infrastructure/database_transaction_manager.py line 220"
      evidence:
        - "SQL Query: 74 coordinate_* operations with broken chain linkage"
        - "Code Inspection: previous_hash = '' (hardcoded, not calculated)"
        - "Test: test_hash_chain_integrity correctly identifies violations"
      evidence_grade: "A"  # 95% confidence
      remediation: "AC-FIX-001-02 (fix) + AC-FIX-001-03 (validation)"
      effort: "1.75 hours"
      
  conclusion: "Do NOT blindly regenerate. Fix code first. 78 violations are real."
```

#### Step 5: Execute Remediation

**If INCOMPLETE_IMPL or HASH_CALC_BUG:**

1. Create AC-FIX-XXX-XX AC-ID
2. Implement using TDD (test first, code second)
3. Verify locally: Unit test passes
4. Verify governance: All CORE rules compliant
5. Lock AC: Log AC_COMPLETE
6. Regenerate audit log (fresh start with fixed code)
7. Verify: test_hash_chain_integrity PASSES ✅
8. Resume: Phase 1 (Full review)

**If TEST_ARTIFACT or TIMING_ISSUE:**

1. Update test fixtures or timing gate
2. Regenerate audit log
3. Verify: test_hash_chain_integrity PASSES ✅
4. Resume: Phase 1 immediately

---

## PHASE 1: SYSTEMATIC AGENT ANALYSIS (2-3 hours)

### Overview

**After Phase 0/0.5:** All gates passed, data is clean, ready for systematic analysis.

**5 Specialized Agents:** Run in parallel (48 min total, not sequential 60+ min)

```
Agent 1: Brittleness          (12 min) → Findings-BRIT-*.yaml
Agent 2: Hallucination        (10 min) → Findings-HALL-*.yaml
Agent 3: Governance           (8 min)  → Findings-GOV-*.yaml
Agent 4: Assumptions          (8 min)  → Findings-ASM-*.yaml
Agent 5: Debt                 (10 min) → Findings-DEBT-*.yaml
─────────────────────────────────────────────────────
PARALLEL EXECUTION            (48 min)
```

### Agent 1: BRITTLENESS

**File:** `.github/agents/cortex-review-brittleness.md`

**Purpose:** Identify structural weaknesses that break under load

**Checks:**
- Single Points of Failure (SPOFs)
- Missing error handling paths
- Bare except clauses (`except:` without exception type)
- TODO/FIXME/HACK/XXX markers
- Uncovered code paths (< 85% coverage)
- File locking issues
- Database connection leaks
- Memory leaks in long-running operations

**Evidence Sources:**
```bash
grep -r "except:" src/ --include="*.py"           # Bare except
grep -r "TODO\|FIXME\|HACK" src/ --include="*.py" # Deferred work
pytest --cov=src --cov-report=term-missing        # Coverage gaps
```

**Output:** `Findings-BRIT-YYYYMMDD.yaml`

### Agent 2: HALLUCINATION

**File:** `.github/agents/cortex-review-hallucination.md`

**Purpose:** Identify AI safety risks (unvalidated output, injection vectors)

**Checks:**
- LLM prompt injection vectors
- Unvalidated AI-generated code execution
- Missing grounding for responses
- Lack of human-in-the-loop gates
- Missing confidence thresholds
- Template interpolation without sanitization
- Context window overflow handling
- MCP protocol compliance

**Evidence Sources:**
```bash
grep -r "@mcp_tool" src/ --include="*.py"           # MCP exposure
grep -r "llm\|gpt\|claude" src/ --include="*.py"   # LLM usage
grep -r "eval\|exec" src/ --include="*.py"         # Code execution risks
grep -r "template\|format" src/ --include="*.py"   # Injection vectors
```

**Output:** `Findings-HALL-YYYYMMDD.yaml`

### Agent 3: GOVERNANCE

**File:** `.github/agents/cortex-review-governance.md`

**Purpose:** Verify compliance with CORE governance rules

**Checks:**

```sql
-- CORE-008: Tests BEFORE implementation
SELECT COUNT(*) FROM audit_log 
WHERE operation = 'AC_TEST_WRITTEN_BEFORE_CODE'

-- CORE-011: Type hints (100%)
SELECT COUNT(*) FROM code_analysis 
WHERE has_type_hints = true

-- CORE-012: Docstrings (100% on public APIs)
SELECT COUNT(*) FROM code_analysis 
WHERE has_docstring = true

-- CORE-025: Hash chain integrity (0 violations)
SELECT COUNT(*) FROM audit_log 
WHERE previous_hash != prior_entry.entry_hash

-- CORE-027: Audit trail completeness
SELECT ac_id FROM audit_log 
WHERE ac_id NOT IN (
  SELECT DISTINCT ac_id FROM audit_log 
  WHERE operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
)
```

**Output:** `Findings-GOV-YYYYMMDD.yaml`

### Agent 4: ASSUMPTIONS

**File:** `.github/agents/cortex-review-assumptions.md`

**Purpose:** Identify hidden environment assumptions

**Checks:**
- Platform assumptions (macOS vs Linux vs Windows)
- Python version dependencies (3.9 vs 3.10 vs 3.11)
- External service availability (API endpoints, databases)
- File system permissions (requires write to specific directories)
- Network connectivity requirements
- Environment variables (required but not documented)
- Timezone and locale assumptions

**Evidence Sources:**
```bash
grep -r "platform\|sys.platform\|os.name" src/
grep -r "import sys" src/ | grep -i "platform"
cat requirements.txt | grep -E "=|version"
grep -r "getenv\|environ" src/
```

**Output:** `Findings-ASM-YYYYMMDD.yaml`

### Agent 5: DEBT

**File:** `.github/agents/cortex-review-debt.md`

**Purpose:** Identify technical debt and deferred decisions

**Checks:**
- Duplicated code patterns
- Deprecated patterns still in use
- Missing abstractions (same logic in 3+ places)
- Over-engineering (unnecessary complexity)
- Under-engineering (shortcuts taken for speed)
- Documentation gaps vs implementation
- Test gaps (integration tests missing)
- Performance issues (slow algorithms, N+1 queries)

**Evidence Sources:**
```bash
grep -r "duplicate\|same as\|copied from" src/
grep -r "deprecated\|legacy\|old" src/
wc -l src/**/*.py | sort -n | tail -20  # Large files
git log --oneline --all | grep "fix.*again" | wc -l  # Repeated fixes
```

**Output:** `Findings-DEBT-YYYYMMDD.yaml`

### Parallel Execution Command

```bash
# Run all 5 agents in parallel
/review agent --name brittleness &
/review agent --name hallucination &
/review agent --name governance &
/review agent --name assumptions &
/review agent --name debt &
wait

# Each produces: Findings-AGENT-YYYYMMDD.yaml
```

---

## PHASE 2: CONSOLIDATION (30 minutes)

### Consolidate All Findings

**Combine:** All 5 agent findings into single YAML report

```yaml
# File: _workspaces/roadmap/issues/REVIEW-FINDINGS-CONSOLIDATED-YYYYMMDD.yaml

metadata:
  review_date: "2026-01-18"
  phases_executed: "0, 1, 2"
  agents_run: 5
  evidence_quality: "A (95% confidence)"

findings:
  - finding_id: "F001"
    severity: "CRITICAL|HIGH|MEDIUM|LOW"
    evidence_grade: "A|B|C"
    agent: "brittleness|hallucination|governance|assumptions|debt"
    root_cause: "IMPLEMENTATION_FLAW|INTEGRATION_ISSUE|DESIGN_WEAKNESS"
    affected_files: ["file1.py", "file2.py"]
    ac_id_suggested: "AC-FIX-XXX-XX"
    remediation_effort: "2h|4h|1d|1w"
    description: "Clear description of issue"
    
governance_compliance:
  CORE-008: "PASS|FAIL"
  CORE-011: "PASS|FAIL"
  CORE-012: "PASS|FAIL"
  CORE-025: "PASS|FAIL"
  CORE-027: "PASS|FAIL"
  # ... etc

quality_metrics:
  production_readiness_score: "X/10"
  blocking_critical_findings: "N"
  high_priority_findings: "N"
  investigation_needed: "N"

recommendations:
  - "Fix AC1, AC2, AC3 before production deployment"
  - "Consider AC4, AC5 for next phase (nice-to-have)"
  - "Document assumption X for operations team"
```

### Classify Findings by Severity

```
CRITICAL (Blocks Deployment)
├─ Hash chain broken (audit trail compromised)
├─ Type hints missing (CORE-011 violation)
├─ Governance rule violation
├─ AI safety vulnerability
└─ SPOF without fallback

HIGH (Should Fix Before Deployment)
├─ Bare except clauses
├─ Uncovered code paths (< 85% coverage)
├─ Unvalidated LLM output
├─ Performance issues (N+1 queries)
└─ Environment assumptions not documented

MEDIUM (Fix in Next Phase)
├─ Code duplication
├─ Documentation gaps
├─ Deprecated patterns
└─ Technical debt accumulation

LOW (Nice-to-Have)
├─ Code style improvements
├─ Over-engineered components
├─ Non-critical optimizations
```

### Calculate Production Readiness Score

```
Score = (PASS rules × 10) / Total rules

0-3/10: NOT READY (fix CRITICAL findings)
4-6/10: MOSTLY READY (fix HIGH findings)
7-8/10: READY (document assumptions, plan MEDIUM)
9-10/10: PRODUCTION READY ✅
```

---

## PHASE 3: REMEDIATION INTEGRATION (Systematic Gap → Master Plan)

### ⚠️ CRITICAL: DEFAULT BEHAVIOR - ALWAYS INTEGRATE GAPS

**MANDATE:** Every review MUST produce gap identifications that are automatically integrated into `cortex-master.yaml` via cortex-builder.prompt.md. This is NOT optional.

**Default Workflow:**
```
Phase 2 Output: REVIEW-FINDINGS-CONSOLIDATED-YYYYMMDD.yaml
            ↓ (contains all findings with severity/evidence/remediation)
Phase 3: Automatic Gap Extraction
            ↓ (classify by type: implementation_flaw, integration_issue, design_weakness)
      Holistic Refactor Analysis
            ↓ (analyze interdependencies across findings)
      YAML Generation: gaps_addressed + ac_breakdown updates
            ↓ (structured for cortex-builder.prompt.md integration)
cortex-builder.prompt.md Integration
            ↓ (read phase_tracker, identify gaps section)
      Update cortex-master.yaml
            ↓ (ADD gaps_addressed + NEW AC-FIX ACs to phase)
COMPLETE: Phase status IN_PROGRESS, locked: false, ready for implementation
```

### Step 1: Extract Gaps from Consolidated Findings

**Input:** `REVIEW-FINDINGS-CONSOLIDATED-YYYYMMDD.yaml`

**Process:** For EACH finding with severity >= MEDIUM:

```yaml
# Map finding to gap entry format
gap_extraction:
  finding_id: "F001"
  severity: "CRITICAL"
  evidence_grade: "A"
  
  # Convert to gaps_addressed format
  gap_id: "GAP-HASH-CHAIN-001"  # Systematic ID: GAP-{DOMAIN}-{NNN}
  description: "Hash chain integrity - [specific issue from finding]"
  root_cause: "IMPLEMENTATION_FLAW|INTEGRATION_ISSUE|DESIGN_WEAKNESS"
  affected_ac_ids: ["AC-FIX-001-01", "AC-DECORATOR-001"]  # Which ACs have this issue
  
  # Remediation mapping
  remedy_ac_id: "AC-FIX-001-02"  # New AC to create for fix
  remedy_effort: "1h"
  remedy_priority: "P0 - CRITICAL"
  
  # Cross-dependencies
  blocking_for: ["AC-FIX-001-03", "test_hash_chain_integrity"]
  depends_on: ["AC-FIX-001-01"]
  
  # Governance
  related_skull_rules: ["CORE-025", "CORE-027", "CORE-008"]
  
  # Traceability
  issue_id: "ISSUE-005B"
  investigation_report: "_workspaces/roadmap/issues/REVIEW-INVESTIGATION-REPORT-20260118.yaml"
```

### Step 2: Holistic Refactoring Analysis

**Systematic Review Pattern:**

Before creating individual AC-FIX entries, analyze ALL gaps for:

#### A. Interdependencies
```yaml
dependency_matrix:
  # Do multiple gaps stem from single root cause?
  # Example: 5 gaps from single hash chain design defect
  - root_cause_cluster: "Hash Chain Design"
    gaps_affected: ["GAP-HASH-CHAIN-001", "GAP-HASH-VALIDATE-001"]
    single_fix_addresses: 2
    combined_effort: "1.75h"
    
  # Separate concerns (independent gaps need separate ACs)
  - root_cause_cluster: "Test Isolation"
    gaps_affected: ["GAP-TEST-FIXTURE-001"]
    single_fix_addresses: 1
    combined_effort: "45m"
```

#### B. Pattern Recognition
```yaml
pattern_analysis:
  # Brittle patterns appearing in multiple files?
  - pattern: "Bare except clauses"
    files_affected: 3
    potential_consolidation: "AC-REFACTOR-ERROR-HANDLING-001"
    
  # Missing abstractions?
  - pattern: "Duplicated logic in X locations"
    refactoring_opportunity: "AC-REFACTOR-ABSTRACTION-001"
```

#### C. Evidence-Based Decision Making
```yaml
evidence_based_decisions:
  # CRITICAL gaps (Grade A evidence) → P0 ACs, immediate remediation
  - gap: "GAP-HASH-CHAIN-001"
    evidence_grade: "A (95% confidence)"
    decision: "IMMEDIATE - Blocks test_hash_chain_integrity"
    priority: "P0 - CRITICAL"
    
  # HIGH gaps (Grade B evidence) → P1 ACs, prioritized
  - gap: "GAP-BARE-EXCEPT-001"
    evidence_grade: "B (85% confidence)"
    decision: "NEXT SPRINT - Production risk but not blocking"
    priority: "P1 - HIGH"
    
  # MEDIUM gaps (Grade B evidence) → P2 ACs, planned
  - gap: "GAP-CODE-DUPLICATION-001"
    evidence_grade: "B (80% confidence)"
    decision: "REFACTORING PHASE - Technical debt"
    priority: "P2 - MEDIUM"
```

### Step 3: Generate Structured YAML for cortex-builder Integration

**Output File:** `_workspaces/roadmap/issues/REVIEW-GAPS-EXTRACTED-YYYYMMDD.yaml`

```yaml
metadata:
  review_date: "2026-01-18"
  consolidated_findings_source: "REVIEW-FINDINGS-CONSOLIDATED-YYYYMMDD.yaml"
  total_findings: 15
  gaps_extracted: 8
  critical_gaps: 2
  high_gaps: 4
  medium_gaps: 2

gap_summary:
  total_affected_acs: 12
  total_new_acs_needed: 8
  combined_effort: "8.5 hours"
  blocking_status: "CRITICAL (2 gaps block test suite)"

gaps_addressed:
  - gap_id: "GAP-HASH-CHAIN-001"
    severity: "CRITICAL"
    evidence_grade: "A"
    description: "Hash chain integrity - previous_hash hardcoded to empty string"
    root_cause: "IMPLEMENTATION_FLAW in DatabaseTransactionManager._log_audit_entry()"
    affected_ac_ids: ["AC-FIX-001-01"]
    affected_tests: ["test_hash_chain_integrity"]
    
    remedy:
      ac_id: "AC-FIX-001-02"
      title: "Fix Hash Chain Calculation"
      description: "Replace hardcoded previous_hash with calculation from prior entry"
      effort: "1 hour"
      priority: "P0 - CRITICAL"
      blocking_for: ["AC-FIX-001-03", "PHASE-REMEDIATION-04"]
      depends_on: ["AC-FIX-001-01"]
      related_skull_rules: ["CORE-008", "CORE-011", "CORE-012", "CORE-025", "CORE-027"]
      issue_id: "ISSUE-005B"
    
    # Holistic refactoring context
    holistic_context:
      root_cause_cluster: "Hash Chain Architecture"
      cluster_gaps: ["GAP-HASH-CHAIN-001", "GAP-HASH-VALIDATE-001"]
      cluster_effort_total: "1.75 hours"
      cluster_priority: "CRITICAL PATH"
      cluster_blocking: "test_hash_chain_integrity cannot pass until both ACs complete"
  
  - gap_id: "GAP-HASH-VALIDATE-001"
    severity: "CRITICAL"
    evidence_grade: "A"
    description: "Hash chain validation gate missing - no validation before commit"
    root_cause: "DESIGN_WEAKNESS - missing validation layer after hash calculation"
    affected_ac_ids: []  # New gap from investigation
    affected_tests: ["test_hash_chain_integrity"]
    
    remedy:
      ac_id: "AC-FIX-001-03"
      title: "Add Hash Chain Validation Gate"
      description: "Add _validate_hash_chain() method, call before transaction commit"
      effort: "45 minutes"
      priority: "P0 - CRITICAL"
      blocking_for: ["clean_audit_log_regeneration", "PHASE-REMEDIATION-04"]
      depends_on: ["AC-FIX-001-02"]
      related_skull_rules: ["CORE-008", "CORE-011", "CORE-012", "CORE-025", "CORE-027"]
      issue_id: "ISSUE-005B"
    
    holistic_context:
      root_cause_cluster: "Hash Chain Architecture"
      cluster_gaps: ["GAP-HASH-CHAIN-001", "GAP-HASH-VALIDATE-001"]
      cluster_effort_total: "1.75 hours"
      cluster_priority: "CRITICAL PATH"
      cluster_blocking: "test_hash_chain_integrity cannot pass until both ACs complete"

# Additional gaps follow same pattern...

cortex_master_yaml_updates:
  # These updates MUST be applied by cortex-builder.prompt.md
  # See cortex-builder.prompt.md → "INTEGRATION PATTERN: Review Gaps → Master Plan"
  
  affected_phase: "PHASE-REMEDIATION-03"
  current_phase_status: "COMPLETED"  # Need to change to IN_PROGRESS
  
  phase_changes:
    title: "Add ISSUE-005B reference"
    status: "IN_PROGRESS"  # Was: COMPLETED
    locked: false  # Was: true
    ac_ids: "8 → 10"  # Adding AC-FIX-001-02 and AC-FIX-001-03
    completed_ac_ids: "8 (unchanged)"
    blocking: true  # Critical path
    
  gaps_addressed_section:
    # Add this new section with all gaps from this review
    gaps: "[see gaps_addressed array above]"
    
  ac_breakdown:
    critical_blockers: "2 → 4"  # Adding new blocker ACs
    
  metadata:
    review_investigation_date: "2026-01-18"
    review_investigation_report: "_workspaces/roadmap/issues/REVIEW-INVESTIGATION-REPORT-YYYYMMDD.yaml"
    decision_gate: "_workspaces/roadmap/issues/DECISION-GATE-YYYYMMDD.yaml"
```

### Step 4: Trigger cortex-builder Integration

**Command:** 
```bash
/cortex-builder integrate-gaps \
  --findings-file REVIEW-FINDINGS-CONSOLIDATED-YYYYMMDD.yaml \
  --gaps-file REVIEW-GAPS-EXTRACTED-YYYYMMDD.yaml \
  --master-plan cortex-master.yaml
```

**cortex-builder.prompt.md will:**
1. Read gaps_addressed from REVIEW-GAPS-EXTRACTED file
2. Identify affected phase in phase_tracker
3. Update phase status, ac_ids, gaps_addressed section
4. Add new AC-FIX entries with full specifications
5. Update ac_breakdown with new critical blockers
6. Add investigation references (dates, reports)
7. Set phase status to IN_PROGRESS and locked: false
8. Commit with: `git commit -m "integrate-review-gaps: ISSUE-XXX remediation ACs added"`

### If No Critical Findings

```yaml
decision: "READY FOR PRODUCTION DEPLOYMENT"
findings_summary: "No CRITICAL or blocking issues identified"
next_phase: "PHASE-NEXT (from cortex-master.yaml)"
production_readiness: "9/10 (all governance compliant)"
documentation_complete: true
assumptions_documented: true
```

---

## EVIDENCE GRADING SYSTEM

### Grade A: Direct Verification (95% Confidence)

**What Qualifies:**
- Code inspection (reading the actual code)
- SQL query results (direct database query)
- Test that fails/passes
- Compile error
- Type checker error (mypy)

**Example:**
```
Finding: "Bare except found"
Evidence: grep output + line number + file location
Grade: A (can see the code directly)
Confidence: 95%
```

### Grade B: Strong Inference (85% Confidence)

**What Qualifies:**
- Multiple related data points
- Pattern observed in multiple places
- Corroborating evidence from different sources
- High probability but not 100% certain

**Example:**
```
Finding: "No error handling in function X"
Evidence: Function reads file, doesn't wrap in try/except
         Similar functions in codebase do handle errors
         Test coverage shows 0% coverage for error paths
Grade: B (highly likely but not proven)
Confidence: 85%
```

### Grade C: Speculation (70% Confidence)

**NOT ALLOWED FOR CRITICAL FINDINGS**

**What Qualifies:**
- Assumption-based inference
- "Seems like" reasoning
- Single data point
- Unverified suspicion

**Example:**
```
Finding: "This code might have a memory leak"
Evidence: "It looks fragile, similar code elsewhere had memory leak"
Grade: C (speculation without proof)
Confidence: 70%

ACTION: Either upgrade to A/B with evidence, or DON'T report
```

**Rule:** CRITICAL findings MUST be Grade A or B. No C-grade critical findings allowed.

---

## COMPLETE WORKFLOW EXAMPLE

### Scenario: Review PHASE-20 Implementation

```bash
# Phase 0: Pre-validation (15 min)
/review gate 0a  # Freshness check → PASS ✅
/review gate 0b  # Audit trail check → PASS ✅
/review gate 0c  # Hash chain check → FAIL ❌
/review gate 0d  # Test isolation check → PASS ✅

# Phase 0 Decision: Gate 0C failed → Go to Phase 0.5
→ PROCEED TO PHASE 0.5

# Phase 0.5: Surgical Investigation (40 min)
/review surgical --ac-id AC-FIX-001-01
# Identifies: 74 violations from hardcoded previous_hash = ""
# Classifies: IMPLEMENTATION_FLAW
# Creates: REVIEW-INVESTIGATION-REPORT-20260118.yaml
# Decision: Create AC-FIX-001-02 and AC-FIX-001-03

# Remediation (2 hours)
/implement AC-FIX-001-02  # Fix hash calculation (1 hour)
/implement AC-FIX-001-03  # Add validation (45 min)
# Clean regenerate audit log (5 min)
# Verify: test_hash_chain_integrity → PASS ✅

# Phase 1: Agent Analysis (48 min)
/review agent --name brittleness &
/review agent --name hallucination &
/review agent --name governance &
/review agent --name assumptions &
/review agent --name debt &
wait
# Produces: 5 × Findings-AGENT-*.yaml

# Phase 2: Consolidation (10 min)
/review consolidate
# Produces: REVIEW-FINDINGS-CONSOLIDATED-20260118.yaml

# Phase 3: Handoff (5 min)
/review remediation
# Produces: phase-remediation-NNN.yaml with any new AC-FIX findings
# If none: Ready for production ✅

TOTAL TIME: 4.5 hours (vs 6-8 hours blind regen approach)
BLOCKERS BEFORE PHASE 1: 0 (AC-FIX remediation complete)
PRODUCTION READINESS: 95% (governance compliant)
```

### Phase 3 Continuation: Gap Extraction & Integration (NEW - 2026-01-18)

```bash
# After Phase 2 consolidation:
/review consolidate
# Output: REVIEW-FINDINGS-CONSOLIDATED-20260118.yaml

# Phase 3A: Extract gaps from consolidated findings
/review extract-gaps --findings REVIEW-FINDINGS-CONSOLIDATED-20260118.yaml
# Output: REVIEW-GAPS-EXTRACTED-20260118.yaml
# Time: ~10 min

# Phase 3B: Holistic refactoring analysis
/review refactor-holistic --gaps REVIEW-GAPS-EXTRACTED-20260118.yaml
# Updates REVIEW-GAPS-EXTRACTED-20260118.yaml with:
#   - Holistic context for each gap
#   - Root cause clustering analysis
#   - Pattern recognition recommendations
#   - Dependency optimization suggestions
# Time: ~5 min

# Phase 3C: Generate structured YAML for cortex-builder
/review remediation --gaps REVIEW-GAPS-EXTRACTED-20260118.yaml --master cortex-master.yaml
# Validates gaps are ready for integration
# Generates cortex_master_yaml_updates section
# Time: ~5 min

# AUTOMATIC (cortex-builder integration)
# cortex-builder.prompt.md detects REVIEW-GAPS-EXTRACTED file and:
#   1. Reads gap entries from REVIEW-GAPS-EXTRACTED-20260118.yaml
#   2. Updates cortex-master.yaml phase_tracker
#   3. Adds gaps_addressed section with evidence metadata
#   4. Creates new AC-FIX entries with full specifications
#   5. Updates ac_breakdown with new critical blockers
#   6. Adds investigation references (dates, reports)
#   7. Commits with traceable message

TOTAL TIME (Phase 3): 20 min (gap extraction + analysis + yaml generation)
INTEGRATION TIME: Automatic (cortex-builder triggered)
RESULT: cortex-master.yaml updated, phase ready for implementation
```

---

## SYSTEMATIC GAP IDENTIFICATION & REMEDIATION (Default Workflow)

### Purpose

**MANDATE:** Every review AUTOMATICALLY produces:
1. REVIEW-FINDINGS-CONSOLIDATED (Phase 2 output)
2. REVIEW-GAPS-EXTRACTED (Phase 3A output) ← NEW
3. cortex_master_yaml_updates section (Phase 3B/3C output) ← NEW
4. Integration into cortex-master.yaml (cortex-builder.prompt.md) ← AUTOMATIC

**Outcome:** Zero manual gap management. Systematic, traceable, actionable.

### Key Principles

**1. Holistic Analysis Before AC Creation**
```
Instead of: Finding detected → Create AC immediately
Principle:  Analyze all findings → Cluster by root cause → Create minimal AC set
Result:     78 violations from 1 defect = 2 ACs (fix + validation), not 78 ACs
```

**2. Evidence-Based Prioritization**
```
Grade A (95% confidence) → P0 - CRITICAL → Implement immediately
Grade B (85% confidence) → P1 - HIGH → Next sprint
Grade C (70% confidence) → P2 - MEDIUM → Backlog (NOT for critical findings)
```

**3. Systematic Root Cause Classification**
```
IMPLEMENTATION_FLAW  → Code bug, usually fixable in 1-2 ACs
INTEGRATION_ISSUE    → Component mismatch, may need refactoring
DESIGN_WEAKNESS      → Architectural issue, often needs multiple ACs
```

**4. Automatic Integration into Master Plan**
```
Review findings → Extract gaps → cortex-builder reads files → Master plan updated
No manual "add to roadmap" needed - it's automatic on file detection
```

### Gap Extraction Algorithm (Phase 3A)

```yaml
for each finding in REVIEW-FINDINGS-CONSOLIDATED:
  if finding.severity >= MEDIUM AND finding.evidence_grade in ["A", "B"]:
    # Extract gap entry
    gap_id = "GAP-" + finding.domain.upper() + "-" + counter
    
    # Map to remedy AC
    remedy_ac_id = "AC-FIX-" + ac_domain + "-" + counter
    remedy_effort = estimate_from_root_cause(finding.root_cause)
    remedy_priority = map_evidence_to_priority(finding.evidence_grade)
    
    # Identify dependencies
    blocking_for = identify_blocked_tests_and_acs(finding)
    depends_on = identify_prerequisite_acs(finding)
    
    # Add to gaps_addressed
    gaps_addressed.append({
      gap_id, severity, evidence_grade, description,
      remedy_ac_id, remedy_effort, remedy_priority,
      blocking_for, depends_on, related_skull_rules,
      issue_id, investigation_report
    })
```

### Holistic Refactoring Analysis (Phase 3B)

For all gaps extracted, systematically analyze:

```yaml
holistic_analysis:

  # 1. Root Cause Clustering
  root_cause_clusters:
    - cluster_name: "Hash Chain Architecture"
      cluster_gaps: ["GAP-HASH-CHAIN-001", "GAP-HASH-VALIDATE-001"]
      cluster_root_cause: "Design defect in DatabaseTransactionManager"
      cluster_effort_total: "1.75 hours"
      cluster_priority: "CRITICAL PATH"
      cluster_ac_count: 2
      single_root_cause_benefit: "Fixes 2 gaps with unified approach"
      
      action: "Keep both ACs - they're sequential (fix then validate)"
  
  # 2. Pattern Recognition
  pattern_analysis:
    - pattern: "Bare except clauses"
      occurrences: 5
      files_affected: ["src/file1.py", "src/file2.py", "src/file3.py"]
      consolidation_opportunity: "AC-REFACTOR-ERROR-HANDLING-001"
      effort: "2 hours"
      priority: "P1 - HIGH"
      
      recommendation: "Single refactoring AC instead of 5 separate fixes"
      action: "Create AC-REFACTOR-ERROR-HANDLING-001 with 5 locations"
  
  # 3. Dependency Optimization
  dependency_graph:
    - node: "AC-FIX-001-02"
      depends_on: ["AC-FIX-001-01"]
      blocking_for: ["AC-FIX-001-03"]
      can_parallelize_with: []
      
      analysis: "Sequential - AC-FIX-001-02 must complete before AC-FIX-001-03"
      optimization: "No parallelization possible"
    
    - node: "AC-REFACTOR-ERROR-HANDLING-001"
      depends_on: []
      blocking_for: []
      can_parallelize_with: ["AC-FIX-001-02", "AC-FIX-001-03"]
      
      analysis: "Independent - can be done in parallel with hash chain fixes"
      optimization: "Recommend parallel execution for faster delivery"
  
  # 4. Evidence Grading Summary
  evidence_distribution:
    grade_a: 2  # 95% confidence
    grade_b: 4  # 85% confidence
    grade_c: 0  # 70% confidence (NOT allowed for critical)
    
    by_severity:
      critical: {a: 2, b: 0, c: 0}
      high: {a: 0, b: 4, c: 0}
      medium: {a: 0, b: 0, c: 0}
    
    analysis: "All critical findings have Grade A evidence ✅"
    compliance: "APPROVED for remediation"

  # 5. AC Deduplication Check
  ac_deduplication:
    - potential_duplicate: "AC-REFACTOR-ERROR-HANDLING-001"
      consolidates_gaps: 5
      separate_ac_count_avoided: 5
      effort_saved: "~1 hour"
      
      recommendation: "Consolidate 5 error handling gaps into 1 AC"
      action: "Create unified AC instead of 5 separate ACs"
  
  # 6. Governance Coverage
  governance_coverage:
    rules_referenced: ["CORE-008", "CORE-011", "CORE-012", "CORE-025", "CORE-027", "CORE-028"]
    rules_covered_by_remediation_acs: ["CORE-008", "CORE-011", "CORE-012", "CORE-025", "CORE-027"]
    rules_not_addressed: []
    
    coverage: "100% of relevant governance rules"
    compliance: "All ACs include governance rules in specifications"
```

### Integration Validation (Before cortex-builder commits)

```bash
# Run these checks in cortex-builder BEFORE committing gap integration

# 1. Syntax validation
yamllint cortex-master.yaml

# 2. Gap-to-AC mapping validation
python3 << 'EOF'
import yaml
with open('cortex-master.yaml') as f:
  master = yaml.safe_load(f)

for phase in master['phase_tracker'].values():
  if 'gaps_addressed' in phase:
    for gap in phase['gaps_addressed']:
      # Verify remedy AC exists in phase
      remedy_id = gap['remedy_ac_id']
      ac_snake = remedy_id.lower().replace('-', '_')
      if ac_snake not in phase:
        print(f"ERROR: {remedy_id} referenced in gaps but AC spec missing")
      else:
        print(f"✅ {remedy_id} found and specified")
EOF

# 3. Dependency cycle detection
python3 << 'EOF'
# Check for circular dependencies in blocking_for / depends_on
# If AC-X depends_on AC-Y and AC-Y blocking_for AC-X → CYCLE ERROR
EOF

# 4. Governance rule verification
for phase in cortex-master.yaml:
  for ac in phase.ac_ids:
    for rule in ac.governance_rules:
      if rule not in cortex_brain/tier0/governance/core-rules.yaml:
        echo "ERROR: Unknown rule $rule in $ac"

# 5. Evidence grading check
for gap in gaps_addressed:
  if gap.severity == "CRITICAL" AND gap.evidence_grade not in ["A", "B"]:
    echo "ERROR: CRITICAL gap must have A or B evidence grade"
```

---

## COMMANDS REFERENCE

### Full Review (All Phases)

```bash
# Complete review: Phase 0 → 0.5 (if needed) → 1 → 2 → 3
/review full

# With options
/review full --skip-phase-0         # Skip data validation (safe if verified)
/review full --investigation-only   # Phase 0.5 only (for troubleshooting)
```

### Individual Phases

```bash
/review phase 0                          # Data validation gates
/review phase 0.5 --ac-id AC-FIX-001-01 # Surgical investigation
/review agent --name brittleness         # Single agent
/review consolidate                      # Phase 2 consolidation
/review extract-gaps                     # Phase 3A: Extract gaps from consolidation
/review refactor-holistic                # Phase 3B: Holistic refactoring analysis
/review remediation                      # Phase 3C: Generate YAML for integration
```

### Investigation Tools

```bash
/review surgical                    # Start Phase 0.5 investigation
/review classify --ac-id AC-XXX-XX  # Classify defect type (Q1-Q6)
/review evidence --grade A          # Show A-grade evidence only
/review report --investigation      # Show investigation report
```

### Remediation

```bash
/review remediation --blocking      # Show CRITICAL findings only
/review remediation --create-phase  # Create phase-remediation-NNN.yaml
/review metrics                     # Show production readiness score
```

---

## TROUBLESHOOTING

### Problem: Phase 0 Gate Fails

**Gate 0A (Freshness):**
```
Error: Data > 24 hours old
Fix: Delete governance.db, run tests to regenerate
```

**Gate 0B (Audit Trail):**
```
Error: < 2000 audit entries
Fix: Audit logger not working, check src/infrastructure/audit_logger.py
```

**Gate 0C (Hash Chain):**
```
Error: test_hash_chain_integrity FAILS
Fix: Go to Phase 0.5 (Surgical Investigation)
     Don't regenerate yet - need to find root cause first
```

**Gate 0D (Test Isolation):**
```
Error: > 6 test fixtures found
Fix: Update TEST_FIXTURES list in test_audit_trail_integrity.py
     Add newly discovered test ACs
```

### Problem: Phase 0.5 Investigation Stuck

**Can't classify defect:**
```
Action: Run queries manually (see Phase 0.5 step 1)
        Review code manually (see Phase 0.5 step 2)
        Create evidence YAML with findings
        Escalate for manual decision
```

**Defect type unclear:**
```
Decision Tree: Work through Q1-Q6 systematically
               Document each answer with evidence
               Classification will become clear
```

### Problem: Phase 1 Agent Fails

**Agent hangs or times out:**
```
Check: Is test data contaminated? (Gate 0D check)
       Is there a SPOF blocking analysis? (Gate 0C check)
       Is database connection valid?
Action: Re-run Phase 0, verify all gates pass
```

---

## SUCCESS CRITERIA

### Phase 0: Complete
- [ ] All 4 gates checked
- [ ] Decision made (Phase 1 or Phase 0.5)
- [ ] No data quality issues

### Phase 0.5: Complete (if needed)
- [ ] Defect type classified
- [ ] Root cause identified (A/B grade evidence)
- [ ] AC-FIX-XXX-XX suggested or test filters updated
- [ ] Investigation report created

### Phase 1: Complete
- [ ] 5 agents executed successfully
- [ ] Each agent produces Findings-AGENT-*.yaml
- [ ] All evidence graded (A/B/C)
- [ ] No critical blockers found (or AC-FIX planned)

### Phase 2: Complete
- [ ] All agent findings consolidated
- [ ] CRITICAL vs HIGH vs MEDIUM vs LOW classified
- [ ] Production readiness score calculated
- [ ] Governance compliance verified

### Phase 3: Complete
- [ ] If findings exist: phase-remediation-NNN.yaml created
- [ ] If no findings: "Ready for production" documented
- [ ] Next phase known and documented

---

## KEY PRINCIPLES

1. **Don't Blindly Regenerate:** Always investigate root cause first (Phase 0.5)
2. **Grade Your Evidence:** No speculation for critical findings (A/B only)
3. **Validate Assumptions:** Check all assumptions explicitly in gates
4. **Parallel Where Possible:** Agents run parallel, saves time
5. **Preserve Evidence:** Keep all YAML reports for audit trail
6. **Classify Defects:** IMPLEMENTATION_FLAW vs TEST_ARTIFACT vs TIMING_ISSUE (very different fixes)
7. **Use Decision Trees:** Systematic classification prevents false positives
8. **Root Cause Analysis:** Understand WHY before fixing
9. **Governance First:** All CORE rules before production deployment
10. **Actionable Findings:** Every finding has clear remediation path

---

## COMPANION DOCUMENTS

**Read Together With:**
- `CORTEX-INTEGRATED-SYSTEM-v3.md` — Complete toolkit (planner, builder, agents)
- `docs/cortex-builder.md` — Implementation guidance with TDD pattern
- `TRANSITION-INVESTIGATION-TO-IMPLEMENTATION.md` — Step-by-step AC-FIX guide
- `TOOLKIT-INDEX-20260118.md` — File locations and quick reference

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | Earlier | Initial review system |
| v2.0 | Chat01 | Added data validation gates, evidence grading |
| v3.0 | 2026-01-18 | Surgical investigation, parallel agents, design-build gap detection |

**Current Version:** 3.0 ✅ PRODUCTION READY

---

## NEXT STEP

**Ready to begin review?**

```bash
/review full
```

**Or, if investigating a specific issue:**

```bash
/review phase 0.5 --ac-id AC-FIX-001-01
```

**Questions about the protocol?** → See companion documents above.

---

**Status:** UNIFIED & READY ✅  
**Efficiency:** 4.5 hours (investigation + fix + review + delivery)  
**Confidence:** A-grade evidence (95%+)  
**Last Updated:** 2026-01-18

---

## 📚 Related Prompts

**Specialized Review Prompts (in `review/` subfolder):**
- `review/cortex-review-assumptions.prompt.md` - Detect platform/environment assumptions
- `review/cortex-review-brittleness.prompt.md` - Identify fragile error handling & state management
- `review/cortex-review-debt.prompt.md` - Find TODOs, skipped tests, type stubs, duplication
- `review/cortex-review-hallucination.prompt.md` - Verify claims and detect contradictions

**Building & Implementation:**
- `cortex-builder.prompt.md` - AC-ID implementation with TDD & governance
- `builder/cortex-builder-continuation.prompt.md` - Resume sessions without context dumps

**Planning & Tools:**
- `planning/cortex-planner.prompt.md` - Phase readiness & next steps
- `planning/cortex-governance.prompt.md` - Compliance verification
- `utilities/cortex-gap-detection.prompt.md` - Design-build gap analysis

**System & Reference:**
- `CORTEX.prompt.md` - Master Orchestrator & Intent Router
- `cortex-git-commit.prompt.md` - Multi-machine development protocol
