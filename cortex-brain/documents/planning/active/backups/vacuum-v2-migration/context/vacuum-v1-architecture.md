# Vacuum v1 Architecture Analysis

**Date:** 2026-01-02  
**Analyzed By:** CORTEX Planning System v5  
**Source Files:**
- `.github/prompts/cortex-vacuum.prompt.md` (1053 lines - v1 specification)
- `src/operations/modules/vacuum/vacuum_orchestrator.py` (412 lines - v0 implementation)

---

## 🎯 Executive Summary

Vacuum v1 exists in **TWO FORMS**:

1. **v0 (Python)**: BaseOrchestrator implementation focusing on:
   - SQLite database VACUUM operations
   - AST-powered duplicate detection
   - Orphaned test identification
   - Unused import detection

2. **v1 (GUIDED Prompt)**: Comprehensive specification for:
   - 10 filesystem cleanup categories
   - 10-phase execution workflow
   - Safety mechanisms (dry-run, checkpoints, rollback)
   - CORTEX governance integration

**Migration Strategy:** Merge both approaches into v2 autonomous orchestrator

---

## 📦 V0 Implementation Analysis

### Architecture

```python
VacuumOrchestrator(BaseOrchestrator)
├── _register_phases()
│   ├── sqlite_vacuum (required)
│   ├── duplicate_detection (optional)
│   ├── orphaned_tests (optional)
│   ├── unused_imports (optional)
│   └── finalization (required)
├── FilesystemEngine (NOT IMPLEMENTED)
├── ASTEngine (imported from operations/modules/analysis/)
└── DeduplicationAnalyzer (imported)
```

### Implemented Features

#### 1. SQLite VACUUM (✅ Complete)
**File:** `vacuum_orchestrator.py` lines 142-189

**Logic:**
```python
for db_path in self.databases:
    size_before = db_path.stat().st_size
    conn = sqlite3.connect(str(db_path))
    cursor.execute("VACUUM")
    size_after = db_path.stat().st_size
    space_saved = size_before - size_after
```

**Databases:**
- `cortex-brain/conversation-history.db`
- `cortex-brain/cortex-brain.db`
- `cortex_alerts.db`
- `cortex_metrics.db`
- `cortex_status.db`

**Metrics:**
- `space_saved_bytes`
- `databases_vacuumed`
- Error tracking

#### 2. Duplicate Detection (✅ Complete)
**File:** `vacuum_orchestrator.py` lines 191-225

**Delegates to:** `DeduplicationAnalyzer` (AST-based)

**Parameters:**
- Similarity threshold: 85% (hardcoded)
- Minimum lines: 10
- Target path: entire project

**Output:**
- `duplicates_found` (count)
- `duplicate_lines` (total lines)
- `estimated_cleanup_hours`

#### 3. Orphaned Tests (✅ Complete)
**File:** `vacuum_orchestrator.py` lines 227-254

**Logic:** `ASTEngine.find_orphaned_tests()`

**Detection:**
- Test files without corresponding source files
- Returns list of Path objects

#### 4. Unused Imports (✅ Complete)
**File:** `vacuum_orchestrator.py` lines 256-283

**Logic:** `ASTEngine.find_unused_imports()`

**Output:**
- File paths with unused imports
- List of unused import names per file

#### 5. Finalization (✅ Complete)
**File:** `vacuum_orchestrator.py` lines 285-329

**Summary Report:**
- Space saved (bytes → MB)
- Databases vacuumed
- Duplicates found
- Orphaned tests
- Unused imports
- Total issues
- Errors

### Missing Features (From V1 Spec)

❌ **Filesystem cleanup categories** (temp files, build artifacts, IDE metadata, etc.)  
❌ **File reorganization** (misplaced files → correct locations)  
❌ **Checkpoint/rollback system** (backup before execution)  
❌ **Dry-run mode** (preview without execution)  
❌ **Safety validation** (critical file protection)  
❌ **Exclusion patterns** (`.gitignore`, whitelist/blacklist)  
❌ **Risk assessment** (SAFE/LOW/MEDIUM/HIGH/CRITICAL)  
❌ **Interactive confirmations** (HIGH-risk operations)  
❌ **Large binary detection** (>10MB files)  
❌ **Stale log archival** (>30 days)

---

## 📜 V1 Specification Analysis

### 10 Cleanup Categories

