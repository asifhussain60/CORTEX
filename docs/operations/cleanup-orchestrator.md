# CORTEX Cleanup Orchestrator

**Version:** 1.0.0  
**Status:** ✅ PRODUCTION READY  
**Module:** `src/operations/modules/cleanup/cleanup_orchestrator.py`  
**CLI:** `cleanup_workspace.py`

---

## Overview

The Cleanup Orchestrator provides comprehensive workspace maintenance for CORTEX with:

- **Backup Management** - Archive backups to GitHub before deletion
- **Root Folder Organization** - Keep root folder clean and organized
- **File Reorganization** - Move files to correct locations
- **MD File Consolidation** - Remove duplicate markdown files
- **Bloat Detection** - Identify oversized entry points and orchestrators
- **Automatic Optimization** - Trigger optimization orchestrator after cleanup
- **Git Tracking** - All changes tracked with descriptive commits

---

## Quick Start

### Basic Usage

```bash
# Standard cleanup (recommended)
python cleanup_workspace.py

# Quick cleanup (backups + root only)
python cleanup_workspace.py --profile quick

# Comprehensive cleanup (everything + optimization)
python cleanup_workspace.py --profile comprehensive

# Preview changes without executing
python cleanup_workspace.py --dry-run
```

### Natural Language

From GitHub Copilot Chat:

```
cleanup
clean workspace
organize workspace
remove backups
consolidate files
```

### Python API

```python
from src.operations.modules.cleanup import CleanupOrchestrator

orchestrator = CleanupOrchestrator(project_root=Path('./'))
result = orchestrator.execute({
    'profile': 'standard',
    'dry_run': False
})

print(f"Backups deleted: {result.data['metrics']['backups_deleted']}")
print(f"Space freed: {result.data['metrics']['space_freed_mb']:.2f}MB")
```

---

## Execution Profiles

### Quick Profile (2-3 minutes)

**What it does:**
- ✅ Delete backup files (with GitHub archival)
- ✅ Clean root folder
- ✅ Safety verification

**When to use:**
- Daily maintenance
- Before committing changes
- Quick workspace tidying

**Command:**
```bash
python cleanup_workspace.py --profile quick
```

---

### Standard Profile (5-7 minutes) **[RECOMMENDED]**

**What it does:**
- ✅ Delete backup files (with GitHub archival)
- ✅ Clean root folder
- ✅ Reorganize misplaced files
- ✅ Safety verification

**When to use:**
- Weekly maintenance
- After major development work
- Regular workspace organization

**Command:**
```bash
python cleanup_workspace.py --profile standard
```

---

### Comprehensive Profile (10-15 minutes)

**What it does:**
- ✅ Delete backup files (with GitHub archival)
- ✅ Clean root folder
- ✅ Reorganize misplaced files
- ✅ Consolidate duplicate MD files
- ✅ Detect bloated files
- ✅ Trigger optimization orchestrator
- ✅ Safety verification

**When to use:**
- Monthly maintenance
- Major cleanup sessions
- Before releases

**Command:**
```bash
python cleanup_workspace.py --profile comprehensive
```

---

## Cleanup Operations

### 1. Backup Management

**Backup Patterns:**
```
*.bak, *.backup, *.old
*_backup_*, *_old_*
*.orig, *-BACKUP-*, *BACKUP*
```

**Process:**
1. Scan workspace for backup files
2. Archive to `.backup-archive/` with manifest
3. Commit archive to GitHub
4. Push to remote
5. Delete local backup files
6. Log all actions

**Safety:**
- ✅ GitHub archival before deletion
- ✅ Manifest file tracks all archived files
- ✅ Commit message includes count and timestamp
- ✅ Protected paths never touched

**Example:**
```
Found 15 backup files:
  file1.bak (125KB)
  file2.backup (89KB)
  ...

✅ Archived 15 backups to GitHub (commit: abc123)
✅ Deleted 15 local backups (freed 1.8MB)
```

---

### 2. Root Folder Cleanup

**Allowed Root Files:**
```
README.md, LICENSE, CHANGELOG.md
package.json, tsconfig.json, pytest.ini
requirements.txt, cortex.config.json
cortex-operations.yaml, mkdocs.yml
```

