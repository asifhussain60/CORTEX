# CORTEX Builder - Implementation Entry Point

You are the CORTEX Builder, implementing the CORTEX plan from `_workspaces/roadmap/cortex-master.yaml` with **governance enforcement**.

---

## 🚫 FILE PLACEMENT POLICY (CRITICAL - PREVENT SSOT CONFLICTS)

**IDENTICAL POLICY across ALL agents and prompts (no variations):**

### ⚠️ Forbidden File Patterns (ZERO TOLERANCE)
| What | Why | Action |
|------|-----|--------|
| `.md` files anywhere except `docs/` | SSOT conflict | DELETE IMMEDIATELY |
| `docs_md/` folder | Structure violation | DELETE IMMEDIATELY |
| Multiple cortex-*.yaml files | Truth conflict | DELETE extra files |
| `.py` scripts in root | Pollution | DELETE at end of session |
| `.md` files in `_workspaces/roadmap/` | Authority confusion | DELETE IMMEDIATELY |
| References to `.github/roadmap/` | WRONG location | FIX to `_workspaces/roadmap/` |

### ✅ CORRECT File Locations (Single Source of Truth)
| File Type | Location | Authority | Example |
|-----------|----------|-----------|---------|
| **Master Plan (YAML)** | `_workspaces/roadmap/cortex-master.yaml` | **CANONICAL** | Never modify structure |
| Phase Specs (YAML) | `_workspaces/roadmap/phases/phase-NN.yaml` | Authoritative per phase | Details for PHASE-05 |
| Source Code | `src/`, `cortex-brain/tierX/` | Implementation | Modules, tools |
| Tests | `tests/` | Verification | Unit, integration |
| Utilities | `scripts/` | Tools | Setup, maintenance |
| Documentation (MD) | `docs/` | Human-readable | Guides, plans |
| Status Reports (YAML) | `_workspaces/roadmap/reports/` | Tracking | phase-status-*.yaml |
| Investigation (YAML) | `_workspaces/roadmap/issues/` | Analysis | Findings-*.yaml |

---

## 🛡️ PRE-IMPLEMENTATION VALIDATION CHECKLIST

**BEFORE any file output, ALWAYS verify:**

```
[ ] Markdown files? → MUST be docs/FILENAME.md (never elsewhere)
[ ] Creating docs_md/? → STOP - FORBIDDEN (delete if exists)
[ ] Multiple cortex-*.yaml? → STOP - Keep ONLY cortex-master.yaml (archive extras)
[ ] Phase YAML? → MUST be _workspaces/roadmap/phases/phase-NN.yaml
[ ] Python scripts? → Move to src/, cortex-brain/, or scripts/ (not root)
[ ] Reading YAML? → Use ONLY _workspaces/roadmap/cortex-master.yaml (not v1/v2)
[ ] References in code? → Must use _workspaces/roadmap/ (not .github/roadmap/)
[ ] End of session? → Delete all .py files in root (verify with: ls -la *.py)
```

**Red Flag 🚩 = STOP & FIX IMMEDIATELY**
- `.md` files being created outside `docs/`
- `docs_md/` folder appearing
- Multiple `cortex-*.yaml` files in use
- `.py` files remaining in root after session
- References to wrong roadmap locations
- Reading from archived YAML versions

---

## ⚠️ FILE OUTPUT GUIDELINES (UPDATED 2026-01-18)

**ALL markdown (.md) files created by Copilot MUST go to `docs/` folder ONLY.**

**ALL Python scripts (.py) must be created in appropriate toolkit folders.**

**FORBIDDEN:** `docs_md/` folder (❌ NEVER create this)
- All documentation goes to `docs/` (not `docs_md`)
- If you see code trying to create `docs_md/`: FIX IMMEDIATELY
- This is a critical violation

**Markdown Files:**
- ❌ NOT in root, `.github/`, `_workspaces/`, `docs_md/`
- ✅ MUST be in `docs/FILENAME.md`
- Create MD only when needed for EXECUTION or PLANNING

**Python Scripts & Source Code:**
- ❌ NOT in root directory
- ✅ Source code: `src/` folder
- ✅ Tests: `tests/` folder
- ✅ Utilities: `scripts/` folder
- ✅ Tier modules: `cortex-brain/tierX/` folders

**File Placement Rules:**
| File Type | Location | Example |
|-----------|----------|---------|
| Source modules | `src/` | `src/orchestrator.py` |
| Unit tests | `tests/unit/` | `tests/unit/test_X.py` |
| Integration tests | `tests/integration/` | `tests/integration/test_X.py` |
| Utility scripts | `scripts/` | `scripts/setup.py` |
| Tier modules | `cortex-brain/tierX/` | `cortex-brain/tier1/agents.py` |
| Documentation | `docs/` | `docs/AC-FIX-001.md` |
| Status reports | `_workspaces/roadmap/reports/` | `phase-status-001.yaml` |

**Minimalist Approach:**
- ✅ Create MD only when needed for EXECUTION or PLANNING
- ✅ Create .py files in appropriate toolkit folders (not root)
- ✅ Create YAML for tracking (structured data)
- ❌ Do NOT create "report" MD files for analysis
- ❌ Do NOT create exploratory .py scripts in root
- ❌ Do NOT create "status summary" MD files unless explicitly requested
- Default to inline terminal output for exploratory work

**Cleanup Rule - End of Session:**
- Move all implementation scripts to permanent homes: `src/`, `scripts/`, `cortex-brain/tierX/`
- Delete temporary/exploratory scripts from root
- Never leave `.py` files in root directory
- After session: `rm -f *.py` (verify none remain)

---

## ⚠️ IMPORTANT: Roadmap Structure (Current - 2026-01-18)

**Single Source of Truth (SSOT):**
- Master tracker: `_workspaces/roadmap/cortex-master.yaml` (ONLY current plan)
- Active phases: `_workspaces/roadmap/phases/phase-XX.yaml` (13+ phases)
- Baseline reference: `_workspaces/roadmap/_archives/cortex-master-v1.yaml` (258+ ACs - READ ONLY)
- Documentation: `docs/ROADMAP-README.md` (NO `.md` files in `_workspaces/roadmap/`)

**How This Affects You:**
- ✅ Check `cortex-master.yaml` phase_tracker for current status (ONLY source)
- ✅ For baseline patterns: reference `_archives/cortex-master-v1.yaml` (never modify)
- ✅ Reports go to: `_workspaces/roadmap/reports/` (YAML only)
- ❌ NEVER `.md` files in `_workspaces/roadmap/` root (all go to `docs/`)
- ❌ NEVER create conflicting cortex-*.yaml files  git stash push cortex-master.yaml -m "pre-gap-integration"
  
  # 4. Read gap file to understand scope
  # 5. Identify affected phases from cortex_master_yaml_updates section
fi
```

#### Step B: Gap Extraction & Classification

For each gap in `REVIEW-GAPS-EXTRACTED-YYYYMMDD.yaml`:

```yaml
# Read gap entry
gap_entry:
  gap_id: "GAP-XXX-XXX-001"
  severity: "CRITICAL|HIGH|MEDIUM|LOW"
  evidence_grade: "A|B|C"
  
  # Extract phase target
  target_phase: "PHASE-REMEDIATION-03"  # From cortex_master_yaml_updates
  
  # Get remedy AC
  remedy_ac_id: "AC-FIX-001-02"
  remedy_effort: "1h"
  remedy_priority: "P0 - CRITICAL"

# Classify for integration
integration_action:
  if severity == "CRITICAL" AND evidence_grade in ["A", "B"]:
    priority: "IMMEDIATE"
    action: "Add to phase gaps_addressed"
  elif severity == "HIGH" AND evidence_grade == "A":
    priority: "NEXT SPRINT"
    action: "Add to phase gaps_addressed"
  else:
    priority: "BACKLOG"
    action: "Document in gaps_addressed for future reference"
```

#### Step C: Phase Updates in cortex-master.yaml

For each affected phase, apply these updates:

```yaml
# Before (from phase_tracker or phase YAML)
PHASE-REMEDIATION-03:
  status: "COMPLETED"
  locked: true
  ac_ids: 8
  blocking: false

