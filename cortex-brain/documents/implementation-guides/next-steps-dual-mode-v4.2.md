# Next Steps Dual-Mode System v4.2

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Created:** December 21, 2025  
**Status:** ✅ Enhancement to v4.1

---

## 🎯 Purpose

Extends Next Steps Intelligence v4.1 with optional **Autonomous Mode** for multi-step execution sequences while preserving the single-action **Interactive Mode** as default.

**Problem Solved:** Users want both focused single-action guidance (interactive) AND ability to see/execute multi-step roadmaps (autonomous).

**Solution:** Dual-mode system with keyword-triggered mode switching.

---

## 🏗️ Architecture

### Mode Detection

**Interactive Mode (Default):**
- Activated: Always (unless autonomous keyword detected)
- Output: Single high-value next step
- Format: `**Next:** {action_with_context}`

**Autonomous Mode (Opt-in):**
- Activated by keywords:
  - "autonomous"
  - "execute autonomously"
  - "show plan" / "show me the plan"
  - "roadmap" / "full roadmap"
  - "what's next" (with context suggesting multi-step)
  - "show all steps"
- Output: 3-5 step execution sequence
- Format: Checkbox list with effort/impact

---

## 📋 Interactive Mode (v4.1 - Unchanged)

**Decision Tree:** 9 steps (Critical → In-progress → High → Medium → Low)

**Output Format:**
```markdown
**Next:** {single_action_with_context}
```

**Examples:**
- `**Next:** Refactor align_system_v2 (complexity 56) - core system function`
- `**Next:** Fix 15 failing tests (blocking deployment)`
- `**Next:** Complete Phase 3: Validation`
- `✅ **All work complete!** No further action required.`

---

## 🚀 Autonomous Mode (v4.2 - New)

### Generation Rules

1. **Generate 3-5 steps** using same priority hierarchy as interactive mode
2. **Include effort estimate** for each step (e.g., "2h", "30m", "1 day")
3. **Include impact level** (HIGH, MEDIUM, LOW)
4. **Add checkboxes** for progress tracking (- [ ])
5. **Steps must be executable in sequence** (dependencies resolved)
6. **Total effort reasonable** for one session (<4 hours ideal)

### Output Format

```markdown
**Next (Autonomous Mode):**

- [ ] **Step 1:** {action_description} (effort: {time}, impact: {level})
- [ ] **Step 2:** {action_description} (effort: {time}, impact: {level})
- [ ] **Step 3:** {action_description} (effort: {time}, impact: {level})
[... up to 5 steps ...]

**Total Effort:** {sum_of_efforts}

Say "go" or "execute step 1" to begin autonomous execution.
Say "show me step 1" for detailed implementation plan.
```

### Examples

**Complexity Refactoring:**
```markdown
**Next (Autonomous Mode):**

- [ ] **Step 1:** Refactor `align_system_v2` - Extract 4 phase functions (effort: 2h, impact: HIGH)
- [ ] **Step 2:** Add comprehensive test coverage - Ensure 80%+ coverage (effort: 1h, impact: HIGH)
- [ ] **Step 3:** Measure complexity reduction - Validate <15 per function (effort: 15m, impact: MEDIUM)

**Total Effort:** 3h 15m

Say "go" to begin autonomous execution.
```

**System Maintenance:**
```markdown
**Next (Autonomous Mode):**

- [ ] **Step 1:** Run align with auto-fix - Fix registration gaps (effort: 10m, impact: HIGH)
- [ ] **Step 2:** Clean up obsolete files - Remove deprecated code (effort: 5m, impact: MEDIUM)
- [ ] **Step 3:** Optimize CORTEX.prompt.md - Reduce to <350 lines (effort: 15m, impact: MEDIUM)
- [ ] **Step 4:** Run full test suite - Validate no regressions (effort: 3m, impact: HIGH)

**Total Effort:** 33m

Say "go" to begin autonomous execution.
```

