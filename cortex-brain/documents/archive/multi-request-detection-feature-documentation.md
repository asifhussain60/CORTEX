# Multi-Request Detection Feature Documentation

**Feature:** Multi-Request Detection  
**Location:** Previously in `src/cortex_agents/strategic/intent_router.py`  
**Status:** Removed with router consolidation (December 4, 2025)  
**Reason:** Strategic router consolidated into main router; feature not ported

---

## 🎯 Feature Overview

Multi-request detection was an automatic feature in the strategic intent router that identified when users requested multiple actions in a single message and automatically routed them to the planning workflow.

---

## 🔍 Detection Patterns

The feature looked for these patterns in user messages:

### Pattern 1: Conjunction with "and"
```
"fix the auth bug and add a dashboard and investigate performance"
```
**Detection:** Multiple action verbs joined by "and"

### Pattern 2: Comma-separated actions
```
"implement login, create tests, update documentation"
```
**Detection:** Multiple action verbs separated by commas

### Pattern 3: Plus operator
```
"debug the API plus refactor the database"
```
**Detection:** Multiple actions joined with "plus"

---

## 🛠️ Implementation Details

### Method: `_detect_multi_request(message: str) -> bool`

**Purpose:** Analyze user message for multiple distinct requests

**Algorithm:**
1. Normalize message (lowercase, remove punctuation)
2. Split on conjunctions ("and", "plus") and commas
3. Count action verbs in each segment
4. Return `True` if 2+ action segments detected

**Action Verbs Recognized:**
- fix, debug, investigate, analyze
- add, create, implement, build
- update, modify, refactor, optimize
- test, validate, verify
- deploy, publish, release

### Integration: `_classify_intent(request: AgentRequest) -> IntentType`

**Routing Logic:**
```python
if self._detect_multi_request(request.user_message):
    return IntentType.PLAN  # Auto-route to planning workflow
```

---

## 📊 Test Coverage

**File:** `tests/test_ux_enhancements_integration.py`

### Test Suite: `TestMultiRequestDetection`

**5 Tests (All Skipped After Feature Removal):**

#### 1. `test_single_request_not_detected`
**Purpose:** Verify single actions don't trigger detection  
**Input:** "fix the authentication bug"  
**Expected:** `False` (not multi-request)

#### 2. `test_multi_request_with_and`
**Purpose:** Detect requests joined by "and"  
**Input:** "fix the auth bug and add a dashboard and investigate performance"  
**Expected:** `True` (multi-request detected)

#### 3. `test_multi_request_with_comma`
**Purpose:** Detect comma-separated requests  
**Input:** "implement login, create tests, update documentation"  
**Expected:** `True` (multi-request detected)

#### 4. `test_multi_request_with_plus`
**Purpose:** Detect requests with "plus"  
**Input:** "debug the API plus refactor the database"  
**Expected:** `True` (multi-request detected)

#### 5. `test_classify_intent_returns_plan_for_multi_request`
**Purpose:** Verify auto-routing to PLAN intent  
**Input:** "fix auth and add dashboard and test performance"  
**Expected:** `IntentType.PLAN`

---

## 🎯 Use Cases Supported

### Before Removal (Automatic)
**User:** "fix the auth bug and add a dashboard"  
**System:** *Automatically detects multi-request*  
**Routing:** → Planning workflow (DoR/DoD validation)

### After Removal (Manual)
**User:** "fix the auth bug and add a dashboard"  
**System:** *Routes as general request*  
**Routing:** → May execute immediately or use LLM classification

**Explicit Planning Still Available:**
**User:** "plan to fix auth and add dashboard"  
**System:** *"plan" keyword triggers planning*  
**Routing:** → Planning workflow

---

## 📈 Impact Analysis

### Benefits of Feature
- ✅ Automatic complex task detection
- ✅ Prevented rushed multi-step implementations
- ✅ Enforced planning for compound work

### Removal Impact
- ⚠️ Users must explicitly say "plan" for planning workflow
- ⚠️ Simple multi-requests may execute without planning
- ✅ Main router still supports planning via explicit intent
- ✅ LLM can still detect complexity and suggest planning

### Mitigation
**Current Alternative:**
- Users can explicitly use "plan" keyword
- Main router's LLM classification may still detect complexity
- Planning workflow fully functional, just not auto-triggered

---

## 🔄 Re-Implementation Guidance

If multi-request detection needs to be restored to main router:

### Step 1: Port Detection Method
Add to `src/cortex_agents/intent_router.py`:
```python
def _detect_multi_request(self, message: str) -> bool:
    """Detect if message contains multiple distinct requests."""
    # Implementation from strategic router
    action_verbs = ['fix', 'debug', 'add', 'create', 'implement', ...]
    conjunctions = ['and', 'plus', ',']
    
    # Normalize and split
    normalized = message.lower()
    segments = self._split_on_conjunctions(normalized, conjunctions)
    
    # Count action verbs per segment
    action_count = sum(
        1 for segment in segments 
        if any(verb in segment for verb in action_verbs)
    )
    
    return action_count >= 2
```

### Step 2: Integrate with Classification
Modify `_classify_intent()` in main router:
```python
def _classify_intent(self, request: AgentRequest) -> IntentType:
    # Early check for multi-request
    if self._detect_multi_request(request.user_message):
        self.logger.info("Multi-request detected - routing to planning")
        return IntentType.PLAN
    
    # Continue with existing classification logic
    ...
```

### Step 3: Restore Tests
Un-skip the 5 tests in `test_ux_enhancements_integration.py`

### Step 4: Update Documentation
- Add feature to main router capabilities
- Update user docs to mention automatic planning triggers

---

## 📝 Removal Justification

**Why Removed:**
1. **Router Consolidation:** Strategic router eliminated (766 lines)
2. **Low Usage:** Feature rarely documented or highlighted
3. **Alternative Available:** Users can explicitly trigger planning
4. **Complexity:** NLP detection adds complexity to main router
5. **LLM Capability:** Modern LLMs can suggest planning when appropriate

**Acceptable Trade-off:**
- ✅ 766 lines removed (45% code reduction)
- ✅ Single router implementation maintained
- ✅ Planning workflow still accessible
- ⚠️ Slightly more user effort for complex requests

---

## 🎓 Lessons Learned

1. **Implicit vs Explicit:** Auto-magic features need clear documentation
2. **Alternative Paths:** If removing automation, ensure manual path exists
3. **Test as Documentation:** Skipped tests preserve feature knowledge
4. **Incremental Features:** Can always re-add if user feedback demands it

---

## 📅 Timeline

- **Created:** Unknown (part of strategic router)
- **Last Active:** December 4, 2025 (strategic router consolidation)
- **Removed:** December 4, 2025 (router consolidation)
- **Tests Skipped:** December 4, 2025
- **Documented:** December 4, 2025 (this file)

---

## ✅ Documentation Complete

This file serves as historical reference for the multi-request detection feature. Tests remain skipped in codebase as living documentation of removed functionality.