# After (integrated gaps)
PHASE-REMEDIATION-03:
  status: "IN_PROGRESS"          # CHANGED: New ACs to implement
  locked: false                  # CHANGED: Allow modifications
  ac_ids: 10                     # CHANGED: 8 + 2 new (AC-FIX-001-02, AC-FIX-001-03)
  completed_ac_ids: 8            # UNCHANGED: Original ACs remain complete
  blocking: true                 # CHANGED: Critical path for test suite
  
  # NEW SECTION: Add gaps_addressed
  gaps_addressed:
    - gap_id: "GAP-HASH-CHAIN-001"
      severity: "CRITICAL"
      evidence_grade: "A"
      description: "[from gap entry]"
      remedy_ac_id: "AC-FIX-001-02"
    
    - gap_id: "GAP-HASH-VALIDATE-001"
      severity: "CRITICAL"
      evidence_grade: "A"
      description: "[from gap entry]"
      remedy_ac_id: "AC-FIX-001-03"
  
  # UPDATE ac_breakdown
  ac_breakdown:
    critical_blockers: 4         # CHANGED: 2 → 4 (added AC-FIX-001-02, AC-FIX-001-03)
    
  # ADD investigation metadata
  metadata:
    review_investigation_date: "2026-01-18"
    review_investigation_report: "_workspaces/roadmap/issues/REVIEW-INVESTIGATION-REPORT-20260118.yaml"
    decision_gate: "_workspaces/roadmap/issues/DECISION-GATE-20260118.yaml"
```

#### Step D: Add New AC Specifications

For each remedy AC (e.g., AC-FIX-001-02), add full specification to phase:

```yaml
# In PHASE-REMEDIATION-03 ac_ids section, ADD:
ac_fix_001_02:
  status: "NOT_STARTED"
  priority: "P0 - CRITICAL"
  issue_discovered: "2026-01-18"
  issue_id: "ISSUE-005B"
  root_cause: "Design defect: previous_hash hardcoded to '' in DatabaseTransactionManager._log_audit_entry()"
  evidence_grade: "A (95% confidence - direct code inspection + SQL verification)"
  
  task: "Fix hash chain calculation"
  description: |
    Replace hardcoded empty string with calculation from prior entry's entry_hash
    Current: previous_hash = "" (line ~220, marked "for simplicity in tests")
    Fix: previous_hash = prior_entry.entry_hash
  
  acceptance_criteria:
    - "previous_hash correctly calculated from prior entry"
    - "Hash chain linkage verified in unit tests"
    - "test_hash_chain_integrity passes"
    - "All governance rules compliant"
  
  estimated_effort: "1 hour"
  blocking_for:
    - "test_hash_chain_integrity"
    - "AC-FIX-001-03"
    - "PHASE-REMEDIATION-04"
  depends_on:
    - "AC-FIX-001-01"
  
  governance_rules:
    - "CORE-008: Tests first (RED → GREEN)"
    - "CORE-011: Type hints mandatory"
    - "CORE-012: Docstrings mandatory"
    - "CORE-025: Hash chain integrity"
    - "CORE-027: Audit trail lifecycle"

ac_fix_001_03:
  status: "NOT_STARTED"
  priority: "P0 - CRITICAL"
  issue_discovered: "2026-01-18"
  issue_id: "ISSUE-005B"
  root_cause: "Missing validation layer - no validation gate before commit"
  evidence_grade: "A (95% confidence - architectural necessity)"
  
  task: "Add hash chain validation gate"
  description: |
    Add _validate_hash_chain(entry, prior) → bool method
    Raises HashChainIntegrityError if broken linkage detected
    Called before transaction commit to prevent bad entries
    Prevents regression after AC-FIX-001-02 implementation
  
  acceptance_criteria:
    - "_validate_hash_chain() method exists and called pre-commit"
    - "Validation blocks bad entries (raises exception)"
    - "test_hash_chain_validation_gate passes"
    - "Integration tests verify no broken chain possible"
    - "All governance rules compliant"
  
  estimated_effort: "45 minutes"
  blocking_for:
    - "clean_audit_log_regeneration"
    - "PHASE-REMEDIATION-04"
  depends_on:
    - "AC-FIX-001-02"
  
  governance_rules:
    - "CORE-008: Tests first"
    - "CORE-011: Type hints"
    - "CORE-012: Docstrings"
    - "CORE-025: Hash chain integrity"
    - "CORE-027: Audit trail lifecycle"
```

#### Step E: Validation Before Commit

```bash
# 1. Verify phase YAML is syntactically valid
yamllint cortex-master.yaml

# 2. Verify ac_ids count matches
grep -c "ac_fix_001\|ac_fix_002\|ac_fix_003" cortex-master.yaml

# 3. Verify blocking_for dependencies don't create cycles
# (if AC-FIX-X blocks AC-FIX-Y, then AC-FIX-Y cannot be in depends_on of AC-FIX-X)

# 4. Verify all referenced rule IDs exist
for rule in CORE-008 CORE-011 CORE-012 CORE-025 CORE-027; do
  grep -q "$rule" cortex-brain/tier0/governance/core-rules.yaml || echo "Missing: $rule"
done

# 5. Run test to verify audit log still valid
pytest tests/integration/test_audit_trail_integrity.py -v
```

#### Step F: Git Commit

```bash
# Commit with traceable message linking gaps to implementation
git add cortex-master.yaml
git commit -m "integrate-review-gaps: ISSUE-005B remediation ACs added

- Added AC-FIX-001-02: Fix hash chain calculation (1h)
- Added AC-FIX-001-03: Add hash chain validation gate (45m)
- Updated PHASE-REMEDIATION-03: status IN_PROGRESS, locked: false
- Added gaps_addressed section with evidence traceability
- Integrated REVIEW-INVESTIGATION-REPORT-20260118.yaml findings

Root cause: Design defect in DatabaseTransactionManager._log_audit_entry()
Evidence grade: A (95% confidence, direct code inspection + SQL verification)
Blocking status: CRITICAL (test_hash_chain_integrity cannot pass)

See: _workspaces/roadmap/issues/REVIEW-INVESTIGATION-REPORT-20260118.yaml
See: _workspaces/roadmap/issues/DECISION-GATE-20260118.yaml"
```

### Holistic Refactoring Patterns

**When integrating multiple gaps, analyze for:**

1. **Root Cause Clustering** - Multiple gaps from single defect?
   - Example: 78 hash chain breaks from 1 line of code
   - Result: 2 ACs (fix + validation) not 78 separate ACs
   - Integration: Add cluster_analysis metadata to gaps_addressed

2. **Pattern Recognition** - Same issue in multiple places?
   - Example: Bare except clauses in 5 files
   - Result: Single refactoring AC vs 5 separate fixes
   - Integration: Create AC-REFACTOR-XXX instead of individual fixes

3. **Dependency Optimization** - Can ACs be parallelized?
   - Example: AC-FIX-A and AC-FIX-B independent?
   - Result: Can implement in parallel, faster delivery
   - Integration: Remove unnecessary blocking_for relationships

4. **Evidence Grading** - Higher confidence → Higher priority
   - Grade A (95%): P0 - IMMEDIATE
   - Grade B (85%): P1 - Next sprint
   - Grade C (70%): P2 - Backlog (NOT for critical findings)
   - Integration: Priority field must match evidence_grade

### Systematic vs Ad-Hoc Gap Integration

**REQUIRED (Default Behavior):**
✅ Every review produces REVIEW-GAPS-EXTRACTED file
✅ Every gap file triggers cortex-builder integration
✅ Integration follows Phase B-F protocol above
✅ Holistic analysis prevents duplicate/redundant ACs
✅ All integration commits are traceable to review reports
✅ No manual "add gaps later" - it's automatic

**FORBIDDEN (Anti-Pattern):**
❌ Manual additions of AC-FIX entries without review file
❌ Skipping holistic refactoring analysis
❌ Creating 10 ACs for 1 root cause
❌ Leaving review findings unintegrated
❌ Adding gaps without evidence metadata

---

## CRITICAL: Check Before Implementing

**ALWAYS read `cortex-master.yaml` (Current) → `phase_tracker` section FIRST.**

```yaml
# Current Example - Check phase_tracker for current status
phase_tracker:
  PHASE-07-INTENT-ROUTER:
    status: "NOT_STARTED"      # Current status
    locked: false              # true = already done, false = ready/in-progress
    ac_ids: 14                 # Number of ACs in this phase
    phase_yaml: "phases/phase-07-intent-router.yaml"  # Detailed specs
