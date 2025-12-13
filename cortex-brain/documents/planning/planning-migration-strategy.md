# CORTEX Planning Migration Strategy

**Date:** December 13, 2025  
**Author:** Asif Hussain  
**Version:** 1.0.0  
**Status:** 📋 READY FOR EXECUTION

---

## 🎯 Executive Summary

**Objective:** Migrate 99+ planning documents from flat file structure to hierarchical folder-based organization.

**Approach:** Phased migration with TDD validation, backward compatibility, and zero downtime.

**Timeline:** 2-3 weeks (HIGH: 2 days, MEDIUM: 1 week, LOW: 1 week)

**Risk:** LOW (automated with dry-run validation)

---

## 📋 Migration Phases

### Phase 1: HIGH Priority Plans (2 days)

**Scope:** 6 major enhancement plans

#### 1.1 Orchestrator Enhancement V2 (COMPLETE)
**Source:** `orchestrator-enhancement-plan-v2.md` (3,078 lines)  
**Target:** `completed/orchestrator-enhancement-v2/`

**Actions:**
```bash
# 1. Create folder
mkdir -p cortex-brain/documents/planning/completed/orchestrator-enhancement-v2

# 2. Split plan into master + sub-plans
# - MASTER-PLAN.md (executive summary, timeline, DoR/DoD)
# - 01-feature-9-progress-renderer.md
# - 02-feature-10-metrics-collector.md
# - 03-feature-11-holistic-review.md
# - 04-feature-12-task-injection.md
# - 05-feature-13-checkpoint-system.md
# - 06-feature-14-knowledge-graph-updater.md
# - 07-feature-15-parallel-coordination.md
# - 08-feature-16-analytics-dashboard.md
# - completion-report.md (copy from v2-orchestrator-completion-report.md)

# 3. Create metadata.json
cat > metadata.json << EOF
{
  "plan_name": "Orchestrator Enhancement Plan V2",
  "version": "2.0",
  "status": "COMPLETE",
  "created": "2025-12-13",
  "completed": "2025-12-13",
  "features": 8,
  "test_coverage": "221/221 passing",
  "git_commits": ["f9949480", "08bb692f"],
  "parent_plan": "../orchestrator-enhancement-v1/",
  "related_plans": ["../cortex-4.0/"]
}
EOF

# 4. Move original to archive
git mv orchestrator-enhancement-plan-v2.md completed/orchestrator-enhancement-v2/ORIGINAL.md
```

**Validation:**
- ✅ All 8 sub-plans created
- ✅ Metadata.json valid JSON
- ✅ Git history preserved
- ✅ No broken imports

---

#### 1.2 Orchestrator Enhancement V1 (COMPLETE)
**Source:** `orchestrator-enhancement-plan-v1.md`  
**Target:** `completed/orchestrator-enhancement-v1/`

**Actions:** (Same pattern as V2)

---

#### 1.3 Orchestration Master Plan (IN PROGRESS)
**Source:** `orchestration-master-plan.md` (1,260+ lines)  
**Target:** `active/orchestration-master-plan/`

**Sub-Plans:**
- `MASTER-PLAN.md` (phases overview)
- `01-tdd-orchestrator.md`
- `02-devops-orchestrator.md`
- `03-qa-orchestrator.md`
- `04-planning-orchestrator.md`
- `05-execution-orchestrator.md`
- `06-documentation-orchestrator.md`
- `07-intelligence-orchestrator.md`
- `08-observability-orchestrator.md`
- `09-onboarding-orchestrator.md`

**Metadata:**
```json
{
  "plan_name": "CORTEX 3.0 → 4.0 Orchestration Master Plan",
  "version": "2.0",
  "status": "IN_PROGRESS",
  "created": "2025-12-10",
  "orchestrators": 9,
  "phases": 7,
  "timeline_months": 12,
  "related_plans": ["../cortex-4.0/", "../orchestrators/"]
}
```

---

#### 1.4 Admin Dashboard Enhancement (IN PROGRESS)
**Source:** `admin-dashboard-holistic-enhancement-plan.md`  
**Target:** `active/admin-dashboard-enhancement/`

