# Response Template Refactor Plan - Enhancement Summary

**Date:** 2025-12-01  
**Author:** Asif Hussain  
**Plan Version:** 2.1 (Enhanced with Cleanup & Deployment Gates)

---

## Changes Made to Original Plan

### 1. Added Phase 7: Cleanup & Enforcement (4 hours)

**Purpose:** Remove legacy implementation to prevent confusion and enforce new system

**Key Tasks:**
- Archive `cortex-brain/response-templates.yaml` → `archives/legacy-response-templates-v2.yaml`
- Delete `src/response_templates/` module (6 Python files)
- Delete `tests/response_templates/` (2 test files)
- Update 5 validation tools to use new YAML files
- Add CLI enforcement to 4 entry points (cortex_entry, deploy, align, healthcheck)
- Create migration tool: `src/operations/migrate_templates.py`

**Files Affected:**
- **Deleted:** 10 files (8 Python + 2 test files)
- **Updated:** 9 files (validation tools + CLI wrappers)
- **Created:** 1 migration tool

**CLI Enforcement Strategy:**
```python
# Startup validation in cortex_entry.py
if (brain_path / "response-templates.yaml").exists():
    logger.warning("⚠️ Legacy response-templates.yaml detected")
    logger.warning("   Run: python -m src.operations.migrate_templates")
    sys.exit(1)

required_files = [
    "response-base-components.yaml",
    "response-template-definitions.yaml",
    "response-profile-variants.yaml",
    "response-routing-rules.yaml"
]

missing = [f for f in required_files if not (brain_path / f).exists()]
if missing:
    logger.error(f"❌ Missing template files: {missing}")
    sys.exit(1)
```

---

### 2. Enhanced Phase 6 → Phase 6 & 8 (6 hours total)

**Phase 6: Documentation & Pre-Deployment (3 hours)**
- Added deployment validation spec creation
- Added rollback procedures documentation
- Extended from 2h → 3h to account for deployment prep

**Phase 8: Deployment with Validation Gates (3 hours)**
- **NEW:** 3 deployment validation gates (Gates 17-19)
- **NEW:** Post-deployment smoke tests
- **NEW:** Feature flag configuration
- **NEW:** Rollback procedure execution guide

---

### 3. New Deployment Validation Gates

**Gate 17: Template System Architecture ✅ (ERROR)**
- **Check:** New modular YAML files exist and valid
- **Validates:**
  - `response-base-components.yaml` exists
  - `response-template-definitions.yaml` exists
  - `response-profile-variants.yaml` exists
  - `response-routing-rules.yaml` exists
  - Legacy `response-templates.yaml` removed
  - `TemplateComposer` class exists
  - `TemplateSelector` class exists

**Gate 18: Legacy Code Removed ✅ (ERROR)**
- **Check:** Old `src/response_templates/` module deleted
- **Validates:**
  - `src/response_templates/template_loader.py` deleted
  - `src/response_templates/template_renderer.py` deleted
  - `src/response_templates/template_registry.py` deleted
  - `tests/response_templates/test_introduction_discovery_template.py` deleted
  - All legacy imports removed from codebase

**Gate 19: CLI Enforcement Active ⚠️ (WARNING)**
- **Check:** Entry points validate new system on startup
- **Validates:**
  - `cortex_entry.py` checks for legacy file
  - Validates new YAML files present
  - Uses `TemplateComposer` class
  - Exits with error if validation fails

**Integration with Existing Gates:**
- Total gates: 19 (was 16)
- ERROR gates: 17 (must pass)
- WARNING gates: 2 (should pass)

---

### 4. Enhanced Migration Strategy

**Added Production Deployment Section:**
- Pre-deployment checklist (9 items)
- Deployment steps (4 stages)
- Post-deployment validation (3 smoke tests)
- Gradual rollout strategy (4-week timeline)

**Key Addition:**
```yaml
# Conservative rollout approach
Week 1: Internal testing (users_percentage: 0)
Week 2: Limited release (users_percentage: 10)
Week 3: Majority release (users_percentage: 50)
Week 4: Full release (users_percentage: 100)
```

---

### 5. Comprehensive Rollback Plan

**Added 3-Level Rollback Strategy:**

**Level 1: Feature Flag Disable (5 minutes)**
```yaml
features:
  modular_templates: false  # Emergency revert
```

**Level 2: Git Revert (15 minutes)**
```bash
# Restore legacy files
git checkout CORTEX-3.0 -- cortex-brain/response-templates.yaml
git checkout CORTEX-3.0 -- src/response_templates/
git checkout CORTEX-3.0 -- tests/response_templates/
```

**Level 3: Branch Rollback (30 minutes)**
```bash
# Full deployment rollback
git revert <bad-commit-hash>
git push origin main --force
```

**Rollback Triggers:**
- Composition time >100ms (2x target)
- Error rate >5%
- User complaints >10
- Critical security issue
- Data corruption

---

### 6. Updated Risk Assessment

**Added New Risks:**

**High Risk:**
- **Production Deployment Failure** (NEW)
  - Mitigation: 3 validation gates + smoke tests
  - Fallback: Documented rollback procedure

**Medium Risk:**
- **CLI Enforcement Breaking Workflows** (NEW)
  - Mitigation: Clear error messages + migration command
  - Fallback: Feature flag disable

- **Legacy Code Removal Impact** (NEW)
  - Mitigation: Comprehensive grep + archive files
  - Fallback: Restore from archives

---

### 7. Enhanced Next Steps (Week-by-Week Plan)

