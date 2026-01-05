# GAP-9 Investigation - Plan Viewer HTML Not Generated
**Date:** 2026-01-04  
**Investigator:** CORTEX AI Assistant  
**Trigger:** User noticed C150 plan missing plan-viewer.html

---

## 🎯 Executive Summary

**Finding:** Planning Orchestrator v5 doesn't generate `plan-viewer.html` + `launch_plan_viewer.py` despite manifest specification and available implementation.

**Severity:** MEDIUM  
**Impact:** No real-time progress monitoring, poor user experience, manual file tracking required  
**Root Cause:** Integration gap - `planning_orchestrator_v5.py` doesn't call `DualModePlanningOrchestrator.generate_html_viewer()`

---

## 🔍 Investigation Details

### Evidence Collected

**1. C50 Plan (HAS plan viewer):**
```
/cortex-brain/documents/planning/active/C50-cortex-v5-remediation/
├── plan-viewer.html ✅
├── launch_plan_viewer.py ✅
└── [17 feature folders]
```

**2. C150 Plan (MISSING plan viewer):**
```
/cortex-brain/documents/planning/active/c150-remediation-plan/
├── 00-c150-remediation-plan.yaml ✅
├── README.md ✅
├── tracking/progress-tracker.json ✅
├── plan-viewer.html ❌ MISSING
└── launch_plan_viewer.py ❌ MISSING
```

**3. Manifest Specification:**
```yaml
# planning-system-5.0-manifest.yaml (lines 50-59)
required_files:
  - path: "plan-viewer.html"
    type: "viewer"
    description: "Universal HTML viewer - auto-detects EPIC vs FEATURE mode"
    generation_phase: "approval"
  
  - path: "launch_plan_viewer.py"
    type: "utility"
    description: "HTTP server launcher for plan viewer"
    generation_phase: "approval"
```

**4. Implementation EXISTS:**
```python
# src/orchestrators/planning/dual_mode_integration.py (line 250)
def generate_html_viewer(self) -> Path:
    """Generate interactive HTML viewer for plan progress tracking."""
    # ... 40 lines of implementation
    output_path = self.plan_path / "plan-viewer.html"
    generator.generate(tracker_data, output_path)
    return output_path
```

**5. Planning Orchestrator v5 DOESN'T call it:**
```bash
$ grep -r "DualModePlanningOrchestrator\|html_viewer\|plan-viewer" \
  src/orchestrators/planning/planning_orchestrator_v5.py

# NO MATCHES - Integration missing!
```

---

## 🧩 Architecture Analysis

### Current State (Broken)

```
┌──────────────────────────────────────┐
│ Planning Orchestrator v5             │
│                                      │
│  ✅ Creates plan folder structure    │
│  ✅ Generates 00-plan.yaml           │
│  ✅ Creates tracking/progress.json   │
│  ❌ Doesn't call viewer generator    │
└──────────────────────────────────────┘
                 │
                 │ (missing integration)
                 ▼
┌──────────────────────────────────────┐
│ DualModePlanningOrchestrator         │
│                                      │
│  ✅ generate_html_viewer() EXISTS    │
│  ✅ HTMLViewerGenerator integrated   │
│  ✅ Auto-detects EPIC vs FEATURE     │
│  ⏸️  Never called by v5              │
└──────────────────────────────────────┘
```

### Expected State (Fixed)

```
┌──────────────────────────────────────┐
│ Planning Orchestrator v5             │
│                                      │
│  ✅ Creates plan folder structure    │
│  ✅ Generates 00-plan.yaml           │
│  ✅ Creates tracking/progress.json   │
│  ✅ Calls viewer generator ⚡ NEW    │
└──────────────────────────────────────┘
                 │
                 │ orchestrator.generate_html_viewer()
                 ▼
┌──────────────────────────────────────┐
│ DualModePlanningOrchestrator         │
│                                      │
│  ✅ Generates plan-viewer.html       │
│  ✅ Generates launch_plan_viewer.py  │
│  ✅ Auto-detects mode from structure │
└──────────────────────────────────────┘
```

---

## 🛠️ Root Cause Analysis

### Why This Happened

1. **Planning System 5.0 Evolution:**
   - `DualModePlanningOrchestrator` was created (January 2026)
   - `HTMLViewerGenerator` was extracted into separate module
   - **Integration step skipped** - Planning Orchestrator v5 not updated

2. **Split Codebase:**
   - Viewer logic in `dual_mode_integration.py` ✅
   - Planning logic in `planning_orchestrator_v5.py` ✅
   - **Bridge code missing** ❌

3. **Manifest vs Implementation:**
   - Manifest **specifies** plan-viewer.html should be generated
   - Implementation **provides** generation capability
   - **Execution code** doesn't connect them

---

## 📝 Remediation Plan

### Phase 16: Fix Plan Viewer HTML Generation

**Estimated Hours:** 3.0  
**Priority:** P2 (Medium)

**Changes Required:**

1. **Add import to `planning_orchestrator_v5.py`:**
   ```python
   from src.orchestrators.planning.dual_mode_integration import (
       DualModePlanningOrchestrator,
       create_epic_plan,
       create_feature_plan
   )
   ```

