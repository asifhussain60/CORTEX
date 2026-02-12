# CORTEX MCP v2 Migration Guide

**Version:** 2.0.0  
**Date:** 2026-02-12  
**Status:** PRODUCTION READY

---

## Overview

CORTEX MCP v2 represents a complete architectural reset of the Model Context Protocol implementation:

| Metric | v1 (Legacy) | v2 (Current) | Change |
|--------|-------------|--------------|--------|
| **Tools** | 98 | 24 | 75% reduction |
| **Files** | 78 (744 KB) | 6 | 92% reduction |
| **Test Coverage** | Partial | 123 tests | Comprehensive |
| **Cross-Platform** | Issues | Full support | ✅ |
| **Architecture** | Scattered | Consolidated | ✅ |

---

## For Team Members: Quick Start

### Step 1: Pull Latest Code

```bash
git checkout CORTEX
git pull origin CORTEX
```

### Step 2: Run Setup Script

The setup script is **cross-platform** (macOS, Windows, Linux):

```bash
python .cortex/setup-mcp-v2.py
```

This will:
- ✅ Detect your OS automatically
- ✅ Find your Python interpreter
- ✅ Generate correct `.vscode/settings.json`
- ✅ Configure MCP v2 for Copilot Chat

### Step 3: Reload VS Code

1. Open Command Palette: `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: "Developer: Reload Window"
3. Press Enter

### Step 4: Verify MCP Tools Available

Open Copilot Chat and type:
```
@workspace what MCP tools are available?
```

You should see 24 production tools listed.

---

## What Changed?

### Tool Consolidation

**Before (v1):** 98 scattered tools with duplicates

**After (v2):** 24 consolidated tools organized by capability

#### Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| **Core (4)** | `cortex_process_request`, `cortex_challenge`, `cortex_classify`, `cortex_request_lifecycle` | Main entry points |
| **Intelligence (3)** | `cortex_lens`, `cortex_knowledge`, `cortex_git` | Code analysis, search, history |
| **Governance (3)** | `cortex_governance`, `cortex_validate`, `cortex_load` | Rules, compliance, loading |
| **Operations (5)** | `cortex_debug`, `cortex_refactor`, `cortex_plan`, `cortex_onboard`, `cortex_dashboard` | Development workflows |
| **Utilities (9)** | `cortex_verify`, `cortex_ask`, `cortex_vacuum`, `cortex_tools_catalog`, `cortex_total_recall`, `cortex_metrics`, `cortex_check`, `cortex_vision`, `cortex_orchestrator` | Support functions |

### Architecture Changes

**v1 Structure:**
```
cortex/mcp/
├── tools/
│   ├── analysis_*.py (13 files)
│   ├── debug_*.py (13 files)
│   ├── governance_*.py (20 files)
│   └── ... (78 files total)
└── server.py
```

**v2 Structure:**
```
cortex/mcp/
├── v2/
│   ├── __init__.py
│   ├── base.py (Tool, ToolResult, ToolCategory)
│   ├── registry.py (24 production tools)
│   ├── server.py (MCPServerV2)
│   ├── tools/
│   │   ├── core.py (4 tools)
│   │   ├── intelligence.py (3 tools)
│   │   ├── governance.py (3 tools)
│   │   ├── operations.py (5 tools)
│   │   └── utilities.py (9 tools)
│   └── tests/ (123 tests)
└── __init__.py (v1→v2 redirect)
```

### Backward Compatibility

**v1 imports still work:**
```python
# Old code continues to work
from cortex.mcp.server import MCPServer

