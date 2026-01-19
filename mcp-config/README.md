# MCP Configuration Guide

## Overview

CORTEX is configured as an MCP (Model Context Protocol) server that can be used with Claude Desktop and VS Code.

## Claude Desktop Integration

### On macOS
1. Locate Claude's configuration directory: `~/.config/claude/`
2. Edit (or create) `claude_desktop_config.json`
3. Add the CORTEX server configuration from `mcp-config/claude-desktop.json`
4. Restart Claude Desktop

### Configuration
```json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "src.mcp"],
      "cwd": "/path/to/CORTEX",
      "env": {
        "CORTEX_DB_PATH": "/path/to/CORTEX/cortex_brain/state/governance.db"
      }
    }
  }
}
```

## VS Code Integration

### Setup
1. Install the MCP extension (if available)
2. Add the configuration from `mcp-config/vscode-mcp.json` to your VS Code settings
3. Restart VS Code

### Configuration
```json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "src.mcp"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

## Available Tools

CORTEX exposes the following MCP tools:

### Orchestrator Tools
- `scaffold_orchestrator` - Generate a new orchestrator from template
- `validate_template` - Validate an orchestrator template
- `check_phase_readiness` - Check if a phase is ready to start

### Knowledge Management
- `ingest_business_knowledge` - Ingest business knowledge documents
- `query_audit_trail` - Query the governance audit trail

### And many more...

## Protocol Details

- **Transport**: stdio (JSON-RPC 2.0)
- **Encoding**: UTF-8
- **Protocol Version**: 2024-11-05

## Troubleshooting

### Server won't start
- Check that Python 3.9+ is available
- Verify CORTEX dependencies are installed: `pip install -r requirements.txt`
- Check that `src/mcp/` directory exists and has `__init__.py`

### Tools not showing up
- Restart the client (Claude, VS Code)
- Check server logs for errors
- Verify tool functions have `@mcp_tool` decorator

### Connection refused
- Ensure the server is running
- Check that stdio transport is working correctly
- Verify environment variables are set correctly

## Development

To test the MCP server locally:

```bash
cd /path/to/CORTEX
python -m src.mcp
```

This starts the server in stdio mode. Send JSON-RPC requests to test.
