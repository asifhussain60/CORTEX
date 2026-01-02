# User-Facing Token Warning Display

**Status:** ✅ IMPLEMENTED  
**Phase:** 4 - Core Infrastructure Enhancement  
**Date:** 2026-01-02  
**Author:** Asif Hussain

---

## 🎯 Overview

Implemented user-facing display for continuation prompt warnings when chat sessions approach the 80k token threshold. Previously, warnings only appeared in logs - now users see formatted messages directly in chat responses.

---

## 🔧 Implementation

### Modified Files

1. **src/orchestration_4_0/base/base_orchestrator.py** (v4.0)
   - Updated `check_token_usage()` to return `user_message` key
   - Formatted warning message with emojis and markdown
   - Preserved logger.warning() for debugging

2. **src/orchestrators/base/base_orchestrator_v4_1.py** (v4.1)
   - Added `check_token_usage()` method with database integration
   - Added `_estimate_phase_tokens()` helper method
   - Added `token_warning_threshold` configuration support
   - Returns user-facing message when threshold reached

3. **src/orchestrators/planning/planning_orchestrator_v5.py**
   - Integrated token warning into `execute()` workflow
   - Appends user message to `OrchestratorResult.message`
   - Includes token status in result data for debugging

---

## 📋 API Changes

### check_token_usage() Return Value

**Before:**
```python
{
    "estimated_tokens": 5000,
    "threshold": 80000,
    "should_warn": False,
    "percentage": 6.25
}
```

**After:**
```python
{
    "estimated_tokens": 85000,
    "threshold": 80000,
    "should_warn": True,
    "percentage": 106.25,
    "user_message": """

⚠️ **TOKEN WARNING**: Estimated 85,000 tokens (106.2% of 80,000 threshold).

📋 **Continuation prompt updated**: `tracking/CONTINUATION-PROMPT.md`
💡 **Recommendation**: Consider copying the continuation prompt for session handoff to maintain context across chat sessions."""
}
```

---

## 🎨 User Experience

### Display Example

When user reaches token threshold during planning:

```
## 🧠 CORTEX Plan Execution

✅ Plan 'user-authentication' created successfully

⚠️ **TOKEN WARNING**: Estimated 85,000 tokens (106.2% of 80,000 threshold).

📋 **Continuation prompt updated**: `tracking/CONTINUATION-PROMPT.md`
💡 **Recommendation**: Consider copying the continuation prompt for session handoff to maintain context across chat sessions.

**Next:** Review plan in `cortex-brain/documents/planning/active/user-authentication/`
```

---

## 🔍 Technical Details

### Token Estimation Heuristic

**Formula:** `completed_phases × 1000 tokens/phase`

**Rationale:**
- Each phase includes: user request, context analysis, code generation, response
- Average 1000 tokens per phase interaction
- Simple heuristic, sufficient for warning threshold

### Threshold Configuration

**Default:** 80,000 tokens (configurable via manifest)

**BaseOrchestrator v4.0:**
```python
orchestrator = BaseOrchestrator(
    orchestrator_name="planning",
    orchestrator_version="5.0",
    token_warning_threshold=80000  # Constructor parameter
)
```

**BaseOrchestrator v4.1:**
```yaml
# planning-system-5.0-manifest.yaml
execution:
  token_warning_threshold: 80000
```

### Warning Trigger

**Condition:** `estimated_tokens >= token_warning_threshold`

**Actions:**
1. Create formatted user message with emojis/markdown
2. Log warning to logger (debugging)
3. Return user_message in check_token_usage() result
4. Orchestrator appends to response message

---

## 🧪 Testing

### Test Suite

**File:** `tests/test_token_warning_display.py`

**Coverage:**
- ✅ Below threshold (no warning)
- ✅ At threshold (warning triggered)
- ✅ Above threshold (warning triggered)
- ✅ No plan context (no warning)
- ✅ Database integration (v4.1)
- ✅ Message formatting (emojis, markdown)
- ✅ Integration with PlanningOrchestratorV5

**Run Tests:**
```bash
pytest tests/test_token_warning_display.py -v
```

### Demo Script

**File:** `demo_token_warning_display.py`

**Demonstrates:**
- Token monitoring during phase execution
- Warning trigger at 5k threshold (demo)
- User-facing message display
- Implementation details

**Run Demo:**
```bash
python demo_token_warning_display.py
```

---

## 🔄 Integration with Phase 4.5

This feature naturally integrates with **Phase 4.5: Cross-Session Context Middleware**:

1. **Token Warning** → User sees chat approaching limit
2. **Continuation Prompt** → User copies handoff instructions
3. **New Session** → User provides continuation prompt
4. **Context Middleware** → Detects continuation, enriches with Tier 1 metadata
5. **Seamless Handoff** → Context preserved across sessions

---

## 📊 Before/After Comparison

| Aspect | Before | After |
|--------|--------|-------|
| **User Awareness** | ❌ No visibility | ✅ Clear warning in chat |
| **Warning Location** | Logs only | Chat response + logs |
| **Message Format** | Plain text | Markdown with emojis |
| **Actionable Guidance** | None | Link to continuation prompt |
| **Session Management** | Manual tracking | Automated warning + prompt |

---

## 🚀 Usage for Other Orchestrators

All orchestrators inheriting from BaseOrchestrator v4.0/v4.1 can use this feature:

```python
def execute(self, user_request: str, **kwargs) -> OrchestratorResult:
    """Execute orchestrator with token warning display."""
    
    # ... orchestrator logic ...
    
    # Check token usage before returning
    token_status = self.check_token_usage()
    
    success_message = "Operation completed successfully"
    
    # Append token warning if threshold reached
    if token_status['should_warn'] and token_status.get('user_message'):
        success_message += token_status['user_message']
    
    return OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        message=success_message,
        data={'token_status': token_status}  # Optional debugging info
    )
```

---

## 📝 Configuration

### Enable/Disable Warnings

**v4.0 (Constructor):**
```python
orchestrator = BaseOrchestrator(
    token_warning_threshold=0  # Disable warnings
)
```

**v4.1 (Manifest):**
```yaml
execution:
  token_warning_threshold: 0  # Disable warnings
```

### Adjust Threshold

For testing or different use cases:

```yaml
execution:
  token_warning_threshold: 5000  # Warn at 5k tokens (demo)
```

---

## 🎉 Benefits

1. **User Visibility** - Users see when session approaching limit
2. **Proactive Management** - Time to copy continuation prompt
3. **Context Preservation** - Enables seamless session handoffs
4. **Clear Guidance** - Links to continuation prompt file
5. **Debug Support** - Token status in result data
6. **Consistent UX** - All orchestrators inherit feature

---

## 🔗 Related Documentation

- `cortex-brain/response-templates-v4.yaml` - Response formatting
- `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml` - Configuration
- `tracking/CONTINUATION-PROMPT.md` - Session handoff instructions
- Phase 4.5 specification in `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-MASTER-PLAN-V5.md`

---

**Status:** ✅ Complete | **Phase 4 Enhancement** | **2026-01-02**
