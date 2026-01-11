# Evidence Validation Quick Reference Card

**Purpose:** Daily validation of CORTEX 6.0 status claims  
**Principle:** "Implemented" = Tests Pass + Audit Evidence

---

## ⚡ Quick Status Check (30 seconds)

```bash
# Run validator
python3 scripts/audit_based_evidence_validator.py

# Check verification rate (should be ≥ 80%)
# Current: 56% (30/53 AC-IDs verified)
```

**Green:** ≥ 80% verification  
**Yellow:** 60-79% verification  
**Red:** < 60% verification ❌ (current state)

---

## 📊 Current Status (2026-01-11)

**Total AC-IDs:** 102  
**Verified:** 30 (29% of total, 56% of claimed)  
**Claimed:** 53  
**Gap:** 23 false positives

### By Phase:
- ✅ Phase 1: 44% (15/34) - Accurate
- ✅ Phase 1.5: 33% (1/3) - Accurate  
- ✅ Phase 2: 47% (14/30) - Accurate
- ❌ Phase 3: 0% (0/23) - Inflated to 100%
- ❌ Phase 4+: 0% (0/11) - Inflated to 100%

---

## 🎯 What Percentage of AC Has Been Met?

### Answer: **29% of total requirements (30/102)**

**Breakdown:**
- 30 AC-IDs have passing tests ✅
- 23 AC-IDs claimed but no tests ❌
- 49 AC-IDs not started yet ⏳

**To reach 80% target:**
- Need 82 AC-IDs verified
- Gap: 52 more AC-IDs
- Est. timeline: 8 weeks @ 1 AC-ID/day

---

## 🔍 Validation Commands

### Full Validation
```bash
python3 scripts/audit_based_evidence_validator.py
```

### Fix Tracker (Remove False Positives)
```bash
python3 scripts/audit_based_evidence_validator.py --fix
```

### Check Single AC-ID
```bash
python3 -m pytest tests/ -k "AC-AUDIT-001" -v
```

### Audit Log Query
```bash
sqlite3 cortex-brain/database/governance.db \
  "SELECT * FROM audit_log WHERE metadata LIKE '%AC-AUDIT-001%'"
```

### Sync Dashboard
```bash
python3 scripts/sync_plan_viewer_data.py
```

---

## ✅ Evidence Requirements

**For AC-ID to be "Verified":**

1. **Implementation file exists** (src/)
2. **Test file exists** (tests/)
3. **Test has marker:** `@pytest.mark.ac_id("AC-XXX-NNN")`
4. **Test passes:** `pytest -k {ac_id}` → PASSED
5. **Audit log entry:** governance.db has TEST_EXECUTION record

**Minimum:** #1 + #2 + #4 (File + Test + Pass)  
**Preferred:** All 5 (includes audit trail)

---

## 🚨 Red Flags

❌ Tracker shows 100% but tests failing  
❌ AC-ID in "implemented" without test file  
❌ Test exists but never executed  
❌ Audit DB missing/empty  
❌ Verification rate dropping over time

---

## 🔧 Quick Fixes

### False Positive Detected
```bash
# Remove from tracker
python3 scripts/audit_based_evidence_validator.py --fix

# Implement properly
python3 -m src.main "implement AC-XXX-NNN using TDD"
```

### Missing Audit Logs
```bash
# Re-run tests with audit logging
pytest tests/ -v --log-cli-level=INFO

# Check if logs generated
ls -lh cortex-brain/database/governance.db
```

### Tracker Out of Sync
```bash
# Regenerate from evidence
python3 scripts/audit_based_evidence_validator.py --fix
python3 scripts/sync_plan_viewer_data.py
```

---

## 📈 Daily Workflow

### Before Starting Work
1. Run validator → Know current baseline
2. Check which AC-IDs need work
3. Pick highest priority unverified AC-ID

### During Implementation
4. Write test first (TDD)
5. Add `@pytest.mark.ac_id("AC-XXX-NNN")`
6. Implement until test passes
7. Run validator → Confirm verification

### Before Committing
8. Run validator → No decrease in rate
9. Run tests → All still passing
10. Commit with AC-ID in message

---

## 🎓 Quick Tips

💡 **Never manually edit tracker** → Use `--fix` flag  
💡 **Tag all tests** → Future validation automatic  
💡 **Run validator daily** → Catch inflation early  
💡 **Evidence > Claims** → Show, don't tell  
💡 **Audit everything** → Historical proof matters

---

## 📞 When to Escalate

**Verification rate < 60%** → Review all "implemented" claims  
**Phase shows 100% but 0 tests** → Immediate fix required  
**Audit DB missing** → Restore/rebuild critical  
**Multiple sources diverge** → Data integrity issue

---

## 🔗 Key Files

| File | Purpose |
|------|---------|
| `scripts/audit_based_evidence_validator.py` | Main validator |
| `.github/prompts/EVIDENCE-VALIDATOR.prompt.md` | Full protocol |
| `cortex-brain/tier1/tracking/progress-tracker.json` | Status tracker |
| `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` | AC registry |
| `cortex-brain/documents/validation/evidence-validation-executive-summary-2026-01-11.md` | Detailed report |

---

**Last Updated:** 2026-01-11  
**Next Review:** 2026-01-18  
**Owner:** Asif Hussain