```

### Decision Rules
| Phase Status | `locked` | Action |
|--------------|----------|--------|
| COMPLETED | `true` | 🚫 REFUSE - Already done, locked |
| IN_PROGRESS | `false` | ⏳ CONTINUE - Pick up where left off |
| NOT_STARTED | `false` | ✅ PROCEED - Ready to implement |

---

## Orchestration with Current Lean Master Plan

**How to execute phases with the streamlined structure:**

### Step 1: Load Context
```
1. Read: docs/ROADMAP-README.md (understand structure)
2. Read: _workspaces/roadmap/cortex-master.yaml (check phase_tracker)
3. Locate: _workspaces/roadmap/phases/phase-XX.yaml (detailed AC specs)
4. Reference: _workspaces/roadmap/_archives/cortex-master-v1.yaml (if needed for patterns)
```

### Step 2: Verify Phase Ready
```yaml
# From cortex-master.yaml phase_tracker, find your phase:
phase_tracker:
  PHASE-XX:
    status: "NOT_STARTED"      # Check this is not LOCKED
    locked: false              # Must be false to proceed
    ac_ids: N                  # Number of ACs to implement
    phase_yaml: "phases/phase-XX.yaml"  # Read this file for details
    
    # Optional: Check dependencies
    dependencies:
      - "PHASE-YY (or None)"   # Must be completed first
```

### Step 3: Load Phase Details
```bash
# Read the specific phase YAML for AC-IDs and requirements
cat _workspaces/roadmap/phases/phase-XX.yaml

# This contains:
# - ac_ids: [AC-XXX-XX-01, AC-XXX-XX-02, ...]
# - files_to_create: [list of files]
# - testing: {unit_tests_expected, integration_tests_expected, ...}
# - success_criteria: [verifiable outcomes]
```

### Step 4: Execute Phase
```
For each AC-ID in the phase:
  1. Create git checkpoint: git commit -m "checkpoint: before AC-XXX-XX-01"
  2. Implement AC (with tests, audit logging)
  3. Verify audit entries created (AC_START, AC_EXECUTE, AC_COMPLETE)
  4. Update phase_tracker status if needed
  5. Move to next AC-ID
```

### Step 5: Lock Phase
```yaml
# When ALL AC-IDs in phase are COMPLETED:
1. Verify audit trail: SELECT COUNT(*) FROM audit_log WHERE ac_id LIKE 'AC-XXX-%'
2. Update cortex-master.yaml:
   phase_tracker:
     PHASE-XX:
       status: "COMPLETED"
       locked: true
3. Git commit: git commit -m "phase-XX: COMPLETED - audit verified"
```

### File References During Phase Execution

| Purpose | File | Location |
|---------|------|----------|
| Current phase status | cortex-master.yaml | `_workspaces/roadmap/cortex-master.yaml` |
| AC-ID specifications | phase-XX.yaml | `_workspaces/roadmap/phases/phase-XX.yaml` |
| baseline patterns/reference | cortex-master-v1.yaml | `_workspaces/roadmap/_archives/cortex-master-v1.yaml` |
| Phase completion reports | phase-XX-report.md | `_workspaces/roadmap/reports/phase-XX-*.md` |
| Governance rules | core-rules.yaml | `cortex-brain/tier0/governance/core-rules.yaml` |
| Audit trail | governance.db | `cortex-brain/state/governance.db` |

---

## Governance Tools Integration (PHASE-08 Feature)

**New governance tools available for developer workflows:**

### Governance CLI Commands

```bash
# Query governance rules
cortex-governance query CORE-008                    # Query specific rule
cortex-governance query --domain tdd --phase PHASE-01  # Filter by domain/phase
cortex-governance query --tier 0 --format json     # Immutable rules in JSON

# Validate compliance
cortex-governance validate --path src/              # Validate directory
cortex-governance validate --phase PHASE-01         # Validate phase compliance
cortex-governance validate --ac-id AC-AR-001-01     # Check AC completion
cortex-governance validate --strict --fix           # Fix auto-fixable violations
```

### Agent Commands (Governance-Aware)

**Use these commands in your workflow to integrate governance:**

```
/governance-query              # Interactive rule query
/governance-validate <path>    # Validate compliance
/governance-compliance <phase> # Generate compliance report
/governance-violations <phase> # List violations by severity
/phase-readiness <phase>       # Complete readiness assessment
```

### Pre-Commit Hook

Git commits are validated automatically:
- AC-ID format checked (AC-DOMAIN-NNN-NN)
- Governance violations prevent commit
- Use `git commit --no-verify` to bypass (use with caution)

### IDE Integration (PHASE-08 Feature)

VS Code extension shows:
- Governance violations inline (squiggly lines)
- Hover shows violation details and remediation
- Quick-fix suggestions for auto-fixable issues
- Configurable per-rule severity

---

## PHASE-13 Implementation Context

### Current Phase: Observability & Telemetry Maturity ⏳

**What's Completed (12 phases locked + 2 enhancement phases):**
- ✅ PHASE-01 through PHASE-12: Foundation → Knowledge Ecosystem
- ✅ PHASE-ENHANCEMENT-01, 02: Response header injection system
- ✅ Total: 243 tier3 tests passing (KN-001 through KN-004)

**What's Next (PHASE-13, 5 ACs):**
1. **OB-001-01**: OpenTelemetry Integration
2. **OB-001-02**: Metrics Dashboard
3. **OB-002-01**: Alerting & Health Monitoring
4. **OB-002-02**: Performance Profiling & Optimization
5. **OB-003-01**: Audit Trail Enhancement

**Governance Rules for OB-IDs:**
- CORE-008: Tests first (RED → GREEN) - MANDATORY
- CORE-011: Type hints MANDATORY on all functions
- CORE-012: Docstrings MANDATORY (Google style)
- CORE-024: Observability must log to audit trail
- CORE-028: Kebab-case, ≤25 chars (e.g., `otel_exporter.py`, NOT `open_telemetry_exporter_system.py`)

**Before Starting OB-001-01:**
1. Load `_workspaces/roadmap/phases/phase-13.yaml`
2. Verify prerequisites: PHASE-10-ADAPTIVE-EXECUTION locked ✅
3. Create git checkpoint: `git commit -m "checkpoint: before OB-001-01"`
4. Load phase-specific rules: `phase-enforcement-map.yaml`
5. Display Phase Initiation Summary

---

## EXECUTIVE SUMMARY PROTOCOL

**MANDATORY: Display executive summary BEFORE starting any phase and AFTER completing any phase.**

### Phase Initiation Summary (Display BEFORE starting phase)

```yaml
executive_summary_start:
  phase: "PHASE-XX"
  title: "[Phase Title from cortex-master.yaml]"
  
  # WHAT IS BEING IMPLEMENTED
  scope:
    - "[Focus area 1 from phases.phase_XX.focus]"
    - "[Focus area 2]"
    - "[Focus area N]"
  
  # ACCEPTANCE CRITERIA OVERVIEW
  acceptance_criteria:
    total_ac_ids: N
    critical_acs:
      - "[AC-ID]: [Description] — CRITICAL for [reason]"
    verification_method: "Each AC-ID requires START → EXECUTE → COMPLETE audit entries"
  
  # AUDIT & SAFETY VALIDATION
  audit_validation:
    minimum_entries_required: "N × 3 (one per AC-ID lifecycle event)"
    hash_chain_enforcement: "Tamper-evident chain must remain unbroken"
    verification_query: "SELECT ac_id, COUNT(*) FROM audit_log WHERE ac_id LIKE 'AC-%-XX%' GROUP BY ac_id"
  
  # DETERMINISM & SAFETY
  determinism:
    state_source: "SQLite governance.db (WAL mode)"
    idempotency: "Re-running phase with same inputs produces same state"
    rollback_point: "Git checkpoint created before first AC-ID"
  
  # ASSUMPTIONS (Facts vs. Expectations)
  assumptions:
    - "[Assumption 1] — Source: [where this is defined]"
    - "[Assumption 2] — Source: [where this is defined]"
  
  # RISKS & BLOCKERS
  risks:
    - severity: "HIGH|MEDIUM|LOW"
      description: "[Risk description]"
      mitigation: "[How to address]"
  blockers:
    - "[Blocker if any — empty if none]"
  
  # DEPENDENCIES
  dependencies:
    required_phases: "[PHASE-XX or 'None']"
    required_components: "[List components that must exist]"
  
  # IMPACT ASSESSMENT
  impact:
    files_affected: "[Estimated count or list]"
    new_components: "[Components to be created]"
    governance_rules_enforced: "[SKULL rules applied]"
  
  # RECOMMENDATION (Separated from facts)
  recommendation: |
    [Clear, actionable next step. e.g., "PROCEED with AC-AR-001-01" or "RESOLVE blocker X first"]
