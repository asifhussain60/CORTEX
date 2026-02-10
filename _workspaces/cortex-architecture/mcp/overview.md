# MCP Overview

**Purpose:** The neural protocol that connects minds to the CORTEX brain  
**Audience:** All Technical Stakeholders  
**Last Updated:** 2026-02-10

---

## Overview

**MCP: The Neural Interface to the CORTEX Brain**

Just as the human nervous system uses electrical signals to communicate between the brain and the body, CORTEX uses the **Model Context Protocol (MCP)** as its neural communication system. MCP creates a **standardized neural pathway** that allows any AI assistant, development tool, or automation system to connect to and communicate with the CORTEX brain.

**Think of MCP as the Nervous System:**
- **🧠 Brain (CORTEX)** ↔ **⚡ Neural Signals (JSON-RPC)** ↔ **🖐️ Body (Client Tools)**
- **Consistent Communication** → All interactions use the same "neural language"
- **Secure Transmission** → Built-in authentication and validation like the blood-brain barrier
- **Bidirectional Flow** → Information flows both ways between brain and external tools
- **Extensible Network** → New connections can be added without changing existing pathways

**The Result:** Any system can tap into CORTEX's intelligence using standard protocols—no custom integration required.

```
┌─────────────────────────────────────────────────────────────────┐
│              🧠 MCP NEURAL COMMUNICATION SYSTEM                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              🖐️ External Body (Clients)                  │   │
│  │         (Development tools & AI assistants)             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ VS Code  │  │   CLI    │  │  Custom  │              │   │
│  │  │ Copilot  │  │  Tools   │  │   APIs   │              │   │
│  │  │   🤖     │  │   ⚙️     │  │   🔧     │              │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘              │   │
│  └───────┼─────────────┼─────────────┼─────────────────────┘   │
│          │             │             │                          │
│          └─────────────┴─────────────┘                          │
│                        │                                         │
│                ⚡ Neural Signals                                 │
│                (JSON-RPC 2.0 Protocol)                          │
│                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               🧠 CORTEX BRAIN INTERFACE                  │   │
│  │                 (MCP Server)                            │   │
│  │                                                          │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │            ⚡ Neural Signal Router                │   │   │
│  │  │      (Directs signals to brain regions)          │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                        │                                 │   │
│  │  ┌─────────┬──────────┼──────────┬─────────┐           │   │
│  │  │         │          │          │         │            │   │
│  │  ▼         ▼          ▼          ▼         ▼            │   │
│  │  ┌───────┐ ┌────────┐ ┌────────┐ ┌───────┐ ┌────────┐ │   │
│  │  │ Core  │ │Analysis│ │Planning│ │Govern.│ │ Debug  │ │   │
│  │  │ Tools │ │ Tools  │ │ Tools  │ │ Tools │ │ Tools  │ │   │
│  │  └───────┘ └────────┘ └────────┘ └───────┘ └────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### D3.js MCP Protocol Flow

```json
{
  "type": "protocol_sequence",
  "title": "MCP Neural Communication Protocol",
  "phases": [
    {
      "name": "🤝 Neural Handshake",
      "steps": [
        {
          "client": "VS Code Copilot",
          "action": "Connect to MCP Server",
          "protocol": "JSON-RPC 2.0 over WebSocket/HTTP",
          "payload": {"jsonrpc": "2.0", "method": "initialize", "params": {"capabilities": ["tools"]}}
        },
        {
          "server": "CORTEX Brain",
          "action": "Send Capabilities",
          "payload": {"tools": [{"name": "cortex_process_request", "description": "Main request processor"}]}
        },
        {
          "client": "VS Code Copilot", 
          "action": "Acknowledge",
          "payload": {"jsonrpc": "2.0", "method": "initialized", "params": {}}
        }
      ]
    },
    {
      "name": "🧠 Cognitive Request",
      "steps": [
        {
          "client": "VS Code Copilot",
          "action": "Send Thought",
          "method": "tools/call",
          "payload": {
            "name": "cortex_process_request",
            "arguments": {
              "operation": "implement",
              "request": "Add user authentication to the API",
              "context": {"file_path": "src/api/auth.py", "language": "python"}
            }
          }
        },
        {
          "server": "CORTEX Brain",
          "action": "Process Neural Signal", 
          "internal_flow": [
            "Route to MasterOrchestrator",
            "Classify intent via IntentRouter", 
            "Analyze context via LENS",
            "Execute via TDDOrchestrator",
            "Apply governance checks"
          ]
        },
        {
          "server": "CORTEX Brain",
          "action": "Return Intelligence",
          "payload": {
            "result": {
              "status": "success",
              "implementation": "Generated auth code with tests",
              "tests_created": 8,
              "coverage": "94%",
              "audit_trail": "AC_START: AC-AUTH-001..."
            }
          }
        }
      ]
    }
  ]
}
```

### D3.js Tool Ecosystem Map

```json
{
  "type": "ecosystem_map", 
  "title": "MCP Tool Neural Network",
  "center": {"name": "🧠 MCP Server", "size": 100},
  "tool_categories": [
    {
      "name": "🧠 Core Cognitive Tools",
      "color": "#4CAF50",
      "tools": [
        {"name": "cortex_process_request", "usage": 450, "success_rate": 97.2},
        {"name": "cortex_challenge", "usage": 120, "success_rate": 94.8},
        {"name": "cortex_total_recall", "usage": 85, "success_rate": 96.1},
        {"name": "cortex_lens_analyze", "usage": 380, "success_rate": 95.7}
      ]
    },
    {
      "name": "🔍 Analysis & Intelligence", 
      "color": "#2196F3",
      "tools": [
        {"name": "cortex_git_history", "usage": 220, "success_rate": 98.9},
        {"name": "cortex_ast_analyze", "usage": 195, "success_rate": 97.3},
        {"name": "cortex_detect_duplicates", "usage": 140, "success_rate": 93.4},
        {"name": "cortex_pattern_analysis", "usage": 165, "success_rate": 91.8}
      ]
    },
    {
      "name": "📅 Planning & Strategy",
      "color": "#FF9800", 
      "tools": [
        {"name": "cortex_plan_setup", "usage": 95, "success_rate": 89.2},
        {"name": "cortex_plan_teardown", "usage": 78, "success_rate": 92.1},
        {"name": "cortex_plan_resolve", "usage": 65, "success_rate": 88.7},
        {"name": "cortex_plan_sync", "usage": 55, "success_rate": 94.3}
      ]
    },
    {
      "name": "🛡️ Governance & Quality",
      "color": "#E91E63",
      "tools": [
        {"name": "cortex_audit", "usage": 180, "success_rate": 99.1},
        {"name": "cortex_governance_check", "usage": 210, "success_rate": 98.7},
        {"name": "cortex_security_scan", "usage": 145, "success_rate": 96.8},
        {"name": "cortex_compliance_validate", "usage": 125, "success_rate": 97.9}
      ]
    }
  ]
}
```

### Real-time MCP Metrics

```json
{
  "type": "real_time_metrics",
  "title": "MCP Neural Activity Monitor", 
  "update_frequency": "1s",
  "metrics": [
    {
      "name": "Neural Signal Rate",
      "type": "line_chart",
      "current_value": 847,
      "unit": "requests/min",
      "trend": "+12%",
      "history": [820, 835, 842, 847, 851, 848, 847]
    },
    {
      "name": "Cognitive Response Time",
      "type": "histogram",
      "p50": "245ms",
      "p95": "890ms", 
      "p99": "1.2s",
      "distribution": [
        {"range": "0-100ms", "count": 145},
        {"range": "100-500ms", "count": 423},
        {"range": "500ms-1s", "count": 186},
        {"range": "1s-2s", "count": 67},
        {"range": "2s+", "count": 12}
      ]
    },
    {
      "name": "Tool Usage Heat Map",
      "type": "heatmap",
      "data": {
        "hours": ["00", "04", "08", "12", "16", "20"],
        "tools": [
          {"name": "process_request", "values": [45, 120, 380, 450, 420, 180]},
          {"name": "lens_analyze", "values": [25, 85, 280, 380, 350, 150]},
          {"name": "git_history", "values": [15, 45, 180, 220, 195, 95]},
          {"name": "audit", "values": [30, 55, 145, 180, 160, 85]}
        ]
      }
    }
  ]
}
```
│  │  ┌───┐   ┌───┐      ┌───┐      ┌───┐    ┌───┐         │   │
│  │  │T1 │   │T2 │      │T3 │      │T4 │    │TN │         │   │
│  │  └───┘   └───┘      └───┘      └───┘    └───┘         │   │
│  │  35+ MCP Tools                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                        │                                         │
│                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Orchestrators                           │   │
│  │              (23 registered)                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## MCP-First Architecture

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Single Interface** | All operations via MCP tools |
| **No Direct Imports** | CORTEX = SaaS, not a library |
| **Tool-Based Access** | Every capability is a tool |
| **Protocol Compliance** | JSON-RPC 2.0 standard |

### Why MCP-First?

```
Traditional Library Approach:
  from cortex.lens import analyze
  result = analyze("file.py")  # Direct import
  
