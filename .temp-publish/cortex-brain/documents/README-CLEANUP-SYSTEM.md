# CORTEX Cleanup System Documentation

**Version:** 2.0  
**Last Updated:** 2025-11-22  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## 📋 Overview

The CORTEX Cleanup System provides comprehensive workspace cleanup with intelligent categorization and one-shot efficient deletion. It tracks and removes:

- **Documentation files** (summaries, reports, analyses, reviews)
- **Completion files** (*-COMPLETE.md, *COMPLETION*.md)
- **Progress files** (*-PROGRESS.md, *SESSION*.md)
- **Investigation files** (*INVESTIGATION*.md)
- **Guide files** (*-GUIDE.md, except essential guides)
- **Temporary files** (temp-*.md, TEMP*.md)
- **Fix reports** (*-FIX-*.md, *RESTORATION*.md)
- **Integration docs** (*INTEGRATION*.md)
- **Resolution docs** (*RESOLUTION*.md)
- **Status files** (*-STATUS.md)
- **Notes files** (*-NOTES.md)

---

## 🎯 Key Features

### 1. Intelligent Protection
- **Never deletes** source code, configuration, or essential documentation
- **Preserves** organized structures (cortex-brain/documents/, .github/prompts/)
- **Protects** active phase documentation (PHASE-3-*, PHASE-4-*)
- **Keeps** CORTEX 3.0 design documentation

### 2. One-Shot Efficiency
- Scans entire repository once
- Categorizes all findings
- Deletes all identified files in single operation
- Cleans up empty directories automatically

### 3. Comprehensive Reporting
- Detailed scan reports (JSON format)
- Cleanup execution reports
- Category breakdown
- Space savings metrics

---

## 🚀 Quick Start

### Dry-Run (Preview Only)
```bash
python scripts/master_cleanup.py
```

### Execute Cleanup
```bash
python scripts/master_cleanup.py --execute
```

### Skip Scan (Use Existing Report)
```bash
python scripts/master_cleanup.py --skip-scan --execute
```

---

## 📂 File Structure

```
scripts/
├── master_cleanup.py              # Main orchestrator (one-shot)
├── scan_unnecessary_files.py      # Scan and categorize files
└── cleanup_unnecessary_files.py   # Execute deletion

cortex-brain/
├── cleanup-rules.yaml             # Cleanup configuration
├── cleanup-reports/               # Scan/execution reports
│   ├── unnecessary-files-*.json   # Scan reports
│   └── cleanup-execution-*.json   # Execution reports
└── documents/
    └── README-CLEANUP-SYSTEM.md   # This documentation
```

---

## 🔧 Components

### 1. Master Cleanup Script (`master_cleanup.py`)

**Purpose:** One-shot orchestration of scan and cleanup phases.

**Usage:**
```bash
# Dry-run (preview)
python scripts/master_cleanup.py

# Execute cleanup
python scripts/master_cleanup.py --execute

# Skip scan phase
python scripts/master_cleanup.py --skip-scan --execute
```

**Workflow:**
1. **Phase 1: Scan** - Recursively scan repository for unnecessary files
2. **Phase 2: Cleanup** - Delete identified files and clean empty directories

---

### 2. Scan Script (`scan_unnecessary_files.py`)

**Purpose:** Identify and categorize unnecessary files.

**Usage:**
```bash
python scripts/scan_unnecessary_files.py
```

**Output:**
- Console report (summary by category)
- JSON report: `cortex-brain/cleanup-reports/unnecessary-files-YYYYMMDD_HHMMSS.json`

**Categories Detected:**
- `summary` - *-SUMMARY.md files
- `status` - *-STATUS.md files
- `report` - *-REPORT.md files
- `analysis` - *-ANALYSIS.md files
- `review` - *-REVIEW.md files
- `complete` - *-COMPLETE.md, *COMPLETION*.md
- `investigation` - *INVESTIGATION*.md files
- `progress` - *-PROGRESS.md files
- `notes` - *-NOTES.md files
- `guide` - *-GUIDE.md files
- `temp` - temp-*.md files
- `fix` - *-FIX-*.md files
- `restoration` - *RESTORATION*.md files
- `enhancement` - *ENHANCEMENT*.md files
- `integration` - *INTEGRATION*.md files
- `ambient` - *AMBIENT*.md files
- `resolution` - *RESOLUTION*.md files
- `quick` - QUICK-*.md files
- `session` - *-SESSION*.md files

---

### 3. Cleanup Script (`cleanup_unnecessary_files.py`)

**Purpose:** Execute file deletion based on scan report.