```

### Phase Completion Summary (Display AFTER completing phase)

```yaml
executive_summary_complete:
  phase: "PHASE-XX"
  title: "[Phase Title]"
  status: "COMPLETED"
  
  # WHAT WAS DELIVERED
  delivered:
    ac_ids_completed: N
    components_created:
      - "[Component 1]"
      - "[Component N]"
    tests_passing: N
  
  # AUDIT VERIFICATION RESULTS
  audit_verification:
    total_entries: N
    entries_per_ac_id_avg: N
    hash_chain_valid: true|false
    verification_timestamp: "ISO-8601"
    anomalies_detected: "[None or list]"
  
  # SAFETY CONFIRMATION
  safety:
    governance_violations: 0
    tier0_rules_enforced: "[SKULL-XXX through SKULL-YYY]"
    production_mode_tested: true|false
  
  # EVIDENCE CAPTURED
  evidence:
    git_checkpoint: "[commit-hash]"
    evidence_bundles: N
    audit_log_entries: N
  
  # FACTS (Verified outcomes)
  facts:
    - "[Fact 1 — verifiable from audit logs]"
    - "[Fact 2 — verifiable from test results]"
  
  # RISKS REALIZED (If any)
  risks_realized:
    - "[Risk that materialized] — Resolution: [how resolved]"
  
  # OPEN ITEMS (Deferred or discovered)
  open_items:
    - "[Item] — Deferred to: [PHASE-XX]"
  
  # NEXT PHASE READINESS
  next_phase:
    id: "PHASE-XX"
    title: "[Title]"
    prerequisites_met: true|false
    recommendation: "[PROCEED or WAIT for X]"
```

---

## Path Portability Patterns (CORE-028)

**After PHASE-12 Fix:** All paths MUST be portable across machines.

### What Was Fixed in PHASE-12
- 5 tier3 knowledge modules hardcoded `/Users/asifhussain/PROJECTS/CORTEX/` paths
- All converted to `Path(__file__).parent` patterns  
- Commit: `54fe9ad91` - "fix(CORE-028): Replace absolute paths with portable Path(__file__).parent patterns"
- All 243 tier3 tests validated - zero regressions

### Correct Patterns by File Type

**Python Source Code (cortex_brain/, cortex_brain/, src/):**

```python
# ✅ CORRECT - Module initialization paths (use this in __init__ methods)
config_path = Path(__file__).parent / "config.yaml"              # Same directory
db_path = Path(__file__).parent.parent.parent / "state" / "db.db" # Up 3 dirs

# Example from expert_registry.py (post-fix):
self.registry_path = Path(__file__).parent / "expert-registry.yaml"
self.db_path = Path(__file__).parent.parent.parent / "state" / "governance.db"

# ✅ CORRECT - For tests, use path resolution
from pathlib import Path
test_path = Path(__file__).parent / "fixtures" / "data.yaml"

# ❌ WRONG - Breaks on other machines / CI/CD systems
path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/config.yaml")
```

**YAML Configuration Files:**

```yaml
# ✅ CORRECT - Relative paths only
paths:
  database: "cortex-brain/state/governance.db"
  rules: "cortex-brain/tier0/governance/core-rules.yaml"
  logs: "cortex-brain/state/audit.log"

# ❌ WRONG - Absolute paths lock to one machine
paths:
  database: "/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/state/governance.db"
```

### Validation

**Pre-commit hook ensures CORE-028 compliance:**
```bash
# This is automatically run during git commit
grep -rn '/Users/\|/home/' --include="*.py" --include="*.yaml" . | grep -v '.git/' | grep -v 'prompt.md' | grep -v '.venv/'
# If output is empty → ✅ PASS
# If output found → ❌ FAIL - Must fix before committing
```

**If violations found:**
1. Replace with portable patterns using `Path(__file__).parent`
2. Commit with: `git commit -m "fix(CORE-028): [description]"`
3. Validate: `pytest tests/unit/tier3/ -q --tb=no`

---

## Workflow

1. **Read** `cortex-master.yaml` → check `phase_tracker`
2. **DISPLAY EXECUTIVE SUMMARY** → Phase Initiation Summary (MANDATORY)
3. **Read** `_workspaces/roadmap/phases/phase-XX.yaml` → get AC-IDs for current phase
4. **GIT CHECKPOINT** → Create checkpoint before starting AC-ID
5. **Implement** one AC-ID at a time with tests (audit logging ACTIVE)
6. **Verify Audit Trail** → Query audit logs for AC-ID entries
7. **Update** phase YAML status when AC-ID complete
8. **BEFORE PHASE LOCK**: Execute cleanup (see Cleanup Protocol below)
9. **When phase done**: Validate audit trace → **DISPLAY COMPLETION SUMMARY** → Update `phase_tracker` → `status: "COMPLETED"`, `locked: true`

---

## Enhancement Phases (Optional Refinement Phases)

**NEW CONCEPT (2026-01-18): Optional phases that extend locked phases with new capabilities**

### Purpose
Enhancement phases allow strategic refinement and modernization of previously completed phases. They capture new requirements that emerge after a phase is locked, WITHOUT disrupting the baseline implementation.

### When to Use Enhancement Phases
Enhancement phases are **ONLY** considered for implementation when:
1. ✅ ALL OTHER phases in phase_tracker have: `locked: true`
2. ✅ This phase is the ONLY phase with: `locked: false` AND `implement_when_ready: true`
3. ✅ ALL mandatory phases from `cortex-master.yaml` phase_tracker are COMPLETED
4. ✅ NO other pending work exists in phase_tracker
5. ✅ System is in a stable, production-ready state

### Enhancement Phase Property (Updated 2026-01-18)

Enhancement phases have a special metadata property in `cortex-master.yaml`:

```yaml
PHASE-XX-ENHANCEMENT:
  title: "Enhancement Phase Title"
  description: "Description of enhancements"
  
  # UPDATED PROPERTY (2026-01-18) - Indicates this is an enhancement phase
  enhancement_phase: true
  implement_when_ready: true  # BLOCKS execution until gating conditions met
  
  # Standard properties
  status: "NOT_STARTED"
  locked: false  # ONLY this phase has locked: false
  requires: "PHASE-XX"  # References the original phase being enhanced
  estimated_hours: N
  
  # Enhancement-specific notes
  enhancement_rationale: |
    Why this enhancement is valuable and what changed since original phase
  
  implementation_prerequisite: |
    cortex-builder.prompt.md MUST implement this phase ONLY when:
    - ALL OTHER phases in phase_tracker have: locked: true
    - This phase is the ONLY phase with: locked: false AND implement_when_ready: true
    - ALL mandatory phases (PHASE-01 through PHASE-22) are COMPLETED and LOCKED
    - System audit trail is fully verified and unbroken
    - Production baseline is established and stable
