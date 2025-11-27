# Vision API Enforcement Test Suite

**Status:** ✅ 18/18 PASSING  
**Coverage:** Automatic triggering, integration, regression prevention  
**Priority:** CRITICAL - Must pass before merge

---

## Purpose

These tests **enforce** that Vision API automatically triggers when images are attached to requests. Any failure indicates a **breaking change** that must be fixed before merging.

---

## Test Categories

### 1. Auto-Trigger Tests (11 tests)
Verify Vision API automatically engages on image detection:

- ✅ `test_intent_router_has_vision_orchestrator` - Router has orchestrator
- ✅ `test_vision_orchestrator_auto_processes_images` - Orchestrator processes images
- ✅ `test_intent_router_processes_images_before_routing` - Processing happens before routing
- ✅ `test_vision_results_injected_into_context` - Results injected into context
- ✅ `test_data_uri_detection_triggers_vision` - Data URIs trigger detection
- ✅ `test_copilot_attachment_triggers_vision` - Copilot attachments trigger
- ✅ `test_multiple_image_formats_supported` - All formats supported
- ✅ `test_context_aware_prompt_selection` - Correct prompts selected
- ✅ `test_disabled_config_prevents_detection` - Disable works
- ✅ `test_max_images_limit_enforced` - Limits enforced
- ✅ `test_vision_error_does_not_block_routing` - Errors don't block

### 2. Integration Tests (2 tests)
Verify complete end-to-end flow:

- ✅ `test_end_to_end_image_processing` - Full detection→analysis→injection
- ✅ `test_metrics_tracking` - Metrics collected correctly

### 3. Regression Tests (3 tests)
Prevent breaking changes:

- ✅ `test_import_stability` - Imports don't break
- ✅ `test_interface_stability` - Public APIs stable
- ✅ `test_config_backward_compatibility` - Old configs work

### 4. Performance Tests (1 test)
Ensure quick_check is fast:

- ✅ `test_quick_check_performance` - Must complete <100ms

### 5. Configuration Tests (1 test)
Validate config file:

- ✅ `test_configuration_validation` - All settings present

---

## Critical Assertions

These assertions **MUST** pass:

```python
# CRITICAL: Intent Router must have VisionOrchestrator
assert hasattr(router, 'vision_orchestrator')
assert router.vision_orchestrator is not None

# CRITICAL: Images must be detected
assert result['images_found'] is True
assert result['images_analyzed'] > 0

# CRITICAL: Results must be injected into context
assert 'vision_analysis' in request.context
assert vision_data['images_found'] is True

# CRITICAL: All formats must be supported
for fmt in ['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp']:
    assert fmt in supported_formats

# CRITICAL: Errors must not block routing
assert response.success  # Even if Vision API fails
```

---

## Running Tests

### Run All Enforcement Tests
```bash
pytest tests/test_vision_api_enforcement.py -v
```

### Run Specific Category
```bash
# Auto-trigger tests only
pytest tests/test_vision_api_enforcement.py::TestVisionAPIAutoTrigger -v

# Integration tests only
pytest tests/test_vision_api_enforcement.py::TestVisionAPIIntegrationFlow -v

# Regression tests only
pytest tests/test_vision_api_enforcement.py::TestVisionAPIRegression -v
```

### Run with Coverage
```bash
pytest tests/test_vision_api_enforcement.py --cov=src.tier1 --cov=src.cortex_agents.intent_router -v
```

### Run in CI/CD
```bash
# Fast mode (parallel)
pytest tests/test_vision_api_enforcement.py -n auto -v

# Strict mode (fail fast)
pytest tests/test_vision_api_enforcement.py -x -v
```

---

## CI/CD Integration

### Pre-Commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
echo "Running Vision API enforcement tests..."
pytest tests/test_vision_api_enforcement.py -x
if [ $? -ne 0 ]; then
    echo "❌ Vision API enforcement tests failed - commit blocked"
    exit 1
fi
echo "✅ Vision API enforcement tests passed"
```

### GitHub Actions Workflow
```yaml
name: Vision API Enforcement
on: [push, pull_request]

