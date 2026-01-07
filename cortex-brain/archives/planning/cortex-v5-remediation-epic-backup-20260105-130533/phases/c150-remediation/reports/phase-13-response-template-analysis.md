# Phase 13: Response Templates Refinement - Analysis

**Date:** January 4, 2026  
**Plan:** C150 Remediation Plan  
**Status:** 🔄 IN PROGRESS

## Executive Summary

**Requirement:** Update `response-templates-v4.yaml` for orchestrator hand-offs

**Current Status:**
- ✅ Template file exists and is structured
- ✅ `autonomous_execution_progress` template defined (line 1551)
- ⚠️ Shield icon (🛡️) missing from template header
- ⚠️ Header format doesn't match CORTEX.prompt.md specification
- ⚠️ Concise mode defined but not implemented in TemplateRenderer

## Gap Analysis

### 1. Shield Icon in Headers

**Required (from CORTEX.prompt.md):**
```markdown
## 🛡️🧠 CORTEX {Orchestrator Name} Execution
```

**Current (response-templates-v4.yaml:1551):**
```yaml
format: |
  ## 🛡️🧠 CORTEX Plan Execution
  **Author:** Asif Hussain | **Plan:** {{plan_name}} | **Orchestrator:** Planning System 5.0 ✅
```

**Current (template_renderer.py:731):**
```python
output = f"""## 🧠 CORTEX Plan Execution
**Author:** Asif Hussain | **Plan:** {plan_name}
```

**Issue:** TemplateRenderer.render_autonomous_progress() doesn't include 🛡️ shield icon

**Impact:** User sees `## 🧠 CORTEX` instead of `## 🛡️🧠 CORTEX`

**Fix Required:**
1. Add `orchestrator_name` parameter to `render_autonomous_progress()`
2. Update header format to include 🛡️ shield
3. Use generic orchestrator name instead of "Plan Execution"

### 2. Accessibility (Concise Mode)

**Required (response-templates-v4.yaml:1556):**
```yaml
default_mode: "concise"  # NEW: Accessibility-first

modes:
  concise:
    description: "Minimal updates for accessibility (WCAG-aligned cognitive load management)"
    use_when: "default for all autonomous execution"
    display_policy:
      phase_start: "Show phase name + overall progress bar only"
      task_completion: "SILENT - no user output"
      phase_completion: "Show completed phase + next phase (3 lines)"
      overall_completion: "Summary table (≤40 lines)"
```

**Current Implementation:** None - `render_autonomous_progress()` always uses verbose format

**Impact:** All autonomous orchestrators produce verbose output (violates cognitive load management)

**Fix Required:**
1. Add `mode` parameter to `render_autonomous_progress(mode='concise')`
2. Implement concise format:
   - Phase start: Progress bar + phase name only
   - Task completion: No output
   - Phase completion: 3-line update
   - Overall completion: Summary table

### 3. Orchestrator-Specific Headers

**Required:** Different header text for each orchestrator

**Current:** Hard-coded "Plan Execution"

**Expected Headers:**
- Planning v5: `## 🛡️🧠 CORTEX Planning System Execution`
- ADO v2: `## 🛡️🧠 CORTEX ADO Work Item Generation`
- Sanitization v2: `## 🛡️🧠 CORTEX Sanitization Execution`
- Cleanup v2: `## 🛡️🧠 CORTEX Cleanup Execution`
- Vacuum v2: `## 🛡️🧠 CORTEX Vacuum Execution`

**Fix Required:**
1. Add `orchestrator_title` parameter
2. Template: `## 🛡️🧠 CORTEX {orchestrator_title}`

### 4. Template Metadata

**Current (response-templates-v4.yaml:1627):**
```yaml
context_needed: true
metadata:
  category: planning
  operation: autonomous_execution
response_type: adaptive
accessibility:
  wcag_level: "AA"
  cognitive_load: "minimized"
  default_verbosity: "low"
```

**Issue:** Metadata correctly specifies WCAG AA and low verbosity, but implementation doesn't honor it

**Fix Required:** Implement concise mode to match metadata promises

## Template Renderer Analysis

### Current Method Signature

