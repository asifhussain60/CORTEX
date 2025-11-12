# 📦 CORTEX Branch Publisher

**Purpose:** Publish CORTEX to a dedicated `cortex-publish` branch for clean, user-friendly deployment.

---

## 🎯 Why This Matters

**Problem:**
- Main development branch has 10,000+ commits
- Includes tests, CI/CD, build scripts, dev tools
- Full clone takes minutes and uses 500+ MB
- Users only need production code

**Solution:**
- Dedicated `cortex-publish` orphan branch
- Contains ONLY production-ready code
- No commit history from main branch
- 90% faster clone, 70% smaller size
- Users clone with: `git clone -b cortex-publish --single-branch <repo>`

---

## 🚀 Usage

### Quick Publish

```bash
# From CORTEX root directory
python scripts/publish_to_branch.py
```

This will:
1. ✅ Build production package (excludes tests, docs, dev tools)
2. ✅ Create/update `cortex-publish` orphan branch
3. ✅ Copy clean content to branch
4. ✅ Commit with version info
5. ✅ Push to origin
6. ✅ Return you to original branch

### Dry Run (Preview Only)

```bash
# Preview what would be published
python scripts/publish_to_branch.py --dry-run
```

This creates `.temp-publish/` folder with preview content (not pushed to git).

### Custom Branch Name

```bash
# Publish to different branch
python scripts/publish_to_branch.py --branch my-custom-publish
```

---

## 📦 What Gets Published

### ✅ Included

**Core Source Code:**
- `src/` - All Python source (agents, plugins, operations)
- `cortex-brain/` - Brain storage (YAML configs, schemas)
- `.github/prompts/` - Copilot integration files
- `prompts/` - Modular documentation
- `scripts/` - Automation tools

**Essential Files:**
- `requirements.txt` - Dependencies
- `setup.py` - Installation script
- `cortex.config.template.json` - Config template
- `cortex-operations.yaml` - Operations config
- `README.md`, `LICENSE`, `CHANGELOG.md`
- `SETUP-CORTEX.md` - Comprehensive setup guide (auto-generated)
- `PACKAGE-INFO.md` - Package statistics (auto-generated)

### ❌ Excluded

- `tests/` - Test suite
- `docs/` - MkDocs documentation site
- `.github/workflows/` - CI/CD pipelines
- `examples/` - Example code
- `workflow_checkpoints/` - Dev artifacts
- `logs/` - Log files
- `*.pyc`, `__pycache__/` - Bytecode
- `*.db` - Populated brain databases

---

## 🔄 How It Works

### 1. Orphan Branch Creation

```bash
git checkout --orphan cortex-publish
```

**Why orphan?**
- No parent commits from main branch
- Clean git history (starts fresh)
- Smaller clone size
- Faster operations

### 2. Content Build

Script builds production package:
- Copies essential directories (`src/`, `cortex-brain/`, etc.)
- Excludes dev tools and tests
- Creates auto-generated guides (`SETUP-CORTEX.md`, `PACKAGE-INFO.md`)
- Generates clean `.gitignore`

### 3. Branch Update

```bash
# Switch to publish branch
git checkout cortex-publish

# Remove old content
rm -rf * (except .git)

# Copy new content
cp -r .temp-publish/* .

# Commit and push
git add -A
git commit -m "CORTEX 5.2.0 - Production Release"
git push -f origin cortex-publish
```

### 4. Return to Original Branch

```bash
git checkout CORTEX-2.0  # (or whatever branch you were on)
```

---

## 👥 User Installation

### Option 1: Clone Publish Branch Only (Recommended)

```bash
git clone -b cortex-publish --single-branch https://github.com/asifhussain60/CORTEX.git
cd CORTEX
pip install -r requirements.txt
cp cortex.config.template.json cortex.config.json
# Edit cortex.config.json with your paths
```

**Benefits:**
- ✅ Only downloads production code
- ✅ No dev history (fast clone)
- ✅ 70% smaller disk usage
- ✅ Clean, minimal installation

### Option 2: Switch to Publish Branch

```bash
# If they already cloned main branch
git fetch origin
git checkout cortex-publish
```

---

## 📊 Package Statistics (Example)

After running `publish_to_branch.py`:

```
Files Included: 847
Directories Created: 112
Files Excluded: 1,234
Total Size: 18.3 MB
```

**vs. Full Repository:**
- Main branch: 500+ MB, 10,000+ commits
- Publish branch: 18 MB, ~100 commits
- **Savings: 96% smaller**

---

## 🔧 Prerequisites

**Before running:**
1. ✅ Clean working directory (no uncommitted changes)
2. ✅ On main development branch (e.g., `CORTEX-2.0`)
3. ✅ Git configured with push access
4. ✅ Python 3.8+ installed

**Check status:**
```bash
git status  # Should show "nothing to commit, working tree clean"
```

---

## ⚠️ Important Notes

### Force Push

Script uses `git push -f` (force push) because:
- Orphan branch has no common history with main
- Each publish creates fresh content
- Previous publish commits are replaced

**This is SAFE because:**
- Only affects `cortex-publish` branch
- Main development branch untouched
- Users should never commit to publish branch

### Automatic Files

Script auto-generates:
1. **SETUP-CORTEX.md** - Comprehensive installation guide
2. **PACKAGE-INFO.md** - Package statistics and info
3. **.gitignore** - Clean ignore rules for production

These files are created fresh each publish.

---

## 🐛 Troubleshooting

### "Uncommitted changes" Error

```bash
git status
git add -A
git commit -m "Save work before publish"
```

### Push Failed

```bash
# Manual push (if script push fails)
git checkout cortex-publish
git push -f origin cortex-publish
git checkout CORTEX-2.0
```

### Branch Doesn't Exist Remotely

First publish will create branch automatically. If push fails:

```bash
git push --set-upstream origin cortex-publish
```

### Clean Up After Failed Publish

```bash
# Return to original branch
git checkout CORTEX-2.0

# Delete local publish branch (if corrupted)
git branch -D cortex-publish

# Re-run publish script
python scripts/publish_to_branch.py
```

---

## 📚 Related Files

- **Main Script:** `scripts/publish_to_branch.py`
- **Old Build Script:** `scripts/build_user_deployment.py` (deprecated)
- **Published Content:** Available on `cortex-publish` branch
- **Setup Guide:** `SETUP-CORTEX.md` (auto-generated in publish branch)

---

## 🎓 Best Practices

### When to Publish

✅ **Do publish when:**
- New CORTEX version released (e.g., 5.3.0)
- Major bug fixes
- New user-facing features
- Documentation updates

❌ **Don't publish for:**
- Work in progress
- Experimental features
- Dev tool changes
- Test suite updates

### Version Numbering

Update `PACKAGE_VERSION` in `publish_to_branch.py` before publishing:

```python
PACKAGE_VERSION = "5.2.0"  # Update this!
```

### Testing Before Publish

Always dry-run first:

```bash
python scripts/publish_to_branch.py --dry-run
# Review .temp-publish/ folder
# If looks good:
python scripts/publish_to_branch.py
```

---

## 📞 Support

**Questions?** See:
- Repository: https://github.com/asifhussain60/CORTEX
- Issues: https://github.com/asifhussain60/CORTEX/issues

---

**Copyright © 2024-2025 Asif Hussain. All rights reserved.**

*Last Updated: 2025-11-12*
