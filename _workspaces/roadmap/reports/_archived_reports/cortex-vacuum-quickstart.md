# CORTEX Vacuum System - Quick Start Guide

**Status**: ✅ Production Ready  
**Version**: 1.0  
**Date**: 2026-01-15

## What is CORTEX Vacuum?

CORTEX Vacuum is a three-tier repository standardization system that transforms your codebase into a production-grade, consistent structure.

**Features:**
- ✅ Automated file organization by tier and function
- ✅ Kebab-case naming enforcement (≤20 chars)
- ✅ Smart cleanup (removes backups, duplicates, temp files)
- ✅ Cross-file reference tracking and updating
- ✅ Non-destructive analysis phase
- ✅ Safe execution with snapshots
- ✅ Full rollback capability

---

## Quick Start: 5 Minutes

### Step 1: Analyze (2 minutes)
Run the analyzer to see what WILL change, WITHOUT making any changes:

```bash
python scripts/run-cortex-vacuum.py analyze --output-dir cortex-brain/vacuum/
```

**Output files:**
- `cortex-brain/vacuum/analysis-report.json` - Detailed findings
- `cortex-brain/vacuum/migration-plan.json` - What will be changed
- `cortex-brain/vacuum/reference-map.json` - Cross-file references

### Step 2: Review (2 minutes)
Look at the analysis results:

```bash
# View summary
cat cortex-brain/vacuum/analysis-report.json | head -50

# Or open in your editor
code cortex-brain/vacuum/analysis-report.json
```

Check:
- ✅ Are the deletions correct?
- ✅ Are the file movements appropriate?
- ✅ Do the new names look good?

### Step 3: Dry Run (1 minute)
See exactly what will happen WITHOUT making changes:

```bash
python scripts/run-cortex-vacuum.py execute \
  --plan cortex-brain/vacuum/migration-plan.json \
  --dry-run
```

Look for any warnings or issues in the output.

### Step 4: Execute
When ready, execute the actual changes:

```bash
python scripts/run-cortex-vacuum.py execute \
  --plan cortex-brain/vacuum/migration-plan.json \
  --auto-approve
```

Execution will:
1. Create snapshots for rollback
2. Delete backup/temp files
3. Move files to correct locations
4. Rename files to kebab-case
5. Update all cross-file references
6. Generate execution report

### Step 5: Verify
Verify everything is correct:

```bash
python scripts/run-cortex-vacuum.py verify
```

---

## Key Concepts

### Phase 1: Analysis (Non-Destructive)
- 🔍 Scans entire repository
- 📋 Identifies issues (naming violations, duplicates, orphans)
- 🔗 Maps all cross-file references
- 📊 Generates comprehensive report
- ✅ **Zero side effects** - can run unlimited times

### Phase 2: Execution (Controlled)
- 📸 Creates snapshots before changes
- 🗑️ Deletes backup/temp files
- 📁 Moves files to correct folders
- ✏️ Renames files to kebab-case
- 🔗 Updates all references automatically
- 💾 Generates execution report

### Phase 3: Verification (Read-Only)
- ✅ Validates compliance
- 🔍 Checks for broken references
- 📊 Provides statistics

---

## File Organization Rules

### Where Files Go

| File Type | Destination |
|-----------|-------------|
| Executive docs | `docs/executive/` |
| Phase docs | `docs/phases/` |
| Review docs | `docs/reviews/` |
| Status docs | `docs/` |
| Reports | `reports/` |
| Utility scripts | `scripts/` |
| Config files | `config/` or root |

### Naming Convention: Kebab-Case

**Format:** `noun-descriptor-type` (max 20 chars, lowercase)

**Examples:**
```
BEFORE                                AFTER
────────────────────────────────────────────────
CORTEX-MASTER-COMPLETION-ANALYSIS.md → cortex-analysis.md
PHASE-CHAT-VERIFICATION-REPORT.md    → phase-chat-verify.md
EXECUTIVE-BRIEF-FOR-DECISION.md      → executive-brief.md
AR-013-TRILOGY-COMPLETION-REPORT.md  → ar-013-trilogy.md
```

**Rules:**
- ❌ No uppercase
- ❌ No spaces
- ❌ No adjectives (old, new, fixed, enhanced, etc.)
- ✅ Use abbreviations (verify, impl, exec, arch)
- ✅ Keep names semantic

---

## What Gets Deleted?

Files automatically marked for deletion:
- `*.bak`, `*.backup` - Backup files
- `*-old*`, `*-new*` - Version suffixes
- `*-fixed*`, `*-enhanced*` - State suffixes
- `*.pyc` - Python bytecode
- `__pycache__/` - Python cache

Files PROTECTED (never deleted):
- `pytest.ini`, `requirements.txt` - Config
- Database files (`.db`, `.db-shm`, `.db-wal`)
- Active code (`src/`, `tests/`)

---

## Safety Features

