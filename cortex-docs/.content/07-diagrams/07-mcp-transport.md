# MCP Transport

---
title: MCP Transport Diagram
type: diagram
audience: [Software Developers]
last_verified: 2026-02-25
source_of_truth: cortex/mcp/ + .vscode/settings.json
order: 7
---

## stdio Transport Flow

```
┌─────────────────────────────────────────────────────────┐
│                    VS CODE                              │
│                                                         │
│  ┌──────────────────┐     ┌──────────────────────────┐  │
│  │   Copilot Chat   │     │  .vscode/settings.json   │  │
│  │                  │     │  mcpServers.cortex:       │  │
│  │  User types:     │     │    command: python3       │  │
│  │  "Implement      │     │    args: [-m, cortex.mcp] │  │
│  │   user auth"     │     │    transport: stdio       │  │
│  └────────┬─────────┘     └──────────────────────────┘  │
│           │                                             │
│           │ 1. Generate tool call                       │
│           ▼                                             │
│  ┌──────────────────┐                                   │
│  │  MCP Client      │                                   │
│  │  (in VS Code)    │                                   │
│  └────────┬─────────┘                                   │
└───────────┼─────────────────────────────────────────────┘
            │
            │ 2. JSON-RPC 2.0 over stdin
            │
            │  {"jsonrpc":"2.0","method":"tools/call",
            │   "params":{"name":"cortex_process_request",
            │   "arguments":{"operation":"implement",
            │   "request":"user auth"}},"id":1}
            │
            ▼
┌───────────────────────────────────────────────────────┐
│                 MCP SERVER PROCESS                     │
│           python3 -m cortex.mcp                       │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  stdin reader → JSON-RPC parser                 │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                  │
│                    ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Tool Registry → Find "cortex_process_request"  │  │
│  │  Validate parameters                            │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                  │
│                    ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  CortexProcessRequest.execute(args)             │  │
│  │  → MasterOrchestrator 4-stage pipeline          │  │
│  │  → IntentRouter → TDDOrchestrator               │  │
│  │  → Governance + Audit                           │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                  │
│                    ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ToolResult → JSON-RPC response                 │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                  │
└────────────────────┼──────────────────────────────────┘
                     │
                     │ 3. JSON-RPC 2.0 over stdout
                     │
                     │  {"jsonrpc":"2.0","result":{
                     │   "content":[{"type":"text",
                     │   "text":"Implementation complete..."}]
                     │  },"id":1}
                     │
                     ▼
┌───────────────────────────────────────────────────────┐
│                    VS CODE                            │
│  ┌──────────────────┐                                 │
│  │   Copilot Chat   │                                 │
│  │                  │                                 │
│  │  Displays result │                                 │
│  │  to user         │                                 │
│  └──────────────────┘                                 │
└───────────────────────────────────────────────────────┘
```

## Lifecycle Management

```
VS Code Opens Workspace
    │
    ├── 1. Read .vscode/settings.json
    ├── 2. Find mcpServers.cortex config
    ├── 3. Spawn: python3 -m cortex.mcp
    ├── 4. Connect stdin/stdout
    ├── 5. Send tools/list → receive 23 tools
    │
    │   [normal operation — tool calls as needed]
    │
    ├── 6. VS Code closes
    └── 7. MCP server process terminates
```

---

*Verified against MCP stdio transport implementation · 25 February 2026*
