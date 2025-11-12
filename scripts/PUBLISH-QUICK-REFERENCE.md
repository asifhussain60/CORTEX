# 🚀 CORTEX Publish Quick Reference

**Use this when you're ready to publish CORTEX to the `cortex-publish` branch for user deployment.**

---

## ✅ Pre-Publish Checklist

```bash
# 1. Verify you're on CORTEX-2.0 branch
git branch --show-current
# Should show: CORTEX-2.0

# 2. Verify clean working directory
git status
# Should show: "nothing to commit, working tree clean"

# 3. Update version number
# Edit: scripts/publish_to_branch.py
# Change: PACKAGE_VERSION = "5.2.0"  # Update to new version!

# 4. Update changelog
# Edit: CHANGELOG.md
# Add release notes for this version
```

---

## 🔍 Test First (Dry Run)

```bash
# Preview what will be published (no git changes)
python scripts/publish_to_branch.py --dry-run
```

**Expected Output:**
```
INFO: ================================================================================
INFO: CORTEX Branch Publisher
INFO: ================================================================================
INFO: Version: 5.2.0
INFO: Target branch: cortex-publish
INFO: Dry run: True
INFO: Building publish content...
INFO: Created SETUP-CORTEX.md
INFO: Created PACKAGE-INFO.md
✅ Build complete:
INFO:    Files: 1,090
INFO:    Size: 67.77 MB
🔍 DRY RUN - No git operations performed
```

---

## 🚀 Publish for Real

```bash
# Publish to cortex-publish branch
python scripts/publish_to_branch.py
```

**Expected Output:**
```
INFO: ================================================================================
INFO: CORTEX Branch Publisher
INFO: ================================================================================
INFO: Creating/updating publish branch...
INFO: Copying new content to publish branch...
INFO: Staging files...
INFO: Committing changes...
INFO: Pushing to origin/cortex-publish...
✅ Push successful
INFO: Returning to original branch: CORTEX-2.0
✅ CORTEX published successfully!

📦 Users can now clone with:
   git clone -b cortex-publish --single-branch https://github.com/asifhussain60/CORTEX.git
```

---

## 📋 What Happens During Publish

1. ✅ **Validation** - Checks for uncommitted changes
2. ✅ **Build** - Creates production package in `.temp-publish/`
3. ✅ **Branch Switch** - Checks out `cortex-publish` (creates if doesn't exist)
4. ✅ **Content Update** - Replaces old content with new build
5. ✅ **Auto-Generate** - Creates SETUP-CORTEX.md and PACKAGE-INFO.md
6. ✅ **Commit** - Commits with version info and stats
7. ✅ **Push** - Force-pushes to origin (orphan branch, safe to force)
8. ✅ **Return** - Switches back to CORTEX-2.0

**Time:** ~30-60 seconds (depending on network)

---

## 🔄 Post-Publish Verification

```bash
# 1. Verify you're back on CORTEX-2.0
git branch --show-current
# Should show: CORTEX-2.0

# 2. Check publish branch on GitHub
# Visit: https://github.com/asifhussain60/CORTEX/tree/cortex-publish

# 3. Test user clone (in a different directory)
cd /tmp  # or C:\temp on Windows
git clone -b cortex-publish --single-branch https://github.com/asifhussain60/CORTEX.git cortex-test
cd cortex-test

# 4. Verify files are correct
ls -la  # Should see: src/, cortex-brain/, .github/prompts/, SETUP-CORTEX.md, etc.
# Should NOT see: tests/, docs/, .github/workflows/, examples/

# 5. Check setup guide
cat SETUP-CORTEX.md  # Should have current version and date
```

---

## 🎯 User Installation (After Publish)

**Tell users to clone with:**

```bash
git clone -b cortex-publish --single-branch https://github.com/asifhussain60/CORTEX.git
cd CORTEX
pip install -r requirements.txt
cp cortex.config.template.json cortex.config.json
# Edit cortex.config.json with your paths
```

**Benefits for users:**
- ⚡ 90% faster clone (10-20 seconds vs 2-5 minutes)
- 💾 87% smaller (68 MB vs 500+ MB)
- 🎯 Only production code (no tests, dev tools, docs site)
- 📚 Clear setup guide (SETUP-CORTEX.md)

---

## ⚠️ Troubleshooting

### Error: "Uncommitted changes"

```bash
git status
git add -A
git commit -m "Save changes before publish"
```

### Error: Push failed

```bash
# Manual push
git checkout cortex-publish
git push -f origin cortex-publish
git checkout CORTEX-2.0
```

### Want to Delete and Start Fresh

```bash
# Delete local branch
git branch -D cortex-publish

# Delete remote branch
git push origin --delete cortex-publish

# Re-run publish
python scripts/publish_to_branch.py
```

---

## 🔧 Advanced Options

### Publish to Different Branch

```bash
python scripts/publish_to_branch.py --branch custom-publish-name
```

### Dry Run with Custom Branch

```bash
python scripts/publish_to_branch.py --branch test-publish --dry-run
```

---

## 📊 Expected Statistics

After publish, you should see:

```
Files Included: ~1,090
Package Size: ~68 MB
Directories: ~112
Files Excluded: ~2,400
```

**Compared to full repo:**
- Main branch: 500+ MB, 3,500+ files
- Publish branch: 68 MB, 1,090 files
- **Savings: 87% smaller**

---

## 📝 Publishing Schedule

**Publish for:**
- ✅ New version releases (5.3.0, 5.4.0, etc.)
- ✅ Critical bug fixes
- ✅ User-facing feature additions
- ✅ Documentation updates

**Don't publish for:**
- ❌ Work in progress
- ❌ Experimental features
- ❌ Dev-only tool changes
- ❌ Test suite updates

---

## 🎓 Quick Commands Summary

```bash
# PRE-PUBLISH
git status                                      # Check clean
git branch --show-current                       # Verify CORTEX-2.0
# Edit scripts/publish_to_branch.py (version)
# Edit CHANGELOG.md (release notes)

# TEST
python scripts/publish_to_branch.py --dry-run   # Preview

# PUBLISH
python scripts/publish_to_branch.py             # Publish for real

# VERIFY
git branch --show-current                       # Should be CORTEX-2.0
# Visit GitHub: /tree/cortex-publish
# Test clone in /tmp
```

---

## 📚 Documentation

- **Full Guide:** `scripts/PUBLISH-TO-BRANCH-README.md`
- **Implementation:** `cortex-brain/PUBLISH-BRANCH-IMPLEMENTATION-COMPLETE.md`
- **Script:** `scripts/publish_to_branch.py`

---

## ✨ First Time Publishing?

**Before your very first publish:**

1. Update version in `scripts/publish_to_branch.py`
2. Update `CHANGELOG.md` with release notes
3. Commit changes to CORTEX-2.0
4. Run dry-run to preview
5. Run actual publish
6. Verify on GitHub
7. Update main README with clone instructions

**After first publish, it's just:**
1. Update version
2. Update changelog
3. Commit
4. Publish

---

**Copyright © 2024-2025 Asif Hussain. All rights reserved.**

*Quick Reference | Keep this handy for publishing!*
