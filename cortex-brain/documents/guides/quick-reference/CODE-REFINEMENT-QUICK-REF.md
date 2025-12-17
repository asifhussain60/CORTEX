# Code Refinement Toolkit - Quick Reference

**Fast access guide for CORTEX code refinement operations.**

---

## 🚀 Quick Commands

### Path Hardening

```bash
# Preview changes (all modules)
python scripts/refine.py paths --dry-run

# Preview specific module
python scripts/refine.py paths --module tier1 --dry-run

# Apply to specific module
python scripts/refine.py paths --module tier1 --apply

# Apply to all modules
python scripts/refine.py paths --apply-all
```

---

## 🎯 Common Workflows

### Progressive Module Processing

```bash
# Process brain tiers first
python scripts/refine.py paths --module tier0 --apply
python scripts/refine.py paths --module tier1 --apply
python scripts/refine.py paths --module tier2 --apply
python scripts/refine.py paths --module tier3 --apply

# Then operations
python scripts/refine.py paths --module operations --apply

# Then utilities
python scripts/refine.py paths --module utils --apply
```

### Safe Refinement Workflow

```bash
# 1. Preview
python scripts/refine.py paths --module tier1 --dry-run

# 2. Review report
cat cortex-brain/documents/reports/path-hardening-report-*.md | tail -50

# 3. Apply if satisfied
python scripts/refine.py paths --module tier1 --apply

# 4. Test changes
pytest tests/tier1/
```

---

## 🐍 Python API

### Basic Usage

```python
from scripts.batch_path_hardening import PathHardeningOrchestrator

orchestrator = PathHardeningOrchestrator()

# Dry run
result = orchestrator.execute(module="tier1", dry_run=True)

# Apply
result = orchestrator.execute(module="tier1", dry_run=False)

# Report
print(orchestrator.generate_report(result))
```

### QA Orchestrator Integration

```python
from src.orchestration_3_0.orchestrators.qa.qa_orchestrator import create_qa_orchestrator

qa = create_qa_orchestrator()

# Path hardening
result = qa.execute_path_hardening(module="tier1", dry_run=False)

# Report
print(qa.generate_path_hardening_report(result))
```

---

## 📊 Output Locations

| Item | Location |
|------|----------|
| Reports | `cortex-brain/documents/reports/path-hardening-report-{timestamp}.md` |
| Backups | `cortex-brain/backups/path-hardening/backup_{timestamp}/` |
| Manifests | `cortex-brain/backups/path-hardening/backup_{timestamp}/manifest.json` |

---

## ⚠️ Safety Tips

1. **Always dry-run first:** `--dry-run` before `--apply`
2. **Process in batches:** Module-by-module for control
3. **Review reports:** Check before continuing
4. **Test after changes:** Run tests on modified modules
5. **Check backups:** Verify backup created before applying

---

## 🔍 Pattern Detection

Tool detects and fixes these patterns:

| Pattern | Replacement |
|---------|-------------|
| `Path(__file__).parent.parent.parent` | `get_root_path()` |
| `Path(__file__).parent.parent.parent / "cortex-brain"` | `get_brain_path()` |
| `Path(__file__).parent.parent.parent / "cortex-brain" / "file.yaml"` | `get_brain_file("file.yaml")` |

---

## 📁 Module Names

Common module names for `--module` flag:

- `tier0`, `tier1`, `tier2`, `tier3` - Brain tiers
- `operations` - Operations modules
- `utils` - Utility functions
- `workflows` - Workflow orchestrators
- `plugins` - Plugin system
- `agents` - Agent implementations
- `orchestrators` - Orchestrator modules

---

## ✅ Success Indicators

**Dry-run output:**
```
🔍 PREVIEWING path hardening changes...
📁 Found 5 files with hardcoded paths
🔧 Generated 6 replacements
📊 Summary:
  Total files scanned: 5
  Files processed: 5
  Replacements made: 6
  Errors: 0
💡 This was a dry run.
```

**Apply output:**
```
✅ APPLYING path hardening changes...
✅ Backup created: cortex-brain/backups/path-hardening/backup_20251216_160856
📁 Found 5 files with hardcoded paths
🔧 Generated 6 replacements
✅ Path hardening complete!
   6 replacements in 5 files
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import not added | Add manually: `from src.utils.resource_resolver import get_root_path` |
| Pattern not found | Adjust manually or skip file |
| Backup permission denied | `chmod -R u+w cortex-brain/backups/` |
| Module not found | Check spelling, use lowercase |

---

**Full Guide:** `cortex-brain/documents/implementation-guides/code-refinement-toolkit.md`

**Author:** Asif Hussain | **Date:** December 16, 2025
