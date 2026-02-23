# Quick Start Guide

---
title: CORTEX Quick Start — First Request in 5 Minutes
type: how-to
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: .vscode/settings.json + cortex/mcp/
format: tutorial
order: 5
---

> **Goal:** Get CORTEX running in your IDE and process your first request in under 5 minutes.

---

## Prerequisites

- **VS Code** with GitHub Copilot Chat (or Cursor / Claude Desktop)
- **Python 3.9+** installed
- The CORTEX repository cloned locally

---

## Step 1: Open the Workspace (30 seconds)

Open the CORTEX repository in VS Code. The MCP server is configured to **auto-start** via Pylance-style stdio — no manual startup required.

**How it works:** When VS Code opens the workspace, it reads `.vscode/settings.json` and starts the MCP server automatically:

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

---

## Step 2: Verify MCP Is Active (30 seconds)

Open GitHub Copilot Chat and type:

```
Call cortex_sample_tool
```

If you see a response, MCP is active. If not, check that:
- Python 3.9+ is on your PATH
- `requirements.txt` dependencies are installed: `pip install -r requirements.txt`

---

## Step 3: Your First Request (1 minute)

Try any of these in Copilot Chat:

| What You Type | What Happens |
|--------------|-------------|
| "Analyze this codebase" | LENS runs 8 parallel analyzers, delivers inline report |
| "What MCP tools are available?" | `cortex_tools_catalog` lists all 23 tools |
| "Check governance compliance" | `cortex_validate_compliance` checks CORE rules |
| "Onboard this repository" | `cortex_onboard_repository` runs LENS + creates dashboard |
| "Run health check" | `cortex_verify_environment` checks Python, deps, MCP connectivity |

---

## Step 4: Run the Test Suite (2 minutes)

Open the VS Code Command Palette (`Cmd+Shift+P`) and search for "Tasks: Run Task". You'll see 6 tiered test profiles:

| Task | What It Runs | Speed |
|------|-------------|-------|
| **Smoke Tests (Parallel)** | Tests marked `@pytest.mark.smoke` | ~30s |
| **Unit Tests (Parallel)** | `tests/unit/` with `-n auto` | ~2min |
| **Integration Tests** | `tests/integration/` with 4 workers | ~3min |
| **Golden Tests (Serial)** | `tests/golden/` — deterministic | ~1min |
| **Full Parallel Suite** | Everything with `-n auto` | ~5min |
| **Debug (Serial)** | Full suite, no xdist, verbose | ~15min |

Or run from the terminal:

```bash
# Quick smoke test
python3 -m pytest tests/ -m smoke -n auto --dist loadfile -v

# Full parallel suite (recommended)
python3 -m pytest tests/ -n auto --dist loadscope --tb=short
```

---

## Step 5: Understand the Structure (1 minute)

```
cortex/                   ← Python source (1 canonical package)
  orchestrators/          ← 17 wired orchestrators across 3 tiers
  mcp/tools/              ← 26 MCP tools
  core/                   ← OrchestratorBase, FileFactory, WorkflowEngine
  testing/                ← Test framework, parallel runner, quality gate
  intelligence/           ← Brain: perception, reasoning, action, domain
  lens/                   ← 8-analyzer code intelligence
  governance/             ← Rule enforcement, compliance
  infrastructure/         ← CortexAuditDB, infrastructure detection

cortex-registry/          ← YAML governance rules, patterns, plans
  core/tier0-skull/       ← skull-rules.yaml (35 CORE rules, 22 actively enforced)
  patterns/               ← 9 enterprise architecture patterns
  planning/               ← cortex-refactor-master.yaml
  workflows/              ← Workflow templates

tests/                    ← All tests (mirrors cortex/ structure)
  golden/                 ← 696 golden tests (must always pass)
  unit/                   ← Unit tests (parallel)
  integration/            ← Integration tests

.cortex-runtime/          ← Runtime data (SQLite DBs, logs, traces)
```

---

## What Just Happened?

When you opened VS Code:
1. MCP server started automatically (Pylance-style stdio)
2. 26 active tools became available in Copilot Chat
3. CORTEX loaded governance rules from `cortex-registry/core/tier0-skull/skull-rules.yaml`
4. The test framework registered the parallel runner and quality gate plugins

When you ran a request:
1. RequestRephraseOrchestrator enriched your request (Stage -1)
2. MCP Gateway validated and routed it (Stage 0)
3. IntentRouter classified intent (Stage 1)
4. The appropriate orchestrator executed the workflow
5. Results were delivered inline (CORE-002)
6. Audit trail was recorded to CortexAuditDB

---

## Common Next Steps

| I want to… | Do this |
|------------|---------|
| Understand the full pipeline | Read `03-how-cortex-works.md` |
| See all MCP tools | Read `04-mcp/03-tools-catalog.md` |
| Learn about governance | Read `01-capabilities/07-governance-compliance.md` |
| Understand the Brain tiers | Read `04-brain-tier-architecture.md` |
| Contribute to CORTEX | Follow TDD: write failing test → implement → refactor |

---

*Verified against live MCP server · 20 February 2026*
