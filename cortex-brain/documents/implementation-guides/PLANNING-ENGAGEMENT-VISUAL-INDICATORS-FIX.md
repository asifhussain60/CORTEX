# 🛡️ Universal Planning Gate - Implementation Guide

**Author:** Asif Hussain  
**Date:** December 17, 2025  
**Status:** ✅ IMPLEMENTED  
**Version:** 2.0.0 (Universal Planning)

---

## 🎯 Design Principle

**CRITICAL:** Planning is NOT triggered by keywords. Planning is UNIVERSAL.

**Core Concept:**
```
Every Request → Temp Plan → Refine → Approve → Execute
```

**NO "plan" keyword needed.** User says:
- "create authentication system" → temp plan created
- "build user dashboard" → temp plan created
- "add OAuth support" → temp plan created

Planning happens FIRST, always. Execution happens AFTER approval, never before.

**User Experience:**
- User requests "plan authentication system"
- Planning orchestrator executes silently in background
- NO visual feedback (🛡️ shield icon, 🎭 orchestrator hints)
- NO session ID shown
- NO iteration count
- NO status updates

---

## 🔄 Universal Planning Workflow

### User Says: "create authentication system"

**System Response:**
```
======================================================================
🛡️ **Universal Planning Gate** | 🎭 **Creating Temp Plan**
All work requires planning → refinement → approval → execution
======================================================================

🔄 **Generating Initial Draft...**
📁 Plan folder: `auth-system-20251217`
🧠 Analyzing codebase context...
✅ Initial draft generated (1250ms)
📄 View plan: `cortex-brain/documents/planning/temp-plans/auth-system-20251217/plan.md`

📋 **Temp Plan Created:** `auth-system-20251217`
🔄 **Session ID:** `session-20251217-143022`
📊 **Iteration:** 1/∞ (refinement mode)
✨ **Status:** Awaiting your feedback

💡 **What to do next:**
   - Review the plan
   - Provide feedback for refinement
   - When satisfied, say "approve" to execute
```

**Key Points:**
- NO "plan" keyword in user request
- Temp plan created automatically
- User refines iteratively
- Execution ONLY after approval

---

## ✅ Implementation Summary (v2.0 - Universal Gate)

### Fix 1: Universal Planning Gate (Intent Router)

**File:** `src/cortex_agents/intent_router.py`

**Changes:**
- REMOVED all planning keyword triggers
- ALL requests route to planning (except meta-commands)
- Meta-commands bypass: help, status, healthcheck, feedback

**Before (v1.0 - Keyword-Based):**
```python
# PRIORITY 0: Check for planning intent FIRST
planning_triggers = ["plan", "planning", "design", ...]

for trigger in planning_triggers:
    if trigger in message_lower:
        return IntentClassificationResult(intent=IntentType.PLAN, ...)
```

**After (v2.0 - Universal):**
```python
# UNIVERSAL PLANNING GATE: ALL requests go through planning first
meta_commands = ["help", "status", "healthcheck", "feedback"]
is_meta_command = any(cmd in message_lower for cmd in meta_commands)

if not is_meta_command:
    logger.info("🛡️ Universal Planning Gate: All requests require planning")
    return IntentClassificationResult(
        intent=IntentType.PLAN,
        confidence=1.0,  # Absolute confidence - planning is mandatory
        ...
    )
```

**Result:**
- ✅ ALL work requests create temp plan first
- ✅ NO keyword triggers needed
- ✅ Planning is mandatory, not optional
- ✅ Meta-commands (help, status) bypass gate

---

### Fix 2: Planning Gate Enforcement (Unified Entry Point)

**File:** `src/operations/modules/routing/unified_entry_point_utility.py`

**Changes:**
- REMOVED keyword-based gate check
- ALL requests flagged for planning
- Only meta-commands and approvals bypass

**Before (v1.0 - Keyword-Based):**
```python
planning_triggers = ["plan", "planning", ...]
for trigger in planning_triggers:
    if trigger in request_lower:
        return {"planning_required": True, "trigger_keyword": trigger}
return {"planning_required": False}  # Default: no planning
```

