# CORTEX Prompt Migration: v6.0 → v7.0

**Date:** 2026-01-11  
**Author:** Asif Hussain  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Why v7.0 Was Needed

### Problems Identified in chat01.md

**Issue 1: Cramped Single-Paragraph Style**
```
❌ AC-LIFECYCLE-001 complete (10/10 tests passing) → Phase 1 now 70% (23/33) → 
Implementing AC-LIFECYCLE-002 AC-ID assignment → Executing now... [command] → 
AC-LIFECYCLE-002 complete (152/152 tests passing) → Phase 1 now 73% (24/33) → 
Implementing AC-LIFECYCLE-003 next...
```

**Why this happened:**
- v6.0 said "concise response format" but didn't enforce readability
- Used arrows (→) to chain multiple updates
- Result: unreadable run-on paragraphs

**v7.0 Solution:**
- Explicit format rules with ✅/❌ examples
- Enforces line breaks between logical sections
- Shows exactly what "concise and readable" means

---

**Issue 2: Presenting Options Instead of Deciding**
```
❌ Phase 1 complete at 97%.
Ready to proceed to Phase 2 or address remaining issues?
```

**Why this happened:**
- v6.0 said "autonomous execution" but still trained Copilot to present choices
- "Next Steps" sections implied asking permission
- No clear decision tree for what to do next

**v7.0 Solution:**
- Explicit decision tree: state → decide → execute → loop
- NO options presented: "YOU DECIDE and execute"
- Phase transition logic: automatic at 95%+ completion

---

**Issue 3: Stopping Between Phases**
```
❌ Phase 1 complete (97%). Ready for Phase 2 Orchestration Core or final progress update?
```

**Why this happened:**
- v6.0 didn't have phase chaining logic
- Copilot treated each phase as separate task requiring approval
- No strategic awareness of overall plan

**v7.0 Solution:**
- Phase transition is automatic (no asking)
- Strategic planning section with full phase map
- "When to stop" explicitly defined (only 3 conditions)

---

**Issue 4: No Master Orchestrator Logic**
```
❌ v6.0 said "You are a routing proxy + context guardian"
```

**Why this happened:**
- v6.0 was designed as a router to Python orchestrators
- But Python MasterOrchestrator isn't ready yet
- Result: no strategic decision-making, just command execution

**v7.0 Solution:**
- "YOU ARE the MasterOrchestrator until Python version ready"
- Built-in strategic planning with phase awareness
- Clear mental model: persistent execution loop
- Will transition back to lightweight router when Python proven

---

## 📊 Structural Differences

### v6.0 Architecture
```
User Request
    ↓
Copilot (Router)
    ↓
Python Orchestrators (Decision-makers)
    ↓
Execution
```

**Problem:** Python orchestrators aren't fully autonomous yet, so Copilot stops and asks.

### v7.0 Architecture
```
User Request
    ↓
Copilot (Master Orchestrator)
    ├─ Load State
    ├─ Decide Next Action
    ├─ Execute via Python Tools
    ├─ Report Outcome
    └─ Loop Automatically
```

**Benefit:** Copilot makes strategic decisions, chains phases, doesn't stop.

---

## 🔄 Key Changes Detail

### 1. Identity Shift

**v6.0:**
> You are a routing proxy + context guardian

**v7.0:**
> You ARE the MasterOrchestrator until the Python version is ready.
> You don't route to orchestrators - YOU ARE the orchestrator.

### 2. Decision Tree Added

**v6.0:** No explicit decision logic (relied on Python)

**v7.0:** Clear 4-step decision tree
```python
if planned_ac_ids:
    next_action = f"implement {planned_ac_ids[0]}"
elif partial_ac_ids:
    next_action = f"fix {partial_ac_ids[0]}"
elif percent >= 95:
    next_action = f"start phase {next_phase_num}"
else:
    next_action = "verify phase completion"
```

### 3. Response Format Enforcement

**v6.0:** Said "concise" but showed conflicting examples

**v7.0:** Explicit ✅ CORRECT vs ❌ WRONG examples
- Readable format with line breaks
- Cramped paragraph explicitly forbidden
- Verbose sections explicitly forbidden

### 4. Phase Awareness

**v6.0:** No phase map or strategic awareness

