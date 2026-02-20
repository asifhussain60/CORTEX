# CORTEX GitHub Copilot Instructions

**Updated:** 2026-02-20 | ## About CORTEX

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI Engineering Framework:

- **52 Canonical Orchestrators** across 10 domains (core, domain, git, health, intelligence, strategies, support, synthesis, validation, workflow)
- **23 MCP Tools** via Pylance-style stdio server (auto-starts with VS Code)
- **17 CORE Governance Rules** enforced at pre-commit, CI, and runtime
- **TDD-First Development** — CORE-008: tests before implementation, no exceptions
- **LENS Analysis** — workspace-aware code intelligence (Language → Examination → Navigation → Synthesis)
- **1 Canonical Package** — all imports use `cortex.*` (no `cortex_intelligence`, `cortex_lens`, or `cortex.brain`)

---

## Architecture

| Metric | Value |
|---|---|
| Package | `cortex` (single canonical) |
| Orchestrators | 52 classes in `cortex/orchestrators/` |
| MCP Tools | 23 in `cortex/mcp/tools/` |
| Top-level Dirs | 16 canonical under `cortex/` |
| Governance Rules | 17 active in `cortex-registry/core/` |
| Test Suite | 15,230 tests (486 golden, 177 phase) |
| Parallel Testing | pytest-xdist (`-n auto --dist loadscope`) |

---

## MCP Architecture

CORTEX uses **Pylance-style MCP** — the server auto-starts when VS Code opens the workspace. No manual startup required.

**Configuration** (`.vscode/settings.json`):
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

## Development Standards

| Rule | Description |
|---|---|
| CORE-002 | All output inline — never create .md/.txt report files |
| CORE-008 | TDD mandatory — write failing test first, then implement |
| CORE-011 | Type hints on all functions |
| CORE-012 | Docstrings on all public APIs |
| CORE-028 | File naming: snake_case only |
| CORE-035 | Single canonical implementation — no duplicates |
| CORE-048 | Holistic validation gate before IMPLEMENT/FIX/REFACTOR |
| CORE-049 | Silent autonomous execution (progress bars only) |

---

## Workflow

1. **Write the test first** (CORE-008 — RED phase)
2. **Implement minimum code** to pass tests (GREEN phase)
3. **Refactor** with all tests passing (REFACTOR phase)
4. **EnforcementOrchestrator** validates CORE rules pre-commit
5. **Commit** with conventional commit message

---

## File Organization

```
cortex/              ← Python source (16 canonical dirs)
  orchestrators/     ← 52 orchestrators across 10 domains
  mcp/tools/         ← 23 MCP tools
  core/              ← OrchestratorBase, FileFactory, WorkflowEngine
  testing/           ← Test framework, parallel runner, quality gate
  intelligence/      ← LENS, domain brain, knowledge synthesis
  governance/        ← Rule enforcement, compliance
cortex-registry/     ← YAML governance rules, patterns, plans
tests/               ← All tests (mirrors cortex/ structure)
.cortex-runtime/     ← Runtime data (logs, traces, .db files)
.github/             ← CI/CD, prompts, agents, templates
cortex-docs/         ← User-facing documentation (HTML/CSS only)
```

---

## Key Entry Points

| Component | Location |
|---|---|
| MasterOrchestrator | `cortex/orchestrators/core/master_orchestrator.py` |
| IntentRouter | `cortex/orchestrators/core/intent_router.py` |
| TDDOrchestrator | `cortex/orchestrators/core/tdd_orchestrator.py` |
| EnforcementOrchestrator | `cortex/orchestrators/core/enforcement_orchestrator.py` |
| OrchestratorBase | `cortex/core/orchestrator_base.py` |
| MCP Server | `cortex/mcp/` |
| Refactor Plan | `cortex-registry/planning/cortex-refactor-master.yaml` |

---

## References

- Architecture: `cortex-docs/architecture-recommendation.md`
- MCP Setup: `.github/prompts/MCP-SETUP-GUIDE.md`
- Security: `cortex-docs/security.md`
- Architect Prompt: `.github/prompts/cortex-architect.prompt.md`
- Response Templates: `.github/templates/cortex-response-templates.md`
