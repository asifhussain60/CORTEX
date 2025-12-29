# CORTEX Code Refinement Toolkit

**Purpose:** Automated code refinement tools for CORTEX codebase improvements.

**Version:** 1.0.0 | **Date:** December 16, 2025

---

## Overview

The Code Refinement Toolkit provides automated solutions for common codebase improvements:

1. **Path Hardening** - Fix hardcoded development paths for production compatibility
2. **Import Optimization** - (Future) Organize and optimize imports
3. **Type Annotation** - (Future) Add type hints automatically
4. **Code Formatting** - (Future) Apply consistent formatting

---

## Batch Path Hardening

### Purpose

Automatically replaces hardcoded development paths like `Path(__file__).parent.parent.parent` with production-safe resource resolver calls.

**Problem:**
```python
# BREAKS in production (points to site-packages)
project_root = Path(__file__).parent.parent.parent
brain_path = project_root / "cortex-brain"
```

**Solution:**
```python
# WORKS everywhere (uses resource resolver)
from src.utils.resource_resolver import get_root_path, get_brain_path
project_root = get_root_path()
brain_path = get_brain_path()
```

---

## Usage

### Command Line Interface

**Preview changes (dry-run mode):**
```bash
# All modules
python scripts/refine.py paths --dry-run

# Specific module
python scripts/refine.py paths --module tier1 --dry-run
```

**Apply changes:**
```bash
# Specific module
python scripts/refine.py paths --module tier1 --apply

# All modules
python scripts/refine.py paths --apply-all
```

### Python API

**Basic usage:**
```python
from scripts.batch_path_hardening import PathHardeningOrchestrator

orchestrator = PathHardeningOrchestrator()

# Dry run (preview)
result = orchestrator.execute(module="tier1", dry_run=True)

# Apply changes
result = orchestrator.execute(module="tier1", dry_run=False)

# Generate report
report = orchestrator.generate_report(result)
print(report)
```

**Integration with QA Orchestrator:**
```python
from src.orchestration_3_0.orchestrators.qa.qa_orchestrator import create_qa_orchestrator

qa = create_qa_orchestrator()

# Execute path hardening
result = qa.execute_path_hardening(module="tier1", dry_run=False)

# Generate report
report = qa.generate_path_hardening_report(result)
```

---

## Features

### Automatic Import Management

The tool automatically adds required imports:

```python
# Before
project_root = Path(__file__).parent.parent.parent

# After (import added automatically)
from src.utils.resource_resolver import get_root_path

project_root = get_root_path()
```

### Pattern Detection

Detects multiple hardcoded path patterns:

1. **Project root:** `Path(__file__).parent.parent.parent`
2. **Brain directory:** `Path(__file__).parent.parent.parent / "cortex-brain"`
3. **Brain files:** `Path(__file__).parent.parent.parent / "cortex-brain" / "file.yaml"`

### Safety Features

1. **Dry-run mode** - Preview changes before applying
2. **Automatic backups** - Creates timestamped backups before modifications
3. **Context validation** - Analyzes surrounding code for safe replacement
4. **Error handling** - Graceful failure with detailed error messages

### Detailed Reporting

Generates comprehensive reports including:
- Total files scanned/processed
- Number of replacements made
- Specific changes with line numbers
- Errors and skipped files
- Timestamp and mode (dry-run vs applied)

Reports saved to: `cortex-brain/documents/reports/path-hardening-report-{timestamp}.md`

---

## Architecture

### PathHardeningOrchestrator

**Core class** for batch path operations.

**Key methods:**
- `scan_files(module)` - Find files with hardcoded paths
- `analyze_file(file_path)` - Generate replacements for a file
- `apply_replacements(replacements, dry_run)` - Execute changes
- `execute(module, dry_run)` - Full workflow orchestration
- `generate_report(result)` - Create detailed report

**Workflow:**
```
scan_files() → analyze_file() → apply_replacements() → generate_report()
```

### PathReplacement

**Data class** representing a single replacement:
```python
@dataclass
class PathReplacement:
    file_path: Path
    line_number: int
    old_pattern: str
    new_pattern: str
    context_before: str
    context_after: str
    reason: str
```

### BatchResult

**Data class** containing operation results:
```python
@dataclass
class BatchResult:
    total_files: int
    files_processed: int
    replacements_made: int
    errors: List[str]
    skipped_files: List[str]
    replacements: List[PathReplacement]
    dry_run: bool
```

