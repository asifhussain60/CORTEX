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
│  │                        TOOL REGISTRY (39 tools)                            │  │
│  │                                                                            │  │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────────┐  │  │
│  │  │ CORE & ROUTING     │  │ GOVERNANCE         │  │ INTELLIGENCE         │  │  │
│  │  │ cortex_classify    │  │ cortex_governance  │  │ cortex_brain_query   │  │  │
│  │  │ cortex_orchestrator│  │ cortex_load        │  │ cortex_challenge     │  │  │
│  │  │ cortex_request_    │  │ cortex_validate    │  │ cortex_refactor      │  │  │
│  │  │   lifecycle        │  │ cortex_check       │  │ cortex_vision        │  │  │
│  │  └────────────────────┘  └────────────────────┘  │ cortex_knowledge     │  │  │
│  │                                                  │ cortex_total_recall  │  │  │
│  │  ┌────────────────────┐  ┌────────────────────┐  └──────────────────────┘  │  │
│  │  │ PLANNING & AUDIT   │  │ TESTING & QUALITY  │                            │  │
│  │  │ cortex_master_plan │  │ cortex_gen_tests   │  ┌──────────────────────┐  │  │
│  │  │ cortex_plan        │  │ cortex_score_tests │  │ DIAGNOSTICS          │  │  │
│  │  │ cortex_onboard     │  │                    │  │ cortex_health_scan   │  │  │
│  │  │ cortex_query_opj   │  └────────────────────┘  │ cortex_verify        │  │  │
│  │  └────────────────────┘                          │ cortex_debug         │  │  │
│  │                                                  │ cortex_ask           │  │  │
│  │  ┌────────────────────┐  ┌────────────────────┐  │ cortex_metrics       │  │  │
│  │  │ AUTOMATION         │  │ MAINTENANCE        │  └──────────────────────┘  │  │
│  │  │ cortex_workflow    │  │ cortex_vacuum      │                            │  │
│  │  │ cortex_list_wf_    │  │ cortex_vacuum_exec │  ┌──────────────────────┐  │  │
│  │  │   templates        │  │                    │  │ TOOLKIT              │  │  │
│  │  │ cortex_scaffold    │  └────────────────────┘  │ cortex_batch_xform   │  │  │
│  │  └────────────────────┘                          │ cortex_enrich        │  │  │
│  │                          ┌────────────────────┐  │ cortex_scan          │  │  │
│  │                          │ VCS & DOCS         │  │ cortex_bulk_digest   │  │  │
│  │                          │ cortex_git         │  │ cortex_sweep_status  │  │  │
│  │                          │ cortex_dashboard   │  └──────────────────────┘  │  │
│  │                          │ cortex_tools_cat   │                            │  │
│  │                          └────────────────────┘                            │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  Tool Call Flow:                                                                 │
│  stdin → JSON parse → Tool Registry lookup → Parameter validation →              │
│  Tool.execute() → MasterOrchestrator pipeline → ToolResult → stdout              │
└──────────────────────────────────────────────────────────────────────────────────┘
```
