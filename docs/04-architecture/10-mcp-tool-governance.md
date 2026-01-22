# MCP Tool Governance

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Architects, Developers, Integrators  
**Prerequisites:** [MCP Protocol Specification](../03-api-reference/mcp-protocol/0-specification.md)

## Overview

CORTEX exposes 14 MCP (Model Context Protocol) tools for AI-native tool discovery and execution. This document covers tool governance, registry architecture, authentication, and authorization patterns.

## Current Status

| Metric | Value |
|--------|-------|
| **Total Tools** | 14 |
| **Status** | Stub implementations |
| **Protocol** | MCP v2024-11-05 |
| **Transport** | stdio (JSON-RPC 2.0) |

⚠️ **Note:** All 14 tools currently return mock data. Implementation occurs after Phase B MCP Centralization.

## Tool Registry Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP Tool Registry                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   cortex/mcp/                                                                │
│   ├── server.py           # MCP server entry point                          │
│   ├── registry.py         # Tool registration and discovery                 │
│   ├── tool_discovery.py   # Dynamic tool discovery                          │
│   ├── tool_governance.py  # Authorization and audit                         │
│   ├── compliance.py       # Governance compliance checks                    │
│   └── tools/              # Tool implementations                            │
│       ├── governance/     # query_tool, validate_tool, execute_tool         │
│       ├── analysis/       # analyze_tool, report_tool                       │
│       ├── knowledge/      # search_tool, index_tool                         │
│       └── utility/        # echo_tool, transform_tool                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Tool Categories

### Governance Tools (5)

| Tool | Description | Auth Level |
|------|-------------|------------|
| `query_tool` | Query governance rules | READ |
| `validate_tool` | Validate against rules | READ |
| `execute_tool` | Execute governance action | WRITE |
| `analyze_tool` | Analyze compliance | READ |
| `report_tool` | Generate compliance report | READ |

### Analysis Tools (2)

| Tool | Description | Auth Level |
|------|-------------|------------|
| `analyze_tool` | Code/pattern analysis | READ |
| `report_tool` | Generate analysis report | READ |

### Knowledge Tools (2)

| Tool | Description | Auth Level |
|------|-------------|------------|
| `search_tool` | Search knowledge base | READ |
| `index_tool` | Index new knowledge | WRITE |

### Utility Tools (5)

| Tool | Description | Auth Level |
|------|-------------|------------|
| `echo_tool` | Echo input (testing) | NONE |
| `sample_tool` | Sample data generation | READ |
| `transform_tool` | Data transformation | READ |
| `status_tool` | System status | READ |
| `health_tool` | Health check | NONE |

## Tool Registration

Tools are registered with metadata for discovery and governance:

```python
@dataclass
class ToolMetadata:
    """Tool registration metadata."""
    name: str
    description: str
    category: ToolCategory
    auth_level: AuthLevel
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    governance_rules: List[str]  # CORE-* rules that apply
    audit_required: bool
    rate_limit: Optional[RateLimit]
```

### Registration Example

```python
from cortex.mcp.registry import register_tool

@register_tool(
    name="query_tool",
    category=ToolCategory.GOVERNANCE,
    auth_level=AuthLevel.READ,
    governance_rules=["CORE-027"],  # Audit trail required
    audit_required=True
)
async def query_tool(query: str, context: Dict) -> ToolResult:
    """Query governance rules."""
    # Implementation
```

## Authorization Levels

| Level | Description | Requires |
|-------|-------------|----------|
| **NONE** | Public tools | Nothing |
| **READ** | Read-only access | Valid session |
| **WRITE** | Mutating operations | Valid session + role |
| **ADMIN** | Administrative ops | Admin role |

## Governance Integration

### Tier 0 Rules Applied

| Rule | Enforcement | Impact |
|------|-------------|--------|
| **CORE-001** | Response < 500 lines | All tools |
| **CORE-027** | Audit trail | WRITE tools |
| **CORE-028** | Kebab-case naming | Tool names |

### Audit Trail

All tool executions are logged:

```python
@dataclass
class ToolAuditEntry:
    """Audit entry for tool execution."""
    timestamp: datetime
    tool_name: str
    user_id: Optional[str]
    input_hash: str
    output_hash: str
    duration_ms: int
    success: bool
    error: Optional[str]
    governance_checks: List[GovernanceCheckResult]
```

## Rate Limiting

Tools have configurable rate limits:

| Category | Default Limit | Burst |
|----------|---------------|-------|
| Governance | 100/min | 20 |
| Analysis | 50/min | 10 |
| Knowledge | 200/min | 50 |
| Utility | 500/min | 100 |

## Error Handling

MCP tools return structured errors:

```python
class ToolError(Exception):
    """Base tool error with MCP-compatible structure."""
    
    def __init__(
        self,
        code: int,           # JSON-RPC error code
        message: str,        # Human-readable message
        data: Dict = None    # Additional context
    ):
        self.code = code
        self.message = message
        self.data = data or {}
```

### Error Codes

| Code | Description |
|------|-------------|
| -32600 | Invalid request |
| -32601 | Tool not found |
| -32602 | Invalid parameters |
| -32603 | Internal error |
| -32000 | Governance violation |
| -32001 | Authorization failed |
| -32002 | Rate limit exceeded |

## Implementation Roadmap

### Phase B: MCP Centralization (2 days)

1. Create `cortex/mcp/registry.py` with tool metadata
2. Implement `tool_discovery.py` for dynamic discovery
3. Add `tool_governance.py` for auth/audit
4. Connect to governance tier 0 rules
5. Implement tool logic (currently return mock data)

### Post-Phase B

After Phase B, tools transition from stubs to implementations:

| Tool | Implementation Priority |
|------|------------------------|
| query_tool | P0 - Core functionality |
| validate_tool | P0 - Governance |
| search_tool | P1 - Knowledge access |
| analyze_tool | P1 - Analysis |
| Others | P2 - Supporting |

## Related

- [MCP Tools Diagram](../_diagrams/mcp-tools.mmd)
- [MCP Protocol Specification](../03-api-reference/mcp-protocol/0-specification.md)
- [Governance Rules](governance-rules.md)
