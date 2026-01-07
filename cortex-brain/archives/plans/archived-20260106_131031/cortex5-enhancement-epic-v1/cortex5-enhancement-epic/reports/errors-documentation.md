# Epic Folder Structure Errors - Documentation

**Date:** 2026-01-06  
**Epic:** cortex5-enhancement-epic  
**Status:** 🔴 NON-COMPLIANT with Planning System v5

---

## 🚨 Identified Errors

### Error 1: Scripts in Plan Folder
**Issue:** `*.sh` and `*.py` files stored directly in plan folder structure

**Found:**
```
cortex5-enhancement-epic/
├── cleanup-planning-active.sh          ❌ Should be toolkit-generated
├── cleanup-epic-structure.sh           ❌ Should be toolkit-generated
└── (potential .py files)               ❌ Should be toolkit-generated
```

**Rule Violation:** Scripts should be created via Toolkit Orchestrator, not stored in plan folders

**Correct Approach:**
- Scripts generated on-demand via Toolkit Orchestrator
- Stored in `cortex-toolkit/` or `scripts/` at workspace root
- Plan folder references them, doesn't contain them

---

### Error 2: Multiple Markdown Files in Root
**Issue:** Several `*.md` documents in root of plan folder

**Found:**
```
cortex5-enhancement-epic/
├── README.md                           ❌ Not allowed
├── A19-cortex-50-remedi-with.md       ❌ Not allowed
├── CORTEX5-SNOWBALL.md                ❌ Not allowed
├── PHASE-0.5-COMPLETE.md              ❌ Not allowed
├── STRUCTURE-REVIEW.md                ❌ Not allowed
└── (other .md files)                   ❌ Not allowed
```

**Rule Violation:** ONLY `plan-viewer.html` is allowed in plan root

**Correct Approach:**
- Master plan → `phases/master-plan.md`
- Tracking docs → `tracking/snowball.md`, `tracking/milestones.md`
- Review docs → `reports/structure-review.md`
- README → Not needed (plan-viewer.html serves this purpose)

---

### Error 3: Missing plan-viewer.html
**Issue:** The ONLY allowed root file is missing

**Expected:**
```
cortex5-enhancement-epic/
└── plan-viewer.html                    ✅ REQUIRED (ONLY root file allowed)
```

**Rule Violation:** Every plan MUST have auto-generated HTML viewer

**Correct Approach:**
- Planning Orchestrator v5 auto-generates `plan-viewer.html`
- Opens in browser at `http://localhost:8150/plan-viewer.html`
- Single source of truth for plan navigation

---

### Error 4: Wrong Folder Format
**Issue:** `plan-*` folders with incorrect naming

**Found:**
```
cortex5-enhancement-epic/
└── (no plan-* folders found in current state)
```

**Note:** This was cleaned in previous step, but documents for future prevention

**Rule Violation:** Child plans should not be nested inside parent epic

**Correct Approach:**
- Child plans at `planning/active/{plan-name}/` (sibling level)
- Epic folder only contains epic structure
- No nested plan folders

---

### Error 5: Missing Required Folders
**Issue:** Missing `phases/` and `features/` folders

**Current Structure:**
```
cortex5-enhancement-epic/
├── analysis/           ✅ Present
├── artifacts/          ✅ Present
├── context/            ✅ Present
├── reports/            ✅ Present
├── tracking/           ✅ Present
├── phases/             ❌ MISSING (REQUIRED)
└── features/           ❌ MISSING (REQUIRED)
```

**Rule Violation:** Plans MUST have 7 standard folders (not 5)

**Correct Structure:**
1. `analysis/` - Deep analysis documents
2. `artifacts/` - Generated artifacts
3. `context/` - Discovery + architecture
4. `features/` - Feature implementation tracking
5. `phases/` - Phase documents + master plan
6. `reports/` - Progress reports
7. `tracking/` - State tracking + metrics

---

## ✅ Correct Epic Structure (Future State)

```
cortex5-enhancement-epic/
│
├── plan-viewer.html                    # ✅ ONLY root file (auto-generated)
│
├── analysis/                           # Deep analysis
│   ├── requirements-analysis.md
│   ├── technical-architecture.md
│   └── dependency-analysis.md
│
├── artifacts/                          # Generated outputs
│   ├── diagrams/
│   ├── configs/
│   └── code-snippets/
│
├── context/                            # Discovery context
│   ├── discovery.md
│   └── architecture-analysis.md
│
├── features/                           # Feature tracking ✅ REQUIRED
│   ├── feature-001-folder-structure.md
│   ├── feature-002-naming-conventions.md
│   ├── feature-003-hierarchy-fixes.md
│   └── feature-004-continuation-prompts.md
│
├── phases/                             # Phase documents ✅ REQUIRED
│   ├── master-plan.md                  # Main plan document
│   ├── phase-0-planning.md
│   ├── phase-1-implementation.md
│   ├── phase-2-testing.md
│   └── phase-3-documentation.md
│
├── reports/                            # Progress reports
│   ├── weekly-progress-2026-01-06.md
│   └── milestone-reports/
│
└── tracking/                           # State tracking
    ├── progress-tracker.json           # Automated progress
    ├── snowball.md                     # Epic snowball
    ├── milestones.md                   # Milestone tracking
    └── CONTINUATION-PROMPT.md          # Resume instructions
```

