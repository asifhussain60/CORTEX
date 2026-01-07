# CORTEX-5.0 Planning Folder Structure Violation Analysis

**Issue ID:** planning-root-pollution  
**Severity:** 🔴 HIGH (Brain Protection Rule Violation)  
**Date Detected:** January 4, 2026  
**Detected By:** User (Asif Hussain)  
**Status:** 🔍 UNDER INVESTIGATION  

---

## 🎯 Issue Summary

The CORTEX-5.0 planning folder has **14+ root-level markdown files** that violate the brain protection rule `FILE_ORGANIZATION_ENFORCEMENT`. These files should be organized into proper subfolders according to the planning system v4.0 manifest.

---

## 📊 Violation Details

### Brain Protection Rule Violated

**Rule:** `FILE_ORGANIZATION_ENFORCEMENT`  
**File:** `cortex-brain/brain-protection-rules.yaml` (lines 5473-5550)  
**Severity:** BLOCKED  

**Description:** "All documents MUST be created in cortex-brain/documents/{category}/ with filename ≤20 characters. Root-level files in any folder are PROHIBITED."

### Planning System Requirements

**Manifest:** `planning-system-4.0-manifest.yaml` (lines 1445-1475)

**Required Folder Structure:**
```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-MASTER-PLAN.md              # ✅ Allowed at root
├── context/                        # ⏳ Required subfolder
│   ├── architecture-design.md
│   ├── vision-documents.md
│   └── user-personas.md
├── reports/                        # ⏳ Required subfolder
│   ├── phase-completion.md
│   ├── status-updates.md
│   └── analysis-reports.md
├── artifacts/                      # ⏳ Required subfolder
│   ├── diagrams/
│   ├── templates/
│   └── reference-docs.md
├── tracking/                       # ✅ CORRECT
│   └── epic-progress-tracker.json
└── {SUB-PLAN-ID}/                 # ✅ CORRECT
    ├── 00-{sub-plan}.md
    ├── context/
    ├── reports/
    └── artifacts/
```

---

## 🔍 Current State Audit

### Root-Level Files in CORTEX-5.0 Folder

**Violating Files (should be in subfolders):**

1. `EPIC-FEATURE-PLANNER-VISION.md` → `context/epic-feature-planner-vision.md`
2. `EPIC-TRANSFORMATION-COMPLETE.md` → `reports/epic-transformation-complete.md`
3. `HOLISTIC-REFINEMENT-ANALYSIS.md` → `reports/holistic-refinement-analysis.md`
4. `ONBOARDING-PLANNING-COMPLETE.md` → `reports/onboarding-planning-complete.md`
5. `ONBOARDING-UX-OVERVIEW.md` → `context/onboarding-ux-overview.md`
6. `ORCHESTRATOR-QUICK-REFERENCE.md` → `context/orchestrator-quick-ref.md` (renamed for length)
7. `QUICK-START.md` → `context/quick-start.md`
8. `README-ORCHESTRATOR.md` → `context/orchestrator-readme.md` (renamed)
9. `README.md` → `context/plan-readme.md` (disambiguate)
10. `SHARED-ORCHESTRATOR-INFRASTRUCTURE-COMPLETE.md` → `reports/shared-infra-complete.md` (renamed for length)
11. `USER-PERSONAS.md` → `context/user-personas.md`
12. `VISUAL-SUMMARY.md` → `reports/visual-summary.md`
13. `master-orchestrator-wiring.md` → `context/orchestrator-wiring.md` (renamed)
14. `vscode-cache-optimization-enhancement.md` → `00D-vscode-cache-optimization/context/enhancement-proposal.md`
15. `13-14-15-README.md` → `context/sub-plans-13-15-readme.md` (renamed)

**Allowed Files (legitimate root-level):**
- ✅ `00-MASTER-REMEDIATION-PLAN.md` (epic master plan)
- ✅ `plan_orchestrator.py` (orchestrator script)
- ✅ `.orchestrator-state.json` (orchestrator state)

**Correct Folders:**
- ✅ `tracking/` (epic progress tracker JSON)
- ✅ `00A-epic-structure-cleanup/` (sub-plan folder)
- ✅ `00B-epic-feature-planner/` (sub-plan folder)
- ✅ ... (all other sub-plan folders)

---

## 🎯 Root Cause Analysis

### Why This Happened

**1. No Automated Folder Creation**
- Planning system v4.0 has `plan_scaffold_generator.py` utility
- CORTEX-5.0 plan was created manually without using scaffolding tool
- Universal subfolders (`context/`, `reports/`, `artifacts/`) not auto-created

**2. Developer Convenience**
- Easier to create files at root than navigate to correct subfolder
- No enforcement mechanism during file creation
- Brain protection rule not checked proactively

**3. Legacy Behavior**
- Earlier planning versions allowed more flexible structure
- CORTEX-5.0 created before v4.0 manifest fully enforced

---

## ✅ Recommended Solution