```

### Decision Logic for cortex-builder (Updated 2026-01-18)

When evaluating phases for implementation:

```yaml
# PSEUDOCODE for phase selection logic with implement_when_ready
if cortex-master.yaml.phase_tracker contains phases with locked: false:
  # Count phases with locked: false
  unlocked_phases = filter phase_tracker where locked == false
  
  if len(unlocked_phases) == 1 AND unlocked_phases[0].implement_when_ready == true:
    # Single enhancement phase with gating property
    enhancement_phase = unlocked_phases[0]
    
    if all_other_phases_locked_true AND system_audit_verified:
      # Gating conditions met
      return enhancement_phase for implementation
    else:
      # Conditions not met - wait
      return "DEFER: Waiting for all mandatory phases to complete"
  
  else:
    # Multiple unlocked phases or wrong phase - implement mandatory phases first
    for each phase in unlocked_phases:
      if phase.implement_when_ready != true:
        # Mandatory phase
        return phase
    
    # Should not reach here
    return "ERROR: Multiple phases with implement_when_ready==true"
  
else:
  # All phases are locked
  return "SYSTEM COMPLETE - All phases locked, ready for deployment"
```

### Implementation Pattern for Enhancements (Updated)

When implementing an enhancement phase with `implement_when_ready: true`:

1. **Verify Gating** - Confirm ALL other phases have `locked: true`
2. **Check Audit Trail** - Verify production baseline is established
3. **Unlock Original Phase** - Set `locked: false` on the phase being enhanced
4. **Create New AC-IDs** - Prefix new ACs with enhanced domain (e.g., `DO-002-04` after `DO-002-03`)
5. **Reference Baseline** - Link to patterns from original phase implementation
6. **Test Everything** - Follow CORE-008 (tests first) for ALL new AC-IDs
7. **Re-Lock Original** - Set `locked: true` after enhancement complete (versioned)

### Example 1: PHASE-15-DASHBOARD-UNIVERSAL with `implement_when_ready: true`

**NEW REDESIGN (2026-01-18)**: Universal multi-repo dashboard architecture

```yaml
# Current baseline phase (stays locked)
PHASE-15-NEURAL-OBSERVATORY:
  status: "COMPLETED"
  locked: true
  ac_ids: 12  # All original features locked

# NEW PHASE-15-DASHBOARD-UNIVERSAL (enhancement with universal deployment)
PHASE-15-DASHBOARD-UNIVERSAL:
  title: "Universal CORTEX Dashboard - Multi-Repo Visualization"
  description: |
    Dashboard operates from CORTEX/ folder, works in ANY repo where CORTEX is cloned.
    Zero setup required, MCP tools exposed universally.
  
  enhancement_phase: true
  implement_when_ready: true
  
  status: "NOT_STARTED"
  locked: false
  
  ac_ids: 16  # New universal architecture ACs
  
  # SECTIONS (4 ACs each)
  # Section A: Foundation (AC-DASH-001-01 through 001-04)
  # Section B: Visualization (AC-DASH-002-01 through 002-04)
  # Section C: Real-Time (AC-DASH-003-01 through 003-04)
  # Section D: UX (AC-DASH-004-01 through 004-04)
```

**Implementation Pattern**:
```
Week 1: AC-DASH-001-01/02/03/04 - Universal shell, repo detection, metrics, context switching
Week 2: AC-DASH-002-01/02/03/04 - Health dashboard, CORTEX ops, MCP tools, compliance
Week 3: AC-DASH-003-01/02/03/04 - WebSocket, audit streaming, test tracking, alerts
Week 4: AC-DASH-004-01/02/03/04 - Dark/light theme, export, layouts, search
```

**Success Criteria**:
- ✅ Dashboard loads in <2 seconds
- ✅ Works in any repo without setup
- ✅ All 16 ACs with passing tests
- ✅ MCP tools visible and functional
- ✅ Multi-repo context switching works

### Example 2: PHASE-DEPLOYMENT with `implement_when_ready: true`

**NEW REDESIGN (2026-01-18)**: Universal multi-repo deployment & distribution

```yaml
# NEW PHASE-DEPLOYMENT (enhancement with multi-repo distribution)
PHASE-DEPLOYMENT:
  title: "CORTEX Universal Deployment & Multi-Repo Distribution"
  description: |
    Single-command installation, multi-repo deployment, upgrade capability.
    CORTEX operates from its own folder, reads/modifies parent repo.
  
  enhancement_phase: true
  implement_when_ready: true
  
  status: "NOT_STARTED"
  locked: false
  
  ac_ids: 10  # Multi-repo deployment ACs
  
  # SECTIONS (2-3 ACs each)
  # Section A: Bootstrap (AC-DEPLOY-001-01 through 001-03)
  # Section B: Multi-Repo (AC-DEPLOY-002-01 through 002-03)
  # Section C: Upgrade (AC-DEPLOY-003-01 through 003-02)
  # Section D: Production (AC-DEPLOY-004-01 through 004-02)
```

**Installation Flow**:
```bash
# Single command installation
cd company-repo
git clone https://github.com/cortex-ai/cortex.git CORTEX
cd CORTEX
./cortex init
cortex dashboard  # Opens dashboard showing parent repo metrics
```

**Implementation Pattern**:
```
Week 1: AC-DEPLOY-001-01/02/03 - Init command, auto-detection, MCP registration
Week 2: AC-DEPLOY-002-01/02/03 - Path isolation, context switching, shared state
Week 3: AC-DEPLOY-003-01/02 - Upgrade mechanism, versioning
Week 4: AC-DEPLOY-004-01/02 - Security hardening, performance optimization
```

**Success Criteria**:
- ✅ `git clone + cortex init` works in <5 minutes
- ✅ Parent repo completely unchanged (except CORTEX/ folder)
- ✅ Dashboard accessible immediately after init
- ✅ MCP tools available in any repo context
- ✅ `cortex upgrade` pulls latest without breaking
- ✅ All 10 ACs with passing tests

### Critical Interdependency

**PHASE-15-DASHBOARD-UNIVERSAL** MUST complete before **PHASE-DEPLOYMENT** begins:

```
1. PHASE-15-DASHBOARD-UNIVERSAL (16 ACs) → universal dashboard foundation
           ↓ (MUST be locked: true)
2. PHASE-DEPLOYMENT (10 ACs) → uses dashboard in deployment package
```

**Reason**: PHASE-DEPLOYMENT includes dashboard in installation package. Dashboard must be production-ready before packaging.

### Gating Logic for Both Enhancement Phases

Both PHASE-15-DASHBOARD-UNIVERSAL and PHASE-DEPLOYMENT use the SAME gating mechanism:

```python
def can_implement_enhancement_phase(phase_name):
    """Check if enhancement phase with implement_when_ready should be implemented"""
    
    # 1. Verify only ONE phase has locked: false
    unlocked = [p for p in all_phases if p.locked == false]
    if len(unlocked) != 1:
        return False, f"ERROR: {len(unlocked)} unlocked phases, expected 1"
    
    # 2. Verify that one phase has implement_when_ready: true
    if unlocked[0].implement_when_ready != true:
        return False, "ERROR: Only unlocked phase doesn't have implement_when_ready"
    
    # 3. Verify ALL other phases have locked: true
    if not all(p.locked == true for p in all_phases if p != unlocked[0]):
        return False, "ERROR: Not all other phases are locked"
    
    # 4. Verify audit trail is verified
    if not audit_trail.is_verified():
        return False, "ERROR: Audit trail not verified"
    
    # 5. All checks passed - phase ready for implementation
    return True, f"READY: {phase_name} approved for implementation"
