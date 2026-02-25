# Extensibility

---
title: CORTEX Extensibility — Adding New Capabilities
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-25
source_of_truth: cortex/mcp/tools/ + cortex/orchestrators/domain/ + cortex-registry/patterns/
order: 8
---

> **Brain analogy:** Extensibility is **neuroplasticity** — the brain's ability to form new neural connections throughout life. CORTEX is designed to grow new capabilities without surgery on the core.

---

## Extension Points

| Extension | Where to Add | Discovery |
|-----------|-------------|-----------|
| **MCP Tools** | `cortex/mcp/tools/` | Auto-discovered by MCP server |
| **Domain Orchestrators** | `cortex/orchestrators/domain/` | Registered in wiring contract |
| **Workflow Templates** | `cortex-registry/workflows/templates/` | Read by WorkflowEngine |
| **Enterprise Patterns** | `cortex-registry/patterns/` | Used by Perception tier |
| **Knowledge Base** | `cortex-registry/knowledge-base/` | Used by intelligence layer |
| **Infrastructure Catalog** | `cortex-registry/company/` | Platform, API, application definitions |
| **Governance Rules** | `cortex-registry/core/tier0-skull/` | Enforced by EnforcementOrchestrator |

All extensions are **hot-reload** — no core code changes required.

---

## Adding a New MCP Tool

1. Create `cortex/mcp/tools/your_tool.py`
2. Implement the tool function with MCP decorator
3. Add type hints (CORE-011) and docstring (CORE-012)
4. Write a test first (CORE-008)
5. The MCP server discovers it automatically on next startup

---

## Adding a Domain Orchestrator

1. Create `cortex/orchestrators/domain/your_domain/your_orchestrator.py`
2. Inherit from `OrchestratorProtocolMixin` (primary base, Phase 58) — or `IOrchestrator` directly
3. Implement `execute_operation()` — cross-cutting hooks (LENS, KnSynth, GovGate) fire automatically via `_activate_cross_cutting_hooks()`
4. Register in the wiring contract
5. Write tests first (CORE-008)

---

## Adding Enterprise Patterns

1. Create a YAML file in `cortex-registry/patterns/`
2. Define pattern signatures, success rates, and associated strategies
3. Perception tier picks them up automatically

Current patterns: mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, command.

---

## Practical Examples

**Business Leader:** "When we enter the healthcare vertical, we add a HealthcareOrchestrator and healthcare patterns to the registry. No core platform changes. The system adapts."

**Product Owner:** "Adding a new MCP tool is a single file with a test. It's discovered automatically. No PRs to the core, no deployment coordination."

**Developer:** "I created a custom refactoring tool in `cortex/mcp/tools/`. Wrote the test first (CORE-008), implemented the tool, and it appeared in `cortex_tools_catalog` on the next MCP restart. Total: 45 minutes."

---

*Verified against extension point registry · 25 February 2026*
