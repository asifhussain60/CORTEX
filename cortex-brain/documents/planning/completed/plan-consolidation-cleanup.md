# 🧹 Active Plans Consolidation & Cleanup - CORTEX v5

**Created:** January 5, 2026  
**Author:** Asif Hussain  
**Priority:** P0_CRITICAL  
**Status:** READY_TO_EXECUTE

---

## 🎯 Problem Statement

**Current State:** 19 fragmented plans in `cortex-brain/documents/planning/active/`  
**Expected State:** 3 cohesive active plans only

**Issue:** Planning Orchestrator v5 creates fragmented, UUID-based plans instead of proper hierarchical structure.

---

## 📊 Current Active Plans Inventory

### ✅ KEEP - Valid Active Plans (3)

| Plan | Location | Type | Status |
|------|----------|------|--------|
| **Glassmorphism Alignment** | `html-glassmorphism-alignment/` | Feature | Active |
| **Enterprise Audit Logger** | `enterprise-python-audit-logger-with-self-healing/` | Feature | Active |
| **CORTEX5 Remediation Epic** | `C50-cortex-v5-remediation/` + `c150-remediation-plan/` | Epic (MERGE REQUIRED) | Active |

### ❌ DELETE - Fragmented/Test Plans (16)

| Plan | Type | Reason |
|------|------|--------|
| `plan-07e9b3b7-*` | UUID Plan | Fragmented - no context |
| `plan-135c89d1-*` | UUID Plan | Fragmented - no context |
| `plan-749e72a9-*` | UUID Plan | Fragmented - no context |
| `plan-a1e78fe9-*` | UUID Plan | Fragmented - no context |
| `plan-b86069d7-*` | UUID Plan | Fragmented - no context |
| `a00-test-yaml-genera/` | Test Plan | Test artifact |
| `a01-test-yaml-genera/` | Test Plan | Test artifact |
| `a19-create-epic-plan-for/` | Test Plan | Test artifact |
| `create-epic-plan-for-user-auth/` | Duplicate | 3 versions of same plan |
| `create-epic-plan-for-user-auth-system/` | Duplicate | 3 versions of same plan |
| `create-epic-plan-for-user-authentication-system/` | Duplicate | 3 versions of same plan |
| `poc-python-execution/` | POC | Proof of concept - completed |
| `test/` | Test Folder | Test artifact |
| `ado-v2-1-tasklist-integration/` | Work-in-Progress | Move to ADO-specific location |
| `backups/` | Backup Folder | Archive, not active plan |

---

## 🔄 Consolidation Strategy

### Phase 1: Merge CORTEX5 Remediation Plans

**Source Plans:**
- `c150-remediation-plan/` (YAML-based, 29 phases, 21% complete)
- `C50-cortex-v5-remediation/` (Epic-level, 18 child plans)

**Target Structure:**
```
cortex-brain/documents/planning/active/cortex-v5-remediation-epic/
├── 00-cortex-v5-remediation-epic.yaml (merged master plan)
├── README.md (epic overview)
├── c50-epic-manifest.yaml (child plan registry)
├── plan-viewer.html (unified viewer)
├── launch_plan_viewer.py
├── phases/
│   ├── C50-00A/ (Planning System v5 Stabilization)
│   ├── C50-00B/ (Master Orchestrator Hardening)
│   ├── C50-00C/ (TDD v2 Enhancement)
│   ├── C50-00D/ (Brain Tier Integration)
│   ├── C50-01/ through C50-18/ (feature plans)
│   └── c150-remediation/ (HTML alignment gaps)
├── analysis/
├── artifacts/
├── context/
├── reports/
└── tracking/
    ├── progress-tracker.json
    └── epic-status.json
```

**Merge Logic:**
1. **Master Plan:** Combine `00-c150-remediation-plan.yaml` + `00-cortex-v5-remediation.md` → `00-cortex-v5-remediation-epic.yaml`
2. **Hierarchy:** C50 Epic → C150 as Phase (not separate plan)
3. **Tracking:** Merge progress trackers
4. **Viewer:** Unified plan-viewer.html for epic + child plans

### Phase 2: Move Work-in-Progress Plans

**ADO v2.1 TaskList Integration:**
- **From:** `cortex-brain/documents/planning/active/ado-v2-1-tasklist-integration/`
- **To:** `cortex-brain/documents/planning/ado/` (domain-specific location)

### Phase 3: Archive & Delete

**Archive to `cortex-brain/archives/planning/2026-01-05-consolidation/`:**
- All UUID-based plans (for forensic analysis)
- Test plans (a00, a01, a19)
- POC plans
- Duplicate user-auth plans

**Permanent Delete:**
- `backups/` folder (already backed up externally)

---

## 🛠️ Execution Commands

### Step 1: Create Archive Location
```bash
mkdir -p cortex-brain/archives/planning/2026-01-05-consolidation/{uuid-plans,test-plans,duplicates}
```

