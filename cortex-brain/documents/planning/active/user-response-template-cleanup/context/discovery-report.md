# Discovery Report - User Response Template Cleanup

**Date:** 2025-12-30  
**Author:** CORTEX Planning System

---

## 1. Orphaned `inherits_from` References (27 total)

### Files with non-existent references to `core/base-templates/5-part-standard.yaml`:

| File | Line Numbers |
|------|--------------|
| `operations/general/general.yaml` | 4, 51, 98, 145, 185, 228, 266, 367, 482, 622, 745, 795, 843, 968, 1070, 1184, 1245 |
| `operations/admin/admin.yaml` | 4 |
| `operations/diagram/diagram.yaml` | 4 |
| `operations/feedback/feedback.yaml` | 4 |
| `operations/help/help.yaml` | 4 |
| `operations/onboarding/onboarding.yaml` | 4 |
| `orchestrators/git-checkpoint/git-checkpoint.yaml` | 4 |
| `orchestrators/planning/planning.yaml` | 4 |
| `specialized/ado-integration/ado-integration.yaml` | 4 |
| `specialized/dashboard/dashboard.yaml` | 4 |
| `specialized/threat-modeling/threat-modeling.yaml` | 4 |

**Root Cause:** The 5-part-standard.yaml file was deleted but references remain.

---

## 2. Duplicate Files (6 files → 3 locations)

| File | Location 1 (DELETE) | Location 2 (KEEP) |
|------|---------------------|-------------------|
| `response-routing-rules.yaml` | `cortex-brain/` (v3.3) | `cortex-brain/response-templates/` (v3.0) |
| `response-profile-variants.yaml` | `cortex-brain/` | `cortex-brain/response-templates/` |
| `response-base-components.yaml` | `cortex-brain/` | `cortex-brain/response-templates/` |

**Recommendation:** Keep `response-templates/` versions as canonical.

---

## 3. Missing Templates (5 total)

Templates defined in routing rules but not implemented:

| Template Name | Expected Location | Status |
|---------------|-------------------|--------|
| `introduction_professional` | `operations/introduction/` | ❌ MISSING |
| `introduction_leadership` | `operations/introduction/` | ❌ MISSING |
| `introduction_product` | `operations/introduction/` | ❌ MISSING |
| `introduction_engineering` | `operations/introduction/` | ❌ MISSING |
| `security_posture` | `operations/security/` | ❌ MISSING |

**Note:** `business_value` exists in `response-templates-v4.yaml` but not in operations folder.

---

## 4. Schema Version Inconsistency

| File | Current Version | Target Version |
|------|-----------------|----------------|
| `response-templates-v4.yaml` | 4.0.2 | 4.0.2 ✅ |
| `response-routing-rules.yaml` (templates/) | 3.0 | 4.0 |
| `response-routing-rules.yaml` (root) | 3.3 | DELETE |
| `base-components.yaml` | 3.2 | 4.0 |
| `response-base-components.yaml` | varies | DELETE |

---

## 5. Architecture Analysis

### Current State (Fragmented)
```
cortex-brain/
├── response-templates-v4.yaml      # New v4 system (good)
├── response-routing-rules.yaml     # Duplicate (delete)
├── response-profile-variants.yaml  # Duplicate (delete)
├── response-base-components.yaml   # Duplicate (delete)
└── response-templates/
    ├── response-routing-rules.yaml # v3 system (upgrade to v4)
    ├── response-profile-variants.yaml
    ├── response-base-components.yaml
    ├── base-components.yaml        # Possible duplicate
    └── operations/                 # 27 orphaned references
```

### Target State (Consolidated)
```
cortex-brain/
├── response-templates-v4.yaml      # Master template definitions
└── response-templates/
    ├── routing.yaml                # Intent → Template (v4)
    ├── profiles.yaml               # User variants
    ├── components.yaml             # Reusable parts
    └── operations/                 # No inherits_from, just triggers
        └── introduction/           # NEW: persona-based intros
```

---

## 6. CORTEX.prompt.md Alignment

The prompt defines 4-tier adaptive format:
- INSTANT (<50 tokens)
- FOCUSED (50-200 tokens)
- STRUCTURED (200-600 tokens)
- COMPREHENSIVE (600+ tokens)

`response-templates-v4.yaml` implements this correctly.
Legacy templates use 5-part structure (obsolete).

**Action:** Align all templates to v4 tier system.

---

## 7. Impact Assessment

| Category | Impact | Priority |
|----------|--------|----------|
| Templates can't render (missing file) | 🔴 CRITICAL | P0 |
| Duplicate files cause confusion | 🟠 HIGH | P1 |
| Missing introduction templates | 🟠 HIGH | P1 |
| Schema inconsistency | 🟡 MEDIUM | P2 |
| Documentation drift | 🟢 LOW | P3 |

---

## 8. Recommended Actions

1. **Immediate (P0):** Remove all 27 `inherits_from` references
2. **High (P1):** Delete 3 duplicate root-level files
3. **High (P1):** Create 5 missing templates (introduction + security)
4. **Medium (P2):** Update routing rules to v4.0 schema
5. **Low (P3):** Update maintenance prompt with validation rule
