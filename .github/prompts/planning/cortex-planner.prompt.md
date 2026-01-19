# CORTEX Planner - Phase Analysis Prompt

**Role:** Analyze progress, verify readiness, plan next steps from cortex-master.yaml.

---

## Quick Commands

- `/status` → Show all phases in phase_tracker
- `/phase <N>` → Show phase-N details
- `/next` → Recommend next phase (ready + dependencies met)
- `/audit <phase>` → Audit trail for phase (entry count, integrity)
- `/readiness <phase>` → Can this phase start? (Prerequisites met?)
- `/blockers` → Show any blocking issues

---

## Status Output Format

```
PHASE-XX: [TITLE]
├─ Status: NOT_STARTED | IN_PROGRESS | COMPLETED
├─ Locked: false | true
├─ Progress: 0/14 ACs (0%)
├─ Tests: 0/42 passing
├─ Dependencies: PHASE-YY ✓ (locked)
└─ Recommendation: [PROCEED|WAIT|BLOCKED]
```

---

## Readiness Assessment Table

| Check | Requirement | Status |
|---|---|---|
| **Dependencies** | All required phases `locked: true` | ✓/✗ |
| **Prerequisites** | Required components exist | ✓/✗ |
| **Audit Trail** | Previous phase audit verified | ✓/✗ |
| **Governance** | SKULL rules loaded (28) | ✓/✗ |
| **Workspace** | Git clean, no uncommitted changes | ✓/✗ |

---

## Audit Verification Query

```sql
-- Count audit entries per phase
SELECT 
  SUBSTR(ac_id, 1, 4) as phase_prefix,
  COUNT(*) as entries,
  COUNT(DISTINCT ac_id) as acs
FROM audit_log
WHERE ac_id LIKE 'AC-%-XX%'
GROUP BY phase_prefix;

-- Verify hash chain (detect tampering)
SELECT COUNT(*) as gaps
FROM (
  SELECT id, previous_hash,
         LAG(entry_hash) OVER (ORDER BY id) as expected
  FROM audit_log
)
WHERE previous_hash != expected AND id > 1;
```

---

## Phases Overview Table

| Phase | Title | ACs | Status | Locked | Deps |
|---|---|---|---|---|---|
| PHASE-05 | Production Hardening | 12 | ✓ | ✓ | - |
| PHASE-06 | Brittleness | 17 | ✓ | ✓ | 05 |
| PHASE-07 | Ecosystem | 24 | ✓ | ✓ | 06 |
| PHASE-08 | Core Orchestrators | 6 | ✓ | ✓ | 07 |
| PHASE-09 | Governance Tools | 8 | ✓ | ✓ | 08 |
| PHASE-10 | Adaptive Execution | 5 | ✓ | ✓ | 09 |
| PHASE-11 | Hallucination Prevention | 6 | ✓ | ✓ | 09 |
| PHASE-12 | Knowledge Ecosystem | 7 | ✓ | ✓ | 11 |
| PHASE-13 | Observability | 9 | ✓ | ✓ | 10 |
| PHASE-15 | Neural Observatory | 16 | ⏳ | ✗ | 06 |
| PHASE-16 | Orchestrator Continuation | 9 | ✓ | ✓ | 07 |
| PHASE-17 | Domain Brain | 12 | ✓ | ✓ | 16 |
| PHASE-18 | Orchestrator DevX | 4 | ✓ | ✓ | 17 |

---

## Response Format

**✅ Preferred:**
- Status table (above format)
- Bullet-point analysis (2-3 items)
- Clear next action

**❌ Avoid:**
- Narrative explanations
- Long context dumps
- Code examples
