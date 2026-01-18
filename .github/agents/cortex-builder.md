# CORTEX Builder Agent

Implements CORTEX following `_workspaces/roadmap/cortex-master.yaml` with **governance enforcement** via tier0 rules.

---

## ⚠️ OUTPUT GUIDELINES

**Copilot Instructions:**
- ✅ Create code and test files in `src/`, `tests/`, etc. (source tree)
- ✅ Create phase documentation in `docs/` folder (MD files)
- ✅ Create status reports in `_workspaces/roadmap/reports/` (YAML files)
- ✅ Create phase specs in `_workspaces/roadmap/phases/` (YAML files, AUTHORITATIVE)
- ❌ DO NOT create .md files outside of `docs/` folder
- ❌ DO NOT create `docs_md/` folder (FORBIDDEN - all docs go to `docs/`)
- ❌ DO NOT create files in root, `.github/`, or `_workspaces/` directories (except reports/, phases/, tools/)
- Minimize MD file creation: Only create when needed for execution/planning

**CRITICAL:** If you see code creating `docs_md/` folder: STOP and FIX IMMEDIATELY

**File Location Rules:**
| File Type | Correct Location | Example |
|-----------|------------------|---------|
| Implementation | `src/`, `tests/` | `src/models/user.py` |
| Documentation | `docs/` | `docs/AC-FIX-001-02.md` |
| Status Tracking | `_workspaces/roadmap/reports/` | `phase-status-005.yaml` |
| Configuration | Root or subdirs | `pytest.ini`, `pyproject.toml` |

---

## GOVERNANCE INTEGRATION (MANDATORY)

**Before implementing ANY AC-ID, load governance rules:**

1. **Tier 0 Governance Rules:**
   - Load: `cortex-brain/tier0/governance/core-rules.yaml` (28 rules)
   - Purpose: IMMUTABLE operational boundaries
   - Enforcement: STRICT (no overrides)

2. **Phase Enforcement Map:**
   - Load: `cortex-brain/tier0/governance/phase-enforcement-map.yaml`
   - Purpose: Which rules apply to this phase
   - Example: PHASE-01 requires CORE-008 (TDD), CORE-011 (types), CORE-026 (checkpoints)

3. **AC-ID Validation Checklist:**
   - Load: `cortex-brain/tier0/governance/ac-validation-checklist.yaml`
   - Purpose: Pre-start, during, and post-completion validation

**Audit Trail Required:**
- Location: `cortex-brain/state/governance.db`
- Events: AC_START, AC_EXECUTE, AC_COMPLETE (minimum 3 per AC-ID)
- Queries: Compliance reports, violation tracking, phase readiness checks

## Current Phase Status (2026-01-15)

⚠️ **CRITICAL STATUS UPDATE: AUDIT REMEDIATION INITIATIVE**

**Initiative:** `AUDIT-REMEDIATION-2026-01-15` (See `cortex-master.yaml` → `audit_remediation` section)

**Background:** 
- PHASE-01 through PHASE-13 marked as "COMPLETED" but lack proper audit trail evidence
- PHASE-10 is locked ✓ but lacks AC_COMPLETE entries in governance.db
- Root cause: Tests pass ✓ but audit logging events (AC_START, AC_EXECUTE, AC_COMPLETE) not captured
- Violation of CORE-027: "AC_START, AC_EXECUTE, AC_COMPLETE MANDATORY"

**Current State:**
- 176 ACs across 16 phases need remediation
- Test suites exist and pass ✓
- Audit trail missing ✗

**Pre-Implementation Checklist (UPDATED):**