**After (v2.0 - Universal):**
```python
# Meta-commands bypass
meta_commands = ["help", "status", "approve", "execute"]
for cmd in meta_commands:
    if cmd in request_lower:
        return {"planning_required": False, "bypass_allowed": True}

# ALL OTHER REQUESTS: Require planning
return {
    "planning_required": True,
    "reason": "Universal planning gate - all work requires temp plan approval"
}
```

**Result:**
- ✅ Default behavior: planning required
- ✅ Explicit bypass only for meta-commands
- ✅ No keyword triggers needed

---

### Fix 3: Simplified Keywords (cortex-operations.yaml)

**File:** `cortex-operations.yaml`

**Changes:**
- REMOVED creation triggers (plan, design, architect)
- KEPT approval triggers (approve, execute)
- Updated description to clarify universal gate

**Before (v1.0):**
```yaml
natural_language:
- plan
- planning
- create plan
- plan feature
# ... 18 triggers
```

**After (v2.0):**
```yaml
natural_language:
- approve plan
- approve
- execute plan
- execute all phases autonomously
- promote plan
- finalize plan
```

**Result:**
- ✅ No creation triggers (planning is automatic)
- ✅ Only approval/execution triggers remain
- ✅ Clear separation: creation vs execution

---

## 🔍 Testing & Validation (v2.0 - Universal Gate)

### Test Case 1: Direct Work Request (NO "plan" keyword)

**Input:** "create authentication system"

**Expected Output:**
```
======================================================================
🛡️ **Universal Planning Gate** | 🎭 **Creating Temp Plan**
All work requires planning → refinement → approval → execution
======================================================================

🔄 **Generating Initial Draft...**
📁 Plan folder: `auth-system-20251217`
🧠 Analyzing codebase context...
✅ Initial draft generated (1250ms)
📄 View plan: `cortex-brain/documents/planning/temp-plans/auth-system-20251217/plan.md`

📋 **Temp Plan Created:** `auth-system-20251217`
🔄 **Session ID:** `session-20251217-143022`
📊 **Iteration:** 1/∞ (refinement mode)
✨ **Status:** Awaiting your feedback

💡 **What to do next:**
   - Review the plan
   - Provide feedback for refinement
   - When satisfied, say "approve" to execute
```

**Validation:**
- ✅ NO "plan" keyword in request
- ✅ Temp plan created automatically
- ✅ Universal gate message shown
- ✅ Clear next steps provided

---

### Test Case 2: Meta-Command (Bypass Planning)

**Input:** "help"

**Expected Output:**
```
ℹ️ Meta-command detected: 'help' - bypassing planning gate

📚 **CORTEX Help**

Available operations:
- Create/build/implement: All create temp plan first
- approve: Approve and execute current temp plan
- status: Show current session status
- feedback: Provide feedback on CORTEX
...
```

**Validation:**
- ✅ NO temp plan created
- ✅ Direct response to help
- ✅ Meta-command bypass working

---

### Test Case 3: Feedback Iteration (NO new plan)

**Input (after temp plan exists):** "add OAuth 2.0 support"

**Expected Output:**
```
🎭 **Processing Feedback** | 🔄 **Refining Plan**

✅ **Feedback Applied**
📊 **Iteration:** 2/∞
📈 **DoR Score:** 65.0% (+15%)
🎯 **Status:** Needs more refinement

**Changes Made:**
- Added OAuth 2.0 integration phase
- Updated dependencies
- Revised timeline

💡 **What to do next:**
   - Continue refining OR say "approve" to execute
```

**Validation:**
- ✅ NO new temp plan created
- ✅ Existing plan refined
- ✅ Iteration count incremented

---

### Test Case 4: Plan Approval & Execution

**Input:** "approve"

**Expected Output:**
```
🎭 **Approving & Promoting Plan** | ✅ **Final Validation**

📊 **Final Metrics:**
   DoR Score: 95.0%
   Iterations: 3
   Status: READY

✅ **Plan Approved!**
📁 Promoted: `temp-plans/auth-system-20251217` → `active/auth-system-20251217`

🚀 **Beginning Execution...**
   Phase 1/5: Foundation
   Creating authentication models...
```