**v7.0:** Built-in phase definitions
```python
PHASES = {
    1: {"name": "Foundation", "ac_count": 33, "critical_path": [...]},
    2: {"name": "Orchestration Core", "ac_count": 24, ...},
    3: {"name": "Feature Orchestrators", "ac_count": 16, ...},
    4: {"name": "Intelligence Layer", "ac_count": 12, ...}
}
```

### 5. Stopping Conditions

**v6.0:** Vague ("continue until blocked")

**v7.0:** Exactly 3 conditions
1. Phase 100% complete AND next phase not defined
2. Blocker cannot be auto-fixed
3. User explicitly says "stop" or "pause"

### 6. Phase Transition Logic

**v6.0:** Not specified (resulted in asking permission)

**v7.0:** Automatic at 95%+ completion with example
```
Phase 1 now 97% (32/33 AC-IDs).
1 partial AC-ID non-blocking.

Phase 1 substantially complete.
Starting Phase 2 Orchestration Core...

Phase 2: 24 AC-IDs (MasterOrchestrator, TodoManager, TDD-Master, Planning v5).

Implementing AC-ORCH-006...
```

---

## 📝 Content Organization

### v6.0 Structure (462 lines)
- Core Principle
- Response Format (conflicting examples)
- Autonomous Execution Loop (too abstract)
- Anti-Patterns (deprecated templates)
- State Management
- Test-Gated Execution
- Intent Routing
- File Organization
- Automatic Maintenance
- Debugging
- Examples (limited)
- Evolution & Design Principles

**Problem:** Mixed router logic with execution logic, unclear on what Copilot should actually DO.

