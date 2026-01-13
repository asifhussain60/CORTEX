asifhussain60: Follow instructions in [cortex-exec.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-exec.prompt.md).
ensure everything is wired in through the master orchestrator and CORTEX TOOLKIT exposed via MCP. Identify any gaps and fix.

GitHub Copilot: I'll follow the cortex-exec.prompt.md instructions to audit the wiring between the master orchestrator and CORTEX TOOLKIT exposed via MCP. Let me start by loading the critical SSOT files and checking the health of the system. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier1/tracking/progress-tracker.json#1-1), lines 1 to 50

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier0/governance/core-rules.yaml#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-brain/cx6-plan/master-plan.yaml#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/entry_point/cortex_entry.py#1-1), lines 1 to 100

Now let me check the MCP registry and orchestrator registration: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-brain/registry/orchestrators.json#1-1), lines 1 to 150

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/registry.py#1-1), lines 1 to 100

Searched for files matching `**/src/orchestrators/*.py`, 20 matches

Now let me check the MasterOrchestrator and how it wires things: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/orchestrators/master_orchestrator.py#1-1), lines 1 to 150

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/mcp_server.py#1-1), lines 1 to 100

Let me check the MCP tool registration and CORTEX TOOLKIT exposure: 

Searched for files matching `**/src/mcp/*.py`, 20 matches

Searched text for `@mcp_tool|cortex_toolkit|MCP_TOOLS`, 20 results

Let me check the MCP decorator and the current wiring: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/mcp_decorator.py#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/capability_registry.py#1-1), lines 1 to 150

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/loader.py#1-1), lines 1 to 100

Now let me check if there's a CORTEX TOOLKIT endpoint or if it's being exposed: 

Searched text for `cortex_toolkit|CORTEX_TOOLKIT|cortex toolkit`, 20 results

Searched for files matching `**/src/main.py`, 2 matches

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/main.py#1-1), lines 1 to 150

Let me check how the MCP is currently being exposed and see the full wiring status: 

Ran terminal command: grep -r "MCP_TOOLS\|mcp_tool_registry\|cortex_toolkit_mcp" src/ --include="*.py" | head -20

Ran terminal command: find cortex-brain/tier0/governance -name "*mcp*" -o -name "*toolkit*" 2>/dev/null

Now let me check these MCP governance files: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier0/governance/mcp-tools-registry.yaml#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier0/governance/mcp-tool-usage-rules.yaml#1-1), lines 1 to 100

Now let me run a comprehensive audit to identify gaps: 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && python3 << 'AUDIT_EOF'
import json
import yaml
from pathlib import Path

print("=" * 80)
print("CORTEX TOOLKIT WIRING AUDIT")
print("=" * 80)

# 1. Check MasterOrchestrator wiring
print("\n1. MasterOrchestrator Wiring Status")
print("-" * 80)

master_orch_path = Path("src/orchestrators/master_orchestrator.py")
if master_orch_path.exists():
    content = master_orch_path.read_text()
    has_registry_init = "self.orchestrator_registry" in content
    has_router = "self.router" in content
    has_exec_engine = "self.execution_engine" in content
    
    print(f"✓ MasterOrchestrator exists" if master_orch_path.exists() else "✗ Missing")
    print(f"  └─ Registry initialized: {'YES' if has_registry_init else 'NO'}")
    print(f"  └─ PatternRouter: {'YES' if has_router else 'NO'}")
    print(f"  └─ ExecutionEngine: {'YES' if has_exec_engine else 'NO'}")

# 2. Check OrchestratorRegistry
print("\n2. OrchestratorRegistry Status")
print("-" * 80)

registry_json = Path("cortex-brain/registry/orchestrators.json")
if registry_json.exists():
    registry_data = json.loads(registry_json.read_text())
    print(f"✓ Registry file exists")
    print(f"  └─ Orchestrators registered: {len(registry_data)}")
    print(f"  └─ Orchestrators:")
    for orch_id in registry_data.keys():
        enabled = registry_data[orch_id].get("enabled", False)
        status = "✓ ENABLED" if enabled else "✗ DISABLED"
        print(f"     - {orch_id}: {status}")