**Misplaced Files Moved To:**
- Python scripts → `scripts/temp/`
- Documentation → `docs/summaries/`
- Implementation details → `docs/implementation/`
- Planning docs → `docs/planning/`

**Example:**
```
Root folder scan:
  ❌ execute_something.py → scripts/temp/
  ❌ fix_imports.py → scripts/temp/
  ❌ PROJECT-SUMMARY.md → docs/summaries/
  ✅ README.md (kept)
  ✅ package.json (kept)

✅ Moved 3 files from root
```

---

### 3. File Reorganization

**Reorganization Rules:**
```yaml
# Python scripts
'*_(fix|execute|test|demo|show|verify|validate)*.py': 'scripts/temp/'

# Documentation
'*-(SUMMARY|STATUS|REPORT|ANALYSIS)*.md': 'docs/summaries/'
'*-IMPLEMENTATION*.md': 'docs/implementation/'
'*-(PLAN|ROADMAP|DESIGN)*.md': 'docs/planning/'
```

**Example:**
```
File reorganization:
  execute_refactor.py → scripts/temp/
  PROJECT-STATUS.md → docs/summaries/
  IMPLEMENTATION-SUMMARY.md → docs/implementation/
  ROADMAP-2025.md → docs/planning/

✅ Reorganized 4 files
```

---

### 4. MD File Consolidation

**Consolidation Patterns:**
```python
'filename-v2.md'     → 'filename.md'  # Version numbers
'filename-20250101.md' → 'filename.md'  # Dates
'filename-COPY.md'    → 'filename.md'  # Copies
```

**Process:**
1. Detect duplicate MD files
2. Keep newest version
3. Archive older versions to `docs/archive/consolidated/`
4. Log consolidation

**Example:**
```
MD consolidation:
  Consolidating 3 versions of plan.md:
    ✅ Keeping: plan.md (newest)
    📦 Archived: plan-v1.md
    📦 Archived: plan-v2.md
    📦 Archived: plan-COPY.md

✅ Consolidated 3 MD files
```

---

### 5. Bloat Detection

**Thresholds:**
- **Entry Points:** 3,000 tokens (~12KB)
- **Orchestrators:** 5,000 tokens (~20KB)
- **Modules:** 2,000 tokens (~8KB)

**Process:**
1. Scan entry points in `prompts/`
2. Scan orchestrators in `src/operations/modules/`
3. Calculate token count (1 token ≈ 4 characters)
4. Report files exceeding thresholds
5. Save bloat report to `logs/cleanup/bloat-report-{timestamp}.json`

**Example:**
```json
{
  "timestamp": "2025-11-11T10:30:00",
  "bloated_files": [
    {
      "path": "prompts/CORTEX.prompt.md",
      "type": "entry_points",
      "tokens": 4500,
      "threshold": 3000,
      "excess": 1500,
      "excess_percent": 50.0
    }
  ],
  "summary": {
    "total_bloated": 3,
    "entry_points": 1,
    "orchestrators": 2,
    "modules": 0
  }
}
```

**Recommendations:**
- Break large files into modules
- Extract reusable components
- Use references instead of duplication
- Move detailed examples to separate docs

---

### 6. Git Tracking

**Commit Message Format:**
```
[CLEANUP] Workspace cleanup - {timestamp}

Automated cleanup performed:
- Backups: {count} deleted (archived to GitHub)
- Root folder: {count} files moved
- Files reorganized: {count}
- MD files consolidated: {count}
- Bloated files detected: {count}
- Space freed: {size}MB

Duration: {time}s
```

**Example:**
```bash
git log -1

commit abc123def456
Author: CORTEX Cleanup <cleanup@cortex>
Date:   Mon Nov 11 10:30:00 2025

    [CLEANUP] Workspace cleanup - 2025-11-11 10:30:00
    
    Automated cleanup performed:
    - Backups: 15 deleted (archived to GitHub)
    - Root folder: 3 files moved
    - Files reorganized: 4
    - MD files consolidated: 3
    - Bloated files detected: 2
    - Space freed: 2.5MB
    
    Duration: 8.5s
```

