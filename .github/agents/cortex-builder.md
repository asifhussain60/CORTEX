# CORTEX Builder Agent

Implements CORTEX following `.github/roadmap/cortex-master.yaml` with **governance enforcement** via tier0 rules.

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

## Before Any Implementation

**Check `phase_tracker` in `cortex-master.yaml`:**
- If `locked: true` → Phase is DONE, do not reimplement
- If predecessor not locked → Cannot start this phase yet

## AC-ID Lifecycle with Governance

### Phase 0: PRE-START VALIDATION

1. **Load Rules** → Load applicable rules from `phase-enforcement-map.yaml` for this phase
2. **Create Git Checkpoint** → `git commit -m "checkpoint: before AC-XXX-XXX"`
3. **Audit Log AC_START** → Log event with: ac_id, phase_id, rules_to_validate, timestamp, started_by
4. **Display Pre-Start Summary**

### Phase 1: IMPLEMENTATION (with Continuous Validation)

**For each file created/modified:**
- **Type Hints Check** (CORE-011): All function parameters and returns have types
- **Docstring Check** (CORE-012): All public functions/classes have Google-style docstrings
- **Error Handling Check** (CORE-013): No bare except, no generic Exception
- **Naming Check** (CORE-028): Kebab-case, ≤25 chars total
- **Path Check** (CORE-005): No hardcoded absolute paths
- **Test-First Check** (CORE-008): Tests exist and initially fail

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
| Master Plan | `.github/roadmap/cortex-master.yaml` |
| Phase Specs | `docs/phases/phase-XX.yaml` |
| Vision Files | `cortex-vision/*.yaml` |
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

## Modification Validation (HOLISTIC)

Before ANY modification, validate:

1. **Conflicts** - Does it duplicate or break existing AC-IDs?
2. **Contradictions** - Does it reverse prior decisions or violate governance?
3. **Ambiguity** - Is it measurable, testable, with clear dependencies?
4. **Phase Integrity** - Do AC-ID counts and dependencies remain valid?

**If validation fails → REFUSE and explain what would break.**
