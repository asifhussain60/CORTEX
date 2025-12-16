# Platform.Classic RA-API-Specs Reorganization Plan

**Date:** December 15, 2025  
**Purpose:** Move CORTEX tools to CORTEX repo, keep Platform.Classic outputs clean  
**Status:** Planning Complete

---

## 🎯 Reorganization Strategy

### Problem
- CORTEX tools mixed with Platform.Classic outputs
- Validation framework in wrong repository
- Templates and guides need proper organization
- Generator v1.0 (old) coexists with generator v3.0 (new)

### Solution
**CORTEX Repository:**
- All reusable tools (generators, validators)
- All templates and guides
- All framework documentation
- All process workflows

**Platform.Classic Repository:**
- Only generated outputs (business-spec.md, openapi.yaml, etc.)
- API-specific specifications
- Clean, simple structure

---

## 📋 File Classification

### MOVE TO CORTEX (Tools, Templates, Frameworks)

**Root Documentation:**
1. `FRAMEWORK-COMPLETION.md` → `cortex-brain/documents/reports/`
2. `MIGRATION-SUMMARY.md` → `cortex-brain/documents/reports/`
3. `TOOLING-INDEX.md` → `cortex-brain/documents/implementation-guides/`

**Guidelines (All):**
4. `guidelines/ra-domain-standards.md` → `cortex-brain/documents/implementation-guides/`
5. `guidelines/architecture/architecture-patterns.md` → `cortex-brain/documents/implementation-guides/`
6. `guidelines/architecture/clean-architecture-layers.md` → `cortex-brain/documents/implementation-guides/`
7. `guidelines/diagrams/README.md` → `cortex-brain/documents/implementation-guides/`

**Process Workflows (All):**
8. `process/specification-generation-workflow.md` → `cortex-brain/documents/implementation-guides/`
9. `process/agent-configs/legacy-specification-generator.md` → `cortex-brain/documents/implementation-guides/`
10. `process/agent-configs/modern-architecture-designer.md` → `cortex-brain/documents/implementation-guides/`

**Tools (All - These are CORTEX capabilities):**
11. `tools/ast_completeness_checker.py` → `src/operations/modules/validators/`
12. `tools/data_flow_validator.py` → `src/operations/modules/validators/`
13. `tools/domain_boundary_checker.py` → `src/operations/modules/validators/`
14. `tools/project_reference_validator.py` → `src/operations/modules/validators/`
15. `tools/specification_generator.py` → **DELETE** (replaced by v3.0)
16. `tools/traceability_calculator.py` → `src/operations/modules/validators/`

**Specification Templates:**
17. `specifications/BUSINESS-SPEC-TEMPLATE.md` → `cortex-brain/documents/templates/`
18. `specifications/VALIDATION-TEMPLATE.md` → `cortex-brain/documents/templates/`
19. `specifications/VALIDATION-QUICK-START.md` → `cortex-brain/documents/implementation-guides/`

**Specification Reports (CORTEX artifacts):**
20. `specifications/ENHANCEMENT-COMPLETION-REPORT.md` → `cortex-brain/documents/reports/`
21. `specifications/GENERATION-SUMMARY.md` → `cortex-brain/documents/reports/`
22. `specifications/USER-STORY-ENHANCEMENT-REPORT.md` → `cortex-brain/documents/reports/`

---

### KEEP IN PLATFORM.CLASSIC (Generated Outputs)

**API Specifications (Generated outputs):**
- `specifications/updater-createrafundinginvoices/business-spec.md` ✅
- `specifications/updater-createrafundinginvoices/openapi.yaml` ✅
- `specifications/updater-createrafundinginvoices/openapi.json` ✅
- `specifications/updater-createrafundinginvoices/traceability-matrix.md` ✅
- `specifications/xgeneratefundinginvoice/business-spec.md` ✅
- `specifications/xgeneratefundinginvoice/openapi.yaml` ✅
- `specifications/xgeneratefundinginvoice/openapi.json` ✅
- `specifications/xgeneratefundinginvoice/traceability-matrix.md` ✅

**Pilot Planning (Platform.Classic specific):**
- `specifications/xupdatefundingbatch/pilot-plan.md` ✅
- `specifications/xupdatefundingbatch/VALIDATION-CHECKLIST.md` ✅
- `specifications/xupdatefundingbatch/validate.py` → **MOVE TO CORTEX** (tool)

---

### DELETE (Obsolete/Duplicate)

**Old Generator (Replaced by v3.0):**
- `tools/specification_generator.py` - Replaced by `src/operations/modules/generators/legacy_spec_generator.py` v3.0

**Redundant README:**
- `specifications/README.md` - Content integrated into Platform.Classic README

---

## 📂 New Structure

### CORTEX Repository

```
CORTEX/
├── src/
│   └── operations/
│       └── modules/
│           ├── generators/
│           │   └── legacy_spec_generator.py (v3.0 - EXISTS)
│           └── validators/
│               ├── ast_completeness_checker.py (NEW)
│               ├── data_flow_validator.py (NEW)
│               ├── domain_boundary_checker.py (NEW)
│               ├── project_reference_validator.py (NEW)
│               └── traceability_calculator.py (NEW)
│
└── cortex-brain/
    └── documents/
        ├── templates/
        │   ├── business-spec-template.md (NEW)
        │   └── validation-template.md (NEW)
        │
        ├── implementation-guides/
        │   ├── openapi-generation-guide.md (EXISTS)
        │   ├── cortex-lens-usage-guide.md (EXISTS)
        │   ├── ra-domain-standards.md (NEW)
        │   ├── architecture-patterns.md (NEW)
        │   ├── clean-architecture-layers.md (NEW)
        │   ├── visual-diagram-guide.md (NEW)
        │   ├── specification-generation-workflow.md (NEW)
        │   ├── legacy-specification-generator-config.md (NEW)
        │   ├── modern-architecture-designer-config.md (NEW)
        │   ├── validation-quick-start.md (NEW)
        │   └── tooling-index.md (NEW)
        │
        └── reports/
            ├── legacy-spec-generator-v3-completion.md (EXISTS)
            ├── framework-completion.md (NEW)
            ├── migration-summary.md (NEW)
            ├── enhancement-completion-report.md (NEW)
            ├── generation-summary.md (NEW)
            └── user-story-enhancement-report.md (NEW)
```

