# Response Header Integration Guide

**Version:** 1.0  
**Date:** January 15, 2026  
**Status:** ACTIVE (PHASE-ENHANCEMENT-01)  
**Commit:** 723b0c37e (Foundation), TBD (Reference Implementation)

---

## Overview

This guide documents the hybrid integration approach for the ResponseHeaderInjector system into CORTEX orchestrators. The system provides global CORTEX headers on all orchestrator responses.

### Key Principles

1. **Single Source of Truth:** All headers defined in `cortex_brain/tier0/response-headers.yaml`
2. **Non-Invasive:** Uses composition pattern—ResponseTemplateEngine unchanged
3. **Hybrid Rollout:** Reference implementation first, then pattern-based adoption
4. **Zero Duplication:** Document the pattern once, reuse everywhere

---

## Component Overview

### 1. Header Configuration (Tier 0)
**File:** `cortex_brain/tier0/response-headers.yaml`

```yaml
metadata:
  version: "1.0"
  created: "2026-01-15"

author:
  name: "Asif Hussain"
  github_handle: "asifhussain60"
  repository: "https://github.com/asifhussain60/CORTEX"

copyright:
  notice: "Copyright © {start_year}-{end_year} {holder}. All rights reserved."
  holder: "Asif Hussain"

header_template: |
  ## 🧠 CORTEX {operation}
  **Author:** {author} | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

variables:
  mandatory: ["operation", "phase", "orchestrator"]
  auto_populated: ["author", "copyright_notice"]
```

**Modification:** Edit this ONE file to change headers globally across all orchestrators.

### 2. Configuration Manager (Singleton)
**File:** `src/core/response_header_config.py`

Loads and manages header configuration. Singleton pattern ensures one instance.

```python
from src.core.response_header_config import HeaderConfigurationManager

# Initialize at application startup
config_manager = HeaderConfigurationManager.get_instance()
config_manager.load_configuration('cortex_brain/tier0/response-headers.yaml')

# Use anywhere
author = config_manager.get_author_name()  # "Asif Hussain"
notice = config_manager.get_copyright_notice()  # "Copyright © 2025-2026..."
```

### 3. Header Injector (Composition Layer)
**File:** `src/core/response_header_injector.py`

Wraps ResponseTemplateEngine and injects headers into rendered responses.

```python
from src.core.response_header_injector import ResponseHeaderInjector

# Wrap the engine (no modifications to engine itself)
injector = ResponseHeaderInjector(engine, config_manager)

# Use injector instead of engine
result = injector.render(domain, template_name, context)
# Returns: [Header]\n\n[Response]\n\n[Copyright Footer]
```

---

## Integration Pattern

### Step 1: Update Orchestrator Initialization

**Before:**
```python
from src.core.response_template_engine import ResponseTemplateEngine

class MyOrchestrator:
    def __init__(self):
        self.engine = ResponseTemplateEngine(registry)
```

**After:**
```python
from src.core.response_template_engine import ResponseTemplateEngine
from src.core.response_header_config import HeaderConfigurationManager
from src.core.response_header_injector import ResponseHeaderInjector

class MyOrchestrator:
    def __init__(self):
        # Initialize config manager
        config_manager = HeaderConfigurationManager.get_instance()
        config_manager.load_configuration('cortex_brain/tier0/response-headers.yaml')
        
        # Wrap engine with injector
        engine = ResponseTemplateEngine(registry)
        self.injector = ResponseHeaderInjector(engine, config_manager)
```

### Step 2: Update Render Calls

**Before:**
```python
def generate_response(self, domain, template, context):
    return self.engine.render(domain, template, context)
```

**After:**
```python
def generate_response(self, domain, template, context):
    return self.injector.render(domain, template, context)
```

### Step 3: Ensure Context Contains Required Variables

The `context` dict must include mandatory variables for header substitution:

```python
context = {
    "operation": "GetPlanStatus",      # Mandatory
    "phase": "PHASE-PLANNING",         # Mandatory
    "orchestrator": "PlanningOrchestrator",  # Mandatory
    # ... other template variables
}
```

### Step 4: Test & Verify

```bash
# Run orchestrator tests
pytest tests/unit/test_planning_orchestrator.py -v

# Verify headers appear in output
python -c "
from src.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
orch = PlanningOrchestrator()
response = orch.generate_response('planning', 'status_template', {
    'operation': 'GetStatus',
    'phase': 'PHASE-01',
    'orchestrator': 'PlanningOrchestrator',
})
print(response)
# Should show:
# ## 🧠 CORTEX GetStatus
# **Author:** Asif Hussain | **Phase:** PHASE-01 | **Orchestrator:** PlanningOrchestrator ✅
# ---
# [rest of response]
# ---
# **Copyright © 2025-2026 Asif Hussain. All rights reserved.**
"
```

---

## Implementation Roadmap

### Phase: PHASE-ENHANCEMENT-01 (Current)

#### AC-ENH-001-01: Reference Implementation (PlanningOrchestrator)
- **Status:** IN_PROGRESS
- **Time:** ~1-2 hours
- **Work:** Integrate ResponseHeaderInjector into PlanningOrchestrator
- **Completion:** Header injection working, tests passing

