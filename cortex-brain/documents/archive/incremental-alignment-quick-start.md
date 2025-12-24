# Incremental Alignment System - Quick Start Guide

**Version:** 3.2  
**Status:** Production Ready  
**Author:** Asif Hussain

---

## Overview

CORTEX 3.2 introduces **Incremental Alignment** - a smart validation system that only checks what changed, reducing alignment time by 60-80% on repeated runs.

**Key Features:**
- ✅ **Phase 0 Validation** - Documentation sync check (CORTEX.prompt.md ↔ copilot-instructions.md)
- ✅ **File Change Detection** via SHA256 checksums
- ✅ **Auto-Discovery & Wiring** for new features
- ✅ **Admin vs User Context** detection
- ✅ **Performance Metrics** tracking
- ✅ **Backward Compatible** with existing workflows

---

## Quick Start

### Basic Usage

```bash
# Smart alignment (auto-detects incremental or full scan)
align

# Or via Python module
python -m src.operations.align
```

**Behavior:**
- **First run OR >24h since last full scan:** Full scan
- **Otherwise:** Incremental scan (only checks changed features)

### Command Flags

```bash
# Force full scan (ignores incremental optimization)
align --full

# Quick mode (infrastructure checks only, skip features)
align --quick

# Legacy v2.0 mode (full realignment with auto-fix)
align --auto-fix
```

---

## How It Works

### State Tracking

Alignment state stored in `cortex-brain/.alignment-state.json`:

```json
{
  "version": "3.2",
  "last_alignment": "2025-12-04T10:00:00",
  "last_full_scan": "2025-12-04T08:00:00",
  "scan_mode": "incremental",
  "context_type": "admin",
  
  "file_checksums": {
    "src/.../hands_on_tutorial_orchestrator.py": {
      "sha256": "abc123...",
      "last_modified": "2025-12-04T09:45:00",
      "last_checked": "2025-12-04T10:00:00",
      "size_bytes": 15420
    }
  },
  
  "changes_detected": {
    "files_modified": ["src/.../hands_on_tutorial_orchestrator.py"],
    "features_impacted": ["HandsOnTutorialOrchestrator"]
  },
  
  "performance_metrics": {
    "last_run_duration_seconds": 2.3,
    "features_checked": 3,
    "features_skipped": 39,
    "cache_hit_rate": 0.93
  }
}
```

### Decision Tree

```
┌─────────────────────────────────────┐
│      Alignment Run Triggered        │
└──────────────┬──────────────────────┘
               │
               ├─ --full flag? ────────► Full Scan
               │
               ├─ --quick flag? ───────► Quick Mode
               │
               ├─ First run? ──────────► Full Scan
               │
               ├─ >24h since full? ────► Full Scan
               │
               └─ Otherwise ───────────► Incremental Scan
                                           │
                                           ├─ Compute file checksums
                                           ├─ Compare with previous state
                                           ├─ Detect changed files
                                           ├─ Map to impacted features
                                           └─ Validate changed features only
```

### Performance Comparison

| Mode | Duration | Features Checked | Use Case |
|------|----------|------------------|----------|
| **Quick** | 1-2s | 0 (infrastructure only) | CI/CD pre-checks |
| **Incremental** | 1-2s | 3-5 (changed only) | Daily development |
| **Full** | 4-6s | 40+ (all features) | After major changes |

---

## Context Detection

### Admin Context (CORTEX Repo)

**Detected when:**
- `cortex-brain/admin/` directory exists
- `src/operations/modules/admin/` directory exists
- `.github/prompts/CORTEX.prompt.md` exists

**Operations:**
- Full feature discovery and scoring
- Wiring validation in response-templates.yaml
- Auto-discovery of new orchestrators/agents
- Deployment gate validation

### User Context (Dev Repo)

**Detected when:**
- CORTEX installed as embedded system
- Admin markers not present

**Operations:**
- Infrastructure validation only
- No feature discovery/scoring
- Basic health checks
- Optimized for user projects

---

## Validation Phases

### Phase 0: Documentation Sync (NEW in 3.5.5)

**CRITICAL FIRST STEP** - Ensures CORTEX's two primary documentation files stay synchronized:

