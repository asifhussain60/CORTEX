# 🤖 Autonomous Execution Mode

**⚠️ CRITICAL: This prompt is designed for FULLY AUTONOMOUS execution.**

---

## Execution Behavior

| Setting | Value | Description |
|---------|-------|-------------|
| **Auto-Proceed** | ✅ ENABLED | Phases execute sequentially without user confirmation |
| **Auto-Repair** | ✅ ENABLED | Issues are fixed immediately upon detection |
| **Auto-Commit** | ✅ ENABLED | Changes are committed to git after each phase |
| **Pause Points** | ❌ NONE | No user interaction required between phases |
| **Rollback** | ✅ AUTO | Failed phases trigger automatic rollback |

---

## ⛔ FORBIDDEN Behaviors in Autonomous Mode

**❌ NEVER DO THESE:**
- Ask "Should I proceed?" or "Do you want me to continue?"
- Wait for user confirmation before starting next phase
- Output "Ready for next phase?" messages
- Pause execution after discovery/reports
- Request approval for auto-repair actions
- Generate partial reports and stop

**✅ ALWAYS DO THESE:**
- Execute ALL 10 phases in sequence automatically
- Proceed to next phase immediately after current phase completes
- Auto-repair ALL detected issues without asking
- Commit changes after each phase automatically
- Generate final consolidated report ONLY at Phase 10 completion
- Show visual progress tracker at phase transitions

---

## Phase Transition Logic

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS EXECUTION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   START ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5       │
│               │           │           │           │           │             │
│               ▼           ▼           ▼           ▼           ▼             │
│           [auto]      [auto]      [auto]      [auto]      [auto]           │
│               │           │           │           │           │             │
│               └───────────┴───────────┴───────────┴───────────┘             │
│                                   │                                         │
│   Phase 6 ◄── Phase 7 ◄── Phase 8 ◄── Phase 9 ◄── Phase 10 ◄──┘           │
│      │           │           │           │           │                      │
│      ▼           ▼           ▼           ▼           ▼                      │
│   [auto]      [auto]      [auto]      [auto]    [FINAL]                    │
│                                                     │                       │
│                                                     ▼                       │
│                                           CONSOLIDATED REPORT               │
│                                                     │                       │
│                                                     ▼                       │
│                                                   END                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Auto-Transition Rules

**After EACH phase completion, IMMEDIATELY:**

1. **Render Progress Tracker** (visual ASCII progress bar)
2. **Log Phase Summary** (one-liner: `✅ Phase N complete: {summary}`)
3. **Start Next Phase** (no delay, no confirmation)
4. **On Error:** Auto-repair OR rollback OR skip with warning

**Phase Completion Template:**
```
✅ Phase {N} - {NAME}: Complete
   └─ Actions: {count} | Fixed: {fixed_count} | Skipped: {skipped_count}
   └─ Duration: {seconds}s
   └─ Auto-proceeding to Phase {N+1}...
```

| Phase | Progress | Status |
|-------|----------|--------|
| Phase {N} | `██████████` | 100% ✅ Complete |
| Phase {N+1} | `░░░░░░░░░░` | 0% 🔄 Starting |

---

## Error Handling in Autonomous Mode

| Error Type | Action | Continue? |
|------------|--------|-----------|
| **Non-Critical** | Log warning, continue | ✅ YES |
| **Critical (fixable)** | Auto-repair, retry | ✅ YES |
| **Critical (unfixable)** | Log error, skip phase | ✅ YES (with warning) |
| **Catastrophic** | Rollback, abort | ❌ NO |

**Catastrophic = Only if continuing would corrupt the system**

---

## Invocation

**Standard (autonomous):**
```
system maintenance
```

**With specific phases:**
```
system maintenance --phases 1,2,5
```

**Dry-run (no changes):**
```
system maintenance --dry-run
```
