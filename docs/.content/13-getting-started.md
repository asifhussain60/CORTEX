# Getting Started with CORTEX

---
title: Getting Started — Setup, First Steps, and Quick Reference
type: guide
audience: [Software Developers]
last_verified: 2026-03-07
order: 13
---

> **The central idea:** CORTEX requires no special infrastructure. If you have Python 3.9+ and a supported IDE, you are minutes away from your first session. This guide covers prerequisites, setup, your first requests, and the commands you'll use every day.

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| **Python** | 3.9 | 3.11 recommended for best performance |
| **Git** | 2.30 | Required for commit hooks and audit trail |
| **VS Code** | 1.85 | GitHub Copilot extension required |
| **GitHub Copilot** | Active subscription | Chat mode required for MCP communication |
| **Disk space** | 500 MB | Repository + dependencies + runtime database |

No Docker. No Kubernetes. No database server. No cloud infrastructure. Everything runs locally from a single Python package.

---

## Five-Step Setup

### Step 1 — Clone the Repository

```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
```

### Step 2 — Create and Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows PowerShell
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Open in VS Code

```bash
code .
```

VS Code opens the workspace. The CORTEX MCP server starts automatically — no manual startup required.

### Step 5 — Verify Everything Works

In the VS Code terminal:

```bash
make test-smoke
```

A passing smoke test (under 60 seconds) confirms Python, dependencies, and the test suite are all healthy.

---

## Verifying the AI Connection

The AI-powered features work through GitHub Copilot Chat. To confirm CORTEX is connected:

1. Open Copilot Chat (`Ctrl+Shift+I` / `Cmd+Shift+I`)
2. Select **Agent** mode in the chat dropdown
3. Click the **Tools** button — you should see CORTEX tools listed
4. Type a test message: `What is CORTEX?`

If CORTEX tools appear in the tools list, the connection is active. If they don't appear, run `python3 scripts/setup-mcp.py` in the terminal and reload the VS Code window.

---

## Your First Requests

Once connected, you can interact with CORTEX entirely through natural language in Copilot Chat. Here are example requests that demonstrate the range of capabilities:

| What You Want | What to Ask |
|---|---|
| Understand what CORTEX can do | `What capabilities does CORTEX provide?` |
| Review code quality | `Review the code quality of src/services/user_service.py` |
| Check governance compliance | `Run a compliance check on the current codebase` |
| Start a new feature with TDD | `Implement user email verification using TDD` |
| Find and fix quality issues | `Audit the codebase and fix all quality issues` |
| Debug a failing test | `Debug why the authentication tests are failing` |
| Understand a codebase | `Analyse the architecture of this repository` |
| Check security posture | `Run a security audit` |
| Refactor a file | `Refactor user_controller.py to follow clean architecture` |
| Generate documentation | `Generate documentation for the payment module` |

---

## Running Tests — Quick Reference

All test commands use the scripts/run_tests.py runner or the equivalent Makefile targets. Always use these — running pytest directly bypasses the optimised configuration.

| Task | Command | When to Use |
|---|---|---|
| **After saving a file** | `make test-changed` | TDD inner loop — fastest feedback |
| **Before committing** | `make test-smoke` | Quick sanity check (< 60 seconds) |
| **Full unit suite** | `make test` | Local development, after larger changes |
| **Complete suite** | `make test-parallel` | Pre-commit, pre-push (uses all CPU cores) |
| **CI-safe sequential** | `make test-batch` | Continuous integration environments |
| **Critical wiring only** | `make test-preflight` | Fastest check — integration critical paths |

On Windows, replace `make test-*` with `python scripts\run_tests.py {mode}` in PowerShell.

---

## VS Code Tasks — Click to Run

All test commands are also available as VS Code tasks (no terminal required):

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type `Run Task`
3. Select any CORTEX task from the list

Available tasks include all test modes, MCP setup, and the full audit pipeline.

---

## Workspace Structure at a Glance

| Path | What Lives Here |
|---|---|
| `cortex/` | All CORTEX source code (the Python package) |
| `cortex/orchestrators/` | The 290+ orchestrators that handle every request type |
| `cortex/mcp/tools/` | The 32 tools exposed to Copilot Chat |
| `cortex-registry/` | Governance rules, workflow templates, knowledge base (YAML) |
| `tests/` | The full test suite (mirrors `cortex/` structure) |
| `.cortex-runtime/` | Runtime databases and logs (auto-created, excluded from git) |
| `cortex-docs/` | User-facing documentation (HTML/CSS site) |
| `scripts/` | Development utilities and maintenance scripts |
| `deployment/` | Production infrastructure configuration |

---

## Environment Variables — Quick Reference

These environment variables adjust CORTEX behaviour for specific scenarios. Defaults work for most situations — only change these when you have a specific reason.

| Variable | Effect | Default |
|---|---|---|
| `CORTEX_WORKERS=4` | Cap parallel test workers (useful on low-core CI machines) | All available cores |
| `CORTEX_DISABLE_PARALLEL=true` | Force sequential test execution | Parallel enabled |
| `CORTEX_DISABLE_TESTMON=true` | Skip change-detection in test runs | Change-detection enabled |
| `CORTEX_SKIP_PREFLIGHT=true` | Skip dependency validation at startup | Validation enabled |
| `CORTEX_DISABLE_DB_CLEANUP=true` | Skip database maintenance (for CI environments) | Cleanup enabled |

---

## Common Next Steps

After your first successful session, most developers explore:

1. **Read the governance rules** — `cortex-registry/core/` contains the 32 rules CORTEX enforces. Understanding them helps you understand why CORTEX makes the recommendations it does.

2. **Run your first audit** — In Copilot Chat, ask for a full audit: `Audit the codebase and fix all quality issues`. Watch the nine-stage pipeline work through the codebase systematically.

3. **Try test-driven development** — Ask CORTEX to implement a small feature using TDD: `Implement a simple rate limiter using TDD`. Observe how CORTEX writes the test first, then implements to make it pass.

4. **Explore the knowledge base** — Ask `What enterprise patterns does CORTEX recognise?` to see the architectural intelligence available.

5. **Review the operational documentation** — The files in this `cortex-docs/.content/` folder provide detailed explanation of each capability area.

---

## Getting Help

**Within Copilot Chat:** Ask `What can CORTEX help me with?` or `How do I [specific task]?` — CORTEX will route the question to the appropriate specialist and provide a direct answer.

**For environment issues:** Run `python3 scripts/setup-mcp.py` to reconfigure the MCP connection. Run `make test-preflight` to validate that critical dependencies are working.

**For unexpected behaviour:** Ask CORTEX directly: `Why did CORTEX recommend X?` or `Explain the governance rule that blocked Y.` The audit trail stores the reasoning behind every decision.

---

*Setup instructions verified against live repository configuration*
