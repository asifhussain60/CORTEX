# CORTEX Toolkit - Maintenance Tools

System maintenance and cleanup utilities.

## Tools

### cleanup-temp (`cortex-cleanup-temp`)

**Purpose:** Clean up temporary files and directories.

**File:** `cleanup_temp_files.py`

**Usage:**
```bash
python cortex-toolkit/maintenance/cleanup_temp_files.py
```

**Features:**
- Remove `__pycache__` directories
- Clean `.pyc` files
- Remove temp log files
- Clear build artifacts

**Safe Cleanup:**
- Preserves active files
- Logs all deletions
- Dry-run mode available

---

### detect-duplicates (`cortex-duplicates`)

**Purpose:** Detect duplicate code across the codebase.

**File:** `detect_duplicates.py`

**Usage:**
```bash
python cortex-toolkit/maintenance/detect_duplicates.py
```

**Features:**
- AST-based duplicate detection
- Similarity scoring
- Refactoring suggestions
- Cross-file analysis

---

### master-cleanup (`cortex-master-cleanup`)

**Purpose:** Master cleanup operation for comprehensive maintenance.

**File:** `master_cleanup.py`

**Usage:**
```bash
python cortex-toolkit/maintenance/master_cleanup.py
```

**Features:**
- Orchestrates all cleanup operations
- Progress tracking
- Safety validations
- Rollback on errors

**Cleanup Steps:**
1. Temp file cleanup
2. Duplicate detection
3. Orphaned code removal
4. Log rotation
5. Cache cleanup

---

## Safety

All maintenance tools:
- Log operations to `logs/toolkit/`
- Support dry-run mode
- Validate before deletion
- Provide rollback capability

## Integration

Maintenance tools integrate with:
- **System Maintenance Orchestrator:** v3.0 workflow
- **Cleanup Rules:** `cortex-brain/aggressive-cleanup-rules.yaml`
- **Brain Protection:** SKULL rules enforcement

## Scheduling

Recommended schedule:
- **Daily:** `cleanup-temp`
- **Weekly:** `detect-duplicates`
- **Monthly:** `master-cleanup`

## Usage in Workflows

```bash
# Part of system maintenance
python cortex-toolkit/maintenance/cleanup_temp_files.py
python cortex-toolkit/maintenance/detect_duplicates.py
python cortex-toolkit/maintenance/master_cleanup.py
```
