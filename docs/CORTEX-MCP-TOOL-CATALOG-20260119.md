# CORTEX MCP Tool Catalog
**Date**: January 19, 2026  
**Version**: 1.0  
**Status**: COMPLETE

---

## Quick Reference: All Exposed MCP Tools

### Category 1: Orchestrator-Level Tools

#### Master Orchestrator (`cortex/orchestrators/core/master_orchestrator.py`)
| Method | Return Type | Availability | Status |
|---|---|---|---|
| `get_mcp_tools()` | `Result[Dict[str, Any]]` | Always | ✅ Active |

**Description**: Returns all MCP tools available from the master orchestrator instance.

---

#### Planning Orchestrator (`cortex/orchestrators/domain/planning_orchestrator.py`)
| Method | Return Type | Availability | Status |
|---|---|---|---|
| `get_mcp_tools()` | `Result[Dict[str, Any]]` | Always | ✅ Active |

**Description**: Returns planning-specific MCP tools for orchestration operations.

---

#### Intent Router (`cortex/orchestrators/core/intent_router.py`)
| Method | Return Type | Availability | Status |
|---|---|---|---|
| `get_mcp_tools()` | `Result[Dict[str, Any]]` | Always | ✅ Active |

**Description**: Returns intent routing and resolution MCP tools.

---

### Category 2: Governance Tools

**Module**: `cortex/brain/mcp/tools/governance_tools.py`  
**Decorator**: `@mcp_tool`

| Tool Name | Parameters | Return Type | Purpose | Status |
|---|---|---|---|---|
| `check_phase_lock` | `phase_id: str` | `Result[Dict]` | Verify phase lock status | ✅ |
| `validate_ac_id` | `ac_id: str` | `Result[Dict]` | Validate AC-ID existence | ✅ |
| `canonicalize_intent` | `intent: str`, `intent_type: str` | `Result[Dict]` | Normalize intent (anti-hallucination) | ✅ |
| `enforce_operation` | `operation: str`, `parameters: dict` | `Result[Dict]` | Full operation enforcement | ✅ |
| `get_phase_status` | `phase_id: str` | `Result[Dict]` | Get comprehensive phase status | ✅ |

**Audit Integration**: All governance tools integrated with `GovernanceEnforcer` and database logging.

---

### Category 3: Analysis Tools

**Module**: `cortex/mcp/domain_operations.py`  
**Decorator**: `@mcp_tool`

| Tool Name | Parameters | Return Type | Purpose | Status |
|---|---|---|---|---|
| `analyze_code_structure` | `code: str`, `language: str` | `Dict[str, Any]` | Extract code structure and patterns | ✅ |
| `analyze_dependencies` | `module: str` | `Dict[str, Any]` | Analyze module dependencies | ✅ |
| `analyze_performance` | `code: str` | `Dict[str, Any]` | Analyze code performance characteristics | ✅ |

---

### Category 4: Validation Tools

**Module**: `cortex/mcp/domain_operations.py`  
**Decorator**: `@mcp_tool`

| Tool Name | Parameters | Return Type | Purpose | Status |
|---|---|---|---|---|
| `validate_context` | `context: dict`, `rules: list` | `Dict[str, Any]` | Validate execution context | ✅ |
| `validate_rules` | `rules: list`, `context: dict` | `Dict[str, Any]` | Validate rule set | ✅ |
| `validate_constraints` | `constraints: list` | `Dict[str, Any]` | Validate constraints | ✅ |
| `validate_boundaries` | `bounds: dict`, `values: list` | `Dict[str, Any]` | Check boundary conditions | ✅ |

---

### Category 5: Transformation Tools

**Module**: `cortex/mcp/domain_operations.py`  
**Decorator**: `@mcp_tool`

| Tool Name | Parameters | Return Type | Purpose | Status |
|---|---|---|---|---|
| `transform_code` | `code: str`, `transformation: str` | `Dict[str, Any]` | Apply code transformations | ✅ |
| `transform_data` | `data: dict`, `rules: list` | `Dict[str, Any]` | Apply data transformations | ✅ |

---

