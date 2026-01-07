# Root Cause Analysis: Continuation Prompts Not Displaying

**Investigation ID:** INVEST-20260103-150000  
**Author:** Asif Hussain  
**Date:** January 3, 2026  
**Severity:** HIGH  
**Status:** ✅ Root Cause Identified

---

## 🎯 Issue Summary

### Symptom
Continuation prompts are **generated** and **written to files** (`tracking/CONTINUATION-PROMPT.md`), but the user **never sees them in the chat response** when the session approaches token limits.

### User Expectation
When estimated tokens reach 80% of threshold (default 80,000):
1. ✅ System generates continuation prompt file
2. ❌ **System displays warning message in chat:** "⚠️ TOKEN WARNING: Estimated 85,000 tokens..."
3. ❌ **System tells user where to find continuation prompt:** "📋 Continuation prompt updated: `tracking/CONTINUATION-PROMPT.md`"

### Actual Behavior
1. ✅ `check_token_usage()` correctly generates `user_message` field
2. ✅ Orchestrators append `user_message` to their success/completion messages
3. ❌ **Master Orchestrator never renders the message to user**
4. ❌ **User sees generic success message, no token warning**

---

## 🔍 Investigation Trail

### Layer 1: Code Implementation ✅ EXISTS & WORKING

**File:** `src/orchestrators/base/base_orchestrator_v4_1.py`

```python
def check_token_usage(self) -> Dict[str, Any]:
    """Check estimated token usage and return user-facing warning if needed."""
    # ... calculation logic ...
    
    if should_warn:
        result["user_message"] = (
            f"\n\n⚠️ **TOKEN WARNING**: Estimated {estimated_tokens:,} tokens "
            f"({percentage:.1f}% of {self.token_warning_threshold:,} threshold).\n\n"
            f"📋 **Continuation prompt updated**: `tracking/CONTINUATION-PROMPT.md`\n"
            f"💡 **Recommendation**: Consider copying the continuation prompt "
            f"for session handoff to maintain context across chat sessions."
        )
    
    return result  # ✅ user_message field correctly populated
```

**Verdict:** ✅ Base class implementation CORRECT

---

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`

```python
def execute(self, user_request: str, **kwargs) -> OrchestratorResult:
    # ... phase execution ...
    
    # Check token usage and prepare user-facing warning if needed
    token_status = self.check_token_usage()
    success_message = f"Plan '{feature_name}' created successfully"
    
    # Append token warning to message if threshold reached
    if token_status['should_warn'] and token_status.get('user_message'):
        success_message += token_status['user_message']  # ✅ Appending works
    
    return OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        message=success_message,  # ✅ Message includes token warning
        data={...}
    )
```

**Verdict:** ✅ Planning v5 implementation CORRECT

---

**File:** `src/orchestrators/vacuum/vacuum_orchestrator_v2.py`

```python
def execute(self, target_path: str, **kwargs) -> OrchestratorResult:
    # ... phase execution ...
    
    # Check final token usage
    final_token_check = self.check_token_usage()
    completion_message = f"Vacuum completed successfully in {duration:.1f}s"
    
    # Append token warning if threshold reached
    if final_token_check.get('user_message'):
        completion_message += final_token_check['user_message']  # ✅ Appending works
    
    return OrchestratorResult(
        status=OrchestratorStatus.SUCCESS,
        message=completion_message,  # ✅ Message includes token warning
        artifacts=artifacts,
        errors=errors
    )
```

**Verdict:** ✅ Vacuum v2 implementation CORRECT

---

### Layer 2: Configuration/Wiring ❌ **ROOT CAUSE IDENTIFIED**

**File:** `src/orchestrators/master_orchestrator.py`

**PROBLEM:** `handle_request()` method never renders `OrchestratorResult.message` to user.

```python
def handle_request(self, user_input: str, context: dict) -> dict:
    """
    Handle user request by routing to appropriate orchestrator.
    
    Returns:
        dict: Execution result
    """
    # Step 1: Parse user input
    # Step 2: Route to orchestrator
    match = self.route_request(user_input, context)
    
    if not match.is_matched:
        return {"error": "No matching orchestrator found"}
    
    # Step 3: Execute orchestrator
    result = self.execute_orchestrator(
        match.orchestrator_id,
        params={'user_input': user_input, **context}
    )
    
    # ❌ MISSING: Step 4 - Render result.message to user
    # Currently returns raw ExecutionResult, not user-facing markdown
    
    return {
        "orchestrator_id": match.orchestrator_id,
        "status": result.status.value,
        "message": result.message,  # ❌ This dict is INTERNAL, not displayed
        "execution_time": result.execution_time
    }