# But v2 is recommended
from cortex.mcp.v2 import MCPServerV2
```

---

## For Developers: API Changes

### Server Initialization

**v1:**
```python
from cortex.mcp.server import MCPServer
server = MCPServer(enable_auth=True)
```

**v2:**
```python
from cortex.mcp.v2 import MCPServerV2
server = MCPServerV2()  # Auth handled by environment
```

### Tool Invocation

**v1:**
```python
# Multiple tools for same capability
result = cortex_lens_analyze(target=".")
result = cortex_ast_analyze(target=".")
result = cortex_git_history(hours=24)
```

**v2:**
```python
# Single tool with operation parameter
result = cortex_lens(operation="analyze", target=".")
result = cortex_lens(operation="ast", target=".")
result = cortex_git(operation="history", hours=24)
```

### Tool Registration

**v1:**
```python
# Manual registration in server.py
from cortex.mcp.tools.analysis_tools import AnalysisTool
server.register_tool(AnalysisTool())
```

**v2:**
```python
# Automatic registration via registry
from cortex.mcp.v2.registry import register_tool

@register_tool("cortex_custom", category=ToolCategory.UTILITIES)
class CustomTool(ConsolidatedTool):
    ...
```

---

## Cross-Platform Setup Details

### macOS / Linux

**Python Path:** `.venv/bin/python`

**VS Code Settings:**
```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "type": "stdio",
      "command": "/absolute/path/to/CORTEX/.venv/bin/python",
      "args": ["-m", "cortex.mcp"],
      "cwd": "/absolute/path/to/CORTEX",
      "env": {
        "PYTHONPATH": "/absolute/path/to/CORTEX",
        "CORTEX_MCP_ENABLED": "true",
        "CORTEX_MCP_VERSION": "2.0.0"
      }
    }
  }
}
```

### Windows

**Python Path:** `.venv\Scripts\python.exe`

**VS Code Settings:**
```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "type": "stdio",
      "command": "C:\\absolute\\path\\to\\CORTEX\\.venv\\Scripts\\python.exe",
      "args": ["-m", "cortex.mcp"],
      "cwd": "C:\\absolute\\path\\to\\CORTEX",
      "env": {
        "PYTHONPATH": "C:\\absolute\\path\\to\\CORTEX",
        "CORTEX_MCP_ENABLED": "true",
        "CORTEX_MCP_VERSION": "2.0.0"
      }
    }
  }
}
```

**Important:** `.vscode/settings.json` is **NOT** committed to git (cross-platform policy). Each developer generates their own via `setup-mcp-v2.py`.

---

## Troubleshooting

### MCP Tools Not Available

**Symptoms:** Copilot Chat doesn't see CORTEX tools

**Solutions:**

1. **Check VS Code settings:**
   ```bash
   cat .vscode/settings.json | grep mcpServers
   ```
   Should show `cortex` configuration.

2. **Re-run setup:**
   ```bash
   python .cortex/setup-mcp-v2.py
   ```

3. **Reload VS Code:**
   Command Palette → "Developer: Reload Window"

4. **Check Python path:**
   ```bash
   which python  # macOS/Linux
   where python  # Windows
   ```
   Should point to `.venv` interpreter.

### Tests Failing

**Run tests:**
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

python -m pytest cortex/mcp/v2/tests/ -v
```

**Expected:** 123 tests passing

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'cortex.mcp.v2'`

**Solution:**
```bash
# Ensure PYTHONPATH includes workspace root
export PYTHONPATH=/path/to/CORTEX:$PYTHONPATH  # macOS/Linux
set PYTHONPATH=C:\path\to\CORTEX;%PYTHONPATH%  # Windows
```

---

## Migration Timeline

| Date | Action | Status |
|------|--------|--------|
| 2026-02-12 | v2 development complete | ✅ |
| 2026-02-12 | Tests passing (123/123) | ✅ |
| 2026-02-12 | Migration guide published | ✅ |
| 2026-02-13 | Team onboarding begins | 🔵 |
| 2026-02-15 | v1 marked deprecated | ⚪ |
| 2026-03-01 | v1 removal planned | ⚪ |

---

## Questions?

Contact: Asif Hussain (CORTEX Architect)

Documentation: `.github/prompts/cortex-architect.prompt.md`

Registry: `cortex-registry/_cortex-master/waves/WAVE-100-MCP-V2-RESET.yaml`
