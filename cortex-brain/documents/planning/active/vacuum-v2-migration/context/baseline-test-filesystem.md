# Baseline Test Filesystem Structure

**Date:** 2026-01-02  
**Purpose:** Document test filesystem structure for validating Vacuum v2 operations

---

## 🎯 Test Scenarios

The baseline test filesystem covers **ALL edge cases** from the V1 specification:

1. Temporary files (safe deletion)
2. Build artifacts (safe deletion)
3. IDE metadata (selective deletion)
4. Duplicate files (hash detection)
5. Orphaned files (AST analysis)
6. Large binaries (warnings)
7. Misplaced files (reorganization)
8. Stale logs (archival)
9. Empty directories (cleanup)
10. Symlinks (safe handling)
11. Permission issues (error handling)
12. Git integration (uncommitted changes)
13. CORTEX brain protection (critical files)

---

## 📁 Test Filesystem Layout

```
test-vacuum-workspace/
├── .git/                           # Git metadata (CRITICAL - never delete)
│   ├── config
│   ├── HEAD
│   └── objects/
├── .gitignore                      # Git config (CRITICAL - never delete)
├── .github/                        # CI/CD workflows (CRITICAL)
│   └── workflows/
│       └── test.yml
├── .vscode/                        # IDE metadata (selective)
│   ├── settings.json              # Delete (generic)
│   ├── launch.json                # Keep (custom)
│   └── tasks.json                 # Keep (custom)
├── .idea/                          # JetBrains (delete)
│   └── workspace.xml
├── src/                            # Source code (CRITICAL)
│   ├── main.py                    # Keep
│   ├── utils.py                   # Keep (original)
│   ├── legacy_utils.py            # Keep (source code)
│   └── __pycache__/               # Delete (build artifact)
│       ├── main.cpython-311.pyc
│       └── utils.cpython-311.pyc
├── tests/                          # Tests (CRITICAL)
│   ├── test_main.py               # Keep
│   ├── test_orphan.py             # Orphaned (no src/orphan.py)
│   └── __pycache__/               # Delete
├── build/                          # Build artifacts (DELETE)
│   ├── lib/
│   └── temp/
├── dist/                           # Distribution (DELETE)
│   └── package.whl
├── node_modules/                   # Dependencies (DELETE)
│   └── (1000+ packages)
├── logs/                           # Logs (archive old)
│   ├── app-2025-01-01.log         # Archive (>30 days)
│   ├── app-2025-12-01.log         # Keep (recent)
│   └── error-2024-06-15.log       # Archive (>6 months)
├── temp/                           # Temporary files (DELETE)
│   ├── cache.tmp
│   ├── session-abc123.temp
│   └── ~backup.bak
├── duplicates/                     # Duplicate files (test detection)
│   ├── utils.py                   # Duplicate of src/utils.py
│   ├── backup/
│   │   └── utils.py               # Another duplicate
│   └── old/
│       └── utils.py               # Yet another duplicate
├── large-files/                    # Large binaries (warn before delete)
│   ├── dataset.csv                # 50 MB
│   ├── backup.zip                 # 100 MB
│   └── video.mp4                  # 500 MB
├── symlinks/                       # Symlink edge cases
│   ├── link-to-src -> ../src/     # Safe (inside workspace)
│   ├── link-to-main.py -> ../src/main.py  # Safe
│   └── broken-link -> /nonexistent  # Broken symlink (delete)
├── permissions/                    # Permission edge cases
│   ├── readonly.txt               # Read-only file
│   ├── locked.db                  # Locked file (simulated)
│   └── no-write/                  # Directory with no write permission
│       └── file.txt
├── unicode/                        # Unicode filenames
│   ├── 测试文件.txt               # Chinese
│   ├── файл.py                    # Russian
│   └── 📄document.md              # Emoji
├── empty-dirs/                     # Empty directories
│   ├── placeholder/               # Empty (delete)
│   ├── with-gitkeep/              # Has .gitkeep (keep)
│   │   └── .gitkeep
│   └── migrations/                # Required by framework (keep)
├── git-status-tests/               # Git integration tests
│   ├── modified.py                # Modified (uncommitted) - BLOCK
│   ├── untracked.txt              # Untracked - HIGH RISK
│   └── staged.md                  # Staged - BLOCK
├── cortex-brain/                   # CORTEX brain (CRITICAL)
│   ├── tier0/                     # Governance (NEVER DELETE)
│   │   └── brain-protection-rules.yaml
│   ├── tier1/                     # Working memory (NEVER DELETE)
│   │   └── sessions.db
│   ├── cache/                     # Cache (SAFE to delete)
│   │   └── response-cache.json
│   └── logs/                      # Logs (SAFE to archive)
│       └── orchestrator.log
├── misplaced/                      # Files in wrong location
│   ├── summary.md                 # Should be in cortex-brain/documents/summaries/
│   ├── analysis.txt               # Should be in cortex-brain/documents/analysis/
│   └── plan.yaml                  # Should be in cortex-brain/documents/planning/
├── recent-files/                   # Recently modified files
│   ├── work-in-progress.py        # Modified 1 hour ago - HIGH RISK
│   └── draft-doc.md               # Modified 30 minutes ago - HIGH RISK
├── config/                         # Configuration (CRITICAL)
│   ├── settings.yaml              # Keep
│   ├── requirements.txt           # Keep
│   └── package.json               # Keep
├── docs/                           # Documentation (CRITICAL)
│   ├── README.md                  # Keep
│   ├── LICENSE                    # Keep
│   └── CHANGELOG.md               # Keep
└── auto-generated/                 # Auto-generated code (LOW RISK)
    ├── api_client.py              # Has "# Auto-generated" marker
    └── models.py                  # Has "# DO NOT EDIT" marker
```

