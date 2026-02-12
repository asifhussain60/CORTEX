# MCP Integration Guide

**Purpose:** Guide for integrating with CORTEX MCP  
**Audience:** Developers, Integration Engineers  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Client Setup](#client-setup)
- [VS Code Integration](#vs-code-integration)
- [Programmatic Integration](#programmatic-integration)
- [Authentication](#authentication)
- [Best Practices](#best-practices)
- [Related Documents](#related-documents)

---

## Overview

This guide covers integrating with the CORTEX MCP server from various clients.

```
┌─────────────────────────────────────────────────────────────────┐
│                 INTEGRATION OPTIONS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  VS Code + Copilot                                        │  │
│  │  • Native MCP support                                     │  │
│  │  • Automatic tool discovery                               │  │
│  │  • Chat-based invocation                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  HTTP Client                                              │  │
│  │  • REST-like access                                       │  │
│  │  • JSON-RPC over HTTP POST                                │  │
│  │  • Synchronous requests                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  WebSocket Client                                         │  │
│  │  • Persistent connection                                  │  │
│  │  • Bidirectional communication                            │  │
│  │  • Real-time notifications                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CLI Client                                               │  │
│  │  • Command-line access                                    │  │
│  │  • Script integration                                     │  │
│  │  • Piped I/O                                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Client Setup

### Prerequisites

1. CORTEX MCP server running
2. Network access to server (default: localhost:8000)
3. API key (if authentication enabled)

### Start Server

```bash
# Development
python -m cortex.mcp.server

# Production
uvicorn cortex.mcp.server:app --host 0.0.0.0 --port 8000

# With custom configuration
CORTEX_PORT=9000 CORTEX_LOG_LEVEL=DEBUG python -m cortex.mcp.server
```

### Verify Connection

```bash
# Health check
curl http://localhost:8000/health

# Expected response
{"status": "healthy", "orchestrators": 23, "tools": 35}
```

---

## VS Code Integration

### Configuration

Add to `.vscode/settings.json`:

```json
{
    "github.copilot.chat.mcpServers": {
        "cortex": {
            "command": "python",
            "args": ["-m", "cortex.mcp.server", "--stdio"],
            "cwd": "${workspaceFolder}"
        }
    }
}
```

### Alternative: HTTP Server

```json
{
    "github.copilot.chat.mcpServers": {
        "cortex": {
            "url": "http://localhost:8000/mcp"
        }
    }
}
```

### Usage in Copilot Chat

```
# List available tools
@cortex /tools

# Analyze code
@cortex analyze src/auth/service.py

# Implement feature
@cortex implement OAuth support in auth module

# Audit codebase
@cortex /audit
```

### Tool Invocation

Copilot automatically discovers and invokes MCP tools:

```
User: Analyze the authentication module

Copilot: [Invoking cortex_lens_analyze with target="src/auth/"]

Analysis Results:
- 5 Python files analyzed
- 3 classes, 15 methods found
- 2 security patterns detected
...
```

---

## Programmatic Integration

### Python Client

```python
import httpx
import json
from typing import Any, Dict, Optional

class CortexClient:
    """CORTEX MCP client."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None
    ):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self._request_id = 0
    
    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id
    
    async def call_tool(
        self,
        tool: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call an MCP tool."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp",
                headers=self.headers,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool,
                        "arguments": arguments
                    },
                    "id": self._next_id()
                }
            )
            
            result = response.json()
            
            if "error" in result:
                raise CortexError(result["error"])
            
            return result["result"]
    
    async def list_tools(self) -> list:
        """List available tools."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp",
                headers=self.headers,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": self._next_id()
                }
            )
            return response.json()["result"]["tools"]

# Usage
async def main():
    client = CortexClient()
    
    # List tools
    tools = await client.list_tools()
    print(f"Available tools: {len(tools)}")
    
    # Analyze code
    result = await client.call_tool(
        "cortex_lens_analyze",
        {"target": "src/auth/service.py"}
    )
    print(result)
```

### TypeScript Client

```typescript
interface MCPRequest {
    jsonrpc: "2.0";
    method: string;
    params?: Record<string, unknown>;
    id: number;
}

interface MCPResponse {
    jsonrpc: "2.0";
    result?: unknown;
    error?: {
        code: number;
        message: string;
        data?: unknown;
    };
    id: number;
}

class CortexClient {
    private baseUrl: string;
    private requestId = 0;

    constructor(baseUrl = "http://localhost:8000") {
        this.baseUrl = baseUrl;
    }

    async callTool<T>(tool: string, args: Record<string, unknown>): Promise<T> {
        const response = await fetch(`${this.baseUrl}/mcp`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "tools/call",
                params: { name: tool, arguments: args },
                id: ++this.requestId
            } as MCPRequest)
        });

        const result: MCPResponse = await response.json();

        if (result.error) {
            throw new Error(result.error.message);
        }

        return result.result as T;
    }

    async listTools(): Promise<Array<{ name: string; description: string }>> {
        const response = await fetch(`${this.baseUrl}/mcp`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "tools/list",
                id: ++this.requestId
            })
        });

        const result: MCPResponse = await response.json();
        return (result.result as any).tools;
    }
}

// Usage
const client = new CortexClient();
const tools = await client.listTools();
console.log(`Available tools: ${tools.length}`);
```

### CLI Integration

```bash
#!/bin/bash
# cortex-cli.sh

CORTEX_URL="${CORTEX_URL:-http://localhost:8000}"

cortex_call() {
    local tool=$1
    local args=$2
    
    curl -s -X POST "$CORTEX_URL/mcp" \
        -H "Content-Type: application/json" \
        -d "{
            \"jsonrpc\": \"2.0\",
            \"method\": \"tools/call\",
            \"params\": {
                \"name\": \"$tool\",
                \"arguments\": $args
            },
            \"id\": 1
        }" | jq '.result'
}

# Usage
cortex_call "cortex_lens_analyze" '{"target": "src/app.py"}'
```

---

## Authentication

### API Key Authentication

```python
# Server configuration
CORTEX_API_KEY_REQUIRED=true
CORTEX_API_KEYS=key1,key2,key3

# Client usage
client = CortexClient(api_key="your-api-key")
```

### Header Format

```
Authorization: Bearer <api-key>
```

### Request with Authentication

```bash
curl -X POST http://localhost:8000/mcp \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer your-api-key" \
    -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

---

## Best Practices

### Error Handling

```python
class CortexError(Exception):
    """CORTEX error."""
    
    def __init__(self, error: dict):
        self.code = error["code"]
        self.message = error["message"]
        self.data = error.get("data")
        super().__init__(self.message)

async def safe_call(client, tool, args):
    """Call tool with error handling."""
    try:
        return await client.call_tool(tool, args)
    except CortexError as e:
        if e.code == -32005:  # Rate limited
            await asyncio.sleep(e.data.get("retry_after", 30))
            return await client.call_tool(tool, args)
        elif e.code == -32004:  # Governance violation
            logger.error(f"Governance violation: {e.data}")
            raise
        else:
            raise
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def call_with_retry(client, tool, args):
    """Call tool with automatic retry."""
    return await client.call_tool(tool, args)
```

### Timeout Configuration

```python
async def call_with_timeout(client, tool, args, timeout=30):
    """Call tool with timeout."""
    async with httpx.AsyncClient(timeout=timeout) as http:
        return await client.call_tool(tool, args)
```

---

## Related Documents

- [MCP Overview](overview.md) — Introduction
- [MCP Protocol](protocol.md) — Protocol details
- [Tools Catalog](tools-catalog.md) — All tools

---

*Part of CORTEX Architecture Documentation*