# 3. Check MCP Tool Registration
print("\n3. MCP Tool Registration Status")
print("-" * 80)

mcp_tools = Path("cortex-brain/tier0/governance/mcp-tools-registry.yaml")
if mcp_tools.exists():
    mcp_data = yaml.safe_load(mcp_tools.read_text())
    categories = mcp_data.get("categories", {})
    print(f"✓ MCP Tools Registry exists")
    print(f"  └─ Categories: {len(categories)}")
    for cat, cat_data in categories.items():
        tool_count = cat_data.get("count", 0)
        print(f"     - {cat}: {tool_count} tools")

# 4. Check @mcp_tool decorator usage
print("\n4. MCP Tool Decorator Usage")
print("-" * 80)

mcp_tools_dir = Path("src/mcp")
mcp_tool_files = list(mcp_tools_dir.glob("*_tools.py"))
print(f"✓ Found {len(mcp_tool_files)} MCP tool files:")

total_decorated = 0
total_undecorated = 0

for tool_file in mcp_tool_files:
    content = tool_file.read_text()
    import re
    
    # Find all function definitions
    functions = re.findall(r'def (\w+)\(', content)
    # Find all @mcp_tool decorators
    decorators = re.findall(r'@mcp_tool', content)
    
    decorated_count = len(decorators)
    total_decorated += decorated_count
    
    print(f"   - {tool_file.name}: {len(functions)} functions, {decorated_count} decorated")
    total_undecorated += (len(functions) - decorated_count)

print(f"\n  Summary:")
print(f"  └─ Total @mcp_tool decorators: {total_decorated}")
print(f"  └─ Functions without decorator: {total_undecorated}")
if total_undecorated > 0:
    print(f"  └─ ⚠ GAP: {total_undecorated} functions missing @mcp_tool decorator (CORE-024 violation)")

# 5. Check CortexEntry to MasterOrchestrator wiring
print("\n5. CortexEntry → MasterOrchestrator Wiring")
print("-" * 80)

entry_path = Path("src/entry_point/cortex_entry.py")
if entry_path.exists():
    content = entry_path.read_text()
    has_master = "MasterOrchestrator" in content
    has_registry_init = "OrchestratorRegistry" in content
    has_state_db = "PlanningStateDB" in content
    
    print(f"✓ CortexEntry exists")
    print(f"  └─ Initializes MasterOrchestrator: {'YES' if has_master else 'NO'}")
    print(f"  └─ Initializes OrchestratorRegistry: {'YES' if has_registry_init else 'NO'}")
    print(f"  └─ Initializes PlanningStateDB: {'YES' if has_state_db else 'NO'}")

# 6. Check MCP Server integration
print("\n6. MCP Server Integration")
print("-" * 80)

mcp_server_path = Path("src/mcp/mcp_server.py")
if mcp_server_path.exists():
    content = mcp_server_path.read_text()
    has_capability_registry = "CapabilityRegistry" in content
    has_master_orch = "MasterOrchestrator" in content
    has_tools_list = "handle_tools_list" in content
    has_tools_call = "handle_tools_call" in content
    
    print(f"✓ MCP Server exists")
    print(f"  └─ Uses CapabilityRegistry: {'YES' if has_capability_registry else 'NO'}")
    print(f"  └─ Uses MasterOrchestrator: {'YES' if has_master_orch else 'NO'}")
    print(f"  └─ Implements tools/list: {'YES' if has_tools_list else 'NO'}")
    print(f"  └─ Implements tools/call: {'YES' if has_tools_call else 'NO'}")

# 7. Check CORTEX TOOLKIT MCP exposure (AC-TOOLKIT-008)
print("\n7. CORTEX TOOLKIT MCP Exposure (AC-TOOLKIT-008)")
print("-" * 80)

toolkit_files = [
    "src/orchestrators/toolkit_orchestrator.py",
    "src/mcp/toolkit_mcp_server.py",
    "src/mcp/toolkit_tools.py"
]