**Files Validated:**
- `.github/prompts/CORTEX.prompt.md` (Primary user-facing prompt)
- `.github/copilot-instructions.md` (GitHub Copilot integration instructions)

**Synchronization Checks:**
1. ✅ Both files exist
2. ✅ Response format sections consistent (`## 🧠 CORTEX`)
3. ✅ Document organization rules aligned (`📁 Document Organization (CRITICAL)`)
4. ✅ Architecture overview sections present (`🏗️ Architecture Overview`)
5. ✅ Version numbers match (`**Version:** X.Y.Z`)

**Why Phase 0?**
- Documentation drift causes user confusion and inconsistent behavior
- Version mismatches indicate incomplete feature rollouts
- Response format inconsistencies break CORTEX's communication standards
- **Runs BEFORE all other checks** to ensure alignment foundation is solid

**Failure Response:**
- **ERROR:** Missing files (blocks alignment)
- **WARNING:** Out-of-sync sections (allows alignment to continue with warnings)

**Example Output:**
```
✅ [OK] Prompt Sync (Phase 0): CORTEX.prompt.md and copilot-instructions.md are synchronized
```

Or:
```
⚠️ [WARN] Prompt Sync (Phase 0): Documentation files out of sync (1 issues)
  └─ Version mismatch (prompt: 3.5.5, instructions: 3.2.0)
```

---

## Auto-Discovery & Wiring

### Discovery Process

1. **Phase 0:** Validate documentation synchronization

2. **Scan for Python modules:**
   - `src/operations/modules/**/*_orchestrator.py`
   - `src/orchestrators/**/*_orchestrator.py`
   - `src/cortex_agents/**/*_agent.py`

3. **Extract metadata:**
   - Module path
   - Class name
   - Docstring
   - File checksum

4. **Validate wiring:**
   - Check `response-templates.yaml` for `expected_orchestrator` field
   - Check triggers list for module name references
   - Verify routing configuration

5. **Update state:**
   - Add new features to state
   - Mark wiring status
   - Compute integration score

### Wiring Validation

```python
# Example: HandsOnTutorialOrchestrator
{
  "wired": true,  # Found in response-templates.yaml
  "triggers": [
    "tutorial",
    "start tutorial",
    "hands on tutorial"
  ],
  "expected_orchestrator": "HandsOnTutorialOrchestrator"
}
```

**If not wired:**
- Score remains <90%
- Warning issued during alignment
- Deployment gate may block (admin context)

---

## State Management

### Loading State

```python
from src.operations.modules.admin.alignment_state import AlignmentStateManager

manager = AlignmentStateManager(Path("cortex-brain/.alignment-state.json"))
state = manager.load()

if state:
    print(f"Last run: {state.last_alignment}")
    print(f"Health: {state.overall_health}%")
    print(f"Features: {len(state.feature_scores)}")
```

### Saving State

```python
# State auto-saved after every alignment
# Manual save:
success = manager.save(state)
```

### Backup & Restore

```python
# Create backup
manager.backup()  # Creates .alignment-state.json.backup

# Restore from backup
import shutil
shutil.copy("cortex-brain/.alignment-state.json.backup", 
            "cortex-brain/.alignment-state.json")
```

### State Corruption Recovery

```bash
# If state file corrupted:
rm cortex-brain/.alignment-state.json

# Next align run will regenerate
align --full
```

---

## Migration from Legacy

### Automatic Migration

**Old format (v3.0):**
```json
{
  "last_alignment": "2025-11-30T07:41:03",
  "feature_scores": { ... },
  "overall_health": 77
}
```

**Auto-migrated to v3.2:**
```json
{
  "version": "3.2",
  "last_alignment": "2025-11-30T07:41:03",
  "last_full_scan": "2025-11-30T07:41:03",
  "scan_mode": "full",
  "context_type": "admin",
  "file_checksums": {},
  "feature_scores": { ... },
  "changes_detected": { ... },
  "performance_metrics": { ... },
  "overall_health": 77
}
```

**Migration happens automatically** on first v3.2 alignment run.

---

## Integration with Existing Systems

### Deployment Gates

**Gate 18** (EPM Wiring Validation) already consumes `.alignment-state.json`:

