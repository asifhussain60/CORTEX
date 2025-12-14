# Planning Orchestrator Autonomous Mode Failures Investigation

**Investigation Date:** December 14, 2025  
**Investigator:** GitHub Copilot  
**Severity:** HIGH  
**Status:** ACTIVE

---

## 🎯 Problem Summary

Multiple critical failures observed in Planning Orchestrator's autonomous execution mode:

1. **ASCII Progress Bar Rendering** - Visual progress bar showing raw ASCII in GitHub Copilot Chat instead of rendered bar
2. **Master Plan Status Updates Missing** - Phases not marked "In Progress" at start
3. **Master Plan Completion Updates Missing** - Phases not marked "Complete" at end
4. **Plan Folder Movement on Approval** - Approved plans not moved to `active/` folder
5. **Plan Folder Movement on Completion** - Completed plans not moved to `completed/` folder
6. **Knowledge Extraction Phase Missing** - No knowledge graph/learning library updates before completion

---

## 🔍 Root Cause Analysis

### Issue 1: ASCII Progress Bar in Copilot Chat

**File:** `cortex-brain/response-templates.yaml`  
**Location:** Lines 86-105 (autonomous_execution_progress template)

**Problem:**
```yaml
autonomous_execution_progress:
  format: '## 🧠 CORTEX Autonomous Plan Execution
    ...
    **Progress:** [{progress_bar}] {percentage}%
```

The `{progress_bar}` variable contains ASCII characters like `█████░░░░░` which may not render correctly in GitHub Copilot Chat's markdown renderer.

**Evidence:**
- Template expects ASCII bar from `planning_orchestrator.py:_generate_progress_bar()`
- Method returns raw ASCII: `"█" * filled + "░" * empty`
- Copilot Chat may not support extended ASCII rendering

**Fix Strategy:**
- Replace ASCII with HTML/CSS progress bar
- Use markdown-compatible progress indicators (✅/☐)
- Add fallback to percentage-only display

---

### Issue 2: Phase Status Not Updated to "In Progress"

**File:** `src/orchestrators/planning_orchestrator.py`  
**Method:** `execute_plan_autonomous()` (Line 1822)

**Problem:**
Autonomous execution loop does NOT call `update_phase_status()` when starting a phase.

**Evidence:**
```python
# Line 1886-1924: Execute each phase
for phase_idx, phase in enumerate(phases, 1):
    phase_name = phase.get('phase_name', f'Phase {phase_idx}')
    phase_tasks = phase.get('tasks', [])
    
    # Render phase progress in chat using template
    if self.template_manager:
        # ... template rendering ...
    
    # NO CALL TO: self.update_phase_status(phase_name, 'in_progress')
    
    yield_progress(...)
    
    # Execute each task in phase
    for task_idx, task in enumerate(phase_tasks, 1):
        # ... task execution ...
```

**Missing Call:**
```python
# Should be added at line ~1890:
self.update_phase_status(
    phase_name=phase_name,
    status='in_progress',
    progress=0
)
```

---

### Issue 3: Phase Status Not Updated to "Complete"

**File:** `src/orchestrators/planning_orchestrator.py`  
**Method:** `execute_plan_autonomous()` (Line 1822)

**Problem:**
After completing all tasks in a phase, `update_phase_status()` is NOT called to mark phase complete.

**Evidence:**
```python
# Line 1990-2080: After all tasks complete
# Save orchestration checkpoint at phase boundary (Feature 11)
try:
    checkpoint_state = {
        'plan_id': plan_id,
        'phase': phase_idx,
        'phase_name': phase_name,
        # ...
    }
    
    checkpoint_id = self.checkpoint_manager.save_checkpoint(...)
    
    # NO CALL TO: self.update_phase_status(phase_name, 'completed', 100)
```

**Missing Call:**
```python
# Should be added at line ~1995 (before checkpoint):
self.update_phase_status(
    phase_name=phase_name,
    status='completed',
    progress=100,
    tokens_used=0  # TODO: Track actual tokens
)
```

---

### Issue 4: Plan Folder Not Moved to Active on Approval

**File:** `src/orchestrators/planning_orchestrator.py`  
**Method:** `approve_plan()` (Line 1743)

**Problem:**
Method only moves plan FILE from `active/` to `approved/` directory. Does NOT move plan FOLDER (if folder structure enabled).