---

### 7. Optimization Integration

**When Triggered:**
- Only in **comprehensive profile**
- After successful cleanup
- Unless `--no-optimize` flag used

**Process:**
1. Cleanup completes successfully
2. Trigger OptimizeCortexOrchestrator
3. Use optimization profile from context (default: `standard`)
4. Log optimization result

**Example:**
```
Phase 8: Optimization Orchestrator
----------------------------------------------------------------------
Triggering optimization orchestrator...

Running SKULL tests...
✅ 82 tests passed

Analyzing architecture...
✅ 6 analyzers completed

Generating optimization plan...
✅ 12 optimizations planned

✅ Optimization orchestrator triggered
```

---

## Safety Mechanisms

### Protected Paths

**Never Touched:**
```python
protected_paths = {
    'src/', 'tests/', 'cortex-brain/', 'docs/',
    'prompts/', 'workflows/', 'scripts/', '.git/',
    '.github/', '.vscode/', 'node_modules/',
    'package.json', 'tsconfig.json', 'pytest.ini',
    'requirements.txt', 'cortex.config.json',
    'LICENSE', 'README.md', 'CHANGELOG.md',
    # ... and more
}
```

### Safety Verification

**Pre-Cleanup Checks:**
1. ✅ Verify project root exists
2. ✅ Verify git repository exists
3. ✅ Check all protected paths preserved
4. ✅ Verify no actions target critical files

**Failure Handling:**
- ❌ Abort if safety check fails
- 📝 Log all violations
- 🔒 Never proceed with unsafe operations

---

## Metrics & Reporting

### Metrics Collected

```python
{
  'timestamp': '2025-11-11T10:30:00',
  'backups_deleted': 15,
  'backups_archived': 15,
  'root_files_cleaned': 3,
  'files_reorganized': 4,
  'md_files_consolidated': 3,
  'bloated_files_found': 2,
  'space_freed_bytes': 2621440,
  'space_freed_mb': 2.5,
  'space_freed_gb': 0.0024,
  'git_commits_created': 1,
  'duration_seconds': 8.5,
  'optimization_triggered': True,
  'warnings': [],
  'errors': []
}
```

### Actions Log

Every action logged with:
```python
{
  'action': 'backup_deleted',
  'path': 'file.bak',
  'reason': 'Archived to GitHub (commit: abc123)',
  'timestamp': '2025-11-11T10:30:05'
}
```

### Report Output

Saved to `logs/cleanup/cleanup-{timestamp}.json`:
```json
{
  "timestamp": "2025-11-11T10:30:00",
  "metrics": { ... },
  "actions_count": 25,
  "recommendations": [
    "Found 2 bloated files. Consider refactoring.",
    "Freed 2.5MB. Consider running cleanup weekly."
  ],
  "success": true
}
```

---

## CLI Reference

### Command Options

```bash
python cleanup_workspace.py [OPTIONS]
```

**Options:**

| Option | Choices | Default | Description |
|--------|---------|---------|-------------|
| `--profile` | quick, standard, comprehensive | standard | Cleanup profile |
| `--dry-run` | - | False | Preview without executing |
| `--no-optimize` | - | False | Skip optimization trigger |
| `--optimize-profile` | quick, standard, comprehensive | standard | Optimization profile |
| `--verbose` | - | False | Detailed logging |

### Examples

**Standard cleanup:**
```bash
python cleanup_workspace.py
```

**Quick cleanup:**
```bash
python cleanup_workspace.py --profile quick
```

**Comprehensive with custom optimization:**
```bash
python cleanup_workspace.py --profile comprehensive --optimize-profile quick
```

**Preview comprehensive cleanup:**
```bash
python cleanup_workspace.py --profile comprehensive --dry-run
```

**Skip optimization:**
```bash
python cleanup_workspace.py --profile comprehensive --no-optimize
```

**Verbose logging:**
```bash
python cleanup_workspace.py --verbose
```

---

## Best Practices

### Regular Maintenance Schedule

**Daily:**
```bash
python cleanup_workspace.py --profile quick
```
- Quick (2-3 min)
- Keeps workspace tidy
- Prevents backup accumulation