### Step 2: Archive Fragmented Plans
```bash
# UUID plans
mv cortex-brain/documents/planning/active/plan-* cortex-brain/archives/planning/2026-01-05-consolidation/uuid-plans/

# Test plans
mv cortex-brain/documents/planning/active/a00-test-yaml-genera cortex-brain/archives/planning/2026-01-05-consolidation/test-plans/
mv cortex-brain/documents/planning/active/a01-test-yaml-genera cortex-brain/archives/planning/2026-01-05-consolidation/test-plans/
mv cortex-brain/documents/planning/active/a19-create-epic-plan-for cortex-brain/archives/planning/2026-01-05-consolidation/test-plans/
mv cortex-brain/documents/planning/active/poc-python-execution cortex-brain/archives/planning/2026-01-05-consolidation/test-plans/
mv cortex-brain/documents/planning/active/test cortex-brain/archives/planning/2026-01-05-consolidation/test-plans/

# Duplicates
mv cortex-brain/documents/planning/active/create-epic-plan-for-* cortex-brain/archives/planning/2026-01-05-consolidation/duplicates/
```

### Step 3: Move ADO Plan to Domain Location
```bash
mkdir -p cortex-brain/documents/planning/ado/
mv cortex-brain/documents/planning/active/ado-v2-1-tasklist-integration cortex-brain/documents/planning/ado/
```

### Step 4: Merge CORTEX5 Remediation Plans
```bash
# Create unified epic folder
mkdir -p cortex-brain/documents/planning/active/cortex-v5-remediation-epic/phases/c150-remediation

# Copy C50 epic structure
cp -r cortex-brain/documents/planning/active/C50-cortex-v5-remediation/* cortex-brain/documents/planning/active/cortex-v5-remediation-epic/

# Move C150 as child phase
cp -r cortex-brain/documents/planning/active/c150-remediation-plan/* cortex-brain/documents/planning/active/cortex-v5-remediation-epic/phases/c150-remediation/

# Archive originals
mv cortex-brain/documents/planning/active/C50-cortex-v5-remediation cortex-brain/archives/planning/2026-01-05-consolidation/pre-merge/
mv cortex-brain/documents/planning/active/c150-remediation-plan cortex-brain/archives/planning/2026-01-05-consolidation/pre-merge/
```

### Step 5: Delete Backups Folder
```bash
rm -rf cortex-brain/documents/planning/active/backups
```

---

## ✅ Validation Checklist

After execution, verify:

- [ ] Only 3 folders in `cortex-brain/documents/planning/active/`:
  - `html-glassmorphism-alignment/`
  - `enterprise-python-audit-logger-with-self-healing/`
  - `cortex-v5-remediation-epic/`
- [ ] Unified epic structure with C150 as child phase
- [ ] All archived plans in `cortex-brain/archives/planning/2026-01-05-consolidation/`
- [ ] ADO plan in `cortex-brain/documents/planning/ado/`
- [ ] Plan viewers still functional
- [ ] Progress tracking preserved

---

## 🐛 Root Cause Analysis: Planning Orchestrator v5

### Issue: Fragmented Plan Creation

**Symptoms:**
- UUID-based plan folders (`plan-07e9b3b7-*`)
- No proper hierarchy
- Duplicate plans for same feature

**Root Causes:**

1. **Missing Plan ID Extraction:**
   - Planning v5 generates UUID when feature name not parsed correctly
   - Should derive plan-id from feature name (e.g., "user authentication" → "user-authentication")

2. **No Duplicate Detection:**
   - Doesn't check if plan already exists before creating
   - No HOLISTIC_DISCOVERY before plan creation

3. **No Parent-Child Linking:**
   - Creates flat plans instead of hierarchical epic → feature → sub-plan structure

4. **Broken Plan Naming Convention:**
   - Should follow: `{plan_type}-{sanitized_feature_name}`
   - Actually creates: `plan-{uuid}`

### Required Fixes (Future):

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`

```python
# ADD: Plan ID generation from feature name
def generate_plan_id(feature_name: str, plan_type: str) -> str:
    """Generate human-readable plan ID from feature name."""
    sanitized = feature_name.lower().replace(" ", "-")[:50]
    return f"{plan_type}-{sanitized}"

# ADD: Duplicate detection
def check_existing_plan(feature_name: str) -> Optional[str]:
    """Check if plan already exists for feature."""
    # Search cortex-brain/documents/planning/active/
    # Return existing plan_id if found

# ADD: Hierarchical linking
def link_to_parent_epic(plan_id: str, parent_epic_id: str):
    """Register plan as child of parent epic."""
    # Update parent epic's c50-epic-manifest.yaml
```

**Priority:** P1 (after consolidation complete)

---

## 📈 Success Metrics

**Before:**
- 19 folders in active/
- 5 UUID-based plans
- 3 duplicate user-auth plans
- 2 separate CORTEX5 remediation plans
- No clear hierarchy

**After:**
- 3 folders in active/
- 0 UUID-based plans
- 1 unified CORTEX5 epic with proper hierarchy
- Clear parent-child structure
- Planning Orchestrator improvements documented

---

## 🚀 Next Steps

1. **Execute consolidation** (15 minutes)
2. **Validate structure** (5 minutes)
3. **Update plan viewers** (10 minutes)
4. **File Planning v5 bug** (add to CORTEX5 remediation epic as new phase)
5. **Resume work on active plans** (glassmorphism, audit logger, remediation)

---

**Estimated Time:** 30 minutes  
**Risk:** LOW (all plans archived, not deleted)  
**Blocker:** None - ready to execute