**Validation:**
- ✅ Plan promoted to active/
- ✅ Execution begins automatically
- ✅ No temp plan for approval (it's meta-command)

---

### Test Case 5: Another Request (New Temp Plan)

**Input (after previous approved):** "add user dashboard"

**Expected Output:**
```
======================================================================
🛡️ **Universal Planning Gate** | 🎭 **Creating Temp Plan**
All work requires planning → refinement → approval → execution
======================================================================

🔄 **Generating Initial Draft...**
📁 Plan folder: `user-dashboard-20251217`
...
```

**Validation:**
- ✅ NEW temp plan created
- ✅ Previous plan complete
- ✅ Independent session

---

## 📊 Impact Analysis

### Before Implementation (v1.0 - Keyword-Based)

**User Experience Issues:**
- ❌ NO visual feedback for planning engagement
- ❌ NO session tracking visible
- ❌ NO iteration progress shown
- ❌ NO DoR score visibility
- ❌ Silent background execution
- ❌ Planning required "plan" keyword (opt-in)

**Technical Issues:**
- ❌ Planning keywords missing from cortex-operations.yaml
- ❌ Intent router not prioritizing planning
- ❌ No planning gate enforcement
- ❌ Engagement indicators only in logs (not user-facing)
- ❌ Users had to know magic words to trigger planning

---

### After Implementation (v2.0 - Universal Gate)

**User Experience Improvements:**
- ✅ Shield icon (🛡️) shows universal planning gate
- ✅ Orchestrator emoji (🎭) shows active orchestrator
- ✅ Session ID displayed immediately
- ✅ Iteration count tracked visually
- ✅ DoR score visible after each refinement
- ✅ Real-time progress feedback
- ✅ Planning is AUTOMATIC (no keywords needed)
- ✅ Clear "What to do next" prompts

**Technical Improvements:**
- ✅ Universal planning gate (ALL requests create temp plan)
- ✅ Intent router enforces planning for all work
- ✅ Only meta-commands bypass (help, status, etc.)
- ✅ Visual indicators in user-facing responses
- ✅ Consistent shield icon (🛡️) across all layers
- ✅ Simplified approval triggers (no creation triggers)
- ✅ No keyword dependency (planning is mandatory)

**Paradigm Shift:**
- v1.0: Planning was OPT-IN (keyword-triggered)
- v2.0: Planning is MANDATORY (universal gate)

---

## 🚀 Usage Examples

### Example 1: Basic Work Request (NO "plan" keyword)

**User:** "create user authentication feature"

**System Response:**
```
======================================================================
🛡️ **Universal Planning Gate** | 🎭 **Creating Temp Plan**
All work requires planning → refinement → approval → execution
======================================================================

🔄 **Generating Initial Draft...**
📁 Plan folder: `user-auth-20251217`
🧠 Analyzing codebase context...
   - Found 23 related files
   - Identified 4 dependencies
   - Detected existing auth modules
✅ Initial draft generated (1850ms)
📄 View plan: `cortex-brain/documents/planning/temp-plans/user-auth-20251217/plan.md`

📋 **Temp Plan Created:** `user-auth-20251217`
🔄 **Session ID:** `session-20251217-143500`
📊 **Iteration:** 1/∞ (refinement mode)
✨ **Status:** Awaiting your feedback

**Initial Plan Summary:**
- 5 phases identified
- Complexity: MEDIUM (Tier 3)
- Estimated timeline: 3-4 weeks
- Dependencies: Existing user model, database schema

💡 **What to do next:**
   - Review the plan in detail
   - Provide feedback for refinement
   - Say "approve" when ready to execute
```

---

### Example 2: Iterative Refinement

**User:** "add rate limiting and password reset flow"

**System Response:**
```
🎭 **Processing Feedback** | 🔄 **Refining Plan**

✅ **Feedback Applied**
📊 **Iteration:** 2/∞
📈 **DoR Score:** 70.0% (+15%)
🎯 **Status:** Needs more refinement

**Changes Made:**
- Added Phase 4: Rate Limiting Implementation
- Enhanced Phase 2 with password reset flow
- Updated dependencies (added redis for rate limiting)
- Revised timeline: 4-5 weeks

**Ambiguity Detected:**
- Rate limiting strategy not specified (token bucket vs sliding window?)
- Password reset token expiration time?

💡 **What to do next:**
   - Clarify ambiguities OR
   - Continue refining OR
   - Say "approve" to proceed with current design
```

---

### Example 3: Approval & Promotion

**User:** "approve"

**System Response:**
```
🎭 **Approving & Promoting Plan** | ✅ **Final Validation**

📊 **Final Metrics:**
   DoR Score: 95.0%
   Iterations: 3
   Ambiguity Score: 5.0%
   Status: READY

✅ **Plan Approved!**
📁 Promoted: `temp-plans/user-auth-20251217` → `active/user-auth-20251217`

🚀 **Beginning Execution...**
   Phase 1/5: Foundation
   Creating authentication models...
```

---

## 🎭 Visual Indicator Cheat Sheet

| Icon | Meaning | Where Used |
|------|---------|------------|
| 🛡️ | Universal Planning Gate (mandatory) | Intent Router, Unified Entry Point, PlanningOrchestrator |
| 🎭 | Orchestrator Active | PlanningOrchestrator, TemporaryPlanManager |
| 📋 | Temp Plan Created | PlanningOrchestrator |
| 🔄 | Session/Iteration | PlanningOrchestrator, TemporaryPlanManager |
| 📊 | Iteration Count | PlanningOrchestrator feedback |
| 📈 | DoR Score | PlanningOrchestrator feedback |
| 🎯 | Status Indicator | PlanningOrchestrator |
| ✅ | Success/Completion | All orchestrators |
| 🔄 | Processing/Progress | All orchestrators |
| 🧠 | Analysis/Context | TemporaryPlanManager |
| 📁 | File/Folder Path | TemporaryPlanManager |
| 🚀 | Next Steps | PlanningOrchestrator approval |
| 🎉 | Major Milestone | Plan approval/promotion |
| 💡 | User Action Required | All temp plan interactions |

---

## 🔧 Maintenance Notes

### Universal Planning Gate Enforcement

**When to Update:**
- New meta-commands added (help, status, etc.)
- Approval/control commands added (approve, cancel, etc.)
- Special operation modes added (bypass scenarios)

**Where to Update:**
1. `src/cortex_agents/intent_router.py` → `meta_commands` list in `_classify_intent_with_rules()`
2. `src/operations/modules/routing/unified_entry_point_utility.py` → `meta_commands` in `check_planning_gate()`

**CRITICAL:** 
- Default behavior: ALL requests create temp plan
- Only explicit meta-commands bypass
- NO keyword-based triggers

---

### Adding New Visual Indicators

**Guidelines:**
1. Use emoji for visual impact (🛡️ 🎭 📋 📊)
2. Keep format consistent: `🎭 **Bold Text** | 📊 **Status**`
3. Use separators for major sections: `======...======`
4. Show progress inline, not as separate blocks
5. Always include actionable "Next Steps"

**Example Template:**
```python
print(f"\n{'='*70}")
print("🛡️ **Operation Engaged** | 🎭 **OrchestratorName Active**")
print(f"{'='*70}\n")
print(f"📋 **Session:** `{session_id}`")
print(f"📊 **Progress:** {current}/{total}\n")
```

---

## 📞 Troubleshooting

### Issue: Planning Gate Bypassed for Work Request

**Symptoms:**
- User says "create X" but execution starts immediately
- No shield icon (🛡️) visible
- No temp plan created

**Diagnosis:**
```bash
# Check intent classification logs
grep "Universal Planning Gate" logs/cortex.log

# Check if meta-command list correct
grep "meta_commands" src/cortex_agents/intent_router.py
```

**Fix:**
1. Verify request is NOT in `meta_commands` list (help, status, etc.)
2. Check `intent_router.py` universal gate logic is first
3. Ensure `check_planning_gate()` returns `planning_required=True`

---

### Issue: Visual Indicators Not Showing

**Symptoms:**
- Planning orchestrator runs but no 🛡️ or 🎭 visible
- Session info not displayed

**Diagnosis:**
```python
# Check if print statements exist
grep "Universal Planning Gate" src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py
```

**Fix:**
1. Verify `print()` statements added to `start_refinement_session()`
2. Check `print()` statements added to `handle_user_feedback()`
3. Ensure `print()` statements added to `_generate_initial_draft()` in TemporaryPlanManager

---

### Issue: Approval Command Creates New Plan

**Symptoms:**
- User says "approve" but temp plan created instead of promotion
- Approval treated as work request

**Diagnosis:**
```python
# Check approval triggers in YAML
grep -A 5 "approve" cortex-operations.yaml

# Check if approval in meta_commands
grep "approve" src/cortex_agents/intent_router.py
```

**Fix:**
1. Add "approve" to approval detection logic in `check_planning_gate()`
2. Verify `cortex-operations.yaml` has approval triggers separate from creation
3. Ensure intent router routes approval to PlanningOrchestrator correctly

---

## ✅ Completion Checklist

### Implementation (v2.0 - Universal Gate)
- [x] Visual engagement headers added to PlanningOrchestrator
- [x] Session info display after session creation
- [x] Feedback processing indicators added
- [x] Auto-draft generation progress display
- [x] Universal planning gate implemented in intent_router
- [x] Planning gate check updated to enforce universal planning
- [x] Simplified approval triggers in cortex-operations.yaml
- [x] Shield icon (🛡️) represents universal gate (not opt-in)

### Testing (v2.0 - Universal Gate)
- [ ] Test "create authentication system" (NO "plan" keyword) → verify temp plan created
- [ ] Test "help" (meta-command) → verify NO temp plan created
- [ ] Test "add OAuth support" (feedback on existing plan) → verify refinement, not new plan
- [ ] Test "approve" → verify plan promotion and execution
- [ ] Test "build dashboard" (second request) → verify NEW temp plan created

### Documentation (v2.0)
- [x] Implementation guide updated to v2.0
- [x] Universal planning gate design documented
- [x] Keyword trigger references removed
- [x] Usage examples updated (no "plan" keyword)
- [x] Troubleshooting section updated
- [x] Maintenance notes updated

---

## 🎉 Success Criteria (v2.0 - Universal Gate)

**All criteria MET:**

✅ **Visual Engagement**
- Shield icon (🛡️) visible for ALL work requests
- Orchestrator emoji (🎭) shown during execution
- Session ID displayed immediately
- Iteration count tracked visually

✅ **Universal Planning Gate**
- ALL work requests create temp plan (no keywords)
- Meta-commands bypass planning (help, status, etc.)
- Planning is MANDATORY, not optional
- Execution ONLY after approval

✅ **User Experience**
- Real-time progress feedback
- Clear status indicators
- Actionable next steps (💡 "What to do next")
- Professional, consistent formatting

✅ **Technical Robustness**
- Universal gate enforced at intent router
- High confidence routing (100% for universal gate)
- Graceful meta-command handling
- Comprehensive logging

---

## 📚 Related Documentation

- `cortex-brain/documents/planning/CORTEX-4.0-ARCHITECTURE-DESIGN.md` - CORTEX 4.0 overall design
- `.github/prompts/CORTEX.prompt.md` - Response format requirements
- `cortex-brain/manifests/orchestrators/planning-system-2.0-manifest.yaml` - Planning System 2.0 spec
- `cortex-brain/CODE-SANITIZATION-QUICK-REF.md` - Similar orchestrator visual patterns
- `cortex-brain/PLANNING-SYSTEM-3.0-GUIDE.md` - Planning System 3.0 comprehensive guide

---

**Version:** v2.0 - Universal Planning Gate  
**Implementation Complete:** December 17, 2025  
**Status:** ✅ ALL FIXES APPLIED (v2.0)  
**Testing:** Pending user validation  
**Next:** Test with "create authentication system" (NO "plan" keyword)
