# CORTEX Cleanup Tool - Quick Start Guide

**Version:** 1.0  
**Last Updated:** 2025-11-13

---

## 🚀 Quick Start

### 1. Analyze Workspace

First, see what temporary files exist:

```powershell
python scripts/analyze_temp_patterns.py
```

**Output:**
```
🔍 PATTERN DISCOVERY RESULTS
Total files scanned: 2717
Cleanup candidates: 57 files matching "cleanup"
                   54 files matching "temp"
                   42 dated files
                   90 versioned files
```

### 2. Run Interactive Cleanup

Safe cleanup with preview:

```powershell
python scripts/cleanup_temp_files.py
```

**Workflow:**
1. Tool scans workspace (excludes git-tracked files automatically)
2. Shows preview categorized by risk level
3. You choose cleanup mode:
   - **Option 1:** HIGH CONFIDENCE only (safest)
   - **Option 2:** HIGH + MEDIUM (recommended)
   - **Option 3:** ALL candidates
   - **Option 4:** Custom selection
   - **Option 5:** Cancel
4. Confirm deletion
5. Files deleted (or simulated in dry-run mode)
6. Deletion log created in `cortex-brain/deletion-logs/`

---

## 📊 Example Session

```
================================================================================
🧠 CORTEX Temporary File Cleanup Tool
================================================================================
🔍 Scanning workspace for temporary files...
📂 Root: D:\PROJECTS\CORTEX
📊 Loading git tracked files...
   Found 2673 tracked files
✅ Scanned 1220 files
📋 Found 21 cleanup candidates

================================================================================
📋 CLEANUP PREVIEW
================================================================================

🔴 HIGH CONFIDENCE (Safe to delete)
Files: 8 | Size: 24.3 KB
  1. src/cortex_agents/code_executor.py.backup
  2. src/cortex_agents/health_validator.py.backup
  ...

🟡 MEDIUM CONFIDENCE (Review recommended)  
Files: 5 | Size: 156.2 KB
  1. cortex-brain/SESSION-SUMMARY-2025-10-15.md (29 days old)
  2. cortex-brain/ANALYSIS-REPORT-2025-10-20.json (24 days old)
  ...

⚪ REVIEW REQUIRED (Manual check needed)
Files: 8 | Size: 891.3 KB
  1. pattern_analysis.json
  2. temp_file_scan.json
  ...

================================================================================
📊 TOTAL: 21 files | 1.1 MB
================================================================================

🎯 CLEANUP OPTIONS
1. Delete HIGH CONFIDENCE only (safest)
2. Delete HIGH + MEDIUM CONFIDENCE (recommended)
3. Delete ALL candidates (includes review required)
4. Custom selection (choose specific files)
5. Cancel (no changes)

Your choice (1-5): 2

⚠️  About to delete 13 files (180.5 KB)
🔍 DRY RUN MODE: Files will NOT be actually deleted

Confirm deletion? (yes/no): yes

================================================================================
🔍 DRY RUN - Simulating deletion
================================================================================
✅ [DRY RUN] Deleted: src/cortex_agents/code_executor.py.backup
✅ [DRY RUN] Deleted: cortex-brain/SESSION-SUMMARY-2025-10-15.md
...

📝 Deletion log saved: cortex-brain/deletion-logs/deletion-log-20251113_145632_DRYRUN.json

================================================================================
📊 CLEANUP SIMULATION COMPLETE
✅ Would delete: 13 files
================================================================================
```

---

## ⚙️ Configuration

### Customize Detection Patterns

Edit `cortex-brain/cleanup-detection-patterns.yaml`:

```yaml
# Add custom temporal keywords
temporal_keywords:
  - experimental
  - prototype

# Add custom exclusions (files to never delete)
custom_exclusions:
  - important_temp_analysis.py
  - WIP-feature-X.md

# Adjust age thresholds (days)
age_thresholds:
  session_summaries: 30
  reports: 14
  logs: 7
```

### Disable Dry-Run Mode

For actual deletion (use with caution):

**Option 1:** Edit config file
```yaml
safety:
  dry_run_default: false
```

**Option 2:** Modify script
```python
cleanup.interactive_cleanup(dry_run=False)
```

---

## 🛡️ Safety Features

**Automatic Protections:**
- ✅ Git tracked files excluded (2,673 files protected)
- ✅ Protected directories (`.git`, `.venv`, `src/`, `tests/`)
- ✅ Protected files (`cortex.config.json`, `requirements.txt`, etc.)
- ✅ Dry-run mode by default
- ✅ Deletion logs for rollback
- ✅ Confirmation required
- ✅ Max 100 files per operation

**Manual Protections:**
- Preview before deletion
- Category-based risk assessment
- Custom file selection
- Cancel option always available

---

## 🔄 Rollback

If you need to restore deleted files:

1. Check deletion log:
   ```powershell
   cat cortex-brain/deletion-logs/deletion-log-20251113_145632.json
   ```

2. Deletion logs contain:
   - File paths
   - File sizes
   - Deletion timestamps
   - Match reasons
   - Dry-run flag

3. Restore from git (if previously tracked):
   ```powershell
   git checkout -- path/to/file
   ```

4. Restore from backup (if you have one):
   - Check `.backup-archive/`
   - Check Windows recycle bin (if not permanently deleted)

---

## 📁 Files Created

**Phase 1 (Analysis):**
- `scripts/analyze_temp_patterns.py` - Pattern analyzer
- `cortex-brain/cleanup-detection-patterns.yaml` - Configuration
- `temp_file_scan.json` - Scan results (regenerate anytime)
- `pattern_analysis.json` - Pattern matches (regenerate anytime)

**Phase 2 (Cleanup):**
- `scripts/cleanup_temp_files.py` - Interactive cleanup tool
- `cortex-brain/deletion-logs/*.json` - Deletion audit trail

**Documentation:**
- `cortex-brain/TEMP-FILE-CLEANUP-SYSTEM.md` - Full documentation
- `cortex-brain/CLEANUP-QUICK-START.md` - This guide

---

## 💡 Tips

**Before first cleanup:**
1. Run analyzer to see what would be found
2. Check `pattern_analysis.json` for false positives
3. Add exclusions to config if needed
4. Test in dry-run mode first

**Regular maintenance:**
1. Run analyzer monthly
2. Review patterns for accuracy
3. Update config based on new patterns
4. Clean up high-confidence files regularly

**Custom patterns:**
1. Watch for new temporal keywords in your workflow
2. Add them to config
3. Test with analyzer
4. Adjust risk classification if needed

---

*Safe, configurable cleanup for CORTEX workspace maintenance*
