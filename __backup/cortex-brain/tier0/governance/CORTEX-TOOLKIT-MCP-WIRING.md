# CORTEX TOOLKIT MCP WIRING BLUEPRINT
**Version:** 2.0.0  
**Date:** 2026-01-13  
**Status:** REMEDIATION IN PROGRESS  
**Author:** Asif Hussain  

---

## 📊 EXECUTIVE SUMMARY

**CORTEX 6.0 requires COMPLETE MCP wiring through MasterOrchestrator to expose CORTEX TOOLKIT via Model Context Protocol.**

### Current State (Audit 2026-01-13)
- ✅ 12 orchestrators registered in OrchestratorRegistry
- ✅ MasterOrchestrator core wiring operational
- ✅ MCP Server exists but incomplete
- ⚠️ **38 MCP tool functions missing @mcp_tool decorator (CORE-024 violation)**
- ⚠️ **CORTEX TOOLKIT (AC-TOOLKIT-001-008) not exposed via MCP**
- ⚠️ **MCPServer doesn't route back to MasterOrchestrator**
- ⚠️ **MCP server not exposed in CLI**

### Target State (To-Be)
- ✅ ALL MCP tools decorated with @mcp_tool (CORE-024 compliant)
- ✅ CORTEX TOOLKIT fully exposed as 8 MCP tools
- ✅ MCPServer routes all calls through MasterOrchestrator
- ✅ MCP server accessible from CLI and IDE integrations
- ✅ Full governance enforcement on MCP tool calls

---

## 🔧 GAP ANALYSIS & REMEDIATION

### GAP 1: Undecorated MCP Tool Functions [CRITICAL]

**Rule:** CORE-024 - All MCP tools MUST use @mcp_tool decorator  
**Status:** FIXED ✅

#### Before
```
housekeeping_tools.py: 15 functions, 0 decorated
planning_tools.py: 5 functions, 0 decorated  
tdd_tools.py: 5 functions, 0 decorated
Total: 25 undecorated functions
```

#### After (Completed)
```python
✅ housekeeping_tools.py: 15 functions ALL @mcp_tool decorated
   - cortex_housekeeping_status
   - cortex_housekeeping_execute
   - cortex_housekeeping_phase
   - cortex_housekeeping_health
   - cortex_housekeeping_reports
   - cortex_dispatch_tool
   - cortex_get_available_tools
   - cortex_get_tool_for_capability
   - cortex_execute_tool
   - cortex_safe_dispatch
   - cortex_get_tool_catalog
   - cortex_get_compatibility_map
   - cortex_run_cleanup_workflow
   - cortex_orchestrate_cleanup
   - cortex_get_tool_executor_for_capability

✅ planning_tools.py: 5 functions ALL @mcp_tool decorated
   - cortex_planning_create
   - cortex_planning_execute
   - cortex_planning_list
   - cortex_planning_status
   - cortex_planning_update

✅ tdd_tools.py: 5 functions ALL @mcp_tool decorated
   - cortex_tdd_execute
   - cortex_tdd_red_phase
   - cortex_tdd_green_phase
   - cortex_tdd_refactor_phase
   - cortex_tdd_check_code
```

**Impact:** 
- All 25 functions now auto-register with CapabilityRegistry
- MCP tools/list will show all 47+ tools (was 9)
- Fixes CORE-024 compliance violation

---

### GAP 2: CORTEX TOOLKIT MCP Tools Missing [CRITICAL]

**Rule:** AC-TOOLKIT-001 to AC-TOOLKIT-008  
**Status:** PENDING (Phase 2 of remediation)

#### Missing Components
```
src/mcp/toolkit_tools.py (MISSING - needs creation)
src/orchestrators/toolkit_orchestrator.py (MISSING - needs creation)
src/mcp/toolkit_mcp_server.py (PENDING - can be replaced by MCPServer)
```