```python
def render_autonomous_progress(
    self,
    plan_name: str,
    current_phase: int,
    total_phases: int,
    current_phase_name: str,
    current_task: str,
    overall_percentage: float,
    phases: list,
    elapsed_seconds: float = 0,
    estimated_remaining_seconds: float = 0,
    threat_analysis: dict = None,
    dor_status: dict = None,
    dod_status: dict = None,
    next_action: str = "Continue execution..."
) -> str:
```

### Required Changes

**Add Parameters:**
```python
def render_autonomous_progress(
    self,
    orchestrator_name: str,           # NEW: e.g., "Planning System"
    orchestrator_title: str,          # NEW: e.g., "Planning System Execution"
    plan_name: str,
    current_phase: int,
    total_phases: int,
    current_phase_name: str,
    current_task: str,
    overall_percentage: float,
    phases: list,
    elapsed_seconds: float = 0,
    estimated_remaining_seconds: float = 0,
    threat_analysis: dict = None,
    dor_status: dict = None,
    dod_status: dict = None,
    next_action: str = "Continue execution...",
    mode: str = "concise"             # NEW: "concise" or "verbose"
) -> str:
```

## Implementation Plan

### Change 1: Add Shield Icon to Header

**File:** `src/response_templates/template_renderer.py`  
**Line:** 798  
**Change:**
```python
# Before:
output = f"""## 🧠 CORTEX Plan Execution
**Author:** Asif Hussain | **Plan:** {plan_name}

# After:
output = f"""## 🛡️🧠 CORTEX {orchestrator_title}
**Author:** Asif Hussain | **Orchestrator:** {orchestrator_name} | **Plan:** {plan_name}
```

### Change 2: Implement Concise Mode

**File:** `src/response_templates/template_renderer.py`  
**Location:** After line 798  
**Add:**
```python
# NEW: Handle concise mode (accessibility-first)
if mode == "concise":
    return f"""## 🛡️🧠 CORTEX {orchestrator_title}

`{overall_bar}` **{overall_percentage:.0f}%** {status_emoji}

**Phase {current_phase}/{total_phases}:** {current_phase_name}  
**Task:** {current_task[:60]}

**Next:** {next_action}
"""
```

### Change 3: Update Method Signature

**File:** `src/response_templates/template_renderer.py`  
**Line:** 731  
**Change:** Add new parameters with defaults for backward compatibility

### Change 4: Update YAML Template

**File:** `cortex-brain/response-templates-v4.yaml`  
**Line:** 1590  
**Change:** Update format to include 🛡️ and orchestrator_title placeholder

## Testing Requirements

### Test 1: Shield Icon Rendering
- Call `render_autonomous_progress(orchestrator_title="Planning System Execution", ...)`
- Verify header: `## 🛡️🧠 CORTEX Planning System Execution`

### Test 2: Concise Mode (Default)
- Call with `mode="concise"` (or omit for default)
- Verify output ≤10 lines
- Verify NO phase breakdown table
- Verify NO threat analysis section
- Verify NO DoR/DoD section

### Test 3: Verbose Mode
- Call with `mode="verbose"`
- Verify full output with all sections
- Verify phase breakdown table exists
- Verify threat analysis section (if provided)
- Verify DoR/DoD section

### Test 4: Orchestrator Name Variations
- Test with all 5 orchestrator names
- Verify header format consistent

### Test 5: Backward Compatibility
- Ensure existing calls without new parameters still work
- Use sensible defaults

## Orchestrator Integration

### Orchestrators to Update

| Orchestrator | File | Method | Status |
|--------------|------|--------|--------|
| Planning v5 | `src/orchestrators/planning/planning_orchestrator_v5.py` | Various progress calls | 🔄 TODO |
| ADO v2 | `src/orchestrators/ado/v2/ado_orchestrator_v2.py` | Progress updates | 🔄 TODO |
| Sanitization v2 | `src/orchestrators/sanitization/v2/sanitization_orchestrator_v2.py` | Progress updates | 🔄 TODO |
| Cleanup v2 | `src/orchestrators/cleanup/v2/cleanup_orchestrator_v2.py` | Progress updates | 🔄 TODO |
| Vacuum v2 | `src/orchestrators/vacuum/v2/vacuum_orchestrator_v2.py` | Progress updates | 🔄 TODO |

### Update Pattern

**Before:**
```python
renderer.render_autonomous_progress(
    plan_name=self.plan_name,
    current_phase=current_phase,
    total_phases=total_phases,
    current_phase_name=phase_name,
    ...
)
```

