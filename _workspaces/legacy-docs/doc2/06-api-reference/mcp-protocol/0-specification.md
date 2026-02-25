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

| File | Purpose | Status |
|------|---------|--------|
| `cortex/mcp/server.py` | Main MCP server (JSON-RPC processor, stdio handler) | ✅ Working |
| `cortex/mcp/registry.py` | **NEW:** Tool registry with metadata + discovery | Phase B |
| `cortex/mcp/tools/governance/` | 5 governance tools (query, validate, execute, analyze, report) | Stub → Phase 2 |
| `cortex/mcp/tools/orchestration/` | 4 orchestration tools (status, monitor, optimize, diagnose) | Stub → Phase 2 |
| `cortex/mcp/tools/knowledge/` | 3 knowledge tools (search, analyze, generate) | Stub → Phase 2 |
| `cortex/mcp/tools/utility/` | 2 utility tools (echo, sample, transform) | Stub → Phase 2 |

**Note:** As of 2026-01-20, all 14 tools are registered stub implementations (return mock data). Phase B (2 days) creates the registry. Phase 2 (3-4 days) implements real tool logic.

---

## MCP Tools Directory (14 Total)

### Governance Tools (5)

| Tool | ID | Description | Auth | Parameters |
|------|----|----|------|-----------|
| **Query Governance State** | `query-governance` | Query current governance rules and assignments | ✅ Required | `context`, `rule_id` (optional) |
| **Validate Compliance** | `validate-compliance` | Check if action complies with governance rules | ✅ Required | `action`, `context` |
| **Execute Governance Action** | `execute-governance` | Execute a governance-controlled operation | ✅ Required | `action`, `parameters` |
| **Analyze Governance** | `analyze-governance` | Analyze effectiveness of governance rules | ✅ Required | `time_range`, `scope` |
| **Generate Governance Report** | `report-governance` | Generate compliance and governance reports | ✅ Required | `report_type`, `date_range` |

### Orchestration Tools (4)

| Tool | ID | Description | Auth | Parameters |
|------|----|----|------|-----------|
| **Orchestrator Status** | `status-orchestrator` | Check status of running orchestrators | ❌ Optional | `orchestrator_id`, `include_logs` |
| **Monitor Orchestration** | `monitor-orchestration` | Real-time orchestration metrics and health | ❌ Optional | `time_window`, `metric_types` |
| **Optimize Orchestration** | `optimize-orchestration` | Get optimization suggestions for orchestration | ❌ Optional | `analysis_type`, `performance_goal` |
| **Diagnose Issues** | `diagnose-issues` | Diagnose orchestration problems and failures | ❌ Optional | `orchestrator_id`, `log_level` |

### Knowledge Tools (3)

| Tool | ID | Description | Auth | Parameters |
|------|----|----|------|-----------|
| **Search Knowledge** | `search-knowledge` | Search the knowledge graph and domain content | ❌ Optional | `query`, `filters`, `limit` |
| **Analyze Knowledge** | `analyze-knowledge` | Extract insights and analyze knowledge base | ❌ Optional | `domain`, `analysis_type` |
| **Generate Knowledge** | `generate-knowledge` | Generate knowledge recommendations | ❌ Optional | `context`, `intent` |

### Utility Tools (2)

| Tool | ID | Description | Auth | Parameters |
|------|----|----|------|-----------|
| **Echo Test** | `echo-test` | Simple echo tool for connectivity testing | ❌ No | `message` |
| **Transform Data** | `transform-data` | Transform data between formats | ❌ No | `input`, `format`, `target_format` |

---

## Tool Discovery

### List Tools

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {
    "category": "governance"  // Optional: governance|orchestration|knowledge|utility
  },
  "id": 2
}
```

**Response (All Tools):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": {
      "governance": [
        "query-governance",
        "validate-compliance", 
        "execute-governance",
        "analyze-governance",
        "report-governance"
      ],
      "orchestration": [
        "status-orchestrator",
        "monitor-orchestration",
        "optimize-orchestration",
        "diagnose-issues"
      ],
      "knowledge": [
        "search-knowledge",
        "analyze-knowledge",
        "generate-knowledge"
      ],
      "utility": [
        "echo-test",
        "transform-data"
      ]
    },
    "total": 14
  },
  "id": 2
}
```

