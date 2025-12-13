# CORTEX Patch Release Strategy

**Version:** 1.0  
**Created:** 2025-12-01  
**Author:** Asif Hussain  
**Purpose:** Lightweight deployment for bug fixes and incremental updates without full reinstall

---

## 🎯 Overview

**Problem:** Current `deploy_cortex.py` always publishes complete CORTEX package. For bug fixes or small feature additions, users must re-setup entirely - this is heavyweight, time-consuming, and carries risk of disrupting working installations.

**Solution:** Implement patch release system allowing incremental updates:
- Version format: `X.Y.Z` where Z = patch number
- Patch includes only changed files + manifest
- Users run `cortex patch apply` to incrementally update
- Full rollback capability: `cortex patch rollback <version>`
- Preserves brain data and user configurations

---

## 📐 Design

### Version Format

**Semantic Versioning Extended:**
- `X.Y.Z` - Major.Minor.Patch
- Example: `3.4.1` = CORTEX 3.4 with patch 1
- Patch increments for bug fixes, minor updates
- Minor/Major increments trigger full deployment

### Patch Types

**1. Hot-Fix Patch** (Critical bug fix)
- Single file or small group of files
- No new features
- Applied immediately without validation gates
- Example: Fix crash in feedback agent

**2. Feature Patch** (Small enhancement)
- New capability without architecture changes
- Runs subset of validation gates (Gates 1-4, 12)
- Example: Add new CLI command

**3. Security Patch** (Vulnerability fix)
- Security-related updates
- Runs security-focused gates (Gates 3, 5, 12)
- Tagged as security release

### Patch Manifest

**Structure:**
```json
{
  "patch_id": "3.4.1",
  "base_version": "3.4.0",
  "patch_type": "hotfix|feature|security",
  "created": "2025-12-01T14:30:00Z",
  "author": "Asif Hussain",
  "description": "Fix feedback agent crash on empty context",
  "files": [
    {
      "path": "src/cortex_agents/feedback_agent.py",
      "operation": "update|add|delete",
      "checksum": "sha256:abc123...",
      "size_bytes": 4567
    }
  ],
  "validation_gates": [1, 3, 12],
  "rollback_data": {
    "previous_checksums": {
      "src/cortex_agents/feedback_agent.py": "sha256:def456..."
    }
  }
}
```

---

## 🛠️ Implementation

### Phase 8.4 Deliverable Breakdown

**File Structure:**
```
scripts/
  ├── patch_builder.py          # Creates patch packages
  └── deploy_cortex.py          # Enhanced with --patch flag

src/orchestrators/
  └── patch_orchestrator.py     # Applies/rolls back patches

cortex-brain/
  └── patches/                  # Patch storage
      ├── 3.4.1/
      │   ├── manifest.json
      │   └── files/
      │       └── src/cortex_agents/feedback_agent.py
      └── 3.4.2/
          └── ...

tests/orchestrators/
  └── test_patch_orchestrator.py
```

### Components

#### 1. Patch Builder (`scripts/patch_builder.py`)

**Responsibilities:**
- Detect changed files since last release (git diff)
- Calculate checksums for validation
- Create patch manifest
- Package files into patch directory
- Generate rollback data

**Usage:**
```bash
# Create patch for current changes
python scripts/patch_builder.py --version 3.4.1 --type hotfix

# Create patch from specific commit range
python scripts/patch_builder.py --version 3.4.1 --from v3.4.0 --to HEAD

# Preview without creating
python scripts/patch_builder.py --version 3.4.1 --dry-run
```

**Output:**
```
✅ Patch 3.4.1 created successfully

Files included (2):
  • src/cortex_agents/feedback_agent.py (updated)
  • tests/cortex_agents/test_feedback_agent.py (updated)

Manifest: cortex-brain/patches/3.4.1/manifest.json
Package size: 12.4 KB

To publish: python scripts/deploy_cortex.py --patch 3.4.1
```

#### 2. Patch Orchestrator (`src/orchestrators/patch_orchestrator.py`)

**Responsibilities:**
- List available patches
- Apply patches with validation
- Rollback to previous versions
- Verify checksums before/after operations
- Backup original files

**Natural Language Commands:**
```
"cortex patch list"           # Show available patches
"cortex patch info 3.4.1"     # Show patch details
"cortex patch apply 3.4.1"    # Apply specific patch
"cortex patch apply latest"   # Apply newest patch
"cortex patch rollback 3.4.0" # Rollback to version
"cortex patch status"         # Show current version + available patches
```

