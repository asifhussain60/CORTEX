# Multi-Machine Alignment Guide

**Version:** 1.0  
**Author:** Asif Hussain  
**Purpose:** Keep CORTEX aligned across multiple development machines  
**Status:** PRODUCTION

---

## Overview

When working with CORTEX across multiple machines (desktop, laptop, server), each machine needs proper setup to maintain alignment and avoid unwiring after git operations.

---

## Problem: Alignment Unwiring Across Machines

**What Happens Without Protection:**

```
Machine A:
1. Run align → alignment-state.json created
2. Git commit → State committed
3. Git push → State pushed to remote

Machine B:
1. Git pull → Remote state overwrites local
2. Run align → Full scan (slow) because checksums don't match Machine B's files
3. Local state diverges from remote
4. Next pull → Merge conflict or lost state
```

**Root Cause:**
- Alignment state contains machine-specific file checksums
- Machine A's checksums don't match Machine B's files
- State should be machine-local, not shared via git

---

## Solution: Machine-Local Alignment State

### Step 1: Add `.gitignore` Entry

**What:** Prevent alignment-state.json from being committed  
**Why:** Each machine should maintain its own state  
**Where:** Repository root `.gitignore`

```bash
# Navigate to CORTEX root
cd /path/to/CORTEX

# Add to .gitignore (if not already present)
echo "cortex-brain/admin/alignment-state.json" >> .gitignore
```

**Verification:**
```bash
git status
# Should NOT show alignment-state.json as modified
```

---

### Step 2: Initial Alignment on Each Machine

**Run on EVERY machine where you work with CORTEX:**

```bash
# Navigate to CORTEX root
cd /path/to/CORTEX

# Run full alignment
python -m src.operations.align

# Expected output:
# ✅ System healthy (8/8 checks passed)
# 📝 Alignment state saved
# 🔄 Full scan (15.2s, 92 features checked)
```

**What This Does:**
- Creates machine-specific `alignment-state.json`
- Computes SHA256 checksums for all CORTEX files
- Stores baseline for incremental scans
- File remains local (not committed)

---

### Step 3: Verify Machine-Specific Configuration

**Check `cortex.config.json` has your machine hostname:**

```json
{
  "machines": {
    "YOUR-HOSTNAME": {
      "rootPath": "D:/PROJECTS/CORTEX",  // Windows
      "brainPath": "D:/PROJECTS/CORTEX/cortex-brain"
    },
    "YOUR-LAPTOP": {
      "rootPath": "/Users/you/projects/CORTEX",  // macOS
      "brainPath": "/Users/you/projects/CORTEX/cortex-brain"
    }
  }
}
```

**Get Your Hostname:**
```powershell
# Windows PowerShell
$env:COMPUTERNAME

# macOS/Linux
hostname
```

**If Missing:** Add your machine's entry to `cortex.config.json`

---

### Step 4: Post-Pull Alignment

**After every `git pull`, run alignment:**

```bash
# Pull latest changes
git pull origin CORTEX-3.0

# Re-align system
python -m src.operations.align

# Expected output:
# 🔄 Incremental scan (2.1s, 3 features checked, 89 skipped)
```

**Why This Works:**
- Local state tracks your machine's file checksums
- Incremental scan only validates changed files
- Fast (2s vs 15s full scan)
- No merge conflicts with alignment state

---

## Standard Workflow Across Machines

### Machine A (Primary Development)

```bash
# Make changes
git add src/operations/new_feature.py
git commit -m "feat: add new feature"

# Run alignment
python -m src.operations.align
# ✅ System healthy (8/8 checks passed)
# 🔄 Incremental scan (2.3s, 1 feature checked)

# Push changes
git push origin CORTEX-3.0
```

**Note:** Alignment state stays local (not pushed)

---

### Machine B (Secondary Development)

```bash
# Pull changes from Machine A
git pull origin CORTEX-3.0
# remote: Compressed objects: 100% (5/5), done.
# Updating abc123..def456

# Run alignment
python -m src.operations.align
# ✅ System healthy (8/8 checks passed)
# 🔄 Incremental scan (2.1s, 1 feature checked)

# Continue work...
```

**Note:** Machine B's alignment state remains independent

---

## Verification Checklist

Run this on EACH machine:

```bash
# 1. Check .gitignore contains alignment-state.json
grep "alignment-state.json" .gitignore
# Expected: cortex-brain/admin/alignment-state.json

# 2. Verify state file exists locally
ls cortex-brain/admin/alignment-state.json
# Expected: File found

# 3. Verify state file NOT staged
git status
# Expected: alignment-state.json NOT in "Changes to be committed"

# 4. Run alignment
python -m src.operations.align
# Expected: ✅ System healthy

# 5. Check state file modified time (should be recent)
ls -l cortex-brain/admin/alignment-state.json
# Expected: Timestamp = now
```

---