### Phase 1: Immediate Cleanup (30 minutes)

**Create missing universal subfolders:**
```bash
cd cortex-brain/documents/planning/active/CORTEX-5.0
mkdir -p context/ reports/ artifacts/
```

**Move files to correct locations:**
```bash
# Context documents (vision, design, reference)
git mv EPIC-FEATURE-PLANNER-VISION.md context/epic-feature-planner-vision.md
git mv ONBOARDING-UX-OVERVIEW.md context/onboarding-ux-overview.md
git mv USER-PERSONAS.md context/user-personas.md
git mv ORCHESTRATOR-QUICK-REFERENCE.md context/orchestrator-quick-ref.md
git mv QUICK-START.md context/quick-start.md
git mv README-ORCHESTRATOR.md context/orchestrator-readme.md
git mv README.md context/plan-readme.md
git mv master-orchestrator-wiring.md context/orchestrator-wiring.md
git mv 13-14-15-README.md context/sub-plans-13-15-readme.md

# Reports (completion, status, analysis)
git mv EPIC-TRANSFORMATION-COMPLETE.md reports/epic-transformation-complete.md
git mv HOLISTIC-REFINEMENT-ANALYSIS.md reports/holistic-refinement-analysis.md
git mv ONBOARDING-PLANNING-COMPLETE.md reports/onboarding-planning-complete.md
git mv SHARED-ORCHESTRATOR-INFRASTRUCTURE-COMPLETE.md reports/shared-infra-complete.md
git mv VISUAL-SUMMARY.md reports/visual-summary.md

# Move to sub-plan context
git mv vscode-cache-optimization-enhancement.md 00D-vscode-cache-optimization/context/enhancement-proposal.md
```

**Commit changes:**
```bash
git add -A
git commit -m "refactor(CORTEX-5.0): Enforce proper folder structure - move root files to context/reports/

- Moved 9 files to context/ (vision, design, reference docs)
- Moved 5 files to reports/ (completion reports, analysis)
- Moved 1 file to 00D sub-plan context/
- Renamed files >20 chars to comply with brain protection rules
- Enforces planning-system-4.0-manifest.yaml folder structure
- Resolves FILE_ORGANIZATION_ENFORCEMENT violation"

git push origin CORTEX-5.0
```

### Phase 2: Update References (15 minutes)

**Files that may link to moved documents:**
- `00-MASTER-REMEDIATION-PLAN.md` (master plan may reference context docs)
- Sub-plan `00-*.md` files (may link to context/reports)
- `plan_orchestrator.py` (may reference README paths)

**Search and update:**
```bash
# Find references to moved files
grep -r "EPIC-FEATURE-PLANNER-VISION" .
grep -r "USER-PERSONAS" .
grep -r "README-ORCHESTRATOR" .
# ... etc.

# Update with new paths:
# EPIC-FEATURE-PLANNER-VISION.md → context/epic-feature-planner-vision.md
```

### Phase 3: Prevent Future Violations (15 minutes)

**Update brain protection rules:**

Add specific enforcement for epic/sub-plan structures in `brain-protection-rules.yaml`:

```yaml
- name: "Epic Planning Folder Structure Enforcement"
  severity: "blocked"
  description: "Epic plans MUST use universal subfolder structure: context/, reports/, artifacts/, tracking/. Only master plan (00-*.md), orchestrator scripts, and sub-plan folders allowed at root."
  
  detection:
    patterns:
      root_file_creation:
        - "*.md in planning/active/{epic}/ (not 00-*.md)"
        - "Missing context/ OR reports/ OR artifacts/ folders"
    scope: ["file_creation", "folder_structure"]
  
  alternatives:
    - "STEP 1: Use plan scaffold generator: python cortex-toolkit/core/utilities/plan_scaffold_generator.py 'EPIC-NAME'"
    - "STEP 2: Vision/design docs → context/"
    - "STEP 3: Completion/status reports → reports/"
    - "STEP 4: Diagrams/templates → artifacts/"
    - "STEP 5: Progress tracking → tracking/"
```

---

## 📋 Migration Script

**File:** `cortex-brain/documents/planning/active/CORTEX-5.0/artifacts/migrate-folder-structure.py`