### Category 6: Synthesis Tools

**Module**: `cortex/mcp/domain_operations.py`  
**Decorator**: `@mcp_tool`

| Tool Name | Parameters | Return Type | Purpose | Status |
|---|---|---|---|---|
| `synthesize_knowledge` | `sources: list` | `Dict[str, Any]` | Synthesize knowledge from sources | ✅ |
| `synthesize_solution` | `approaches: list` | `Dict[str, Any]` | Synthesize solution recommendations | ✅ |

---

### Category 7: Conflict Resolution Tools

**Module**: `cortex/mcp/domain_operations.py`  
**Decorator**: `@mcp_tool`

| Tool Name | Parameters | Return Type | Purpose | Status |
|---|---|---|---|---|
| `resolve_conflicts` | `conflicts: list` | `Dict[str, Any]` | Resolve operation conflicts | ✅ |
| `resolve_constraints` | `constraints: list` | `Dict[str, Any]` | Resolve constraint conflicts | ✅ |

---

## Tool Discovery Methods

### Method 1: List Tools Endpoint
```python
from cortex.mcp.endpoints import list_tools_endpoint

tools = list_tools_endpoint()
# Returns: {
#     "tools": [
#         {"name": "...", "description": "...", "parameters": {...}},
#         ...
#     ],
#     "count": N
# }
```

### Method 2: Registry Direct Access
```python
from cortex.mcp.decorators import MCP_TOOLS_REGISTRY

for tool_name, tool_meta in MCP_TOOLS_REGISTRY.items():
    print(f"Tool: {tool_name}")
    print(f"  Description: {tool_meta['description']}")
    print(f"  Parameters: {tool_meta['parameters']}")
```

### Method 3: Orchestrator Discovery
```python
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

master = MasterOrchestrator.instance()
result = master.get_mcp_tools()

if result.is_ok():
    tools = result.value
    for tool_name, tool_info in tools.items():
        print(f"Tool: {tool_name}")
```

### Method 4: Domain Filtering
```python
from cortex.mcp.endpoints import filter_tools_by_domain

governance_tools = filter_tools_by_domain("governance")
analysis_tools = filter_tools_by_domain("analysis")
validation_tools = filter_tools_by_domain("validation")
```

### Method 5: Get Tool Metadata
```python
from cortex.mcp.endpoints import get_tool_metadata

metadata = get_tool_metadata("check_phase_lock")
# Returns: {
#     "name": "check_phase_lock",
#     "description": "Check if a phase is locked...",
#     "parameters": {...},
#     "callable": True
# }
```

---

## Tool Invocation Examples

### Example 1: Governance Tool
```python
from cortex.brain.mcp.tools.governance_tools import check_phase_lock

result = check_phase_lock("PHASE-01")
if result.is_ok():
    status = result.value
    print(f"Phase locked: {status['locked']}")
else:
    error = result.error
    print(f"Error: {error}")
```

### Example 2: Analysis Tool
```python
from cortex.mcp.domain_operations import analyze_code_structure

code = """
def hello():
    print("Hello, World!")
"""

result = analyze_code_structure(code, language="python")
print(f"Lines: {result['lines']}")
print(f"Patterns: {result['patterns']}")
```

### Example 3: Validation Tool
```python
from cortex.mcp.domain_operations import validate_context

context = {
    "operation": "deployment",
    "phase": "PHASE-02",
    "user": "developer"
}

rules = ["must_have_phase", "must_have_user"]

result = validate_context(context, rules)
print(f"Valid: {result['valid']}")
print(f"Violations: {result['violations']}")
```

### Example 4: Multiple Tools
```python
from cortex.mcp.endpoints import list_tools_endpoint

# Discover all tools
tools_response = list_tools_endpoint()
print(f"Total tools available: {tools_response['count']}")

# List all tools
for tool in tools_response['tools']:
    print(f"- {tool['name']}: {tool['description']}")
```

---

## Tool Statistics

