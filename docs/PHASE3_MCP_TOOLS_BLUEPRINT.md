# Phase 3: MCP Tools Exposure - Integration Blueprint
**Date:** 2026-01-24  
**Status:** READY FOR IMPLEMENTATION  
**Effort:** 3-4 hours  
**Blocking:** NO (Phase 2 complete)

---

## 15 MCP Tools Catalog

### Governance Tools (5 tools)
1. **query_governance_context** - Query execution context for governance rules
   - Location: `cortex/mcp/tools/governance/__init__.py`
   - Parameters: `operation_id`, `context_type`
   - Category: GOVERNANCE

2. **validate_governance_compliance** - Validate operation against governance rules
   - Location: `cortex/mcp/tools/governance/__init__.py`
   - Parameters: `operation`, `ruleset`
   - Category: GOVERNANCE

3. **execute_governance_check** - Execute comprehensive governance check
   - Location: `cortex/mcp/tools/governance/__init__.py`
   - Parameters: `operation`, `check_type`
   - Category: GOVERNANCE

4. **analyze_governance_impact** - Analyze governance impact of proposed operation
   - Location: `cortex/mcp/tools/governance/__init__.py`
   - Parameters: `operation`, `scope`
   - Category: GOVERNANCE

5. **report_governance_status** - Generate governance status report
   - Location: `cortex/mcp/tools/governance/__init__.py`
   - Parameters: `scope`, `time_range`
   - Category: GOVERNANCE

### Orchestration Tools (4 tools)
6. **get_operation_status** - Get status of ongoing operation
   - Location: `cortex/mcp/tools/orchestration/__init__.py`
   - Parameters: `operation_id`
   - Category: ORCHESTRATION

7. **monitor_orchestrator_health** - Monitor orchestrator health and metrics
   - Location: `cortex/mcp/tools/orchestration/__init__.py`
   - Parameters: `orchestrator_id`
   - Category: ORCHESTRATION

8. **optimize_orchestrator_config** - Optimize orchestrator configuration
   - Location: `cortex/mcp/tools/orchestration/__init__.py`
   - Parameters: `orchestrator_id`, `optimization_type`
   - Category: ORCHESTRATION

9. **diagnose_orchestrator_issues** - Diagnose issues in orchestrator operation
   - Location: `cortex/mcp/tools/orchestration/__init__.py`
   - Parameters: `orchestrator_id`
   - Category: ORCHESTRATION

### Knowledge Tools (3 tools)
10. **search_knowledge_base** - Search knowledge base for relevant information
    - Location: `cortex/mcp/tools/knowledge/__init__.py`
    - Parameters: `query`, `domain`
    - Category: KNOWLEDGE

11. **analyze_knowledge_gap** - Analyze gaps in knowledge coverage
    - Location: `cortex/mcp/tools/knowledge/__init__.py`
    - Parameters: `domain`, `scope`
    - Category: KNOWLEDGE

12. **generate_knowledge_summary** - Generate knowledge summary for a domain
    - Location: `cortex/mcp/tools/knowledge/__init__.py`
    - Parameters: `domain`, `detail_level`
    - Category: KNOWLEDGE

### Utility Tools (3 tools)
13. **echo_tool** - Echo tool for testing MCP connectivity
    - Location: `cortex/mcp/tools/utility/__init__.py`
    - Parameters: `message`
    - Category: UTILITY

14. **sample_tool** - Sample tool demonstrating basic MCP functionality
    - Location: `cortex/mcp/tools/utility/__init__.py`
    - Parameters: `input`
    - Category: UTILITY

15. **transform_tool** - Transform data using specified transformation
    - Location: `cortex/mcp/tools/utility/__init__.py`
    - Parameters: `data`, `transformation`
    - Category: UTILITY

---

## Current Implementation Status

### IOrchestrator Interface Status
✅ Already has abstract method: `get_mcp_tools() -> Any`

```python
@abstractmethod
def get_mcp_tools(self) -> Any:
    """Get available MCP tools.

    Returns:
        Result[Dict[str, Any]] with tool definitions.
    """
    pass
```

### Orchestrators Currently Implementing get_mcp_tools()
- ✅ MasterOrchestrator (3+ tools)
- ✅ PlanningOrchestrator (some tools)
- ✅ RefactoringOrchestrator (some tools)
- ✅ SeleniumPlaywrightOrchestrator (some tools)
- ✅ IntentRouter (some tools)

### Orchestrators Missing get_mcp_tools() Implementation
- ❌ InteractionOrchestrator (from WIRE-001)
- ❌ TDDOrchestrator (from WIRE-001)
- ❌ WorkflowOrchestrator (from WIRE-001)
- ❌ WrappedTDDOrchestrator (from WIRE-001)
- ❌ OrchestratorBootstrap (from WIRE-001)
- ❌ 13+ domain orchestrators (from WIRE-002)
- ❌ 6 support orchestrators (from WIRE-003)

**Total Missing:** 18 orchestrators need get_mcp_tools() implementation

---

## Implementation Strategy

### Step 1: Create Unified MCP Tools Registry
**File:** Create `cortex/orchestrators/mcp_tools_registry.py`

```python
class MCPToolsRegistry:
    """Central registry for all MCP tools"""
    
    GOVERNANCE_TOOLS = [
        "query_governance_context",
        "validate_governance_compliance",
        "execute_governance_check",
        "analyze_governance_impact",
        "report_governance_status",
    ]
    
    ORCHESTRATION_TOOLS = [
        "get_operation_status",
        "monitor_orchestrator_health",
        "optimize_orchestrator_config",
        "diagnose_orchestrator_issues",
    ]
    
    KNOWLEDGE_TOOLS = [
        "search_knowledge_base",
        "analyze_knowledge_gap",
        "generate_knowledge_summary",
    ]
    
    UTILITY_TOOLS = [
        "echo_tool",
        "sample_tool",
        "transform_tool",
    ]
    
    @staticmethod
    def get_all_tools():
        """Return all 15 tools"""
        return {
            "governance": MCPToolsRegistry.GOVERNANCE_TOOLS,
            "orchestration": MCPToolsRegistry.ORCHESTRATION_TOOLS,
            "knowledge": MCPToolsRegistry.KNOWLEDGE_TOOLS,
            "utility": MCPToolsRegistry.UTILITY_TOOLS,
        }
```

