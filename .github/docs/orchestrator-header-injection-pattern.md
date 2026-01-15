# Orchestrator Header Injection Pattern

**AC-ENH-001-01 Reference Implementation**

Last Updated: 2026-01-15  
Status: Reference Implementation Complete  
Tests: 18/18 Integration + 24/24 Unit = 42/42 PASSING ✅

---

## Overview

This document describes the **composition-based header injection pattern** for integrating CORTEX global headers into orchestrator responses. This is the reference implementation established by AC-ENH-001-01 using PlanningOrchestrator.

### Key Principles

1. **Non-invasive**: Uses composition pattern, does not modify ResponseTemplateEngine
2. **Optional**: Orchestrators can optionally specify custom response templates
3. **Orthogonal**: Header injection is independent of template rendering
4. **Graceful**: Headers are enhancement-only; system works without them
5. **Backward compatible**: Existing orchestrators continue to work unmodified

---

## Architecture

### Component Diagram

```
Orchestrator Response Flow
├── Custom Response Template (Optional)
│   └── ResponseTemplateEngine.render() → rendered_content
│
├── OR Default Response
│   └── Orchestrator builds response string directly → response_content
│
└── Header Injection Layer (AC-ENH-001)
    └── ResponseHeaderInjector
        ├── _build_header_section() → prepends header
        ├── _build_copyright_section() → appends copyright
        ├── _assemble_sections() → proper spacing
        └── Output: Header + Content + Copyright
```

### Assembly Order

```
═══════════════════════════════════════════════════════════════
Header Section
═══════════════════════════════════════════════════════════════
## 🧠 CORTEX Operation
**Author:** Author Name | **Phase:** PHASE-XX | **Orchestrator:** Name ✅

---

Response Content
(Original orchestrator response or custom template output)

---
**Copyright © 2025-2026 Author. All rights reserved.**
═══════════════════════════════════════════════════════════════
```

---

## Implementation Guide

### Step 1: Add ResponseHeaderInjector to Orchestrator `__init__`

```python
from src.core.response_header_config import HeaderConfigurationManager
from src.core.response_header_injector import ResponseHeaderInjector

class MyOrchestrator(IOrchestrator):
    def __init__(self):
        self._name = "MyOrchestrator"
        
        # AC-ENH-001: Initialize header system (composition pattern)
        try:
            config_manager = HeaderConfigurationManager.get_instance()
            config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')
            self._header_config = config_manager
            
            # Create ResponseHeaderInjector instance
            # Pass None as template_engine if orchestrator doesn't use templates
            # Pass actual engine if orchestrator uses ResponseTemplateEngine
            self._header_injector = ResponseHeaderInjector(
                template_engine=None,  # Optional
                config_manager=config_manager
            )
        except Exception as e:
            print(f"Warning: Failed to initialize header system: {e}")
            self._header_config = None
            self._header_injector = None
```

### Step 2: Implement `get_response_with_headers()` Method

```python
def get_response_with_headers(self, response_content: str) -> str:
    """
    Wrap response content with CORTEX headers.
    
    AC-ENH-001-01: Reference implementation pattern
    
    Args:
        response_content: The response body to wrap
        
    Returns:
        Response with header, content, and copyright
    """
    if not self._header_injector or not self._header_config:
        return response_content
    
    try:
        # Prepare context for header variable substitution
        context = {
            "operation": "OperationName",
            "orchestrator": self._name,
            "phase": "PHASE-XX",
            "mode": self._mode.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Build sections using injector's internal methods
        header_section = self._header_injector._build_header_section(context)
        copyright_section = self._header_injector._build_copyright_section(context)
        
        # Assemble: header + content + copyright
        sections = []
        if header_section:
            sections.append(header_section)
        sections.append(response_content)
        if copyright_section:
            sections.append(copyright_section)
        
        # Use injector's assembly logic for consistent spacing
        result = self._header_injector._assemble_sections(sections)
        return result
        
    except Exception as e:
        # Graceful degradation: return original on error
        print(f"Warning: Failed to add headers: {e}")
        return response_content
```

### Step 3: Wrap Orchestrator Output