2. **Call viewer generator after plan creation:**
   ```python
   # In PlanningOrchestratorV5.execute() or approve_plan():
   
   try:
       orchestrator = DualModePlanningOrchestrator(self.plan_path)
       viewer_path = orchestrator.generate_html_viewer()
       self.logger.info(f"Generated plan viewer: {viewer_path}")
       
       # Also generate launcher script
       launcher_path = self.plan_path / "launch_plan_viewer.py"
       self._generate_launcher_script(launcher_path)
       
   except Exception as e:
       self.logger.warning(f"Failed to generate plan viewer: {e}")
       # Non-blocking error - plan still valid without viewer
   ```

3. **Add launcher script template method:**
   ```python
   def _generate_launcher_script(self, output_path: Path) -> None:
       """Generate launch_plan_viewer.py script."""
       template = self._get_launcher_template()
       output_path.write_text(template)
       output_path.chmod(0o755)  # Make executable
   ```

**Validation:**
- ✅ `plan-viewer.html` generated for C150 plan
- ✅ `launch_plan_viewer.py` generated for C150 plan
- ✅ HTML viewer auto-detects FEATURE mode
- ✅ Progress tracker JSON loads correctly
- ✅ Launcher script opens browser successfully
- ✅ No breaking changes to existing functionality

---

## 🎯 Retroactive Generation

**Immediate Fix for C150 Plan:**

```python
from src.orchestrators.planning.dual_mode_integration import DualModePlanningOrchestrator
from pathlib import Path

plan_path = Path("cortex-brain/documents/planning/active/c150-remediation-plan")
orchestrator = DualModePlanningOrchestrator(plan_path)
viewer_path = orchestrator.generate_html_viewer()
print(f"✅ Generated: {viewer_path}")
```

This can be run immediately after Phase 16 implementation to generate the missing files for C150.

---

## 📊 Comparison: C50 vs C150

| Feature | C50 Plan | C150 Plan | Status |
|---------|----------|-----------|--------|
| **plan-viewer.html** | ✅ 1,148 lines | ❌ Missing | GAP-9 |
| **launch_plan_viewer.py** | ✅ 214 lines | ❌ Missing | GAP-9 |
| **Real-time progress** | ✅ Available | ❌ Manual tracking | Impact |
| **User experience** | ✅ Browser-based | ❌ File inspection | Impact |
| **Auto-refresh** | ✅ 30s interval | ❌ N/A | Impact |

---

## 🔗 Plan Viewer Features (Missing from C150)

### HTML Viewer Capabilities:
1. **Real-time Progress Tracking:**
   - Auto-refresh every 30 seconds
   - Live phase status updates
   - Duration tracking

2. **Glassmorphism UI:**
   - CORTEX brand colors
   - Responsive design
   - Accessibility features (WCAG AA)

3. **Interactive Features:**
   - Phase expansion/collapse
   - Progress bars
   - Status indicators (⏳ in_progress, ✅ complete, ❌ failed)

4. **Data Source:**
   - Reads from `tracking/progress-tracker.json`
   - No server-side processing needed
   - Pure client-side JavaScript

### Launcher Script Capabilities:
1. **Automatic Server Start:**
   - Launches Python HTTP server (port 8000)
   - Non-blocking execution
   - Auto-detects project root

2. **Browser Integration:**
   - Opens default browser automatically
   - Constructs correct relative URL
   - Handles path resolution

---

## 📚 Related Files

**Modified in Phase 16:**
- `src/orchestrators/planning/planning_orchestrator_v5.py` (integration code)

**Referenced (no changes needed):**
- `src/orchestrators/planning/dual_mode_integration.py` (viewer generator)
- `src/orchestrators/planning/html_viewer_generator.py` (HTML template)
- `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml` (specification)

**Generated by Phase 16:**
- `cortex-brain/documents/planning/active/c150-remediation-plan/plan-viewer.html`
- `cortex-brain/documents/planning/active/c150-remediation-plan/launch_plan_viewer.py`

---

## ✅ Success Criteria (AC-12)

**Description:** Plan viewer HTML generation integrated into Planning Orchestrator v5

**Validation:**
- Check `plan-viewer.html` exists in C150 plan folder
- Check `launch_plan_viewer.py` exists in C150 plan folder
- Planning Orchestrator v5 calls `DualModePlanningOrchestrator.generate_html_viewer()`

**Pass Criteria:**
- HTML viewer generated ✅
- Launcher script works ✅
- Real-time progress monitoring available ✅

---

## 🎓 Lessons Learned

1. **Manifest ≠ Implementation:**
   - Specifying something in manifest doesn't auto-implement it
   - Need explicit integration code

2. **Module Extraction Risks:**
   - When extracting code into new modules, update all callers
   - Check for orphaned functionality

3. **Feature Completeness:**
   - HTML viewer is "polish" feature but significantly improves UX
   - Plan viewing experience: CLI vs Browser = Night vs Day

4. **Testing Gaps:**
   - Should have end-to-end test: "Create plan → Verify plan-viewer.html exists"
   - Integration tests would catch this

---

**Status:** ✅ Investigation complete, GAP-9 added to remediation plan  
**Next Step:** Execute Phase 16 to implement fix