**Feature Implementation (TDD):**
```markdown
**Next (Autonomous Mode):**

- [ ] **Step 1:** Design API interface - Define contracts (effort: 30m, impact: HIGH)
- [ ] **Step 2:** Write failing tests (RED phase) - TDD first phase (effort: 45m, impact: HIGH)
- [ ] **Step 3:** Implement core logic (GREEN phase) - Make tests pass (effort: 2h, impact: HIGH)
- [ ] **Step 4:** Refactor for SOLID - Clean code principles (effort: 1h, impact: MEDIUM)
- [ ] **Step 5:** Integration testing - End-to-end validation (effort: 30m, impact: HIGH)

**Total Effort:** 4h 45m

Say "go" to begin autonomous execution.
```

---

## 🔄 Execution Flow

### Interactive Mode (Default)
1. User asks: "What should I do next?"
2. System analyzes state (errors, in-progress, complexity, etc.)
3. System shows single highest-priority action
4. User executes action manually
5. Repeat

### Autonomous Mode
1. User triggers: "show me the autonomous plan" or "roadmap"
2. System generates 3-5 step sequence
3. System displays with checkboxes, effort, impact
4. User confirms: "go" or "execute step 1"
5. System executes step 1, updates: `- [x] **Step 1:**`
6. System shows progress: "Step 1 complete (1/3)"
7. System auto-proceeds to step 2 OR waits for confirmation
8. User can interrupt: "stop" or "pause" anytime
9. Final summary shows all completed steps

---

## 📊 Mode Comparison

| Aspect | Interactive Mode | Autonomous Mode |
|--------|------------------|-----------------|
| **Activation** | Default (always) | Keywords: "autonomous", "roadmap", etc. |
| **Output** | Single action | 3-5 step sequence |
| **Format** | `**Next:** {action}` | Checkbox list with effort/impact |
| **Use Case** | Step-by-step guidance | Batch execution planning |
| **User Control** | Execute each action manually | Can execute all autonomously |
| **Interruption** | N/A | Can stop/pause anytime |
| **Best For** | Learning, exploration | Efficient batch work |

---

## 🎯 Use Cases

### When to Use Interactive Mode

- ✅ Learning a new workflow
- ✅ Exploring unfamiliar codebase
- ✅ Want to understand each step deeply
- ✅ Debugging or investigating
- ✅ Quick single-action guidance

### When to Use Autonomous Mode

- ✅ Know the domain well, want to batch work
- ✅ Repetitive refactoring (e.g., reduce 10 high-complexity functions)
- ✅ System maintenance routines
- ✅ Feature implementation with clear requirements
- ✅ Want to see full roadmap before starting

---

## 🔧 Implementation

### YAML Configuration

**File:** `cortex-brain/response-templates-v4.yaml`

**Changes Required:**

1. Update `next_steps` section guidelines to include dual-mode rules
2. Add `autonomous_mode` subsection under `next_steps_intelligence`
3. Update `standard_structure.parts.next_steps.content` with mode detection
4. Add examples for both modes
5. Increment version to 4.2.0

### Prompt Instructions

**File:** `.github/prompts/CORTEX.prompt.md`

**Changes Required:**

1. Update "Next Steps Intelligence" section with dual-mode support
2. Add autonomous mode trigger keywords
3. Provide examples of both formats
4. Update format rules to allow 3-5 items in autonomous mode

### Copilot Instructions

**File:** `.github/copilot-instructions.md`

**Changes Required:**

1. Add "Autonomous Mode" quick reference
2. Update response format rules for mode detection
3. Add trigger keyword list

---

## 📚 Examples by Domain

### Code Quality

**Interactive:**
```
**Next:** Refactor `_check_rule` (complexity 35) - critical SKULL validation path
```

**Autonomous:**
```
**Next (Autonomous Mode):**

- [ ] **Step 1:** Refactor `_check_rule` - Extract rule-specific validators (effort: 1.5h, impact: HIGH)
- [ ] **Step 2:** Refactor `build_pr_context` - Separate collection from formatting (effort: 2h, impact: HIGH)
- [ ] **Step 3:** Refactor `generate_master_plan` - Extract phase generators (effort: 1.5h, impact: HIGH)

**Total Effort:** 5h
```