**Sub-Plans:**
- `MASTER-PLAN.md`
- `01-architecture-review.md`
- `02-feature-implementation.md`
- `03-testing-strategy.md`

---

#### 1.5 Dashboard Unified Plan (IN PROGRESS)
**Source:** `dashboard-unified-plan.md`  
**Target:** `active/dashboard-unified-plan/`

---

#### 1.6 CORTEX 4.0 Vision (ALREADY COMPLIANT)
**Action:** None (already in `cortex-4.0/` folder)

---

### Phase 2: MEDIUM Priority Plans (1 week)

**Scope:** 8 ADO plans + 5 application plans

#### 2.1 RA Migration Consolidation
**Sources:**
- `ra-migration-plan-v2-changes.md`
- `ra-migration-progress-tracker.md`
- `ra-funding-invoices-migration-plan.md`
- `ra-migration-coherence-audit.md`

**Target:** `ado/ra-migration/`

**Actions:**
```bash
mkdir -p cortex-brain/documents/planning/ado/ra-migration

# Consolidate
# - MASTER-PLAN.md (overview of RA migration)
# - 01-v2-changes.md
# - 02-progress-tracker.md (live document)
# - 03-funding-invoices.md
# - 04-coherence-audit.md
# - metadata.json
```

---

#### 2.2 BadMonolith Modernization
**Sources:**
- `badmonolith-modernization-plan.md`
- `BadMonolith-to-Cortex-Clean-Refactoring-Plan.md`

**Target:** `active/badmonolith-modernization/`

---

### Phase 3: LOW Priority Plans (1 week)

**Scope:** Phase reports, template plans, misc documents

#### 3.1 Archive Completed Phase Reports
**Sources:**
- `PHASE-1-COMPLETION-REPORT.md`
- `phase-3-implementation-summary.md`
- `phase-4-subplans-completion-report.md`

**Target:** `completed/phase-reports/`

---

#### 3.2 Template Enhancement Plans
**Sources:** Multiple template-related markdown files

**Target:** `completed/template-enhancements/` OR keep in root if active

---

### Phase 4: Root Cleanup (1 day)

**Actions:**
1. Move status documents to `active/` if in-use OR delete if stale
2. Keep only:
   - `README.md` (navigation index)
   - `INDEX.md` (if needed)
   - Active status trackers (<5 files)
3. Verify all folders have `metadata.json`
4. Create navigation `README.md` in root

---

## 🛠️ Migration Tools

### Automated Migration Script

```python
# src/operations/modules/planning/migrate_plan.py

from pathlib import Path
import json
import shutil
from typing import Dict, List

def migrate_plan_to_folder(
    source_file: str,
    target_folder: str,
    sub_plan_count: int = 0,
    status: str = "IN_PROGRESS"
) -> Dict:
    """
    Migrate single planning document to folder structure.
    
    Args:
        source_file: Path to original plan markdown
        target_folder: Target folder path
        sub_plan_count: Number of sub-plans to create (0 = single file)
        status: Plan status (IN_PROGRESS, COMPLETE, ARCHIVED)
        
    Returns:
        Migration report
    """
    source = Path(source_file)
    target = Path(target_folder)
    
    # Create folder
    target.mkdir(parents=True, exist_ok=True)
    
    # Move file
    if sub_plan_count == 0:
        # Simple migration (no sub-plans)
        shutil.copy2(source, target / "MASTER-PLAN.md")
    else:
        # Complex migration (requires manual splitting)
        shutil.copy2(source, target / "ORIGINAL.md")
        print(f"⚠️  MANUAL SPLIT REQUIRED: {target / 'ORIGINAL.md'}")
        print(f"   Create {sub_plan_count} sub-plans")
    
    # Create metadata
    metadata = {
        "plan_name": source.stem,
        "status": status,
        "migrated_date": "2025-12-13",
        "source_file": str(source),
        "sub_plans": sub_plan_count
    }
    
    with open(target / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    return {
        "success": True,
        "source": str(source),
        "target": str(target),
        "metadata_created": True
    }

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python migrate_plan.py <source> <target> [sub_plans] [status]")
        sys.exit(1)
    
    result = migrate_plan_to_folder(
        sys.argv[1],
        sys.argv[2],
        int(sys.argv[3]) if len(sys.argv) > 3 else 0,
        sys.argv[4] if len(sys.argv) > 4 else "IN_PROGRESS"
    )
    
    print(f"✅ Migration complete: {result['target']}")
```

