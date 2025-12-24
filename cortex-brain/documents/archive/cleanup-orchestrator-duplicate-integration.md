# Cleanup Orchestrator - Duplicate Analysis Integration

**Created:** December 7, 2025  
**Author:** Asif Hussain  
**Version:** 3.8.1

---

## Overview

Successfully integrated the duplicate functionality analyzer (`analyze_duplicates_v2.py`) into the Cleanup Orchestrator as Phase 0, enabling automatic detection and safe deletion of archived duplicate files during system maintenance.

---

## Implementation Summary

### Files Modified

1. **`src/operations/modules/orchestration/cleanup_orchestrator.py`** (669 lines)
   - Added Phase 0: Duplicate Analysis
   - Enhanced Phase 3: Cleanup Obsolete (now uses duplicate analysis)
   - Updated reporting to include duplicate statistics
   - Added auto_delete_archived parameter support

### Integration Points

#### 1. Phase 0: Duplicate Analysis (New)

**Location:** Lines 197-247 in cleanup_orchestrator.py

**Features:**
- Instantiates `DuplicateFunctionalityAnalyzer`
- Performs 4-layer analysis (files, functions, classes, modules)
- Applies 5-layer safety system (active imports, git history, location priority)
- Generates safety scores and recommendations
- Saves detailed JSON report to `cortex-brain/documents/analysis/`

**Metrics Tracked:**
- `duplicates_found` - Total duplicate files detected
- `safe_to_delete` - Archived duplicates safe for deletion
- `needs_review` - Active duplicates requiring manual review

**Execution:**
```python
cleanup = CleanupOrchestrator()
result = cleanup.execute({
    'dry_run': True,
    'skip_duplicate_analysis': False  # Run Phase 0
})
```

#### 2. Phase 3: Cleanup Obsolete (Enhanced)

**Location:** Lines 423-506 in cleanup_orchestrator.py

**New Features:**
- Accepts `auto_delete_archived` parameter
- Processes recommendations from Phase 0 analysis
- Automatically deletes archived duplicates when `auto_delete_archived=True`
- Filters for `SAFE` actions with `archived` in recommendation
- Updates metrics: `duplicates_deleted`, `files_removed`, `space_freed_mb`

**Execution:**
```python
cleanup = CleanupOrchestrator()
result = cleanup.execute({
    'dry_run': False,
    'auto_delete_archived': True  # Enable automatic deletion
})
```

**Safety Checks:**
- Verifies file exists before deletion
- Confirms file is in `archives/` directory
- Logs all deletions with file paths
- Tracks space freed in MB

#### 3. Metrics & Reporting (Enhanced)

**New Metrics:**
- `duplicates_deleted` - Count of archived duplicates removed

**Report Structure:**
```json
{
  "duplicate_analysis": {
    "duplicates_found": 277,
    "safe_to_delete": 0,
    "needs_review": 58,
    "duplicates_deleted": 0,
    "summary": {
      "duplicate_files": 277,
      "duplicate_functions": 1233,
      "duplicate_classes": 631
    },
    "analysis_timestamp": "2025-12-07T19:04:32"
  }
}
```

**Summary Format:**
```
[DRY RUN] Cleanup complete: 2 moved 0 removed 0 references updated 
(277 duplicates: 0 deleted, 58 need review)
```

---

## Usage Examples

### Example 1: Dry Run with Duplicate Analysis

```python
from src.operations.modules.orchestration.cleanup_orchestrator import CleanupOrchestrator

cleanup = CleanupOrchestrator()
result = cleanup.execute({
    'dry_run': True,
    'skip_duplicate_analysis': False,
    'auto_delete_archived': False
})

print(f"Duplicates found: {result.data['metrics']['duplicates_found']}")
print(f"Safe to delete: {result.data['metrics']['safe_to_delete']}")
print(f"Need review: {result.data['metrics']['needs_review']}")
```

### Example 2: Execute with Automatic Deletion

```python
cleanup = CleanupOrchestrator()
result = cleanup.execute({
    'dry_run': False,
    'skip_duplicate_analysis': False,
    'auto_delete_archived': True
})

print(f"Duplicates deleted: {result.data['metrics']['duplicates_deleted']}")
print(f"Space freed: {result.data['metrics']['space_freed_mb']:.2f} MB")
```

### Example 3: Skip Duplicate Analysis (Fast Mode)

