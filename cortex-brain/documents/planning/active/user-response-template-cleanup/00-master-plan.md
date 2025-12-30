# 🧠 CORTEX User Response Template Cleanup Plan

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Created:** 2025-12-30  
**Status:** 🔄 IN PROGRESS

---

## 📊 Visual Progress Tracker

**Overall Progress:** `██░░░░░░░░░░░░░░░░░░` **10%** 🔄 Planning Phase

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - Discovery & Audit | `██████████` | 100% ✅ Complete |
| Phase 2 - Delete Obsolete Templates | `░░░░░░░░░░` | 0% ⏳ Pending |
| Phase 3 - Consolidate Duplicates | `░░░░░░░░░░` | 0% ⏳ Pending |
| Phase 4 - Create Missing Templates | `░░░░░░░░░░` | 0% ⏳ Pending |
| Phase 5 - Update Routing Rules | `░░░░░░░░░░` | 0% ⏳ Pending |
| Phase 6 - Wire Maintenance Prompt | `░░░░░░░░░░` | 0% ⏳ Pending |

---

## 🎯 Executive Summary

**Problem:** The CORTEX response template system has accumulated significant technical debt:
- Obsolete 5-part-standard.yaml referenced by 27 templates (file doesn't exist)
- Duplicated routing/component files across two locations
- Missing introduction templates that are defined in routing rules but don't exist
- Inconsistent architecture between v4 (adaptive) and legacy (5-part) formats
- No enforcement in maintenance prompt to validate template wiring

**Solution:** 6-phase cleanup to consolidate, fix, and enforce response template integrity.

**Impact:**
- 🗑️ Delete ~30 obsolete file references
- 🔧 Consolidate 6 duplicated files → 3 canonical locations
- ✨ Create 4 missing introduction templates
- 🔌 Wire maintenance prompt to validate templates

---

## 🔍 Phase 1: Discovery & Audit (COMPLETE)

### 1.1 Critical Issues Found

| Issue | Count | Severity | Location |
|-------|-------|----------|----------|
| Templates referencing non-existent `5-part-standard.yaml` | 27 | 🔴 CRITICAL | `cortex-brain/response-templates/operations/**/*.yaml` |
| Duplicated routing rules files | 2 | 🟠 HIGH | `cortex-brain/` vs `cortex-brain/response-templates/` |
| Duplicated profile variants files | 2 | 🟠 HIGH | Same |
| Duplicated base components files | 2 | 🟠 HIGH | Same |
| Missing introduction templates (defined in routing, not implemented) | 4 | 🔴 CRITICAL | `introduction_professional/leadership/product/engineering` |
| Missing business_value template (defined in routing) | 1 | 🟠 HIGH | Only exists in `response-templates-v4.yaml` |
| Inconsistent schema versions | Multiple | 🟡 MEDIUM | v3.0, v3.2, v3.3, v4.0 |

### 1.2 File Inventory

**Duplicated Files (PICK ONE):**
```
cortex-brain/response-routing-rules.yaml (v3.3, 369 lines)
cortex-brain/response-templates/response-routing-rules.yaml (v3.0, 459 lines)
→ KEEP: response-templates/ version (more comprehensive)

cortex-brain/response-profile-variants.yaml
cortex-brain/response-templates/response-profile-variants.yaml
→ KEEP: response-templates/ version

cortex-brain/response-base-components.yaml
cortex-brain/response-templates/response-base-components.yaml
→ KEEP: response-templates/ version (base-components.yaml is similar)
```

**Obsolete References (DELETE):**
```
27 files reference: core/base-templates/5-part-standard.yaml (DOES NOT EXIST)
The only file in core/base-templates/ is: tech-aware.yaml
```

**Missing Templates (CREATE):**
```
introduction_professional - Defined in routing, doesn't exist
introduction_leadership - Defined in routing, doesn't exist
introduction_product - Defined in routing, doesn't exist
introduction_engineering - Defined in routing, doesn't exist
business_value - Only in response-templates-v4.yaml (not in operations folder)
security_posture - Defined in routing, doesn't exist
```

### 1.3 Architecture Decision

**Current State:**
- `response-templates-v4.yaml` = New adaptive system (INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE)
- `operations/**/*.yaml` = Legacy 5-part system (orphaned references)
- Two parallel architectures causing confusion

**Target State:**
- ALL templates use v4 adaptive format
- Single source of truth in `response-templates-v4.yaml`
- Operations YAML files become thin wrappers that reference v4 components
- OR delete operations YAML files entirely and use v4 only

**Recommendation:** Migrate to v4-only architecture:
1. Delete all `inherits_from: core/base-templates/5-part-standard.yaml` references
2. Operations YAML can be simplified to just triggers + orchestrator references
3. Actual template content lives in `response-templates-v4.yaml`

---

## 🗑️ Phase 2: Delete Obsolete Templates

### 2.1 Remove 5-Part References

**Action:** Remove all `inherits_from: core/base-templates/5-part-standard.yaml` lines from:

| File | Lines to Remove |
|------|-----------------|
| `operations/general/general.yaml` | Lines 4, 51, 98, 145, 185, 228, 266, 367, 482, 622, 745, 795, 843, 968, 1070, 1184, 1245 |
| `operations/admin/admin.yaml` | Line 4 |
| `operations/diagram/diagram.yaml` | Line 4 |
| `operations/feedback/feedback.yaml` | Line 4 |
| `operations/help/help.yaml` | Line 4 |
| `operations/onboarding/onboarding.yaml` | Line 4 |
| `orchestrators/git-checkpoint/git-checkpoint.yaml` | Line 4 |
| `orchestrators/planning/planning.yaml` | Line 4 |
| `specialized/ado-integration/ado-integration.yaml` | Line 4 |
| `specialized/dashboard/dashboard.yaml` | Line 4 |
| `specialized/threat-modeling/threat-modeling.yaml` | Line 4 |

### 2.2 Delete Duplicated Root-Level Files

**Action:** Delete these files from `cortex-brain/` (keep `response-templates/` versions):

```
DELETE: cortex-brain/response-routing-rules.yaml
DELETE: cortex-brain/response-profile-variants.yaml
DELETE: cortex-brain/response-base-components.yaml
```

### 2.3 Delete Empty Base Template Directory

```
DELETE: cortex-brain/response-templates/core/base-templates/5-part-standard.yaml (if exists)
KEEP: cortex-brain/response-templates/core/base-templates/tech-aware.yaml
```

---

## 🔧 Phase 3: Consolidate Duplicates

### 3.1 Merge Routing Rules

**From:** `cortex-brain/response-templates/response-routing-rules.yaml` (459 lines, v3.0)
**Into:** Update to v4.0 format matching `response-templates-v4.yaml` architecture

**Key Changes:**
1. Update schema_version to 4.0
2. Add introduction/business_value templates (from v4.yaml)
3. Remove references to non-existent templates
4. Align with CORTEX.prompt.md tier system (INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE)

### 3.2 Single Source of Truth

**Canonical Locations:**
```
cortex-brain/response-templates-v4.yaml         # Master template definitions
cortex-brain/response-templates/routing.yaml    # Intent → Template mapping
cortex-brain/response-templates/profiles.yaml   # User profile variants
cortex-brain/response-templates/components.yaml # Reusable components
```

---

## ✨ Phase 4: Create Missing Templates

### 4.1 Introduction Templates

Create in `cortex-brain/response-templates/operations/introduction/introduction.yaml`:

```yaml
category: operations/introduction
templates:
  introduction_professional:
    # For Software Engineers - comprehensive technical overview
  introduction_product:
    # For Product Owners - delivery and planning focus
  introduction_leadership:
    # For Leadership - ROI and business value focus
  introduction_engineering:
    # Alias for introduction_professional
```

### 4.2 Business Value Template

Already exists in `response-templates-v4.yaml` - ensure routing points to it.

### 4.3 Security Posture Template

Create in `cortex-brain/response-templates/operations/security/security.yaml`:

```yaml
category: operations/security
templates:
  security_posture:
    # Security overview for concerned stakeholders
```

---

## 🔌 Phase 5: Update Routing Rules

### 5.1 Fix Intent Detection

Update `cortex-brain/response-templates/response-routing-rules.yaml`:

1. Ensure introduction templates point to real template definitions
2. Add `template_file` field to specify actual YAML location
3. Validate all template references exist

### 5.2 Add Template Validation

Add to routing rules:
```yaml
validation:
  on_load:
    - check_template_exists: true
    - check_inherits_from_exists: true
    - warn_on_missing: true
```

---

## 📝 Phase 6: Wire Maintenance Prompt

### 6.1 Add Rule 8: Response Template Integrity

Add to `cortex-maintenance.prompt.md`:

```markdown
### Rule 8: Response Template Integrity (NEW - December 30, 2025)

**Phase 11: Response Template Validation**

**ALL response template references MUST resolve to existing files.**

**Validation Checks:**
1. Every `inherits_from` reference points to existing file
2. Every `template:` in routing rules points to defined template
3. No orphaned template definitions
4. Schema versions are consistent (v4.0)
5. Introduction templates exist for all audiences

**❌ FORBIDDEN:**
- `inherits_from: core/base-templates/5-part-standard.yaml` (file doesn't exist)
- Template references to undefined templates
- Duplicate routing/component files

**✅ REQUIRED:**
- Single source of truth: `response-templates-v4.yaml`
- All routing in: `response-templates/response-routing-rules.yaml`
- Validated on every maintenance run

**Auto-Repair Actions:**
- Remove orphaned `inherits_from` references
- Delete duplicate files in `cortex-brain/` root
- Generate missing introduction templates
```

### 6.2 Add Phase 11 to Pipeline

Update pipeline in maintenance prompt:
```
Phase 11: TEMPLATE VALIDATION
  ├─ Scan all template YAML files
  ├─ Validate `inherits_from` references
  ├─ Check routing → template mappings
  ├─ Delete orphaned references
  └─ Report template health score
```

---

## 📋 Implementation Checklist

### Phase 2 Tasks
- [ ] Remove 27 `inherits_from: core/base-templates/5-part-standard.yaml` lines
- [ ] Delete `cortex-brain/response-routing-rules.yaml`
- [ ] Delete `cortex-brain/response-profile-variants.yaml`
- [ ] Delete `cortex-brain/response-base-components.yaml`

### Phase 3 Tasks
- [ ] Update `response-templates/response-routing-rules.yaml` to v4.0
- [ ] Merge any unique content from deleted files

### Phase 4 Tasks
- [ ] Create `operations/introduction/introduction.yaml`
- [ ] Create `operations/security/security.yaml`
- [ ] Verify `response-templates-v4.yaml` has business_value

### Phase 5 Tasks
- [ ] Add template_file references to routing rules
- [ ] Add validation section to routing rules

### Phase 6 Tasks
- [ ] Add Rule 8 to `cortex-maintenance.prompt.md`
- [ ] Add Phase 11 to pipeline
- [ ] Test maintenance runs template validation

---

## 🎯 Success Criteria

| Metric | Before | After |
|--------|--------|-------|
| Orphaned `inherits_from` references | 27 | 0 |
| Duplicate routing files | 2 | 1 |
| Missing introduction templates | 4 | 0 |
| Template validation in maintenance | ❌ | ✅ |
| Schema version consistency | Mixed | v4.0 |

---

## 📚 Artifacts to Create

| Artifact | Location |
|----------|----------|
| Discovery report | `context/discovery-report.md` |
| Deletion manifest | `artifacts/deletion-manifest.yaml` |
| New introduction templates | `artifacts/introduction-templates.yaml` |
| Maintenance patch | `artifacts/maintenance-prompt-patch.md` |
| Progress tracker | `tracking/progress-tracker.json` |

---

**Next Step:** Execute Phase 2 - Delete Obsolete Templates
