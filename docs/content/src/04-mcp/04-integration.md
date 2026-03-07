# MCP Integration

---
title: MCP Integration — IDE & Client Setup
type: how-to
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: .vscode/settings.json + cortex/mcp/
order: 4
---

> **Brain analogy:** Integration is how the spinal cord **connects to different body parts**. VS Code is the hands (primary workspace), Cursor is the eyes (visual focus), Claude Desktop is the voice (conversational interface). Each connects through the same spinal cord (MCP), same reflexes (tools), same brain (CORTEX).

---

## VS Code Integration (Primary)

### Auto-Start Configuration

CORTEX uses **Pylance-style MCP** — the server starts automatically when the workspace opens.

`.vscode/settings.json`:
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

### Verification Steps

1. Open VS Code in the CORTEX workspace
2. Open Copilot Chat (Ctrl+Shift+I / Cmd+Shift+I)
3. Type: "Call `cortex_sample_tool`"
4. If it responds → MCP is active
5. Type: "Call `cortex_tools_catalog`" → see all 23 tools

### VS Code Tasks Integration

CORTEX provides 9 pre-configured tasks in `.vscode/tasks.json`:

| Task | Command |
|------|---------|
| Smoke Tests (Parallel) | `pytest tests/ -m smoke -n auto` |
| Unit Tests (Parallel — loadscope) | `pytest tests/unit/ -n auto --dist loadscope` |
| Integration Tests (4 workers) | `pytest tests/integration/ -n 4 --dist loadfile` |
| Golden Tests (Serial) | `pytest tests/golden/ -p no:xdist` |
| Full Parallel Suite | `pytest tests/ -n auto --dist loadscope` |
| Debug (Serial — no xdist) | `pytest tests/ -p no:xdist --tb=long -v -s` |
| Full Test Suite | `pytest tests/ -v --tb=short` |
| Full Test Suite (Live) | `pytest tests/ -v --tb=short` (live output) |
| Full Suite — No Stop on Fail | `pytest tests/ -v --continue-on-collection-errors` |

---

## Cursor Integration

Cursor supports MCP servers natively. Same configuration:

`.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "/path/to/CORTEX"
    }
  }
}
```

---

## Claude Desktop Integration

Claude Desktop supports MCP through its settings:

`claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "/path/to/CORTEX"
    }
  }
}
```

---

## Custom JSON-RPC Client

Any application that speaks JSON-RPC 2.0 over stdio can connect:

```python
import subprocess
import json

# Start MCP server
proc = subprocess.Popen(
    ["python3", "-m", "cortex.mcp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd="/path/to/CORTEX"
)

# Send tools/list request
request = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
}
proc.stdin.write(json.dumps(request).encode() + b"\n")
proc.stdin.flush()

# Read response
response = json.loads(proc.stdout.readline())
# response["result"]["tools"] → list of 23 tools
```

---

## Environment Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.9+ |
| VS Code | 1.85+ (for MCP support) |
| Copilot | Latest (with MCP tool calling) |
| Dependencies | `requirements.txt` (pip install -r) |

### Quick Environment Check

```bash
# Verify Python version
python3 --version  # Must be 3.9+

# Install dependencies
pip install -r requirements.txt

# Verify MCP server starts
python3 -m cortex.mcp --help
```

Or use the MCP tool: `cortex_verify` — checks Python version, dependencies, and MCP connectivity.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "MCP server not found" | settings.json misconfigured | Verify `cwd` path and `command` |
| Tools not appearing | Server failed to start | Check `python3 -m cortex.mcp` in terminal |
| Import errors | Missing dependencies | Run `pip install -r requirements.txt` |
| Slow startup | Large workspace scan | First launch scans workspace; subsequent launches are cached |
| Tool timeout | Long-running operation | Some tools (LENS analysis, onboarding) can take 30-60s |

---

## Practical Examples

**Product Owner:** "CORTEX works in VS Code, Cursor, and Claude Desktop with the same configuration. Teams choose their preferred IDE — the tools are identical."

**Developer:** "I open VS Code and start coding. Copilot Chat has access to all 23 CORTEX tools. I can ask it to analyze code, run tests, check governance compliance, or onboard a new repo — all without leaving the editor."

---

*Verified against MCP integration configuration · 20 February 2026*