MCP-First Approach:
  POST /mcp {"method": "tools/call", "params": {"name": "cortex_lens_analyze"}}
```

**Benefits:**
- ✅ Consistent API surface
- ✅ Built-in governance enforcement
- ✅ Audit trails for every operation
- ✅ Security gates applied uniformly
- ✅ Version management
- ✅ Rate limiting

---

## Core Concepts

### Tools

A **tool** is a discrete capability exposed via MCP:

```python
# Tool Definition
{
    "name": "cortex_lens_analyze",
    "description": "Perform comprehensive code analysis",
    "inputSchema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "analyzers": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["target"]
    }
}
```

### Requests

Clients invoke tools via JSON-RPC requests:

```json
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "cortex_lens_analyze",
        "arguments": {
            "target": "src/auth/service.py",
            "analyzers": ["git", "ast"]
        }
    },
    "id": "req-001"
}
```

### Responses

Tools return structured responses:

```json
{
    "jsonrpc": "2.0",
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Analysis complete. Found 3 issues."
            }
        ],
        "data": {
            "issues": [...],
            "metrics": {...}
        }
    },
    "id": "req-001"
}
```

### Errors

Errors follow JSON-RPC conventions:

```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32004,
        "message": "Governance validation failed",
        "data": {
            "violations": [
                {"rule": "CORE-008", "message": "Tests required"}
            ]
        }
    },
    "id": "req-001"
}
```

---

## Benefits

### For Developers

| Benefit | Description |
|---------|-------------|
| Consistent API | Same interface for all tools |
| Self-Documenting | Tool schemas describe usage |
| IDE Integration | Works with VS Code Copilot |
| Error Handling | Standard error format |

### For Operations

| Benefit | Description |
|---------|-------------|
| Observability | All calls logged and traced |
| Rate Limiting | Built-in throttling |
| Security | Uniform authentication |
| Versioning | Tool version management |

### For Governance

| Benefit | Description |
|---------|-------------|
| Audit Trail | Every call recorded |
| Policy Enforcement | Gates on every operation |
| Compliance | CORE rules applied |
| Visibility | Full operation history |

---

## Quick Start

### Start MCP Server

```bash
# Development
python -m cortex.mcp.server

# Production
uvicorn cortex.mcp.server:app --host 0.0.0.0 --port 8000
```

### List Available Tools

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

### Call a Tool

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "cortex_lens_analyze",
        "arguments": {
            "target": "src/app.py"
        }
    },
    "id": 1
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
# {"status": "healthy", "orchestrators": 23, "tools": 35}
```

---

## Related Documents

- [MCP Protocol](protocol.md) — Protocol details
- [Tools Catalog](tools-catalog.md) — All tools
- [Integration Guide](integration.md) — Client integration
- [Versioning](versioning.md) — Version management

---

*Part of CORTEX Architecture Documentation*