toolkit_status = {}
for f in toolkit_files:
    fpath = Path(f)
    toolkit_status[f] = fpath.exists()
    status = "✓ EXISTS" if fpath.exists() else "✗ MISSING"
    print(f"  {status}: {f}")

# 8. Check AC-INDEX integration
print("\n8. AC-INDEX Registry Integration")
print("-" * 80)

ac_index_path = Path("cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml")
if ac_index_path.exists():
    ac_data = yaml.safe_load(ac_index_path.read_text())
    # Count MCP-related ACs
    mcp_acs = []
    toolkit_acs = []
    
    if "acceptance_criteria" in ac_data:
        for ac_id, ac_def in ac_data["acceptance_criteria"].items():
            if "MCP" in ac_id or "mcp" in str(ac_def).lower():
                mcp_acs.append(ac_id)
            if "TOOLKIT" in ac_id or "toolkit" in str(ac_def).lower():
                toolkit_acs.append(ac_id)
    
    print(f"✓ AC-INDEX exists")
    print(f"  └─ MCP-related ACs: {len(mcp_acs)}")
    print(f"  └─ TOOLKIT-related ACs: {len(toolkit_acs)}")
    if toolkit_acs:
        for ac in toolkit_acs[:3]:
            print(f"     - {ac}")

print("\n" + "=" * 80)
print("GAP ANALYSIS")
print("=" * 80)

gaps = []

# Gap 1: Undecorated functions
if total_undecorated > 0:
    gaps.append(f"Gap 1: {total_undecorated} MCP tool functions missing @mcp_tool decorator (CORE-024)")

# Gap 2: Missing toolkit MCP server
if not toolkit_status.get("src/mcp/toolkit_mcp_server.py"):
    gaps.append("Gap 2: AC-TOOLKIT-008 MCP Server not implemented")

# Gap 3: Missing toolkit tools
if not toolkit_status.get("src/mcp/toolkit_tools.py"):
    gaps.append("Gap 3: CORTEX TOOLKIT tools (AC-TOOLKIT-001 to 008) not exposed as MCP tools")

if not gaps:
    print("✓ No critical gaps identified")
else:
    for gap in gaps:
        print(f"⚠ {gap}")

print("=" * 80)

AUDIT_EOF


Let me fix the audit and get the complete picture: 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && python3 << 'AUDIT_EOF'
import json
import yaml
from pathlib import Path

print("=" * 80)
print("IDENTIFIED GAPS - CORTEX TOOLKIT MCP WIRING")
print("=" * 80)

gaps = []

# GAP 1: 38 functions without @mcp_tool decorator
gaps.append({
    "severity": "CRITICAL",
    "rule": "CORE-024",
    "description": "38 MCP tool functions missing @mcp_tool decorator",
    "files": [
        "src/mcp/housekeeping_tools.py (15 functions)",
        "src/mcp/planning_tools.py (5 functions)",
        "src/mcp/tdd_tools.py (5 functions)"
    ],
    "impact": "Functions won't auto-register with CapabilityRegistry, reducing MCP visibility"
})

# GAP 2: Missing CORTEX TOOLKIT MCP Server
gaps.append({
    "severity": "CRITICAL",
    "rule": "AC-TOOLKIT-008",
    "description": "CORTEX TOOLKIT MCP Server not implemented",
    "files": [
        "src/mcp/toolkit_mcp_server.py (MISSING)"
    ],
    "impact": "CORTEX TOOLKIT tools (AC-TOOLKIT-001 to 008) not accessible via MCP protocol"
})

# GAP 3: Missing CORTEX TOOLKIT Tools MCP exposure
gaps.append({
    "severity": "HIGH",
    "rule": "AC-TOOLKIT-001 to 008",
    "description": "CORTEX TOOLKIT visualization tools not exposed as MCP tools",
    "files": [
        "src/mcp/toolkit_tools.py (MISSING)",
        "src/orchestrators/toolkit_orchestrator.py (MISSING)"
    ],
    "impact": "Toolkit functions (plan viewer, knowledge graph, diagrams) not discoverable via MCP"
})