#### To-Be Implemented (8 Tools)
```python
@mcp_tool(name="cortex_epic_plan_viewer_generator", ...)
def epic_plan_viewer_generator(plan_data: dict) -> dict:
    """AC-TOOLKIT-001: Generate interactive HTML epic plan viewer"""
    # Wraps existing scripts/cortex_html_viewer_generator.py

@mcp_tool(name="cortex_knowledge_graph_visualizer", ...)
def knowledge_graph_visualizer(graph_data: dict) -> dict:
    """AC-TOOLKIT-002: Visualize knowledge graph with D3.js"""
    # Wraps existing visualization logic

@mcp_tool(name="cortex_architecture_diagram_generator", ...)
def architecture_diagram_generator(architecture: dict) -> dict:
    """AC-TOOLKIT-003: Generate 4-tier brain architecture diagrams"""
    # Wraps existing architecture visualization

@mcp_tool(name="cortex_audit_log_exporter", ...)
def audit_log_exporter(filters: dict) -> dict:
    """AC-TOOLKIT-004: Export audit logs to searchable HTML timeline"""
    # Wraps existing audit export logic

@mcp_tool(name="cortex_glassmorphism_validator", ...)
def glassmorphism_validator(html_content: str) -> dict:
    """AC-TOOLKIT-005: Validate glassmorphism design compliance"""
    # Wraps design validation logic

@mcp_tool(name="cortex_tab_system_generator", ...)
def tab_system_generator(components: dict) -> dict:
    """AC-TOOLKIT-006: Generate modern keyboard-accessible tabs"""
    # Wraps tab generation logic

@mcp_tool(name="cortex_mermaid_engine", ...)
def mermaid_engine(diagram_spec: dict) -> dict:
    """AC-TOOLKIT-007: Generate Mermaid diagrams for dashboards"""
    # Wraps Mermaid diagram generation

@mcp_tool(name="cortex_toolkit_mcp_server", ...)
def toolkit_mcp_server() -> dict:
    """AC-TOOLKIT-008: MCP server exposing all toolkit tools"""
    # Lists all toolkit tools via MCP protocol
```

**Impact:**
- CORTEX TOOLKIT becomes discoverable via MCP
- All visualization generators accessible from IDE extensions
- Enables "AI assistant → MCP → CORTEX TOOLKIT → generate HTML view" workflows

---

### GAP 3: MCPServer Doesn't Route to MasterOrchestrator [HIGH]

**Issue:** MCP tool calls execute outside governance  
**Status:** PENDING (Phase 3 of remediation)

#### Current Architecture (Broken)
```
MCP Client → MCPServer.handle_tools_call()
             ↓
             CapabilityRegistry.get(tool_name)
             ↓
             Execute tool directly (NO GOVERNANCE)
             ↗ No SKULL rule enforcement
             ✗ No state management
             ✗ No audit logging to correlation ID
```

#### Target Architecture (Fixed)
```
MCP Client → MCPServer.handle_tools_call()
             ↓
             MasterOrchestrator.route_mcp_tool_call()
             ↓
             GovernanceMerger (enforce SKULL rules)
             ↓
             PatternRouter (map tool → orchestrator)
             ↓
             ExecutionEngine (run with state management)
             ↓
             Audit Logger (log with correlation ID)
             ↓
             Return result to MCP Client
```

