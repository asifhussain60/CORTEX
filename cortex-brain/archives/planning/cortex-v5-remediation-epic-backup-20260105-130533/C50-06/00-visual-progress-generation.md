# C50-06: Visual Progress Generation

**Plan ID:** C50-06  
**Epic:** C50 CORTEX v5 Gap Remediation  
**Status:** 🔄 IN PROGRESS  
**Duration:** 2 days (16 hours)  
**Dependencies:** C50-00B (Epic & Feature Planner) ✅

---

## 🎯 Objective

Standardize visual progress bar rendering across all autonomous orchestrators to ensure consistent, 10-character width progress visualization in response templates.

**Current State:**
- ✅ Progress bar generation exists in `TemplateRenderer` (lines 93-117)
- ✅ ASCII progress bars implemented (█ filled, ░ empty)
- ✅ Response templates v4 support progress rendering
- ✅ Tests exist (`test_progress_bar_helpers.py`)

**Gap Analysis:**
- ❌ No standardized 10-character width enforcement
- ❌ Inconsistent progress rendering across orchestrators
- ❌ No centralized progress generation module
- ❌ Missing integration with autonomous execution templates

---

## 📋 Phases

### Phase 1: Standardize Progress Bar Width (4h)

**Goal:** Enforce 10-character standard width across all progress bars

**Tasks:**
1. Update `TemplateRenderer.generate_progress_bar()` to default to width=10
2. Update response templates to use 10-character progress bars
3. Update all orchestrators using progress bars to use standard width
4. Add validation for progress bar width in tests

**Deliverables:**
- Modified `src/response_templates/template_renderer.py` (line 93)
- Updated `cortex-brain/response-templates-v4.yaml` (progress_bar components)
- 5 unit tests for width standardization

**Acceptance Criteria:**
- ✅ Default width is 10 characters
- ✅ All templates use 10-character bars
- ✅ Backward compatibility maintained (custom width still supported)
- ✅ All existing tests pass

---

### Phase 2: Centralized Progress Module (6h)

**Goal:** Create dedicated `VisualProgressGenerator` module for reusable progress rendering

**Tasks:**
1. Create `src/orchestrators/shared/visual_progress_generator.py`
2. Implement `VisualProgressGenerator` class with:
   - `generate_bar(percentage, width=10)` - ASCII progress bar
   - `generate_with_label(label, percentage, width=10)` - Labeled bar
   - `generate_multi_phase(phases, current_phase)` - Multi-phase display
   - `generate_epic_progress(completed, total)` - Epic-level overview
3. Migrate `TemplateRenderer.generate_progress_bar()` to use new module
4. Add comprehensive unit tests

**Deliverables:**
- NEW: `src/orchestrators/shared/visual_progress_generator.py` (~200 LOC)
- Modified: `src/response_templates/template_renderer.py` (delegate to new module)
- 15 unit tests for new module

**Acceptance Criteria:**
- ✅ `VisualProgressGenerator` class operational
- ✅ All 4 methods implemented and tested
- ✅ `TemplateRenderer` delegates to new module
- ✅ No breaking changes to existing progress bars
- ✅ 15/15 tests passing

---

### Phase 3: Autonomous Template Integration (4h)

**Goal:** Integrate standardized progress bars into autonomous execution response templates

**Tasks:**
1. Update `autonomous_execution_progress` template (response-templates-v4.yaml)
2. Add progress bar rendering to planning, ADO, vacuum, cleanup templates
3. Ensure 10-character width consistency
4. Add template validation tests

**Deliverables:**
- Modified: `cortex-brain/response-templates-v4.yaml` (4 templates updated)
- 8 integration tests for template rendering

**Acceptance Criteria:**
- ✅ All autonomous templates use `VisualProgressGenerator`
- ✅ 10-character width enforced in all templates
- ✅ Templates render correctly with sample data
- ✅ 8/8 integration tests passing

---

### Phase 4: Documentation & Validation (2h)

**Goal:** Document progress rendering standards and validate across system

**Tasks:**
1. Create progress rendering guide (`docs/progress-rendering-guide.md`)
2. Update orchestrator documentation with progress examples
3. Run full test suite validation
4. Update copilot instructions with progress rendering rules

**Deliverables:**
- NEW: `docs/progress-rendering-guide.md`
- Modified: Orchestrator documentation (planning, ADO, vacuum, cleanup)
- Modified: `.github/copilot-instructions.md` (progress rendering section)
- Validation report

**Acceptance Criteria:**
- ✅ Documentation complete
- ✅ All tests passing (28+ progress-related tests)
- ✅ No regressions in existing progress rendering
- ✅ Copilot instructions updated

---

## 🎯 Definition of Done

- ✅ 10-character standard width enforced
- ✅ `VisualProgressGenerator` module created and tested
- ✅ All autonomous templates use standardized progress bars
- ✅ 28+ unit/integration tests (100% passing)
- ✅ Documentation complete
- ✅ No breaking changes to existing functionality
- ✅ Validation report generated

---

## 📊 Success Metrics

- **Consistency:** 100% of autonomous orchestrators use 10-character bars
- **Test Coverage:** 28+ tests, 90%+ coverage for progress module
- **Performance:** Progress generation <1ms per bar
- **Usability:** Clear, standardized visual feedback across all orchestrators

---

## 🔗 References

- Existing: `src/response_templates/template_renderer.py` (lines 93-117)
- Existing: `tests/response_templates/test_progress_bar_helpers.py` (328 lines)
- Templates: `cortex-brain/response-templates-v4.yaml` (progress components)
- Investigation: `cortex-brain/documents/investigations/progress-bar-brittleness/`
- Epic: `C50-cortex-v5-remediation/00-cortex-v5-remediation.md`

---

**Author:** Asif Hussain  
**Created:** 2026-01-04  
**Last Updated:** 2026-01-04
