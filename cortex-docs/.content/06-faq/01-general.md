# FAQ — General & Getting Started

---
title: FAQ — General & Getting Started
type: reference
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-25
source_of_truth: cortex/ + cortex-registry/ + .github/copilot-instructions.md
order: 1
---

> **Purpose:** Answers to the most common questions about what CORTEX is, how to get started, and how it fits into your existing workflow. All answers verified against live code.

---

## What is CORTEX?

**CORTEX** (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI engineering framework. It combines:

- **27 wired orchestrators** across 3 tiers (core, domain, support)
- **26 active MCP tools** exposed via Pylance-style stdio server
- **35 CORE governance rules** (+ 2 AC rules) enforced at pre-commit, CI, and runtime
- **LENS** — an 10-analyzer parallel code intelligence engine
- **TDD-first execution** — CORE-008 mandates RED → GREEN → REFACTOR on every IMPLEMENT/FIX

It works directly inside your IDE (VS Code, Cursor, Claude Desktop) via the Model Context Protocol — no browser, no context switching.

---

## How is CORTEX different from GitHub Copilot or other AI coding tools?

| Dimension | Generic AI Coding Tools | CORTEX |
|-----------|------------------------|--------|
| **Scope** | Answer questions, suggest code | Orchestrate entire workflows end-to-end |
| **Governance** | None | 35 CORE rules enforced automatically |
| **TDD** | Optional | Mandatory (CORE-008) — blocked if skipped |
| **State** | Stateless per conversation | Persistent SQLite audit log (`.cortex-runtime/`) |
| **Architecture** | Single model | 27 specialized orchestrators, 3 tiers |
| **Observability** | None | OpenTelemetry, Prometheus, AC markers, SQLite traces |
| **Integration** | IDE only | IDE + CI/CD + pre-commit hooks + ADO/Jira work items |

CORTEX doesn't replace GitHub Copilot — it orchestrates it. The MCP server sits between your IDE and the orchestration layer.

---

## What IDEs does CORTEX support?

Any IDE or AI assistant that supports the **Model Context Protocol (MCP)** with stdio transport:

- ✅ **VS Code** with GitHub Copilot Chat (primary — Pylance-style auto-start)
- ✅ **Cursor**
- ✅ **Claude Desktop**
- ✅ Any MCP-compatible client

**VS Code auto-start:** When VS Code opens the CORTEX workspace, it reads `.vscode/settings.json` and starts the MCP server automatically — identical to how Pylance auto-starts. No manual server startup required.

---

## How do I verify CORTEX is running?

Three methods — any one is sufficient:

**Method 1 (fastest):** In Copilot Chat, call:
```
Call cortex_sample_tool
```
If it responds, MCP is live.

**Method 2 (settings check):** Open `.vscode/settings.json` and look for:
```json
"github.copilot.chat.mcpServers": { "cortex": { ... } }
```

**Method 3 (terminal):** Run `python3 -m cortex.mcp` — if it starts without import errors, the server is healthy.

---

## What Python version does CORTEX require?

**Python 3.9 or higher.** Verified by `UpgradeOrchestrator.validate_requirements()` at session start.

If the environment is incomplete, CORTEX attempts `pip install -r requirements.txt` autonomously before proceeding (CORE-049: silent execution).

To skip preflight in CI/CD: set `CORTEX_SKIP_PREFLIGHT=true`.

---

## How do I install CORTEX?

```bash
# 1. Clone the repository
git clone <your-cortex-repo-url>
cd CORTEX

# 2. Install dependencies
pip install -r requirements.txt

# 3. Open in VS Code — MCP auto-starts
code .

# 4. Verify (in Copilot Chat)
# Call cortex_sample_tool
```

Full setup guide: `00-getting-started/05-quick-start.md`

---

## Is there a Windows version?

Yes. All commands have Windows equivalents:

| Unix/macOS | Windows |
|-----------|---------|
| `python3` | `python` |
| `make test-batch` | VS Code Task: **CORTEX: Full Batch Run (Windows)** |
| `./scripts/run-tests.sh batch` | `python scripts\run_tests.py batch` |
| `python3 scripts/setup-mcp.py` | VS Code Task: **CORTEX: Setup MCP (Windows)** |

The MCP setup script (`scripts/setup-mcp.py`) auto-detects Windows/macOS/Linux and configures accordingly.

---

## What is the single canonical package name?

`cortex` — that's it. One Python package. All imports use `cortex.*`.

```python
from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
from cortex.lens.facade import LENSFacade
from cortex.mcp.tools.core import cortex_challenge
```

There is no `cortex_intelligence`, no `cortex_lens`, no `cortex.brain`. These were consolidated in the 12-phase Cohesive Brain Refactor (completed February 2026).

---

## How do I run the test suite?

**Always use the canonical runner — never raw pytest:**

```bash
# Recommended: full batch run
make test-batch

# Or cross-platform (works on Windows too)
python3 scripts/run_tests.py batch

# Smoke tests only (~30s)
make test-smoke

# Unit tests only
make test-fast
```

**Never use:** `python3 -m pytest tests/ -x -q` or any command that adds `-q` or overrides `-o addopts=` — these bypass the `CortexXdistPlugin` batch reporter and xdist parallelism.

The full suite contains **16,259 tests** (486 golden, 177 phase) and runs with `pytest-xdist` (`-n auto --dist loadscope`).

---

## Where does CORTEX store its runtime data?

All runtime data lives in `.cortex-runtime/` (gitignored):

| Path | Contents |
|------|---------|
| `.cortex-runtime/audit.db` | SQLite WAL audit log — all orchestrator events |
| `.cortex-runtime/traces/orchestrator-traces.db` | AC marker traces, sweep catalogues |
| `.cortex-runtime/sweeps/{sweep_id}.db` | Per-sweep CORE-064 tracking (SQLite WAL) |

No PostgreSQL, no MongoDB, no Redis required. The entire persistence layer is SQLite + Git-backed YAML.

---

## What is the `cortex-registry/` folder?

The **Git-backed configuration registry** — CORTEX's single source of truth for everything that isn't Python code:

```
cortex-registry/
├── core/tier0-skull/skull-rules.yaml   ← 35 CORE + 2 AC governance rules
├── cortex-master.yaml                  ← Thin phase index (≤500 lines)
├── planning/phases/                    ← Detailed phase files
├── workflows/templates/                ← 63 workflow YAML templates
├── patterns/                           ← 9 enterprise architecture patterns
└── knowledge/                          ← Domain knowledge base
```

All changes are versioned in Git — rollback is `git revert`. No database dependency.

---

*Verified against live codebase · 25 February 2026 · Phase 79-D Complete*
