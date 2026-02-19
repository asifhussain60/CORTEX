# CORTEX GitHub Copilot Instructions

## About CORTEX

CORTEX is a production-grade AI Engineering Framework built on:
- **Domain-Driven Orchestration** — each domain has exactly one canonical orchestrator
- **TDD-First Development** — CORE-008 mandates tests before implementation
- **LENS Analysis** — workspace-aware code intelligence on every turn
- **EventBus Architecture** — loose coupling between orchestrators via pub/sub

---

## MCP Architecture

CORTEX uses a **Pylance-style MCP architecture** — the MCP server behaves exactly
like Pylance (the VS Code Python language server):

> The server **auto-starts** when VS Code opens the workspace. You do not need to
> start it manually, and **no server startup** command is required.

VS Code manages the full lifecycle via the `github.copilot.chat.mcpServers` setting.

### How to Detect CORTEX MCP Server Status

Use the following three methods in sequence:

**Method 1 — Tool Registry Query**

Query the tool registry directly to verify CORTEX tools are registered:

```bash
# List registered MCP tools
python3 -c "from cortex.mcp import list_tools; print(list_tools())"
```

Check for `tool_query` response — if tools are listed, the server is active.

**Method 2 — Environment Variable Detection**

CORTEX sets `CORTEX_MCP_ACTIVE=1` when the server starts. Check:

```bash
echo $CORTEX_MCP_ACTIVE
```

If the env_vars variable is present, MCP is running.

**Method 3 — Network Port Check (optional)**

For HTTP transport mode (non-default), CORTEX listens on port 7890:

```bash
lsof -i :7890
```

Use `port` detection only when stdio transport is not available.

---

## Development Standards

All code in this repository must comply with CORE governance rules:

| Rule | Description |
|---|---|
| CORE-002 | No markdown/text file generation via bash |
| CORE-008 | Test-first development (TDD mandatory) |
| CORE-011 | Type hints on all functions |
| CORE-012 | Docstrings on all public APIs |
| CORE-028 | File naming: snake_case only |
| CORE-035 | Single canonical implementation |

---

## Workflow

1. **Write the test first** (CORE-008)
2. **Run LENS analysis** — every turn uses workspace context
3. **Implement minimum code** to pass tests
4. **EnforcementOrchestrator scans** — CORE rules checked before commit
5. **Commit** with authority tag

---

## File Organization

```
cortex/          ← Python source code
cortex-registry/ ← YAML governance rules & patterns
tests/           ← All test files (mirrors cortex/ structure)
.cortex-runtime/         ← Runtime data (logs, traces, setup)
.github/         ← CI/CD, prompts, copilot instructions
```

---

## Contact

- Architecture: `cortex-docs/ARCHITECTURE-RECOMMENDATION.md`
- MCP Setup: `.github/prompts/MCP-SETUP-GUIDE.md`
- Security: `cortex-docs/SECURITY.md`