```

**Evidence:**
1. `execute_orchestrator()` returns `ExecutionResult` object
2. `ExecutionResult` contains nested `OrchestratorResult.message`
3. `handle_request()` returns dict with `message` field
4. **NOWHERE** is this message converted to user-facing markdown
5. **NOWHERE** is response-templates-v4.yaml used for rendering

**Test Case:**
```python
# What happens when Planning v5 returns result with token warning
result = OrchestratorResult(
    status=OrchestratorStatus.COMPLETED,
    message="Plan created successfully\n\n⚠️ TOKEN WARNING: Estimated 85,000 tokens..."
)

# Master Orchestrator returns:
return {
    "status": "completed",
    "message": result.message  # ❌ NOT RENDERED TO USER
}

# User sees: NOTHING (or raw dict, depending on caller)
```

**Verdict:** ❌ **ROOT CAUSE: Missing response rendering pipeline**

---

### Layer 3: Architecture/Design ⚠️ **SYSTEMIC ISSUE**

**Problem:** No standard response rendering pipeline exists in CORTEX v5.

**Current State:**
- Each orchestrator formats its own messages
- Master Orchestrator treats `OrchestratorResult.message` as opaque string
- No integration with `response-templates-v4.yaml`
- No middleware to inject system messages (token warnings, security alerts, etc.)

**Architecture Gap:**
```
User Request → Master Orchestrator → Orchestrator → OrchestratorResult
                                                            ↓
                                                     message="..."
                                                            ↓
                                                    ❌ NO RENDERER
                                                            ↓
                                                    dict with message
                                                            ↓
                                                    ??? (who displays?)
```

**Should Be:**
```
User Request → Master Orchestrator → Orchestrator → OrchestratorResult
                                                            ↓
                                                     message="..."
                                                            ↓
                                        ✅ ResponseRenderer (uses templates)
                                                            ↓
                                        ✅ ResponseMiddleware (injects warnings)
                                                            ↓
                                                 Formatted Markdown
                                                            ↓
                                               Display to User (Chat)
