# Visual Progress Bar Wiring Guide

**Purpose:** Ensure planning and ADO orchestrators display visual progress bars after each phase, matching the maintenance prompt pattern.

**Author:** Asif Hussain | **Date:** 2025-12-30  
**Reference:** #file:Chat01.md (maintenance execution demonstrates correct pattern)

---

## 🎯 Problem Statement

The maintenance prompt (`.github/prompts/cortex-maintenance.prompt.md`) successfully displays visual progress bars after each phase:

```
### 📊 MAINTENANCE STATUS

**Overall Progress:** `██░░░░░░░░░░░░░░░░░░` **9%** 🔄 In Progress

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - DISCOVERY | `██████████` | 100% ✅ Complete |
| Phase 2 - CLEANUP | `░░░░░░░░░░` | 0% 🔄 Starting |
```

**Planning and ADO orchestrators should use the same pattern** for consistency and user visibility.

---

## ✅ Solution Implemented

### 1. Planning System Manifest Updated

**File:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`

**Added Section:** `visual_progress_enforcement` under `REQ-005`

**Key Enforcement Rules:**

- ❌ **Forbidden:** Phase completions without progress visualization
- ❌ **Forbidden:** Text-only status updates
- ❌ **Forbidden:** Skipping progress bars in autonomous mode
- ✅ **Required:** Render visual progress table after EVERY phase
- ✅ **Required:** Use ASCII progress bars (`██████████░░░░░░░░░░` format)
- ✅ **Required:** Show emojis (✅ Complete, 🔄 In Progress, ⏳ Pending)

**Reference Format:**
```markdown
---
### 📊 PLAN EXECUTION STATUS

**Overall Progress:** `████████░░░░░░░░░░░░` **XX%** {STATUS_EMOJI} {STATUS_TEXT}

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - {Name} | `██████████` | 100% ✅ Complete |
| Phase 2 - {Name} | `████████░░` | 80% 🔄 In Progress |
| Phase 3 - {Name} | `░░░░░░░░░░` | 0% ⏳ Pending |

📊 **Tests:** XX/XX passing | **Code:** X,XXX LOC | **Status:** {STATUS}

---
```

**Implementation References:**
- Template: `cortex-brain/response-templates-v4.yaml`
- Component: `components.visual_progress.plan_tracker`
- Renderer: `src/response_templates/template_renderer.py::generate_progress_bar()`
- Phase Rows: `src/response_templates/template_renderer.py::generate_phase_rows()`

---

### 2. ADO Orchestrator Manifest Updated

**File:** `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml`

**Added Section:** `visual_progress_enforcement` under `REQ-005`

**ADO-Specific Enhancements:**

- **Work Item Metrics:** Epics/Features/Tasks created, total story points
- **Link Display:** ADO work item URLs (clickable)
- **Status Indicators:** ✅ Created, 🔗 Linked, ⚠️ Pending, ❌ Failed

**Reference Format:**
```markdown
---
### 📊 ADO WORK ITEM GENERATION STATUS

**Overall Progress:** `████████░░░░░░░░░░░░` **XX%** {STATUS_EMOJI} {STATUS_TEXT}

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - DISCOVERY | `██████████` | 100% ✅ Complete |
| Phase 2 - VALIDATION | `████████░░` | 80% 🔄 In Progress |
| Phase 3 - GENERATION | `░░░░░░░░░░` | 0% ⏳ Pending |
| Phase 4 - APPROVAL | `░░░░░░░░░░` | 0% ⏳ Pending |
| Phase 5 - EXECUTION | `░░░░░░░░░░` | 0% ⏳ Pending |
| Phase 6 - COMPLETION | `░░░░░░░░░░` | 0% ⏳ Pending |

📊 **Work Items:** XX/XX created | **Story Points:** XXX | **Status:** {STATUS}