```python
#!/usr/bin/env python3
"""
CORTEX-5.0 Folder Structure Migration Script

Moves root-level markdown files to proper subfolders according to
planning-system-4.0-manifest.yaml requirements.

Usage:
    python migrate-folder-structure.py --dry-run  # Preview changes
    python migrate-folder-structure.py --execute  # Apply changes
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# File categorization based on content/purpose
MIGRATIONS = {
    # Context documents (vision, design, reference)
    "context": [
        ("EPIC-FEATURE-PLANNER-VISION.md", "epic-feature-planner-vision.md"),
        ("ONBOARDING-UX-OVERVIEW.md", "onboarding-ux-overview.md"),
        ("USER-PERSONAS.md", "user-personas.md"),
        ("ORCHESTRATOR-QUICK-REFERENCE.md", "orchestrator-quick-ref.md"),
        ("QUICK-START.md", "quick-start.md"),
        ("README-ORCHESTRATOR.md", "orchestrator-readme.md"),
        ("README.md", "plan-readme.md"),
        ("master-orchestrator-wiring.md", "orchestrator-wiring.md"),
        ("13-14-15-README.md", "sub-plans-13-15-readme.md"),
    ],
    
    # Reports (completion, status, analysis)
    "reports": [
        ("EPIC-TRANSFORMATION-COMPLETE.md", "epic-transformation-complete.md"),
        ("HOLISTIC-REFINEMENT-ANALYSIS.md", "holistic-refinement-analysis.md"),
        ("ONBOARDING-PLANNING-COMPLETE.md", "onboarding-planning-complete.md"),
        ("SHARED-ORCHESTRATOR-INFRASTRUCTURE-COMPLETE.md", "shared-infra-complete.md"),
        ("VISUAL-SUMMARY.md", "visual-summary.md"),
    ],
}

# Special case: Move to sub-plan context
SUB_PLAN_MIGRATIONS = [
    ("vscode-cache-optimization-enhancement.md", "00D-vscode-cache-optimization/context/enhancement-proposal.md"),
]

def migrate_files(plan_root: Path, dry_run: bool = True):
    """Migrate files to proper folder structure."""
    
    print(f"\n{'🔍 DRY RUN' if dry_run else '⚡ EXECUTING'} Migration")
    print("=" * 60)
    
    # Create universal subfolders
    for folder in ["context", "reports", "artifacts"]:
        folder_path = plan_root / folder
        if not folder_path.exists():
            print(f"\n📁 Create: {folder}/")
            if not dry_run:
                folder_path.mkdir(parents=True, exist_ok=True)
    
    # Migrate files by category
    for category, files in MIGRATIONS.items():
        print(f"\n📂 Category: {category}/")
        for old_name, new_name in files:
            old_path = plan_root / old_name
            new_path = plan_root / category / new_name
            
            if old_path.exists():
                print(f"   📄 {old_name}")
                print(f"   └─→ {category}/{new_name}")
                
                if not dry_run:
                    shutil.move(str(old_path), str(new_path))
                    print("      ✅ Moved")
            else:
                print(f"   ⚠️  File not found: {old_name}")
    
    # Migrate sub-plan specific files
    print(f"\n📂 Sub-Plan Context:")
    for old_name, relative_new_path in SUB_PLAN_MIGRATIONS:
        old_path = plan_root / old_name
        new_path = plan_root / relative_new_path
        
        if old_path.exists():
            print(f"   📄 {old_name}")
            print(f"   └─→ {relative_new_path}")
            
            if not dry_run:
                new_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_path), str(new_path))
                print("      ✅ Moved")
    
    print(f"\n{'✅ Dry run complete' if dry_run else '🎉 Migration complete'}")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    plan_root = Path(__file__).parent.parent  # CORTEX-5.0 folder
    
    if len(sys.argv) < 2:
        print("Usage: python migrate-folder-structure.py [--dry-run|--execute]")
        sys.exit(1)
    
    dry_run = sys.argv[1] == "--dry-run"
    migrate_files(plan_root, dry_run=dry_run)
```

---

## 🎯 Success Criteria

### Immediate (Post-Migration)

- ✅ Zero markdown files at CORTEX-5.0 root (except `00-MASTER-REMEDIATION-PLAN.md`)
- ✅ All context docs in `context/` folder
- ✅ All reports in `reports/` folder
- ✅ All filenames ≤20 characters
- ✅ Universal subfolders created and populated

### Long-Term (Prevention)

- ✅ Brain protection rule updated with epic structure enforcement
- ✅ Plan scaffold generator integrated into workflow
- ✅ Developer documentation updated with folder structure requirements
- ✅ Future epic plans automatically create proper structure

---

## 📚 Related Documents

**Brain Protection Rules:**
- `cortex-brain/brain-protection-rules.yaml` (FILE_ORGANIZATION_ENFORCEMENT)

**Planning System Manifest:**
- `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml` (folder structure requirements)

**Scaffold Generator:**
- `cortex-toolkit/core/utilities/plan_scaffold_generator.py` (automated folder creation)

---

## ✅ Action Items

**Immediate (Today):**
1. [ ] Run migration script in dry-run mode
2. [ ] Review proposed changes
3. [ ] Execute migration
4. [ ] Update file references in master plan
5. [ ] Commit and push changes

**Follow-Up (This Week):**
6. [ ] Update brain protection rules with epic structure enforcement
7. [ ] Document folder structure in CORTEX-5.0 README
8. [ ] Add pre-commit hook to prevent future root-level files

---

**Analysis Author:** GitHub Copilot (CORTEX Assistant)  
**Date:** January 4, 2026  
**Severity:** HIGH (Brain Protection Violation)  
**Resolution:** Migration + Prevention
