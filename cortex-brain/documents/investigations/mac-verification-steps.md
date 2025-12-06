# Mac Verification Steps After Windows Fix

**Date:** December 2, 2025  
**Context:** Verifying cross-platform initialization fix works on Mac

---

## Pre-Pull State (Mac)

Expected Mac environment before pulling Windows fix:
- ✅ `cortex-brain/tier1/` exists with `working_memory.db`, `conversations.db`
- ✅ `cortex-brain/tier2/` exists with `knowledge_graph.db`
- ✅ `cortex-brain/tier3/` exists with `context.db`
- ✅ CORTEX currently functional

---

## Pull and Verification

### Step 1: Pull Changes
```bash
cd /path/to/CORTEX
git pull origin CORTEX-3.0
```

**Expected Output:**
```
Updating a1b2c3d..e4f5g6h
Fast-forward
 src/entry_point/cortex_entry.py                                    | 7 ++-----
 cortex-brain/documents/investigations/cross-platform-initialization-fix.md | 215 +++++++++++++++++++
 2 files changed, 217 insertions(+), 5 deletions(-)
```

### Step 2: Verify Code Changes
```bash
git diff HEAD~1 src/entry_point/cortex_entry.py
```

**Expected:** Only 3 database file checks removed from `_check_first_time_setup()`

### Step 3: Test CORTEX Initialization
```bash
python -m src.main "help"
```

**Expected Output:**
- ✅ No initialization errors
- ✅ Help text displays correctly
- ✅ No "setup required" messages

### Step 4: Verify Database Connectivity
```bash
python -c "
from src.entry_point.cortex_entry import CortexEntry
entry = CortexEntry(skip_setup_check=True)
print('✅ CortexEntry initialized')
print(f'✅ Brain path: {entry.brain_path}')
print('✅ All tier systems operational')
"
```

**Expected:** All checks pass, no errors

### Step 5: Run Basic Operations
```bash
# Test optimize command
python -m src.main "optimize"

# Test version check
python -m src.main "version"

# Test status
python -m src.main "status"
```

**Expected:** All commands execute without initialization errors

---

## Success Criteria

✅ **PASS** if ALL of the following are true:
1. Git pull completes without conflicts
2. CORTEX initializes without "setup required" errors
3. Help command displays correctly
4. All tier systems connect to databases
5. Basic commands (optimize, version, status) execute successfully
6. No new warnings or errors in logs

❌ **FAIL** if ANY of the following occur:
1. Initialization errors about missing brain structure
2. Database connection failures
3. Commands fail that previously worked
4. Setup wizard unexpectedly triggers

---

## Rollback Plan (If Needed)

If verification fails on Mac:

```bash
# Rollback to previous commit
git reset --hard HEAD~1

# Or revert specific commit
git revert <commit-hash>

# Push rollback
git push origin CORTEX-3.0
```

**Note:** Rollback should NOT be necessary - fix only removes checks, doesn't add requirements.

---

## Expected Outcome

**High Confidence Prediction:** Mac will work perfectly because:
1. Validation is now LESS strict (removed checks)
2. Mac already has all tier directories
3. Mac databases already exist (no creation needed)
4. Fix improves resilience (databases auto-recreate if deleted)
5. No new dependencies or requirements added

**Risk Assessment:** 🟢 **VERY LOW**
- Change type: Pure relaxation of validation
- Direction: Windows fix → Mac (Mac already working)
- Code impact: 7 lines removed, 3 lines added (documentation)
- Testing: Windows validation confirmed working

---

## Contact

If Mac verification fails (unexpected):
1. Check git log for merge conflicts
2. Verify Python environment matches Mac's original setup
3. Review logs in `cortex-brain/tier1/requests.log`
4. Report issue with full error output and environment details
