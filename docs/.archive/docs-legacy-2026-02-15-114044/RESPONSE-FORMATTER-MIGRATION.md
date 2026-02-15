# Response Formatter Migration Guide
**Version:** 1.0 | **Date:** 2026-02-13 | **Authority:** Phase 53 Simplification

---

## Quick Start (5 minutes)

### Before (Deprecated)
```python
from cortex.agents.core.response_template_generator import ResponseTemplate

response = ResponseTemplate.session_summary(
    session_name="WAVE-1",
    completed_items=["Feature X", "Tests"],
    in_progress_items=[],
    blocked_items=[],
    next_steps=["Deploy"],
    token_usage=(150, 200)
)
```

### After (Recommended)
```python
from cortex.orchestrators.response.simple_response_formatter import format_response

response = format_response(
    title="WAVE-1 Complete",
    status="COMPLETE",
    sections=[
        {"title": "Work Done", "items": ["Feature X", "Tests"]}
    ],
    metrics={"Token Usage": "150k/200k (75%)"},
    next_steps=["Deploy"]
)
```

**Result:** Same clarity, 80% less code to understand.

---

## Migration Checklist

### For Orchestrators Using `ResponseTemplate`

**Files to check:**
- `cortex/orchestrators/core/master_orchestrator.py`
- `cortex/orchestrators/core/intent_router.py`
- `cortex/orchestrators/core/tdd_orchestrator.py`
- `cortex/orchestrators/domain/refactoring_orchestrator.py`

**Migration steps:**
1. ✅ Import simple formatter: `from cortex.orchestrators.response.simple_response_formatter import format_response`
2. ✅ Replace `ResponseTemplate.*` calls with `format_response(...)`
3. ✅ Test output in Copilot Chat
4. ✅ Commit with AC marker

**Timeline:** Optional, no deadline (backward compatible)

---

## Feature Mapping

| Old Feature | New Equivalent | Notes |
|-------------|----------------|-------|
| `session_summary()` | `format_response(title, sections, metrics, next_steps)` | More flexible |
| `create_header()` | Built into title param | Emoji auto-detected from status |
| Status color detection | `status` param | Explicit: "COMPLETE", "IN_PROGRESS", "BLOCKED" |
| Token usage formatting | metrics dict | `{"Token Usage": "150k/200k"}` |
| Completed items | sections[0]["items"] | `{"title": "Done", "items": [...]}` |
| In-progress items | sections[1]["items"] | `{"title": "In Progress", "items": [...]}` |
| Blocked items | sections[2]["items"] | `{"title": "Blocked", "items": [...]}` |
| Next steps | next_steps param | Direct pass-through |

---

## Examples

### Example 1: Simple Completion
```python
response = format_response(
    title="Implementation Complete",
    status="COMPLETE"
)
```

**Output:**
```
----------------------------------------
✅ Implementation Complete
----------------------------------------

----------------------------------------
```

### Example 2: With Metrics
```python
response = format_response(
    title="WAVE-1: Foundation Complete",
    status="COMPLETE",
    metrics={
        "Progress": 100,
        "Tests": "90/90",
        "Duration": "3 hours"
    }
)
```

**Output:**
```
----------------------------------------
✅ WAVE-1: Foundation Complete
----------------------------------------

[██████████] 100%

## Metrics

**Tests:** 90/90
**Duration:** 3 hours

----------------------------------------
```

### Example 3: Full Response
```python
response = format_response(
    title="WAVE-2: Scaffolder Integration",
    status="IN_PROGRESS",
    sections=[
        {
            "title": "Work Completed",
            "items": [
                "Demand generator wired",
                "Test composer integrated",
                "Quality validator enabled"
            ]
        },
        {
            "title": "Test Results",
            "table": {
                "headers": ["Component", "Tests", "Status"],
                "rows": [
                    ["Demand Generator", "16/16", "✅ Pass"],
                    ["Test Composer", "21/21", "✅ Pass"],
                    ["Quality Validator", "22/22", "✅ Pass"]
                ]
            }
        }
    ],
    metrics={
        "Progress": 60,
        "Tests": "59/59",
        "Duration": "2 hours so far"
    },
    next_steps=[
        "Complete Stage 4 integration tests",
        "Proceed to WAVE-3"
    ]
)
```

**Output:** Full chat01.md style response with headers, tables, progress bar, metrics, and next steps.

---

## FAQ

**Q: Do I need to migrate immediately?**  
A: No. Existing code continues working. Migrate when convenient.

**Q: What if I like `ResponseTemplate.create_header()`?**  
A: Keep using it! It's not removed, just deprecated. Or switch to `format_response(title=...)` for consistency.

**Q: Can I mix both approaches?**  
A: Yes, but not recommended. Pick one for consistency.

**Q: What about `ResponseHeaderInjector`?**  
A: Keep using it. That's for system-level headers (metadata), not response formatting.

**Q: What about `BLUFTemplateEngine`?**  
A: Keep using it. That's for user interaction (questions/answers), not orchestrator responses.

**Q: Why was ENH-082 superseded?**  
A: After holistic review, 8-11 days of work for formatting was overengineering. Simple solution achieves same user goal in 30 minutes.

---

## Testing

### Before Migration
```python
# Run existing tests
pytest tests/unit/agents/test_response_template_generator.py
```

### After Migration
```python
# Test simple formatter
python cortex/orchestrators/response/simple_response_formatter.py

# Verify output matches chat01.md clarity
```

---

## Support

**Questions?** Check:
- Simple formatter code: `cortex/orchestrators/response/simple_response_formatter.py` (150 lines, self-documenting)
- ENH-082 superseded rationale: `cortex-registry/_cortex-master/_superseded/enh-082/ENH-082-SUPERSEDED.md`
- Git commit: `c51fb7b53` (Simple formatter implementation)

**Authority:** Phase 53 anti-overengineering initiative + holistic git history review
