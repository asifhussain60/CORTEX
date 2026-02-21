# MCP Overview

---
title: MCP — Model Context Protocol Gateway
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-20
source_of_truth: cortex/mcp/ + .vscode/settings.json
order: 1
---

> **Brain analogy:** The MCP Gateway is the **spinal cord** — the high-bandwidth channel connecting the brain to the body. Every command from the brain (IDE) travels through the spinal cord (MCP) to reach the muscles (orchestrators). It doesn't process the command; it transmits it reliably and quickly.

---

## What Is MCP?

**Model Context Protocol** — a JSON-RPC 2.0 communication standard connecting IDEs to CORTEX. CORTEX implements MCP as a **Pylance-style stdio server** that auto-starts when VS Code opens the workspace.

- **Transport:** stdio (development) — no manual server startup
- **Protocol:** JSON-RPC 2.0
- **Tools:** 23 canonical MCP tools
- **Clients:** VS Code (Copilot Chat), Cursor, Claude Desktop

---

## How It Works

```
[VS Code / Cursor / Claude Desktop]
        │
        │  JSON-RPC 2.0 over stdio
        │
        ▼
[cortex/mcp/ — Pylance-style server]
        │
        ├── Tool validation
        ├── Rate limiting
        └── Dispatch to MCP tool function
        │
        ▼
[23 Canonical MCP Tools]
        │
        ▼
[Orchestrator Execution]
```

---

## Configuration

The MCP server auto-starts via `.vscode/settings.json`:

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

**Verification:** Call `cortex_sample_tool` in Copilot Chat. If it responds, MCP is active.

---

## Practical Examples

**Business Leader:** "MCP is the invisible infrastructure. Teams don't manage servers — the IDE starts CORTEX automatically when the workspace opens."

**Product Owner:** "23 tools available from any IDE that supports MCP. VS Code, Cursor, Claude Desktop — same tools, same experience."

**Developer:** "I open VS Code, and CORTEX is ready. No `python3 -m cortex.mcp start` command. No Docker container. It's just there. I call tools directly from Copilot Chat."

---

*Verified against MCP server configuration · 20 February 2026*
