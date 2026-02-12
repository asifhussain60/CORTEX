# CORTEX MCP Architecture

## Overview

The Model Context Protocol (MCP) Server is the **SINGLE entry point** for ALL CORTEX functionality. Every operation - whether it's implementing features, analyzing code, validating governance, or debugging - flows through MCP tools.

## Design Principles

1. **Single Entry Point**: All functionality via MCP tools, no direct Python imports
2. **24 Tools Maximum**: Consolidated by business capability, not arbitrary count
3. **Cross-Platform**: Works on macOS, Windows, Linux without modification
4. **Extensible**: New capabilities = new operations, not new tools
5. **Testable**: 48 tests covering consolidation, protocol, and performance

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL CLIENTS                                │
│   VS Code Copilot  │  CLI  │  REST API  │  CI/CD  │  Other IDEs         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                         JSON-RPC 2.0 / stdio
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       MCP SERVER v2                                      │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │                      TOOL REGISTRY (24 Tools)                        │ │
│ │ ┌───────────┐ ┌───────────────┐ ┌────────────┐ ┌──────────────────┐ │ │
│ │ │   CORE    │ │ INTELLIGENCE  │ │ GOVERNANCE │ │   OPERATIONS     │ │ │
│ │ │ (4 tools) │ │   (3 tools)   │ │  (3 tools) │ │   (5 tools)      │ │ │
│ │ └───────────┘ └───────────────┘ └────────────┘ └──────────────────┘ │ │
│ │ ┌─────────────────────────────────────────────────────────────────┐ │ │
│ │ │                      UTILITIES (9 tools)                        │ │ │
│ │ └─────────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR LAYER                                  │
│   MasterOrchestrator → IntentRouter → Domain Orchestrators              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Tool Categories

### Tier 1: Core Request Processing (4 tools)

| Tool | Description |
|------|-------------|
| `cortex_process_request` | Main entry point for all requests |
| `cortex_challenge` | Generate challenges and alternatives |
| `cortex_classify` | Intent classification using LENS |
| `cortex_request_lifecycle` | Approve/reject/modify requests |

### Tier 2: Code Intelligence (3 tools)

| Tool | Operations |
|------|-----------|
| `cortex_lens` | analyze, deep_analyze, ast, discover, extract_comments |
| `cortex_knowledge` | search, analyze_gap, tdd_guidance, generate_summary |
| `cortex_git` | history, detect_duplicates, blame |

### Tier 3: Governance & Compliance (3 tools)

| Tool | Operations |
|------|-----------|
| `cortex_governance` | query, execute, analyze_impact, report, remediation_plan |
| `cortex_validate` | compliance, architecture, holistic, environment, against_rules |
| `cortex_load` | core_rules, audit_checklist, modes, response_format |

### Tier 4: Operations (5 tools)

| Tool | Operations |
|------|-----------|
| `cortex_debug` | inject, capture, analyze, fix_plan, cleanup, full_cycle, status |
| `cortex_refactor` | execute, available_operations, supported_languages |
| `cortex_plan` | setup, execute, teardown, resolve, sync |
| `cortex_onboard` | analyze_configs, onboard, security_scan |
| `cortex_dashboard` | list_repos, create_repo, update_repo, delete_repo, generate_suite... |

### Tier 5: Utilities (9 tools)

| Tool | Purpose |
|------|---------|
| `cortex_verify` | Environment and claim verification |
| `cortex_ask` | Educational queries |
| `cortex_vacuum` | Cleanup markdown sprawl |
| `cortex_tools_catalog` | Tool discovery |
| `cortex_total_recall` | Feature recall |
| `cortex_metrics` | Metrics capture/report |
| `cortex_check` | System checks |
| `cortex_vision` | Vision API |
| `cortex_orchestrator` | Orchestrator diagnostics |

## Consolidated Tool Pattern

Instead of 98 separate tools, we use an **operation parameter** to route within a tool:

```json
// Before: 13 separate debug tools
cortex_debug_inject(...)
cortex_debug_capture(...)
cortex_debug_analyze(...)

// After: 1 consolidated tool with operations
cortex_debug(operation="inject", target="/path/to/file", ...)
cortex_debug(operation="capture", ...)
cortex_debug(operation="analyze", ...)
```

Benefits:
- Reduced cognitive load (24 vs 98 tools)
- Better discoverability (operations in enum)
- Easier maintenance
- Same functionality

## Cross-Platform Setup

### For Team Members

```bash
# Clone the repo
git clone https://github.com/org/CORTEX.git
cd CORTEX

# Run setup script
python .cortex/setup-mcp-v2.py

# Reload VS Code
# Command Palette → Developer: Reload Window
```

### How It Works

The setup script:
1. Detects your operating system
2. Finds your Python interpreter
3. Generates the correct `.vscode/mcp.json`
4. Validates the MCP server starts

### Platform Differences

| Platform | Python Path |
|----------|-------------|
| macOS | `.venv/bin/python` |
| Windows | `.venv\Scripts\python.exe` |
| Linux | `.venv/bin/python` |

## JSON-RPC Protocol

MCP uses JSON-RPC 2.0 over stdio:

### Initialize

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {"protocolVersion": "2024-11-05"},
  "id": "1"
}
```

### List Tools

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": "2"
}
```

### Call Tool

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "cortex_lens",
    "arguments": {"operation": "analyze", "target": "."}
  },
  "id": "3"
}
```

## Testing

48 tests organized by concern:

- **Tool Consolidation** (5 tests): Verify 24 tools, categories, operations
- **Registry** (5 tests): Registration, lookup, schema generation
- **MCP Server** (6 tests): Initialization, tool listing, execution
- **JSON-RPC Protocol** (6 tests): Initialize, list, call, errors
- **Base Classes** (4 tests): Definition, result, validation
- **Cross-Platform** (5 tests): macOS, Windows, Linux
- **Extensibility** (3 tests): Custom tools, operations
- **Performance** (3 tests): Init <100ms, lookup O(1)
- **Integration** (2 tests): Full workflows
- **Regression** (4 tests): No dev tools, no duplicates

Run tests:
```bash
pytest cortex/mcp/v2/tests/test_mcp_v2.py -v
```

## Migration from v1

The legacy MCP server (`cortex/mcp/server.py`) with 98 tools will be deprecated. Migration path:

1. **Phase 1**: v2 available alongside v1
2. **Phase 2**: v2 becomes default, v1 deprecated
3. **Phase 3**: v1 removed

Tool mapping available in `cortex-registry/_cortex-master/waves/WAVE-100-MCP-V2-RESET.yaml`.