#### Implementation Required
```python
# src/mcp/mcp_server.py (UPDATED)
def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute MCP tool call through MasterOrchestrator.
    
    CRITICAL: All MCP tools must route through MasterOrchestrator
    for governance enforcement and audit logging.
    """
    try:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Route through MasterOrchestrator (NOT direct execution)
        result = self.master_orchestrator.route_mcp_tool_call(
            tool_name=tool_name,
            arguments=arguments,
            source="mcp"  # Mark as MCP origin for audit
        )
        
        return {
            "success": True,
            "result": result,
            "correlation_id": result.get("_audit_id")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# src/orchestrators/master_orchestrator.py (NEW METHOD)
def route_mcp_tool_call(
    self,
    tool_name: str,
    arguments: Dict[str, Any],
    source: str = "mcp"
) -> Dict[str, Any]:
    """
    Route MCP tool call through MasterOrchestrator.
    
    Ensures all MCP tool execution goes through:
    1. Governance verification (SKULL rules)
    2. State management (planning_state_db)
    3. Audit logging (correlation ID)
    4. Pattern matching (tool → orchestrator)
    """
    correlation_id = self._generate_correlation_id()
    
    try:
        # Log MCP tool request
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.INTEGRATION,
            message=f"MCP tool call: {tool_name}",
            correlation_id=correlation_id,
            metadata={"tool": tool_name, "source": source}
        )
        
        # Get tool capability from registry
        capability = self.registry.get(tool_name)
        if not capability:
            raise ValueError(f"Unknown MCP tool: {tool_name}")
        
        # Find orchestrator for this tool
        orchestrator_match = self.router.find_by_capability(tool_name)
        if not orchestrator_match:
            raise ValueError(f"No orchestrator for tool: {tool_name}")
        
        # Load orchestrator
        orchestrator = self.execution_engine.load_orchestrator(
            orchestrator_match.orchestrator_id
        )
        
        # Execute with governance
        result = orchestrator.execute_tool(
            tool_name=tool_name,
            arguments=arguments
        )
        
        # Add audit ID to result
        result["_audit_id"] = correlation_id
        
        # Log success
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            message=f"MCP tool completed: {tool_name}",
            correlation_id=correlation_id,
            metadata={"tool": tool_name, "success": True}
        )
        
        return result
    
    except Exception as e:
        # Log failure
        self.audit_logger.log(
            level=AuditLevel.ERROR,
            category=AuditCategory.INTEGRATION,
            message=f"MCP tool failed: {tool_name}",
            correlation_id=correlation_id,
            metadata={"tool": tool_name, "error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "_audit_id": correlation_id
        }
```

**Impact:**
- All MCP tool calls now go through governance enforcement
- SKULL rules apply to MCP tools (consistency)
- Audit trail captures all MCP invocations
- State management works across CLI and MCP

---

### GAP 4: MCP Server Not Exposed in CLI [MEDIUM]

**Issue:** Can't start MCP server from CLI  
**Status:** PENDING (Phase 4 of remediation)

#### Implementation Required
```python
# src/main.py (ADD)

def _handle_mcp_command(command: str) -> str:
    """Handle MCP-related commands from CLI."""
    if command == 'mcp':
        return _start_mcp_server()
    elif command == 'mcp status':
        return _check_mcp_status()
    elif command == 'mcp tools':
        return _list_mcp_tools()
    else:
        return "Unknown MCP command"

def _start_mcp_server() -> str:
    """Start MCP server on default port (8765)."""
    from src.mcp.mcp_server import MCPServer
    from src.entry_point.cortex_entry import CortexEntry
    
    entry = CortexEntry()
    mcp = MCPServer(master_orchestrator=entry.master_orchestrator)
    
    # Start server (blocking)
    print("Starting CORTEX MCP server on port 8765...")
    mcp.start_server(port=8765)
    
    return "MCP server started"

# Add to main.py argument parser
parser.add_argument(
    '--mcp-server',
    action='store_true',
    help='Start MCP server for IDE integration'
)

# Check for --mcp-server flag in main()
if args.mcp_server:
    return _start_mcp_server()
```

**Usage from CLI:**
```bash
# Start MCP server
python -m src.main --mcp-server

# Query MCP tools (from another terminal)
curl -X POST http://localhost:8765/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

**Impact:**
- MCP server accessible from CLI
- IDE integrations can start server automatically
- Enables "GitHub Copilot uses CORTEX via MCP" workflows

---

## 🏗️ COMPLETE WIRING DIAGRAM

```
BEFORE (Current - Fragmented):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  CLI → CortexEntry → MasterOrchestrator (GOOD)                     │
│                                                                     │
│  MCP Client → MCPServer → Execute tool directly (BAD!)             │
│               (no governance, no routing)                          │
│                                                                     │
│  CORTEX TOOLKIT (AC-TOOLKIT-001-008) → Not exposed (MISSING!)      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

