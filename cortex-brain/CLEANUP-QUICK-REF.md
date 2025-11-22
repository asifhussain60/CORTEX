# CORTEX Cleanup - Quick Reference

**Version:** 2.0 | **Author:** Asif Hussain | **Date:** 2025-11-22

---

## 🚀 Quick Commands

```bash
# Preview what will be deleted (DRY-RUN)
python scripts/master_cleanup.py

# Actually delete files
python scripts/master_cleanup.py --execute

# Use existing scan report
python scripts/master_cleanup.py --skip-scan --execute
```

---

## 📊 What Gets Cleaned

### ✅ Removed
- Documentation files (*-SUMMARY.md, *-REPORT.md, *-ANALYSIS.md)
- Completion files (*-COMPLETE.md, *COMPLETION*.md)
- Progress files (*-PROGRESS.md, *-SESSION.md)
- Investigation files (*INVESTIGATION*.md)
- Guide files (*-GUIDE.md)
- Temporary files (temp-*.md)
- Fix reports (*-FIX-*.md)
- Integration docs (*INTEGRATION*.md)

### ❌ Protected
- Source code (*.py, *.js, *.ts, etc.)
- Configuration files (*.yaml, *.json)
- Essential docs (README.md, CHANGELOG.md)
- Active phase docs (PHASE-3-*, PHASE-4-*)
- Organized structures (cortex-brain/documents/)

---

## 🎯 Typical Results

```
📊 Summary:
   Files found: 92
   Files to delete: 77
   Files preserved: 15
   Space freed: 0.93 MB

⏱️ Execution Time: ~8 seconds
```

---

## 🛡️ Safety

✅ Dry-run by default  
✅ User confirmation required  
✅ Protected files never deleted  
✅ Rollback support (manifests)  
✅ Detailed execution reports  

---

## 📂 Reports Location

```
cortex-brain/cleanup-reports/
├── unnecessary-files-*.json      # Scan reports
└── cleanup-execution-*.json      # Execution reports
```

---

## 🔍 Individual Scripts

```bash
# Just scan (no cleanup)
python scripts/scan_unnecessary_files.py

# Just cleanup (requires scan report)
python scripts/cleanup_unnecessary_files.py
python scripts/cleanup_unnecessary_files.py --execute
```

---

## 📚 Full Documentation

See: `cortex-brain/documents/README-CLEANUP-SYSTEM.md`

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
