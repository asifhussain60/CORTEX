# MCP Protocol

---
title: MCP Protocol & Transport
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex/mcp/
order: 2
---

> **Brain analogy:** The spinal cord carries signals using specific nerve fiber types — some fast (motor), some slow (sensory). MCP works the same way: JSON-RPC 2.0 is the fiber standard, stdio is the fast motor pathway, and every message follows the same format.

---

## Protocol: JSON-RPC 2.0

Every MCP message follows JSON-RPC 2.0:

```json
// Request (IDE → CORTEX)
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "cortex_onboard_repository",
    "arguments": {}
  },
  "id": 1
}

// Response (CORTEX → IDE)
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      { "type": "text", "text": "Repository onboarded successfully..." }
    ]
  },
  "id": 1
}
```

### Message Types

| Type | Direction | Purpose |
|------|-----------|---------|
| `tools/list` | IDE → CORTEX | Discover available tools |
| `tools/call` | IDE → CORTEX | Execute a specific tool |
| `notifications` | CORTEX → IDE | Progress updates, status |
| `errors` | CORTEX → IDE | Error codes with messages |

---

## Transport: stdio

CORTEX uses **stdio transport** (standard input/output):

- **stdin:** IDE writes JSON-RPC requests
- **stdout:** CORTEX writes JSON-RPC responses
- **stderr:** Logging and diagnostics (never protocol data)

### Why stdio?

| Factor | stdio | HTTP |
|--------|-------|------|
| Startup | Instant (IDE spawns process) | Manual server start |
| Latency | Sub-millisecond (in-process) | Network overhead |
| Security | No exposed ports | Port binding required |
| Lifecycle | IDE manages process | Separate process management |
| Config | `.vscode/settings.json` | Environment variables |

---

## Lifecycle

```
IDE Opens Workspace
    │
    ▼
Read .vscode/settings.json
    │
    ▼
Spawn: python3 -m cortex.mcp (stdio)
    │
    ▼
MCP Server Initializes
    │
    ├── Register 23 tools
    ├── Load governance rules
    └── Ready for requests
    │
    ▼
IDE Sends tools/list → Get tool catalog
    │
    ▼
IDE Sends tools/call → Execute tool
    │
    ▼
IDE Closes → Process terminates
```

---

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| -32600 | Invalid request | Fix JSON format |
| -32601 | Method not found | Check tool name |
| -32602 | Invalid params | Check tool arguments |
| -32603 | Internal error | Check CORTEX logs |
| -32700 | Parse error | Fix JSON syntax |

All errors include structured messages with remediation guidance.

---

## Client Compatibility

| Client | Transport | Status |
|--------|-----------|--------|
| VS Code (Copilot Chat) | stdio | ✅ Primary |
| Cursor | stdio | ✅ Supported |
| Claude Desktop | stdio | ✅ Supported |
| Custom JSON-RPC client | stdio | ✅ Compatible |

---

## Practical Examples

**Product Owner:** "We chose stdio because it's zero-config. No servers to manage, no ports to configure, no Docker containers. The IDE handles everything."

**Developer:** "The MCP server starts when I open VS Code. I can see all 23 tools through `tools/list`. Each tool call is a single JSON-RPC round-trip."

---

*Verified against MCP protocol implementation · 25 February 2026*