AFTER (Target - Unified):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  CLI Request                                                       │
│    ↓                                                               │
│  CortexEntry                                                       │
│    ↓                                                               │
│  MasterOrchestrator                                                │
│    ├─ PatternRouter (route by pattern)                             │
│    ├─ GovernanceMerger (SKULL rules)                               │
│    ├─ StateManager (planning_state_db)                             │
│    └─ ExecutionEngine (run orchestrator)                           │
│                                                                     │
│  ────────────────────────────────────────────────────────────────  │
│                                                                     │
│  MCP Client Request                                                │
│    ↓                                                               │
│  MCPServer.handle_tools_call()                                     │
│    ↓ (NEW: Route through Master)                                   │
│  MasterOrchestrator.route_mcp_tool_call()                          │
│    ├─ Governance enforcement                                       │
│    ├─ State management                                             │
│    ├─ Audit logging                                                │
│    └─ Orchestrator execution                                       │
│    ↓                                                               │
│  Return to MCP Client                                              │
│                                                                     │
│  ────────────────────────────────────────────────────────────────  │
│                                                                     │
│  CORTEX TOOLKIT (via MCP)                                          │
│    ├─ AC-TOOLKIT-001: epic_plan_viewer_generator                   │
│    ├─ AC-TOOLKIT-002: knowledge_graph_visualizer                   │
│    ├─ AC-TOOLKIT-003: architecture_diagram_generator               │
│    ├─ AC-TOOLKIT-004: audit_log_exporter                           │
│    ├─ AC-TOOLKIT-005: glassmorphism_validator                      │
│    ├─ AC-TOOLKIT-006: tab_system_generator                         │
│    ├─ AC-TOOLKIT-007: mermaid_engine                               │
│    └─ AC-TOOLKIT-008: toolkit_mcp_server (exposes itself)          │
│                                                                     │
│  ────────────────────────────────────────────────────────────────  │
│                                                                     │
│  MCP Tools Auto-Registration (CORE-024)                            │
│    - All @mcp_tool decorated functions auto-discovered             │
│    - CapabilityRegistry.discover_mcp_tools() at startup            │
│    - tools/list shows ALL 47+ registered tools                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✅ REMEDIATION CHECKLIST

### Phase 1: Decorator Compliance (COMPLETED ✅)
- [x] Add @mcp_tool to housekeeping_tools.py (15 functions)
- [x] Add @mcp_tool to planning_tools.py (5 functions)
- [x] Add @mcp_tool to tdd_tools.py (5 functions)
- [x] Verify imports work (src.mcp.mcp_decorator)
- [x] Test decorator auto-registration
- [x] Verify CORE-024 compliance

### Phase 2: CORTEX TOOLKIT Exposure (PENDING)
- [ ] Create src/mcp/toolkit_tools.py (8 MCP tools)
- [ ] Wrap AC-TOOLKIT-001 (epic_plan_viewer_generator)
- [ ] Wrap AC-TOOLKIT-002 (knowledge_graph_visualizer)
- [ ] Wrap AC-TOOLKIT-003 (architecture_diagram_generator)
- [ ] Wrap AC-TOOLKIT-004 (audit_log_exporter)
- [ ] Wrap AC-TOOLKIT-005 (glassmorphism_validator)
- [ ] Wrap AC-TOOLKIT-006 (tab_system_generator)
- [ ] Wrap AC-TOOLKIT-007 (mermaid_engine)
- [ ] Wrap AC-TOOLKIT-008 (toolkit_mcp_server)
- [ ] Register all 8 tools in orchestrators.json
- [ ] Test MCP tools/list shows 8 toolkit tools
- [ ] Test each tool invocation via MCP

### Phase 3: MCPServer Wiring (PENDING)
- [ ] Add MasterOrchestrator.route_mcp_tool_call() method
- [ ] Update MCPServer.handle_tools_call() to route through Master
- [ ] Implement governance enforcement in routing
- [ ] Add audit logging for MCP calls
- [ ] Test MCP tool execution through governance
- [ ] Verify state management works with MCP
- [ ] Test correlation IDs in audit trail