**Apply Workflow:**
```
User: "cortex patch apply 3.4.1"

CORTEX:
  🔍 Validating patch 3.4.1...
  ✅ Patch compatible with current version (3.4.0)
  ✅ All files present and checksums valid
  
  Changes to be applied:
    • src/cortex_agents/feedback_agent.py (updated)
    • tests/cortex_agents/test_feedback_agent.py (updated)
  
  📸 Creating backup checkpoint...
  ✅ Backup created: .cortex-backup-3.4.0
  
  Applying patch...
  ✅ Files updated successfully
  ✅ Checksums verified
  
  Running validation gates (3 gates)...
  ✅ Gate 1: Code Quality (passed)
  ✅ Gate 3: Test Coverage (passed)
  ✅ Gate 12: Deploy Manifest (passed)
  
  ✅ Patch 3.4.1 applied successfully
  
  Current version: 3.4.0 → 3.4.1
  
  To rollback: cortex patch rollback 3.4.0
```

**Rollback Workflow:**
```
User: "cortex patch rollback 3.4.0"

CORTEX:
  ⚠️  ROLLBACK WARNING
  
  This will restore version 3.4.0 (previous state)
  
  Changes to be reversed:
    • src/cortex_agents/feedback_agent.py (restore)
    • tests/cortex_agents/test_feedback_agent.py (restore)
  
  Type 'yes' to confirm: yes
  
  📸 Creating safety checkpoint...
  ✅ Safety checkpoint: .cortex-rollback-3.4.1
  
  Restoring files from backup...
  ✅ Files restored
  ✅ Checksums verified
  
  ✅ Rolled back to version 3.4.0
  
  To re-apply: cortex patch apply 3.4.1
```

#### 3. Enhanced Deployment Script

**New Flag:** `--patch <version>`

**Modified `deploy_cortex.py`:**
```python
# Add patch mode argument
parser.add_argument('--patch', type=str, help='Deploy as patch release (version)')

# Modified validation for patch mode
def run_validation_gates(patch_mode=False):
    if patch_mode:
        # Subset of gates for patch releases
        gates = [1, 3, 12]  # Code Quality, Test Coverage, Manifest
    else:
        # All 16 gates for full releases
        gates = range(1, 17)
    
    for gate_num in gates:
        run_gate(gate_num)
```

**Usage:**
```bash
# Full deployment (all 16 gates)
python scripts/deploy_cortex.py

# Patch deployment (gates 1, 3, 12 only)
python scripts/deploy_cortex.py --patch 3.4.1
```

---

## ✅ Acceptance Criteria

**Patch Builder:**
- ✅ Detects changed files since last release (git diff)
- ✅ Calculates SHA256 checksums for validation
- ✅ Creates valid manifest with all required fields
- ✅ Packages files into patch directory
- ✅ Generates rollback data (previous checksums)
- ✅ Supports dry-run mode for preview
- ✅ Validates patch applies cleanly before committing

**Patch Orchestrator:**
- ✅ Lists available patches sorted by version
- ✅ Shows patch details (files, operations, size)
- ✅ Validates current version before applying
- ✅ Creates backup checkpoint before changes
- ✅ Updates only changed files (preserves brain data)
- ✅ Verifies checksums after operations
- ✅ Rollback restores exact previous file versions
- ✅ Runs validation gates appropriate to patch type
- ✅ Updates VERSION file after successful apply

**Deployment Integration:**
- ✅ deploy_cortex.py accepts --patch flag
- ✅ Patch releases skip heavy gates (setup validation)
- ✅ Patch releases run critical gates (quality, coverage, manifest)
- ✅ Patch releases tagged in git: vX.Y.Z-patch
- ✅ Users receive notification of available patches

**Testing:**
- ✅ Unit tests for patch builder (manifest generation)
- ✅ Unit tests for patch orchestrator (apply/rollback)
- ✅ Integration test: Create patch → Apply → Validate → Rollback
- ✅ Edge case: Apply patch on modified installation (warning)
- ✅ Edge case: Rollback when backup missing (error handling)
- ✅ Performance: Patch apply <10 seconds for typical patch

---

## 🔧 Configuration

**New Config Section in `cortex.config.json`:**
```json
{
  "patch_system": {
    "enabled": true,
    "auto_check": true,
    "check_interval_hours": 24,
    "patch_directory": "cortex-brain/patches",
    "backup_directory": ".cortex-backups",
    "max_backups": 5,
    "validation_gates": {
      "hotfix": [1, 3, 12],
      "feature": [1, 2, 3, 4, 12],
      "security": [1, 3, 5, 12]
    }
  }
}
```

