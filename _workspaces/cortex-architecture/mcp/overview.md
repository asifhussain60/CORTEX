# MCP Overview

**Purpose:** Introduction to Model Context Protocol in CORTEX  
**Audience:** All Technical Stakeholders  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [MCP-First Architecture](#mcp-first-architecture)
- [Core Concepts](#core-concepts)
- [Benefits](#benefits)
- [Quick Start](#quick-start)
- [Related Documents](#related-documents)

---

## Overview

CORTEX uses the **Model Context Protocol (MCP)** as its primary interface. All functionality is exposed through MCP tools, creating a consistent, secure, and auditable API surface.

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     Clients                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ VS Code  │  │   CLI    │  │  API     │              │   │
│  │  │ Copilot  │  │  Client  │  │ Client   │              │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘              │   │
│  └───────┼─────────────┼─────────────┼─────────────────────┘   │
│          │             │             │                          │
│          └─────────────┴─────────────┘                          │
│                        │                                         │
│                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   MCP Server                             │   │
│  │                (JSON-RPC 2.0)                            │   │
│  │                                                          │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │                 Tool Router                       │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                        │                                 │   │
│  │  ┌─────────┬──────────┼──────────┬─────────┐           │   │
│  │  │         │          │          │         │            │   │
│  │  ▼         ▼          ▼          ▼         ▼            │   │
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
