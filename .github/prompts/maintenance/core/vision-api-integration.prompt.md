# 🔍 VISION API AUTO-ENGAGEMENT

**⚡ AUTOMATIC IMAGE DETECTION AND ANALYSIS**

When images are attached to context (PNG, JPG, JPEG), CORTEX MUST automatically engage Vision API WITHOUT user prompting.

---

## Workflow

1. **Image Detection** → `src/tier1/vision_orchestrator.py` detects image attachments
2. **Auto-Analysis** → GPT-4V analyzes image (<500ms)
3. **Context Injection** → Analysis injected into conversation context
4. **Orchestrator Use** → Planning/Debug/ADO orchestrators use vision context

---

## Configuration

- `auto_detect_images: true` (config: `cortex-brain/config/vision_api_config.template.yaml`)
- `auto_analyze_on_detect: true`
- `auto_inject_context: true`

---

## Middleware

- Location: `src/operations/utilities/vision_context_middleware.py`
- Decorator: `@with_vision_context_middleware`
- Cache: 24hr TTL to prevent duplicate API calls
- Token Budget: 500 token limit per analysis

---

## Context Types

- `generic`: General image analysis
- `planning`: Extract UI elements, buttons, layouts for implementation
- `debugging`: Extract error messages, stack traces, issues
- `ado`: Extract work item IDs, titles, acceptance criteria

---

## Integration Points

- Planning Orchestrator: UI mockups → component extraction
- Debug Orchestrator: Screenshots → error analysis
- ADO Orchestrator: Work item screenshots → automated story creation

---

## Validation

- ✅ Vision orchestrator exists: `src/tier1/vision_orchestrator.py`
- ✅ Middleware exists: `src/operations/utilities/vision_context_middleware.py`
- ✅ Config template exists: `cortex-brain/config/vision_api_config.template.yaml`
- ✅ All orchestrators use vision context when images present
