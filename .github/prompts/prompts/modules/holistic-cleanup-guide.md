# Holistic Cleanup Guide

**Purpose:** Complete repository cleanup with production-ready naming validation and detailed reporting  
**Version:** 1.0  
**Status:** ✅ PRODUCTION READY  
**Audience:** CORTEX Administrators

---

## 🎯 Overview

The Holistic Cleanup System performs comprehensive repository analysis to identify and remove non-production files, validate naming standards, and generate detailed manifests for informed decision-making.

### Key Features

✅ **Recursive Scanning** - Scans entire repository structure, all directories and subdirectories  
✅ **Production Validation** - Detects 10 non-production naming patterns  
✅ **File Categorization** - 5 distinct categories (production, non-production, redundant, deprecated, reports)  
✅ **Detailed Manifests** - JSON + Markdown reports with recommendations  
✅ **Safe Execution** - Dry-run default, user approval required, git backup, rollback available  
✅ **Protected Paths** - Never touches critical directories (src/, tests/, cortex-brain/tier*, .git/)

---

## 🚀 Commands

### Basic Commands

```bash
# Run holistic cleanup (dry-run by default)
cleanup

# Explicit holistic mode
holistic cleanup

# Clean CORTEX repository specifically
cleanup cortex
```

### Advanced Options

```bash
# Preview cleanup without executing
cleanup --dry-run

# Execute cleanup (requires approval)
cleanup --execute

# Clean specific directory
cleanup --path cortex-brain/archives

# Skip approval (dangerous, not recommended)
cleanup --force
```

---

## 📋 Cleanup Phases

### Phase 1: Repository Scan (30-60s)

**What Happens:**
- Recursively scans all directories
- Categorizes files by type and purpose
- Detects naming pattern violations
- Identifies redundancies and orphaned files
- Calculates file sizes and statistics

**Protected Paths (Never Touched):**
- `src/` - Core source code
- `tests/` - Test suites
- `cortex-brain/tier1/` - Working memory
- `cortex-brain/tier2/` - Knowledge graph
- `cortex-brain/tier3/` - Development context
- `.git/` - Git repository data
- `.github/` - GitHub workflows and prompts
- `package.json` - Dependencies
- `LICENSE` - License file
- `README.md` - Documentation

**Example Output:**
```
[1/4] Scanning Repository (30-60s)
   📂 Scanning: d:\PROJECTS\CORTEX
   📊 Progress: 2,847 files scanned
   
   Statistics:
   • Total files: 2,847
   • Total size: 1.2 GB
   • Production files: 1,924 (68%)
   • Non-production files: 542 (19%)
   • Redundant files: 253 (9%)
   • Deprecated files: 98 (3%)
   • Report files: 30 (1%)
```

### Phase 2: Production Validation (10-20s)

**What Happens:**
- Checks file naming standards
- Detects temporary/versioned patterns
- Suggests production-ready names
- Flags files requiring attention
- Assigns severity levels (Critical/Warning/Info)

**10 Non-Production Patterns Detected:**

| Pattern | Example | Severity | Description |
|---------|---------|----------|-------------|
| **Temporary Prefix** | `temp_auth.py` | Warning | Files prefixed with temp_ |
| **Version Suffix** | `api_v1.py` | Warning | Files with version numbers |
| **Date Suffix** | `report-20250101.md` | Warning | Files with date timestamps |
| **Modification Prefix** | `clean_parser.py` | Critical | Files prefixed with clean/modified/updated/fixed |
| **Backup Suffix** | `config.backup` | Critical | Files with backup/old suffixes |
| **Copy Indicator** | `auth_copy.py` | Warning | Files marked as copies |
| **Summary Files** | `SUMMARY.md` | Info | Uppercase summary/report files |
| **Archive Prefix** | `archive_data.json` | Warning | Files in archive directories |
| **Legacy Prefix** | `legacy_parser.py` | Warning | Files marked as legacy |
| **Duplicate Extension** | `file.txt.bak` | Warning | Files with duplicate extensions |

