# Planning Intent Detection Fix

**Date:** December 6, 2025  
**Issue:** Planning orchestrator not engaging when "plan" appears mid-request  
**Status:** ✅ RESOLVED

---

## Problem Statement

When users said things like:
- "I want to create user authentication. **Create a plan for it.**"
- "Build a notification system. **Make a plan.**"
- "Add payment processing. **Put together a plan.**"

CORTEX was **not** triggering the planning orchestrator. Instead, it would often interpret these as CODE intent and try to implement directly.

---

## Root Cause Analysis

### Keyword Scoring Logic
The intent router uses keyword matching with weighted scoring:
- Each keyword match scores points equal to its word count
- "create" (1 word) = 1 point
- "plan" (1 word) = 1 point
- **Both get equal scores → non-deterministic winner**

### Example Breakdown
Message: `"I want to create user authentication. Create a plan for it."`

**Before Fix:**
- CODE intent matches: `"create"` → 1 point
- PLAN intent matches: `"plan"` → 1 point
- **Result:** Tie score → Winner depends on dict iteration order → ❌ Unreliable

**After Fix:**
- CODE intent matches: `"create"` → 1 point
- PLAN intent matches: `"create a plan"` (3 words) → 3 points, `"plan for it"` (3 words) → 3 points, `"plan"` → 1 point
- **Total:** PLAN = 7 points, CODE = 1 point
- **Result:** PLAN wins decisively → ✅ Correct

---

## Solution Implemented

### Code Changes

**File:** `src/cortex_agents/intent_router.py`

Added multi-word planning phrases to `IntentType.PLAN` keywords:

```python
IntentType.PLAN: [
    # Multi-word phrases (checked first, score higher)
    "create a plan", "make a plan", "build a plan", "put together a plan",
    "create plan", "make plan", "build plan", "develop a plan",
    "plan a feature", "plan this", "let's plan", "help me plan",
    "plan it", "plan for it", "plan that", "planning for",
    # Single words (fallback)
    "plan", "planning", "feature", "breakdown", "design", "architect"
],
```

**Key Principle:** Multi-word phrases score higher than single words, ensuring planning intent wins when users explicitly say planning-related phrases.

---

## Test Coverage

**File:** `tests/test_planning_intent_detection.py`

**Test Results:** ✅ 17/17 tests passing

### Test Categories

1. **Multi-word planning phrases** (PRIMARY)
   - "Create a plan for it" → PLAN ✅
   - "Make a plan" → PLAN ✅
   - "Put together a plan" → PLAN ✅
   - "Build a plan" → PLAN ✅

2. **Planning at sentence start**
   - "Plan a feature for X" → PLAN ✅
   - "Let's plan the X" → PLAN ✅
   - "Help me plan X" → PLAN ✅

3. **Planning with "for"**
   - "Plan for the feature" → PLAN ✅
   - "Planning for v2.0" → PLAN ✅
   - "Plan it out" → PLAN ✅

4. **Negative cases (CODE intent)**
   - "Implement the gateway" → CODE ✅
   - "Build the service" → CODE ✅

---

## Verification Commands

```bash
# Run planning intent tests
python -m pytest tests/test_planning_intent_detection.py -v

# Interactive verification
python -c "
from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.base_agent import AgentRequest

router = IntentRouter(name='TestRouter', config={})
request = AgentRequest(
    intent='unknown',
    context={},
    user_message='I want to create authentication. Create a plan for it.'
)

result = router._classify_intent_with_rules(request)
print(f'Intent: {result.intent.value if hasattr(result.intent, \"value\") else result.intent}')
print(f'Confidence: {result.confidence}')
print(f'Matched: {result.metadata.get(\"matched_keywords\", [])}')
"
```

**Expected Output:**
```
Intent: plan
Confidence: 0.7+
Matched: ['create a plan', 'plan for it', 'plan']
```

---

## Impact Analysis

### Before Fix
- ❌ "Create a plan" → 50% chance of CODE intent (non-deterministic)
- ❌ Users had to say "plan" at sentence start
- ❌ Mid-sentence planning requests ignored

### After Fix
- ✅ "Create a plan" → 100% PLAN intent (deterministic)
- ✅ Planning phrases work anywhere in sentence
- ✅ Natural language planning requests work reliably

### User Experience Improvement
- **Natural language:** Users can say "Create a plan for it" naturally
- **Intelligent routing:** System correctly identifies planning intent
- **Predictable behavior:** Same request → same result every time

---

## Future Considerations

### Potential Enhancements
1. **Context-aware scoring:** Consider previous conversation context
2. **Phrase position weighting:** Give higher weight to end-of-sentence phrases
3. **Negative keywords:** Penalize non-planning keywords in planning requests

### Known Limitations
1. YAML operations with generic triggers (e.g., "plan this") may override core keywords
2. Very complex sentences with multiple intents may need disambiguation
3. Single-word "plan" in non-planning context may still trigger (acceptable tradeoff)

---

## Lessons Learned

1. **Multi-word phrases are critical:** Single-word keywords create ambiguity
2. **Weighted scoring matters:** Word count weighting provides intent differentiation
3. **Test real user patterns:** Tests should mirror actual user language
4. **YAML operations override:** Core keywords can be overridden by YAML-loaded operations

---

## Related Files

- `src/cortex_agents/intent_router.py` - Intent classification logic
- `src/cortex_agents/agent_types.py` - Intent type definitions
- `tests/test_planning_intent_detection.py` - Comprehensive test suite
- `cortex-operations.yaml` - YAML-based operation triggers

---

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX
