# MCP Protocol Specification

**Last Updated:** 2026-01-20  
**Audience:** Developers, Integrators  
**Prerequisites:** [System Overview](../../02-architecture/1-system-overview.md)

## Overview

CORTEX implements the Model Context Protocol (MCP) v2024-11-05 specification for AI-native tool discovery and execution. The MCP server enables integration with Claude Desktop, VS Code, and other MCP-compatible clients through JSON-RPC 2.0 over stdio transport.

## Protocol Specification

### Transport Layer

| Property | Value |
|----------|-------|
| **Protocol** | JSON-RPC 2.0 |
| **Transport** | stdio (stdin/stdout) |
| **Encoding** | UTF-8 |
| **Message Format** | Newline-delimited JSON |

### Message Structure

#### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value1",
      "param2": "value2"
    }
  },
  "id": "request-123"
}
```

#### Response Format (Success)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Tool execution result"
      }
    ]
  },
  "id": "request-123"
}
```

#### Response Format (Error)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Invalid Request",
    "data": {
      "details": "Missing required parameter: param1"
    }
  },
  "id": "request-123"
}
```

## MCP Server Implementation

### Server Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Server (CORTEX)                         │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐│
│  │ stdio Reader  │  │ JSON-RPC     │  │ Tool Registry         ││
│  │ (stdin)       │──│ Processor    │──│ (@mcp_tool decorated) ││
│  └───────────────┘  └───────────────┘  └───────────────────────┘│
│         │                  │                      │              │
│         │                  ▼                      ▼              │
│  ┌──────┴──────┐  ┌───────────────┐  ┌───────────────────────┐ │
│  │ stdio Writer│  │ Request       │  │ Input Validator       │ │
│  │ (stdout)    │◀─│ Router        │──│ (Schema validation)   │ │
│  └─────────────┘  └───────────────┘  └───────────────────────┘ │
│                           │                      │              │
│                           ▼                      ▼              │
│                  ┌───────────────┐  ┌───────────────────────┐  │
│                  │ Tool Executor │  │ Error Handler         │  │
│                  │ (Async)       │──│ (Structured errors)   │  │
│                  └───────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Files

| File | Purpose |
|------|---------|
| `src/mcp/server_sdk.py` | Main MCP server implementation |
| `src/mcp/decorator.py` | `@mcp_tool` decorator for tool registration |
| `src/mcp/registry.py` | Tool registry and discovery |
| `src/mcp/input_validator.py` | Parameter validation |
| `src/mcp/error_handler.py` | Error response formatting |
| `src/mcp/executor.py` | Async tool execution |
| `src/mcp/compliance.py` | Protocol compliance verification |
| `cortex/mcp/server.py` | Alternative server implementation |

## Supported Methods

### Core MCP Methods

| Method | Description | Required |
|--------|-------------|----------|
| `initialize` | Initialize server capabilities | ✅ |
| `tools/list` | List all available tools | ✅ |
| `tools/call` | Execute a tool | ✅ |
| `notifications/initialized` | Client ready notification | Optional |

### Method: `initialize`

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "clientInfo": {
      "name": "claude-desktop",
      "version": "1.0.0"
    },
    "capabilities": {}
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "cortex-mcp-server",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {}
    }
  },
  "id": 1
}
```

### Method: `tools/list`

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 2
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "cortex_execute_orchestrator",
        "description": "Execute a CORTEX orchestrator with given context",
        "inputSchema": {
          "type": "object",
          "properties": {
            "orchestrator_name": {
              "type": "string",
              "description": "Name of the orchestrator to execute"
            },
            "context": {
              "type": "object",
              "description": "Execution context"
            }
          },
          "required": ["orchestrator_name"]
        }
      }
    ]
  },
  "id": 2
}
```

### Method: `tools/call`

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "cortex_execute_orchestrator",
    "arguments": {
      "orchestrator_name": "planning",
      "context": {
        "intent": "create_feature"
      }
    }
  },
  "id": 3
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Orchestrator 'planning' executed successfully.\n\nResult: Feature planning complete."
      }
    ]
  },
  "id": 3
}
```

## Tool Registration

### Using the @mcp_tool Decorator

```python
from src.mcp.decorator import mcp_tool

@mcp_tool(
    name="cortex_query_knowledge",
    description="Query the CORTEX Domain Brain for knowledge",
    parameters={
        "domain": {
            "type": "string",
            "description": "Domain to query (e.g., 'financial', 'compliance')",
            "required": True
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Search keywords",
            "required": False
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum results to return",
            "default": 10
        }
    }
)
async def query_knowledge(domain: str, keywords: list = None, max_results: int = 10):
    """Query Domain Brain for knowledge."""
    from src.core.knowledge.domain_brain import DomainBrain
    
    brain = DomainBrain()
    results = brain.query(
        domains=[domain],
        keywords=keywords or [],
        max_results=max_results
    )
    
    return {
        "content": [
            {"type": "text", "text": f"Found {len(results)} results:\n{format_results(results)}"}
        ]
    }
```

