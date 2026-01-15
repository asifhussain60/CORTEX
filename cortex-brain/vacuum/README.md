# CORTEX Vacuum Configuration

This directory contains the CORTEX Vacuum system for repository reorganization.

## Files

- `config.yaml` - Classification and naming rules
- `migration-plan.json` - Generated during analysis phase
- `analysis-report.json` - Full analysis results
- `reference-map.json` - Cross-file reference tracking
- `execution-report.json` - Execution results and logging

## Workflow

### Phase 1: Analysis (Non-Destructive)
```bash
python scripts/run-cortex-vacuum.py analyze --output-dir cortex-brain/vacuum/
```

This generates:
- `migration-plan.json` - What will be changed
- `analysis-report.json` - Detailed analysis
- `reference-map.json` - All cross-references found

### Phase 2: Review & Approval
Review the generated reports and ensure the planned changes are correct.

### Phase 3: Execution (Controlled)
```bash
# First, dry run to verify
python scripts/run-cortex-vacuum.py execute \
  --plan cortex-brain/vacuum/migration-plan.json \
  --dry-run

# Then execute with approval
python scripts/run-cortex-vacuum.py execute \
  --plan cortex-brain/vacuum/migration-plan.json \
  --auto-approve
```

This generates:
- `execution-report.json` - What was actually changed
- Snapshot backup files for rollback

### Phase 4: Verification
```bash
python scripts/run-cortex-vacuum.py verify
```

## Safety Features

- **Pre-flight Analysis**: Identify issues before making changes
- **Snapshots**: Full repository state backed up before execution
- **Dry Run**: See exactly what will happen before committing
- **Reference Tracking**: All cross-file references updated automatically
- **Rollback**: Revert to previous state if needed

## Key Features

✅ **Naming Compliance**: All files follow kebab-case convention (≤20 chars)  
✅ **Smart Organization**: Files moved to appropriate tier folders  
✅ **Reference Integrity**: Cross-file references maintained and updated  
✅ **Cleanup**: Backup and redundant files deleted  
✅ **Audit Trail**: Complete logging of all changes  
✅ **Reversible**: Snapshots enable rollback capability  

## Documentation

See `/Users/asifhussain/PROJECTS/CORTEX/cortex-vacuum.prompt.md` for complete specification and rules.