```

**Verdict:** ⚠️ **Architecture incomplete** - response rendering not implemented

---

### Layer 4: System Assumptions ⚠️ **GAP IN EXPECTATIONS**

**Incorrect Assumption:**
- **Developer Thought:** "If I put user_message in OrchestratorResult.message, it will display"
- **Reality:** Master Orchestrator has no display layer, returns dict to unknown caller

**Evidence:**
1. `demo_continuation_prompt.py` **directly prints** the user_message:
   ```python
   result = orchestrator.update_continuation_prompt(...)
   if result:
       print("✅ Continuation prompt generated!")  # Manual display
   ```

2. Test files **assert message content** but don't test **display**:
   ```python
   assert "TOKEN WARNING" in result.message  # ✅ Content exists
   # ❌ But no test verifies user actually sees it
   ```

3. No documentation of **who is responsible for rendering responses**

**Verdict:** ⚠️ **Assumed GitHub Copilot Chat auto-displays OrchestratorResult.message** (incorrect)

---

## 🎯 Root Cause Summary

| Layer | Issue | Severity | Priority |
|-------|-------|----------|----------|
| **Layer 2: Wiring** | Master Orchestrator missing ResponseRenderer integration | 🔴 **CRITICAL** | 🔥 **P0** |
| **Layer 3: Architecture** | No response rendering pipeline system-wide | 🟠 **HIGH** | 🔥 **P1** |
| **Layer 4: Assumptions** | No documentation of response rendering responsibility | 🟡 **MEDIUM** | **P2** |

### PRIMARY ROOT CAUSE
**Master Orchestrator lacks ResponseRenderer integration**

The code correctly generates token warnings, but the Master Orchestrator has no mechanism to convert `OrchestratorResult.message` into user-facing markdown that gets displayed in GitHub Copilot Chat.

---

## 💡 Similar Issues Found (Same Root Cause)

### 1. Error Messages Not Displaying ❌
**File:** All orchestrators  
**Symptom:** When orchestrators return errors in `OrchestratorResult.errors`, user never sees them  
**Root Cause:** Same - no response renderer to format and display errors

### 2. Success Messages Missing Metadata ❌
**File:** Cleanup v2, ADO v2  
**Symptom:** Users don't see file counts, duration, metrics in success messages  
**Root Cause:** Same - orchestrators include metadata in message, but Master Orchestrator doesn't render it

### 3. Warnings from Safety Validators Not Visible ❌
**File:** Vacuum v2, Sanitization v1  
**Symptom:** Safety warnings logged but never displayed to user  
**Root Cause:** Same - warnings in `OrchestratorResult.message`, but no renderer

### 4. Holistic Review Insights Not Injected ❌
**File:** Master Orchestrator (after holistic review auto-trigger)  
**Symptom:** Review insights added to context but never mentioned in response  
**Root Cause:** Same - insights should be rendered as "📋 Review Complete: 8 insights available", but no renderer

---

## 📊 Impact Analysis

### Affected Components
| Component | Impact | Users Affected | Fix Required? |
|-----------|--------|----------------|---------------|
| Planning v5 | High | All users creating plans | ✅ YES |
| Vacuum v2 | High | All users running vacuum | ✅ YES |
| Cleanup v2 | Medium | Users running cleanup | ✅ YES |
| ADO v2 | Medium | Users creating ADO items | ✅ YES |
| Sanitization v1 | Medium | Users sanitizing code | ✅ YES |
| Debug v1 | Low | Few users (manual orchestrator) | ✅ YES |
| Refinement v1 | Low | Few users | ✅ YES |
| TDD v1 | Low | Few users | ✅ YES |
| **Master Orchestrator** | **CRITICAL** | **ALL USERS** | ✅ **YES** |

**Total Affected:** 8 orchestrators + 1 master orchestrator = **9 components**

---

## 🔧 Fix Complexity Analysis

### Option A: Quick Patch (Band-Aid Fix) ⚠️ NOT RECOMMENDED
**Approach:** Add `print(result.message)` in Master Orchestrator  
**Time:** 0.5 hours  
**Pros:** Fast, zero risk  
**Cons:** 
- Not maintainable
- Doesn't solve systemic issue
- Doesn't integrate with response-templates-v4.yaml
- Creates more technical debt

**Verdict:** ❌ **Reject** - band-aid fixes create brittleness

---

### Option B: Architecture Refactor (Proper Fix) ✅ RECOMMENDED
**Approach:** Create ResponseRenderer + ResponseMiddleware + integrate with Master Orchestrator  
**Time:** 6-8 hours  
**Pros:**
- Solves systemic issue
- Integrates response-templates-v4.yaml
- Fixes all 9 components
- Enables future enhancements (theme support, localization, etc.)
- Maintainable

**Cons:**
- Longer implementation time
- Requires testing 9 orchestrators
- Potential breaking changes (mitigated with backward compatibility)

**Verdict:** ✅ **ACCEPT** - proper architecture-level fix

---

### Option C: Hybrid Approach (Pragmatic Fix) 🟡 FALLBACK
**Approach:** ResponseRenderer only (no middleware yet) + Master Orchestrator integration  
**Time:** 3-4 hours  
**Pros:**
- Faster than Option B
- Still architecture-level
- Room for future middleware enhancement
- Fixes all 9 components

**Cons:**
- Defers middleware implementation
- Less comprehensive than Option B

**Verdict:** 🟡 **Acceptable** - if time-constrained

---

## 🎯 Recommended Solution: Option B

**Components to Create:**
1. **ResponseRenderer** (300 lines)
   - Template-driven markdown generation
   - Tier routing (INSTANT → COMPREHENSIVE)
   - Block composition (header, progress, next steps, etc.)
   - Integration with response-templates-v4.yaml

2. **ResponseMiddleware** (150 lines)
   - Post-execution message injection
   - Token warnings
   - Security alerts
   - Deprecation notices
   - Success messages with metadata

3. **Master Orchestrator Integration** (50 lines)
   - Instantiate ResponseRenderer
   - Modify `handle_request()` to render responses
   - Return formatted markdown instead of raw dict

4. **Tests** (400 lines)
   - ResponseRenderer unit tests (15 tests)
   - ResponseMiddleware unit tests (10 tests)
   - Master Orchestrator integration tests (8 tests)
   - End-to-end tests (5 orchestrators × 2 scenarios = 10 tests)

**Total:** ~900 lines code + tests

---

## 📋 Implementation Plan

### Phase 1: Create ResponseRenderer (2h)
**Deliverables:**
- `/src/orchestrators/response_renderer.py` (300 lines)
- Integration with response-templates-v4.yaml
- Unit tests (200 lines)

**Key Methods:**
```python
class ResponseRenderer:
    def render(
        self,
        result: OrchestratorResult,
        tier: str = 'auto',
        context: Dict[str, Any] = None
    ) -> str:
        """Render OrchestratorResult to user-facing markdown"""
    
    def _select_blocks(self, result: OrchestratorResult, tier: str) -> List[str]:
        """Select response blocks based on tier and context"""
    
    def _compose_response(self, blocks: List[Dict], context: Dict) -> str:
        """Compose final markdown from selected blocks"""