### Tool Discovery

Tools are automatically discovered from:

1. `src/mcp/tools/` - Core MCP tools
2. `src/orchestrators/` - Orchestrator tools
3. `src/tools/` - Utility tools

```python
from src.mcp.registry import get_registered_tools

# List all registered tools
tools = get_registered_tools()
for tool in tools:
    print(f"Tool: {tool.name} - {tool.description}")
```

## Available Tools

### Core Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `cortex_execute_orchestrator` | Execute an orchestrator | `orchestrator_name`, `context` |
| `cortex_query_knowledge` | Query Domain Brain | `domain`, `keywords`, `max_results` |
| `cortex_validate_governance` | Validate against rules | `entity_type`, `entity_data` |
| `cortex_audit_trail` | Query audit trail | `ac_id`, `date_range` |

### Orchestrator Tools

| Tool | Description | Domain |
|------|-------------|--------|
| `cortex_onboarding` | User onboarding workflow | Planning |
| `cortex_complexity_assessment` | Assess operation complexity | Analysis |
| `cortex_gap_detection` | Detect implementation gaps | Analysis |
| `cortex_bkio` | Business knowledge ingestion | Integration |

## Error Handling

### Error Codes

| Code | Name | Description |
|------|------|-------------|
| `-32700` | Parse Error | Invalid JSON |
| `-32600` | Invalid Request | Malformed request |
| `-32601` | Method Not Found | Unknown method |
| `-32602` | Invalid Params | Invalid parameters |
| `-32603` | Internal Error | Server error |
| `-32000` | Tool Error | Tool execution failed |
| `-32001` | Validation Error | Parameter validation failed |
| `-32002` | Governance Error | Governance rule violated |

### Error Response Structure

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid Params",
    "data": {
      "parameter": "orchestrator_name",
      "error": "Required parameter missing",
      "suggestion": "Provide a valid orchestrator name"
    }
  },
  "id": "request-123"
}
```

## Configuration

### Server Configuration

```yaml
# cortex-config.yaml
mcp:
  server:
    name: "cortex-mcp-server"
    version: "1.0.0"
    protocol_version: "2024-11-05"
  transport:
    type: "stdio"
    encoding: "utf-8"
  tools:
    auto_discover: true
    discovery_paths:
      - "src/mcp/tools"
      - "src/orchestrators"
      - "src/tools"
  validation:
    strict_mode: true
    schema_validation: true
  logging:
    level: "INFO"
    output: "stderr"
```

### Client Configuration (Claude Desktop)

```json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "src.mcp"],
      "cwd": "/path/to/cortex"
    }
  }
}
```

### Client Configuration (VS Code)

```json
{
  "mcp.servers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "src.mcp"],
      "workingDirectory": "${workspaceFolder}"
    }
  }
}
```

## Running the Server

### Command Line

```bash
# Run MCP server
python -m src.mcp

# With debug logging
python -m src.mcp --debug

# With specific config
python -m src.mcp --config path/to/config.yaml
```

### Programmatic

```python
from src.mcp.server_sdk import CORTEXMCPServer

async def main():
    server = CORTEXMCPServer()
    await server.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Testing MCP Tools

### Unit Testing

```python
import pytest
from src.mcp.decorator import get_tool

@pytest.mark.asyncio
async def test_query_knowledge_tool():
    tool = get_tool("cortex_query_knowledge")
    
    result = await tool.execute({
        "domain": "financial",
        "keywords": ["transaction"],
        "max_results": 5
    })
    
    assert "content" in result
    assert result["content"][0]["type"] == "text"
```

### Integration Testing

```python
import pytest
from src.mcp.server_sdk import CORTEXMCPServer

@pytest.mark.asyncio
async def test_mcp_server_initialize():
    server = CORTEXMCPServer()
    
    response = await server.handle_request({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"},
        "id": 1
    })
    
    assert response["result"]["protocolVersion"] == "2024-11-05"
```

## Protocol Compliance

CORTEX MCP implementation is verified against:

- **MCP Specification:** v2024-11-05
- **JSON-RPC:** 2.0
- **Implementation Phase:** PHASE-22-MCP-PROTOCOL-COMPLIANCE

### Compliance Verification

```bash
# Run compliance tests
python -m pytest tests/mcp/test_protocol_compliance.py -v
```

## Related Documentation

- [System Overview](../../02-architecture/1-system-overview.md) - Architecture context
- [REST API](../rest-api/0-guide.md) - HTTP API alternative
- [CLI Reference](../cli/0-guide.md) - Command-line interface
- [Tool Development](../../04-guides/integration/developing-mcp-tools.md) - Creating custom tools