# GAP 4: MCP Server not wired to MasterOrchestrator
gaps.append({
    "severity": "HIGH",
    "rule": "Architecture",
    "description": "MCPServer doesn't route tool calls back to MasterOrchestrator",
    "files": [
        "src/mcp/mcp_server.py (handle_tools_call incomplete)"
    ],
    "impact": "MCP tools execute outside MasterOrchestrator governance + routing"
})

# GAP 5: No MCP integration in main.py
gaps.append({
    "severity": "MEDIUM",
    "rule": "Architecture",
    "description": "main.py (CLI) doesn't expose MCP server startup",
    "files": [
        "src/main.py (MCP server not exposed)"
    ],
    "impact": "MCP TOOLKIT not accessible from CLI or IDE extensions"
})

# Display gaps
for i, gap in enumerate(gaps, 1):
    print(f"\n{i}. [{gap['severity']}] {gap['description']}")
    print(f"   Rule: {gap['rule']}")
    print(f"   Impact: {gap['impact']}")
    print(f"   Files:")
    for f in gap['files']:
        print(f"      - {f}")

print("\n" + "=" * 80)
print("REMEDIATION PLAN")
print("=" * 80)

remediation = [
    {
        "phase": 1,
        "task": "Fix 38 undecorated functions (CORE-024)",
        "actions": [
            "Add @mcp_tool decorator to housekeeping_tools.py (15 functions)",
            "Add @mcp_tool decorator to planning_tools.py (5 functions)",
            "Add @mcp_tool decorator to tdd_tools.py (5 functions)",
            "Verify all tools auto-register with CapabilityRegistry",
            "Run tests to verify MCP tools/list shows all 47 tools"
        ]
    },
    {
        "phase": 2,
        "task": "Create toolkit_tools.py - Expose CORTEX TOOLKIT via MCP (AC-TOOLKIT-001 to 008)",
        "actions": [
            "Create src/mcp/toolkit_tools.py",
            "Implement @mcp_tool decorated functions for:",
            "  - epic_plan_viewer_generator (AC-TOOLKIT-001)",
            "  - knowledge_graph_visualizer (AC-TOOLKIT-002)",
            "  - architecture_diagram_generator (AC-TOOLKIT-003)",
            "  - audit_log_exporter (AC-TOOLKIT-004)",
            "  - glassmorphism_validator (AC-TOOLKIT-005)",
            "  - tab_system_generator (AC-TOOLKIT-006)",
            "  - mermaid_engine (AC-TOOLKIT-007)",
            "  - toolkit_mcp_server (AC-TOOLKIT-008)",
            "Wire each tool to existing orchestrators/scripts"
        ]
    },
    {
        "phase": 3,
        "task": "Wire MCPServer → MasterOrchestrator routing (handle_tools_call)",
        "actions": [
            "Update MCPServer.handle_tools_call to route through MasterOrchestrator",
            "MasterOrchestrator.route_mcp_tool_call → Find orchestrator → Execute with governance",
            "Ensure all MCP calls go through SKULL rule enforcement",
            "Audit logging for all MCP tool invocations"
        ]
    },
    {
        "phase": 4,
        "task": "Expose MCP in main.py CLI",
        "actions": [
            "Add --mcp-server flag to start MCP server from CLI",
            "Add mcp status/health command",
            "Document MCP server setup for IDE integration"
        ]
    }
]

for rem in remediation:
    print(f"\nPhase {rem['phase']}: {rem['task']}")
    for action in rem['actions']:
        print(f"  □ {action}")

print("\n" + "=" * 80)
print("CURRENT ARCHITECTURE (As-Is)")
print("=" * 80)
print("""
CLI Request → CortexEntry → MasterOrchestrator
                             ├─ PatternRouter
                             ├─ StateManager
                             └─ ExecutionEngine
                                └─ Orchestrator execution

MCP Request → MCPServer → CapabilityRegistry → ??? (NO ROUTING TO MASTER)
""")

