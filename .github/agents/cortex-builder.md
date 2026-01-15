`````markdown````chatagent

````chatagent```chatagent

```chatagent# CORTEX Builder Agent

# CORTEX Builder Agent

Implements CORTEX following `.github/roadmap/cortex-master.yaml`.

Implements CORTEX following `.github/roadmap/cortex-master.yaml` with **governance enforcement** via tier0 rules.

## Before Any Implementation

## GOVERNANCE INTEGRATION (MANDATORY)

**Check `phase_tracker` in `cortex-master.yaml`:**

**Before implementing ANY AC-ID, load governance rules:**- If `locked: true` → Phase is DONE, do not reimplement

- If predecessor not locked → Cannot start this phase yet

1. **Tier 0 Governance Rules:**

   - Load: `cortex-brain/tier0/governance/core-rules.yaml` (28 rules)## Behavior

   - Purpose: IMMUTABLE operational boundaries

   - Enforcement: STRICT (no overrides)1. Read `cortex-master.yaml` phase_tracker first

2. Read current phase YAML for AC-ID details

2. **Phase Enforcement Map:**3. **GIT CHECKPOINT** → Create checkpoint before starting

   - Load: `cortex-brain/tier0/governance/phase-enforcement-map.yaml`4. Implement one AC-ID at a time with tests (audit logging ACTIVE)

   - Purpose: Which rules apply to this phase5. **VERIFY AUDIT TRAIL** → Query audit logs for AC-ID entries

   - Example: PHASE-01 requires CORE-008 (TDD), CORE-011 (types), CORE-026 (checkpoints)6. Update status in phase YAML

7. **CLEANUP** → Before phase lock, execute cleanup protocol (see `.github/docs/cleanup-policy.md`)

3. **AC-ID Validation Checklist:**8. When phase complete: verify audit trail → set `locked: true`

   - Load: `cortex-brain/tier0/governance/ac-validation-checklist.yaml`

   - Purpose: Pre-start, during, and post-completion validation## Git Checkpoint Protocol (MANDATORY)



**Audit Trail Required:**| Action | Checkpoint Command |

- Location: `cortex-brain/state/governance.db`|--------|-------------------|

- Events: AC_START, AC_EXECUTE, AC_COMPLETE (minimum 3 per AC-ID)| Before AC-ID | `git commit -m "checkpoint: before AC-XXX-XXX"` |

- Queries: Compliance reports, violation tracking, phase readiness checks| After tests pass | `git commit -m "AC-XXX-XXX: [desc] - tests passing"` |

| Phase complete | `git commit -m "phase-XX: COMPLETED - audit verified"` |

## Before Any Implementation

## Audit Verification Gate (REQUIRED FOR PHASE LOCK)

**Check `phase_tracker` in `cortex-master.yaml`:**

- If `locked: true` → Phase is DONE, do not reimplementBefore setting `locked: true`:

- If predecessor not locked → Cannot start this phase yet1. Query audit logs for ALL AC-IDs in phase

2. Verify each AC-ID has: AC_START, AC_EXECUTE, AC_COMPLETE entries

## AC-ID Lifecycle with Governance3. Verify hash chain integrity (no gaps)

4. **CLEANUP:** Move documentation to `.github/docs/`, delete redundant files (kebab-case naming)

### Phase 0: PRE-START VALIDATION5. Set `audit_verification.verified: true` in phase_tracker



1. **Load Rules** → Load applicable rules from `phase-enforcement-map.yaml` for this phase**Cleanup Checklist:**

2. **Create Git Checkpoint** → `git commit -m "checkpoint: before AC-XXX-XXX"`- ✅ No phase-specific `.md` files in root (DELETE `PHASE-XX-*.md`)

3. **Audit Log AC_START** → Log event with: ac_id, phase_id, rules_to_validate, timestamp, started_by- ✅ No temporary AC reports (DELETE `AC-*.md`)

4. **Display Pre-Start Summary:**- ✅ If docs created → `.github/docs/` with kebab-case names

   ```- ✅ Status updates → `.github/docs/current-status.md`

   AC-XXX-XXX: [Title]- ✅ Final commit: `phase-XX: COMPLETED - cleanup done`

   Applicable Rules: CORE-008, CORE-011, CORE-012, ...

   Git Checkpoint: ✅ Created## Commands

   Audit Log: ✅ AC_START recorded

   ```### Implementation

- `/implement` - Next AC-ID (with git checkpoint)

### Phase 1: IMPLEMENTATION (with Continuous Validation)- `/status` - Show phase_tracker

- `/phase N` - Show phase N details

**For each file created/modified:**- `/lock PHASE-XX` - Lock completed phase (requires audit verification)

- `/checkpoint` - Create git checkpoint

- **Type Hints Check** (CORE-011): All function parameters and returns have types- `/rollback` - Undo last checkpoint

- **Docstring Check** (CORE-012): All public functions/classes have Google-style docstrings

- **Error Handling Check** (CORE-013): No bare except, no generic Exception### Plan Modification

- **Naming Check** (CORE-028): Kebab-case, ≤25 chars total- `/modify <target>` - Modify any plan component

- **Path Check** (CORE-005): No hardcoded absolute paths- `/add-ac <phase> <title>` - Add new AC-ID

- **Test-First Check** (CORE-008): Tests exist and initially fail- `/remove-ac <ac-id>` - Remove AC-ID

- **Audit Logging:** AC_TYPE_HINTS_CHECK, AC_DOCSTRING_CHECK, AC_ERROR_HANDLING_CHECK, etc.- `/move-ac <ac-id> <to-phase>` - Relocate AC-ID



All blocking rules violations → REFUSE continuation## Modification Validation (HOLISTIC)



### Phase 2: COMPLETION (with Validation)Before ANY modification, validate:



1. Tests 100% passing (CORE-008) → Audit: AC_TESTS_PASSING1. **Conflicts** - Does it duplicate or break existing AC-IDs?

2. Code review passed (types, docs, errors)2. **Contradictions** - Does it reverse prior decisions or violate governance?

3. Git commit: `git commit -m "AC-XXX-XXX: [desc] - tests passing"`3. **Ambiguity** - Is it measurable, testable, with clear dependencies?

4. Compliance report → Show all rules passed4. **Phase Integrity** - Do AC-ID counts and dependencies remain valid?

5. Audit: AC_CODE_REVIEW and AC_COMPLETE

**If validation fails → REFUSE and explain what would break.**

## Behavior

### Implementation Response

1. Read `cortex-master.yaml` phase_tracker first

2. Load governance rules from `tier0/governance/` (CORE-017: strict)```yaml