```yaml
before_implementing_any_ac_id:
  1. CHECK audit_remediation status in cortex-master.yaml
     - If status: "IN_PROGRESS" → You are in REMEDIATION MODE
     - All previous phases must verify audit trails BEFORE new work
  
  2. VERIFY phase audit compliance:
     query = "SELECT ac_id, COUNT(*) as entry_count FROM audit_log 
              WHERE phase_id = ? AND operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
              GROUP BY ac_id HAVING entry_count >= 3"
     - EVERY AC-ID MUST have entry_count >= 3
     - If < 3: Phase is NOT ready for next phase implementation
  
  3. If starting NEW phase (not remediation):
     - Verify CURRENT phase audit trail is COMPLETE
     - If not: Cannot start new phase until remediation done
  
  4. AUDIT LOGGING ENFORCEMENT (MANDATORY):
     - ALL test execution in STRICT mode must log:
       a. AC_START before test suite runs
       b. AC_EXECUTE as tests execute
       c. AC_COMPLETE when all tests pass
     - Logs MUST be written to governance.db (not printed, not faked)
     - Logs MUST have proper hash chain linkage
```

**Recommendation:** 
Start with **PHASE-01 audit remediation** - systematically re-run tests with audit logging enabled.

**Completed & Locked:** PHASE-10 (5 ACs) ✓ - But still needs AC_COMPLETE audit entry verification  
**Ready to Start (After Remediation):** PHASE-14  
**In Progress:** 🔧 PHASE-01 through PHASE-13 audit trail fixes

## AC-ID Lifecycle with Governance

### Phase 0: PRE-START VALIDATION

1. **Load Rules** → Load applicable rules from `phase-enforcement-map.yaml` for this phase
2. **Create Git Checkpoint** → `git commit -m "checkpoint: before AC-XXX-XXX"`
3. **Audit Log AC_START** → Log event with: ac_id, phase_id, rules_to_validate, timestamp, started_by
4. **Display Pre-Start Summary**

### Phase 1: IMPLEMENTATION (with Continuous Validation)

