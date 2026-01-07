# Git Sync Instructions - Active Plans Cleanup

**Date:** January 6, 2026  
**Commit:** Active plans consolidation - 6 plans → 2 plans  
**Impact:** Multi-machine sync requires no manual intervention

---

## 🎯 What Changed

**This commit consolidates CORTEX active plans:**
- ✅ **cortex5-enhancement-epic** - Main CORTEX 5.0 enhancement plan (renamed from cortex5-snowball)
- ✅ **html-glassmorphism-alignment** - HTML documentation standardization
- 🗂️ **4 plans archived** - Moved to `cortex-brain/archives/plans/archived-2026-01-06-cleanup/`

---

## 📋 For Machines Pulling This Commit

### Automatic Actions (No User Intervention)

When you run `git pull origin CORTEX-5.0`, Git will automatically:

1. ✅ **Move 4 folders** from `active/` to `archives/` (Git tracks as renames)
2. ✅ **Rename 1 folder** (`cortex5-snowball` → `cortex5-enhancement-epic`)
3. ✅ **Create archive manifest** at `archives/plans/archived-2026-01-06-cleanup/ARCHIVE-MANIFEST.md`
4. ✅ **Update all file references** (Git handles path changes)

**Result:** Your local `cortex-brain/documents/planning/active/` will have exactly 2 folders.

---

## 🔍 Verification After Pull

**Check active plans folder:**
```bash
ls -1 cortex-brain/documents/planning/active/
```

**Expected output:**
```
cortex5-enhancement-epic/
html-glassmorphism-alignment/
```

**Check archives:**
```bash
ls -1 cortex-brain/archives/plans/archived-2026-01-06-cleanup/
```

**Expected output:**
```
a19-cortex5-snowball/
ARCHIVE-MANIFEST.md
cortex5-remediation/
cortex5-snowball-enhancement-implement/
plan-caf79368-0d43-415d-943a-f66d668fee7b/
```

---

## ⚠️ Potential Issues & Solutions

### Issue 1: Merge Conflicts (Unlikely)

**Scenario:** You modified plans locally before pulling

**Solution:**
```bash
# Stash local changes
git stash

# Pull updates
git pull origin CORTEX-5.0

# Reapply your changes
git stash pop

# If conflicts occur, Git will mark them - resolve manually
```

### Issue 2: Untracked Files in active/ Folder

**Scenario:** You created new plans locally

**Solution:**
```bash
# Check for untracked files
git status

# Either commit them first:
git add cortex-brain/documents/planning/active/my-new-plan/
git commit -m "feat: add my-new-plan"
git pull origin CORTEX-5.0

# Or move them to archives manually:
mv cortex-brain/documents/planning/active/my-new-plan/ \
   cortex-brain/archives/plans/my-drafts/
```

### Issue 3: Modified Files in Archived Plans

**Scenario:** You edited files in plans that were archived

**Solution:**
```bash
# Your changes are in archived plans - safe to keep
git pull origin CORTEX-5.0

# Access your changes in archives folder:
ls cortex-brain/archives/plans/archived-2026-01-06-cleanup/
```

---

## 🔄 Git Pull Command

**Standard pull (recommended):**
```bash
git pull origin CORTEX-5.0
```

**Force sync (if you have conflicts and want to match remote exactly):**
```bash
git fetch origin
git reset --hard origin/CORTEX-5.0
git clean -fd
```

**⚠️ WARNING:** Force sync will **discard all local changes**. Use only if you're sure.

---

## 📊 What Happens on Other Machines

### Machine A (Your machine - already synced)
```
active/
├── cortex5-enhancement-epic/  ← Main plan
└── html-glassmorphism-alignment/
```

### Machine B (Pulls this commit)
**Before pull:**
```
active/
├── a19-cortex5-snowball/
├── cortex5-remediation/
├── cortex5-snowball/
├── cortex5-snowball-enhancement-implement/
├── html-glassmorphism-alignment/
└── plan-caf79368-0d43-415d-943a-f66d668fee7b/
```

**After pull:**
```
active/
├── cortex5-enhancement-epic/  ← Renamed from cortex5-snowball
└── html-glassmorphism-alignment/

archives/plans/archived-2026-01-06-cleanup/  ← 4 plans moved here
├── a19-cortex5-snowball/
├── cortex5-remediation/
├── cortex5-snowball-enhancement-implement/
├── plan-caf79368-0d43-415d-943a-f66d668fee7b/
└── ARCHIVE-MANIFEST.md  ← Explains what was moved
```

---

## 📝 Commit Message

```
chore(planning): consolidate active plans - 6 → 2 plans

- Archived 4 duplicate/obsolete cortex5 plans
- Renamed cortex5-snowball → cortex5-enhancement-epic
- Kept html-glassmorphism-alignment
- Created archive manifest for tracking

Archived plans:
- a19-cortex5-snowball (duplicate with A19 prefix)
- cortex5-remediation (consolidated into epic)
- cortex5-snowball-enhancement-implement (merged)
- plan-caf79368-0d43-415d-943a-f66d668fee7b (orphaned)

Active plans:
- cortex5-enhancement-epic (main CORTEX 5.0 plan)
- html-glassmorphism-alignment (HTML standardization)

Location: cortex-brain/archives/plans/archived-2026-01-06-cleanup/
```

---

## ✅ Post-Pull Checklist

After running `git pull`, verify:

- [ ] Only 2 folders in `cortex-brain/documents/planning/active/`
- [ ] `cortex5-enhancement-epic` folder exists (not `cortex5-snowball`)
- [ ] 4 archived plans in `cortex-brain/archives/plans/archived-2026-01-06-cleanup/`
- [ ] Archive manifest exists and explains changes
- [ ] No untracked files in `active/` folder (check with `git status`)
- [ ] Your local workspace compiles/runs correctly

---

## 🆘 Need Help?

**If something goes wrong:**

1. **Check Git status:**
   ```bash
   git status
   ```

2. **View recent commits:**
   ```bash
   git log --oneline -5
   ```

3. **Reset to last working state:**
   ```bash
   git reflog  # Find last good commit
   git reset --hard HEAD@{1}  # Go back one step
   ```

4. **Ask for help:**
   - Check `ARCHIVE-MANIFEST.md` for details
   - Review this document for troubleshooting
   - Contact team if issues persist

---

**Status:** ✅ READY FOR MULTI-MACHINE SYNC  
**Impact:** Zero manual intervention required (Git handles everything)
