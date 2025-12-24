# CORTEX Pre-Commit Hook Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 18, 2025  
**Status:** ✅ ACTIVE

---

## 📋 Overview

Automated pre-commit hook system that maintains repository hygiene by enforcing CORTEX file organization rules, detecting violations, and auto-fixing common issues.

**Location:** `.git/hooks/pre-commit`

---

## 🎯 What It Does

### 1. Root-Level Document Detection (BLOCKING)

**Problem:** Documents created at repository root violate CORTEX organization rules.

**Solution:** Automatically detects and moves misplaced documents to correct `cortex-brain/documents/` category.

**Example:**
```bash
# Before commit
CORTEX/
├── analysis-report.md  ❌ Root-level violation

# After auto-fix
CORTEX/
└── cortex-brain/
    └── documents/
        └── analysis/
            └── analysis-report.md  ✅ Moved automatically
```

**Categories:**
- `reports/` - Status, test results, validation reports
- `analysis/` - Code analysis, reviews, investigations
- `summaries/` - Project summaries, overviews
- `investigations/` - Debug logs, issue investigations
- `planning/` - Plans, roadmaps, milestones
- `implementation-guides/` - How-to guides, tutorials

---

### 2. Debug Marker Detection (WARNING)

**Problem:** Debug code accidentally committed to repository.

**Solution:** Warns about debug markers but doesn't block commit (manual cleanup required).

**Detected Patterns:**
```python
# Python
print("DEBUG: ...")
import pdb; pdb.set_trace()
breakpoint()

# JavaScript/TypeScript
console.log("DEBUG ...")
debugger;
```

**Action:** Review and remove before committing, or commit with warning if intentional.

---

### 3. Temporary File Detection (BLOCKING)

**Problem:** Temporary files accidentally staged for commit.

**Solution:** Auto-unstages temporary files.

**Detected Patterns:**
- `*.tmp`
- `*.temp`
- `*~`
- `.DS_Store`
- `Thumbs.db`

---

### 4. cortex-brain/ Structure Validation (WARNING)

**Problem:** Files placed directly in `cortex-brain/` instead of subdirectories.

**Solution:** Warns but doesn't block (some valid cases exist like `response-templates-v4.yaml`).

**Expected Structure:**
```
cortex-brain/
├── response-templates-v4.yaml  ✅ Exception
├── documents/                   ✅ Valid
├── manifests/                   ✅ Valid
├── tier1/, tier2/, tier3/       ✅ Valid
└── random-file.md               ⚠️  Warning
```

---

### 5. File Size Limits (WARNING)

**Problem:** Large files slow down repository operations.

**Solution:** Warns about files >5MB.

**Recommended Action:**
- Use Git LFS for large binaries
- Compress files if possible
- Store large assets externally

---

## 🚀 Usage

### Automatic Execution

Hook runs automatically on every `git commit`:

```bash
git add cortex-brain/documents/planning/my-plan.md
git commit -m "Add planning document"

# Output:
🔍 CORTEX Pre-Commit Hook: Running repository hygiene checks...

✅ All checks passed! Repository is clean.
[CORTEX-4.0 abc123] Add planning document
 1 file changed, 50 insertions(+)
```

---

### Example: Auto-Fix Root-Level Document

```bash
# Create document at root (mistake)
echo "# Analysis" > analysis-report.md
git add analysis-report.md
git commit -m "Add analysis"

# Hook output:
🔍 CORTEX Pre-Commit Hook: Running repository hygiene checks...

✅ Auto-fixes applied:
   ✅ Moved analysis-report.md → cortex-brain/documents/analysis/

✅ Commit allowed (warnings are non-blocking).
[CORTEX-4.0 def456] Add analysis
 1 file changed, 1 insertion(+)
 create mode 100644 cortex-brain/documents/analysis/analysis-report.md
```

---

### Example: Debug Marker Warning

```bash
git add src/orchestrators/my_orchestrator.py
git commit -m "Add orchestrator"

# Hook output:
🔍 CORTEX Pre-Commit Hook: Running repository hygiene checks...

⚠️  Warnings (non-blocking):
   ⚠️  Debug markers detected:
   - src/orchestrators/my_orchestrator.py: print\(["\']DEBUG:

✅ Commit allowed (warnings are non-blocking).
[CORTEX-4.0 ghi789] Add orchestrator
```

---

### Example: Blocking Error (Temp Files)