When orchestrator generates responses, call the wrapper:

```python
def execute_operation(self, operation_name: str, parameters: dict):
    """Execute operation and wrap response with headers."""
    
    # 1. Generate response (custom template or default)
    response_content = self._generate_response(operation_name, parameters)
    
    # 2. Wrap with headers (AC-ENH-001-01 pattern)
    wrapped_response = self.get_response_with_headers(response_content)
    
    # 3. Return wrapped response
    return Ok(wrapped_response)
```

---

## Custom Response Templates

### Option A: No Custom Template (Use Defaults)

```python
# Orchestrator builds response directly
response_content = f"Status: OK\nPhase: {phase}\nProgress: {progress}%"
wrapped = self.get_response_with_headers(response_content)
```

**Result**:
```
## 🧠 CORTEX OperationName
**Author:** ...

---

Status: OK
Phase: PHASE-02
Progress: 75%

---
**Copyright © ...**
```

### Option B: Custom Domain Template

**1. Define template in tier2 (orchestrator-specific)**

```yaml
# cortex-brain/tier2/response-templates/my-orchestrator.yaml
domain_templates:
  my_orchestrator:
    description: "Templates for MyOrchestrator"
    templates:
      operation_complete:
        id: "my_orchestrator:operation_complete"
        name: "operation_complete"
        template: |
          ✅ **Operation Completed**
          
          **Summary:** {summary}
          **Duration:** {duration_ms}ms
          **Status:** {status}
        variables:
          - name: "summary"
            type: "string"
            required: true
          - name: "duration_ms"
            type: "integer"
            required: true
          - name: "status"
            type: "string"
            required: true
```

**2. Use in orchestrator**

```python
from src.core.response_template_engine import ResponseTemplateEngine

class MyOrchestrator(IOrchestrator):
    def __init__(self):
        # ... header initialization ...
        self._template_engine = ResponseTemplateEngine()
    
    def execute_operation(self, operation_name, parameters):
        # 1. Render custom template
        rendered = self._template_engine.render(
            domain_id="my_orchestrator",
            template_name="operation_complete",
            context={
                "summary": "Task executed successfully",
                "duration_ms": 245,
                "status": "SUCCESS"
            }
        )
        
        # 2. Wrap with headers
        wrapped = self.get_response_with_headers(rendered)
        
        return Ok(wrapped)
```

**Result**:
```
## 🧠 CORTEX ExecuteOperation
**Author:** ...

---

✅ **Operation Completed**

**Summary:** Task executed successfully
**Duration:** 245ms
**Status:** SUCCESS

---
**Copyright © ...**
```

---

## Configuration

### Global Header Configuration

**Location:** `cortex-brain/tier0/response-headers.yaml` (Tier 0 - Immutable)

### Key Settings

```yaml
# Header template (appears at start)
header:
  enabled: true
  template: |
    ## 🧠 CORTEX {operation}
    **Author:** {author} | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

# Copyright section (appears after content)
copyright_section:
  enabled: true
  template: |
    **{notice}**
  formatting:
    separator_before: true    # --- before copyright
    separator_after: false    # No separator after

# Footer (optional, disabled by default)
footer:
  enabled: false
  template: |
    ---
    **Reference:** {repository} | **License:** {license}
```

### Template Variables

**Mandatory (provided by orchestrator):**
- `operation`: Operation being performed
- `phase`: Current phase (e.g., "PHASE-02")
- `orchestrator`: Orchestrator name

**Auto-populated:**
- `author`: From `author.name` (Asif Hussain)
- `notice`: From `copyright.notice`
- `repository`: From `author.repository`
- `license`: From `copyright.license`

---

## Testing

### Test Structure

**Integration Tests** (18 tests, all passing):
- Orchestrator initializes with headers
- `get_response_with_headers()` method exists
- Headers wrap responses correctly
- Author info appears in headers
- Header/footer/copyright structure verified
- Variable substitution verified
- Edge cases (empty, multiline, special chars)
- Backward compatibility verified

**Unit Tests** (24 tests, all passing):
- Orchestrator interface compliance
- MCP tools exposure
- Audit logging with hash chain
- Operation execution
- Singleton pattern
- Complete workflow integration

