---
id: architecture-mcp-gateway
title: MCP gateway architecture (stdio + HTTP transport)
purpose: Explain how IDE clients invoke CORTEX tools via MCP over stdio, and how authenticated HTTP transport (Phase 99) enables secure programmatic access.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/mcp/
  - cortex/mcp/http_transport.py
  - cortex/secrets/
  - .vscode/settings.json
  - .github/templates/cortex-response-templates.md
last_verified: 2026-03-02
diagram_type: Architecture
render: ascii
response_header_enhancement:
  feature: Intent-aligned business/engineering quote in every response header
  library: BLOCK-QUOTE-LIBRARY
  library_location: .github/templates/cortex-response-templates.md § BLOCK-QUOTE-LIBRARY
  quote_count: 32
  themes: [quality, improvement, security, architecture, discipline, systems-thinking, strategy, flow, learning, universal]
  selection_mechanism: >
    IntentRouter intent classification drives theme selection at response-emit time.
    The same routing decision that selects the orchestrator selects the quote theme.
    TDD/testing → quality · security → security · refactor → improvement ·
    architecture/design → architecture · audit/governance → discipline ·
    fix/debug → systems-thinking · plan/roadmap → strategy · team/process → flow ·
    learn/digest → learning · default → universal
  format: |
    ## {icon} CORTEX {mode}
    **Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.

    > *"{quote}"*
    > — {Author}, **{Book}**

    ---
  governance_anchor: >
    Quote sources are co-located with governance rule book_reference fields in
    cortex-registry/core/tier0-skull/skull-rules.yaml and VBP-013 in
    cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml.
    No quote may be fabricated outside the BLOCK-QUOTE-LIBRARY.
---

# MCP Gateway Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            IDE INTEGRATION (stdio)                               │
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
│  │  Categories: routing · governance · intelligence · audit · testing · docs   │
  │  Tool count: 30 registered tools · 31 tool files in cortex/mcp/tools/     │  │
│  │                                                                            │  │
│  │  Tool Call Flow:                                                           │  │
│  │  stdin → JSON parse → tool lookup → validate → orchestrate → stdout        │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│          HTTP TRANSPORT — Phase 99 (Secure Programmatic Access)                  │
│                                                                                  │
│  External Client ──── HTTPS ───► FastAPI App (cortex/mcp/http_transport.py)     │
│                        + API Key (X-API-Key header, constant-time validation)    │
│                              │                                                   │
│  Public endpoints:           ├── /health          ← no auth required            │
│                              └── /health/ready    ← no auth required            │
│                                                                                  │
│  Authenticated endpoints:    ├── POST /tools/list ← ApiKeyAuthMiddleware         │
│                              └── POST /tools/call ← ApiKeyAuthMiddleware         │
│                                              │                                   │
│                              SecretsManager (cortex/secrets/)                    │
│                              generate_api_key() · validate_api_key()             │
│                              revoke_api_key()   · list_api_keys()                │
└──────────────────────────────────────────────────────────────────────────────────┘
```