---

### Platform.Classic Repository

```
Platform.Classic/
└── cortex/
    └── ra-api-specs/
        ├── README.md (UPDATED - simplified)
        │
        └── specifications/
            ├── updater-createrafundinginvoices/
            │   ├── business-spec.md
            │   ├── openapi.yaml
            │   ├── openapi.json
            │   └── traceability-matrix.md
            │
            ├── xgeneratefundinginvoice/
            │   ├── business-spec.md
            │   ├── openapi.yaml
            │   ├── openapi.json
            │   └── traceability-matrix.md
            │
            └── xupdatefundingbatch/
                ├── pilot-plan.md
                └── VALIDATION-CHECKLIST.md
```

---

## 🔄 Migration Steps

### Phase 1: Move Validators to CORTEX (5 files)
```powershell
New-Item -ItemType Directory -Path "C:\PROJECTS\CORTEX\src\operations\modules\validators" -Force
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\tools\ast_completeness_checker.py" `
  "C:\PROJECTS\CORTEX\src\operations\modules\validators\"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\tools\data_flow_validator.py" `
  "C:\PROJECTS\CORTEX\src\operations\modules\validators\"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\tools\domain_boundary_checker.py" `
  "C:\PROJECTS\CORTEX\src\operations\modules\validators\"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\tools\project_reference_validator.py" `
  "C:\PROJECTS\CORTEX\src\operations\modules\validators\"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\tools\traceability_calculator.py" `
  "C:\PROJECTS\CORTEX\src\operations\modules\validators\"
```

### Phase 2: Move Templates to CORTEX (2 files)
```powershell
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\BUSINESS-SPEC-TEMPLATE.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\templates\business-spec-template.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\VALIDATION-TEMPLATE.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\templates\validation-template.md"
```

### Phase 3: Move Implementation Guides to CORTEX (10 files)
```powershell
# Root guides
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\TOOLING-INDEX.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\implementation-guides\tooling-index.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\VALIDATION-QUICK-START.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\implementation-guides\validation-quick-start.md"

# Guidelines folder
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\guidelines\ra-domain-standards.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\implementation-guides\ra-domain-standards.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\guidelines\architecture\architecture-patterns.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\implementation-guides\architecture-patterns.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\guidelines\architecture\clean-architecture-layers.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\implementation-guides\clean-architecture-layers.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\guidelines\diagrams\README.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\implementation-guides\visual-diagram-standards.md"

# Process folder
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\process\specification-generation-workflow.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\implementation-guides\specification-generation-workflow.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\process\agent-configs\legacy-specification-generator.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\implementation-guides\legacy-specification-generator-config.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\process\agent-configs\modern-architecture-designer.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\implementation-guides\modern-architecture-designer-config.md"
```

### Phase 4: Move Reports to CORTEX (5 files)
```powershell
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\FRAMEWORK-COMPLETION.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\reports\framework-completion.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\MIGRATION-SUMMARY.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\reports\migration-summary.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\ENHANCEMENT-COMPLETION-REPORT.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\reports\enhancement-completion-report.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\GENERATION-SUMMARY.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\reports\generation-summary.md"
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\USER-STORY-ENHANCEMENT-REPORT.md" `
  "C:\PROJECTS\CORTEX\cortex-brain\documents\reports\user-story-enhancement-report.md"
```

### Phase 5: Move XUpdateFundingBatch Tool to CORTEX (1 file)
```powershell
Move-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\xupdatefundingbatch\validate.py" `
  "C:\PROJECTS\CORTEX\src\operations\modules\validators\validation_suite.py"
```

### Phase 6: Delete Obsolete Files
```powershell
Remove-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\tools\specification_generator.py" -Force
Remove-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\README.md" -Force
```

### Phase 7: Clean Up Empty Directories
```powershell
Remove-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\tools" -Recurse -Force
Remove-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\guidelines" -Recurse -Force
Remove-Item "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\process" -Recurse -Force
```

### Phase 8: Update Platform.Classic README
```powershell
# Create new simplified README
```

---

## 📊 Migration Summary

**Files to Move:** 23 files  
**Files to Delete:** 2 files  
**Directories to Remove:** 3 directories  
**Files to Keep:** 10 files (generated outputs)

**CORTEX Additions:**
- 5 validators
- 2 templates
- 10 implementation guides
- 6 reports

**Platform.Classic Result:**
- Clean specification outputs only
- 3 API specification folders
- No tools or frameworks
- Simple README

---

## ✅ Validation Checklist

After migration:
- [ ] All CORTEX tools in `src/operations/modules/`
- [ ] All templates in `cortex-brain/documents/templates/`
- [ ] All guides in `cortex-brain/documents/implementation-guides/`
- [ ] All reports in `cortex-brain/documents/reports/`
- [ ] Platform.Classic contains only generated outputs
- [ ] No Python files in Platform.Classic ra-api-specs
- [ ] No framework documentation in Platform.Classic
- [ ] Generator v3.0 works with new validator locations
- [ ] README updated in Platform.Classic

---

**Status:** Ready for Execution  
**Estimated Time:** 15 minutes  
**Risk:** Low (all moves, no deletions of generated specs)