### v7.0 Structure (new)
- YOUR IDENTITY (who you are)
- EXECUTION MODEL (state → decide → execute → loop)
- RESPONSE FORMAT RULES (explicit ✅/❌ examples)
- PHASE TRANSITION LOGIC (automatic chaining)
- HANDLING FAILURES (don't block on failures)
- STRATEGIC PLANNING INTEGRATION (phase awareness)
- PLAN ALIGNMENT CHECKS (self-maintenance)
- COMMAND EXECUTION (how to invoke tools)
- PROGRESS TRACKING (how to update state)
- STOPPING CONDITIONS (exactly when to stop)
- EXAMPLES (comprehensive scenarios)
- ANTI-PATTERNS (explicit don'ts)
- SELF-MAINTENANCE (automatic checks)
- YOUR MENTAL MODEL (execution loop pseudocode)
- INTEGRATION WITH EXISTING CORTEX
- QUICK REFERENCE (TL;DR)

**Benefit:** Clear progression from identity → decision-making → execution → reporting → looping.

---

## 🎓 Usage Changes

### v6.0 Usage
```
User: "proceed with plan autonomously"
Copilot: [executes one AC-ID]
Copilot: "AC-XYZ-001 complete. Ready to continue?"
User: "continue"
Copilot: [executes next AC-ID]
Copilot: "AC-XYZ-002 complete. Should I proceed to next?"
[repeat approval loop]
```

### v7.0 Usage
```
User: "continue"
Copilot: [loads state silently]
Copilot: Phase 1 at 67% (22/33 AC-IDs).

Implementing AC-LIFECYCLE-001...
[executes]
AC-LIFECYCLE-001 complete.
Tests: 10/10 passing.
Phase 1 now 70%.

Implementing AC-LIFECYCLE-002...
[executes]
AC-LIFECYCLE-002 complete.
Tests: 152/152 passing.
Phase 1 now 73%.

Implementing AC-LIFECYCLE-003...
[continues until phase complete]

Phase 1 complete at 97%.
1 partial AC-ID non-blocking.

Starting Phase 2 Orchestration Core...
[continues automatically into Phase 2]
```

**Difference:** Single "continue" command → full phase completion + automatic phase transition.

---

## 🔧 Implementation Changes

### File Changes Made

1. **Created:** `.github/prompts/CORTEX-v7.prompt.md`
   - Complete rewrite from scratch
   - Acts as master orchestrator, not router
   - Strategic planning built in

2. **Updated:** `.github/prompts/CORTEX.prompt.md`
   - Added deprecation notice
   - Points to v7
   - v6 content archived in same file

3. **Updated:** `.github/copilot-instructions.md`
   - Entry point now references v7
   - Updated philosophy statement
   - Added v7 changes summary

4. **Created:** `.github/prompts/MIGRATION-v6-to-v7.md` (this file)
   - Documents why change was needed
   - Shows structural differences
   - Provides before/after examples

---

## ✅ Expected Behavior Changes

### Before (v6.0)
1. Copilot executes single AC-ID
2. Copilot reports result with cramped arrows
3. Copilot asks "Ready to continue?" or presents options
4. User says "continue"
5. Repeat steps 1-4 for each AC-ID
6. At phase end: "Phase complete. Ready for Phase 2?"
7. User says "yes"
8. Repeat for next phase

**Total user interactions per phase:** ~20-30 approvals

### After (v7.0)
1. User says "continue" ONCE
2. Copilot:
   - Loads state
   - Implements all planned AC-IDs in phase
   - Reports each completion (readable format)
   - Fixes failures and continues
   - Transitions to next phase automatically
   - Repeats for all phases
3. Stops only when:
   - All phases complete
   - Real blocker requiring user action
   - User says "stop"

**Total user interactions per phase:** 1 (or 0 if already running)

---

## 🧪 Testing the Migration

### Test Case 1: Single Phase Completion
```
Given: Phase 1 at 67% (7 AC-IDs remaining)
When: User says "continue"
Then: 
  - All 7 AC-IDs implemented without stopping
  - Phase marked 100% complete
  - Phase 2 starts automatically
  - No "Ready to continue?" questions
```

### Test Case 2: Readable Output Format
```
Given: Any implementation
When: AC-ID completes
Then:
  - Output uses line breaks (not arrows)
  - One fact per line
  - Next action stated explicitly
  - No asking permission
```

### Test Case 3: Failure Handling
```
Given: AC-ID implementation fails tests
When: Failure detected
Then:
  - Mark as partial
  - Report briefly (1-2 lines)
  - Continue to next AC-ID immediately
  - No blocking on failure
```

### Test Case 4: Phase Transition
```
Given: Phase at 97% (1 partial AC-ID)
When: Last AC-ID completes
Then:
  - Note partial as non-blocking
  - Start next phase automatically
  - No "Ready for Phase X?" question
```

---

## 📈 Success Metrics

**Before (v6.0 issues):**
- User saying "continue" 20-30 times per phase
- Cramped unreadable paragraphs
- Stopping at phase boundaries
- Presenting multiple options

**After (v7.0 success):**
- ✅ User says "continue" once, entire phase completes
- ✅ Readable output with line breaks
- ✅ Automatic phase transitions
- ✅ No options presented (autonomous decisions)
- ✅ Clear progress visibility (% and counts)

---

## 🔮 Future Evolution

### When Python MasterOrchestrator is Ready

1. v7 prompt becomes lightweight router again
2. Python handles:
   - State loading
   - Decision tree
   - Strategic planning
   - Progress tracking
3. Copilot just:
   - Invokes Python MasterOrchestrator
   - Displays output
   - Continues loop

### But Core Principles Remain
- Autonomous execution (no approval loops)
- Readable format (line breaks, not arrows)
- Automatic phase chaining
- Strategic awareness
- Clear stopping conditions

**v7 establishes the behavior model that Python will eventually implement.**

---

## 📚 References

- **Original prompt:** `.github/prompts/CORTEX.prompt.md` (now v6 archived)
- **New prompt:** `.github/prompts/CORTEX-v7.prompt.md`
- **Context file:** `.github/copilot-instructions.md`
- **Evidence:** `.cortex/chats/chat01.md` (shows v6 issues)

---

## 🎯 Summary

**The Problem:** v6.0 said "autonomous" but trained Copilot to present options and stop for approval.

**The Root Cause:** Prompt was designed as router to Python orchestrators that aren't ready yet.

**The Solution:** v7.0 makes Copilot the master orchestrator with strategic planning, decision tree, automatic phase chaining, and readable output format.

**The Result:** True autonomous execution - user says "continue" once, system completes entire phase(s) without stopping.

**The Future:** When Python MasterOrchestrator is proven, v7 prompt becomes lightweight router again, but the autonomous execution principles remain.

---

**Version History:**
- v6.0 (2026-01-10): Autonomous execution gateway (router pattern)
- v7.0 (2026-01-11): Autonomous master orchestrator (decision-maker pattern)

**Status:** v7.0 active, v6.0 archived
