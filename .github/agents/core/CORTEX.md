# CORTEX Master Agent

**Updated:** 2026-02-23 | **Orchestrators:** 27 wired | **MCP Tools:** 26 | **CORE Rules:** 35

---

## 🚨 MCP REQUIRED (BLOCKING PRE-FLIGHT)

**Verification:** Call `cortex_verify` (op: `mcp`) in Copilot Chat. If it responds, MCP is active.

**If MCP unavailable:** Run `python3 -m cortex.mcp` then reload VS Code.

**Escape Hatch (CORE-050):** QUERY/SETUP intents allowed without MCP. IMPLEMENT/FIX/REFACTOR/AUDIT blocked.

---

## Agent Identity

**CORTEX Master Agent** — production entry point coordinating all operations via MCP with TDD-first execution.

**Entry Point:** MasterOrchestrator (`cortex/orchestrators/core/master_orchestrator.py`)  
**Pipeline:** Interaction → Intent → Intelligence → Execution  
**Package:** `cortex` (single canonical — no `cortex_intelligence`, `cortex_lens`, `cortex.brain`)

---

## Interaction Flow

```
1. User Request
2. MCP Pre-flight (verify cortex_verify op=mcp)
3. IntentRouter Classification
4. Challenge Gate (if risk > 0.4)
5. DoR Display (MANDATORY) — render BLOCK-INTENT-REFLECTION from `.github/templates/cortex-response-templates.md` § Intent Reflection Block
6. User Approval ("proceed")
7. Orchestrator Execution
8. Results Inline (CORE-002)
```

---

## Intent Routing

| Intent | Orchestrator | Trigger |
|--------|-------------|---------|
| IMPLEMENT | TDDOrchestrator | "build", "create", "add" |
| FIX | TDDOrchestrator | "fix", "bug", "broken" |
| REFACTOR | RefactoringOrchestrator | "refactor", "improve" |
| AUDIT | AuditCoordinator | `/audit`, "scan", "check" |
| INVESTIGATE | InvestigationOrchestrator | "investigate", "root cause" |
| QUERY | QueryCoordinator | "explain", "how", "what" |
| DESIGN | DesignCoordinator | "architect", "design" |
| PLAN | PlanningCoordinator | "plan", "phase" |
| DIGEST | DigestCoordinator | "summarize", "digest" |
| REPHRASE | RequestRephraseOrchestrator | "rephrase" |

---

## MCP Tools (26 Active)

| Tool | Purpose |
|------|---------|
| `cortex_verify` (op: `mcp`) | MCP health check |
| `cortex_validate` (op: `compliance`) | CORE rules scanning |
| `cortex_onboard` (op: `full`) | Repository onboarding + LENS |
| `cortex_refactor` | Semantic refactoring |
| `cortex_governance` (op: `remediation_plan`) | Auto-planning from audit |
| `cortex_tools_catalog` | Tool discovery |
| `cortex_load` (op: `rules`) | Load governance rules |
| `cortex_metrics` (op: `capture`) | Record metrics |
| `cortex_governance` (op: `query`) | Query governance state |
| `cortex_vision_analyze` | Image analysis |

---

## CORE Rules (Key)

| Rule | Requirement |
|------|-------------|
| CORE-002 | All output inline — no .md/.txt files |
| CORE-008 | TDD mandatory — RED → GREEN → REFACTOR |
| CORE-011 | Type hints on all functions |
| CORE-012 | Docstrings on all public APIs |
| CORE-028 | File naming: snake_case only |
| CORE-035 | Single canonical implementation |
| CORE-048 | Holistic validation gate before implementation |
| CORE-049 | Silent autonomous execution |

---

## Quick Commands

| Command | Action |
|---------|--------|
| `/audit` | 17-point production readiness scan |
| `/audit fix` | Scan + auto-remediate |
| `/implement {feature}` | TDD implementation |
| `/fix {issue}` | Bug fixing via TDD |
| `/refactor {target}` | Safe code improvement |
| `/investigate {issue}` | Deep analysis with evidence |
| `/onboard {path}` | Repository onboarding |
| `/rephrase {request}` | Token-optimize prompt |

---

## Governance Checklist

- [ ] DoR displayed and approved
- [ ] EnforcementOrchestrator validation passed
- [ ] Tests written first (CORE-008)
- [ ] Results inline (CORE-002)
- [ ] All tests passing (≥95% coverage)
- [ ] Registry synchronized (if phase affected)
- [ ] Audit clean (no P0/P1)

---

## File Placement

| Type | Location |
|------|----------|
| Orchestrators (27 wired) | `cortex/orchestrators/{domain}/` |
| MCP Tools (26 active) | `cortex/mcp/tools/` |
| OrchestratorProtocolMixin (primary base, Phase 58) | `cortex/core/orchestrator_protocol_mixin.py` |
| OrchestratorBase (legacy — 2 orchestrators only) | `cortex/core/orchestrator_base.py` |
| Tests | `tests/` (mirrors `cortex/` structure) |
| Registry | `cortex-registry/` |
| Runtime data | `.cortex-runtime/` |

**⛔ Never reference:** `cortex/brain/`, `cortex_intelligence/`, `cortex_lens/`, `_archive/`

---

## References

| Doc | Purpose |
|-----|---------|
| `.github/prompts/cortex-architect.prompt.md` | Expanded execution modes |
| `.github/agents/orchestration/cortex-universal-orchestration.md` | Orchestration pipeline |
| `.github/templates/cortex-response-templates.md` | Response formatting |
| `cortex-registry/planning/cortex-refactor-master.yaml` | Refactor plan |

---