---

## 🧪 Expected Behavior by Category

### 1. **Temporary Files** (SAFE - Delete)
- ✅ `temp/cache.tmp`
- ✅ `temp/session-abc123.temp`
- ✅ `temp/~backup.bak`

**Result:** 3 files deleted, ~1 MB recovered

### 2. **Build Artifacts** (SAFE - Delete)
- ✅ `src/__pycache__/`
- ✅ `tests/__pycache__/`
- ✅ `build/`
- ✅ `dist/`
- ✅ `node_modules/`

**Result:** 1000+ files deleted, ~500 MB recovered

### 3. **IDE Metadata** (MEDIUM - Selective)
- ✅ Delete: `.vscode/settings.json`
- ✅ Delete: `.idea/workspace.xml`
- ❌ Keep: `.vscode/launch.json`
- ❌ Keep: `.vscode/tasks.json`
- ❌ Keep: `.github/workflows/test.yml`

**Result:** 2 files deleted, 3 files preserved

### 4. **Duplicate Files** (MEDIUM - Hash Detection)
**Groups:**
- Group 1: `src/utils.py`, `duplicates/utils.py`, `duplicates/backup/utils.py`, `duplicates/old/utils.py`

**Strategy:**
- Keep newest: `src/utils.py` (modified most recently)
- Delete others: 3 duplicates

**Result:** 3 duplicates removed, ~10 KB recovered

### 5. **Orphaned Files** (MEDIUM - Confirm)
- ⚠️ `tests/test_orphan.py` (no `src/orphan.py`)

**Strategy:**
- Warn user
- Require confirmation
- Archive instead of delete (if confirmed)

**Result:** 1 orphaned test archived

### 6. **Large Binaries** (MEDIUM - Warn)
- ⚠️ `large-files/dataset.csv` (50 MB)
- ⚠️ `large-files/backup.zip` (100 MB)
- ⚠️ `large-files/video.mp4` (500 MB)

**Strategy:**
- Warn user before deletion
- Require confirmation
- Suggest moving to proper location

**Result:** User-dependent (warn + confirm)

### 7. **Misplaced Files** (HIGH - Reorganize)
- ❌ `misplaced/summary.md` → ✅ `cortex-brain/documents/summaries/summary.md`
- ❌ `misplaced/analysis.txt` → ✅ `cortex-brain/documents/analysis/analysis.txt`
- ❌ `misplaced/plan.yaml` → ✅ `cortex-brain/documents/planning/active/{plan}/plan.yaml`

**Strategy:**
- Move files to correct locations
- Resolve conflicts (rename if target exists)
- Validate moves completed

**Result:** 3 files reorganized

### 8. **Stale Logs** (MEDIUM - Archive)
- ✅ Archive: `logs/app-2025-01-01.log` (>30 days) → `logs/archive/2025-01/`
- ✅ Archive: `logs/error-2024-06-15.log` (>6 months) → Delete after compression
- ❌ Keep: `logs/app-2025-12-01.log` (recent)

**Strategy:**
- Move logs >30 days to archive
- Compress archived logs (gzip)
- Delete logs >6 months

**Result:** 2 logs archived, 1 deleted

### 9. **Empty Directories** (LOW - Clean)
- ✅ Delete: `empty-dirs/placeholder/`
- ❌ Keep: `empty-dirs/with-gitkeep/` (has `.gitkeep`)
- ❌ Keep: `empty-dirs/migrations/` (required by framework)

**Result:** 1 empty directory removed

