# MCP Setup Guide — Pylance-Style Architecture

**Authority:** ENH-066 | **Date:** 2026-02-15

## Overview

CORTEX MCP runs **locally within VS Code** using a Pylance-style architecture.
VS Code will **automatically** start the MCP server when Copilot Chat invokes any
`cortex_*` tool — **no manual server startup** is required.

The MCP server communicates over **stdio** using JSON-RPC 2.0, identical to how
Pylance, ESLint, and other language servers operate.

## Auto-Start Behaviour

When you invoke a `cortex_*` tool in Copilot Chat, VS Code reads the MCP server
configuration from `.vscode/settings.json` and auto-starts the process. There is
**no server startup** step for developers.

## VS Code Settings Configuration

Add this to `.vscode/settings.json`:

```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "type": "stdio",
      "command": "python3 -m cortex.mcp",
      "args": ["--mode", "stdio"],
      "env": {
        "CORTEX_MCP_ENABLED": "true",
        "CORTEX_MODE": "architect"
      }
    }
  }
}
```

### Key Settings

| Setting | Purpose |
|---------|---------|
| `type: stdio` | Use stdio transport (not HTTP) |
| `command` | `python3 -m cortex.mcp` starts the MCP server module |
| `env` | Environment variables injected into the server process |

## Setup Script

Run the setup script to auto-generate platform-specific settings:

```bash
python .cortex/setup-mcp.py
```

The script:
1. Detects your OS and Python path
2. Creates `.vscode/settings.json` with the correct `python` / `python3` command
3. Validates the MCP module is importable
4. Writes `.cortex/setup.log` with results

## Cross-Platform Support

The setup script handles platform differences:

| Platform | Python Executable | venv path |
|----------|------------------|-----------|
| macOS / Linux (Darwin) | `bin/python` | `.venv/bin/python` |
| Windows (win32) | `Scripts/python.exe` | `.venv/Scripts/python.exe` |

## Detection Methods

CORTEX validates MCP availability using 3 methods (see copilot-instructions.md):

1. **Method 1 — Tool Registry:** Query Copilot for `cortex_*` tools
2. **Method 2 — Environment Variables:** Check `CORTEX_MCP_ENABLED`
3. **Method 3 — Network Port:** Health check on `localhost:9000`

## Troubleshooting

If MCP tools are not available:

```bash
# 1. Re-run setup
python .cortex/setup-mcp.py

# 2. Reload VS Code
# Command Palette → Developer: Reload Window

# 3. Verify in Copilot Chat
# Type: "what MCP tools are available?"
```

---
*ENH-066: Pylance-Style MCP Architecture Documentation*