---
```

**ADO Orchestrator Path:** `src/orchestrators/ado/ado_orchestrator.py`

---

### 3. Template Renderer Verification

**File:** `src/response_templates/template_renderer.py`

**✅ Already Fixed (GAPS-1230):**

Lines 231-236 explain that `progress_bar` component is **ALWAYS** shown for planning operations (no longer skipped in autonomous mode).

**Available Methods:**

1. **`generate_progress_bar(percentage, width=20, filled='█', empty='░')`**
   - Lines 607-625
   - Generates ASCII progress bars like `██████████░░░░░░░░░░`

2. **`generate_phase_rows(phases)`**
   - Lines 666-730
   - Generates phase table rows with progress bars and status emojis

3. **`format_elapsed_time(seconds)`**
   - Lines 645-663
   - Formats durations like "2m 30s" or "1h 15m"

4. **`generate_tdd_status(red_done, green_done, refactor_done)`**
   - Lines 627-643
   - Generates TDD status like "R✅ G✅ F⏸️"

---

## 📋 Implementation Checklist for Orchestrators

When implementing visual progress in planning or ADO orchestrators:

### Phase Completion Pattern

```python
# After each phase completes
print(f"""
✅ Phase {phase_num} - {phase_name}: Complete
   └─ Actions: {action_count} | Duration: {elapsed_time}
   └─ Auto-proceeding to Phase {phase_num + 1}...

### 📊 {OPERATION_NAME} STATUS

**Overall Progress:** `{progress_bar}` **{percentage}%** {status_emoji} {status_text}

| Phase | Progress | Status |
|-------|----------|--------|
{phase_rows}

📊 {metrics}

---
""")
```

### Required Imports

```python
from src.response_templates.template_renderer import TemplateRenderer

# In orchestrator __init__
self.template_renderer = TemplateRenderer()
```

### Generate Progress Bar

```python
# Generate overall progress bar
overall_percentage = (completed_phases / total_phases) * 100
progress_bar = self.template_renderer.generate_progress_bar(
    percentage=overall_percentage,
    width=20,
    filled_char='█',
    empty_char='░'
)
```

### Generate Phase Rows

```python
# Prepare phase data
phases = [
    {
        'phase_num': 1,
        'phase_name': 'DISCOVERY',
        'status': 'completed',  # 'completed' | 'in_progress' | 'not_started'
        'percentage': 100,
        'tdd_enabled': False,
        'completed_tasks': 5,
        'total_tasks': 5,
        'elapsed_time': 45.2
    },
    # ... more phases
]

# Generate table rows
phase_rows = self.template_renderer.generate_phase_rows(phases)
```

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `.github/prompts/cortex-maintenance.prompt.md` | Reference implementation (shows correct pattern) |
| `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml` | Planning visual progress enforcement rules |
| `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml` | ADO visual progress enforcement rules |
| `cortex-brain/response-templates-v4.yaml` | Template definitions (components.visual_progress) |
| `src/response_templates/template_renderer.py` | Progress bar generator methods |
| `src/orchestrators/planning_orchestrator.py` | Planning orchestrator (needs wiring) |
| `src/orchestrators/ado/ado_orchestrator.py` | ADO orchestrator (needs wiring) |

---

## 🚀 Next Steps

1. **Wire Planning Orchestrator:**
   - Add `TemplateRenderer` import
   - Call `generate_progress_bar()` after each phase
   - Call `generate_phase_rows()` to render table
   - Include visual progress in all phase completion responses

2. **Wire ADO Orchestrator:**
   - Add `TemplateRenderer` import
   - Include ADO-specific metrics (work items, story points)
   - Render progress after phases: DISCOVERY → VALIDATION → GENERATION → APPROVAL → EXECUTION → COMPLETION

3. **Test Coverage:**
   - Verify progress bars appear in all planning operations
   - Verify progress bars appear in all ADO operations
   - Validate ASCII rendering (no broken characters)
   - Test autonomous mode (progress should show, not skip)

4. **Documentation:**
   - Update planning user guide with visual progress examples
   - Update ADO user guide with work item progress examples
   - Add screenshots to documentation

---

## ✅ Validation

To verify visual progress is working:

1. **Run Maintenance:** `system maintenance` (reference implementation)
2. **Run Planning:** `/CORTEX Plan feature-name` (should match maintenance pattern)
3. **Run ADO:** `ado plan feature-name` (should match maintenance pattern)

**Expected Outcome:** All three operations display identical visual progress bar styles.

---

**Status:** ✅ Manifest updates complete | ⏳ Orchestrator wiring pending  
**Reference:** Chat01.md demonstrates maintenance execution with visual progress
