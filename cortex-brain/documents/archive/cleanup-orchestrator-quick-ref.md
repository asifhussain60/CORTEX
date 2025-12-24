# Cleanup Orchestrator - Quick Reference

**Module:** `src/operations/modules/orchestration/cleanup_orchestrator.py`  
**Version:** 3.8.1  
**Author:** Asif Hussain

## Overview

Comprehensive file organization and cleanup orchestrator that maintains codebase structure and updates all references automatically.

## Features

### 4-Phase Workflow

1. **File Organization** - Move misplaced files to correct locations
   - Root-level test files → `tests/integration/`
   - Misplaced scripts → `scripts/utilities/`
   - Scattered documentation → `cortex-brain/documents/{category}/`

2. **Reference Updates** - Automatically update all code references
   - Python import statements (from/import)
   - File path references in strings
   - Test discovery patterns

3. **Obsolete Cleanup** - Remove obsolete and duplicate files
   - Backup files (*.backup, *.old, *.bak)
   - Temporary files (*.tmp, *~)
   - System files (.DS_Store, Thumbs.db)
   - Empty directories

4. **Validation** - Verify organization compliance
   - No test files in root
   - No misplaced documentation
   - Required directory structure exists

## Usage

### Standalone

```python
from src.operations.modules.orchestration.cleanup_orchestrator import CleanupOrchestrator

# Dry run (preview changes)
cleanup = CleanupOrchestrator()
result = cleanup.execute({'dry_run': True})

# Execute cleanup
result = cleanup.execute({'dry_run': False})
```

### Integrated in System Maintenance

Cleanup runs automatically as Phase 3 of system maintenance:

```bash
# Via CLI (future)
cortex system maintenance

# Via Python
from src.operations.modules.orchestration.system_maintenance_orchestrator import SystemMaintenanceOrchestrator

maintenance = SystemMaintenanceOrchestrator()
result = maintenance.execute({})
```

## System Maintenance Integration

**5-Phase Workflow:**

1. **Pre-healthcheck** - Establish baseline
2. **Alignment** - Fix system issues
3. **🆕 Cleanup** - Organize files and update references
4. **Optimization** - Improve performance
5. **Post-healthcheck** - Validate improvements

**Benefits:**
- Files organized before optimization runs
- References stay consistent across operations
- Automated maintenance reduces manual work
- Safe backups before any moves

## File Organization Rules

### Test Files
```
❌ ROOT/test_*.py
✅ tests/integration/test_*.py
```

### Scripts
```
❌ ROOT/*.py (except setup.py, manage.py)
✅ scripts/utilities/*.py
```

### Documentation
```
❌ ROOT/*.md (except README, LICENSE, CHANGELOG, CONTRIBUTING, MULTI-MACHINE-SETUP)
✅ cortex-brain/documents/{category}/*.md
```

**Categories:**
- `reports/` - Status reports, summaries
- `analysis/` - Code/architecture analysis
- `planning/` - Feature plans, proposals
- `investigations/` - Bug investigations, debugging
- `implementation-guides/` - How-to guides, tutorials
- `summaries/` - General summaries

## Reference Update Patterns

### Python Imports
```python
# Before move
from test_utils import helper

# After move (auto-updated)
from tests.integration.test_utils import helper
```

### File Paths
```python
# Before move
test_file = "test_feature.py"

# After move (auto-updated)
test_file = "tests/integration/test_feature.py"
```

### Module Paths
```python
# Before move
import test_module

# After move (auto-updated)
import tests.integration.test_module
```

## Safety Features

### Backup System
All moved files are backed up to:
```
cortex-brain/backups/cleanup/{timestamp}/
```

### Validation
- Checks directory structure compliance
- Validates no misplaced files remain
- Reports any issues found

### Dry Run
Preview all changes before executing:
```python
result = cleanup.execute({'dry_run': True})
print(result.data['metrics'])
# {
#   'files_moved': 7,
#   'files_removed': 3,
#   'references_updated': 12,
#   ...
# }
```

## Output & Reporting

### Result Metrics
```python
{
    'files_moved': 7,
    'files_removed': 3,
    'references_updated': 12,
    'issues_fixed': 10,
    'space_freed_mb': 0.15,
    'errors': []
}
```

### Report Location
```
cortex-brain/documents/reports/cleanup-{timestamp}.json
```

### Validation Result
```python
{
    'passed': True,
    'issues': []  # Empty if organization compliant
}
```

## Common Scenarios

### After Git Pull (Multi-Machine)
```python
# Someone pushed misplaced files
cleanup = CleanupOrchestrator()
result = cleanup.execute({'dry_run': False})
# Automatically organizes and updates references
```

### Before Deployment
```python
# Ensure clean structure before deploy
cleanup = CleanupOrchestrator()
result = cleanup.execute({'dry_run': False})
# Validation ensures compliance
```

### Regular Maintenance
```python
# Run as part of system maintenance
maintenance = SystemMaintenanceOrchestrator()
result = maintenance.execute({})
# Cleanup runs automatically in Phase 3
```

## Protected Directories

Cleanup **never** touches:
- `.git/` - Git repository
- `.venv/` - Virtual environments
- `node_modules/` - Node packages
- `__pycache__/` - Python cache
- `cortex-brain/` - Brain structure (only organizes within)

## Error Handling

### Move Failures
If a file move fails:
- Error logged to metrics
- Backup already created
- Continues with remaining files
- All errors reported in result

### Reference Update Failures
If reference update fails:
- Warning logged
- Original file unchanged
- Error added to metrics
- Manual review suggested

## Performance

### Typical Execution
- **Dry Run:** <1 second
- **Small Project (<100 files):** 2-5 seconds
- **CORTEX Project (~2000 files):** 10-15 seconds

### Progress Monitoring
Auto-activated for operations >3 seconds:
```
🧹 Cleanup & Organization
├─ Phase 1: Organizing files (1/4)
├─ Phase 2: Updating references (2/4)
├─ Phase 3: Cleaning obsolete files (3/4)
└─ Phase 4: Validating organization (4/4)
```

## Integration Testing

Test 8 in realignment utility validates:
```python
# Test 8: Cleanup Orchestrator
cleanup_orchestrator = CleanupOrchestrator()
cleanup_result = cleanup_orchestrator.execute({'dry_run': True})

assert cleanup_result.success
assert cleanup_result.data['validation']['passed']
```

## Best Practices

1. **Dry Run First** - Always preview changes
2. **Regular Cadence** - Run with system maintenance
3. **Post-Pull** - Run after multi-machine git pulls
4. **Pre-Deploy** - Validate organization before deployment
5. **Review Reports** - Check cleanup reports for patterns

## Troubleshooting

### Files Not Moving
- Check file permissions
- Verify not in protected directory
- Review backup directory for copies

### References Not Updating
- Ensure Python syntax is valid
- Check for dynamic imports (won't update)
- Verify paths are string literals

### Validation Failing
- Review validation issues in report
- Run dry run to see what needs cleanup
- Check for files in `.gitignore` that shouldn't be tracked

## Future Enhancements

Planned features:
- [ ] Configurable organization rules
- [ ] Custom file categorization patterns
- [ ] Import alias preservation
- [ ] Cross-file dependency analysis
- [ ] Automatic PR generation for cleanup

---

**Related Documentation:**
- System Maintenance: `cortex-brain/documents/implementation-guides/system-maintenance-orchestrator.md`
- File Organization: `cortex-brain/documents/reports/cleanup-{timestamp}.json`

**Support:** Report issues via `cortex feedback` command
