# MCP Protocol

**Purpose:** Detailed MCP protocol specification  
**Audience:** Developers, Integration Engineers  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [JSON-RPC 2.0](#json-rpc-20)
- [MCP Methods](#mcp-methods)
- [Message Format](#message-format)
- [Error Codes](#error-codes)
- [Transport](#transport)
- [Related Documents](#related-documents)

---

## Overview

CORTEX implements the Model Context Protocol using JSON-RPC 2.0 over HTTP and WebSocket transports.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP PROTOCOL STACK                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Application Layer                                       │   │
│  │  • Tool invocation                                       │   │
│  │  • Resource access                                       │   │
│  │  • Prompt handling                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Protocol Layer                                          │   │
│  │  • JSON-RPC 2.0                                          │   │
│  │  • Request/Response                                      │   │
│  │  • Notifications                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Transport Layer                                         │   │
│  │  • HTTP POST                                             │   │
│  │  • WebSocket                                             │   │
│  │  • stdio (CLI)                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## JSON-RPC 2.0

### Specification

MCP uses JSON-RPC 2.0 as defined in the [official specification](https://www.jsonrpc.org/specification).

### Request Object

```json
{
    "jsonrpc": "2.0",
    "method": "method_name",
    "params": { ... },
    "id": "unique-id"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `jsonrpc` | string | Yes | Must be "2.0" |
| `method` | string | Yes | Method name |
| `params` | object/array | No | Method parameters |
| `id` | string/number | Yes* | Request identifier |

*Omit `id` for notifications (no response expected)

### Response Object

```json
{
    "jsonrpc": "2.0",
    "result": { ... },
    "id": "unique-id"
}
```

### Error Object

```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32600,
        "message": "Invalid Request",
        "data": { ... }
    },
    "id": "unique-id"
}
```

---

## MCP Methods

### Tool Methods

| Method | Purpose |
|--------|---------|
| `tools/list` | List available tools |
| `tools/call` | Invoke a tool |

### Resource Methods

| Method | Purpose |
|--------|---------|
| `resources/list` | List resources |
| `resources/read` | Read a resource |
| `resources/subscribe` | Subscribe to changes |

### Prompt Methods

| Method | Purpose |
|--------|---------|
| `prompts/list` | List prompts |
| `prompts/get` | Get a prompt |

### Lifecycle Methods

| Method | Purpose |
|--------|---------|
| `initialize` | Initialize connection |
| `ping` | Health check |
| `shutdown` | Graceful shutdown |

---

## Message Format

### tools/list

**Request:**
```json
{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "tools": [
            {
                "name": "cortex_lens_analyze",
                "description": "Perform comprehensive code analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "File or directory to analyze"
                        },
                        "analyzers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific analyzers to use"
                        }
                    },
                    "required": ["target"]
                }
            }
        ]
    },
    "id": 1
}
```

### tools/call

**Request:**
```json
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "cortex_lens_analyze",
        "arguments": {
            "target": "src/auth/service.py",
            "analyzers": ["git", "ast", "comments"]
        }
    },
    "id": 2
}
```

**Response (Success):**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Analysis completed for src/auth/service.py"
            }
        ],
        "isError": false,
        "_meta": {
            "audit_id": "AUDIT-2026-02-10-001",
            "duration_ms": 150
        }
    },
    "id": 2
}
```

**Response (Error):**
```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32004,
        "message": "Governance validation failed",
        "data": {
            "violations": [
                {
                    "rule": "CORE-008",
                    "message": "Tests required before implementation",
                    "severity": "error"
                }
            ]
        }
    },
    "id": 2
}
```

### initialize

**Request:**
```json
{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "resources": {},
            "prompts": {}
        },
        "clientInfo": {
            "name": "vscode-copilot",
            "version": "1.0.0"
        }
    },
    "id": 0
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": true},
            "resources": {"subscribe": true, "listChanged": true},
            "prompts": {"listChanged": true}
        },
        "serverInfo": {
            "name": "cortex-mcp",
            "version": "1.0.0"
        }
    },
    "id": 0
}
```

---

## Error Codes

### Standard JSON-RPC Errors

| Code | Message | Description |
|------|---------|-------------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid Request | Invalid request object |
| -32601 | Method not found | Unknown method |
| -32602 | Invalid params | Invalid parameters |
| -32603 | Internal error | Server error |

### MCP-Specific Errors

| Code | Message | Description |
|------|---------|-------------|
| -32001 | Tool not found | Unknown tool name |
| -32002 | Resource not found | Unknown resource |
| -32003 | Permission denied | Authorization failed |
| -32004 | Governance violation | Rule violation |
| -32005 | Rate limited | Too many requests |
| -32006 | Timeout | Operation timeout |

### Error Response Examples

```json
// Tool not found
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32001,
        "message": "Tool not found",
        "data": {
            "tool": "cortex_unknown_tool",
            "available": ["cortex_lens_analyze", "cortex_process_request"]
        }
    },
    "id": 1
}

// Rate limited
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32005,
        "message": "Rate limited",
        "data": {
            "retry_after": 30,
            "limit": 60,
            "window": "1m"
        }
    },
    "id": 1
}
```

---

## Transport

### HTTP Transport

```
POST /mcp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <token>

{"jsonrpc": "2.0", "method": "tools/list", "id": 1}
```

### WebSocket Transport

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/mcp/ws');

// Send request
ws.send(JSON.stringify({
    jsonrpc: "2.0",
    method: "tools/call",
    params: {
        name: "cortex_lens_analyze",
        arguments: { target: "src/app.py" }
    },
    id: 1
}));

// Receive response
ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log(response);
};
```

### stdio Transport

```bash
# Start server in stdio mode
python -m cortex.mcp.server --stdio

# Send request via stdin
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m cortex.mcp.server --stdio
```

---

## Related Documents

- [MCP Overview](overview.md) — Introduction
- [Tools Catalog](tools-catalog.md) — All tools
- [Integration Guide](integration.md) — Client integration

---

*Part of CORTEX Architecture Documentation*
