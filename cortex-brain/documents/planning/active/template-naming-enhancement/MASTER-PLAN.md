<!--
████████████████████████████████████████████████████████████████████████████████
█                                                                              █
█   ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                        █
█  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                        █
█  ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                         █
█  ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                         █
█  ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                        █
█   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                        █
█                                                                              █
█  AI-Powered Development Intelligence System                                 █
█  Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX            █
█  Copyright © 2025 Asif Hussain. All rights reserved.                       █
█                                                                              █
████████████████████████████████████████████████████████████████████████████████
-->

# Template Naming Convention Enhancement

**Type:** Tier 2 Documented Plan  
**Status:** 🟡 In Progress  
**Created:** 2025-12-16 12:00 PM  
**Last Updated:** 2025-12-16 12:00 PM  
**Completed:** TBD  
**Version:** 1.0.0

---

## Request Context

**Problem:** Current template naming uses generic prefixes (`00-sub-plan-template.md`, `master-plan-template.md`) that make templates hard to find via global search and blend with numbered actual plans.

**Goal:** Implement distinctive ALL-CAPS naming convention for templates:
- `MASTER-PLAN-TEMPLATE.md` - Instantly searchable, clearly a template
- `SUB-PLAN-TEMPLATE.md` - No confusion with `01-`, `02-` numbered plans
- Update all references across codebase, documentation, and orchestrators

---

## Visual Progress Tracker

```
+==============================================================================+
  CORTEX Plan Progress Tracker
+==============================================================================+

  Overall Progress:  [░░░░░░░░░░░░░░░░░░░░] 0% (0/4 phases complete)

  Total Actual Time:    0 minutes  |  Total Elapsed Time:  0:00
  Senior Dev Estimate:  6-8 hours (0.15-0.20 weeks @ 40h/week baseline)

  Estimation Methodology:
    • Base: 4 hours pure development
    • Testing overhead: x1.30 (TDD, unit/integration tests)
    • Documentation: x1.15 (inline docs, READMEs, manifests)
    • Rework/refinement: x1.10 (code review, refactoring)
    • Combined multiplier: 1.55x = 6 hours minimum
    • Complexity buffer: +33% = 8 hours maximum

+==============================================================================+
```

---

## 🔄 Continuation Prompt

**COPY-PASTE THIS TO RESUME WORK:**

```markdown
Continue `template-naming-enhancement`. 0% | Phase 1. Update Plan/Work/Wall/Tokens columns + Overall Progress totals.
```

---

### Phase Status Table

| Phase | Name | Status | Start | End | Actual | Elapsed | Sub-Plan |
|-------|------|--------|-------|-----|--------|---------|----------|
| 1 | File Renaming & Migration | ⏳ Pending | - | - | - | - | - |
| 2 | Reference Updates (Code) | ⏳ Pending | - | - | - | - | - |
| 3 | Reference Updates (Docs) | ⏳ Pending | - | - | - | - | - |
| 4 | Validation & Git Commit | ⏳ Pending | - | - | - | - | - |

**Legend:**
- ⏳ Pending - Not started
- 🟡 In Progress - Active development
- ✅ Complete - Finished and validated
- ⚠️ Blocked - Dependency or issue preventing progress

---

## 🎯 Executive Summary

**Problem:** Template files use generic naming that makes them hard to discover globally:
- `master-plan-template.md` - lowercase, blends with normal docs
- `00-sub-plan-template.md` - numbered prefix confuses with actual plans (`01-`, `02-`)

**Solution:** Distinctive ALL-CAPS naming convention:
- `MASTER-PLAN-TEMPLATE.md` - Unique, searchable, clearly a template
- `SUB-PLAN-TEMPLATE.md` - No number, no confusion

**Primary Goals:**
- Instant global search discovery (`Ctrl+P` → `MASTER` or `SUB-PLAN`)
- Clear distinction between templates and actual plans
- Update all 50+ references across codebase

**Key Outcomes:**
- Renamed 2 template files with proper ALL-CAPS convention
- Updated references in Python orchestrators (UnifiedPlanGenerator, etc.)
- Updated references in documentation and README files
- Validated all imports and paths work correctly

**Autonomous Execution:**
This plan executes all 4 phases autonomously with checkpoint validations.

---

## 📋 Phase Overview

### Phase 1: File Renaming & Migration (1.5h)
- Rename `cortex-brain/templates/planning/master-plan-template.md` → `MASTER-PLAN-TEMPLATE.md`
- Rename `cortex-brain/documents/planning/orchestrators/00-sub-plan-template.md` → `SUB-PLAN-TEMPLATE.md`
- Create git commit: "refactor: Rename templates with ALL-CAPS convention for discoverability"

### Phase 2: Reference Updates (Code) (2h)
- Update Python orchestrators importing/referencing template paths
- Update `unified_plan_generator.py` template loading logic
- Update `cortex_header.py` template references
- Update any CLI wrappers or scripts
- Create git commit: "refactor: Update template path references in orchestrators"

### Phase 3: Reference Updates (Docs) (1.5h)
- Update README files mentioning template paths
- Update orchestrator documentation
- Update quick reference guides
- Update master planner tracker references
- Create git commit: "docs: Update template path references in documentation"

### Phase 4: Validation & Final Commit (1h)
- Run grep search to find any remaining old template references
- Test template loading in orchestrators
- Verify all imports work
- Document changes in learning library
- Create git commit: "docs: Add template naming enhancement to learning library"

---

## ✅ Success Criteria

- [ ] Both template files renamed with ALL-CAPS convention
- [ ] Zero grep matches for old template names (excluding git history/archives)
- [ ] All Python imports/paths updated and working
- [ ] All documentation references updated
- [ ] Learning library entry created with:
  - Use case: Template discoverability
  - Diagram: Before/After naming structure
  - Best practices: Template naming conventions
- [ ] All changes committed with detailed messages
- [ ] Master plan status updated after each phase

---

## 📁 Deliverables

**Phase 1:**
- `MASTER-PLAN-TEMPLATE.md` (renamed)
- `SUB-PLAN-TEMPLATE.md` (renamed)
- Git commit with file moves

**Phase 2:**
- Updated Python orchestrator files
- Git commit with code changes

**Phase 3:**
- Updated documentation files
- Git commit with doc changes

**Phase 4:**
- Validation report
- Learning library entry
- Final git commit

---

## 🚨 Risk Analysis

| Risk | Severity | Mitigation |
|------|----------|------------|
| Broken imports in orchestrators | MEDIUM | Comprehensive grep search + test runs |
| Old references in documentation | LOW | Systematic search and replace |
| Git history references | LOW | Archive/history paths remain unchanged |
| User confusion during transition | LOW | README update explains new convention |

---

## 📖 Related Documentation

- **Current Templates:**
  - `cortex-brain/templates/planning/master-plan-template.md`
  - `cortex-brain/documents/planning/orchestrators/00-sub-plan-template.md`

- **Orchestrators Using Templates:**
  - `src/operations/modules/planning/unified_plan_generator.py`
  - `src/operations/modules/templates/cortex_header.py`
  - `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`

- **Documentation Referencing Templates:**
  - `cortex-brain/MASTER-PLANNER-VISUAL-TRACKER-QUICK-REF.md`
  - `cortex-brain/documents/planning/orchestrators/sub-plan-creation-summary.md`
  - `src/orchestration_3_0/README.md`

---

## 🔄 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-16 | Asif Hussain | Initial plan created |

---

**Plan Status:** 🟡 In Progress  
**Total Project Duration:** 6-8 hours estimated  
**Actual Work Time:** TBD