---

## Integration Points

### QA Orchestrator

Path hardening integrated into QA workflow:

```python
qa_orchestrator.execute_path_hardening(
    module="tier1",
    dry_run=False
)
```

### Refinement Workflows

Can be invoked as part of larger refinement workflows:

1. Path hardening
2. Code review
3. Security scan
4. Performance analysis
5. Architecture review

---

## Configuration

### Skip Patterns

Files automatically skipped:
- `*/config.py` - Uses own resolution
- `*/resource_resolver.py` - The utility itself
- `*/test_*.py` - Test files (validate separately)
- `*/__pycache__/*` - Compiled bytecode
- `*/archive/*` - Archived code

### Backup Location

Backups stored at: `cortex-brain/backups/path-hardening/backup_{timestamp}/`

Each backup includes:
- Original file copies
- `manifest.json` with metadata

---

## Examples

### Example 1: Fix Single Module

```bash
# Preview tier1 changes
python scripts/refine.py paths --module tier1 --dry-run

# Review report
# If satisfied, apply:
python scripts/refine.py paths --module tier1 --apply
```

### Example 2: Progressive Refinement

```python
from scripts.batch_path_hardening import PathHardeningOrchestrator

orchestrator = PathHardeningOrchestrator()

# Process brain tiers progressively
for module in ['tier0', 'tier1', 'tier2', 'tier3']:
    print(f"\n=== Processing {module} ===")
    result = orchestrator.execute(module=module, dry_run=False)
    print(f"✅ {result.replacements_made} replacements in {result.files_processed} files")
```

### Example 3: Integrated QA Workflow

```python
from src.orchestration_3_0.orchestrators.qa.qa_orchestrator import create_qa_orchestrator

qa = create_qa_orchestrator()

# Step 1: Path hardening
path_result = qa.execute_path_hardening(module="operations", dry_run=False)
print(qa.generate_path_hardening_report(path_result))

# Step 2: Code review on changed files
changed_files = [str(r.file_path) for r in path_result.replacements]
review_context = WorkflowContext(inputs={
    'files': changed_files,
    'depth': 'STANDARD',
    'project_path': '.'
})
qa_result = qa.execute(review_context)
```

---

## Best Practices

### 1. Always Dry-Run First

```bash
# ✅ GOOD
python scripts/refine.py paths --dry-run
# Review report
python scripts/refine.py paths --apply-all

# ❌ BAD
python scripts/refine.py paths --apply-all  # No preview!
```

### 2. Process in Batches

Process by module for better control:

```bash
python scripts/refine.py paths --module tier0 --apply
python scripts/refine.py paths --module tier1 --apply
python scripts/refine.py paths --module tier2 --apply
```

### 3. Review Reports

Check generated reports before continuing:

```bash
cat cortex-brain/documents/reports/path-hardening-report-*.md | tail -100
```

### 4. Test After Changes

Run tests after applying changes:

```bash
python scripts/refine.py paths --module tier1 --apply
pytest tests/tier1/
```

---

## Troubleshooting

### Issue: Import Not Added

**Symptom:** Replacement made but import missing

**Solution:** File may have complex import structure. Add manually:
```python
from src.utils.resource_resolver import get_root_path
```

### Issue: Context Mismatch

**Symptom:** Replacement failed with "pattern not found"

**Solution:** File may have unusual formatting. Fix manually or adjust patterns.

### Issue: Backup Failure

**Symptom:** "Permission denied" creating backup

**Solution:** Ensure write permissions:
```bash
chmod -R u+w cortex-brain/backups/
```

---

## Roadmap

**Version 1.1:**
- Import optimization (organize, remove unused)
- Duplicate code detection

**Version 1.2:**
- Type annotation inference
- Docstring generation

**Version 2.0:**
- AI-powered refactoring suggestions
- Full CORTEX LENS integration

---

## Files

| File | Purpose | LOC |
|------|---------|-----|
| `scripts/batch_path_hardening.py` | Core orchestrator | ~450 |
| `scripts/refine.py` | CLI wrapper | ~120 |
| `src/orchestration_3_0/orchestrators/qa/qa_orchestrator.py` | Integration | +60 |

**Total:** ~630 LOC

---

**Last Updated:** December 16, 2025  
**Author:** Asif Hussain  
**Status:** ✅ Production Ready
