# CORTEX Quick Start Guide

---
title: CORTEX Quick Start — First Request in 5 Minutes
type: how-to
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: .vscode/settings.json + cortex/mcp/
consolidates: [00-getting-started-quick-start]
order: 3
---

> **Goal:** Get CORTEX running in your IDE and process your first request in under 5 minutes.

---

## Prerequisites

- VS Code with GitHub Copilot Chat (or Cursor / Claude Desktop)
- Python 3.9 or later installed
- The CORTEX repository cloned locally

---

## Step 1: Open the Workspace (30 seconds)

Open the CORTEX repository in VS Code. The MCP server is configured to auto-start via Pylance-style stdio — no manual startup required. When VS Code opens the workspace, it reads the MCP server configuration from `.vscode/settings.json` and starts the server automatically, connecting to CORTEX over JSON-RPC 2.0 stdio transport.

---

## Step 2: Verify MCP Is Active (30 seconds)

Open GitHub Copilot Chat and call `cortex_verify`. If you see a response, MCP is active. If not, verify that Python 3.9 or later is on your PATH and that all dependencies are installed via `pip install -r requirements.txt`.

---

## Step 3: Your First Request (1 minute)

Try any of these in Copilot Chat:

| What You Type | What Happens |
|--------------|-------------|
| "Analyze this codebase" | LENS runs parallel analyzers and delivers an inline report |
| "What MCP tools are available?" | The tools catalog lists all registered tools |
| "Check governance compliance" | Validates CORE rule compliance |
| "Onboard this repository" | Runs LENS analysis and creates a dashboard |
| "Run health check" | Checks Python version, dependencies, and MCP connectivity |

---

## Step 4: Run the Test Suite (2 minutes)

Open the VS Code Command Palette and search for "Tasks: Run Task". You will see tiered test profiles:

| Task | What It Runs | Speed |
|------|-------------|-------|
| Smoke Tests (Parallel) | Tests marked as smoke | Around 30 seconds |
| Unit Tests (Parallel) | Unit tests with automatic worker distribution | Around 2 minutes |
| Integration Tests | Integration tests with 4 workers | Around 3 minutes |
| Golden Tests (Serial) | Deterministic golden tests | Around 1 minute |
| Full Parallel Suite | Everything with automatic distribution | Around 5 minutes |

Alternatively, use the canonical test runner from the terminal: `make test-smoke` for a quick sanity check, `make test-preflight` for the fastest gate (under 10 seconds), or `make test` for the full unit suite.

---

## Step 5: Understand the Structure (1 minute)

The workspace is organised into well-defined directories. The `cortex/` directory contains all Python source code across 20 subdirectories including orchestrators, MCP tools, core modules, testing framework, intelligence, LENS, governance, and infrastructure. The `cortex-registry/` directory holds all YAML governance rules, patterns, and workflow templates. The `tests/` directory mirrors the cortex structure with golden, unit, and integration tests. The `.cortex-runtime/` directory stores runtime data including SQLite databases and execution traces.

---

## What Just Happened?

When you opened VS Code, the MCP server started automatically, registered tools became available in Copilot Chat, CORTEX loaded governance rules from the registry, and the test framework registered its parallel runner and quality gate plugins.

When you ran a request, the RequestRephraseOrchestrator enriched it (Stage −1), the MCP Gateway validated and routed it (Stage 0), the IntentRouter classified intent (Stage 1), the appropriate orchestrator executed the workflow, results were delivered inline (CORE-002), and the audit trail was recorded to the SQLite database.

---

## Common Next Steps

| Goal | Action |
|------|--------|
| Understand the full pipeline | Read the Platform Overview |
| See all MCP tools | Read the MCP Gateway reference |
| Learn about governance | Read the Governance and Workflows section |
| Understand the Brain tiers | Read the Intelligence Architecture |
| Contribute to CORTEX | Follow TDD: write failing test, implement, refactor |

---

*Verified against live MCP server*