**Suggested Production Names:**
```
temp_auth.py → auth.py
api_v1.py → api.py
report-20250101.md → report.md
clean_parser.py → parser.py
config.backup → config.json
auth_copy.py → auth_alternate.py
```

**Example Output:**
```
[2/4] Validating Production Readiness (10-20s)
   🔍 Checking 2,847 files...
   
   Violations Found:
   • 542 non-production files (19%)
   • 124 critical violations (temp_, clean_, backup)
   • 318 warnings (version, date, copy)
   • 100 info (SUMMARY, REPORT)
   
   Production Naming Suggestions:
   • 542 files need renaming
   • 253 files should be deleted (redundant)
   • 98 files should be archived (deprecated)
```

### Phase 3: Report Generation (5s)

**What Happens:**
- Generates comprehensive cleanup manifest
- Creates JSON report for automation
- Creates Markdown report for human review
- Opens report automatically in VS Code
- Provides recommendations based on findings

**Manifest Structure:**
```json
{
  "generated_at": "2025-01-15T14:30:00Z",
  "repository": "d:\\PROJECTS\\CORTEX",
  "overview": {
    "total_files": 2847,
    "total_size_mb": 1200,
    "production_files": 1924,
    "non_production_files": 542,
    "redundant_files": 253,
    "deprecated_files": 98,
    "report_files": 30
  },
  "categories": {
    "production": [...],
    "non_production": [...],
    "redundant": [...],
    "deprecated": [...],
    "reports": [...]
  },
  "recommendations": [
    {
      "priority": "critical",
      "category": "non_production",
      "action": "rename",
      "file_count": 124,
      "reason": "Files with modification prefixes (clean/modified/updated/fixed)"
    }
  ],
  "proposed_actions": {
    "delete": [...],
    "rename": [...]
  }
}
```

**Markdown Report Sections:**
1. **Header** - Generation timestamp, repository path
2. **Overview** - Statistics summary
3. **File Categories** - Collapsible details for each category
4. **Recommendations** - Priority-ordered actions with indicators (🔴🟡🟢)
5. **Proposed Actions** - Delete/rename operations with samples
6. **Footer** - Safety warning

**Example Output:**
```
[3/4] Generating Cleanup Manifest (5s)
   📊 Creating comprehensive report...
   
   Reports Created:
   • JSON: cortex-brain/documents/reports/cleanup-manifest-20250115-143000.json
   • Markdown: cortex-brain/documents/reports/cleanup-report-20250115-143000.md
   
   Opening report in VS Code...
```

### Phase 4: Safe Execution (With Approval)

**What Happens:**
- Shows dry-run preview with all changes
- Waits for user approval ("approve cleanup")
- Creates git backup point before execution
- Performs cleanup operations (delete/rename)
- Documents changes in git commit
- Provides rollback instructions if needed

**Approval Workflow:**
```
CORTEX: 📋 Review the cleanup manifest. When ready:
        • Say "approve cleanup" to execute
        • Say "cancel cleanup" to abort
        
You: approve cleanup

CORTEX: ✅ Starting cleanup execution...
        [4/4] Executing Cleanup Operations
        
        • Creating git backup... ✅
        • Deleting 253 redundant files... ✅
        • Renaming 542 files... ✅
        • Updating references... ✅
        • Creating git commit... ✅
        
        ✅ Cleanup complete!
        
        Summary:
        • Files deleted: 253
        • Files renamed: 542
        • Space freed: 350 MB
        • Git commit: abc123def
        
        Rollback: git reset --hard HEAD~1
```

**Safety Features:**
- ✅ Dry-run preview before execution
- ✅ Git backup before changes
- ✅ Rollback capability if issues
- ✅ Protected paths never touched
- ✅ Detailed action logging

---

## 📊 File Categorization

### Category: Production Files

**Criteria:**
- Core source code (*.py, *.ts, *.cs)
- Configuration files (*.json, *.yaml, *.toml)
- Documentation (README.md, *.md in docs/)
- Build scripts (Makefile, setup.py, package.json)
- Tests (test_*.py, *.test.ts, *.spec.ts)

**Action:** Keep (no changes recommended)

### Category: Non-Production Files