```bash
git add temp-file.tmp
git commit -m "Add temp"

# Hook output:
🔍 CORTEX Pre-Commit Hook: Running repository hygiene checks...

✅ Auto-fixes applied:
   ✅ Unstaged temp file: temp-file.tmp

❌ Errors (blocking commit):
   ❌ Temporary files detected (should not be committed):
   - temp-file.tmp

💡 Tip: Some issues were auto-fixed. Review changes and commit again.
```

---

## 🔧 Configuration

### .cortexignore File

Customize hook behavior by editing `.cortexignore`:

```bash
# Allow specific root-level files
README.md
LICENSE

# Ignore specific directories
archive/
logs/

# Pattern matching
*.log
.DS_Store
```

**Location:** `CORTEX/.cortexignore`

---

### Disable Hook Temporarily

```bash
# Skip hook for one commit (use sparingly)
git commit --no-verify -m "Emergency fix"

# Disable hook permanently (not recommended)
chmod -x .git/hooks/pre-commit
```

---

## 📊 Check Reference

| Check | Type | Action | Can Override |
|-------|------|--------|--------------|
| Root-level documents | ERROR | Auto-move to correct category | No |
| Debug markers | WARNING | Warn only | Yes (commit anyway) |
| Temporary files | ERROR | Auto-unstage | No |
| cortex-brain structure | WARNING | Warn only | Yes |
| File size >5MB | WARNING | Warn only | Yes |

---

## 🛠️ Troubleshooting

### Hook Not Running

**Problem:** Commits succeed without hook output.

**Solution:**
```bash
# Check if hook is executable
ls -l .git/hooks/pre-commit
# Should show: -rwxr-xr-x

# Make executable if needed
chmod +x .git/hooks/pre-commit
```

---

### False Positives

**Problem:** Hook incorrectly flags valid files.

**Solution:** Add patterns to `.cortexignore`:
```bash
# Add to .cortexignore
my-valid-file.md
special-directory/
```

---

### Auto-Fix Not Working

**Problem:** Hook detects issue but doesn't auto-fix.

**Solution:**
1. Check file permissions (hook needs write access)
2. Review git status - file might not be staged
3. Check `.cortexignore` - file might be excluded

---

## 🔍 Manual Check

Run hook checks without committing:

```bash
# Test hook on currently staged files
.git/hooks/pre-commit

# Check specific file
git add my-file.md
.git/hooks/pre-commit
```

---

## 📈 Benefits

**Before Hook:**
- ❌ Root-level docs: `CORTEX/analysis.md`, `CORTEX/summary.md`
- ❌ Debug code committed: `print("DEBUG: ...")`
- ❌ Temp files: `.DS_Store`, `*.tmp`
- ❌ Manual cleanup required

**After Hook:**
- ✅ Auto-organized: `cortex-brain/documents/analysis/analysis.md`
- ✅ Debug warnings: Reminded to clean up
- ✅ Temp files blocked: Never committed
- ✅ Clean repository: Automatic enforcement

---

## 🚀 Future Enhancements

**Planned:**
1. **Smart categorization** - Machine learning to detect document type
2. **Spell checking** - Detect typos in commit messages
3. **TOD tracking** - Detect and enforce TODO format
4. **Test coverage** - Require tests for new Python files
5. **Manifest validation** - Check YAML schema compliance

---

## 📞 Support

**Issues:**
- Hook not working: Check executable permissions
- False positives: Add to `.cortexignore`
- Feature requests: Create GitHub issue

**Documentation:**
- This guide: `cortex-brain/documents/implementation-guides/PRE-COMMIT-HOOK-GUIDE.md`
- Hook source: `.git/hooks/pre-commit`
- Ignore patterns: `.cortexignore`

---

## ✅ Summary

**What You Get:**
- ✅ Automatic document organization (no more root-level docs)
- ✅ Debug marker detection (prevent accidental commits)
- ✅ Temp file blocking (keep repository clean)
- ✅ Structure validation (enforce cortex-brain/ organization)
- ✅ File size warnings (prevent bloat)

**Best Practices:**
1. Let hook auto-fix when possible
2. Review warnings before committing
3. Add exceptions to `.cortexignore` when needed
4. Never use `--no-verify` unless emergency

**Result:** Clean, organized repository with automated hygiene enforcement.

---

**Version:** 1.0.0  
**Last Updated:** December 18, 2025  
**Status:** ✅ Production Ready