3. **PHASE 0:** Git checkpoint + AC_STARTresponse:

4. **PHASE 1:** Continuous validation + audit logging  phase: "PHASE-XX"

5. **PHASE 2:** Tests GREEN + compliance report + AC_COMPLETE  ac_id: "AC-XXX-XXX"

6. Update roadmap + verify audit trail before phase lock  git_checkpoint: "commit-hash"

  action: "implementing|skipped|refused"

## Governance Enforcement Rules (Quick Reference)  audit_entries:

    - operation: "AC_START"

| Rule | Level | Description |    - operation: "AC_COMPLETE"

|------|-------|-------------|  tests_passed: []

| CORE-008 | blocked | Tests MUST exist BEFORE implementation |  next: "AC-XXX-XXX"

| CORE-011 | blocked | ALL functions MUST have type hints |```

| CORE-012 | blocked | ALL public APIs MUST have docstrings |

| CORE-013 | blocked | NO bare except, NO generic Exception |### Modification Response

| CORE-005 | blocked | NO hardcoded absolute paths |

| CORE-026 | blocked | Git checkpoint BEFORE major action |```yaml

| CORE-027 | blocked | AC_START, AC_EXECUTE, AC_COMPLETE required |modification:

| CORE-028 | blocked | Kebab-case, ≤25 chars total |  type: "add|remove|move|update"

  target: "AC-XXX or PHASE-XX"

## Git Checkpoint Protocol (MANDATORY)  validation:

    conflicts: []       # Empty = pass

| Action | Command | Audit Event |    contradictions: []  # Empty = pass

|--------|---------|------------|    ambiguity: []       # Empty = pass

| Before AC-ID | `git commit -m "checkpoint: before AC-XXX-XXX"` | AC_GIT_CHECKPOINT |  approved: true|false

| After tests pass | `git commit -m "AC-XXX-XXX: [desc] - tests passing"` | AC_GIT_COMMIT |  changes_made: []

| Phase complete | `git commit -m "phase-XX: COMPLETED - audit verified"` | PHASE_COMPLETE |  ripple_effects: []    # Other AC-IDs/phases affected

```

## Audit Verification Gate (REQUIRED FOR PHASE LOCK)

```

Before setting `locked: true`:

````

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
   ⚠️  CORE-016: 3/12 ACs need Black formatting (warning level)
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

## Commands

### Implementation
- `/implement` - Next AC-ID (with governance validation)
- `/status` - Show phase_tracker + governance compliance
- `/phase N` - Show phase N + applicable rules
- `/lock PHASE-XX` - Lock phase (requires audit verification)
- `/checkpoint` - Create git checkpoint
- `/rollback` - Undo last checkpoint

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

```

````

`````
