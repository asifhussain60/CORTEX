# CORTEX Prompts & Agents - Architecture Map

**Purpose:** Visual guide showing how prompts and agents work together with cortex-master.yaml

---

## User Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER COPILOT CHAT REQUEST                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌────────────┐   ┌──────────┐    ┌─────────────┐
    │ IMPLEMENT  │   │   PLAN   │    │   REVIEW    │
    │   NEW AC   │   │  PHASES  │    │  CODE QA    │
    └─────┬──────┘   └────┬─────┘    └──────┬──────┘
          │               │                 │
          ▼               ▼                 ▼
    ┌────────────────────────────────────────────────┐
    │         .github/prompts/                       │
    │                                                │
    │  cortex-builder.prompt.md                     │
    │  cortex-builder-continuation.prompt.md        │
    │  cortex-planner.prompt.md                     │
    │  cortex-gap-detection.prompt.md               │
    │  cortex-governance.prompt.md                  │
    │  cortex-review-*.prompt.md (4 files)          │
    └────────────┬───────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────────────┐
    │    .github/agents/ (Copilot tools)            │
    │                                                │
    │  cortex-builder.md                            │
    │  cortex-planner.md                            │
    │  cortex-gap-detection.md                      │
    │  cortex-review.md                             │
    └────────────┬───────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────────────┐
    │    _workspaces/roadmap/cortex-master.yaml     │
    │                                                │
    │  phase_tracker: Current phase status           │
    │  phases: Detailed AC specifications           │
    │  architecture_decisions: Design decisions     │
    └────────────┬───────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────────────┐
    │    cortex_brain/tier0/governance/              │
    │                                                │
    │  core-rules.yaml (28 SKULL rules)             │
    │  phase-enforcement-map.yaml                   │
    │  ac-validation-checklist.yaml                 │
    └────────────┬───────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────────────┐
    │    IMPLEMENTATION & GOVERNANCE ENFORCEMENT     │
    │                                                │
    │  Create AC-IDs with tests (TDD first)         │
    │  Log audit trail (AC_START→EXECUTE→COMPLETE) │
    │  Verify governance rules compliance           │
    │  Track in: cortex_brain/state/governance.db   │
    └────────────────────────────────────────────────┘
```

---

## Prompt Selection Matrix

| Scenario | Prompt | Agent |
|----------|--------|-------|
| **Start new AC-ID** | cortex-builder.prompt.md | cortex-builder.md |
| **Resume session** | cortex-builder-continuation.prompt.md | (no agent) |
| **Plan next phase** | cortex-planner.prompt.md | cortex-planner.md |
| **Check readiness** | cortex-planner.prompt.md | cortex-planner.md |
| **Find quality issues** | cortex-review-*.prompt.md | cortex-review.md |
| **Detect gaps** | cortex-gap-detection.prompt.md | cortex-gap-detection.md |
| **Verify compliance** | cortex-governance.prompt.md | cortex-review.md |

---

## Session Lifecycle

### Session 1: Start New Phase

```
1. User: "Start PHASE-15"
   → Load: cortex-planner.prompt.md
   → Check: Dependencies met, phase locked=false
   → Display: Phase spec + readiness table

2. User: "Implement AC-1501"
   → Load: cortex-builder.prompt.md
   → Check: Phase not locked, governance rules loaded
   → Execute: TDD → Implement → Audit → Commit
   → Display: AC status table

3. User: "Review code quality"
   → Load: cortex-review-*.prompt.md
   → Check: SKULL rules, brittleness, assumptions, etc
   → Display: Findings table
```

### Session 2: Resume (Hours Later)

```
1. User: "Continue where we left off"
   → Load: cortex-builder-continuation.prompt.md
   → Query: Last AC-ID, last commit, phase status
   → Display: 5-second resumption status table (NO context dump)
   → Ready: Start next AC-ID immediately

2. User: "Status"
   → Load: cortex-planner.prompt.md
   → Display: Current phase, progress (5/14 ACs), next action
```

---

## Data Flow

### Read Operations (No Side Effects)

```
cortex-master.yaml
  ├─ Read: phase_tracker → Current phase status
  └─ Read: phases.PHASE-XX → AC specifications

cortex_brain/tier0/governance/
  ├─ Read: core-rules.yaml → Governance rules
  └─ Read: phase-enforcement-map.yaml → Phase-specific rules

cortex_brain/state/governance.db
  ├─ Query: audit_log → Check AC lifecycle events
  └─ Query: audit_log → Verify hash chain integrity
```

### Write Operations (With Audit Trail)

```
AC Implementation:
  1. Log: AC_START (audit_log)
  2. Create: Test file
  3. Implement: Source code
  4. Run: Tests
  5. Log: AC_EXECUTE (audit_log)
  6. Commit: Git checkpoint
  7. Log: AC_COMPLETE (audit_log)
  8. Update: phase_tracker status
  9. Commit: Final state update
```

---

## Output Format Consistency

### All Prompts Follow This Pattern

```
## [SECTION TITLE]

✅ **Key Finding:** One-liner
• Detail (bullet 1)
• Detail (bullet 2)

