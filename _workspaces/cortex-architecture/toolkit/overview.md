# Toolkit Overview

**Purpose:** The cognitive tools that give CORTEX its capabilities  
**Audience:** All Technical Stakeholders  
**Last Updated:** 2026-02-10

---

## Overview

**CORTEX Toolkit: The Brain's Cognitive Abilities**

Just as the human brain has different cognitive abilities—memory recall, pattern recognition, problem-solving, creative thinking—CORTEX exposes its intelligence through **35+ specialized cognitive tools** accessible via the Model Context Protocol.

**Think of Tools as Cognitive Functions:**
- **🧠 Core Tools** = Basic cognitive functions (memory, attention, processing)
- **🔍 Analysis Tools** = Perceptual abilities (seeing patterns, understanding structure)
- **📅 Planning Tools** = Executive functions (strategic thinking, organization)
- **🛡️ Governance Tools** = Behavioral control (quality assurance, compliance)
- **🔧 Debug Tools** = Problem-solving abilities (diagnosis, error correction)
- **🎯 Discovery Tools** = Learning functions (exploration, knowledge acquisition)

These tools are the **neural pathways** that external systems use to tap into CORTEX's intelligence.

```
┌─────────────────────────────────────────────────────────────────┐
│                  🧠 CORTEX COGNITIVE TOOLKIT                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                🔗 MCP Neural Interface                   │   │
│  │               (JSON-RPC 2.0 Protocol)                   │   │
│  │           Translates requests into neural signals        │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │  🧠 Core    │     │ 🔍 Analysis │     │ 📅 Planning │       │
│  │ Cognitive   │     │ & Pattern   │     │& Strategic  │       │
│  │Functions    │     │Recognition  │     │  Thinking   │       │
│  │ (10 tools)  │     │  (8 tools)  │     │  (5 tools)  │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │🛡️ Governance│     │ 🔧 Problem  │     │ 🎯 Learning │       │
│  │& Behavioral │     │  Solving &  │     │& Discovery  │       │
│  │  Control    │     │  Debugging  │     │ Functions   │       │
│  │  (4 tools)  │     │  (3 tools)  │     │  (5 tools)  │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                  │
│                       35+ Cognitive Tools Total                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Benefits:**
- **🧠 Intelligent Access** → Each tool represents a specific cognitive ability
- **🔄 Composable Intelligence** → Tools can be combined for complex reasoning
- **📖 Self-Describing** → Tools explain their own capabilities and usage
- **🔗 Universal Interface** → Standard JSON-RPC protocol works with any client

### D3.js Tool Performance Analytics

```json
{
  "type": "tool_analytics_dashboard",
  "title": "CORTEX Cognitive Tool Performance",
  "time_range": "Last 30 days",
  "sections": [
    {
      "name": "Tool Usage Patterns",
      "type": "sunburst_chart",
      "data": {
        "name": "🧠 CORTEX Tools",
        "children": [
          {
            "name": "Core Cognitive",
            "size": 1250,
            "children": [
              {"name": "cortex_process_request", "size": 450, "success_rate": 97.2, "avg_time": "1.2s"},
              {"name": "cortex_challenge", "size": 180, "success_rate": 94.8, "avg_time": "0.8s"},
              {"name": "cortex_total_recall", "size": 120, "success_rate": 96.1, "avg_time": "0.6s"},
              {"name": "cortex_lens_analyze", "size": 380, "success_rate": 95.7, "avg_time": "2.1s"},
              {"name": "cortex_git_history", "size": 220, "success_rate": 98.9, "avg_time": "0.4s"}
            ]
          },
          {
            "name": "Analysis & Intelligence", 
            "size": 890,
            "children": [
              {"name": "cortex_ast_analyze", "size": 195, "success_rate": 97.3, "avg_time": "1.8s"},
              {"name": "cortex_detect_duplicates", "size": 140, "success_rate": 93.4, "avg_time": "2.4s"},
              {"name": "cortex_pattern_analysis", "size": 165, "success_rate": 91.8, "avg_time": "3.2s"},
              {"name": "cortex_vision_analyze", "size": 125, "success_rate": 89.7, "avg_time": "4.1s"},
              {"name": "cortex_comment_extract", "size": 95, "success_rate": 94.2, "avg_time": "0.9s"},
              {"name": "cortex_config_analyze", "size": 85, "success_rate": 96.8, "avg_time": "0.7s"},
              {"name": "cortex_database_analyze", "size": 55, "success_rate": 92.1, "avg_time": "1.5s"},
              {"name": "cortex_api_analyze", "size": 30, "success_rate": 88.9, "avg_time": "2.8s"}
            ]
          },
          {
            "name": "Planning & Strategy",
            "size": 425,
            "children": [
              {"name": "cortex_plan_setup", "size": 125, "success_rate": 89.2, "avg_time": "0.5s"},
              {"name": "cortex_plan_teardown", "size": 95, "success_rate": 92.1, "avg_time": "0.3s"},
              {"name": "cortex_plan_resolve", "size": 85, "success_rate": 88.7, "avg_time": "1.1s"},
              {"name": "cortex_plan_sync", "size": 65, "success_rate": 94.3, "avg_time": "0.4s"},
              {"name": "cortex_phase_manage", "size": 55, "success_rate": 90.8, "avg_time": "0.8s"}
            ]
          },
          {
            "name": "Governance & Quality",
            "size": 660,
            "children": [
              {"name": "cortex_audit", "size": 180, "success_rate": 99.1, "avg_time": "0.6s"},
              {"name": "cortex_governance_check", "size": 210, "success_rate": 98.7, "avg_time": "0.4s"},
              {"name": "cortex_security_scan", "size": 145, "success_rate": 96.8, "avg_time": "1.9s"},
              {"name": "cortex_compliance_validate", "size": 125, "success_rate": 97.9, "avg_time": "0.7s"}
            ]
          },
          {
            "name": "Debug & Discovery",
            "size": 320,
            "children": [
              {"name": "cortex_debug_inject", "size": 85, "success_rate": 91.4, "avg_time": "0.2s"},
              {"name": "cortex_debug_capture", "size": 75, "success_rate": 94.7, "avg_time": "0.8s"},
              {"name": "cortex_debug_analyze", "size": 65, "success_rate": 88.2, "avg_time": "1.4s"},
              {"name": "cortex_tools_catalog", "size": 55, "success_rate": 99.5, "avg_time": "0.1s"},
              {"name": "cortex_onboard_repository", "size": 40, "success_rate": 87.3, "avg_time": "12.5s"}
            ]
          }
        ]
      }
    }
  ]
}
```

### Tool Performance Comparison

```json
{
  "type": "performance_comparison",
  "title": "Cognitive Tool Benchmark Analysis",
  "metrics": ["Execution Time", "Success Rate", "Resource Usage", "User Satisfaction"],
  "tools": [
    {
      "name": "cortex_process_request",
      "category": "Core",
      "scores": {"execution_time": 85, "success_rate": 97, "resource_usage": 75, "user_satisfaction": 94},
      "monthly_usage": 13500,
      "trend": "stable"
    },
    {
      "name": "cortex_lens_analyze", 
      "category": "Intelligence",
      "scores": {"execution_time": 72, "success_rate": 96, "resource_usage": 82, "user_satisfaction": 91},
      "monthly_usage": 11400,
      "trend": "increasing"
    },
    {
      "name": "cortex_git_history",
      "category": "Analysis", 
      "scores": {"execution_time": 95, "success_rate": 99, "resource_usage": 92, "user_satisfaction": 96},
      "monthly_usage": 6600,
      "trend": "stable"
    },
    {
      "name": "cortex_audit",
      "category": "Governance",
      "scores": {"execution_time": 90, "success_rate": 99, "resource_usage": 88, "user_satisfaction": 97},
      "monthly_usage": 5400,
      "trend": "increasing"
    },
    {
      "name": "cortex_pattern_analysis",
      "category": "Intelligence",
      "scores": {"execution_time": 65, "success_rate": 92, "resource_usage": 70, "user_satisfaction": 87},
      "monthly_usage": 4950,
      "trend": "stable"
    }
  ]
}
```

### Tool Dependency Graph

```json
{
  "type": "dependency_graph",
  "title": "Cognitive Tool Dependencies & Relationships",
  "nodes": [
    {"id": "process_request", "label": "cortex_process_request", "type": "hub", "size": 80},
    {"id": "lens", "label": "cortex_lens_analyze", "type": "intelligence", "size": 70},
    {"id": "git_history", "label": "cortex_git_history", "type": "analysis", "size": 50},
    {"id": "ast_analyze", "label": "cortex_ast_analyze", "type": "analysis", "size": 45},
    {"id": "audit", "label": "cortex_audit", "type": "governance", "size": 40},
    {"id": "challenge", "label": "cortex_challenge", "type": "core", "size": 35},
    {"id": "plan_setup", "label": "cortex_plan_setup", "type": "planning", "size": 30},
    {"id": "debug_inject", "label": "cortex_debug_inject", "type": "debug", "size": 25}
  ],
  "edges": [
    {"from": "process_request", "to": "lens", "relationship": "depends_on", "strength": 90},
    {"from": "lens", "to": "git_history", "relationship": "uses", "strength": 85},
    {"from": "lens", "to": "ast_analyze", "relationship": "uses", "strength": 80},
    {"from": "process_request", "to": "audit", "relationship": "triggers", "strength": 95},
    {"from": "process_request", "to": "challenge", "relationship": "may_invoke", "strength": 60},
    {"from": "plan_setup", "to": "process_request", "relationship": "prepares_for", "strength": 70},
    {"from": "debug_inject", "to": "lens", "relationship": "enhances", "strength": 40}
  ]
}
```

### Usage Trends & Forecasting

```json
{
  "type": "trend_analysis",
  "title": "Tool Usage Trends & Growth Projections",
  "time_series": {
    "period": "6_months",
    "data": [
      {
        "month": "2025-08",
        "tools": {
          "cortex_process_request": 8200,
          "cortex_lens_analyze": 6800,
          "cortex_git_history": 4200,
          "cortex_audit": 3100,
          "cortex_challenge": 1800
        }
      },
      {
        "month": "2025-09", 
        "tools": {
          "cortex_process_request": 9100,
          "cortex_lens_analyze": 7500,
          "cortex_git_history": 4600,
          "cortex_audit": 3500,
          "cortex_challenge": 2100
        }
      },
      {
        "month": "2025-10",
        "tools": {
          "cortex_process_request": 10200,
          "cortex_lens_analyze": 8400,
          "cortex_git_history": 5100,
          "cortex_audit": 4000,
          "cortex_challenge": 2400
        }
      },
      {
        "month": "2025-11",
        "tools": {
          "cortex_process_request": 11500,
          "cortex_lens_analyze": 9600,
          "cortex_git_history": 5800,
          "cortex_audit": 4600,
          "cortex_challenge": 2900
        }
      },
      {
        "month": "2025-12",
        "tools": {
          "cortex_process_request": 12800,
          "cortex_lens_analyze": 10800,
          "cortex_git_history": 6400,
          "cortex_audit": 5200,
          "cortex_challenge": 3300
        }
      },
      {
        "month": "2026-01",
        "tools": {
          "cortex_process_request": 13500,
          "cortex_lens_analyze": 11400,
          "cortex_git_history": 6600,
          "cortex_audit": 5400,
          "cortex_challenge": 3500
        }
      }
    ],
    "projections": {
      "2026-02": {
        "cortex_process_request": {"predicted": 14200, "confidence": 92},
        "cortex_lens_analyze": {"predicted": 12100, "confidence": 89},
        "cortex_git_history": {"predicted": 6900, "confidence": 94},
        "cortex_audit": {"predicted": 5800, "confidence": 91},
        "cortex_challenge": {"predicted": 3800, "confidence": 87}
      }
    }
  }
}
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