**Criteria:**
- Temporary files (temp_*, *.tmp, *.cache)
- Versioned files (*_v1.py, *-v2.ts)
- Dated files (*-20250101.md, *_2025-01-15.json)
- Modified files (clean_*, modified_*, updated_*, fixed_*)
- Backup files (*.backup, *.old, *_backup_*)
- Copy files (*_copy.*, *(1).*, *-copy.*)

**Action:** Rename to production-ready names or delete if redundant

### Category: Redundant Files

**Criteria:**
- Duplicate files (same content, different names)
- Multiple backups (config.backup, config.backup2, config.old)
- Temporary copies (auth_copy.py, auth_copy2.py)
- Old versions (api_v1.py, api_v2.py when api_v3.py exists)

**Action:** Delete (keep only latest/production version)

### Category: Deprecated Files

**Criteria:**
- Legacy code (legacy_*.py, *_deprecated.*)
- Obsolete tests (test_old_*.py)
- Archived content (archive/*, archived-*)
- Removed features (removed_*.py, deleted_*.ts)

**Action:** Archive to cortex-brain/archives/ or delete if no historical value

### Category: Report Files

**Criteria:**
- Summary documents (SUMMARY*.md, *-SUMMARY.md)
- Report files (REPORT*.md, *-REPORT.md, *_report.json)
- Log files (*.log, debug_*.txt)
- Analysis outputs (analysis-*.json, *_analysis.md)

**Action:** Consolidate into single reports/ directory or delete if outdated

---

## 🔧 Production Naming Standards

### Valid Production Names

**Good Examples:**
- `auth.py` - Simple, descriptive
- `user_service.py` - Clear purpose
- `api_client.ts` - Standard naming
- `config.json` - Configuration file
- `test_auth.py` - Test file

### Non-Production Names (Should Be Fixed)

**Bad Examples:**
- `temp_auth.py` → Rename to `auth.py`
- `api_v1.py` → Rename to `api.py`
- `report-20250101.md` → Rename to `report.md`
- `clean_parser.py` → Rename to `parser.py`
- `config.backup` → Rename to `config.json` or delete
- `auth_copy.py` → Rename to `auth_alternate.py` or delete
- `SUMMARY.md` → Rename to `summary.md` (lowercase)
- `REPORT-20250115.md` → Rename to `report.md`

### Naming Convention Rules

1. **Use lowercase** - Except for README, LICENSE, CONTRIBUTING
2. **No version suffixes** - Use git tags instead (_v1, _v2, -v3)
3. **No date suffixes** - Git history provides timestamps (-20250101, _2025-01-15)
4. **No modification prefixes** - Git shows modification history (clean_, modified_, updated_, fixed_)
5. **No backup suffixes** - Use git branches/tags (.backup, .old, _backup_)
6. **No copy indicators** - Use meaningful alternate names (_copy, (1), -copy)
7. **No temp prefixes** - Use .gitignore for temporary files (temp_, tmp_)
8. **Descriptive names** - Clear purpose without explaining history

---

## 📈 Expected Results

### Typical Cleanup Results

**Before Cleanup:**
```
Total files: 2,847
Total size: 1.2 GB
Production files: 1,924 (68%)
Non-production files: 923 (32%)
```

**After Cleanup:**
```
Total files: 1,924
Total size: 850 MB
Production files: 1,924 (100%)
Space freed: 350 MB
Files removed: 923 (32%)
```

### Benefits

✅ **Cleaner Repository** - Only production-ready files remain  
✅ **Faster Operations** - Less files to scan/index/backup  
✅ **Clear Naming** - All files follow production standards  
✅ **Reduced Confusion** - No ambiguous temp/backup/copy files  
✅ **Better Git History** - Cleaner diffs and commits  
✅ **Smaller Backups** - 30-40% smaller repository size

---

## 🛡️ Safety Mechanisms

### Pre-Execution Checks

1. **Git Status Check** - Warns if uncommitted changes exist
2. **Branch Check** - Warns if not on main/develop branch
3. **Backup Creation** - Creates git stash/commit before cleanup
4. **Protected Paths** - Validates no protected files affected
5. **Dry-Run Preview** - Shows all changes before execution

### During Execution

1. **Transaction Log** - Records every operation
2. **Error Handling** - Stops on critical errors
3. **Progress Tracking** - Shows real-time progress
4. **Rollback Points** - Creates checkpoints during cleanup

### Post-Execution

1. **Verification** - Validates all operations succeeded
2. **Git Commit** - Documents cleanup in repository history
3. **Rollback Instructions** - Provides undo commands
4. **Summary Report** - Shows what changed

### Rollback Procedure

**If cleanup caused issues:**
```bash
# Option 1: Git reset (recommended)
git reset --hard HEAD~1

# Option 2: Git revert (preserves history)
git revert HEAD

# Option 3: Restore from backup
git stash pop
```

---

## 🐛 Troubleshooting

### Issue: "Cleanup removed important file"

**Solution:**
```bash
# Check git history
git log --oneline

# Restore specific file
git checkout HEAD~1 -- path/to/file.py

# Or full rollback
git reset --hard HEAD~1
```

### Issue: "Renamed files broke imports"

**Solution:**
```bash
# Search for old import references
grep -r "old_filename" src/

# Update imports manually or use:
find src/ -type f -exec sed -i 's/old_filename/new_filename/g' {} +

# Or rollback and fix references first
git reset --hard HEAD~1
```

### Issue: "Protected path was modified"

**Cause:** Bug in protection logic  
**Solution:**
```bash
# Report bug immediately
feedback bug "Protected path modified during cleanup"

# Restore from backup
git reset --hard HEAD~1
```

### Issue: "Cleanup manifest too large"

**Cause:** Too many files to process  
**Solution:**
```bash
# Clean specific directory instead
cleanup --path cortex-brain/archives

# Or clean category by category
cleanup --category non_production
cleanup --category redundant
cleanup --category deprecated
```

---

## 📚 Integration with CORTEX Systems

### Planning System

**Integration:** Cleanup runs before major features to ensure clean starting point  
**Example:** Plan authentication → Cleanup first → Begin implementation

### TDD Workflow

**Integration:** Cleanup removes obsolete tests automatically  
**Example:** TDD session → Test cleanup → Generate new tests

### Upgrade System

**Integration:** Cleanup runs after upgrades to remove deprecated files  
**Example:** Upgrade CORTEX → Cleanup deprecated patterns

### Documentation System

**Integration:** Cleanup consolidates report files before doc generation  
**Example:** Generate docs → Cleanup reports → Deploy to GitHub Pages

---

## 🎯 Best Practices

### When to Run Cleanup

✅ **Before Major Features** - Start with clean repository  
✅ **After Upgrades** - Remove deprecated files  
✅ **Monthly Maintenance** - Regular housekeeping  
✅ **Before Releases** - Ensure production-ready naming  
✅ **After Big Refactors** - Remove obsolete code

### What to Review Before Approval

1. **Proposed Deletions** - Verify no critical files
2. **Proposed Renames** - Check suggested names make sense
3. **Protected Paths** - Confirm no protected files affected
4. **Space Savings** - Validate expected space freed
5. **Rollback Plan** - Ensure you can undo if needed

### How to Avoid Issues

1. **Always Dry-Run First** - Review manifest before executing
2. **Commit Before Cleanup** - Ensure git repository clean
3. **Read Manifest Carefully** - Don't rush approval
4. **Test After Cleanup** - Run tests to verify nothing broke
5. **Keep Backup** - Have recent backup before major cleanups

---

## 📖 Related Documentation

- **Response Template:** `cortex-brain/response-templates.yaml` (cleanup_operation)
- **Implementation Plan:** `cortex-brain/documents/implementation-guides/cleanup-enhancement-implementation-plan.md`
- **Orchestrator:** `src/operations/modules/cleanup/holistic_cleanup_orchestrator.py`
- **Original Orchestrator:** `src/operations/modules/cleanup/cleanup_orchestrator.py`

---

## 🎓 Copyright & Attribution

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX

---

**Version:** 1.0 - Holistic Cleanup Guide  
**Last Updated:** January 15, 2025
