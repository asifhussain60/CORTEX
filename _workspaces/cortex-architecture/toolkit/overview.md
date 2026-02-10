# Toolkit Overview

**Purpose:** Introduction to the CORTEX tool ecosystem  
**Audience:** All Technical Stakeholders  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Tool Categories](#tool-categories)
- [Core Tools](#core-tools)
- [Tool Invocation](#tool-invocation)
- [Discovery and Documentation](#discovery-and-documentation)
- [Related Documents](#related-documents)

---

## Overview

CORTEX exposes functionality through **35+ MCP tools** organized into categories. These tools are the primary interface for external clients and internal orchestrators to interact with CORTEX capabilities.

```
┌─────────────────────────────────────────────────────────────────┐
│                     CORTEX TOOLKIT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    MCP Server                            │   │
│  │                  (JSON-RPC 2.0)                          │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │    Core     │     │  Analysis   │     │  Planning   │       │
│  │   Tools     │     │   Tools     │     │   Tools     │       │
│  │  (10 tools) │     │  (8 tools)  │     │  (5 tools)  │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │ Governance  │     │   Debug     │     │  Discovery  │       │
│  │   Tools     │     │   Tools     │     │   Tools     │       │
│  │  (4 tools)  │     │  (3 tools)  │     │  (5 tools)  │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tool Categories

| Category | Count | Purpose |
|----------|-------|---------|
| **Core** | 10 | Primary operations (implement, fix, refactor) |
| **Analysis** | 8 | Code intelligence (LENS, AST, git) |
| **Planning** | 5 | Phase and roadmap management |
| **Governance** | 4 | Auditing and compliance |
| **Debug** | 3 | Troubleshooting and diagnostics |
| **Discovery** | 5 | Tool and feature discovery |

---

## Core Tools

### Primary Operations

| Tool | Purpose | Parameters |
|------|---------|------------|
| `cortex_process_request` | Main request processing | operation, target, request |
| `cortex_challenge` | Generate decision challenges | decision, context |
| `cortex_total_recall` | Feature discovery | query, scope |

### Analysis Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `cortex_lens_analyze` | Unified code intelligence | target, analyzers |
| `cortex_ast_analyze` | AST analysis only | target, language |
| `cortex_git_history` | Git history (24h) | path, hours |
| `cortex_detect_duplicates` | CORE-035 detection | scope |

### Planning Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `cortex_plan_setup` | Pre-implementation hook | phase_id |
| `cortex_plan_teardown` | Post-completion hook | phase_id |
| `cortex_plan_resolve` | Intelligent resolution | query |
| `cortex_plan_sync` | Dashboard synchronization | — |

### Governance Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `cortex_audit` | Codebase health scan | scope |
| `cortex_validate` | Rule validation | target, rules |
| `cortex_compliance_check` | Standards compliance | standards |

### Discovery Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `cortex_tools_catalog` | List available tools | category |
| `cortex_onboard_repository` | Repository setup | path |
| `cortex_describe_tool` | Tool documentation | tool_name |

---

## Tool Invocation

### Request Format

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
    "id": "req-001"
}
```

### Response Format

```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "git_insights": { ... },
            "ast_analysis": { ... },
            "comment_analysis": { ... }
        },
        "audit_id": "AUDIT-2026-02-10-001"
    },
    "id": "req-001"
}
```

### Error Response

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
                    "message": "Tests required before implementation"
                }
            ]
        }
    },
    "id": "req-001"
}
```

---

## Discovery and Documentation

### List All Tools

```bash
# Via MCP
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### Get Tool Details

```bash
# Via MCP
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "cortex_describe_tool",
        "arguments": {"tool_name": "cortex_lens_analyze"}
    },
    "id": 1
  }'
```

### Tool Documentation Structure

```python
@dataclass
class ToolDocumentation:
    """Documentation for a CORTEX tool."""
    
    name: str
    category: ToolCategory
    description: str
    parameters: List[ParameterDoc]
    examples: List[Example]
    related_tools: List[str]
    version: str
    deprecated: bool = False
```

---

## Related Documents

- [Tool Registry](tool-registry.md) — Registration system
- [Tool Categories](tool-categories.md) — Detailed categorization
- [MCP Integration](../mcp/tools-catalog.md) — MCP exposure

---

*Part of CORTEX Architecture Documentation*