### 10. **Symlinks** (Edge Cases)
- ✅ Delete: `symlinks/broken-link` (broken symlink)
- ❌ Keep: `symlinks/link-to-src` (valid, inside workspace)
- ❌ Keep: `symlinks/link-to-main.py` (valid)

**Strategy:**
- Delete broken symlinks
- Preserve valid symlinks inside workspace
- Never follow symlinks outside workspace

**Result:** 1 broken symlink removed

### 11. **Permissions** (Error Handling)
- ⚠️ `permissions/readonly.txt` - Skip (read-only)
- ⚠️ `permissions/locked.db` - Skip (file locked)
- ⚠️ `permissions/no-write/file.txt` - Skip (directory not writable)

**Strategy:**
- Detect permission errors
- Log warnings
- Skip inaccessible files
- Report in final summary

**Result:** 3 files skipped (permission errors)

### 12. **Git Integration** (CRITICAL - Block)
- ❌ BLOCK: `git-status-tests/modified.py` (uncommitted changes)
- ❌ BLOCK: `git-status-tests/staged.md` (staged)
- ⚠️ HIGH RISK: `git-status-tests/untracked.txt` (untracked - not in git)

**Strategy:**
- Check `git status --porcelain` for each file
- Block deletion of modified/staged files
- Warn for untracked files

**Result:** 2 files blocked, 1 warned

### 13. **CORTEX Brain Protection** (CRITICAL - Never Delete)
- ❌ BLOCK: `cortex-brain/tier0/brain-protection-rules.yaml`
- ❌ BLOCK: `cortex-brain/tier1/sessions.db`
- ✅ DELETE: `cortex-brain/cache/response-cache.json`
- ✅ ARCHIVE: `cortex-brain/logs/orchestrator.log`

**Strategy:**
- Block deletion of tier0/1/2/3
- Allow deletion of cache/logs
- Enforce CORTEX brain protection rules

**Result:** 1 cache file deleted, 1 log archived, critical files protected

### 14. **Recent Files** (HIGH RISK - Confirm)
- ⚠️ `recent-files/work-in-progress.py` (modified 1 hour ago)
- ⚠️ `recent-files/draft-doc.md` (modified 30 minutes ago)

**Strategy:**
- Check modification time
- Warn if modified <24 hours
- Require confirmation

**Result:** 2 files warned (user confirmation required)

### 15. **Auto-Generated Code** (LOW RISK)
- ✅ `auto-generated/api_client.py` (has "# Auto-generated")
- ✅ `auto-generated/models.py` (has "# DO NOT EDIT")

**Strategy:**
- Detect auto-generated markers in file
- Lower risk classification
- Still require user confirmation (source code)

**Result:** 2 files flagged as auto-generated (inform user)

---

## 📊 Summary of Expected Results

### Dry-Run Report

**Files to Delete:** ~1,010 files  
**Disk Space Recovery:** ~550 MB  
**Files to Move:** 3 files  
**Files to Archive:** 3 files  
**Warnings:** 12 files  
**Blocked:** 5 files (critical)

### Risk Breakdown

| Risk Level | Count | Examples |
|------------|-------|----------|
| **CRITICAL** (Blocked) | 5 | Git metadata, uncommitted changes, CORTEX tier0 |
| **HIGH** (Confirm) | 4 | Recent files, untracked git files |
| **MEDIUM** (Warn) | 8 | Large binaries, orphaned tests, misplaced files |
| **LOW** (Safe) | 2 | Empty directories, broken symlinks |
| **SAFE** (Auto) | ~1,010 | Temp files, build artifacts, caches |

### Category Breakdown

| Category | Files | Space | Action |
|----------|-------|-------|--------|
| Temp Files | 3 | 1 MB | Delete |
| Build Artifacts | 1,000+ | 500 MB | Delete |
| IDE Metadata | 2 | <1 MB | Delete |
| Duplicates | 3 | 10 KB | Delete (keep newest) |
| Orphaned Files | 1 | 5 KB | Archive (warn) |
| Large Binaries | 3 | 650 MB | Warn + Confirm |
| Misplaced Files | 3 | 20 KB | Move |
| Stale Logs | 2 | 5 MB | Archive |
| Empty Directories | 1 | 0 MB | Delete |
| Broken Symlinks | 1 | 0 MB | Delete |
| Permissions | 3 | — | Skip (errors) |
| Git Protected | 2 | — | Block |
| CORTEX Brain | 2 | — | Block |
| Recent Files | 2 | 50 KB | Warn |

---

## 🧪 Test Execution Plan

### Phase 1: Dry-Run Test
1. Run vacuum with `--dry-run=true`
2. Verify report matches expected results
3. Check no files were actually deleted/moved
4. Validate risk classifications

