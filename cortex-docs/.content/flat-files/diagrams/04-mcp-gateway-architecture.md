# MCP Gateway Architecture
# stdio transport, tool registry, and IDE integration

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            IDE INTEGRATION                                       │
│                                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐               │
│  │    VS Code      │    │     Cursor      │    │ Claude Desktop  │               │
│  │                 │    │                 │    │                 │               │
│  │ .vscode/        │    │ .cursor/        │    │ claude_desktop_ │               │
│  │ settings.json   │    │ mcp.json        │    │ config.json     │               │
│  │                 │    │                 │    │                 │               │
│  │ mcpServers:     │    │ cortex:         │    │ cortex:         │               │
│  │  cortex:        │    │  command:       │    │  command:       │               │
│  │   command:      │    │   python3       │    │   python3       │               │
│  │    python3      │    │  args:          │    │  args:          │               │
│  │   args:         │    │   -m cortex.mcp │    │   -m cortex.mcp │               │
│  │    -m cortex.mcp│    │  transport:     │    │                 │               │
│  │   transport:    │    │   stdio         │    │                 │               │
│  │    stdio        │    │                 │    │                 │               │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘               │
│           │                      │                      │                        │
│           └──────────────────────┼──────────────────────┘                        │
│                                  │                                               │
│                        JSON-RPC 2.0 over stdio                                   │
└──────────────────────────────────┼───────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         MCP SERVER PROCESS                                       │
│                    python3 -m cortex.mcp                                         │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                   TOOL REGISTRY (28 registered / 39 target)               │  │
│  │                                                                            │  │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────────┐  │  │
│  │  │ CORE & ROUTING     │  │ GOVERNANCE         │  │ INTELLIGENCE         │  │  │
│  │  │ cortex_classify    │  │ cortex_governance  │  │ cortex_challenge     │  │  │
│  │  │ cortex_orchestrator│  │ cortex_load        │  │ cortex_refactor      │  │  │
│  │  │ cortex_request_    │  │ cortex_validate    │  │ cortex_vision        │  │  │
│  │  │   lifecycle        │  │ cortex_check       │  │ cortex_knowledge     │  │  │
│  │  └────────────────────┘  └────────────────────┘  │ cortex_total_recall  │  │  │
│  │                                                  └──────────────────────┘  │  │
│  │  ┌────────────────────┐  ┌────────────────────┐                            │  │
│  │  │ PLANNING & AUDIT   │  │ TESTING & QUALITY  │  ┌──────────────────────┐  │  │
│  │  │ cortex_audit_plan  │  │ cortex_gen_tests   │  │ DIAGNOSTICS          │  │  │
│  │  │ cortex_onboard     │  │ cortex_tdd         │  │ cortex_verify        │  │  │
│  │  │ cortex_onboard_v3  │  │                    │  │ cortex_debug         │  │  │
│  │  └────────────────────┘  └────────────────────┘  │ cortex_ask           │  │  │
│  │                                                  │ cortex_metrics       │  │  │
│  │  ┌────────────────────┐  ┌────────────────────┐  └──────────────────────┘  │  │
│  │  │ AUTOMATION         │  │ MAINTENANCE        │                            │  │
│  │  │ cortex_workflow    │  │ cortex_vacuum      │  ┌──────────────────────┐  │  │
│  │  │ cortex_capture_    │  │ cortex_transform   │  │ VCS & DOCS           │  │  │
│  │  │   metrics          │  │                    │  │ cortex_git           │  │  │
│  │  └────────────────────┘  └────────────────────┘  │ cortex_dashboard     │  │  │
│  │                                                  │ cortex_tools_cat    │  │  │
│  │  Note: 11 additional tools in active planning   │ cortex_landing_page │  │  │
│  │  phases (target: 39 registered)                 └──────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  Tool Call Flow:                                                                 │
│  stdin → JSON parse → Tool Registry lookup → Parameter validation →              │
│  Tool.execute() → MasterOrchestrator pipeline → ToolResult → stdout              │
└──────────────────────────────────────────────────────────────────────────────────┘
```