```python
cleanup = CleanupOrchestrator()
result = cleanup.execute({
    'dry_run': False,
    'skip_duplicate_analysis': True,  # Skip Phase 0 for speed
    'auto_delete_archived': False
})
```

---

## Test Results

**Test Execution:** December 7, 2025 @ 19:04

**Test Script:** `test_cleanup_with_duplicates.py`

**Results:**
```
======================================================================
TEST SUMMARY
======================================================================
[PASS] Test 1: Cleanup executed successfully
[PASS] Test 2: Phase 0 integrated and executed
[PASS] Test 3: auto_delete_archived parameter available
[PASS] Test 4: Report generated and structured correctly

[*] Tests Passed: 4/4

[SUCCESS] All integration tests passed!
```

**Duplicate Analysis Results:**
- Total Python files: 2,563
- Duplicate files: 277
- Duplicate functions: 1,233
- Duplicate classes: 631
- Active imports: 1,160 modules
- Recently modified files: 8,283
- Safe-to-delete zones: 671 files

**Safety Classification:**
- Safe to delete (archived): 0 files
- Need manual review (active): 58 files
- Reason: All duplicates are active or in mixed locations

---

## Architecture

### 5-Phase Workflow

```
Phase 0: Duplicate Analysis (Optional)
├── Collect Python files
├── Detect active imports (AST parsing)
├── Analyze git history (30 days)
├── Calculate location priorities
├── Generate safety scores
└── Save JSON report

Phase 1: File Organization
├── Move test files to tests/
├── Move scripts to scripts/utilities/
└── Move docs to cortex-brain/documents/

Phase 2: Reference Updates
├── Update import statements
├── Update file path references
└── Update test discovery patterns

Phase 3: Cleanup Obsolete (Enhanced)
├── Delete archived duplicates (if auto_delete_archived=True)
├── Remove backup files (*.backup, *.old, *.bak)
├── Remove temporary files (*.tmp, *~)
└── Clean empty directories

Phase 4: Validation
├── Check no test files in root
├── Check no misplaced documentation
└── Verify directory structure
```

### Safety System (5 Layers)

1. **Active Import Detection** - AST parsing to find actively used modules
2. **Git History Analysis** - 30-day activity tracking via subprocess
3. **Location Priority Scoring** - src/(100) > scripts/(80) > tests/(70) > archives/(0)
4. **Safety Score Calculation** - priority + (50 if active) - (100 if archived)
5. **Action Classification** - SAFE/MANUAL/MIXED based on scores

---

## Integration with System Maintenance

The Cleanup Orchestrator is executed as Phase 3 of the System Maintenance Orchestrator:

```python
from src.operations.modules.orchestration.system_maintenance_orchestrator import SystemMaintenanceOrchestrator

maintenance = SystemMaintenanceOrchestrator()
result = maintenance.execute({})

# Cleanup runs automatically with duplicate analysis
```

**System Maintenance Workflow:**
1. Pre-healthcheck
2. Alignment
3. **Cleanup (with duplicate analysis)** ← Enhanced
4. Optimization
5. Post-healthcheck

---

## Benefits

### 1. Automated Duplicate Detection
- 4-layer analysis (files, functions, classes, modules)
- No manual scanning required
- Consistent detection across runs

### 2. Safety-First Architecture Identification
- 5-layer safety system prevents accidental deletion of active code
- Active import detection via AST parsing
- Git history integration (30-day activity tracking)
- Location-based priority scoring

### 3. Intelligent Cleanup
- Only deletes archived duplicates when explicitly enabled
- Preserves active code automatically
- Manual review required for mixed-location duplicates

### 4. Comprehensive Reporting
- Detailed JSON reports with all metrics
- Summary includes duplicate statistics
- Timestamped analysis for history tracking

### 5. Multi-Machine Safety
- Alignment state tracking per machine
- Git pull protection (future enhancement)
- No shared state across machines

---

## Configuration

### Cleanup Orchestrator Parameters

```python
cleanup.execute({
    'dry_run': bool,                    # Preview changes without executing
    'skip_duplicate_analysis': bool,    # Skip Phase 0 for faster execution
    'auto_delete_archived': bool        # Enable automatic deletion of archived duplicates
})
```

### Duplicate Analyzer Configuration