```python
# src/deployment/deployment_gates.py
alignment_path = project_root / "cortex-brain" / ".alignment-state.json"
with open(alignment_path) as f:
    state = json.load(f)

epm_status = state["feature_scores"]["SetupEPMOrchestrator"]
if not epm_status.get("wired"):
    gate["passed"] = False
    gate["message"] = "SetupEPMOrchestrator not wired"
```

**No changes required** - v3.2 format is backward compatible.

### Optimize Command

Optimize already calls align internally:

```python
# src/operations/modules/optimization/optimize_cortex_orchestrator.py
from src.operations.modules.admin.align_utility import run_align_utility

# Now uses incremental mode automatically
result = run_align_utility()
```

---

## Troubleshooting

### Issue: Incremental mode not triggering

**Check:**
```bash
# Verify state file exists
ls -la cortex-brain/.alignment-state.json

# Check last full scan timestamp
cat cortex-brain/.alignment-state.json | grep last_full_scan
```

**Solution:**
- If >24h old: Full scan will trigger automatically (expected)
- If state missing: Full scan will trigger (expected)
- If you want to force incremental: No way to force (by design)

### Issue: Changes not detected

**Check:**
```bash
# Verify file checksums are being computed
align --full

# Inspect state file
cat cortex-brain/.alignment-state.json | jq '.file_checksums'
```

**Solution:**
- Ensure files are in discovery paths
- Check file permissions (must be readable)
- Verify not in `.gitignore` or `__pycache__`

### Issue: Performance not improved

**Check:**
```bash
# Run with verbose output
python -m src.operations.align --full

# Check performance metrics in state
cat cortex-brain/.alignment-state.json | jq '.performance_metrics'
```

**Expected:**
- First run: ~5s (full scan, building checksums)
- Second run: ~2s (incremental, cached results)
- 60-80% reduction on subsequent runs

---

## Best Practices

### Daily Development

```bash
# Just use default - it's smart
align
```

Incremental mode automatically activates when appropriate.

### After Major Refactoring

```bash
# Force full scan to rebuild state
align --full
```

Use when you've moved/renamed many files.

### CI/CD Pipeline

```bash
# Quick pre-deployment check
align --quick

# Full validation before merge
align --full
```

Quick mode for fast feedback, full scan for comprehensive validation.

### Debugging Alignment Issues

```bash
# 1. Check current state
cat cortex-brain/.alignment-state.json | jq

# 2. Force full scan with clean state
rm cortex-brain/.alignment-state.json
align --full

# 3. Compare results
cat cortex-brain/.alignment-state.json | jq '.overall_health'
```

---

## Architecture Details

### File Change Detection

```python
# SHA256 checksums computed for all discovered Python modules
import hashlib

def compute_checksum(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
```

**Why SHA256?**
- Cryptographically secure (no collisions)
- Fast computation (~0.1ms per file)
- Standard library support
- Works cross-platform

### Change Mapping

```python
# Map changed files to impacted features
def map_files_to_features(
    changed_files: List[str],
    feature_scores: Dict[str, Dict[str, Any]]
) -> Set[str]:
    impacted = set()
    
    for feature_name, score_data in feature_scores.items():
        module_path = score_data.get("module_path", "")
        if module_path in changed_files:
            impacted.add(feature_name)
    
    return impacted
```

**Smart mapping:**
- Direct file-to-feature mapping (O(n))
- Only validates impacted features
- Preserves previous scores for unchanged features

---

## Future Enhancements (CORTEX 4.0)

Potential additions for next major version:

1. **Dependency Graph Analysis**
   - Track inter-feature dependencies
   - Cascade validation when dependencies change

2. **Parallel Validation**
   - Validate multiple features concurrently
   - Target: 90% reduction on large codebases

3. **Machine Learning Optimization**
   - Predict which features need validation
   - Learn from historical alignment patterns

4. **Real-Time Monitoring**
   - File watcher integration
   - Continuous alignment validation

---

## References

- **Implementation:** `src/operations/modules/admin/align_utility.py`
- **State Management:** `src/operations/modules/admin/alignment_state.py`
- **CLI Wrapper:** `src/operations/align.py`
- **System Alignment Guide:** `.github/prompts/modules/system-alignment-guide.md`

---

**Questions or Issues?**  
Report via: `feedback` command or GitHub Issues