---

## 🛠️ Fixes Required

### Fix 1: Remove Scripts
```bash
# Move to toolkit
mv cleanup-planning-active.sh ../../../../../../cortex-toolkit/cleanup/
mv cleanup-epic-structure.sh ../../../../../../cortex-toolkit/cleanup/
```

### Fix 2: Relocate Markdown Files
```bash
# Move to proper locations
mv A19-cortex-50-remedi-with.md phases/master-plan.md
mv CORTEX5-SNOWBALL.md tracking/snowball.md
mv PHASE-0.5-COMPLETE.md tracking/milestones.md
mv STRUCTURE-REVIEW.md reports/structure-review-2026-01-06.md
rm README.md  # Not needed (plan-viewer.html replaces it)
```

### Fix 3: Create plan-viewer.html
```bash
# Re-run Planning Orchestrator to generate
# OR manually create from template
```

### Fix 4: Create Missing Folders
```bash
mkdir -p phases/
mkdir -p features/
```

### Fix 5: Populate Required Files
```bash
# Create minimal required files
touch phases/master-plan.md
touch features/.gitkeep
touch tracking/progress-tracker.json
touch tracking/CONTINUATION-PROMPT.md
```

---

## 📋 Planning System v5 Standards (Corrected)

| Standard | Current | Required | Status |
|----------|---------|----------|--------|
| **Root Files** | 5+ .md files | ONLY plan-viewer.html | 🔴 Non-compliant |
| **Scripts** | 2 .sh files | 0 (toolkit-managed) | 🔴 Non-compliant |
| **Folder Count** | 5 | 7 (add phases/, features/) | 🔴 Non-compliant |
| **Master Plan** | Root: A19-*.md | phases/master-plan.md | 🔴 Non-compliant |
| **Plan Viewer** | Missing | Required | 🔴 Non-compliant |

---

## 🎯 Cleanup Strategy

### Phase 1: Archive Current Non-Compliant Files
```bash
ARCHIVE_DIR="archives/pre-compliance-cleanup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

# Archive scripts
mv *.sh "$ARCHIVE_DIR/"

# Archive root markdown files
mv *.md "$ARCHIVE_DIR/"
```

### Phase 2: Create Correct Structure
```bash
# Create missing folders
mkdir -p phases/
mkdir -p features/

# Restore files to correct locations
mv "$ARCHIVE_DIR/A19-cortex-50-remedi-with.md" phases/master-plan.md
mv "$ARCHIVE_DIR/CORTEX5-SNOWBALL.md" tracking/snowball.md
mv "$ARCHIVE_DIR/PHASE-0.5-COMPLETE.md" tracking/milestones.md
mv "$ARCHIVE_DIR/STRUCTURE-REVIEW.md" reports/structure-review-2026-01-06.md
```

### Phase 3: Generate plan-viewer.html
```bash
# Run plan viewer generator
python3 -m cortex_toolkit.plan_viewer_generator \
  --plan-path "cortex-brain/documents/planning/active/cortex5-enhancement-epic" \
  --output "plan-viewer.html"
```

---

## ✅ Success Criteria

After cleanup:
- [ ] ONLY `plan-viewer.html` in root
- [ ] NO `*.sh` or `*.py` files in plan folder
- [ ] 7 standard folders present (analysis/, artifacts/, context/, features/, phases/, reports/, tracking/)
- [ ] Master plan at `phases/master-plan.md`
- [ ] Tracking docs in `tracking/`
- [ ] Reports in `reports/`
- [ ] NO `README.md` (plan-viewer.html replaces it)

---

## 📝 Prevention Mechanisms

1. **Planning Orchestrator v5 Validation**
   - Pre-commit hook: Validate plan structure
   - Reject plans without plan-viewer.html
   - Reject plans with root .md files (except plan-viewer.html)
   - Reject plans with scripts in folder

2. **Governance Rules**
   - Update `cortex-brain/brain-protection-rules.yaml`
   - Add PLAN_FILE_ORGANIZATION rule
   - Add PLAN_VIEWER_REQUIRED rule
   - Add SCRIPT_TOOLKIT_ONLY rule

3. **Documentation**
   - Update Planning System v5 docs
   - Add structure examples
   - Add validation rules

---

**Next Action:** Execute cleanup script to fix current epic structure
