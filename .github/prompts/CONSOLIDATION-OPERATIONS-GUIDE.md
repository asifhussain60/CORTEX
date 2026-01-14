# Consolidation Operations Guide

**Version**: 1.0  
**Date**: 2026-01-14  
**Purpose**: Safe, auditable consolidation of folders with validation and recovery support

---

## Overview

The consolidation system consists of two tools working together:

1. **`consolidate.py`** - Consolidates folder and all subfolders into a single machine-readable file
2. **`validate_consolidation.py`** - Validates completeness, generates audit trails, supports recovery

**Key principle**: Validation happens before and after consolidation. The consolidation operation itself should not be run with `--cleanup` flag without validation first.

---

## Safe Consolidation Workflow

### Step 1: Pre-Consolidation Baseline (REQUIRED)

Before running consolidation, capture a baseline of the source folder structure:

```bash
python validate_consolidation.py --folder SSOT/analysis --baseline
```

**What it does**:
- Scans all files in source folder and subfolders
- Records file names, sizes, modification times
- Computes SHA256 hash of each file for integrity verification
- Writes baseline to `.SSOT.analysis.baseline.json` (hidden file)
- Outputs file count and total size statistics

**Output files**:
- `.SSOT.analysis.baseline.json` - Baseline inventory with file hashes

**Duration**: Proportional to folder size (typically <10 seconds for 100 MB)

---

### Step 2: Run Consolidation (Preview Mode First)

First, run consolidation without cleanup to preview what will be consolidated:

```bash
python consolidate.py --folder SSOT/analysis --format yaml
```

**What it does**:
- Recursively reads all files from source folder and subfolders
- Extracts structure and intelligence from each file
- Creates consolidated YAML file in parent directory (`SSOT/analysis.yaml`)
- **Does NOT delete anything**

**Output files**:
- `SSOT/analysis.yaml` - Consolidated machine file with all content

**Verify the consolidation file exists and is readable**:

```bash
ls -lh SSOT/analysis.yaml
wc -l SSOT/analysis.yaml
```

---

### Step 3: Validate Consolidated File (CRITICAL)

After consolidation but before cleanup, validate the consolidated file:

```bash
python validate_consolidation.py --folder SSOT/analysis --validate
```

**What it does**:
- Loads consolidated YAML/JSON file
- Verifies it parses correctly
- Compares file count to baseline
- Checks for missing subfolders
- Verifies metadata consistency
- Generates audit log (`SSOT/analysis.audit.json`)
- Generates recovery manifest (`SSOT/analysis.manifest.json`)

**Output files**:
- `SSOT/analysis.audit.json` - Audit log of validation checks
- `SSOT/analysis.manifest.json` - Recovery manifest with file hashes

**Exit codes**:
- `0` = Validation passed, safe to cleanup
- `1` = Validation failed (errors), DO NOT cleanup
- `2` = Validation passed with warnings, review before cleanup

**If validation fails**: Stop. Do not proceed to cleanup. Review errors in audit log.

---

### Step 4: Run Consolidation with Cleanup (Only If Validation Passes)

If validation passed, run consolidation again with `--cleanup` flag:

```bash
python consolidate.py --folder SSOT/analysis --format yaml --cleanup
```

**Prompts for confirmation**: You must type "yes" to proceed.

**What it does**:
- Writes consolidation file (if not already present)
- Deletes all source files from source folder
- Deletes all empty subfolders
- **Deletes the original source folder**

**After cleanup**:
- `SSOT/analysis/` folder is completely gone
- `SSOT/analysis.yaml` remains in parent directory (`SSOT/`)
- All content is preserved in consolidated file

---

## File Structure After Consolidation

### Before Consolidation
```
SSOT/
  analysis/
    README.md
    overview.md
    reqs/
      requirements.md
      design.md
      implementation.md
    analysis/
      summary.md
      findings.md
```

### After Consolidation
```
SSOT/
  analysis.yaml              ← Single consolidated file with all content
  analysis.audit.json        ← Audit log
  analysis.manifest.json     ← Recovery manifest
  .analysis.baseline.json    ← Baseline (hidden file)
  
  [original analysis/ folder is deleted]
```

---

## Validation Output Explained

### Success Report
```
======================================================================
CONSOLIDATION VALIDATION REPORT
======================================================================

✓ INFO (3):
  • Baseline captured: 25 files, 512,000 bytes
  • Consolidated file parsed successfully
  • File count matches baseline

Status: PASSED (all checks successful)
======================================================================
```

### Failure Report (DO NOT CLEANUP)
```
======================================================================
CONSOLIDATION VALIDATION REPORT
======================================================================

❌ ERRORS (1):
  • File count mismatch: consolidated has 24, baseline had 25 (missing 1)

⚠️  WARNINGS (0):

Status: FAILED (1 error(s))
======================================================================
```

**Action**: Review consolidation for missing files. Check audit log for details.

---

## Recovery Procedures

### If Consolidation File Is Lost or Corrupted

1. **Check manifest file exists**:
   ```bash
   cat SSOT/analysis.manifest.json
   ```

2. **Manifest provides**:
   - Hash of original consolidated file
   - Subfolder list
   - Total file count
   - Recovery instructions