### By Category
| Category | Tool Count | Status |
|---|---|---|
| Orchestrators | 3 | ✅ |
| Governance | 5 | ✅ |
| Analysis | 3 | ✅ |
| Validation | 4 | ✅ |
| Transformation | 2 | ✅ |
| Synthesis | 2 | ✅ |
| Conflict Resolution | 2 | ✅ |
| **TOTAL** | **23+** | **✅** |

### By Type
| Type | Count |
|---|---|
| Orchestrator Methods | 3 |
| @mcp_tool Decorated Functions | 20+ |
| Discovery Endpoints | 3 |

### By Return Type
| Return Type | Count |
|---|---|
| `Result[Dict[str, Any]]` | 5 |
| `Dict[str, Any]` | 15+ |

---

## Compliance Certifications

### Protocol Compliance
- ✅ JSON-RPC 2.0 compliant
- ✅ UTF-8 encoding support
- ✅ Error response format standardized
- ✅ Request/response ID correlation

### Data Model Compliance
- ✅ Tool metadata standardized
- ✅ Parameter definitions consistent
- ✅ Response format uniform
- ✅ Error objects structured

### Functionality Compliance
- ✅ All tools parameter-validated
- ✅ All tools handle errors gracefully
- ✅ All tools return proper types
- ✅ All tools are discoverable

---

## Integration Points

### MCP Server Integration
- ✅ Tool registration in `MCPServer`
- ✅ Tool execution via `MCPServer.execute_tool()`
- ✅ Discovery via `/list-tools` endpoint

### Orchestrator Integration
- ✅ Tools discoverable via orchestrator methods
- ✅ Tools execute in orchestrator context
- ✅ Tools benefit from orchestrator audit logging

### Database Integration
- ✅ Governance tools use database
- ✅ Operations logged to audit trail
- ✅ Phase lock status persisted

### Audit Logging
- ✅ All governance operations logged
- ✅ Operation hash chain maintained
- ✅ User and timestamp tracked
- ✅ Compliance audit trail available

---

## Future Extensibility

### Adding New Tools
```python
from cortex.mcp.decorators import mcp_tool

@mcp_tool(
    name="my_new_tool",
    description="Description of my new tool",
    parameters={"param1": "string", "param2": "int"}
)
def my_new_tool(param1: str, param2: int) -> dict:
    """Implementation of my new tool."""
    return {"result": "success"}

# Tool automatically registered and discoverable!
```

### Adding New Orchestrator Tools
```python
from cortex.brain.core.interfaces import IOrchestrator
from cortex.brain.core.result import Result

class MyOrchestrator(IOrchestrator):
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Return my custom MCP tools."""
        return Ok({
            "my_tool_1": {"description": "..."},
            "my_tool_2": {"description": "..."},
        })
```

---

## Verification Commands

### List All Tools
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python -c "from cortex.mcp.endpoints import list_tools_endpoint; import json; print(json.dumps(list_tools_endpoint(), indent=2))"
```

### Check Registry
```bash
python -c "from cortex.mcp.decorators import MCP_TOOLS_REGISTRY; print(f'Total tools: {len(MCP_TOOLS_REGISTRY)}'); print(list(MCP_TOOLS_REGISTRY.keys()))"
```

### Test Tool Discovery
```bash
pytest tests/unit/mcp/test_mcp_exposure_003.py -v
```

### Run All MCP Tests
```bash
pytest tests/unit/mcp/ -v -k "mcp"
```

---

## Support & Documentation

### For MCP Users
- Start with `list_tools_endpoint()` to discover available tools
- Check tool parameters before invocation
- Use orchestrator methods for domain-specific tool discovery
- Refer to individual tool docstrings for implementation details

### For MCP Developers
- Add new tools via `@mcp_tool` decorator
- Expose orchestrator tools via `get_mcp_tools()` method
- Follow Result pattern for return types
- Include comprehensive docstrings

### For Auditors
- All MCP operations logged via `EnhancedAuditLogger`
- Tool metadata accessible via discovery endpoints
- Compliance tests in `tests/unit/mcp/` directory
- Audit trail accessible via orchestrator methods

---

**Last Updated**: January 19, 2026  
**Status**: COMPLETE & VERIFIED ✅  
**Maintenance**: Active