**Usage:**
```bash
# Dry-run
python scripts/cleanup_unnecessary_files.py

# Execute
python scripts/cleanup_unnecessary_files.py --execute
```

**Features:**
- Loads most recent scan report
- Applies protection rules
- Prompts for confirmation
- Deletes files efficiently
- Cleans empty directories
- Generates execution report

---

### 4. Cleanup Rules (`cleanup-rules.yaml`)

**Purpose:** Configuration for cleanup categories and safety rules.

**Key Sections:**

#### Categories
Defines what to clean, with priorities and risk levels:
- `backup_archive` - Recursive .backup-archive
- `story_backups` - docs/awakening-of-cortex.backup.*.md
- `system_refactor_reports` - Auto-generated reports
- `phase_reports` - PHASE-*-PROGRESS.md files
- `session_summaries` - SESSION-*.md files
- `build_output` - site/ directory (MkDocs)
- `workflow_checkpoints` - workflow_checkpoints/*.json
- `legacy_agent_backups` - *.backup files
- `temp_directories` - cortex-brain/crawler-temp, .temp, tmp
- `python_cache` - __pycache__, .pytest_cache, *.pyc
- `docs_awakening_backups` - docs/awakening-of-cortex.backup.*.md
- `cortex_2_0_legacy` - CORTEX 2.0 design folder (archive)
- `root_clutter` - Test/demo/temp files in root
- `copilot_chats_clutter` - .github/CopilotChats temporary files
- `temp_historical_docs` - Historical completion documents (archive)
- **`doc_pattern_cleanup` - Comprehensive documentation pattern cleanup (NEW!)**

#### Protected Directories
Never cleaned:
- `cortex-brain/documents` - Organized structure
- `cortex-brain/archives` - Already archived
- `.git`, `.github/prompts`, `.github/workflows`
- `src`, `tests/fixtures`, `docs/api`, `docs/reference`

#### Protected Files
Never deleted:
- `README.md`, `CHANGELOG.md`, `LICENSE.md`
- `PHASE-3-COMMIT-GUIDE.md`, `PHASE-3-SUMMARY.md`
- `PHASE-3-VISUAL-SUMMARY.md`, `PHASE-4-PRODUCTION-READY.md`
- `GIT-SYNC-COMPLETE.md`
- `QUICK-START.md` (essential guide)

#### Safety Settings
- `dry_run_default: true` - Always default to dry-run
- `require_git_clean: false` - Don't require clean git status
- `check_git_status: true` - But do check and warn
- `create_manifest_default: true` - Create manifests for rollback
- `enable_rollback: true` - Allow undo operations
- `max_recursion_depth: 15` - Prevent infinite loops
- `verify_before_delete: true` - Verify safety before deletion
- `show_summary_before_execute: true` - Show summary first
- `require_user_confirmation_for_medium_risk: true`
- `require_user_confirmation_for_high_risk: true`

---

## 📊 Typical Results

From Phase 1 execution (2025-11-22):

```
📊 Summary:
   Total files found: 92
   Total size: 1.05 MB
   Categories: 14

📁 Analysis:
   Files to delete: 77
   Files preserved: 15

📋 Top Categories:
   GUIDE: 20 files (0.21 MB)
   COMPLETE: 15 files (0.21 MB)
   REPORT: 11 files (0.24 MB)
   SUMMARY: 7 files (0.09 MB)
   PROGRESS: 5 files (0.02 MB)
   INTEGRATION: 5 files (0.06 MB)
   SESSION: 4 files (0.15 MB)
   FIX: 3 files (0.02 MB)
```

**Space Savings:** 0.93 MB freed after cleanup

---

## 🛡️ Safety Features

### 1. Protected Extensions
Never deleted:
- Source code: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, etc.
- Configuration: `.yaml`, `.yml`, `.json`, `.toml`, `.ini`
- Documentation: `.md`, `.rst`, `.txt` (except patterns)

### 2. Protected Directories
Completely preserved:
- `src/` - Source code
- `tests/fixtures/` - Test fixtures
- `cortex-brain/documents/` - Organized documentation
- `cortex-brain/archives/` - Already archived content
- `.github/prompts/` - Prompt system
- `.github/workflows/` - CI/CD workflows
- `docs/api/` - API documentation
- `docs/reference/` - Reference documentation

### 3. Protected Files
Always preserved:
- `README.md`, `CHANGELOG.md`, `LICENSE.md`
- Active phase docs: `PHASE-3-*`, `PHASE-4-PRODUCTION-READY.md`
- Essential guides: `QUICK-START.md`
- Git sync status: `GIT-SYNC-COMPLETE.md`

### 4. Dry-Run Default
All operations default to dry-run mode. Must explicitly use `--execute` flag.

### 5. User Confirmation
Prompts for confirmation before deletion (can be skipped with `--no-confirm` in individual scripts).

### 6. Rollback Support
- Creates manifests of deleted files
- Enables rollback operations
- Generates detailed execution reports

---

## 🔍 Detailed Workflow

### Phase 1: Scan

1. **Initialize Patterns** - Load 20+ file patterns from configuration
2. **Recursive Scan** - Walk entire repository tree
3. **Categorize Files** - Group by pattern type (summary, report, etc.)
4. **Apply Exclusions** - Skip protected directories and files
5. **Generate Report** - Create JSON report with full details
6. **Display Summary** - Show category breakdown in console

**Output:** `cortex-brain/cleanup-reports/unnecessary-files-YYYYMMDD_HHMMSS.json`

### Phase 2: Cleanup

1. **Load Report** - Read most recent scan report
2. **Apply Protection** - Verify files against protection rules
3. **Calculate Totals** - Count files and size to delete
4. **Display Preview** - Show what will be deleted by category
5. **Confirm Deletion** - Prompt user (unless `--no-confirm`)
6. **Delete Files** - Remove all identified files in one pass
7. **Clean Directories** - Remove empty directories
8. **Generate Report** - Create execution report with results

**Output:** `cortex-brain/cleanup-reports/cleanup-execution-YYYYMMDD_HHMMSS.json`

---

## 📈 Performance Metrics

### Scan Performance
- **Speed:** ~2-3 seconds for 92 files
- **Efficiency:** Single-pass recursive scan
- **Memory:** Low memory footprint (<50 MB)

### Cleanup Performance
- **Speed:** ~1-2 seconds for 77 file deletions
- **Efficiency:** One-shot deletion (no repeated scans)
- **Space Freed:** 0.93 MB per run (typical)

### Total Execution Time
- **Dry-Run:** ~5 seconds
- **Execute:** ~7-8 seconds (including confirmation)

---

## 🚨 Common Issues

### Issue 1: Permission Denied
**Symptom:** Error deleting file - permission denied  
**Cause:** File is open in editor or locked by process  
**Solution:** Close file in editor, retry cleanup

### Issue 2: File Not Found
**Symptom:** File in report doesn't exist  
**Cause:** File was manually deleted between scan and cleanup  
**Solution:** Ignore warning, cleanup continues

### Issue 3: Empty Report
**Symptom:** Scan finds 0 files  
**Cause:** Workspace already clean  
**Solution:** No action needed

### Issue 4: Protected File in List
**Symptom:** Essential file appears in scan  
**Cause:** File matches pattern but is protected  
**Solution:** Protection rules applied during cleanup phase, file won't be deleted

---

## 🔧 Customization

### Adding New Patterns

Edit `scripts/scan_unnecessary_files.py`:

```python
PATTERNS = {
    'custom_category': ['*-CUSTOM.md', '*CUSTOM*.md'],
    # ... other patterns
}
```

### Adding Protected Files

Edit `scripts/cleanup_unnecessary_files.py`:

```python
PROTECTED_FILES = {
    'README.md',
    'MY-ESSENTIAL-DOC.md',  # Add here
    # ... other files
}
```

### Adding Protected Directories

Edit `scripts/cleanup_unnecessary_files.py`:

```python
PRESERVE_DIRS = {
    'cortex-brain/documents',
    'my-important-dir/',  # Add here
    # ... other directories
}
```

---

## 📚 References

- **Cleanup Rules:** `cortex-brain/cleanup-rules.yaml`
- **Scan Reports:** `cortex-brain/cleanup-reports/unnecessary-files-*.json`
- **Execution Reports:** `cortex-brain/cleanup-reports/cleanup-execution-*.json`
- **Master Script:** `scripts/master_cleanup.py`
- **Scan Script:** `scripts/scan_unnecessary_files.py`
- **Cleanup Script:** `scripts/cleanup_unnecessary_files.py`

---

## 🎯 Best Practices

1. **Always Dry-Run First** - Preview before executing
2. **Review Scan Report** - Verify what will be deleted
3. **Backup Critical Data** - Use Git to track changes
4. **Run Regularly** - Weekly or after major work sessions
5. **Monitor Space Savings** - Track cleanup efficiency
6. **Update Protection Rules** - Add new essential files as needed
7. **Review Execution Reports** - Check for errors or warnings

---

## 📞 Support

For issues or questions:
- **Repository:** https://github.com/asifhussain60/CORTEX
- **Documentation:** `cortex-brain/documents/README-CLEANUP-SYSTEM.md`
- **Issues:** Submit via GitHub Issues

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms
