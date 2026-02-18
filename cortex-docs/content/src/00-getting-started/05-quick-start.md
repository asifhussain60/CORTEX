# Quick Start Guide

---
title: CORTEX Quick Start — First Request in 5 Minutes
type: how-to
audience: [Software Developers]
last_verified: 2026-02-18
source_of_truth: deployment/ + cortex/mcp/ + .github/prompts/cortex-architect.prompt.md
format: diátaxis-how-to
order: 5
---

> **Goal:** Get CORTEX running in VS Code and send your first request in under 5 minutes. No prior knowledge of the internals required.

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.9+ | Runtime |
| VS Code | 1.85+ | IDE client |
| GitHub Copilot | Latest | Chat interface |
| Git | 2.x | Registry backend |

---

## Step 1 — Clone & Install

```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

---

## Step 2 — Verify the Environment

```bash
make verify
```

Expected output:
```
✅ Python 3.9+ detected
✅ Dependencies installed (47 packages)
✅ Git hooks configured (.githooks/)
✅ Registry integrity: OK (cortex-registry/)
✅ MCP server: ready
```

If any check fails, run `make setup` for auto-healing.

---

## Step 3 — Configure VS Code

Open VS Code in the CORTEX workspace:

```bash
code .
```

CORTEX auto-starts the MCP server (Pylance-style — no manual launch needed). You will see the CORTEX status indicator in the VS Code status bar within 2 seconds.

If using Claude Desktop or Cursor, add to your MCP config:

```json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "cortex.mcp.server"],
      "cwd": "/path/to/CORTEX"
    }
  }
}
```

---

## Step 4 — Send Your First Request

Open **GitHub Copilot Chat** (`Ctrl+Alt+I` / `Cmd+Option+I`) and type:

```
implement a function that validates an email address with full TDD
```

### What Happens Next

```
User Request
    │
    ▼
┌─────────────────────────────────┐
│  Stage -1: Request Rephrase     │  ~18ms
│  Enhances your prompt with      │
│  governance context             │
└──────────────────┬──────────────┘
                   │
    ▼
┌─────────────────────────────────┐
│  IntentRouter                   │  ~32ms
│  Classifies → IMPLEMENT intent  │
│  Routes to TDDOrchestrator      │
└──────────────────┬──────────────┘
                   │
    ▼
┌─────────────────────────────────┐
│  Holistic Validation Gate       │  ~150ms
│  Risk score: 0.1 (PASS)         │
│  No architecture drift detected │
└──────────────────┬──────────────┘
                   │
    ▼
┌─────────────────────────────────┐
│  TDDOrchestrator                │  ~850ms
│  RED  → writes failing test     │
│  GREEN → minimal implementation │
│  REFACTOR → clean structure     │
└──────────────────┬──────────────┘
                   │
    ▼
┌─────────────────────────────────┐
│  EnforcementOrchestrator        │  ~50ms
│  8-agent governance validation  │
│  All checks: PASS               │
└─────────────────────────────────┘
```

**Total time:** ~1.1 seconds for a simple function.

---

## Step 5 — Common Commands

| Command | What It Does |
|---------|-------------|
| `implement {feature}` | TDD implementation workflow |
| `fix {bug}` | Diagnosis + fix with tests |
| `audit` | Governance scan of current file |
| `/audit` | Full workspace governance audit |
| `/vacuum` | Clean legacy/redundant files |
| `/onboard {repo-path}` | Analyse an external repository |
| `summarize {topic}` | Knowledge digest |

---

## Step 6 — Understand the Output

CORTEX always responds inline in chat — never creates `.md` report files (CORE-002).

**Progress bars** appear during execution:
```
████████░░  80%  Writing tests (RED phase)
██████████ 100%  All 5/5 tests passing ✅
```

**Completion summaries** appear as markdown tables:
```
| Metric        | Value         |
|---------------|---------------|
| Tests Added   | 5             |
| Coverage      | 98%           |
| Risk Score    | 0.1 (PASS)    |
| Elapsed       | 1.1s          |
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| MCP not connecting | Server not started | Run `make mcp-start` |
| Tests failing | Missing dependency | Run `pip install -r requirements.txt` |
| Governance block | TDD not followed | Write test first, then request implementation |
| Slow LENS analysis | Cold cache | First run warms cache; subsequent runs ~70% faster |

---

## Next Steps

Once your first request works, explore in order:

1. **[Key Concepts](./02-key-concepts.md)** — Understand the terminology
2. **[How CORTEX Works](./03-how-cortex-works.md)** — End-to-end mental model
3. **[Capabilities Overview](../01-capabilities/01-overview.md)** — Full feature inventory
4. **[MCP Tools Catalog](../04-mcp/03-tools-catalog.md)** — All 26 tools reference

---

*Last verified: 2026-02-18 | Source: deployment/ + cortex/mcp/ + Makefile*
