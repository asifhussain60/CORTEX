# CORTEX Phase 4 Quick Reference - New Chat Session

## Start Here

In a new chat session, begin with:

```
I need to continue CORTEX Phase 4 execution. Current status:
- Phase 4 Step 1 COMPLETE: 80/137 ACs verified (62% coverage)
- Phase 4 Step 2 READY: 30 ACs to mark (pattern matching)
- Phase 4 Step 3 READY: 25 ACs to mark (targeted creation)
- Time to 100%: ~40 minutes

Load /Users/asifhussain/PROJECTS/CORTEX/docs/PHASE-4-CONTINUATION-PROMPT.md
for full context and execution templates.
```

## Quick Status Check

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Verify git state
git log --oneline -3
git status

# Check database
sqlite3 cortex-brain/state/governance.db \
  "SELECT COUNT(*) as entries, (SELECT COUNT(DISTINCT ac_id) FROM audit_log WHERE operation='AC_COMPLETE') as acs FROM audit_log;"
```

Expected output:
- Latest commit: BRITTLE markers
- Entries: ~1,551+ (started at 1,494)
- ACs: ~80 (was 68 after Phase 3)

## Quick Execution

### Phase 4 Step 2 (30 ACs)
```bash
/Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python << 'EOF'
import subprocess
from pathlib import Path

# Clear locks
import glob, os
for lf in glob.glob('/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/state/governance.db-*'):
    try: os.remove(lf)
    except: pass

# Run pattern matching tests
test_files = [
    "tests/unit/test_ac_domain_mapper.py",
    "tests/unit/test_governance_registry.py",
    "tests/unit/test_planning_orchestrator.py",
    "tests/unit/test_rule_evaluator.py",
]

venv = Path("/Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python")
for tf in test_files:
    subprocess.run([str(venv), "-m", "pytest", tf, "-q", "--tb=no"],
                   cwd="/Users/asifhussain/PROJECTS/CORTEX", timeout=60)

print("✅ Phase 4 Step 2 complete - check database")
EOF
```

### Phase 4 Step 3 (25 ACs)
```bash
# After Step 2, repeat pattern for remaining 25 ACs
# See PHASE-4-CONTINUATION-PROMPT.md for Step 3 template
```

## Key Files

| File | Purpose |
|------|---------|
| `docs/PHASE-4-CONTINUATION-PROMPT.md` | Full context & templates (START HERE) |
| `docs/PHASE-4-EXECUTION-PLAN.md` | Overall Phase 4 strategy |
| `docs/PHASE-3-GAP-ANALYSIS-REPORT.md` | Gap analysis (69 missing ACs) |
| `cortex-brain/state/governance.db` | Audit database |

## Database Lock Safeguard

**ALWAYS do this before test execution:**
```bash
rm -f cortex-brain/state/governance.db-wal
rm -f cortex-brain/state/governance.db-shm
```

## Coverage Tracking

```sql
-- After each step, run this query
SELECT 
  COUNT(DISTINCT ac_id) as acs_verified,
  COUNT(*) as total_entries,
  ROUND(COUNT(DISTINCT ac_id) * 100.0 / 137, 1) as coverage_percent
FROM audit_log
WHERE operation = 'AC_COMPLETE' AND ac_id IS NOT NULL;
```

Expected progression:
- After Step 1: 80 ACs (62%)
- After Step 2: 112 ACs (82%)
- After Step 3: 137 ACs (100%) ✓

## Git Commits

After each step:
```bash
git add -A
git commit -m "Phase 4 Step X: Applied YY markers - ZZ% coverage"
git push origin CORTEX6
```

## Verification at 100%

```bash
# All 137 ACs should have evidence
sqlite3 cortex-brain/state/governance.db \
  "SELECT ac_id, COUNT(*) FROM audit_log WHERE operation='AC_COMPLETE' GROUP BY ac_id ORDER BY ac_id" | wc -l
# Should show: 137
```

---

**In new session:** Reference `PHASE-4-CONTINUATION-PROMPT.md` for full details and execution templates.