```

**How cortex-builder Uses This**:
1. Before each planning cycle, call `can_implement_enhancement_phase()`
2. If returns True: Implement the enhancement phase with full priority
3. If returns False: Focus on completing mandatory phases instead


---

## Cleanup Protocol (REQUIRED BEFORE PHASE LOCK)

**Mandatory cleanup checklist before setting `locked: true`:**

### File Organization (Kebab-Case, Max 20 chars)
- ✅ No phase-specific `.md` files in root (`PHASE-XX-*.md` → DELETE)
- ✅ No temporary AC reports in root (`AC-*.md` → DELETE)
- ✅ If summary docs created → Move to `.github/docs/` with kebab-case names
- ✅ Root contains ONLY: `README.md`, `pytest.ini`, `requirements.txt`

### Documentation Standards
- ✅ Status updates in `.github/docs/current-status.md` (not STATUS.md in root)
- ✅ Structured data as YAML/JSON, not Markdown
- ✅ Evidence captured in `governance.db`, not separate files
- ✅ Archive old phase transcripts to `.github/evidence/chat-archive/`

### Git Cleanup
- ✅ All changes committed with clear messages
- ✅ Final checkpoint: `git commit -m "phase-XX: COMPLETED - cleanup done"`
- ✅ No uncommitted changes before phase lock

**Reference:** `.github/docs/cleanup-policy.md` for detailed guidelines

## Git Checkpoint Protocol

**MANDATORY: Create git checkpoint before every major action**

```bash
# Before starting AC-ID implementation
git add -A && git commit -m "checkpoint: before AC-XXX-XXX"

# After successful test pass
git add -A && git commit -m "AC-XXX-XXX: [description] - tests passing"

# Before any file modification
git stash push -m "pre-modify-checkpoint" || git add -A && git commit -m "checkpoint: pre-modify"
```

### Checkpoint Rules
| Action | Checkpoint Required | Commit Pattern |
|--------|---------------------|----------------|
| Start AC-ID | YES | `checkpoint: before AC-XXX-XXX` |
| File modification | YES | `checkpoint: pre-modify` |
| Tests pass | YES | `AC-XXX-XXX: [desc] - tests passing` |
| Phase cleanup | YES | `phase-XX: cleanup done` |
| Phase complete | YES | `phase-XX: COMPLETED - audit verified, cleanup done` |

### Rollback Commands
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Restore from stash
git stash pop
```

---

## Executive Summary Generation Rules

**When generating executive summaries, follow these principles:**

### Content Rules
1. **Bullet points only** — No paragraphs, no code blocks in summary body
2. **Under 1 minute read** — Maximum 25 bullet points total
3. **Actionable** — Every summary ends with a clear next action
4. **Deterministic language** — Use "WILL", "MUST", "SHALL" not "might", "could", "should"

### Separation of Concerns
| Category | Content Type | Source |
|----------|--------------|--------|
| **Facts** | Verified, measurable | `cortex-master.yaml`, audit logs, test results |
| **Assumptions** | Expected but not yet verified | Phase requirements, dependencies |
| **Risks** | Potential issues | Historical patterns, complexity analysis |
| **Recommendations** | Suggested actions | Builder judgment based on facts |

### Safety & Auditability Emphasis
- Always state hash chain status
- Always state audit entry counts
- Always confirm governance tier enforcement
- Always reference git checkpoint
- Always note any governance bypasses (should be 0)

### Impact Assessment Rules
- List all files that WILL be modified (not might)
- List all new components to be created
- State which SKULL rules will be enforced
- Note any breaking changes

---

## Issue Review & Remediation Pattern

**NEW (Jan 16, 2026): Structured pattern for addressing discovered issues holistically.**

When reviewing issues from `_workspaces/roadmap/issues/`:

1. **Holistic Review**: Read entire cortex-master.yaml + full issue-report-NN.yaml (not sections)
2. **Verification**: Grep codebase to verify claims; check audit trail
3. **Decision**: REMEDIATION | ACCEPT-KNOWN | DEFER | ARCHITECTURE-FIX
4. **Remediation**: Create AC-REM-XXX-XX acceptance criteria with audit evidence
5. **Closure**: Rename issue-report-NN.yaml → issue-report-NN-done.yaml

**See**: `.github/prompts/cortex-builder-issue-remediation-pattern.md` for complete pattern

**Agents**: Create new agents as needed with `.github/agents/cortex-XXX.md` format (kebab-case, ≤25 chars)

## Commands (Current - Updated)

### Implementation Commands
- `/implement` - Implement next AC-ID (checks cortex-master.yaml phase_tracker first)
- `/status` - Show current phase_tracker status from cortex-master.yaml
- `/phase <N>` - Show details for PHASE-N (reads from phases/phase-N.yaml)
- `/lock PHASE-XX` - Mark phase as locked (only after ALL AC-IDs verified + audit)
- `/report <phase>` - Generate completion report to reports/ directory

### Plan Navigation (Current)
- `/show-master` - Display cortex-master.yaml (Current)
- `/show-phase <N>` - Display phases/phase-N.yaml specifications
- `/show-v1` - Reference _archives/cortex-master-v1.yaml (258 ACs)
- `/roadmap-status` - Show all phases and their status (from phase_tracker)
- `/find-phase <keywords>` - Search for phase by description

### Governance & Validation
- `/validate-phase <phase>` - Check phase readiness (dependencies, prerequisites)
- `/audit-trail <ac-id>` - Query governance.db for audit entries
- `/check-governance <path>` - Validate files meet SKULL rules
- `/phase-readiness <phase>` - Complete pre-implementation assessment

### Current Specific
- `/transition-info` - Show v1→v2 transition details
- `/archives` - Show what's in _archives/ and how to reference it
- `/continuation-context` - Show baseline baseline knowledge for current phase
- `/show-reports` - List all reports in reports/ directory

### Plan Modification
- `/modify <target>` - Modify plan component (AC-ID, phase, dependency)
- `/add-ac <phase> <title>` - Add new acceptance criteria to phase
- `/remove-ac <ac-id>` - Remove AC-ID (must not break dependencies)
- `/move-ac <ac-id> <to-phase>` - Move AC-ID to different phase
- `/reorder <ac-id> <after-ac-id>` - Change AC-ID sequence

## Modification Rules (HOLISTIC VALIDATION)

**Before ANY modification, validate:**

```yaml
validation_checklist:
  conflicts:
    - Does this duplicate existing AC-ID scope?
    - Does this contradict another AC-ID's requirements?
    - Does this break existing dependencies?
  
  contradictions:
    - Does this reverse a decision made elsewhere?
    - Does this conflict with tier0 governance rules?
    - Does this invalidate already-completed work?
  
  ambiguity:
    - Is the AC-ID criteria measurable and testable?
    - Are dependencies explicitly stated?
    - Is success/failure clearly defined?

  phase_integrity:
    - Does phase still have coherent scope after change?
    - Are inter-phase dependencies still valid?
    - Does total AC-ID count remain accurate in phase_tracker?
```

### Modification Response Format

```yaml
modification:
  type: "add|remove|move|reorder|update"
  target: "AC-XXX-XXX or PHASE-XX"
  validation:
    conflicts: []      # List any found, empty = pass
    contradictions: [] # List any found, empty = pass  
    ambiguity: []      # List any found, empty = pass
  approved: true|false
  changes_made:
    - file: "path"
      change: "description"
  ripple_effects:      # Other files/AC-IDs affected
    - "Updated phase_tracker.PHASE-XX.ac_count"
```

## Files (Current - Updated Structure)

**Current SSOT (Single Source of Truth) - 2026-01-17 Transition**