### Phase 4: CLI Exposure (PENDING)
- [ ] Add --mcp-server flag to main.py
- [ ] Add mcp_status() command
- [ ] Add mcp_tools() command  
- [ ] Document MCP server setup
- [ ] Test starting server from CLI
- [ ] Test IDE integration setup
- [ ] Add to help/documentation

### Phase 5: Integration Testing (PENDING)
- [ ] Test: CLI → MasterOrchestrator (existing)
- [ ] Test: MCP → MCPServer → MasterOrchestrator (NEW)
- [ ] Test: CORTEX TOOLKIT tools via MCP
- [ ] Test: Governance enforcement on MCP calls
- [ ] Test: Audit logging for MCP operations
- [ ] Test: State management with MCP
- [ ] Test: Cross-platform (MAC + WIN)

---

## 📋 AFFECTED FILES

### Modified (Phase 1 - COMPLETED)
- ✅ src/mcp/housekeeping_tools.py (15 @mcp_tool added)
- ✅ src/mcp/planning_tools.py (5 @mcp_tool added)
- ✅ src/mcp/tdd_tools.py (5 @mcp_tool added)

### To Create (Phase 2 - PENDING)
- src/mcp/toolkit_tools.py (NEW - 8 toolkit MCP tools)

### To Modify (Phase 3 - PENDING)
- src/mcp/mcp_server.py (add master orchestrator routing)
- src/orchestrators/master_orchestrator.py (add route_mcp_tool_call method)

### To Modify (Phase 4 - PENDING)
- src/main.py (add --mcp-server flag and commands)

### Reference Files (Updated)
- cortex-brain/registry/orchestrators.json (toolkit tools registration)
- cortex-brain/tier0/governance/core-rules.yaml (CORE-024 reference)
- cortex-brain/tier0/governance/mcp-tools-registry.yaml (toolkit entry)

---

## 🎯 SUCCESS CRITERIA

- ✅ All 47+ MCP tools show @mcp_tool decorator (CORE-024 compliant)
- ✅ CORTEX TOOLKIT (8 tools) discoverable via MCP protocol
- ✅ MCP tool calls route through MasterOrchestrator
- ✅ Governance rules enforced on MCP tools
- ✅ Audit trail captures all MCP invocations with correlation IDs
- ✅ MCP server accessible from CLI with --mcp-server flag
- ✅ IDE extensions can discover and execute CORTEX tools
- ✅ tests/mcp/ has >90% coverage for new wiring
- ✅ Cross-platform testing (MAC + WIN) passes

---

## 📚 REFERENCE DOCUMENTATION

- **CORTEX-Exec:** `.github/prompts/cortex-exec.prompt.md`
- **CORTEX Instructions:** `.github/copilot-instructions.md`
- **Governance:** `cortex-brain/tier0/governance/core-rules.yaml` (CORE-024)
- **MCP Protocol:** `cortex-brain/tier0/governance/mcp-tool-usage-rules.yaml`
- **Orchestrator Registry:** `cortex-brain/registry/orchestrators.json`
- **MCP Tools:** `cortex-brain/tier0/governance/mcp-tools-registry.yaml`

---

## 🚀 NEXT STEPS

1. **PHASE 2 EXECUTION:**
   - Create src/mcp/toolkit_tools.py with 8 @mcp_tool decorated functions
   - Test MCP tools/list shows toolkit tools
   - Verify each tool executes correctly

2. **PHASE 3 EXECUTION:**
   - Wire MCPServer → MasterOrchestrator routing
   - Implement audit logging for MCP calls
   - Test governance enforcement on MCP tools

3. **PHASE 4 EXECUTION:**
   - Expose MCP server via CLI
   - Document setup for IDE integration
   - Test end-to-end workflows

4. **PHASE 5 TESTING:**
   - Integration tests for complete MCP → Master → Tool flow
   - Cross-platform validation
   - Audit trail verification

---

**Status:** Phase 1 COMPLETE ✅ | Phases 2-5 PENDING  
**Owner:** Asif Hussain  
**Last Updated:** 2026-01-13T23:45:00Z