### Get Tool Metadata

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/metadata",
  "params": {
    "tool_id": "query-governance"
  },
  "id": 3
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "id": "query-governance",
    "name": "Query Governance State",
    "category": "governance",
    "description": "Query the current governance state and rule assignments",
    "parameters": {
      "context": {
        "type": "string",
        "description": "Governance context (e.g., 'conversation', 'domain', 'operation')",
        "required": true
      },
      "rule_id": {
        "type": "string",
        "description": "Optional specific rule ID to query",
        "required": false
      }
    },
    "auth_required": true,
    "version": "1.0.0"
  },
  "id": 3
}
```

---

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

### ⚠️ IMPORTANT: Tool Implementation Status

**As of 2026-01-20:** All MCP tools are registered and discoverable but return **mock/stub data only**. 

| Status | Count | Tools |
|--------|-------|-------|
| **STUB (Mock Data)** | 14 | All tools below |
| **Functional** | 0 | None yet |
| **In Progress** | 0 | None |

**Implications:**
- ✅ Tool schema and discovery works correctly
- ❌ Tool execution returns mock responses, not real data
- ❌ Production integration requires tool implementation
- ⏳ Implementation planned for Phase 26+

### Core Tools (STUBS)

| Tool | Description | Status | Mock Returns | Implementation Required |
|------|-------------|--------|-----|-------------------------|
| `sample_tool` | Sample data tool | STUB | Mock sample data | Yes |
| `echo_tool` | Echo input with metadata | STUB | Input echo | No (intentionally simple) |
| `status_tool` | System status | STUB | Mock status data | Yes - Requires governance.db integration |
| `query_tool` | Knowledge queries | STUB | Mock results | Yes - Requires knowledge graph |
| `validate_tool` | Validation tool | STUB | Mock validation | Yes - Requires governance rules |
| `transform_tool` | Data transformation | STUB | Mock transformation | Yes - Requires template engine |
| `analyze_tool` | Analysis operations | STUB | Mock analysis | Yes - Requires LENS pipeline |
| `generate_tool` | Content generation | STUB | Mock content | Yes - Requires template system |
| `execute_tool` | Orchestrator execution | STUB | Mock execution | Yes - Requires master orchestrator |
| `monitor_tool` | Monitoring operations | STUB | Mock metrics | Yes - Requires monitoring system |
| `alert_tool` | Alert management | STUB | Mock alerts | Yes - Requires alerting system |
| `report_tool` | Report generation | STUB | Mock reports | Yes - Requires reporting engine |
| `optimize_tool` | Optimization operations | STUB | Mock optimization | Yes - Requires optimizer |
| `diagnose_tool` | Diagnostic operations | STUB | Mock diagnostics | Yes - Requires diagnostic engine |

### Governance Tools (Partially Implemented)

| Tool | Description | Status | Returns | Implementation Note |
|------|-------------|--------|---------|---------------------|
| `check_phase_lock` | Check phase lock status | FUNCTIONAL | Real governance.db queries | ✅ Implemented |
| `validate_ac_id` | Validate AC-ID existence | FUNCTIONAL | Real AC validation | ✅ Implemented |
| `canonicalize_intent` | Normalize intent | FUNCTIONAL | Real intent normalization | ✅ Implemented |
| `enforce_operation` | Enforce governance rules | PARTIAL | Mock enforcement | ⚠️ Partial - missing core-rules.yaml |
| `get_phase_status` | Get phase status | FUNCTIONAL | Real phase data | ✅ Implemented |

### Orchestrator-Exposed Tools (From @mcp_tool decorator)

| Tool | Orchestrator | Domain | Status | Returns |
|------|-------------|--------|--------|---------|
| `plan_status` | PlanningOrchestrator | Planning | FUNCTIONAL | Real phase planning data |
| `next_ac` | PlanningOrchestrator | Planning | FUNCTIONAL | Real AC suggestions |
| `enforce_phase_lock` | PlanningOrchestrator | Planning | FUNCTIONAL | Real lock enforcement |
| `register_orchestrator` | MasterOrchestrator | Core | FUNCTIONAL | Real orchestrator registration |
| `get_registered_domains` | MasterOrchestrator | Core | FUNCTIONAL | Real domain list |
| `coordinate_operation` | MasterOrchestrator | Core | FUNCTIONAL | Real coordination |

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