**Evidence:**
```python
# Line 1743-1820: approve_plan() method
def approve_plan(self, plan_filename: str) -> Dict[str, Any]:
    planning_root = self.cortex_root / "cortex-brain" / "documents" / "planning"
    active_dir = planning_root / "active"
    approved_dir = planning_root / "approved"
    
    old_path = active_dir / plan_filename  # FILE PATH ONLY
    new_path = approved_dir / plan_filename
    
    # ... moves file only ...
    
    # MISSING: Check if folder structure enabled via PlanFolderManager
    # MISSING: Call self.folder_manager.move_plan(plan_id, 'active', 'approved')
```

**Fix Required:**
```python
# Add after line 1766 (after path construction):
if self.folder_manager.is_folder_structure_enabled():
    # Extract plan_id from filename (e.g., PLAN-2025-12-14-feature.md)
    plan_id = plan_filename.replace('.md', '')
    try:
        self.folder_manager.move_plan(plan_id, 'active', 'approved')
        logger.info(f"✅ Moved plan folder: {plan_id} (active → approved)")
    except Exception as e:
        logger.warning(f"Failed to move plan folder: {e}")
```

---

### Issue 5: Plan Folder Not Moved to Completed on Completion

**File:** `src/orchestrators/planning_orchestrator.py`  
**Method:** `complete_plan()` (Line 2216)

**Problem:**
Same as Issue 4 - only moves FILE, not FOLDER.

**Evidence:**
```python
# Line 2216-2300: complete_plan() method
def complete_plan(self, plan_filename: str) -> Dict[str, Any]:
    planning_root = self.cortex_root / "cortex-brain" / "documents" / "planning"
    approved_dir = planning_root / "approved"
    completed_dir = planning_root / "completed"
    
    old_path = approved_dir / plan_filename  # FILE PATH ONLY
    new_path = completed_dir / plan_filename
    
    # ... moves file only ...
    
    # MISSING: self.folder_manager.move_plan(plan_id, 'approved', 'completed')
```

**Fix Required:**
```python
# Add after line 2250 (after successful file move):
if self.folder_manager.is_folder_structure_enabled():
    plan_id = plan_filename.replace('.md', '')
    try:
        self.folder_manager.move_plan(plan_id, 'approved', 'completed')
        logger.info(f"✅ Moved plan folder: {plan_id} (approved → completed)")
    except Exception as e:
        logger.warning(f"Failed to move plan folder: {e}")
```

---

### Issue 6: Knowledge Extraction Phase Missing

**File:** `src/orchestrators/planning_orchestrator.py`  
**Method:** `execute_plan_autonomous()` (Line 1822)

**Problem:**
Before calling `complete_plan()`, NO knowledge extraction happens. Learning library and knowledge graph should be updated.

**Evidence:**
```python
# Line 2089-2095: Completion flow
completion_msg = progress_renderer.render_completion_summary(...)
print(completion_msg)

# Complete the plan
completion_result = self.complete_plan(plan_filename)  # IMMEDIATE COMPLETION

# MISSING: Knowledge extraction phase before completion
```

**Required Knowledge Extraction:**

1. **Learning Library Update** (STEP-2.6, STEP-5.7 from manifest)
   - Document successful patterns
   - Capture phase completion insights
   - Store in `cortex-brain/documents/learning/`

2. **Knowledge Graph Update**
   - Extract patterns from execution context
   - Update pattern confidence scores
   - Store file relationships
   - Store workflow success metrics

**Fix Required:**
```python
# Add at line ~2090 (BEFORE complete_plan()):

# Phase 7: Knowledge Extraction (CRITICAL)
logger.info("🎭 Phase transition: EXECUTION → KNOWLEDGE_EXTRACTION")
print("\n### 📚 Phase 7: Knowledge Extraction\n")

try:
    # 1. Extract execution context
    extraction_context = {
        'plan_id': plan_id,
        'total_phases': total_phases,
        'total_tasks': completed_tasks,
        'duration_seconds': (datetime.now() - start_time).total_seconds(),
        'execution_log': execution_log,
        'files_modified': [],  # TODO: Track from git
        'tests_run': 0,  # TODO: Track from test results
        'tests_passed': 0,
        'coverage': 0.0,
        'quality_gates': []  # TODO: Track gates passed
    }
    
    # 2. Update knowledge graph
    from src.operations.utilities.knowledge_graph_auto_updater import KnowledgeGraphAutoUpdater
    kg_updater = KnowledgeGraphAutoUpdater(self.cortex_root)
    kg_result = kg_updater.safe_update(extraction_context)
    
    if kg_result.success:
        logger.info(f"✅ Knowledge graph updated: {kg_result.patterns_added} patterns")
        print(f"   ✅ Added {kg_result.patterns_added} patterns to knowledge graph")
    else:
        logger.warning(f"⚠️  Knowledge graph update failed: {kg_result.error_message}")
    
    # 3. Document to learning library
    from src.tier1.learning_library import store_lesson
    lesson_id = store_lesson(
        category='plan_execution',
        title=f'Autonomous Execution: {plan_id}',
        content={
            'plan_id': plan_id,
            'phases': total_phases,
            'tasks': completed_tasks,
            'duration': extraction_context['duration_seconds'],
            'success': True,
            'patterns': kg_result.patterns_added if kg_result.success else 0
        },
        outcome='success',
        confidence=0.9
    )
    
    logger.info(f"✅ Documented as {lesson_id} in learning library")
    print(f"   ✅ Documented as {lesson_id} in learning library")
    
    print("   ✅ Knowledge extraction complete\n")
    
except Exception as e:
    logger.error(f"❌ Knowledge extraction failed: {e}")
    print(f"   ⚠️  Knowledge extraction failed (non-blocking): {e}\n")

logger.info("🎭 Phase transition: KNOWLEDGE_EXTRACTION → COMPLETION")

# NOW complete the plan
completion_result = self.complete_plan(plan_filename)
```