### Running Tests

```bash
# All integration tests
pytest tests/integration/test_planning_orchestrator_headers.py -v

# All unit tests
pytest tests/unit/test_planning_orchestrator.py -v

# Both suites
pytest tests/unit/test_planning_orchestrator.py tests/integration/test_planning_orchestrator_headers.py -v
```

---

## Orchestrator Implementation Checklist

Use this checklist when implementing AC-ENH-001-01 pattern in new orchestrators:

- [ ] Import `ResponseHeaderInjector` and `HeaderConfigurationManager`
- [ ] Initialize injector in `__init__` with error handling
- [ ] Store `_header_config` and `_header_injector` as instance variables
- [ ] Implement `get_response_with_headers(response_content: str)` method
- [ ] Prepare context dict with operation, orchestrator, phase variables
- [ ] Call `_build_header_section(context)`
- [ ] Call `_build_copyright_section(context)`
- [ ] Assemble sections using `_assemble_sections()`
- [ ] Implement graceful degradation (return original on error)
- [ ] Wrap orchestrator output with `get_response_with_headers()`
- [ ] Write 3-5 integration tests for header wrapping
- [ ] Verify no regressions in existing tests
- [ ] Document any custom response templates in tier2
- [ ] Update roadmap with implementation status

---

## Backward Compatibility

### Existing Orchestrators

Orchestrators that don't implement AC-ENH-001-01:
- Continue to work without headers
- Not affected by header configuration
- Can be upgraded at any time

### Migration Path

1. **Phase 1** (Current): Reference implementation in PlanningOrchestrator
2. **Phase 2**: Document pattern in this guide
3. **Phase 3**: Migrate remaining orchestrators one at a time
4. **Phase 4**: Make headers mandatory (requires governance approval)

---

## Common Patterns

### Pattern 1: Simple String Response

```python
def get_status(self):
    response = f"Status: {self._mode.name}"
    return self.get_response_with_headers(response)
```

### Pattern 2: JSON Response

```python
import json

def get_config(self):
    config_dict = {"mode": self._mode.name, "version": "1.0"}
    response = json.dumps(config_dict, indent=2)
    return self.get_response_with_headers(response)
```

### Pattern 3: Template-Based Response

```python
def get_report(self):
    rendered = self._template_engine.render(
        domain_id="governance",
        template_name="evaluation_report",
        context={"score": 95, "status": "PASS"}
    )
    return self.get_response_with_headers(rendered)
```

### Pattern 4: Conditional Headers

```python
def get_response_with_headers(self, response_content: str, include_headers=True):
    if not include_headers:
        return response_content
    # ... normal header wrapping ...
```

---

## Troubleshooting

### Headers Not Appearing

**Check:**
1. `_header_injector` initialized in `__init__`
2. `get_response_with_headers()` is being called
3. Headers are not disabled in config
4. No exceptions caught silently (enable debug logging)

### Wrong Variables in Headers

**Check:**
1. Context dict has all required variables
2. Variable names match template placeholders
3. No braces `{}` remain in output (indicates missing substitution)

### Custom Template Not Used

**Check:**
1. Template defined in `cortex-brain/tier2/response-templates/`
2. Domain ID and template name match
3. Template variables provided in context
4. Template file is loaded by ResponseTemplateEngine

---

## References

- **AC-ENH-001**: Response Header Injection System Integration
- **AR-009**: Response Templates Architecture
- **PHASE-ENHANCEMENT-01**: Response Header Injection Phase
- **Tier 0**: `cortex-brain/tier0/response-headers.yaml`
- **Tier 2**: `cortex-brain/tier2/response-templates/`

---

## Next Steps (AC-ENH-001-02)

Current: Reference implementation complete (AC-ENH-001-01)

Next: Verify headers in orchestrator responses with custom templates (AC-ENH-001-02)

Roadmap:
- [ ] AC-ENH-001-02: Verify headers with response content
- [ ] AC-ENH-001-03: Document pattern for all orchestrators
- [ ] AC-ENH-001-04: Regression test suite

---
