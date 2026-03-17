---
name: cortex
description: 'CORTEX Framework capability guide. Use when: running /audit, /audit fix, /vacuum, /health, /healthcheck, /debug, /fix, /implement, /refactor, /review, /totalrecall, /rca, /distill, /digest, /onboard, /challenge, /sync, /feedback, /upgrade, /frontend, /typescript, /csharp, /decompose, /train, /meta-audit. Covers all CORTEX commands, orchestrators, MCP tools, TDD workflow, test execution, governance rules, and production certification. Invoke for any CORTEX operation, workflow routing, capability question, or to understand which command to use.'
argument-hint: 'Optional: name the command or intent (e.g. "audit", "debug", "implement", "rca")'
---

# CORTEX — Intent Classification Gateway

**Package:** `cortex` | **Orchestrators:** 302 across 10 domains | **MCP Tools:** 81 registered | **Tests:** ~20,043

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI Engineering Framework that orchestrates GitHub Copilot as the AI engine via a Pylance-style MCP stdio server.

This is the **gateway skill** — it classifies intent and routes to the appropriate domain skill.

---

## Intent Classification Gateway

| User wants to… | Domain Skill | Command |
|---|---|---|
| Implement a feature, fix a bug, or refactor | `cortex-tdd` | `/implement` `/fix` `/refactor` |
| Find and fix all issues across the codebase | `cortex-audit` | `/audit fix` `/health` |
| Verify/fix Claude-primary backbone readiness | `cortex-claude-readiness` | `/claude-ready audit` `/claude-ready fix` `/claude-ready certify` |
| Debug a failing test, error, or UI issue | `cortex-debug` | `/debug` `/debug-inject` `/debug-cleanup` |
| Analyse root causes of recurring failures | `cortex-debug` | `/rca` |
| Plan phases, certify, onboard, or ingest content | `cortex-plan` | `/plan` `/totalrecall` `/digest` `/onboard` |
| Understand governance rules or CORE enforcement | `cortex-audit` | `/audit` `/audit fix` |
| Review CORTEX architecture, Tutorial Mode, Claude backbone, or cross-cutting YAML wiring | `cortex-architecture-review` | `/architecture-review` |

### Overlap Disambiguation

| Situation | Use |
|---|---|
| Test is failing AND you don't know why | `/debug` → `cortex-debug` |
| Test is failing AND you know the cause | `/fix` → `cortex-tdd` |
| Code works but quality/structure is poor | `/refactor` → `cortex-tdd` |
| Code has known security issues | `/audit fix` → `cortex-audit` |
| Recurring failure with no obvious cause | `/rca` → `cortex-debug` |
| Codebase drift between docs and code | `/totalrecall` → `cortex-plan` |

---

## Quick Command Reference

| Command | What It Does |
|---|---|
| `/audit fix` | Full 9-stage production-readiness scan + auto-fix |
| `/audit` | Scan only, no auto-fix |
| `/claude-ready fix` | Claude-primary readiness scan + remediation + convergence |
| `/vacuum` | Markdown sprawl + root clutter + OS artifacts cleanup |
| `/health` | All 22 orchestrator health endpoints |
| `/healthcheck` | Full test suite (parallel) |
| `/implement {desc}` | TDD cycle: test first → implement → converge |
| `/fix {desc}` | TDD cycle: reproduce → root cause → sweep fix |
| `/refactor {desc}` | TDD cycle: baseline → refactor → scorecard |
| `/debug {path}` | Multi-stack: inject → capture → analyze → fix-plan → cleanup |
| `/rca {failure}` | Root cause analysis (4 methodologies) |
| `/totalrecall` | Production certification (10 phases) |
| `/digest {path}` | Intelligent content ingestion (3-pipeline) |
| `/distill {file}` | Chat transcript → executable prompt |
| `/onboard {repo}` | LENS analysis + SQLite dashboard |
| `/review {pr}` | PR code review: security + quality + verdict |
| `/architecture-review` | Deep architecture and explainability review with branch regression comparison |
| `/feedback` | Cross-repo capability extraction |
| `/sync target={path}` | One-way privacy-safe sync |
| `/challenge {request}` | Generate ≥2 alternatives with trade-offs |
| `/upgrade` | Check origin/main, merge if ahead, audit fix |

---

## Domain-Specific Workflows

| Intent | Workflow Template | Command |
|---|---|---|
| HTML/CSS views | `frontend/html-view-lifecycle.yaml` | `/frontend` |
| Docs HTML/CSS | `frontend/docs-html-design-workflow.yaml` | `/frontend docs` |
| TypeScript refactor | `frontend/typescript-refactor-workflow.yaml` | `/typescript` |
| C# refactor | `backend/csharp-refactor-workflow.yaml` | `/csharp refactor` |
| C# security | `backend/csharp-security-workflow.yaml` | `/csharp security` |
| Service decomposition | `lifecycle/service-decomposition-workflow.yaml` | `/decompose` |

---

## Architecture Essentials

| Component | Location |
|---|---|
| MasterOrchestrator | `cortex/orchestrators/core/master_orchestrator.py` |
| IntentRouter | `cortex/orchestrators/core/intent_router.py` |
| IntelligenceFacade | `cortex/intelligence/facade.py` |

**MCP:** Pylance-style stdio, auto-starts with VS Code. Setup: `python3 scripts/setup-mcp.py`

**Test runner:** Always use `make test-{mode}` — never raw `pytest`. Modes: `preflight` (< 10s), `changed` (TDD), `smoke` (< 60s), `unit`, `parallel`, `healthcheck`, `batch`.