---

## 📊 Comparison: Full vs Patch Release

| Aspect | Full Release | Patch Release |
|--------|-------------|---------------|
| **Time** | 5-10 minutes | 10-30 seconds |
| **Validation Gates** | 16 gates | 3-5 gates (type-dependent) |
| **User Impact** | Re-setup required | Transparent update |
| **Risk** | Medium (full reinstall) | Low (incremental) |
| **Rollback** | Git checkout | Instant (backup restore) |
| **Use Case** | Major/minor version | Bug fix, small feature |
| **Brain Data** | Preserved but re-validated | Untouched |
| **Package Size** | 50-100 MB | 10 KB - 2 MB |

---

## 🎓 Benefits

**For Users:**
- ✅ **Fast Updates** - 10-30 seconds vs 5-10 minutes
- ✅ **Low Risk** - Small changes, instant rollback
- ✅ **No Disruption** - CORTEX keeps working during update
- ✅ **Brain Safe** - Configurations and brain data untouched

**For Developers:**
- ✅ **Quick Fixes** - Deploy bug fixes same day
- ✅ **Incremental Delivery** - Ship features as they're ready
- ✅ **Easy Testing** - Isolated changes easier to validate
- ✅ **Version Control** - Clear history of what changed when

**For Project:**
- ✅ **Faster Iteration** - Release cycle measured in hours, not weeks
- ✅ **User Confidence** - Low-risk updates encourage adoption
- ✅ **Better Testing** - Small patches easier to QA
- ✅ **Clear History** - Patch manifests document all changes

---

## 🚨 Edge Cases & Error Handling

### Case 1: Modified Installation

**Scenario:** User edited CORTEX files, patch conflicts with changes

**Detection:**
```python
# Before applying patch
for file_path in patch_files:
    current_checksum = calculate_checksum(file_path)
    expected_checksum = manifest['rollback_data']['previous_checksums'][file_path]
    
    if current_checksum != expected_checksum:
        warn(f"File modified: {file_path}")
```

**Resolution:**
- Show warning with file list
- Options: Overwrite (lose changes), Cancel (keep changes), Merge (advanced)
- Default: Cancel with instructions to commit local changes first

### Case 2: Backup Missing

**Scenario:** User deleted .cortex-backups/, rollback requested

**Detection:**
```python
if not backup_exists(target_version):
    error("Backup for version {target_version} not found")
```

**Resolution:**
- Error message explaining backup missing
- Suggest: "Use git to restore: git checkout v{target_version}"
- Alternative: Re-download full version from GitHub

### Case 3: Partial Apply Failure

**Scenario:** Patch applies 2/3 files then fails

**Handling:**
```python
try:
    for file_op in patch_operations:
        apply_file_operation(file_op)
except Exception as e:
    # Rollback partial changes
    for completed_op in completed_operations:
        revert_operation(completed_op)
    raise PatchApplicationError("Partial failure, reverted")
```

**User Experience:**
- Clear error message
- Automatic rollback of partial changes
- Installation state unchanged (atomic operation)

---

## 📅 Implementation Timeline (Phase 8.4)

**Total Effort:** 14 hours

**Breakdown:**
1. **Patch Builder Implementation** (4 hours)
   - Git diff detection
   - Checksum calculation
   - Manifest generation
   - File packaging

2. **Patch Orchestrator Implementation** (5 hours)
   - Apply logic with validation
   - Rollback logic with backup
   - Checksum verification
   - Natural language CLI integration

3. **Deployment Script Enhancement** (2 hours)
   - Add --patch flag
   - Implement gate filtering
   - Version tagging logic

4. **Testing & Validation** (3 hours)
   - Unit tests (builder + orchestrator)
   - Integration tests (end-to-end)
   - Edge case testing (modified install, missing backup)

---

## 🔗 Related Documentation

- **Phase 8 Details:** `CONSOLIDATED-IMPLEMENTATION-PLAN.yaml` (Deliverable 8.4)
- **Deployment System:** `scripts/deploy_cortex.py`
- **Git Checkpoint Guide:** `.github/prompts/modules/git-checkpoint-guide.md`
- **Upgrade Guide:** `.github/prompts/modules/upgrade-guide.md`

---

**Version:** 1.0  
**Status:** Draft (Phase 8.4 not yet implemented)  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
