# Holistic Cleanup Orchestrator Guide

**Version:** 1.0  
**Status:** Production  
**Module:** src/operations/modules/cleanup/holistic_cleanup_orchestrator.py

---

## Overview

The Holistic Cleanup Orchestrator performs comprehensive repository analysis and cleanup with recursive scanning, production validation, and detailed reporting before execution.

## Key Features

- **Recursive Scan** - Scans entire repository structure
- **File Categorization** - Identifies production/non-production/redundant/deprecated/report files
- **Production Validation** - Detects non-production naming patterns (temp_, _v1, -YYYYMMDD, clean/modified/updated, backup/old, copy, SUMMARY/REPORT)
- **Manifest Generation** - Creates detailed JSON + Markdown report with recommendations
- **Safe Execution** - Dry-run preview, user approval required, git backup, rollback available

## Commands

```
cleanup
clean up
cleanup cortex
clean cortex
holistic cleanup
```

## Expected Results

- **Space savings:** 50-200 MB typical (350+ MB for major cleanups)
- **File reduction:** Removes 20-40% non-production files
- **Production naming:** Suggests production-ready names for all violations
- **Protected paths:** Never touches src/, tests/, cortex-brain/tier*, .git/, package.json

## Workflow

1. **Scanning** - Recursive directory scan
2. **Analysis** - File categorization and pattern detection
3. **Manifest Generation** - Detailed JSON + Markdown report
4. **Review** - User approval required before any deletions
5. **Execution** - Safe cleanup with git backup and rollback capability

## Safety Features

- Pre-execution validation
- Git backup before cleanup
- Protected path enforcement
- Rollback capability
- Dry-run mode available

## Integration

- Uses CleanupValidator for validation
- Uses CleanupVerifier for post-cleanup verification
- Integrated with response-templates.yaml
- Cache-aware for performance optimization

## Performance

- Scan time: 2-5 seconds typical
- Analysis time: 1-3 seconds
- Cleanup execution: 5-15 seconds
- Total: <30 seconds for most repositories

## Error Handling

- Validation failures block cleanup
- Import errors caught and reported
- Protected file violations prevented
- Rollback on execution errors

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