**After:**
```python
renderer.render_autonomous_progress(
    orchestrator_name="Planning System 5.0",
    orchestrator_title="Planning System Execution",
    plan_name=self.plan_name,
    current_phase=current_phase,
    total_phases=total_phases,
    current_phase_name=phase_name,
    ...,
    mode="concise"  # Default, explicitly set for clarity
)
```

## Expected Outcomes

### Before Phase 13
```markdown
## 🧠 CORTEX Plan Execution
**Author:** Asif Hussain | **Plan:** C150 Remediation Plan

---

### 📊 Execution Progress
```
╔══════════════════════════════════════════════════════════════════════════╗
║  Plan: C150 Remediation Plan                                            ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Overall: [████████░░] 85%  🚀                                           ║
║  Phase 13/20: Response Templates Refinement                             ║
...
```
(~80 lines total - verbose)
```

### After Phase 13 (Concise Mode - Default)
```markdown
## 🛡️🧠 CORTEX Planning System Execution

`████████░░` **85%** 🚀

**Phase 13/20:** Response Templates Refinement  
**Task:** Implementing concise mode for accessibility

**Next:** Continue with Phase 14
```
(~8 lines total - concise)

### After Phase 13 (Verbose Mode - User Requested)
```markdown
## 🛡️🧠 CORTEX Planning System Execution
**Author:** Asif Hussain | **Orchestrator:** Planning System 5.0 | **Plan:** C150 Remediation Plan

---

### 📊 Execution Progress
...
(~80 lines total - verbose, with 🛡️ shield icon)
```

## Accessibility Compliance

### WCAG AA Requirements Met

1. **Cognitive Load Management**
   - Concise mode reduces visual noise by 90%
   - Updates only at phase boundaries (not per-task)
   - Summary format aids scanning

2. **Screen Reader Friendliness**
   - Progress bars use consistent format: `[filled][empty] XX%`
   - Status indicators use semantic text (not just emoji)
   - Clear hierarchical structure

3. **Reading Level**
   - Concise mode: 3-8 lines (Grade 6 reading level)
   - Verbose mode: Available on request (Grade 10 reading level)

4. **Visual Clarity**
   - High contrast progress bars
   - Clear status indicators (✅ ⏳ 🔄)
   - Consistent formatting

## Configuration Changes Required

### response-templates-v4.yaml

**Line 1590 (format section):**
```yaml
# OLD:
format: |
  ## 🛡️🧠 CORTEX Plan Execution
  **Author:** Asif Hussain | **Plan:** {{plan_name}} | **Orchestrator:** Planning System 5.0 ✅

# NEW:
format: |
  ## 🛡️🧠 CORTEX {{orchestrator_title}}
  **Author:** Asif Hussain | **Orchestrator:** {{orchestrator_name}} | **Plan:** {{plan_name}}
```

**Line 1564 (concise mode format):**
```yaml
# Already correctly defined:
format: |
  ## 🛡️🧠 CORTEX: {{phase_name}}
  `{{overall_bar}}` **{{overall_percentage}}%**
  
  {{#if phase_completed}}
  ✅ {{completed_phase}} complete
  **Next:** {{next_phase}}
  {{/if}}
```

**Action:** ✅ No changes needed (already correct)

## Summary

### Changes Required

1. ✅ **template_renderer.py**
   - Add `orchestrator_name` parameter
   - Add `orchestrator_title` parameter
   - Add `mode` parameter (default: "concise")
   - Implement concise mode logic
   - Update header to include 🛡️ shield icon

2. ✅ **response-templates-v4.yaml**
   - Update format section with orchestrator_title placeholder
   - Verify concise mode format (already correct)

3. ✅ **5 Orchestrators**
   - Update progress calls to include new parameters
   - Set mode="concise" explicitly

### Estimated Time

- TemplateRenderer changes: 30 minutes
- YAML template updates: 15 minutes
- Orchestrator updates: 45 minutes (5 × 9 minutes each)
- Testing: 30 minutes

**Total:** 2.0 hours

### Phase 13 Status

**Status:** 🔄 ANALYSIS COMPLETE - Ready for implementation

---

*Generated by C150 Remediation Plan - Phase 13*  
*Analysis completed: January 4, 2026*  
*Next: Implement changes*