### Testing

**Interactive:**
```
**Next:** Add tests for `planning_orchestrator.py` (currently 45% coverage, critical path)
```

**Autonomous:**
```
**Next (Autonomous Mode):**

- [ ] **Step 1:** Add unit tests for `PlanningOrchestrator` - Cover happy paths (effort: 45m, impact: HIGH)
- [ ] **Step 2:** Add error handling tests - Edge cases and exceptions (effort: 30m, impact: HIGH)
- [ ] **Step 3:** Add integration tests - End-to-end plan generation (effort: 1h, impact: MEDIUM)
- [ ] **Step 4:** Measure coverage improvement - Validate 80%+ coverage (effort: 10m, impact: HIGH)

**Total Effort:** 2h 25m
```

### Documentation

**Interactive:**
```
**Next:** Remove 3 obsolete planning guides (reduce maintenance burden)
```

**Autonomous:**
```
**Next (Autonomous Mode):**

- [ ] **Step 1:** Identify obsolete planning docs - Scan for deprecated content (effort: 15m, impact: MEDIUM)
- [ ] **Step 2:** Backup obsolete files - Move to archive/ folder (effort: 5m, impact: LOW)
- [ ] **Step 3:** Update cross-references - Fix broken links (effort: 20m, impact: MEDIUM)
- [ ] **Step 4:** Validate documentation - Ensure completeness (effort: 15m, impact: HIGH)

**Total Effort:** 55m
```

---

## ✅ Benefits

### For Users

- 🎯 **Flexibility:** Choose between focused (interactive) and batch (autonomous)
- ⚡ **Efficiency:** Autonomous mode reduces back-and-forth for known workflows
- 📊 **Visibility:** See full roadmap before committing
- 🔄 **Control:** Can interrupt/pause autonomous execution anytime

### For System

- 📈 **Metrics:** Track mode usage patterns
- 🧠 **Learning:** Understand user preferences (interactive vs autonomous)
- 🔍 **Insights:** See which workflows benefit from autonomous mode
- 🎨 **Adaptability:** Can optimize recommendations per mode

---

## 🚨 Cautions

1. **Don't overuse autonomous mode** - Interactive is better for learning
2. **Validate effort estimates** - First few runs may have inaccurate times
3. **Test interruption flow** - Ensure clean stop/pause behavior
4. **Monitor total effort** - Keep <4 hours for single session
5. **Check dependencies** - Steps must be executable in sequence

---

## 📊 Metrics (Target)

- **Mode Detection Accuracy:** >95% (correct mode for user intent)
- **Effort Estimation Error:** <20% (actual vs estimated time)
- **Step Completion Rate:** >80% (steps completed without skipping)
- **Interruption Rate:** <10% (how often users stop mid-execution)
- **User Satisfaction:** 4.5/5.0 stars

---

## 🔮 Future Enhancements

### Phase 1 (v4.2 - Current)
- ✅ Dual-mode documentation
- ☐ YAML configuration updates
- ☐ Prompt instruction updates
- ☐ Manual implementation by developers

### Phase 2 (v4.3 - Planned)
- ☐ Automated mode detection in response formatter
- ☐ Runtime execution flow with progress tracking
- ☐ Interruption handling (stop/pause/resume)
- ☐ Effort tracking and estimation refinement

### Phase 3 (v4.4 - Future)
- ☐ Machine learning for effort estimation
- ☐ User preference learning (interactive vs autonomous)
- ☐ Personalized mode recommendations
- ☐ A/B testing of different autonomous sequences

---

## 📚 Related Documentation

- **Next Steps Intelligence v4.1:** `cortex-brain/documents/implementation-guides/next-steps-intelligence-v4.1.md`
- **Response Templates v4.1:** `cortex-brain/response-templates-v4.yaml`
- **CORTEX Entry Point:** `.github/prompts/CORTEX.prompt.md`
- **Copilot Instructions:** `.github/copilot-instructions.md`

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