```

---

### Phase 2: Create ResponseMiddleware (1h)
**Deliverables:**
- `/src/orchestrators/response_middleware.py` (150 lines)
- Unit tests (100 lines)

**Key Methods:**
```python
class ResponseMiddleware:
    def inject_system_messages(
        self,
        result: OrchestratorResult,
        context: Dict[str, Any]
    ) -> OrchestratorResult:
        """Inject system messages (token warnings, etc.) into result"""
    
    def _inject_token_warning(self, result: OrchestratorResult) -> str:
        """Generate token warning markdown"""
    
    def _inject_security_alerts(self, result: OrchestratorResult) -> str:
        """Generate security alert markdown"""
```

---

### Phase 3: Integrate with Master Orchestrator (1h)
**Deliverables:**
- Modify `/src/orchestrators/master_orchestrator.py` (+50 lines)
- Integration tests (100 lines)

**Changes:**
```python
class MasterOrchestrator:
    def __init__(self, ...):
        # ...existing...
        self.response_renderer = ResponseRenderer(
            template_path="cortex-brain/response-templates-v4.yaml"
        )
        self.response_middleware = ResponseMiddleware()
    
    def handle_request(self, user_input: str, context: dict) -> str:
        # ...existing routing...
        
        # Execute orchestrator
        result = self.execute_orchestrator(match.orchestrator_id, params)
        
        # NEW: Inject system messages (token warnings, etc.)
        enriched_result = self.response_middleware.inject_system_messages(
            result, context
        )
        
        # NEW: Render to user-facing markdown
        markdown_response = self.response_renderer.render(
            enriched_result,
            tier='auto',
            context=context
        )
        
        return markdown_response  # ✅ Now displays to user
```

---

### Phase 4: Update Orchestrators (2h)
**Goal:** Remove manual message appending (now handled by middleware)

**Planning v5:**
```python
# BEFORE (manual appending)
if token_status['should_warn'] and token_status.get('user_message'):
    success_message += token_status['user_message']

