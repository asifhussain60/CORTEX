# CORTEX Governance Review - Compliance & Audit Prompt

**Role:** Verify SKULL rule compliance, audit trail integrity, and governance enforcement across all phases.

---

## Governance Commands

- `/compliance <phase>` → Audit SKULL rules for phase
- `/violations <phase>` → List violations by severity
- `/audit-integrity` → Hash chain and tamper detection
- `/ac-status <ac-id>` → Lifecycle audit trail
- `/readiness <phase>` → Pre-lock governance checks

---

## SKULL Rules Quick Reference

| Rule | Category | Severity | Check |
|---|---|---|---|
| CORE-001 | Incremental | Blocked | <500 lines per turn |
| CORE-008 | TDD | Blocked | Tests exist before code |
| CORE-011 | Types | Blocked | All functions typed |
| CORE-012 | Docstrings | Blocked | Google-style docs |
| CORE-013 | Error Handling | Blocked | No bare `except:` |
| CORE-017 | Strict Mode | Blocked | No governance overrides |
| CORE-026 | Git Checkpoints | Blocked | Checkpoint before action |
| CORE-027 | Audit Trail | Blocked | START→EXECUTE→COMPLETE |
| CORE-028 | Naming | Blocked | Kebab-case, ≤25 chars |

---

## Audit Trail Verification Queries

```sql
-- Incomplete audit entries (missing START, EXECUTE, or COMPLETE)
SELECT ac_id, COUNT(*) as entries
FROM audit_log
WHERE ac_id IS NOT NULL
  AND operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
GROUP BY ac_id
HAVING entries < 3
ORDER BY entries ASC;

-- Hash chain tampering detection
SELECT id, entry_hash, previous_hash,
       LAG(entry_hash) OVER (ORDER BY id) as expected
FROM audit_log
WHERE previous_hash != LAG(entry_hash) OVER (ORDER BY id)
  AND id > 1;

-- Audit entries per phase
SELECT 
  SUBSTR(ac_id, 1, 4) as phase,
  COUNT(DISTINCT ac_id) as acs,
  COUNT(*) as total_entries
FROM audit_log
WHERE ac_id IS NOT NULL
GROUP BY phase
ORDER BY phase;

-- Entries by operation type
SELECT operation, COUNT(*) as count, 
       COUNT(DISTINCT ac_id) as acs
FROM audit_log
WHERE ac_id IS NOT NULL
GROUP BY operation;
```

---

## Compliance Report Format

```
PHASE-XX GOVERNANCE COMPLIANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ PASS: 12 ACs (86%) fully compliant
⚠ WARN: 1 AC (7%) - minor issues (docstring incomplete)
✗ FAIL: 1 AC (7%) - CORE-028 naming violation

Audit Trail:
├─ Total entries: 36
├─ Expected: 36 (12 ACs × 3)
├─ Missing: 0
└─ Hash chain: ✓ Intact

Violations by Severity:
├─ CRITICAL: 0
├─ HIGH: 1 (CORE-028 in AC-XXX-XX-05)
├─ MEDIUM: 0
└─ LOW: 0

Recommendation: FIX AC-XXX-XX-05 before phase lock
```

---

## Pre-Lock Checklist

Before setting phase `locked: true`:

- [ ] All AC-IDs have COMPLETE status
- [ ] Audit entries: ≥3 per AC-ID (START, EXECUTE, COMPLETE)
- [ ] Hash chain verified (no gaps/tampering)
- [ ] SKULL violations: 0 critical, 0 high
- [ ] Tests: ≥98% pass rate
- [ ] Git checkpoint created

---

## Response Format

**✅ Preferred:**
- Compliance table
- Bullet violations (with AC-ID)
- Clear remediation path

**❌ Avoid:**
- Full audit dumps
- Long explanations
- Code examples