**Usage:**
```bash
# Simple migration (no sub-plans)
python scripts/migrate_plan.py \
  "cortex-brain/documents/planning/some-plan.md" \
  "cortex-brain/documents/planning/active/some-plan" \
  0 \
  "IN_PROGRESS"

# Complex migration (8 sub-plans)
python scripts/migrate_plan.py \
  "cortex-brain/documents/planning/orchestrator-enhancement-plan-v2.md" \
  "cortex-brain/documents/planning/completed/orchestrator-enhancement-v2" \
  8 \
  "COMPLETE"
```

---

## ✅ Validation Checklist

After each migration, verify:

### Folder Structure
- [ ] Folder created in correct location (`active/`, `completed/`, `ado/`)
- [ ] MASTER-PLAN.md exists
- [ ] Sub-plans created (if applicable)
- [ ] metadata.json exists and valid

### Content Integrity
- [ ] All content from original file preserved
- [ ] Headings properly formatted
- [ ] Links updated (if referencing other plans)
- [ ] Images/diagrams copied

### Git History
- [ ] Original file moved with `git mv` (preserves history)
- [ ] Commit message follows convention: `refactor: Migrate [plan name] to folder structure`

### Backward Compatibility
- [ ] No broken imports in code
- [ ] No broken links in documentation
- [ ] Tests still passing

### Metadata
- [ ] plan_name matches folder name
- [ ] status accurate (IN_PROGRESS, COMPLETE, ARCHIVED)
- [ ] git_commits listed (if available)
- [ ] related_plans linked

---

## 🚨 Rollback Strategy

If migration causes issues:

```bash
# Rollback single plan
git revert HEAD

# Rollback entire phase
git reset --hard <commit_before_phase>

# Restore original structure
git checkout HEAD~1 -- cortex-brain/documents/planning/[original-file].md
```

---

## 📊 Progress Tracking

Create `migration-progress.md` in planning root:

```markdown
# Planning Migration Progress

## Phase 1: HIGH Priority (2 days)
- [x] Orchestrator Enhancement V2 → completed/
- [x] Orchestrator Enhancement V1 → completed/
- [ ] Orchestration Master Plan → active/
- [ ] Admin Dashboard Enhancement → active/
- [ ] Dashboard Unified Plan → active/
- [x] CORTEX 4.0 Vision (already compliant)

## Phase 2: MEDIUM Priority (1 week)
- [ ] RA Migration → ado/ra-migration/
- [ ] BadMonolith → active/badmonolith-modernization/
- [ ] [other plans...]

## Phase 3: LOW Priority (1 week)
- [ ] Phase Reports → completed/phase-reports/
- [ ] Template Plans → completed/template-enhancements/

## Phase 4: Root Cleanup (1 day)
- [ ] Move status docs
- [ ] Create navigation README
- [ ] Verify metadata.json in all folders
```

---

## 🎯 Success Metrics

Migration is successful when:

1. **Structure:** 95%+ plans in folder structure
2. **Metadata:** All folders have valid metadata.json
3. **Navigation:** Root README.md provides clear index
4. **Tests:** 100% tests passing
5. **References:** Zero broken links/imports
6. **Git:** History preserved for all files
7. **Root Directory:** <20 files remaining

---

## 📞 Next Steps

1. **Dry-Run Phase 1** on test plans
2. **Execute Phase 1** (HIGH priority)
3. **Validate** with checklist
4. **Continue** to Phase 2 & 3
5. **Create** deployment guide for machines pulling changes

---

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Version:** 3.8.1
