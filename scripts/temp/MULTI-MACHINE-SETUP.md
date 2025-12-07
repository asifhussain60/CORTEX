# CORTEX Multi-Machine Setup - Quick Start

**Run these commands on EVERY machine where you use CORTEX**

---

## Step 1: Verify Alignment State Ignored

```bash
# Check if alignment-state.json is in .gitignore
grep "alignment-state.json" .gitignore
```

**Expected:** `cortex-brain/admin/alignment-state.json`

**If not found:**
```bash
echo "cortex-brain/admin/alignment-state.json" >> .gitignore
git add .gitignore
git commit -m "chore: ignore machine-local alignment state"
git push
```

---

## Step 2: Remove from Git Tracking (If Previously Committed)

```bash
# Remove from git tracking (keeps local file)
git rm --cached cortex-brain/admin/alignment-state.json 2>/dev/null || echo "Already untracked"

# If removed, commit the change
git diff --cached --quiet || (git commit -m "chore: untrack alignment-state.json" && git push)
```

---

## Step 3: Initial Alignment

```bash
# Run full alignment to create machine-specific state
python -m src.operations.align
```

**Expected Output:**
```
✅ System healthy (8/8 checks passed)
📝 Alignment state saved
🔄 Full scan (15.2s, 92 features checked)
```

---

## Step 4: Verify State is Local

```bash
# Check git status - should NOT show alignment-state.json
git status
```

**Expected:** No mention of `alignment-state.json`

**If shown as modified:**
```bash
git reset HEAD cortex-brain/admin/alignment-state.json
```

---

## Step 5: Test Incremental Alignment

```bash
# Run align again - should be fast
python -m src.operations.align
```

**Expected Output:**
```
✅ System healthy (8/8 checks passed)
🔄 Incremental scan (2.1s, 3 features checked, 89 skipped)
```

**Performance:** 650% faster (2s vs 15s)

---

## Step 6: Test After Pull

```bash
# Pull latest changes
git pull

# Re-align (should still be fast)
python -m src.operations.align
```

**Expected:** Incremental scan (2-3s) - state preserved

---

## Complete! ✅

Your machine is now configured for:
- ✅ Machine-local alignment state (not shared via git)
- ✅ Fast incremental alignment (2s vs 15s)
- ✅ No merge conflicts on alignment state
- ✅ Independent health tracking per machine

---

## Daily Workflow

```bash
# Pull changes
git pull

# Re-align (fast)
python -m src.operations.align

# Make changes
git add .
git commit -m "feat: my changes"

# (Optional) Verify health before push
python -m src.operations.align

# Push
git push
```

---

## Troubleshooting

**Alignment takes 15s every time:**
```bash
# State file might be corrupted
rm cortex-brain/admin/alignment-state.json
python -m src.operations.align  # Rebuilds state
```

**Git shows alignment-state.json as modified:**
```bash
# Remove from staging
git reset HEAD cortex-brain/admin/alignment-state.json

# Verify .gitignore entry
grep "alignment-state.json" .gitignore
```

**Merge conflict on alignment-state.json:**
```bash
# Keep local version
git checkout --ours cortex-brain/admin/alignment-state.json
git add cortex-brain/admin/alignment-state.json
```

---

## More Information

See `cortex-brain/documents/implementation-guides/multi-machine-alignment.md` for complete guide.