#### 1. **Temporary Files** (Priority: HIGH)
**Patterns:**
- `*.tmp`, `*.temp`, `*.cache`
- `~*` (backup files)
- `*.bak`, `*.old`, `*.orig`
- `.DS_Store`, `Thumbs.db`, `desktop.ini`
- `*.swp`, `*.swo`, `*~`

**Action:** DELETE  
**Safety:** Skip if modified <24h (unless `--aggressive`)

#### 2. **Build Artifacts** (Priority: HIGH)
**Patterns:**
- `bin/`, `obj/`, `target/`, `build/`, `dist/`
- `node_modules/`, `__pycache__/`
- `*.pyc`, `*.pyo`
- `.pytest_cache/`, `htmlcov/`, `.tox/`, `.mypy_cache/`

**Action:** DELETE  
**Rationale:** Reproducible, should not be in git

#### 3. **IDE Metadata** (Priority: MEDIUM)
**Patterns:**
- `.vs/`, `.vscode/settings.json`, `.idea/`
- `*.suo`, `*.user`, `*.iml`
- `.project`, `.classpath`

**Exclusions:**
- `.vscode/launch.json`, `.vscode/tasks.json` (custom configs)
- `.github/` (CI/CD)
- `.copilot-instructions.md`

**Action:** DELETE (selective)

#### 4. **Duplicate Files** (Priority: MEDIUM)
**Detection:**
- Same filename in multiple locations
- Same content hash (SHA256)
- Near-duplicates (>95% similarity)

**Actions:**
- Keep newest version OR
- Keep "correct location" per CORTEX governance
- Create symlinks for legitimate duplicates

#### 5. **Orphaned Files** (Priority: MEDIUM)
**Detection:**
- Test files with no source file
- Config for removed dependencies
- Documentation for deleted modules
- Unused imports/references

