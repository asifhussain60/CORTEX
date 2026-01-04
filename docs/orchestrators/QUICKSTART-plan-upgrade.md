# 🚀 CORTEX Plan Upgrade - Quick Start

**5-Minute Guide to Upgrading Legacy Plans**

---

## 🎯 Quick Command

```bash
# From CORTEX workspace root
python cortex-upgrade-plan.py path/to/legacy-plan/
```

That's it! Your upgraded plan will be in `cortex-brain/documents/planning/active/[plan-name]-v5/`

---

## 📋 Step-by-Step

### 1. Locate Your Legacy Plan

```bash
# Plans are usually in one of these locations:
ls cortex-brain/documents/planning/active/
ls cortex-brain/documents/planning/features/
ls cortex-brain/documents/planning/temp-plans/
```

### 2. Run Upgrade

```bash
# Example: Upgrade a directory-based plan
python cortex-upgrade-plan.py cortex-brain/documents/planning/active/my-old-plan/

# Example: Upgrade a single-file plan
python cortex-upgrade-plan.py cortex-brain/documents/planning/features/feature-plan.md
```

### 3. Review Output

```bash
# Open the new master plan
code cortex-brain/documents/planning/active/my-old-plan-v5/00-master-plan.md

# Read the migration report
code cortex-brain/documents/planning/active/my-old-plan-v5/reports/migration-report.md
```

### 4. Update Placeholders

Search for `*()*` in `00-master-plan.md` and update with actual values:
- `*(Define phase goal)*`
- `*(Define tasks)*`
- `*(Define completion criteria)*`

### 5. Archive Old Plan (Optional)

```bash
# Re-run with --archive flag
python cortex-upgrade-plan.py cortex-brain/documents/planning/active/my-old-plan/ --archive
```

---

## ✅ What You Get

**New Plan Structure:**
```
my-old-plan-v5/
├── 00-master-plan.md          # ✅ CORTEX-5.0 compliant
├── context/                    # Your old context files (copied)
├── reports/
│   └── migration-report.md    # Auto-generated
├── artifacts/
└── tracking/
    └── progress-tracker.json  # Auto-generated
```

**Compliance Fixes:**
- ✅ Visual progress tracker
- ✅ REFACTOR phase (18+ tasks)
- ✅ Git checkpoints documented
- ✅ GIT_NO_PUSH_ENFORCEMENT
- ✅ SKULL rules section
- ✅ Proper folder structure

---

## 🎓 Examples

### Example 1: Simple Upgrade

```bash
$ python cortex-upgrade-plan.py cortex-brain/documents/planning/active/auth-feature/

🔍 Analyzing legacy plan: cortex-brain/documents/planning/active/auth-feature/

📊 Compliance Score: 45%
Issues Found: 6

⚠️  Compliance Issues:
  - Missing subfolders: context/, reports/, artifacts/, tracking/
  - Missing visual progress tracker
  - Missing REFACTOR phase
  - Missing git checkpoint references
  - Only 2 phases defined (recommend 5+)
  - No acceptance criteria defined

🔄 Generating CORTEX-5.0 compliant plan...
✅ New plan created: cortex-brain/documents/planning/active/auth-feature-v5
📄 Master plan: cortex-brain/documents/planning/active/auth-feature-v5/00-master-plan.md
📊 Migration report: cortex-brain/documents/planning/active/auth-feature-v5/reports/migration-report.md
```

### Example 2: Upgrade + Archive

```bash
$ python cortex-upgrade-plan.py old-plan.md --archive

🔍 Analyzing legacy plan: old-plan.md
📊 Compliance Score: 30%
🔄 Generating CORTEX-5.0 compliant plan...
✅ New plan created: cortex-brain/documents/planning/active/old-plan-v5
📦 Archiving legacy plan...
✅ Archived to: cortex-brain/documents/planning/archived/old-plan-archived-20260104_155423
```

---

## 🔧 Options

```bash
# Auto-archive old plan
python cortex-upgrade-plan.py plan/ --archive

# Custom output location
python cortex-upgrade-plan.py plan/ --output custom-location/

# Specify workspace root
python cortex-upgrade-plan.py plan/ --workspace /path/to/CORTEX/

# Show help
python cortex-upgrade-plan.py --help
```

---

## ⚠️ Common Gotchas

### Gotcha #1: Path Must Exist
```bash
# ❌ Wrong
python cortex-upgrade-plan.py nonexistent-plan/

# ✅ Correct
ls cortex-brain/documents/planning/active/  # Verify first
python cortex-upgrade-plan.py cortex-brain/documents/planning/active/actual-plan/
```

### Gotcha #2: Update Placeholders
The generated plan has placeholders like `*(Define tasks)*`. **You must update these!**

### Gotcha #3: Archive Is Permanent
`--archive` moves the old plan. Make sure the new plan is correct first!

---

## 📖 Full Documentation

See: [docs/orchestrators/plan-upgrade-orchestrator.md](plan-upgrade-orchestrator.md)

---

## 🆘 Quick Help

**Problem:** Upgraded plan missing phases  
**Solution:** Legacy plan may have non-standard headers. Check the migration report for what was extracted.

**Problem:** Want to rollback  
**Solution:** Copy from `archived/` back to `active/`

**Problem:** Need to customize REFACTOR tasks  
**Solution:** Edit `00-master-plan.md` after generation. All 18 tasks are templates.

---

**Ready to upgrade?** Just run:

```bash
python cortex-upgrade-plan.py path/to/your/legacy-plan/
```

---

**Copyright © 2026 Asif Hussain. All rights reserved.**
