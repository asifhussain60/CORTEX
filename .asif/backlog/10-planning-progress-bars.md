# 🎯 Planning & ADO Orchestrator Progress Enhancement

**Priority:** HIGH | **Estimated Effort:** 25 min | **Category:** Orchestration

---

## 🎯 Objective

Add visual progress bars to planning and ADO orchestrators that display upon completion of each phase. Progress bars should show both overall execution progress and phase-specific progress before moving to the next phase.

**Requirements:**
- Display progress bar after EACH phase completion  
- Show overall progress (e.g., `[████░░░░] 50% - Phase 3/6 Complete`)
- Show phase-specific progress within each phase
- Use response templates with visual indicators

---

## 📋 Execution Steps

### Step 1: Check Toolkit for Existing Progress Tools
Before implementing, verify no existing progress visualization scripts:
```bash
grep -i "progress.*bar\|visual.*progress" cortex-toolkit/TOOLS-INVENTORY.md

find cortex-toolkit -name "*progress*" -o -name "*visual*" | grep "\.py$"
```

### Step 2: Load Orchestrator Manifests
Read the manifest files to understand current structure:
```bash
cat cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml
cat cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml
```

### Step 3: Verify Response Templates  
Check that progress bar templates exist:
```bash
grep -A 10 "autonomous_execution_progress\|ado_execution_progress" cortex-brain/response-templates-v4.yaml
```

Expected output: Template definitions with progress bar components.

### Step 4: Identify Master Plan Generation Section
Search for section responsible for generating `00-master-plan.md` content:
```bash
grep -n "master.*plan\|plan.*template" cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml | head -5
```

### Step 5: Add Progress Tracking Instructions
Insert these required sections into master plan template at lines identified in Step 4:

```yaml
master_plan_template:
  required_sections:
    - overview
    - phases
    - execution_flow:  # ADD THIS
        progress_tracking:
          - display_after_each_phase: true
          - show_overall_progress: true  
          - show_phase_progress: true
          - template_reference: "autonomous_execution_progress"
        autonomous_execution:
          - execute_and_verify_per_step: true
          - pause_at_phase_boundaries: true
        final_refactor:
          - run_quality_checks: true
          - remove_debug_statements: true
        learning_documentation:
          - update_lessons_learned: true
          - update_knowledge_graph: true
```

### Step 6: Update Both Manifests
Apply same changes to ADO manifest:
```bash
# Create backup first
cp cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml.bak

# Apply same structure to ADO manifest (manually edit or use sed)
```

### Step 7: Verify Template Integration
Check that referenced templates exist:
```bash
grep -c "autonomous_execution_progress\|ado_execution_progress" cortex-brain/response-templates-v4.yaml
```

Expected: At least 2 matches (one for each template).

---

## ✅ Success Criteria
- [ ] Planning manifest includes progress tracking config (verify: `grep -c "progress_tracking" cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml` returns `> 0`)
- [ ] ADO manifest includes progress tracking config (verify: `grep -c "progress_tracking" cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml` returns `> 0`)
- [ ] Progress templates exist (verify: `grep -E "autonomous_execution_progress|ado_execution_progress" cortex-brain/response-templates-v4.yaml | wc -l` returns `>= 2`)
- [ ] Manifests parse without errors (verify: `python3 -c "import yaml; yaml.safe_load(open('cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml'))"` exits with code 0)
- [ ] Learning documentation phase enforced in both manifests

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/10-planning-progress-bars.md
```