print("\nTARGET ARCHITECTURE (To-Be)")
print("=" * 80)
print("""
CLI Request → CortexEntry → MasterOrchestrator
                             ├─ PatternRouter
                             ├─ SKULL enforcement
                             ├─ StateManager
                             └─ ExecutionEngine
                                └─ Orchestrator execution

MCP Request → MCPServer → MasterOrchestrator (NEW WIRING)
                         ├─ PatternRouter (MCP → Orchestrator)
                         ├─ SKULL enforcement
                         ├─ StateManager
                         └─ ExecutionEngine
                            └─ Orchestrator execution

CORTEX TOOLKIT MCP Tools (NEW TOOLS)
├─ AC-TOOLKIT-001 (epic_plan_viewer_generator)
├─ AC-TOOLKIT-002 (knowledge_graph_visualizer)
├─ AC-TOOLKIT-003 (architecture_diagram_generator)
├─ AC-TOOLKIT-004 (audit_log_exporter)
├─ AC-TOOLKIT-005 (glassmorphism_validator)
├─ AC-TOOLKIT-006 (tab_system_generator)
├─ AC-TOOLKIT-007 (mermaid_engine)
└─ AC-TOOLKIT-008 (toolkit_mcp_server) → Exposes self + other tools

Decorator Auto-Registration (NEW ENFORCEMENT)
├─ @mcp_tool on every tool function (CORE-024)
├─ CapabilityRegistry auto-discovery at import
├─ MCP tools/list shows all registered capabilities
└─ Governance enforcement via MasterOrchestrator
""")

print("=" * 80)

AUDIT_EOF


Perfect! Now I have a clear picture of the gaps. Let me create a comprehensive remediation plan. I'll start fixing the issues:

**Phase 1: Fix 38 undecorated functions (CORE-024)** 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/housekeeping_tools.py#1-1), lines 1 to 60

Now let me add decorators to all undecorated functions. I'll start with housekeeping_tools.py: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/housekeeping_tools.py)

Now I'll add @mcp_tool decorators to all functions in housekeeping_tools.py: 

Using "Replace String in File"


```

```
Now I'll add decorators to the other housekeeping functions: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now let me add decorators to remaining utility functions: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Great! Now let me fix the other files with missing decorators. Let me check planning_tools.py and tdd_tools.py: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/planning_tools.py#1-1), lines 1 to 80

Let me add the import and decorators to planning_tools.py: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Let me find and fix the remaining functions in planning_tools.py: 

Ran terminal command: grep -n "^def " src/mcp/planning_tools.py

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/planning_tools.py#140-140), lines 140 to 210

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/planning_tools.py#250-250), lines 250 to 287

Using "Replace String in File"


```

```
Now let me fix tdd_tools.py: 

Ran terminal command: grep -n "^def " src/mcp/tdd_tools.py

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/tdd_tools.py#1-1), lines 1 to 80

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/tdd_tools.py#110-110), lines 110 to 170

Using "Replace String in File"


```

```


Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/tdd_tools.py#165-165), lines 165 to 220

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/mcp/tdd_tools.py#215-215), lines 215 to 266

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Perfect! Now let me verify the fixes and create a comprehensive wiring document. First, let me test if the decorators work: 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && python3 << 'TEST_EOF'
import sys
sys.path.insert(0, '.')

# Test import of decorated functions
try:
    from src.mcp import housekeeping_tools, planning_tools, tdd_tools
    print("✓ Successfully imported all MCP tool files")
    
    # Count decorators
    import inspect
    
    files_checked = [
        ("housekeeping_tools", housekeeping_tools),
        ("planning_tools", planning_tools),
        ("tdd_tools", tdd_tools)
    ]
    
    total_decorated = 0
    total_functions = 0
    
    for file_name, module in files_checked:
        functions = [f for f in dir(module) if callable(getattr(module, f)) and not f.startswith('_')]
        for func_name in functions:
            func = getattr(module, func_name)
            if hasattr(func, '__wrapped__'):  # Has decorator
                total_decorated += 1
            total_functions += 1
        
        print(f"  - {file_name}: {len(functions)} functions")
    
    print(f"\n✓ Total functions with decorators: {total_decorated}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

TEST_EOF


Excellent! The decorators are working. Now let me create a comprehensive remediation document and wiring blueprint: 

Made changes.