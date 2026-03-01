---
id: architecture-mcp-gateway
title: MCP gateway architecture (stdio)
purpose: Explain how IDE clients invoke CORTEX tools via MCP over stdio.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/mcp/
  - .vscode/settings.json
last_verified: 2026-03-01
diagram_type: Architecture
render: ascii
---

# MCP Gateway Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            IDE INTEGRATION                                       │
│                                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐               │
│  │    VS Code      │    │     Cursor      │    │ Claude Desktop  │               │
│  │ .vscode/        │    │ .cursor/        │    │ config.json     │               │
│  │ settings.json   │    │ mcp.json        │    │                 │               │
│  │ mcpServers:     │    │ cortex:         │    │ cortex:         │               │
│  │  cortex:        │    │  command:       │    │  command:       │               │
│  │   command:      │    │   python3       │    │   python3       │               │
│  │    python3      │    │  args: -m ...   │    │  args: -m ...   │               │
│  │   args: -m ...  │    │  transport:     │    │  transport:     │               │
│  │   transport:    │    │   stdio         │    │   stdio         │               │
│  │    stdio        │    │                 │    │                 │               │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘               │
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
│  │                             TOOL REGISTRY                                  │  │
│  │                                                                            │  │
│  │  Categories: routing · governance · intelligence · audit · testing · docs   │  │
│  │                                                                            │  │
│  │  Tool Call Flow:                                                           │  │
│  │  stdin → JSON parse → tool lookup → validate → orchestrate → stdout        │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
```