### Phase 2: Safe Deletion Test
1. Run vacuum with `--dry-run=false --auto-approve=false`
2. Delete only SAFE files (temp, build artifacts)
3. Verify ~1,010 files deleted
4. Verify ~550 MB recovered
5. Validate no critical files touched

### Phase 3: Checkpoint & Rollback Test
1. Run vacuum with checkpoint creation
2. Delete files
3. Verify checkpoint directory created
4. Run rollback command
5. Verify all files restored

### Phase 4: Git Integration Test
1. Create uncommitted changes
2. Run vacuum
3. Verify uncommitted files blocked
4. Commit changes
5. Re-run vacuum
6. Verify files now deletable

### Phase 5: Permission Test
1. Create read-only file
2. Run vacuum
3. Verify file skipped (permission error logged)
4. Verify final report includes skipped files

### Phase 6: CORTEX Brain Protection Test
1. Attempt to vacuum `cortex-brain/tier0/`
2. Verify deletion blocked
3. Verify error message references brain protection rules

### Phase 7: Reorganization Test
1. Place files in wrong locations
2. Run vacuum with `--reorganize=true`
3. Verify files moved to correct locations
4. Verify no file conflicts

### Phase 8: Duplicate Detection Test
1. Create identical files in multiple locations
2. Run vacuum
3. Verify duplicates detected (hash-based)
4. Verify only newest kept
5. Verify others deleted

---

## 🛠️ Test Implementation

### Creating Test Filesystem

```python
from pathlib import Path
import shutil
from datetime import datetime, timedelta

def create_test_filesystem(root: Path):
    """Create baseline test filesystem."""
    root.mkdir(parents=True, exist_ok=True)
    
    # Git metadata
    (root / '.git').mkdir()
    (root / '.git' / 'config').write_text('[core]\n\trepositoryformatversion = 0')
    
    # Source code
    (root / 'src').mkdir()
    (root / 'src' / 'main.py').write_text('def main():\n    print("Hello")')
    (root / 'src' / 'utils.py').write_text('def util():\n    pass')
    
    # Build artifacts
    (root / 'build').mkdir()
    (root / 'dist').mkdir()
    (root / 'src' / '__pycache__').mkdir()
    (root / 'src' / '__pycache__' / 'main.cpython-311.pyc').write_bytes(b'\x00' * 1024)
    
    # Temp files
    (root / 'temp').mkdir()
    (root / 'temp' / 'cache.tmp').write_text('cache data')
    (root / 'temp' / '~backup.bak').write_text('backup')
    
    # Duplicates
    (root / 'duplicates').mkdir()
    shutil.copy(root / 'src' / 'utils.py', root / 'duplicates' / 'utils.py')
    
    # Recent files
    (root / 'recent-files').mkdir()
    recent_file = root / 'recent-files' / 'work-in-progress.py'
    recent_file.write_text('print("WIP")')
    # Set mtime to 1 hour ago
    one_hour_ago = (datetime.now() - timedelta(hours=1)).timestamp()
    os.utime(recent_file, (one_hour_ago, one_hour_ago))
    
    # ... (create remaining test files)
```

### Running Tests

```python
import pytest
from vacuum_orchestrator_v2 import VacuumOrchestratorV2

def test_dry_run():
    """Test dry-run mode (no modifications)."""
    workspace = Path('test-vacuum-workspace')
    create_test_filesystem(workspace)
    
    orchestrator = VacuumOrchestratorV2(config_path='test-config.yaml')
    result = orchestrator.execute(
        target_path=workspace,
        dry_run=True
    )
    
    assert result['status'] == 'success'
    assert result['files_to_delete'] == 1010
    assert result['space_recovery_mb'] == 550
    assert result['blocked_files'] == 5

def test_safe_deletion():
    """Test safe file deletion."""
    workspace = Path('test-vacuum-workspace')
    create_test_filesystem(workspace)
    
    # Count files before
    files_before = len(list(workspace.rglob('*')))
    
    orchestrator = VacuumOrchestratorV2(config_path='test-config.yaml')
    result = orchestrator.execute(
        target_path=workspace,
        dry_run=False,
        auto_approve=True  # Auto-approve SAFE files only
    )
    
    # Count files after
    files_after = len(list(workspace.rglob('*')))
    
    assert files_before - files_after == 1010
    assert result['space_saved_mb'] >= 550
    
    # Verify critical files preserved
    assert (workspace / '.git' / 'config').exists()
    assert (workspace / 'src' / 'main.py').exists()
```

---

**Next:** Create migration strategy document with transactional architecture.