| Table | Heading | When | Appropriate |
|-------|---------|------|-------------|
| Use | tables | for | multi-row |

**Next Action:** Single clear sentence
```

### Response Examples

**Example 1: Status Check**
```
PHASE-07: Ecosystem (24 ACs)
├─ Status: IN_PROGRESS
├─ Progress: 18/24 ACs (75%)
├─ Locked: false
└─ Recommendation: PROCEED with remaining ACs
```

**Example 2: Governance Check**
```
AC-007-003: GOVERNANCE COMPLIANCE

✅ CORE-008 (TDD) - Tests created before code
✅ CORE-011 (Types) - All functions typed
✅ CORE-012 (Docstrings) - Google-style docs present
⚠️  CORE-028 (Naming) - File name 31 chars (exceeds 25)

Action Required: Rename file to ≤25 chars before phase lock
```

**Example 3: Session Resumption**
```
═══════════════════════════════════════════════════════════════
║ SESSION RESUMPTION STATUS                                    ║
╠═══════════════════════════════════════════════════════════════╣
║ Phase: PHASE-15-NEURAL-OBSERVATORY                           ║
║ Status: IN_PROGRESS | 3/16 ACs completed (19%)              ║
║ Last Activity: AC-015-003 completed (4h ago)                ║
║ Last Commit: [abc1234] - "AC-015-003: complete"            ║
║ Next Action: AC-015-004 (ready to start)                   ║
╚═══════════════════════════════════════════════════════════════╝

→ Ready to implement AC-015-004
```

---

## Command Reference

### Universal Commands (All Prompts)

```
/status <phase>              → Show phase status
/next                        → Show next ready action
/readiness <phase>           → Check prerequisites
/audit <phase|ac-id>         → Show audit trail
/governance-check <phase>    → Verify SKULL compliance
/blockers                    → Show blocking issues
```

### Builder Specific

```
/implement <phase>           → Start implementing phase
/lock <phase>                → Mark phase complete
/checkpoint <message>        → Create git checkpoint
/audit-trail                 → Query governance.db
```

### Planner Specific

```
/plan                        → Show implementation plan
/progress                    → Show completion progress
/dependencies <ac-id>        → Show dependency graph
```

### Reviewer Specific

```
/gaps                        → Find design-build gaps
/compliance <phase>          → Compliance report
/violations <phase>          → Violations by severity
/assumptions                 → Hidden assumptions
/brittleness                 → Structural weaknesses
/debt                        → Technical debt
/hallucinations              → False claims
```

---

## File Organization

```
.github/
├── prompts/                    ← All prompt files (read by user)
│   ├── cortex-builder.prompt.md
│   ├── cortex-builder-continuation.prompt.md
│   ├── cortex-planner.prompt.md
│   ├── cortex-gap-detection.prompt.md
│   ├── cortex-governance.prompt.md
│   └── cortex-review-*.prompt.md (4 files)
│
├── agents/                     ← Agent definitions for Copilot tools
│   ├── cortex-builder.md
│   ├── cortex-planner.md
│   ├── cortex-gap-detection.md
│   └── cortex-review.md
│
├── PROMPTS-AGENTS-INDEX.md     ← This file
└── REFACTORING-SUMMARY-20260119.md

_workspaces/roadmap/
├── cortex-master.yaml          ← SSOT (v2.1)
├── phases/                     ← Phase specifications
├── reports/                    ← Generated phase reports (YAML)
└── issues/                     ← Gap findings (YAML)

cortex_brain/
├── tier0/governance/           ← Immutable governance rules
└── state/
    └── governance.db           ← Audit trail (SQLite)

docs/                           ← Documentation ONLY
```

---

## Governance Rules Consolidated

All prompts include quick reference to critical SKULL rules:

| Rule | Category | Check |
|------|----------|-------|
| CORE-001 | Incremental | <500 lines/turn |
| CORE-008 | TDD | Tests before code |
| CORE-011 | Types | All functions typed |
| CORE-012 | Docstrings | Google style |
| CORE-013 | Error Handling | No bare except |
| CORE-017 | Strict | No overrides |
| CORE-026 | Git | Checkpoint before action |
| CORE-027 | Audit | START→EXECUTE→COMPLETE |
| CORE-028 | Naming | Kebab-case ≤25 chars |

---

## Verification Checklist

Before using any prompt:

- [x] File exists in `.github/prompts/` or `.github/agents/`
- [x] No `.md` narrative sections (tables + bullets only)
- [x] Governance rules table present
- [x] Command examples provided
- [x] Output format shown as table
- [x] File placement policy documented
- [x] Links to cortex-master.yaml present
- [x] <100 lines for conciseness
- [x] Session continuation supported (continuation.prompt.md)

---

## Next Steps

1. ✅ All prompts operational
2. ✅ All agents defined
3. Test continuation workflow
4. Verify governance enforcement
5. Monitor audit trail integrity
6. Clean up old docs/ prompt files (optional)

---

**Version:** 2.1 (Refactored)  
**Status:** Ready for use  
**Last Updated:** 2026-01-19