### Step 2: Add Default Implementation to OrchestratorBase

**File:** `cortex/core/orchestrator/orchestrator_base.py`

Add this method to the base class so all orchestrators inherit it:

```python
def get_mcp_tools(self) -> Dict[str, Any]:
    """Get available MCP tools for this orchestrator.
    
    Default implementation returns tools based on orchestrator type.
    Subclasses can override to customize tool exposure.
    
    Returns:
        Dict mapping tool categories to lists of tool names
    """
    from cortex.orchestrators.mcp_tools_registry import MCPToolsRegistry
    
    # Default: expose all tools to all orchestrators
    # Subclasses can override for more granular control
    all_tools = MCPToolsRegistry.get_all_tools()
    
    return {
        "status": "ok",
        "orchestrator": self.get_name(),
        "tools": all_tools,
        "total_tools": 15,
    }
```

### Step 3: Wire MCPServer.list_tools() to Orchestrator Discovery

**File:** `cortex/mcp/server.py`

Replace the static list_tools() with dynamic discovery:

```python
def list_tools(self) -> Dict[str, Any]:
    """List all available MCP tools from all orchestrators.
    
    Queries the MasterOrchestrator registry to discover tools
    exposed by all 23 registered orchestrators.
    
    Returns:
        Dict with consolidated tool list from all orchestrators
    """
    from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
    
    master = MasterOrchestrator.instance()
    all_tools = []
    
    # Get wiring registry to iterate all orchestrators
    from cortex.orchestrators.core.orchestrator_wiring import get_wiring_registry
    registry = get_wiring_registry()
    
    # Query each orchestrator for its tools
    for domain, metadata in registry.wired_orchestrators.items():
        orchestrator = metadata.orchestrator
        
        # Call get_mcp_tools() on each orchestrator
        if hasattr(orchestrator, 'get_mcp_tools'):
            tools_result = orchestrator.get_mcp_tools()
            
            if tools_result and not tools_result.get("error"):
                tools = tools_result.get("tools", {})
                all_tools.extend(self._flatten_tools(tools, domain))
    
    return {
        "status": "ok",
        "total_tools": len(all_tools),
        "total_orchestrators_queried": len(registry.wired_orchestrators),
        "tools": all_tools,
    }

def _flatten_tools(self, tools: Dict, orchestrator_domain: str) -> list:
    """Flatten nested tool structure into flat list"""
    flat = []
    for category, tool_names in tools.items():
        for tool_name in tool_names:
            flat.append({
                "name": tool_name,
                "category": category,
                "orchestrator_domain": orchestrator_domain,
            })
    return flat
```

### Step 4: Update Specific Orchestrators (if needed)

Some orchestrators may want to expose only specific tools:

```python
class TDDOrchestrator(IOrchestrator):
    """TDD-focused orchestrator"""
    
    def get_mcp_tools(self) -> Dict[str, Any]:
        """TDD orchestrator exposes governance, knowledge, and orchestration tools"""
        return {
            "status": "ok",
            "orchestrator": "TDDOrchestrator",
            "tools": {
                "governance": MCPToolsRegistry.GOVERNANCE_TOOLS,
                "knowledge": MCPToolsRegistry.KNOWLEDGE_TOOLS,
                "orchestration": MCPToolsRegistry.ORCHESTRATION_TOOLS,
            },
            "total_tools": 12,  # Everything except utility tools
        }
```

---

## Implementation Phases

### Phase 3a: Create MCP Tools Registry (30 min)
- [ ] Create `cortex/orchestrators/mcp_tools_registry.py`
- [ ] Define all 15 tools with metadata
- [ ] Add validation methods

### Phase 3b: Update OrchestratorBase (30 min)
- [ ] Add default get_mcp_tools() implementation
- [ ] Ensure Result[Dict] return type
- [ ] Add docstrings

### Phase 3c: Update MCPServer (45 min)
- [ ] Modify list_tools() method
- [ ] Add orchestrator discovery logic
- [ ] Add tool flattening helper

### Phase 3d: Test & Validation (45 min)
- [ ] Run test_mcp_exposure.py suite
- [ ] Verify all 15 tools discoverable
- [ ] Test with sample orchestrators

---

## Success Criteria

- ✅ All 15 MCP tools cataloged and registered
- ✅ All 23 orchestrators have get_mcp_tools() implementation (via inheritance)
- ✅ MCPServer.list_tools() returns all 15 tools
- ✅ Tool discovery tests pass
- ✅ Each orchestrator can customize tool exposure
- ✅ Unified interface for tool discovery

---

## Testing Strategy

**Test File:** `tests/unit/orchestrators/test_mcp_exposure.py`

Tests should validate:
1. All 15 tools cataloged in registry
2. Each orchestrator returns valid tool list
3. MCPServer.list_tools() returns all tools
4. Tool categories correct
5. No duplicate tools
6. Tool metadata complete

---

## Git Workflow

```bash
# After completion:
git add cortex/orchestrators/mcp_tools_registry.py
git add cortex/core/orchestrator/orchestrator_base.py
git add cortex/mcp/server.py
git commit -m "AC_MCP-EXPOSURE-001: Implement MCP tools discovery and exposure"
```

---
