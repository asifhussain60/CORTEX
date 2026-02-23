# MCP Setup Guide — CORTEX Framework

> **Pylance-style Architecture**: CORTEX MCP server auto-starts when VS Code opens the
> workspace. No manual server startup is required.

## Overview

The CORTEX MCP (Model Context Protocol) server runs as a background process managed
by VS Code. It automatically provides AI-powered tooling through the GitHub Copilot
Chat interface.

---

## Quick Setup

### Prerequisites

- VS Code 1.95+ with GitHub Copilot Chat extension
- Python 3.9+ in your PATH
- CORTEX workspace cloned locally

### Step 1 — Configure VS Code settings

Add the following to your `.vscode/settings.json`:

```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

The `stdio` transport means the MCP server communicates via standard input/output —
no TCP port, no manual startup needed.

### Step 2 — Verify environment

```bash
python3 -m cortex.mcp --version
python3 scripts/setup-mcp.py
```

This script auto-detects your OS and configures the environment accordingly.

---

## Pylance-Style Architecture

Like Pylance (the VS Code Python language server), CORTEX MCP auto-starts in the
background when VS Code activates the workspace extension. You **do not** need to:

- Manually start the server
- Run any background daemon
- Configure separate ports

VS Code handles the full lifecycle: start on workspace open, stop on workspace close.

---

## Platform Support

The setup script (`scripts/setup-mcp.py` or `.cortex-runtime/setup-mcp.py`) supports:

| Platform | Detection | Notes |
|---|---|---|
| macOS | `platform.system() == "Darwin"` | Homebrew Python recommended |
| Linux | `platform.system() == "Linux"` | System Python or venv |
| Windows | `sys.platform == "win32"` | PowerShell execution policy may need adjustment |

---

## Troubleshooting

### Server not starting

1. Verify Python path: `which python3`
2. Check CORTEX is installed: `python3 -c "import cortex; print('OK')"`
3. Check VS Code Output panel → "MCP: cortex" channel

### Logs

Setup logs are written to `.cortex-runtime/setup.log` on first run.

---

## MCP Tools Exposed

| Tool | Description |
|---|---|
| `cortex_onboard` (op: `full`) | LENS analysis + governance scoring |
| `cortex_validate` (op: `compliance`) | CORE rule scanning |
| `cortex_governance` (op: `query`) | Query governance state |
| `cortex_metrics` (op: `capture`) | Record TDD + debug metrics |
| `cortex_refactor` | Semantic refactoring operations |

---

## Security

- The MCP server runs with the **same permissions as VS Code**
- No network sockets are opened (stdio only)
- All tool calls are logged to `.cortex-runtime/traces/`
- Secrets are never passed through MCP tool arguments — use environment variables

See `SECURITY.md` for full threat model.

---

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [VS Code MCP Extension Docs](https://code.visualstudio.com/docs/copilot/mcp)
- CORTEX Architecture: `cortex-docs/ARCHITECTURE-RECOMMENDATION.md`
- Governance Rules: `cortex-registry/governance/`