3. **Recovery steps**:
   - If you have a backup of `SSOT/analysis.yaml`, restore it
   - Verify hash matches manifest
   - Revalidate using: `python validate_consolidation.py --folder SSOT/analysis --validate`

### If Source Files Were Only Partially Deleted

1. **Check baseline file**:
   ```bash
   cat .SSOT.analysis.baseline.json | jq '.file_inventory'
   ```

2. **Baseline shows**:
   - Exactly which files should exist
   - Which subfolders existed
   - Original file paths

3. **Recovery**:
   - Identify missing files from baseline
   - Restore from backup if available
   - Or re-create manually from consolidated file

---

## Audit Trail Files

### `.baseline.json` (Hidden)
- Captured before consolidation
- Contains file inventory with hashes
- Used for validation comparison
- Should be kept for compliance/audit purposes

### `.audit.json`
- Generated after validation
- Records all validation checks performed
- Lists any errors or warnings
- Timestamp of validation
- Useful for post-mortems

### `.manifest.json`
- Generated after validation
- Contains hash of consolidated file
- Lists subfolders consolidated
- Recovery instructions
- Useful for recovery scenarios

---

## Operational Guidelines

### Do's
✅ Always run baseline before consolidation  
✅ Always validate after consolidation (before cleanup)  
✅ Review audit logs for warnings  
✅ Keep baseline, audit, and manifest files  
✅ Test on non-critical folders first  
✅ Schedule consolidation during low-activity periods  
✅ Backup entire parent directory before large consolidations  

### Don'ts
❌ Never run cleanup without validation first  
❌ Never delete baseline/audit/manifest files  
❌ Never consolidate read-only filesystems without testing  
❌ Never consolidate while other processes write to folder  
❌ Never ignore validation warnings  
❌ Never assume cleanup succeeded without checking audit log  

---

## Troubleshooting

### "File count mismatch" Error
- **Cause**: Some files failed to read during consolidation
- **Check**: Review `consolidation_timestamp` vs. file modification times
- **Action**: Identify which files failed (in consolidated file errors), restore from backup

### "Missing subfolders" Error
- **Cause**: Subfolder existed in baseline but no files from it in consolidated file
- **Check**: Was subfolder empty? Did files fail to read?
- **Action**: Review baseline to see which files should be in missing subfolder

### Cleanup Failed Partway Through
- **Symptom**: Some files deleted, others remain
- **Check**: Review audit log for "Failed to delete" messages
- **Action**: Manual cleanup of remaining files, or revert from backup

### Validation Passed But Looks Wrong
- **Symptom**: File counts match but content seems incomplete
- **Check**: Open consolidated YAML and search for expected content
- **Action**: Use recovery manifest to reconstruct original file structure

---

## Automation & CI/CD

### Do Not Use in Unattended Context
The consolidation tool requires interactive confirmation. For CI/CD:

1. Create validated consolidation in previous step
2. Verify manually or via script validation
3. Delete source folder explicitly via separate CI step
4. Ensure proper logging and rollback procedures

### Example GitHub Actions Workflow
```yaml
- name: Baseline
  run: python validate_consolidation.py --folder SSOT/analysis --baseline

- name: Consolidate (preview)
  run: python consolidate.py --folder SSOT/analysis --format yaml

- name: Validate
  run: python validate_consolidation.py --folder SSOT/analysis --validate

- name: Verify Validation Passed
  run: |
    if [ $? -eq 0 ]; then
      echo "✓ Validation passed, safe to cleanup"
    else
      echo "✗ Validation failed, aborting cleanup"
      exit 1
    fi

- name: Cleanup (if validation passed)
  run: python consolidate.py --folder SSOT/analysis --format yaml --cleanup
  if: success()
```

---

## Performance Characteristics

### Baseline Capture
- Time: ~0.1-1 second per 100 MB of content
- Memory: ~10 MB overhead
- Disk: Creates small JSON baseline file (~1% of content size)

### Consolidation
- Time: ~1-5 seconds per 100 MB of content
- Memory: Loads all content into memory (must have available RAM)
- Disk: Creates YAML/JSON file (content size × 1.2-1.5× due to encoding)

### Validation
- Time: ~0.1-1 second per 100 MB (quick parse/check)
- Memory: ~5 MB overhead
- Disk: Creates audit and manifest files (~50 KB each)

### Cleanup
- Time: ~1-10 seconds per 1000 files deleted
- Memory: Minimal
- Disk: Frees original folder space

---

## Limits & Constraints

### Safe Operational Limits
- **Recommended maximum folder size**: 500 MB - 1 GB
- **Recommended maximum file count**: 10,000 files
- **Minimum available RAM**: 2x the folder size being consolidated

### Beyond These Limits
- Memory issues likely (no streaming write support yet)
- Cleanup may timeout or fail
- Validation becomes time-consuming
- Consider splitting into smaller consolidations

---

## Summary

**Safe consolidation = Baseline + Consolidate + Validate + Cleanup**

Each step is essential. Skipping validation is the most common cause of data loss in consolidation operations. Use the validation script as a safety interlock that must pass before cleanup is allowed.