# AFTER (middleware handles this)
# Just return success message, middleware injects token warning
return OrchestratorResult(
    status=OrchestratorStatus.COMPLETED,
    message=f"Plan '{feature_name}' created successfully",
    metadata={'token_status': token_status}  # Middleware reads this
)
```

**Vacuum v2:** Same pattern  
**Other orchestrators:** Optional (backward compatible)

---

### Phase 5: Testing (2h)
**Test Coverage:**
- ResponseRenderer: 95% (15 unit tests)
- ResponseMiddleware: 95% (10 unit tests)
- Master Orchestrator integration: 90% (8 tests)
- End-to-end: 100% (10 tests covering all orchestrators)

**Manual Testing:**
1. Planning v5: Create plan, verify token warning displays
2. Vacuum v2: Run vacuum, verify completion message displays
3. All orchestrators: Verify success/error messages display
4. Edge cases: 0 tokens, 150% tokens, missing metadata

---

### Phase 6: Documentation (1h)
**Documents to Update:**
1. `CORTEX.prompt.md` - Add response rendering architecture
2. `response-templates-v4.yaml` - Add ResponseRenderer documentation
3. `master-orchestrator.md` - Document rendering pipeline
4. `BaseOrchestrator.md` - Document message conventions
5. `CHANGELOG.md` - Add breaking changes section (if any)

**New Documents:**
1. `/docs/architecture/response-rendering-pipeline.md` (200 lines)
2. `/docs/guides/creating-orchestrator-messages.md` (150 lines)

---

## ✅ Success Criteria

### Functional Requirements
- ✅ Token warnings display in chat responses
- ✅ Error messages display with formatting
- ✅ Success messages include metadata (duration, file counts, etc.)
- ✅ All orchestrators display messages consistently

### Quality Requirements
- ✅ 95%+ test coverage on new components
- ✅ Zero breaking changes (backward compatible)
- ✅ Response rendering < 10ms (performance)
- ✅ Supports all response template tiers (INSTANT → COMPREHENSIVE)

### Documentation Requirements
- ✅ Architecture document explains rendering pipeline
- ✅ Developer guide for creating orchestrator messages
- ✅ Migration guide for updating existing orchestrators (optional)

---

## 🎓 Lessons Learned

### What Went Wrong
1. **Implicit Assumptions:** Assumed OrchestratorResult.message auto-displays (no display layer documented)
2. **Incomplete Architecture:** Response rendering deferred, causing brittleness
3. **No Integration Testing:** Unit tests verified message content but not display
4. **Fragmented Responsibility:** Each orchestrator formats its own messages (inconsistent)

### What Should Have Been Done
1. **Design Rendering Pipeline First:** ResponseRenderer should have been part of v4.1 architecture
2. **Document Display Responsibility:** Explicitly state "Master Orchestrator renders responses"
3. **Integration Tests:** Test end-to-end flow (user request → display)
4. **Standardize Message Format:** All orchestrators use same conventions

### How to Prevent Similar Issues
1. **Architecture-First:** Design rendering/display layer before orchestrators
2. **Integration Testing:** Always test full user journey
3. **Documentation:** Explicitly document component responsibilities
4. **Code Reviews:** Review for "who displays this?" before merging

---

## 📊 Investigation Statistics

| Metric | Value |
|--------|-------|
| **Investigation Duration** | 2.5 hours |
| **Root Causes Identified** | 3 (Primary + 2 Secondary) |
| **Similar Issues Found** | 4 |
| **Affected Components** | 9 |
| **Proposed Fix Time** | 8 hours |
| **Files to Create** | 4 (ResponseRenderer, ResponseMiddleware, tests, docs) |
| **Files to Modify** | 3 (Master Orchestrator, Planning v5, Vacuum v2) |
| **Test Coverage Target** | 95% |
| **Breaking Changes** | 0 (backward compatible) |

---

## 🔗 Next Steps

1. ✅ **Investigation Complete** - Root cause identified
2. ⏸️ **Await Approval** - Option B (Architecture Refactor) recommended
3. ⏸️ **Design Phase** - Create architecture enhancement proposal
4. ⏸️ **Implementation** - Create ResponseRenderer + ResponseMiddleware + integrate
5. ⏸️ **Testing** - 95%+ coverage, end-to-end validation
6. ⏸️ **Documentation** - Update architecture docs, create guides
7. ⏸️ **Rollout** - Deploy to all orchestrators, verify fix

---

**Investigation Status:** ✅ COMPLETE  
**Root Cause:** Master Orchestrator missing ResponseRenderer integration  
**Recommended Fix:** Option B (Architecture Refactor)  
**Expected Duration:** 8 hours  
**Breaking Changes:** 0  

**Approval Required:** Yes (proceed with Option B implementation?)