**Actions:**
- Report (don't auto-delete)
- Archive for 30 days
- User confirmation required

#### 6. **Large Binary Files** (Priority: LOW)
**Patterns:**
- `*.zip`, `*.tar`, `*.gz`
- `*.exe`, `*.dll`, `*.so`
- `*.pdf`, `*.docx`
- `*.mp4`, `*.avi`
- `*.psd`, `*.ai`

**Actions:**
- Move to appropriate location (`docs/`, `assets/`)
- Warn if >10MB in source tree
- Suggest Git LFS

#### 7. **Misplaced Files** (Priority: HIGH - CORTEX)
**CORTEX Governance Rules:**
- Root-level docs → `cortex-brain/documents/{category}/`
- Application code in CORTEX → user repo or archive
- Brain state files → exclude from git
- Tests in wrong location → proper test structure
- Planning artifacts → `cortex-brain/documents/planning/`

**Reorganization Map:**
```
❌ CORTEX/summary.md → ✅ cortex-brain/documents/summaries/summary.md
❌ CORTEX/analysis.txt → ✅ cortex-brain/documents/analysis/analysis.txt
❌ CORTEX/plan.yaml → ✅ cortex-brain/documents/planning/active/{plan}/plan.yaml
```

#### 8. **Stale Log Files** (Priority: MEDIUM)
**Rules:**
- `*.log` older than 30 days → archive
- Archive logs → `logs/archive/YYYY-MM/`
- Compress archived logs (gzip)
- Delete logs older than 6 months

#### 9. **Empty Directories** (Priority: LOW)
**Rules:**
- Delete directories with no files (after cleanup)
- Keep if `.gitkeep` present
- Keep if required by framework (`migrations/`, `uploads/`)

#### 10. **Outdated Dependencies** (Priority: LOW)
**Detection:**
- `requirements.txt` packages not imported
- `package.json` dependencies not used
- Pinned versions with vulnerabilities

**Actions:**
- Report only (don't auto-remove)
- Suggest version updates
- Run `pip-audit` or `npm audit`

---

## 🔄 10-Phase Workflow

### Phase 1: Discovery & Inventory (No modifications)
**Actions:**
1. Traverse target path recursively
2. Catalog all files/directories
3. Calculate sizes, modification dates, git status
4. Generate `vacuum-inventory.json`

**Output:**
```json
{
  "scan_date": "2025-12-31T10:00:00Z",
  "target_path": "d:\\PROJECTS\\CORTEX",
  "total_files": 15420,
  "total_size_mb": 1250.5,
  "total_directories": 420
}
```

### Phase 2: Classification (No modifications)
**Actions:**
1. Apply cleanup rules to each file
2. Categorize by cleanup category (1-10)
3. Flag for: DELETE, MOVE, ARCHIVE, WARN, KEEP
4. Calculate impact (disk space recovered)

### Phase 3: Conflict Detection (No modifications)
**Actions:**
1. Check for move conflicts (target exists)
2. Validate reorganization paths exist
3. Detect circular dependencies
4. Check file locks
5. Verify permissions

### Phase 4: Risk Assessment (No modifications)
**Actions:**
1. Identify critical files flagged for deletion
2. Check git status (uncommitted changes)
3. Validate against CORTEX governance
4. Calculate rollback complexity
5. Estimate recovery time

**Risk Levels:**
- SAFE: Temp files, caches, build artifacts
- LOW: Duplicates, empty directories, old logs
- MEDIUM: Misplaced files, large binaries
- HIGH: Orphaned files, IDE metadata (if custom)
- CRITICAL: Uncommitted changes, recent modifications

### Phase 5: Dry-Run Report (No modifications)
**Actions:**
1. Generate human-readable report
2. Show before/after comparison
3. Highlight high-risk operations
4. Provide undo commands

**Output:** `vacuum-dry-run-report.md`

### Phase 6: Checkpoint Creation
**Actions:**
1. Create `.vacuum-checkpoint-{timestamp}/` directory
2. Copy all files flagged for DELETE/MOVE
3. Generate restoration manifest
4. Create undo script

### Phase 7: Safe Deletions (SAFE + LOW risk)
**Actions:**
1. Delete temporary files
2. Delete build artifacts
3. Delete caches
4. Delete empty directories

**Safety:**
- Skip if modified <24h (unless `--aggressive`)
- Skip if git status is "modified"
- Log every deletion

### Phase 8: File Reorganization (MEDIUM risk)
**Actions:**
1. Move misplaced files to correct locations
2. Resolve conflicts (rename if target exists)
3. Update internal references (imports, paths)
4. Validate moves completed

### Phase 9: High-Risk Operations (Requires confirmation)
**Actions:**
1. Handle orphaned files
2. Remove duplicates
3. Delete large binaries
4. Clean IDE metadata

**Confirmation Required:** Unless `--aggressive`

### Phase 10: Validation & Report
**Actions:**
1. Traverse filesystem again
2. Check for missed files
3. Validate reorganization paths
4. Generate final report
5. Update `.gitignore`

---

## 🛡️ Safety Mechanisms

### 1. Dry-Run First (Default)
- All operations preview-only until approved
- `--dry-run=false` required for execution

### 2. Checkpoint System
- Full backup before modifications
- Automated rollback script
- Retained for 30 days

### 3. Git Integration
- Never delete uncommitted changes
- Respect `.gitignore` patterns
- Preserve git metadata
- Optional pre-vacuum git commit

### 4. Whitelist/Blacklist
**Config:** `.vacuum-config.yaml`
```yaml
whitelist:
  - "*.md"
  - "docs/**"
  
blacklist:
  - "*.tmp"
  - "__pycache__/"
  
protected_paths:
  - ".git"
  - ".github"
  - "cortex-brain/tier0"
```

### 5. Confirmation Prompts
- HIGH/CRITICAL risk requires confirmation
- `--aggressive` bypasses prompts
- `--interactive=false` for CI/CD

### 6. Error Recovery
- Atomic operations (all or nothing per phase)
- Failed operations logged
- Partial rollback if phase fails

---

## ⚠️ Edge Cases & Vulnerabilities

### Edge Cases (from V1 spec)

1. **Symlinks & Hard Links** - Preserve targets, detect broken links
2. **Circular Dependencies** - Build dependency graph, detect cycles
3. **Open/Locked Files** - Check locks, skip locked files
4. **Case-Sensitive Filesystems** - Normalize paths, handle collisions
5. **Very Large Directories** - Stream processing, batching (1K files)
6. **Network/Cloud Paths** - Async I/O, timeout handling
7. **Unicode & Special Characters** - UTF-8 encoding, normalization
8. **Permissions & Ownership** - Check permissions, elevate if needed

### Security Vulnerabilities (from V1 spec)

1. **Path Traversal** - Validate paths, block system directories
2. **Symlink Attack** - Never follow symlinks outside target
3. **Command Injection** - Use OS-native APIs, no shell
4. **Information Disclosure** - Sanitize paths in reports
5. **Privilege Escalation** - Warn if root, preserve permissions

### Performance Bottlenecks

1. **Sequential Processing** - Parallelize discovery (thread pool)
2. **Duplicate Detection** - Hash-based (size filter → hash → compare)
3. **Git Status Checks** - Use `git ls-files`, cache results
4. **Report Generation** - Stream to disk, templates

---

## 🏗️ V2 Migration Strategy

### Merge V0 + V1 Features

**From V0 (Keep):**
- ✅ BaseOrchestrator integration
- ✅ SQLite VACUUM logic
- ✅ AST-powered duplicate detection
- ✅ Orphaned test detection
- ✅ Unused import detection
- ✅ Finalization/summary report

**From V1 (Add):**
- ✅ 10 filesystem cleanup categories
- ✅ 10-phase execution workflow
- ✅ Checkpoint/rollback system
- ✅ Dry-run mode
- ✅ Safety validation
- ✅ Exclusion patterns
- ✅ Risk assessment
- ✅ Interactive confirmations
- ✅ CORTEX governance integration
- ✅ File reorganization

### New Architecture (V2)

```python
VacuumOrchestratorV2(BaseOrchestratorV4_1)
├── execute() → 6-phase workflow
│   ├── DISCOVERY
│   ├── ANALYSIS
│   ├── PLANNING (safety validation)
│   ├── APPROVAL (if not auto-approved)
│   ├── EXECUTION (or dry-run report)
│   └── COMPLETION
├── FilesystemEngine (NEW)
│   ├── scan_directory()
│   ├── FilesystemTransaction
│   ├── CheckpointManager
│   ├── DuplicateDetector
│   └── OrphanDetector
├── SafetyValidator (NEW)
│   ├── validate_critical_files()
│   ├── check_git_status()
│   └── check_permissions()
└── CleanupHandlers (NEW)
    ├── TempFileCleaner
    ├── BuildArtifactCleaner
    ├── IDEMetadataCleaner
    ├── DuplicateRemover
    └── OrphanHandler
```

### Configuration-Driven (Manifest)

**File:** `cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml`

**Content:**
- Cleanup categories with patterns
- Safety rules (critical patterns, thresholds)
- Exclusion patterns
- Output templates

**Zero Python Logic in Manifest** - Pure configuration data

---

## 📊 Comparison Matrix

| Feature | V0 (Python) | V1 (Prompt) | V2 (Target) |
|---------|-------------|-------------|-------------|
| **SQLite VACUUM** | ✅ Complete | ❌ Not specified | ✅ Keep |
| **Duplicate Detection** | ✅ AST-based | ✅ Hash + similarity | ✅ Merge both |
| **Orphaned Tests** | ✅ AST-based | ✅ Broader scope | ✅ Merge |
| **Unused Imports** | ✅ AST-based | ✅ Implied | ✅ Keep |
| **Temp Files** | ❌ | ✅ 10 patterns | ✅ Add |
| **Build Artifacts** | ❌ | ✅ 10 patterns | ✅ Add |
| **IDE Metadata** | ❌ | ✅ With exclusions | ✅ Add |
| **Large Binaries** | ❌ | ✅ >10MB warning | ✅ Add |
| **Misplaced Files** | ❌ | ✅ CORTEX governance | ✅ Add |
| **Stale Logs** | ❌ | ✅ 30-day archive | ✅ Add |
| **Empty Directories** | ❌ | ✅ .gitkeep aware | ✅ Add |
| **Dry-Run Mode** | ❌ | ✅ Default | ✅ Add |
| **Checkpoints** | ❌ | ✅ Pre-execution | ✅ Add |
| **Rollback** | ❌ | ✅ Automated | ✅ Add |
| **Risk Assessment** | ❌ | ✅ 5 levels | ✅ Add |
| **Git Integration** | ❌ | ✅ Status checks | ✅ Add |
| **Safety Validation** | ❌ | ✅ Critical patterns | ✅ Add |
| **Config-Driven** | ❌ Hardcoded | ✅ YAML config | ✅ Add |
| **Master Orch** | ❌ | ❌ | ✅ Add |

---

## 🎯 Key Takeaways

1. **V0 is AST-focused** (code analysis), **V1 is filesystem-focused** (file operations)
2. **V2 must merge both** to provide comprehensive vacuum functionality
3. **Safety is critical** - Dry-run, checkpoints, rollback, git integration
4. **CORTEX governance** must be enforced (misplaced files, brain protection)
5. **Performance matters** - Parallel processing, streaming, caching
6. **Configuration-driven** - Externalize rules to YAML, zero Python logic in manifest

---

**Next:** Create filesystem operations patterns document and migration strategy.