```
_workspaces/roadmap/
├── cortex-master.yaml              ✅ Current Master plan (CURRENT SSOT - ONLY YAML)
│
├── phases/                         ✅ Active phase specifications (Current)
│   ├── phase-07-intent-router.yaml ✅ READY - 14 ACs
│   ├── phase-08.yaml               ✅ READY - 6 ACs
│   ├── phase-09.yaml               ✅ READY - 8 ACs
│   ├── phase-10.yaml               ✅ READY - 5 ACs
│   ├── phase-11.yaml               📝 STUB - 6 ACs
│   ├── phase-12.yaml               📝 STUB - 7 ACs
│   ├── phase-13.yaml               📝 STUB - 9 ACs
│   ├── phase-15-neural-observatory.yaml  📝 STUB - 12 ACs
│   ├── phase-16-orchestrator-continuation.yaml  📝 STUB - 9 ACs
│   ├── phase-17-domain-brain.yaml  📝 STUB - 12 ACs
│   ├── phase-18-orchestrator-devx.yaml  📝 STUB - 4 ACs
│   ├── phase-19-template-tool-implementation.yaml  📝 STUB - 6 ACs
│   └── phase-20-template-content.yaml  📝 STUB - 6 ACs
│
├── reports/                        ✅ Generated phase reports (centralized)
│   └── (phase-XX-completion-report-YYYY-MM-DD.md)
│
└── _archives/                      ✅ baseline Historical Reference
    ├── ARCHIVE-INDEX.md            Archive navigation guide
    ├── cortex-master-v1.yaml       Original comprehensive plan (258 ACs)
    ├── cortex-consolidated.yaml    Previous consolidation
    ├── phases-v1/                  Original phase files (20+)
    ├── docs/                       Historical markdown files (18+)
    ├── issues/                     Issue tracking materials
    └── recommendations/            Automation & config files

cortex-brain/                       # Governance & State
├── tier0/governance/
│   ├── core-rules.yaml             25 immutable SKULL rules
│   ├── phase-enforcement-map.yaml  Phase-specific rules
│   └── ac-validation-checklist.yaml AC validation criteria
└── state/
    └── governance.db               SQLite audit trail (WAL mode)
```

### Key Current Differences from baseline

| Aspect | baseline | Current |
|--------|-----|------|
| Master file | 200KB+ monolithic | 212KB organized (continuation format) |
| Root clutter | 20+ .md files | ZERO (.md files) |
| _workspaces/roadmap root | 20+ files mixed | ZERO (.md files - all in docs/) |
| Phase files | Mixed in root | Organized in `phases/` |
| Reports | Scattered | Centralized in `reports/` (YAML only) |
| Historical docs | In root | Archived in `_archives/` |
| Status | Locked baseline baseline | Active v2 work |
| Reference | None | `_archives/cortex-master-v1.yaml` |

### How to Find Things (Current)

```
❓ "What's the current status?" 
→ Read: cortex-master.yaml (phase_tracker section)

❓ "How do I implement PHASE-XX?"
→ Read: phases/phase-XX.yaml (AC specs + files to create)

❓ "What patterns were used in v1?"
→ Read: _archives/cortex-master-v1.yaml (258 completed ACs)

❓ "Where do I report phase progress?"
→ Write: reports/phase-XX-completion-report-YYYY-MM-DD.md

❓ "How do I verify audit trail?"
→ Query: SELECT * FROM cortex-brain/state/governance.db

❓ "What's the difference between baseline and v2?"
→ Read: docs/PHASE-0-5-TO-PHASE-1-TRANSITION-STATUS.md (this session's work)
```

## Audit Verification Gate

**MANDATORY: Phase completion requires audit trail verification**

```yaml
audit_verification:
  before_lock:
    - Query audit logs for ALL AC-IDs in phase
    - Verify each AC-ID has: START, EXECUTE, COMPLETE entries
    - Verify hash chain integrity (no gaps)
    - Record verification timestamp in phase_tracker

  query_command: |
    SELECT ac_id, COUNT(*) as entries, MIN(timestamp) as start, MAX(timestamp) as end
    FROM audit_log
    WHERE ac_id LIKE 'AC-%-XX%'  -- Replace XX with phase number
    GROUP BY ac_id

  required_entries_per_ac_id:
    - operation: "AC_START" (logged before implementation)
    - operation: "AC_EXECUTE" (logged during implementation)
    - operation: "AC_COMPLETE" (logged after tests pass)
```

### Phase Lock Checklist
```yaml
phase_lock_checklist:
  - [ ] All AC-IDs have status: COMPLETED
  - [ ] All tests passing (pytest output captured)
  - [ ] Audit entries exist for each AC-ID (query verified)
  - [ ] Hash chain integrity verified
  - [ ] Git checkpoint committed
  - [ ] phase_tracker.audit_verified: true
```

## Rules

1. **YAML-only**: Never create markdown docs for the plan
2. **AC-ID driven**: Every action tied to an AC-ID
3. **Test first**: Every AC-ID needs a passing test
4. **Audit always**: Audit logging ACTIVE during ALL development
5. **Verify before lock**: Audit trail verified before `locked: true`
6. **Checkpoint before modify**: Git checkpoint before file changes

## Response Format

```yaml
response:
  phase: "PHASE-XX"
  phase_locked: false
  ac_id: "AC-XXX-XXX"
  action: "implementing|skipped|refused"
  reason: "why"
  git_checkpoint: "commit-hash"  # Created before action
  files_changed: []
  tests_passed: []
  audit_entries:
    - operation: "AC_START"
      timestamp: "ISO-8601"
    - operation: "AC_COMPLETE"
      timestamp: "ISO-8601"
  next: "AC-XXX-XXX"
```

### Phase Completion Response
```yaml
phase_completion:
  phase: "PHASE-XX"
  title: "[Human readable title]"
  ac_ids_completed: 33
  audit_verification:
    total_entries: 99  # ~3 per AC-ID
    hash_chain_valid: true
    query_timestamp: "ISO-8601"
  git_commit: "phase-XX: COMPLETED - audit verified"
  locked: true
```

---

## Example Executive Summaries

### Example: Phase 1 Initiation Summary

```
═══════════════════════════════════════════════════════════════════════════════
                    PHASE-01 EXECUTIVE SUMMARY — INITIATION
═══════════════════════════════════════════════════════════════════════════════

PHASE: PHASE-01 — Foundation
STATUS: INITIATING

▸ SCOPE (What will be implemented)
  • 3-Tier Governance Model (Tier 0 immutable, Tier 1 project, Tier 2 engineering)
  • SQLite-Based AC Index (governance.db with WAL mode)
  • Audit-First Pattern (log intent → execute → log result)
  • State Machine Management (PENDING → IN_PROGRESS → COMPLETED → VERIFIED)
  • Reference Orchestrator Validation (PlanningOrchestrator end-to-end)

▸ ACCEPTANCE CRITERIA
  • Total AC-IDs: 36
  • Critical: AC-AR-002-01 (governance.db schema) — blocks all audit logging
  • Critical: AC-FR-001-02 (hash chain integrity) — ensures tamper evidence
  • Verification: Each AC-ID requires START, EXECUTE, COMPLETE audit entries

▸ AUDIT VALIDATION REQUIREMENTS
  • Minimum audit entries: 108 (36 AC-IDs × 3 lifecycle events)
  • Hash chain: Must remain unbroken throughout phase
  • Verification query ready for phase lock validation

▸ DETERMINISM & SAFETY
  • State stored in: SQLite governance.db (WAL mode for concurrency)
  • Idempotent: Re-running with same inputs produces identical state
  • Rollback: Git checkpoint created before first AC-ID

▸ ASSUMPTIONS
  • SQLite available in Python environment — Source: requirements.txt
  • cortex-brain/tier0/ structure exists — Source: workspace structure
  • No prior governance.db state to migrate — Source: fresh implementation

▸ RISKS
  • HIGH: Database schema changes mid-phase may require migration
    └─ Mitigation: Lock schema after AC-AR-002-01 complete
  • MEDIUM: WAL mode may cause issues on network drives
    └─ Mitigation: Enforce local filesystem for governance.db

▸ BLOCKERS
  • None identified

▸ DEPENDENCIES
  • Required phases: None (PHASE-01 has no prerequisites)
  • Required components: None (foundation phase creates all)

▸ IMPACT
  • New files: ~15 Python modules, 1 SQLite database
  • New components: GovernanceRegistry, DatabaseManager, AuditLogger, StateMachine
  • SKULL rules enforced: SKULL-001 through SKULL-025

▸ RECOMMENDATION
  PROCEED with AC-AR-001-01 (Tier 0 rules loading)
  Create git checkpoint first: `git add -A && git commit -m "checkpoint: before PHASE-01"`

═══════════════════════════════════════════════════════════════════════════════
```

### Example: Phase 1 Completion Summary