#### AC-ENH-001-02: Response Verification
- **Status:** PENDING
- **Time:** ~0.5 hours
- **Work:** Verify headers appear correctly in responses with variable substitution
- **Completion:** E2E test showing headers in live responses

#### AC-ENH-001-03: Documentation & Pattern
- **Status:** PENDING
- **Time:** ~0.5-1 hour
- **Work:** Document integration pattern for future orchestrators
- **Completion:** Clear guide for other orchestrators to follow

#### AC-ENH-001-04: Backward Compatibility
- **Status:** PENDING
- **Time:** ~0.5 hours
- **Work:** Verify no regressions in orchestrator test suite
- **Completion:** All orchestrator tests passing

### Future Phases

**When Other Orchestrators Are Updated:**
Each orchestrator follows the same 2-step pattern:
1. Wrap engine with injector at initialization
2. Update render calls

**No Rework Needed:**
The integration pattern is established. Future work uses the same approach.

---

## Testing Strategy

### Unit Tests
**File:** `tests/unit/test_response_headers.py`

Already passing: 29/29 tests covering:
- Configuration loading
- Manager functionality
- Header injection
- Variable substitution
- Edge cases

### Integration Tests (To Add)

After reference implementation, add:

```python
# tests/integration/test_orchestrator_headers.py

def test_planning_orchestrator_returns_headers():
    """Verify PlanningOrchestrator responses include headers."""
    orch = PlanningOrchestrator()
    response = orch.plan_status({
        'operation': 'GetStatus',
        'phase': 'PHASE-01',
        'orchestrator': 'PlanningOrchestrator'
    })
    
    assert '## 🧠 CORTEX GetStatus' in response
    assert 'Asif Hussain' in response
    assert 'Copyright ©' in response
```

### E2E Tests (To Add)

```bash
# Run full orchestrator suite to verify no regressions
pytest tests/ -k orchestrator -v

# Run header-specific integration tests
pytest tests/integration/test_orchestrator_headers.py -v
```

---

## Configuration Reference

### Adding/Modifying Headers

Edit `cortex_brain/tier0/response-headers.yaml`:

```yaml
# Change header template
header_template: |
  ## 🧠 CORTEX {operation}
  **Author:** {author} | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

# Change copyright notice
copyright:
  notice: "Copyright © {start_year}-{end_year} {holder}. All rights reserved."

# Add domain-specific overrides
domain_overrides:
  governance:
    enabled: true  # Special header for governance responses
    template: |
      ## 🛡️ CORTEX GOVERNANCE {operation}
      **Authority:** {author} | **Enforcement:** {phase}
```

Changes propagate automatically to all orchestrators using ResponseHeaderInjector.

---

## Troubleshooting

### Headers Not Appearing

1. **Check initialization:**
   ```python
   config_manager = HeaderConfigurationManager.get_instance()
   print(config_manager.is_header_enabled())  # Should be True
   ```

2. **Verify context has mandatory variables:**
   ```python
   context = {
       'operation': 'MyOp',
       'phase': 'PHASE-01',
       'orchestrator': 'MyOrchestrator',
   }
   ```

3. **Check render is using injector, not engine:**
   ```python
   # Should use:
   self.injector.render(...)
   # NOT:
   self.engine.render(...)
   ```

### Headers Duplicated

Ensure only ONE injector wraps each engine. Don't create multiple injectors.

### Variable Substitution Failed

Check that mandatory variables are present:
- `operation` - Operation name
- `phase` - Phase identifier (e.g., "PHASE-01")
- `orchestrator` - Orchestrator name

---

## Deployment Checklist

Before marking AC-ENH-001-XX as COMPLETE:

- [ ] Reference orchestrator (PlanningOrchestrator) integrated
- [ ] Headers appear in responses
- [ ] Variables substitute correctly
- [ ] All unit tests passing (29/29)
- [ ] New integration tests passing
- [ ] No regressions in orchestrator suite
- [ ] Documentation updated (this guide)
- [ ] Code committed with clear message
- [ ] Roadmap updated (PHASE-ENHANCEMENT-01 progress)

---

## FAQ

**Q: Do I need to modify ResponseTemplateEngine?**  
A: No. ResponseHeaderInjector uses composition—ResponseTemplateEngine is unchanged.

**Q: What if I only want headers on some orchestrators?**  
A: Use domain overrides in `response-headers.yaml`:
```yaml
domain_overrides:
  governance:
    enabled: true
  audit:
    enabled: false  # No headers on audit responses
```

**Q: How do I disable headers globally?**  
A: Edit `response-headers.yaml`:
```yaml
enforcement:
  require_on_all_responses: false  # Disable globally
```

**Q: Can I have different headers for different orchestrators?**  
A: Yes, through domain overrides or by adding context variables for routing.

**Q: Will this affect performance?**  
A: Negligible. Composition adds <1ms per render.

---

## Related Documents

- **Configuration:** `cortex_brain/tier0/response-headers.yaml`
- **Config Manager:** `src/core/response_header_config.py`
- **Injector:** `src/core/response_header_injector.py`
- **Tests:** `tests/unit/test_response_headers.py`
- **Roadmap:** `.github/roadmap/cortex-master.yaml` (PHASE-ENHANCEMENT-01)

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-01-15 | Initial guide for hybrid integration approach |

---

**Author:** Asif Hussain  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