### 🛡️ Non-Destructive Analysis
Phase 1 never modifies anything - run as many times as needed.

### 📸 Snapshots
Before execution, complete repository state is backed up to `cortex-brain/snapshots/`

### ⏮️ Rollback
If something goes wrong:
```bash
git checkout HEAD  # Restore from git
```

### 🔍 Reference Tracking
All cross-file references are:
1. Identified before execution
2. Updated after file moves
3. Verified to work correctly

### 📋 Audit Trail
Every change is logged with:
- Timestamp
- Operation (move/rename/delete)
- Source and destination
- Success/failure status
- Affected references

---

## Common Scenarios

### Scenario 1: "I want to review changes before any execution"

```bash
# Step 1: Analyze
python scripts/run-cortex-vacuum.py analyze

# Step 2: Review the reports in cortex-brain/vacuum/
# Edit cortex-brain/vacuum/config.yaml if you want to customize rules

# Step 3: Dry run
python scripts/run-cortex-vacuum.py execute --plan cortex-brain/vacuum/migration-plan.json --dry-run

# Step 4: Execute when ready
python scripts/run-cortex-vacuum.py execute --plan cortex-brain/vacuum/migration-plan.json --auto-approve
```

### Scenario 2: "I want to customize which files get moved"

1. Edit `cortex-brain/vacuum/config.yaml`
2. Modify the `file_classifications` section
3. Re-run analysis: `python scripts/run-cortex-vacuum.py analyze`
4. Review new plan
5. Execute

### Scenario 3: "I want to check compliance without changes"

```bash
python scripts/run-cortex-vacuum.py verify
```

This shows:
- ✅ Kebab-case compliance
- ✅ File organization
- ✅ Naming issues
- ✅ Potential problems

### Scenario 4: "Something went wrong!"

```bash
# Check what happened
cat cortex-brain/vacuum/execution-report.json

# Revert using git
git checkout HEAD

# Re-analyze to see what went wrong
python scripts/run-cortex-vacuum.py analyze
```

---

## MCP Tool Integration

The vacuum system is exposed as MCP tools for programmatic access:

```python
from src.mcp.tools import CortexVacuumAnalyzer, CortexVacuumExecutor

# Analyze
analyzer = CortexVacuumAnalyzer("/path/to/repo")
report = analyzer.analyze()

# Execute
executor = CortexVacuumExecutor("/path/to/repo", migration_plan)
result = executor.execute(dry_run=True)
```

Or use the MCP registry:

```python
from src.mcp.tools import register_vacuum_tools

registry.register_tool(register_vacuum_tools)
```

---

## Configuration

Configuration file: `cortex-brain/vacuum/config.yaml`

Key settings:
- **File classifications**: Where files should go
- **Naming rules**: Kebab-case enforcement
- **Deletion rules**: Which files to remove
- **Protected files**: Never touch these
- **Safety settings**: Snapshots, dry-run defaults

---

## Troubleshooting

### Problem: "Analysis takes too long"
- First run builds the reference map
- Subsequent runs cache results
- For large repos, can take 30-60 seconds

### Problem: "Some references didn't update"
- Complex references (regex patterns, computed imports) may not be detected
- Review `reference-map.json` to see what was found
- Manually check those files after execution

### Problem: "I want to undo everything"
```bash
git checkout HEAD  # Restore from git
rm -rf cortex-brain/snapshots/  # Clean up snapshots
```

### Problem: "The naming suggestions don't match my style"
- Edit `cortex-brain/vacuum/config.yaml`
- Modify the `abbreviations` section
- Re-run analysis

---

## Full Documentation

Complete specification available in:
📖 `/Users/asifhussain/PROJECTS/CORTEX/cortex-vacuum.prompt.md`

This document includes:
- Detailed classification rules
- Reference update strategy
- Consolidation rules for reports
- Target directory structure
- Safety guarantees
- Special cases and exceptions

---

## Command Reference

```bash
# Analyze (non-destructive)
python scripts/run-cortex-vacuum.py analyze [--output-dir DIR]

# Execute migration
python scripts/run-cortex-vacuum.py execute --plan FILE [--dry-run] [--auto-approve]

# Verify compliance
python scripts/run-cortex-vacuum.py verify [--fail-on-violations]

# Rollback (experimental)
python scripts/run-cortex-vacuum.py rollback --snapshot FILE

# Get help
python scripts/run-cortex-vacuum.py --help
python scripts/run-cortex-vacuum.py analyze --help
```

---

## Support & Questions

For detailed information:
- See `cortex-vacuum.prompt.md` for full specification
- Check `cortex-brain/vacuum/README.md` for technical details
- Review tool source code:
  - `src/mcp/tools/cortex_vacuum_analyzer.py`
  - `src/mcp/tools/cortex_vacuum_executor.py`

---

**Next Step**: Run the analysis!

```bash
python scripts/run-cortex-vacuum.py analyze --output-dir cortex-brain/vacuum/
```

Good luck! 🚀
