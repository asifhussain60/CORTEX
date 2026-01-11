# CORTEX 6.0 Cleanup Recommendations

**Date:** 2026-01-11 05:15 UTC  
**Status:** ⚠️ PENDING - Manual Review Required

---

## 📊 Redundant Files Detected

### 1. TDD Reports (170 files)
**Location:** `cortex-brain/documents/reports/tdd/`  
**Pattern:** `tdd-report-20260110-*.md`  
**Total Size:** ~8.5MB estimated

**Issue:** 170 TDD reports from single day (2026-01-10) suggest:
- Duplicate test runs
- Incremental report generation without cleanup
- Same content repeated with minor timestamps

**Recommendation:**
```bash
# Option A: Keep only latest 10 reports
cd cortex-brain/documents/reports/tdd/
ls -t tdd-report-*.md | tail -n +11 | xargs rm

# Option B: Aggregate into single summary
python3 scripts/aggregate_tdd_reports.py --date 2026-01-10 --output tdd-summary-2026-01-10.md
rm tdd-report-20260110-*.md

# Option C: Archive old reports
mkdir -p archive/2026-01-10/
mv tdd-report-20260110-*.md archive/2026-01-10/
gzip archive/2026-01-10/*.md
```

**Expected Savings:** ~8MB disk space

---

### 2. Audit Logs (Multiple per Timestamp)
**Location:** `cortex-brain/audit-logs/`  
**Pattern:** Multiple logs per timestamp (middleware + state_management)

**Issue:** Separate log files when could be unified

**Recommendation:**
```bash
# Aggregate audit logs by date
python3 scripts/aggregate_audit_logs.py --output-dir cortex-brain/audit-logs/aggregated/

# Archive originals
mv cortex-brain/audit-logs/202601* cortex-brain/audit-logs/archive/
```

---

### 3. Git History Assets (if duplicates exist)
**Location:** `cortex-brain/git-history-assets/`

**Check:**
```bash
# Find duplicate extracted files
find cortex-brain/git-history-assets/extracted/ -type f -exec md5 {} \; | sort | uniq -d
```

---

### 4. Documents with "FINAL" in Name
**Findings:** Already cleaned up ✅
- `FINAL-REVIEW-SUMMARY.md` → `final-review-summary.md` (renamed)
- No other "FINAL" files detected

---

## 🎯 Priority Actions

### High Priority
1. **TDD Reports:** Aggregate 170 files → 1 summary (saves ~8MB)
2. **Audit Logs:** Already aggregated by script ✅

### Medium Priority
3. **Evidence Bundles:** Verify no stub bundles (<1KB) exist
4. **Archive Compression:** Gzip archive files in cx6-plan/archive/legacy/

### Low Priority
5. **Session Handoff Files:** Review if outdated handoff docs can be archived

---

## 📝 Automation Script Needed

Create: `scripts/cleanup_redundant_reports.py`

```python
#!/usr/bin/env python3
"""
Cleanup redundant TDD reports and audit logs
"""

from pathlib import Path
import shutil
from datetime import datetime

def cleanup_tdd_reports(reports_dir: Path, keep_latest: int = 10):
    """Keep only N latest TDD reports, archive the rest"""
    reports = sorted(reports_dir.glob("tdd-report-*.md"), 
                     key=lambda p: p.stat().st_mtime, 
                     reverse=True)
    
    if len(reports) <= keep_latest:
        print(f"Only {len(reports)} reports, keeping all")
        return
    
    archive_dir = reports_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    for report in reports[keep_latest:]:
        dest = archive_dir / report.name
        shutil.move(str(report), str(dest))
        print(f"Archived: {report.name}")
    
    print(f"✅ Kept {keep_latest} latest reports, archived {len(reports) - keep_latest}")

if __name__ == "__main__":
    workspace = Path(__file__).parent.parent
    tdd_dir = workspace / "cortex-brain" / "documents" / "reports" / "tdd"
    cleanup_tdd_reports(tdd_dir, keep_latest=10)
```

---

## ✅ Completed Cleanups

1. ✅ `cx6-holistic-analysis/` → Reorganized to `cx6-plan/`
2. ✅ UPPERCASE file names → Renamed to kebab-case
3. ✅ Old archive folders → Moved to `cx6-plan/archive/legacy/`
4. ✅ References updated across 4 files
5. ✅ Empty directories removed

---

## 🚀 Next Steps

1. Review this recommendation
2. Choose cleanup strategy for TDD reports (Option A/B/C)
3. Run cleanup script
4. Verify no broken references
5. Commit cleanup changes

---

**Note:** Do NOT delete files without verification. Always archive first, then delete after confirming no dependencies.