**Original:** 5 generic steps  
**Enhanced:** 8 detailed sections with checklists

**Week 1: Review & Approval + Phase 1-2**
- Stakeholder review
- YAML refactoring
- Composer engine

**Week 2: Phase 3-5**
- Profile enhancement
- Selection integration
- Validation & testing

**Week 3: Phase 6-7 + Pre-Deployment**
- Documentation
- Cleanup & enforcement
- Validation gate creation

**Week 4: Deployment**
- Production deployment
- Post-deployment monitoring
- Completion report

**Optional: 4-Week Gradual Rollout**
- Conservative approach for risk mitigation

**Success Criteria:** 10 measurable checkpoints

---

## Implementation Timeline Comparison

### Original Plan
- **Phases:** 6
- **Total Time:** 21 hours (3 days)
- **Deployment:** Feature flag only
- **Cleanup:** Not specified

### Enhanced Plan
- **Phases:** 8
- **Total Time:** 28 hours (4 days)
- **Deployment:** 3 validation gates + smoke tests
- **Cleanup:** Comprehensive (Phase 7)

**Additional Time Breakdown:**
- Phase 6 extended: +1 hour (deployment prep)
- Phase 7 added: +4 hours (cleanup & enforcement)
- Phase 8 added: +3 hours (deployment gates)
- **Total increase:** +7 hours (33% more time for safety)

---

## Files Created/Modified Summary

### New Files (Phase 7-8)
1. `src/operations/migrate_templates.py` - Migration tool
2. `scripts/validation_gates.py` (Gates 17-19 added)
3. `cortex-brain/documents/planning/features/PLAN-2025-12-01-response-template-refactor-CHANGES.md` (this file)

### Deleted Files (Phase 7)
1. `src/response_templates/template_loader.py`
2. `src/response_templates/template_renderer.py`
3. `src/response_templates/template_registry.py`
4. `src/response_templates/multi_template_orchestrator.py`
5. `src/response_templates/confidence_response_generator.py`
6. `src/response_templates/__init__.py`
7. `tests/response_templates/test_introduction_discovery_template.py`
8. `tests/response_templates/__init__.py`

### Archived Files (Phase 7)
1. `cortex-brain/response-templates.yaml` → `cortex-brain/archives/legacy-response-templates-v2.yaml`

### Modified Files (Phase 7)
1. `src/entry_point/cortex_entry.py` - CLI enforcement
2. `src/entry_point/response_formatter.py` - Remove legacy imports
3. `src/operations/modules/questions/question_router.py` - Remove legacy imports
4. `src/operations/deploy.py` - Add template validation
5. `src/operations/align.py` - Add template validation
6. `src/operations/healthcheck.py` - Add template validation
7. `src/operations/setup.py` - Auto-migrate on setup
8. `src/validation/template_header_validator.py` - Use new YAMLs
9. `src/validation/conflict_detector.py` - Use new structure
10. `src/validation/wiring_validator.py` - Use routing rules YAML
11. `src/validators/template_validator.py` - Modular architecture
12. `src/remediation/wiring_generator.py` - Generate new format
13. `scripts/deploy_cortex.py` - Add Gates 17-19

**Total Modified:** 13 files

---

## Deployment Gate Integration

### Existing Deployment System
- **File:** `scripts/deploy_cortex.py`
- **Current Gates:** 16 (Gates 1-16)
- **Validation:** Pre-deployment only

### Enhanced Deployment System
- **New Gates:** 3 (Gates 17-19)
- **Total Gates:** 19
- **Validation:** Pre + post deployment
- **Smoke Tests:** 3 (help, onboard, plan)

### Gate Execution Flow
```
┌─────────────────────────────────────────┐
│   python scripts/deploy_cortex.py       │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────▼─────────┐
        │ Gate 1-16 (Exist) │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │ Gate 17: Template │
        │   Architecture    │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │ Gate 18: Legacy   │
        │      Removed      │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │ Gate 19: CLI      │
        │   Enforcement     │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │  Deploy to main   │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │ Post-Deploy Tests │
        │  (3 smoke tests)  │
        └───────────────────┘
```

---

## Key Improvements Summary

### Safety Enhancements
✅ **3 new validation gates** prevent broken deployments  
✅ **3-level rollback plan** for rapid recovery  
✅ **Gradual rollout option** for risk mitigation  
✅ **Post-deployment monitoring** for first week

### Code Quality
✅ **Legacy code removed** (10 files deleted)  
✅ **CLI enforcement** prevents old system usage  
✅ **Migration tool** for safe cutover  
✅ **Comprehensive testing** (smoke tests + unit tests)

### Documentation
✅ **Deployment checklist** (9 pre-flight items)  
✅ **Rollback procedures** (3 levels documented)  
✅ **Week-by-week timeline** (4-week plan)  
✅ **Success criteria** (10 measurable checkpoints)

---

## Approval Required

**Before Phase 7-8 Implementation:**
- [ ] Approve cleanup strategy (delete vs archive)
- [ ] Approve CLI enforcement approach (hard fail vs warning)
- [ ] Approve deployment gates (Gates 17-19)
- [ ] Approve rollout strategy (immediate vs gradual)
- [ ] Approve rollback triggers (5 conditions)

**Stakeholder Sign-off:**
- [ ] Technical Lead: ___________________ Date: _______
- [ ] Product Owner: ___________________ Date: _______
- [ ] Security Review: _________________ Date: _______

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-01  
**Next Review:** After Phase 6 completion