**Conditional Import:**
```python
try:
    from analyze_duplicates_v2 import DuplicateFunctionalityAnalyzer
    DUPLICATE_ANALYZER_AVAILABLE = True
except ImportError:
    DUPLICATE_ANALYZER_AVAILABLE = False
```

**Fallback Behavior:**
- If analyzer not available: Phase 0 skipped with warning
- Cleanup continues with Phases 1-4
- No duplicate analysis in report

---

## Future Enhancements

### Planned

1. **Git Pull Protection** (In Progress)
   - Prevent remote code from overwriting aligned files
   - Machine-local alignment state tracking
   - Automatic stash + reconcile on pull
   - Status: Implementation guide complete

2. **Duplicate Similarity Threshold**
   - Configurable similarity percentage (default: 80%)
   - AST-based similarity instead of token-based
   - Handle refactored but functionally similar code

3. **Cross-File Dependency Analysis**
   - Detect function calls across modules
   - Identify unused but imported code
   - Safe-to-delete calculation based on call graph

4. **Intelligent Merge Suggestions**
   - AI-powered duplicate consolidation
   - Preserve best version (most recent, most tested, most used)
   - Generate merge strategy for manual review

### Pending Review

5. **Automatic PR Generation**
   - Create GitHub PR for cleanup changes
   - Include before/after metrics
   - Link to duplicate analysis report

6. **Dashboard Integration**
   - Visualize duplicate trends over time
   - Show hot spots (most duplicated files/functions)
   - Track cleanup progress per machine

---

## Troubleshooting

### Issue: Phase 0 Not Executing

**Symptom:** `skip_duplicate_analysis=False` but Phase 0 skipped

**Causes:**
1. `analyze_duplicates_v2.py` not in `scripts/utilities/`
2. Import path issue (sys.path not including scripts/utilities/)
3. `DUPLICATE_ANALYZER_AVAILABLE = False`

**Fix:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'scripts' / 'utilities'))
```

### Issue: No Archived Duplicates Found

**Symptom:** `safe_to_delete: 0` despite duplicates existing

**Causes:**
1. All duplicates are active (imported or recently modified)
2. Duplicates not in archives/ or backups/ directories
3. Location priority scoring doesn't identify safe zones

**Explanation:** This is correct behavior - safety system prevents deletion of active code

### Issue: Slow Phase 0 Execution

**Symptom:** Phase 0 takes >60 seconds

**Causes:**
1. Large repository (>2000 Python files)
2. Git history analysis on large commit history
3. AST parsing of large files

**Fix:** Use `skip_duplicate_analysis=True` for faster execution

---

## Files Created/Modified

| File | Action | Lines | Purpose |
|------|--------|-------|---------|
| `src/operations/modules/orchestration/cleanup_orchestrator.py` | Modified | 669 | Main orchestrator - added Phase 0 |
| `scripts/utilities/analyze_duplicates_v2.py` | Created | 421 | Duplicate analyzer (standalone) |
| `test_cleanup_with_duplicates.py` | Created | 198 | Integration test |
| `cortex-brain/documents/implementation-guides/cleanup-orchestrator-duplicate-integration.md` | Created | This doc | Documentation |

---

## Related Documentation

- **Cleanup Orchestrator:** `cortex-brain/documents/implementation-guides/cleanup-orchestrator-quick-ref.md`
- **System Maintenance:** `cortex-brain/documents/implementation-guides/system-maintenance-orchestrator.md`
- **Git Pull Protection:** `cortex-brain/documents/implementation-guides/git-pull-protection.md`
- **Duplicate Analyzer:** `scripts/utilities/analyze_duplicates_v2.py` (inline docs)

---

## Next Steps

1. ✅ Duplicate analyzer created and tested
2. ✅ Integration into Cleanup Orchestrator complete
3. ✅ Test script created and executed
4. ✅ Documentation complete
5. ⏳ Deploy to system maintenance workflow
6. ⏳ Add to CORTEX.prompt.md for natural language triggers
7. ⏳ Create CLI command: `cortex cleanup --analyze-duplicates --auto-delete-archived`

---

**Status:** ✅ COMPLETE - Duplicate analysis fully integrated into Cleanup Orchestrator with safety-first architecture identification and automatic archived duplicate deletion.

**Author:** Asif Hussain  
**Version:** 3.8.1  
**License:** Proprietary - Source-Available