jobs:
  enforce:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/test_vision_api_enforcement.py -v
        name: Vision API Auto-Trigger Tests
```

---

## Failure Scenarios

### Scenario 1: Vision Orchestrator Not Initialized
```
FAILED test_intent_router_has_vision_orchestrator
AssertionError: Intent Router MUST have vision_orchestrator attribute
```

**Fix:** Check `IntentRouter.__init__()` - ensure `VisionOrchestrator(config)` is called.

---

### Scenario 2: Images Not Detected
```
FAILED test_vision_orchestrator_auto_processes_images
AssertionError: VisionOrchestrator MUST detect images in request
```

**Fix:** Check `ImageDetector.detect()` - regex patterns may be broken.

---

### Scenario 3: Context Not Injected
```
FAILED test_vision_results_injected_into_context
AssertionError: Vision analysis results MUST be injected into request.context
```

**Fix:** Check `IntentRouter.execute()` - ensure vision results are added to `request.context['vision_analysis']`.

---

### Scenario 4: Format Not Supported
```
FAILED test_multiple_image_formats_supported
AssertionError: Format webp MUST be in supported_formats list
```

**Fix:** Check `cortex.config.json` - add missing format to `vision_api.supported_formats`.

---

### Scenario 5: Performance Regression
```
FAILED test_quick_check_performance
AssertionError: quick_check MUST complete in <100ms (took 250.3ms)
```

**Fix:** Optimize `ImageDetector.has_images()` - use faster regex checks.

---

## Test Data

### Sample Data URI (1x1 PNG)
```python
"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
```

### Sample Copilot Attachment
```python
{
    'type': 'image',
    'mimeType': 'image/png',
    'data': 'data:image/png;base64,...',
    'name': 'screenshot.png',
    'size': 1024
}
```

---

## Coverage Requirements

Minimum coverage for Vision API modules:

| Module | Minimum Coverage | Current |
|--------|------------------|---------|
| `image_detector.py` | 85% | ✅ 92% |
| `vision_orchestrator.py` | 85% | ✅ 89% |
| `intent_router.py` (vision parts) | 80% | ✅ 87% |

---

## Maintenance

### Adding New Tests

When adding features, add enforcement tests:

```python
def test_new_feature_enforced(self):
    """ENFORCEMENT: New feature must work automatically."""
    # Setup
    config = {...}
    
    # Execute
    result = feature_function(config)
    
    # Assert with clear failure message
    assert result == expected, \
        "Feature MUST [specific behavior] (got {result})"
```

### Test Naming Convention

- `test_[feature]_enforced` - Feature enforcement
- `test_[scenario]_triggers_vision` - Auto-trigger scenarios
- `test_[component]_integration` - Integration tests
- `test_[feature]_regression` - Regression prevention

---

## Related Documentation

- Implementation Guide: `cortex-brain/documents/implementation-guides/AUTOMATIC-IMAGE-DETECTION.md`
- Vision API Design: `src/tier1/vision_api.py`
- Image Detector: `src/tier1/image_detector.py`
- Vision Orchestrator: `src/tier1/vision_orchestrator.py`

---

## Test Status Dashboard

```
┌─────────────────────────────────────────┐
│  VISION API ENFORCEMENT TEST STATUS     │
├─────────────────────────────────────────┤
│  Total Tests:        18                 │
│  Passing:            18 ✅              │
│  Failing:             0                 │
│  Skipped:             0                 │
│                                         │
│  Auto-Trigger:       11/11 ✅          │
│  Integration:         2/2  ✅          │
│  Regression:          3/3  ✅          │
│  Performance:         1/1  ✅          │
│  Configuration:       1/1  ✅          │
│                                         │
│  Status: PROTECTED ✅                  │
│  Last Run: 2025-11-17 16:45             │
│  Duration: 4.78s                        │
└─────────────────────────────────────────┘
```

---

**Author:** Asif Hussain  
**Last Updated:** 2025-11-17  
**Status:** ✅ ENFORCED  
**Priority:** CRITICAL