```
═══════════════════════════════════════════════════════════════════════════════
                   PHASE-01 EXECUTIVE SUMMARY — COMPLETION
═══════════════════════════════════════════════════════════════════════════════

PHASE: PHASE-01 — Foundation
STATUS: COMPLETED ✓

▸ DELIVERED
  • AC-IDs completed: 36/36 (100%)
  • Components created: GovernanceRegistry, TierResolver, DatabaseManager,
    AuditLogger, HashChainManager, StateMachine, PlanningOrchestrator
  • Tests passing: 108 (all green)

▸ AUDIT VERIFICATION RESULTS
  • Total audit entries: 127
  • Entries per AC-ID (avg): 3.5
  • Hash chain valid: TRUE ✓
  • Verification timestamp: 2026-01-14T10:30:00Z
  • Anomalies detected: None

▸ SAFETY CONFIRMATION
  • Governance violations: 0
  • Tier 0 rules enforced: SKULL-001 through SKULL-025 (all 25)
  • Production mode tested: TRUE ✓

▸ EVIDENCE CAPTURED
  • Git checkpoint: abc123def (tagged: phase-01-complete)
  • Evidence bundles: 36 (one per AC-ID)
  • Audit log entries: 127

▸ FACTS (Verified)
  • All 36 AC-IDs have START, EXECUTE, COMPLETE entries in audit_log
  • Hash chain integrity verified via SQL query
  • All tests pass with 100% success rate
  • governance.db created with correct schema and WAL mode

▸ RISKS REALIZED
  • None — all identified risks were mitigated successfully

▸ OPEN ITEMS
  • None — all Phase 1 scope items completed

▸ NEXT PHASE READINESS
  • Next: PHASE-02 — Orchestration Core
  • Prerequisites met: TRUE ✓
  • Recommendation: PROCEED with PHASE-02 initiation

═══════════════════════════════════════════════════════════════════════════════
```

---

## Current Initialization Checklist

**When starting this cortex-builder session with Current roadmap, follow this checklist:**

### Phase 1: Confirm Current Structure
- [ ] ✅ Read: `docs/ROADMAP-README.md` (Current overview)
- [ ] ✅ Verify: `_workspaces/roadmap/cortex-master.yaml` exists (Current SSOT - ONLY YAML)
- [ ] ✅ Verify: `_workspaces/roadmap/phases/` directory has 13+ phase files
- [ ] ✅ Verify: `_workspaces/roadmap/_archives/cortex-master-v1.yaml` exists (v1 reference)
- [ ] ✅ Verify: NO `.md` files in `_workspaces/roadmap/` root (all moved to `docs/`)

### Phase 2: Confirm baseline Baseline Knowledge
- [ ] ✅ Read: `_workspaces/roadmap/_archives/cortex-master-v1.yaml` (snapshot of v1)
- [ ] ✅ Understand: 258+ completed ACs from baseline are baseline
- [ ] ✅ Understand: 100% test pass rate (153/153 tests) is baseline
- [ ] ✅ Understand: All governance patterns from baseline are still valid
- [ ] ✅ Understand: Current continues from baseline, doesn't replace it

### Phase 3: Load Current Status
- [ ] ✅ Open: `_workspaces/roadmap/cortex-master.yaml`
- [ ] ✅ Locate: `phase_tracker` section
- [ ] ✅ Find: Current phase to work on (status: NOT_STARTED or IN_PROGRESS)
- [ ] ✅ Verify: Phase is not locked (locked: false)
- [ ] ✅ Check: Dependencies are met

### Phase 4: Load Phase Specifications
- [ ] ✅ Locate: `_workspaces/roadmap/phases/phase-XX.yaml` (your target phase)
- [ ] ✅ Read: AC-IDs section (list of all ACs for this phase)
- [ ] ✅ Read: files_to_create section (what will be built)
- [ ] ✅ Read: testing section (test expectations)
- [ ] ✅ Read: success_criteria section (how to verify completion)

### Phase 5: Prepare to Execute
- [ ] ✅ Load: Governance rules from `cortex-brain/tier0/governance/`
- [ ] ✅ Create: Git checkpoint before starting: `git commit -m "checkpoint: before PHASE-XX"`
- [ ] ✅ Display: Executive Summary - Phase Initiation (MANDATORY)
- [ ] ✅ Ready: To begin first AC-ID implementation

### Phase 6: Monitor During Execution
- [ ] ✅ After each AC: Create audit entries (AC_START, AC_EXECUTE, AC_COMPLETE)
- [ ] ✅ After each AC: Verify tests pass (≥98% pass rate target)
- [ ] ✅ After each AC: Create git checkpoint with AC-ID in message
- [ ] ✅ Periodically: Check audit trail integrity (hash chain unbroken)

### Phase 7: Complete Phase
- [ ] ✅ All ACs: Verify all AC-IDs for phase are COMPLETED
- [ ] ✅ Audit Trail: Query governance.db for all AC entries (3 per AC-ID minimum)
- [ ] ✅ Tests: Verify 100% test pass rate achieved
- [ ] ✅ Display: Executive Summary - Phase Completion (MANDATORY)
- [ ] ✅ Update: cortex-master.yaml phase_tracker: status=COMPLETED, locked=true
- [ ] ✅ Commit: `git commit -m "phase-XX: COMPLETED - audit verified"`
- [ ] ✅ Report: Generate phase report to `_workspaces/roadmap/reports/`

---

## Current Master Plan Orchestration Summary

**This prompt orchestrates Current by:**

1. **Awareness**: Knows about Current lean structure (master + phases/*)
2. **Continuation**: References baseline (258 ACs) from _archives/
3. **Execution**: Follows cortex-master.yaml phase_tracker for current work
4. **Specification**: Loads detailed AC requirements from phases/phase-XX.yaml
5. **Governance**: Enforces all SKULL rules from tier0/governance/
6. **Audit**: Logs all AC lifecycle events to governance.db
7. **Reporting**: Generates reports to centralized reports/ directory
8. **Completion**: Marks phases locked after audit verification
9. **Scalability**: Pattern repeats for future iterations (archive current → create next)

**Execution Flow:**
```
1. Load cortex-master.yaml (Current SSOT) → Check phase_tracker
2. Load phases/phase-XX.yaml (detailed specs) → Get AC-IDs
3. Load cortex-builder.prompt.md (this file) → Follow governance
4. Execute → Audit → Verify → Report → Lock → Move to next phase
5. Archive → Continue → Repeat
```

---

## Quick Start: Using Current

### For New Implementation
```bash
# 1. Understand structure
cat _workspaces/roadmap/README.md

# 2. Check status
grep "status:" _workspaces/roadmap/cortex-master.yaml | head -20

# 3. Load phase specs
cat _workspaces/roadmap/phases/phase-07-intent-router.yaml

# 4. Start implementation
# (Follow governance rules, create audit entries)

# 5. Report progress
# (Generate report to _workspaces/roadmap/reports/)
```

### For Referencing baseline Patterns
```bash
# View baseline baseline (258 completed ACs)
cat _workspaces/roadmap/_archives/cortex-master-v1.yaml

# View baseline specific phase details
cat _workspaces/roadmap/_archives/phases-v1/phase-01.yaml

# Understand what changed (v1 → v2)
cat docs/PHASE-0-5-TO-PHASE-1-TRANSITION-STATUS.md
```

### For Phase Completion
```bash
# 1. Verify all ACs done
grep "AC-PHX-007" _workspaces/roadmap/cortex-master.yaml

# 2. Check audit trail
sqlite3 cortex-brain/state/governance.db "SELECT ac_id, COUNT(*) FROM audit_log WHERE ac_id LIKE 'AC-PHX-007%' GROUP BY ac_id"

# 3. Update master plan
# (Edit cortex-master.yaml: status=COMPLETED, locked=true)

# 4. Commit
git commit -m "phase-07: COMPLETED - audit verified"

# 5. Generate report
# (Add phase-07-completion-report-2026-01-XX.md to reports/)
```

---

**Current Ready** ✅  
**Orchestrated by cortex-builder.prompt.md**  
**Last Updated: 2026-01-17**
