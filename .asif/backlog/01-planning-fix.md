
Add instruction: the user response template with progress bar should be deisplayed upon completiono of each phase before moving to next phase.


# 🎯 Planning & ADO Orchestrator Enhancement

**Priority:** HIGH | **Estimated Effort:** 25 min | **Category:** Orchestration

---

## 🎯 Objective

Ensure planning and ADO orchestrators include mandatory execution flow instructions in generated master plans.

---

## 📋 Execution Steps

### Step 1: Load Orchestrator Manifests
```
Read files:
- cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml
- cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml
```

### Step 2: Identify Master Plan Generation Section
Find the section responsible for generating `00-master-plan.md` content.

### Step 3: Add Mandatory Execution Flow Instructions
Insert these required sections into master plan template:

```markdown
---
## 📊 MANDATORY EXECUTION PHASES

### Phase A: Implementation with Progress Tracking
**Visual Progress Bar:** Use response templates with visual progress indicators
```
[████████░░] 80% - Phase X Complete
```

### Phase B: Autonomous Execution Mode
When implementing, use autonomous execution:
1. Execute step → Verify → Report → Next step
2. Do NOT wait for user confirmation between sub-steps
3. Pause only at major phase boundaries

### Phase C: Final Refactor
After all implementation complete:
1. Run code quality checks
2. Remove debug statements
3. Consolidate duplicate code
4. Update imports and dependencies

### Phase D: Knowledge Library Documentation
After completion, document learnings:
1. Update `cortex-brain/lessons-learned.yaml`
2. Add patterns to `cortex-brain/knowledge-graph.yaml`
3. Create summary in `cortex-brain/documents/summaries/`
---
```

### Step 4: Update Both Manifests
Add to `master_plan_template` section in both manifests:
```yaml
master_plan_template:
  required_sections:
    - overview
    - phases
    - execution_flow:  # NEW
        - visual_progress_tracking
        - autonomous_execution
        - final_refactor
        - learning_documentation
```

### Step 5: Verify Template Integration
Check that response templates referenced in execution flow exist:
```bash
grep -r "progress.*bar\|visual.*progress" cortex-brain/response-templates*.yaml
```

---

## ✅ Success Criteria
- [ ] Planning manifest includes mandatory execution phases
- [ ] ADO manifest includes mandatory execution phases
- [ ] Generated master plans include progress tracking instructions
- [ ] Learning documentation phase enforced

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/01-planning-fix.md
```