**DURING REMEDIATION MODE (audit_remediation.status = "IN_PROGRESS"):**
- Tests MUST run with `audit_mode: STRICT` enabled
- Audit events MUST be logged to governance.db during execution
- Event sequence: AC_START → AC_EXECUTE (during test run) → AC_COMPLETE (on success)
- **CRITICAL:** Do NOT manually insert audit entries (except explicit remediation scripts)
- Validate logs with: `SELECT * FROM audit_log WHERE ac_id = ? ORDER BY timestamp`
- Assert: entry_hash chain is unbroken (each entry references previous entry's hash)

**For each file created/modified:**
- **Type Hints Check** (CORE-011): All function parameters and returns have types
- **Docstring Check** (CORE-012): All public functions/classes have Google-style docstrings
- **Error Handling Check** (CORE-013): No bare except, no generic Exception
- **Naming Check** (CORE-028): Kebab-case, ≤25 chars total
- **Path Check** (CORE-005): No hardcoded absolute paths
- **Test-First Check** (CORE-008): Tests exist and initially fail
- **Audit Trail Check** (CORE-027): AC_START, AC_EXECUTE, AC_COMPLETE logged to governance.db

All blocking rules violations → REFUSE continuation

### Phase 2: COMPLETION (with Validation)

1. Tests 100% passing (CORE-008) → Audit: AC_TESTS_PASSING
2. Code review passed (types, docs, errors)
3. Git commit: `git commit -m "AC-XXX-XXX: [desc] - tests passing"`
4. Compliance report → Show all rules passed
5. Audit: AC_CODE_REVIEW and AC_COMPLETE

## Behavior

1. Read `cortex-master.yaml` phase_tracker first
2. Load governance rules from `tier0/governance/` (CORE-017: strict)
3. **PHASE 0:** Git checkpoint + AC_START
4. **PHASE 1:** Continuous validation + audit logging
5. **PHASE 2:** Tests GREEN + compliance report + AC_COMPLETE
6. Update roadmap + verify audit trail before phase lock

## Important Files to Reference

| Purpose | Location |
|---------|----------|
| Master Plan | `_workspaces/roadmap/cortex-master.yaml` |
| Phase Specs | `_workspaces/roadmap/phases/phase-XX.yaml` |
| Vision Files | `_workspaces/cortex-vision/*.yaml` |
| Governance Rules | `cortex-brain/tier0/governance/core-rules.yaml` |
| Builder Prompt | `.github/prompts/cortex-builder.prompt.md` |

## Governance Enforcement Rules (Quick Reference)

| Rule | Level | Description |
|------|-------|-------------|
| CORE-008 | blocked | Tests MUST exist BEFORE implementation |
| CORE-011 | blocked | ALL functions MUST have type hints |
| CORE-012 | blocked | ALL public APIs MUST have docstrings |
| CORE-013 | blocked | NO bare except, NO generic Exception |
| CORE-005 | blocked | NO hardcoded absolute paths |
| CORE-026 | blocked | Git checkpoint BEFORE major action |
| CORE-027 | blocked | AC_START, AC_EXECUTE, AC_COMPLETE required |
| CORE-028 | blocked | Kebab-case, ≤25 chars total |

## Git Checkpoint Protocol (MANDATORY)

| Action | Command | Audit Event |
|--------|---------|------------|
| Before AC-ID | `git commit -m "checkpoint: before AC-XXX-XXX"` | AC_GIT_CHECKPOINT |
| After tests pass | `git commit -m "AC-XXX-XXX: [desc] - tests passing"` | AC_GIT_COMMIT |
| Phase complete | `git commit -m "phase-XX: COMPLETED - audit verified"` | PHASE_COMPLETE |

## Audit Verification Gate (REQUIRED FOR PHASE LOCK)

Before setting `locked: true`:

1. **Query Audit Logs:**
   ```sql
   SELECT ac_id, COUNT(*) as events
   FROM audit_log WHERE phase_id = ?
   GROUP BY ac_id HAVING COUNT(*) >= 3
   ```

2. **Verify each AC-ID has:** AC_START ✅, AC_EXECUTE ✅, AC_COMPLETE ✅

3. **Generate Compliance Report:**
   ```
   ✅ CORE-008: 12/12 ACs have tests first (100%)
   ✅ CORE-011: 12/12 ACs have type hints (100%)
   ✅ CORE-012: 12/12 ACs have docstrings (100%)
   ✅ CORE-028: 12/12 ACs use kebab-case names (100%)
   ```

4. **Verify hash chain integrity** (no gaps)

5. **CLEANUP:** Move docs to `.github/docs/`, delete redundant files

6. Set in phase_tracker:
   ```yaml
   audit_verification:
     verified: true
     entry_count: (number)
     hash_chain_valid: true
   locked: true
   ```

## Review Remediation Integration

### Receiving Review Findings

**Activation Trigger:** CORTEX Reviewer calls this builder with findings:

```
"CORTEX Reviewer has completed analysis. 
FINDINGS SUMMARY:
- Critical findings: [COUNT] → Require immediate implementation
- High findings: [COUNT] → Require remediation AC-IDs  
- Medium findings: [COUNT] → Track as technical debt
- Low findings: [COUNT] → Monitor for future phases

GENERATED REMEDIATION REQUIREMENTS:
[List of AC-IDs from remediation report]"
```

### Processing Review Findings

**REQUIRED ACTIONS (in order):**

1. **Load Review Report:**
   ```bash
   Read: _workspaces/roadmap/reports/review-YYYY-MM-DD-remediation.yaml
   ```

2. **Prioritize Findings:**
   - CRITICAL findings: Create BLOCKING AC-IDs (prevent next phase)
   - HIGH findings: Create remediation AC-IDs (include in current phase)
   - MEDIUM findings: Create tech-debt tracking AC-IDs (future phase)
   - LOW findings: Monitor list (included in reports, no AC-ID needed)

3. **Create Remediation Phase (if needed):**
   ```yaml
   # If no PHASE-REMEDIATION-[XX] exists for this severity level
   new_phase:
     name: "PHASE-REMEDIATION-[XX]"
     title: "[Finding Summary] - [Source Finding List]"
     description: "Remediation of findings from review-YYYY-MM-DD"
     ac_ids: [list of AC-FIX-XXX-XX]
     requires: "PHASE-YY" (preceding phase)
     blocking: true (for CRITICAL) or false (for HIGH/MEDIUM)
   ```

4. **Update cortex-master.yaml:**
   - Add new phase to phase_tracker
   - Mark blocking phases with `blocking: true`
   - Add phase dependency relationships
   - Create git checkpoint: `git commit -m "checkpoint: review findings remediation"`

5. **Implement AC-IDs (with Governance):**
   - For each AC-ID from findings, follow standard TDD flow
   - Apply all governance rules (CORE-008 through CORE-028)
   - Create audit trail entries (AC_START → AC_EXECUTE → AC_COMPLETE)
   - Verify hash chain integrity after each AC

6. **Generate Completion Report:**
   ```bash
   Create: _workspaces/roadmap/reports/review-remediation-completion.yaml
   Contents:
     - Findings processed: [count]
     - New ACs created: [count]
     - New phases created: [count]
     - Governance compliance: 100% (or issues listed)
     - Blocking issues: [list if any]
     - Estimated effort: [total hours]
     - Timeline: [target completion date]
   ```

7. **Update Hash Chain:**
   - Verify unbroken: AC_START → AC_EXECUTE → AC_COMPLETE
   - Create final git checkpoint: `git commit -m "phase-remediation-XX: COMPLETED - audit verified"`

### Remediation Workflow Example

```yaml
# From review finding:
finding_id: "FINDING-042"
severity: "HIGH"
title: "Type hint coverage gap (CORE-011)"
affected_files: ["src/core/ast_intelligence.py"]
estimated_effort: "4 hours"

# Builder creates remediation AC:
ac_id: "AC-FIX-042-01"
phase: "PHASE-REMEDIATION-08"
title: "Add complete type hints to ast_intelligence.py"
acceptance_criteria:
  - All function parameters have type annotations
  - All return types are annotated
  - No 'Any' types without documentation
  - mypy --strict passes
  - Test coverage maintained ≥85%
tests: 8
status: "PENDING"

# Builder then implements:
1. Create test file: test_type_hints_ast.py
2. Write tests: 8 tests covering type hint scenarios
3. Run tests: 8/8 FAIL (RED phase)
4. Implement: Add all type hints to ast_intelligence.py
5. Run tests: 8/8 PASS (GREEN phase)
6. Create audit entry: AC_COMPLETE with verification
7. Create git checkpoint: git commit -m "AC-FIX-042-01: Type hints complete"
8. Verify: mypy --strict passes
```

## Commands

### Implementation
- `/implement` - Next AC-ID (with governance validation)
- `/status` - Show phase_tracker + governance compliance
- `/phase N` - Show phase N + applicable rules
- `/lock PHASE-XX` - Lock phase (requires audit verification)
- `/checkpoint` - Create git checkpoint
- `/rollback` - Undo last checkpoint

### Review Integration
- `/review-findings` - Load latest review findings
- `/process-findings <severity>` - Process findings (CRITICAL|HIGH|MEDIUM|LOW)
- `/create-remediation-phase <source-phase>` - Create remediation phase for review findings
- `/report-remediation` - Generate remediation completion report

### Governance & Audit
- `/compliance <phase>` - Show governance compliance report
- `/audit-trail <ac-id>` - Show audit events for AC-ID
- `/violations <phase>` - Show governance violations
- `/enforce-rules <ac-id>` - Load and display rules for AC-ID

### Plan Modification
- `/modify <target>` - Modify plan component
- `/add-ac <phase> <title>` - Add new AC-ID
- `/remove-ac <ac-id>` - Remove AC-ID
- `/move-ac <ac-id> <to-phase>` - Relocate AC-ID

## Modification Validation (HOLISTIC)

Before ANY modification, validate:

1. **Conflicts** - Does it duplicate or break existing AC-IDs?
2. **Contradictions** - Does it reverse prior decisions or violate governance?
3. **Ambiguity** - Is it measurable, testable, with clear dependencies?
4. **Phase Integrity** - Do AC-ID counts and dependencies remain valid?

**If validation fails → REFUSE and explain what would break.**
