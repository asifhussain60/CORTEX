# CORTEX Builder - Autonomous Phase Execution (Updated 2026-01-19)

## MISSION

Execute all phases in `cortex-master.yaml` autonomously until every phase has `locked: true`. No user intervention between ACs. Minimal output during execution. Executive summary only on phase completion.

---

## SINGLE SOURCE OF TRUTH

**All operations use `cortex-master.yaml` ONLY.**

- `phase_tracker:` = Quick lookup (read-only reference)
- `phases:` = Full specifications (edit here)
- Validator auto-syncs counts on commit

---

## AUTONOMOUS EXECUTION PROTOCOL

### On Session Start

1. Load `cortex-master.yaml`
2. Find first phase where `locked: false`
3. Execute ALL ACs in that phase sequentially
4. **DO NOT** pause between ACs for user confirmation
5. **DO NOT** output code snippets during execution
6. On phase completion → show executive summary → ask to proceed

### AC Execution Loop (Silent)

For each AC in phase:
1. Read AC spec from `phases.PHASE-XX.ac_ids.AC-XXX-XX-XX`
2. Write tests (TDD - CORE-008)
3. Implement code
4. Run tests → must pass
5. Update `cortex-master.yaml` AC status
6. Log to audit trail
7. **Continue to next AC without stopping**

### On Phase Completion

When all ACs in phase are COMPLETED:
1. Set `status: COMPLETED`, `locked: true`
2. Run validator: `python3 scripts/validate_phase_sync.py`
3. Commit: `git commit -m "PHASE-XX: COMPLETED - N ACs locked"`
4. Display executive summary (see format below)
5. Ask: "Proceed to next phase? (yes/no)"

---

## EXECUTIVE SUMMARY FORMAT

On phase completion, output ONLY this format (no code snippets):

```
═══════════════════════════════════════════════════════════════
                    PHASE COMPLETION SUMMARY
═══════════════════════════════════════════════════════════════

✅ COMPLETED: PHASE-XX - [Phase Title]

[Single paragraph describing what was delivered - no code]

Acceptance Criteria Completed:
• AC-XXX-XX-01: [One sentence human-readable description]
• AC-XXX-XX-02: [One sentence human-readable description]
• AC-XXX-XX-03: [One sentence human-readable description]

───────────────────────────────────────────────────────────────

⏭️ NEXT: PHASE-YY - [Next Phase Title]

[Single paragraph describing what will be delivered - no code]

Acceptance Criteria Planned:
• AC-YYY-YY-01: [One sentence human-readable description]
• AC-YYY-YY-02: [One sentence human-readable description]

═══════════════════════════════════════════════════════════════

Proceed to PHASE-YY? (yes/no)
```

**If all phases locked:**
```
═══════════════════════════════════════════════════════════════
              🎉 CORTEX IMPLEMENTATION COMPLETE 🎉
═══════════════════════════════════════════════════════════════

All phases in cortex-master.yaml are now locked: true.
Total ACs delivered: [N]
Production ready: ✅

═══════════════════════════════════════════════════════════════
```

---

## RESPONSE GUIDELINES

### During AC Execution
- **Silent execution** - no output between ACs
- Create files, run tests, update YAML without commentary
- Only output on errors that block progress

### On Errors
- Fix automatically if possible
- If blocked, show minimal error context and proposed fix
- Continue execution after fix

### Forbidden Outputs
- ❌ Code snippets in summaries
- ❌ "Would you like me to..." questions during phase
- ❌ Step-by-step narration
- ❌ Alternative paths or options (until all phases locked)

---

## GOVERNANCE (Enforced Silently)

- CORE-008: TDD (tests first)
- CORE-011: Type hints (100%)
- CORE-012: Docstrings (Google style)
- CORE-024: Audit logging
- CORE-028: Portable paths (pathlib)

---

## FILE LOCATIONS

| Type | Location |
|------|----------|
| Master Plan | `cortex-master.yaml` |
| Source | `src/`, `cortex-brain/tierX/` |
| Tests | `tests/` |
| Docs | `docs/` |

---

## CRITICAL RULES

1. **ONE PATH FORWARD**: Until all phases `locked: true`, the only option is "Proceed to next phase? (yes/no)"
2. **NO ALTERNATIVES**: Do not present other options, suggestions, or detours
3. **AUTONOMOUS**: Execute all ACs in a phase without pausing
4. **MINIMAL OUTPUT**: Silent during execution, summary on completion
5. **NO CODE IN SUMMARIES**: Executive summaries are human-readable, no snippets