---

## 📊 Impact Assessment

| Issue | Severity | User Impact | System Impact |
|-------|----------|-------------|---------------|
| ASCII Progress Bar | Medium | Poor UX - can't see progress | None |
| Missing "In Progress" | Medium | Confusion about current phase | Session state inconsistent |
| Missing "Complete" | Medium | Can't track completion | Metrics inaccurate |
| No Folder Move (Approval) | High | Plans lost/disorganized | File structure broken |
| No Folder Move (Completion) | High | Plans lost/disorganized | File structure broken |
| No Knowledge Extraction | **CRITICAL** | **Learning lost forever** | **No pattern improvement** |

---

## ✅ Resolution Plan

### Phase 1: Critical Fixes (Priority: CRITICAL)
- [ ] Issue 6: Implement knowledge extraction phase
- [ ] Issue 4: Fix folder movement on approval
- [ ] Issue 5: Fix folder movement on completion

### Phase 2: Status Updates (Priority: HIGH)
- [ ] Issue 2: Add "In Progress" status update
- [ ] Issue 3: Add "Complete" status update
- [ ] Add session state persistence

### Phase 3: UX Improvements (Priority: MEDIUM)
- [ ] Issue 1: Fix progress bar rendering
- [ ] Add visual phase transitions
- [ ] Improve progress template

### Phase 4: Validation (Priority: HIGH)
- [ ] Add integration tests for autonomous execution
- [ ] Test folder structure with/without feature flag
- [ ] Validate knowledge extraction with real plans
- [ ] Verify learning library updates

---

## 🔧 Implementation Notes

### Testing Strategy

1. **Unit Tests:**
   - Test `update_phase_status()` calls in autonomous loop
   - Test `folder_manager.move_plan()` integration
   - Test knowledge extraction with mock context

2. **Integration Tests:**
   - Create test plan in `active/`
   - Run `approve_plan()` → verify folder moved
   - Run `execute_plan_autonomous()` → verify phases updated
   - Run `complete_plan()` → verify folder moved + knowledge extracted

3. **Manual Validation:**
   - Run autonomous execution with real plan
   - Monitor Copilot Chat output
   - Check folder structure after approval/completion
   - Verify knowledge graph entries created

### Rollback Plan

If knowledge extraction causes issues:
1. Wrap in try/except (non-blocking)
2. Add feature flag: `cortex.config.json::planning.enable_knowledge_extraction`
3. Default: `true` (extract knowledge)
4. If disabled: Log warning and skip

---

## 📚 References

- **Manifest:** `cortex-brain/orchestrator-manifests/planning-system-2.0-manifest.yaml`
  - REQ-006: Learning library integration (STEP-2.6, STEP-5.7)
  - REQ-009: Modular plan structure (folder management)
- **PlanFolderManager:** `src/workflows/plan_folder_manager.py`
- **Knowledge Graph:** `src/tier2/knowledge_graph.py`
- **KG Auto-Updater:** `src/operations/utilities/knowledge_graph_auto_updater.py`
- **Response Templates:** `cortex-brain/response-templates.yaml`

---

## 📝 Next Steps

1. **Immediate:** Create fix PR for Issues 4, 5, 6 (CRITICAL)
2. **Short-term:** Add phase status updates (Issues 2, 3)
3. **Medium-term:** Fix progress bar rendering (Issue 1)
4. **Long-term:** Add comprehensive integration tests

---

**Investigation Complete - Ready for Implementation**