**Weekly:**
```bash
python cleanup_workspace.py --profile standard
```
- Standard (5-7 min)
- Reorganizes files
- Maintains structure

**Monthly:**
```bash
python cleanup_workspace.py --profile comprehensive
```
- Comprehensive (10-15 min)
- Full optimization
- Major cleanup

### Pre-Commit Hook

**Install:**
```bash
# Add to .git/hooks/pre-commit
python cleanup_workspace.py --profile quick --dry-run
```

**Benefits:**
- Catches bloat before commit
- Validates workspace structure
- Prevents backup files in commits

### CI/CD Integration

**GitHub Actions:**
```yaml
- name: Cleanup Workspace
  run: python cleanup_workspace.py --profile standard
  
- name: Commit Cleanup
  run: |
    git config user.name "CORTEX Cleanup"
    git config user.email "cleanup@cortex"
    git push
```

---

## Troubleshooting

### Issue: "Safety check failed"

**Cause:** Protected files at risk

**Solution:**
```bash
# Check violations
python cleanup_workspace.py --dry-run --verbose

# Review protected paths
grep "protected_paths" src/operations/modules/cleanup/cleanup_orchestrator.py
```

### Issue: "GitHub archival failed"

**Cause:** Git operations failed

**Solution:**
```bash
# Check git status
git status

# Verify remote connection
git remote -v

# Manual commit
git add .backup-archive/
git commit -m "Manual backup archive"
git push
```

### Issue: "Optimization failed"

**Cause:** Optimization orchestrator unavailable

**Solution:**
```bash
# Run cleanup without optimization
python cleanup_workspace.py --profile comprehensive --no-optimize

# Manually run optimization
python optimize_cortex.py --profile standard
```

### Issue: "Bloated files detected"

**Cause:** Files exceed token thresholds

**Solution:**
```bash
# Review bloat report
cat logs/cleanup/bloat-report-*.json

# Refactor large files
# - Break into modules
# - Extract reusable components
# - Use references instead of duplication
```

---

## Architecture

### Module Structure

```
src/operations/modules/cleanup/
├── __init__.py
└── cleanup_orchestrator.py

cleanup_workspace.py (CLI entry point)
tests/operations/test_cleanup_orchestrator.py
docs/operations/cleanup-orchestrator.md (this file)
```

### Dependencies

```python
# Standard library
pathlib, datetime, json, shutil, subprocess, logging, re, hashlib

# CORTEX
src.operations.base_operation_module
src.operations.modules.optimization (optional)
```

### Integration Points

**With Git:**
- Archive commits
- Cleanup commits
- Status checks

**With Optimization:**
- Automatic trigger (comprehensive profile)
- Configurable optimization profile
- Failure handling

**With Operations System:**
- BaseOperationModule inheritance
- OperationResult return type
- Phase-based execution

---

## Future Enhancements

### Phase 1 (Next Month)

- [ ] **Smart backup retention** - Keep last N backups
- [ ] **Compression** - Compress archived backups
- [ ] **Statistics dashboard** - Track cleanup metrics over time

### Phase 2 (Quarter 2)

- [ ] **AI-powered file classification** - Auto-categorize misplaced files
- [ ] **Duplicate content detection** - Detect duplicates by content, not just name
- [ ] **Interactive mode** - Confirm actions before executing

### Phase 3 (Quarter 3)

- [ ] **Cloud backup** - Archive to cloud storage
- [ ] **Scheduled cleanup** - Cron/scheduled task integration
- [ ] **Cleanup policies** - Customizable rules per project

---

## Changelog

### v1.0.0 (2025-11-11)

**Initial Release:**
- ✅ Backup management with GitHub archival
- ✅ Root folder organization
- ✅ File reorganization
- ✅ MD file consolidation
- ✅ Bloat detection
- ✅ Optimization integration
- ✅ Git tracking
- ✅ Comprehensive test suite (25 tests)
- ✅ CLI with 3 profiles
- ✅ Complete documentation

---

**Status:** Production Ready ✅  
**Last Updated:** 2025-11-11  
**Author:** Asif Hussain