## Troubleshooting

### Issue: Alignment state keeps getting committed

**Symptom:** `git status` shows alignment-state.json as modified

**Solution:**
```bash
# Remove from staging
git reset HEAD cortex-brain/admin/alignment-state.json

# Verify .gitignore entry
grep "alignment-state.json" .gitignore

# If missing, add it
echo "cortex-brain/admin/alignment-state.json" >> .gitignore
git add .gitignore
git commit -m "chore: ignore alignment-state.json"
```

---

### Issue: Slow alignment after pull

**Symptom:** Alignment takes 15s instead of 2s

**Cause:** Local state file corrupted or missing

**Solution:**
```bash
# Delete corrupted state
rm cortex-brain/admin/alignment-state.json

# Run full alignment (rebuilds state)
python -m src.operations.align
# Expected: 🔄 Full scan (15.2s)

# Next run should be fast
python -m src.operations.align
# Expected: 🔄 Incremental scan (2.1s)
```

---

### Issue: Merge conflict on alignment-state.json

**Symptom:** Git merge shows conflict on alignment-state.json

**Cause:** File was committed before .gitignore was updated

**Solution:**
```bash
# Accept local version (keep your machine's state)
git checkout --ours cortex-brain/admin/alignment-state.json

# Mark as resolved
git add cortex-brain/admin/alignment-state.json

# Ensure .gitignore updated
echo "cortex-brain/admin/alignment-state.json" >> .gitignore
git add .gitignore

# Complete merge
git commit -m "chore: resolve alignment-state conflict, add to .gitignore"
```

---

### Issue: Different machines show different health status

**Symptom:** Machine A passes all checks, Machine B fails some

**Cause:** Machine-specific environment differences

**Solution:**
```bash
# On failing machine, run verbose align
python -m src.operations.align --verbose

# Check for environment issues:
# - Python version (requires 3.8+)
# - Missing dependencies
# - Corrupted databases
# - Invalid configuration

# Fix environment, then re-align
python -m src.operations.align
```

---

## Best Practices

### 1. Run Align After Every Pull
```bash
# Create git alias for pull + align
git config alias.syncalign '!git pull && python -m src.operations.align'

# Usage
git syncalign
```

### 2. Check Alignment Before Push
```bash
# Ensure system healthy before pushing changes
python -m src.operations.align && git push
```

### 3. Weekly Full Alignment
```bash
# Force full scan weekly to catch drift
python -m src.operations.align --full

# Or via cron (Linux/macOS)
0 9 * * 1 cd /path/to/CORTEX && python -m src.operations.align --full
```

### 4. Monitor Alignment Performance
```bash
# Check alignment state metrics
cat cortex-brain/admin/alignment-state.json | jq '.performance_metrics'

# Expected output:
# {
#   "last_run_duration_seconds": 2.1,
#   "features_checked": 3,
#   "features_skipped": 89,
#   "cache_hit_rate": 0.967
# }
```

---

## Migration: Existing Machines

If alignment-state.json was previously committed:

```bash
# 1. Remove from git tracking (keep local file)
git rm --cached cortex-brain/admin/alignment-state.json

# 2. Add to .gitignore
echo "cortex-brain/admin/alignment-state.json" >> .gitignore

# 3. Commit the change
git add .gitignore
git commit -m "chore: make alignment-state machine-local"

# 4. Push to all machines
git push origin CORTEX-3.0

# 5. On other machines, pull and verify
git pull
git status  # Should NOT show alignment-state.json
```

---

## Quick Reference

| Command | Purpose | When |
|---------|---------|------|
| `python -m src.operations.align` | Incremental alignment | After pull, daily |
| `python -m src.operations.align --full` | Full alignment | Weekly, after major changes |
| `git status` | Check if state staged | Before commit |
| `grep alignment-state.json .gitignore` | Verify ignore entry | Setup, troubleshooting |
| `rm cortex-brain/admin/alignment-state.json` | Reset state | Corruption, major refactor |

---

## Summary

**Key Principles:**
1. ✅ Alignment state is **machine-local** (not shared via git)
2. ✅ Each machine maintains **independent checksums**
3. ✅ Run align **after every pull** for fast incremental checks
4. ✅ Add to `.gitignore` to prevent commits

**Performance:**
- Initial alignment: 15s (full scan, builds state)
- Incremental alignment: 2s (97% cache hit rate)
- After pull: 2-3s (only checks changed files)

**Result:**
- ✅ No alignment unwiring across machines
- ✅ Fast incremental scans (650% faster)
- ✅ No merge conflicts on alignment state
- ✅ Independent machine health tracking

---

## Related Documentation

- `alignment-state-protection.md` - Auto-commit implementation (deprecated approach)
- `.gitignore` - Repository ignore rules
- `cortex.config.json` - Machine-specific configuration
- `src/operations/modules/admin/align_utility.py` - Alignment implementation
