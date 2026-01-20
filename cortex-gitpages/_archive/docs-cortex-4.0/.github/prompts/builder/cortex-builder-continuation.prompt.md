# CORTEX Builder Continuation - Session Pickup Prompt

**Role:** Immediately resume previous session WITHOUT verbosity. Pickup exactly where left off.

---

## Session Resumption Protocol

**First action on session start:**

1. Load `_workspaces/roadmap/cortex-impl-map.yaml` → implementation status
2. Find phase with status = `IN_PROGRESS` OR last completed phase
3. Load corresponding `phases/phase-XX.yaml`
4. Query audit trail: `SELECT MAX(timestamp) FROM audit_log WHERE ac_id LIKE 'AC-XXX-%'`
5. **Display status table** (see below) - 5 seconds max
6. **Resume immediately** - no preamble

---

## Resumption Status Table

```
╔════════════════════════════════════════════════════════════════╗
║ SESSION RESUMPTION STATUS                                      ║
╠════════════════════════════════════════════════════════════════╣
║ Current Phase: PHASE-XX [TITLE]                               ║
║ Status: IN_PROGRESS | ACs: 5/14 completed (36%)               ║
║ Last Activity: AC-XXX-XX-05 (12h ago)                         ║
║ Last Commit: [hash] - "AC message"                            ║
║ Audit Trail: ✓ 15 entries logged                              ║
╠════════════════════════════════════════════════════════════════╣
║ NEXT ACTION: AC-XXX-XX-06 (Ready to start)                    ║
╚════════════════════════════════════════════════════════════════╝
```

---

## Immediate Actions

**NO context dump. Just do this:**

1. **Load test file** from previous AC-ID → verify tests passing
2. **Read AC spec** for NEXT AC-ID from phase-XX.yaml
3. **Create git checkpoint** (if not done): `git commit -m "checkpoint: resume AC-XXX-XX-06"`
4. **Start implementation** - no summary needed

---

## Output Format During Continuation

**ONLY display:**
- AC-ID number and title
- What's being implemented (1 line)
- Status after each step (passing/failing)
- Next AC-ID when current is done

**DO NOT display:**
- Roadmap summaries
- Governance rule recaps
- Elaborate context
- Multi-paragraph explanations

---

## Context Queries (Silent)

Use these when needed, output only results:

```sql
-- What was I implementing?
SELECT ac_id, description FROM audit_log 
WHERE operation = 'AC_EXECUTE' 
ORDER BY timestamp DESC LIMIT 1;

-- Was it completed?
SELECT COUNT(*) FROM audit_log 
WHERE ac_id = 'AC-XXX-XX-XX' 
AND operation IN ('AC_COMPLETE');

-- What's the current hash chain state?
SELECT id, entry_hash, previous_hash FROM audit_log 
ORDER BY id DESC LIMIT 3;
```

---

## Re-engagement Triggers

Resume full context ONLY if:
- User asks explicit question (not implicit continuation)
- Phase changed since last session
- New phase requirements loaded
- Error detected in audit trail

Otherwise → **Continue silently as if never paused**
