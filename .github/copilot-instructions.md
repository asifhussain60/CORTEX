# CORTEX Copilot Instructions
**Version:** 6.0 | **Updated:** 2026-01-31 | **Authority:** MCP-First SaaS Architecture

---

## 🎯 System Identity

**CORTEX** — **CO**gnitive **R**eal-**T**ime **EX**ecution System

**Primary Prompt:** [CORTEX.prompt.md](.github/prompts/CORTEX.prompt.md)  
**Production Mode:** MCP Server (SaaS)  
**Orchestrators:** 23 wired via GitBackedRegistry

---

## ⚠️ TIER 0 RULES (IMMUTABLE)

| Rule | Enforcement |
|------|-------------|
| **CORE-002** | NO markdown file generation (inline chat only) |
| **CORE-029** | Response header MANDATORY |
| **CORE-030** | Implementation Truth — verify code, not docs |
| **CORE-035** | Single canonical implementation |
| **MCP-FIRST** | ALL functionality exposed via MCP tools |

---

## 🏗️ Response Header (MANDATORY)

**EVERY response MUST begin with:**

```markdown
## 🧠 CORTEX {operation}
**Author:** Asif Hussain | **Orchestrator:** {orchestrator} ✅

---
```

---

## 🔄 Interaction Protocol

**See [CORTEX.prompt.md](.github/prompts/CORTEX.prompt.md) for full protocol.**

### Quick Reference:

1. **LENS Classification** — Parse intent via Language→Examination→Navigation→Synthesis
2. **DoR Display** — Show intent classification table (MANDATORY before execution)
3. **Await Approval** — "proceed" / "yes" / "approve"
4. **Execute via MCP** — All operations through MCP tools
5. **Report Inline** — No file generation, inline chat only

---

## 🌐 MCP-FIRST ARCHITECTURE

**CORTEX = SaaS behind MCP server.** All operations through MCP tools.

### Core MCP Tools

| Tool | Purpose |
|------|---------|
| `cortex_process_request` | Main request processing |
| `cortex_challenge` | Challenge generation |
| `cortex_total_recall` | Feature discovery |
| `cortex_lens_analyze` | Unified code intelligence |
| `cortex_git_history` | 24h git context |
| `cortex_ast_analyze` | AST analysis |
| `cortex_detect_duplicates` | CORE-035 detection |
| `cortex_tools_catalog` | Tool discovery |

### MCP Endpoints

```yaml
/tools          # Tool discovery
/tools/{name}   # Tool execution
/health         # Health check
/metrics        # Prometheus metrics
```

---

## 🛡️ Governance (4-Layer Defense)

```
Layer 1: Pre-Execution Gate     → BLOCKS violations
Layer 2: Runtime Monitor        → STOPS at 3+ violations
Layer 3: Post-Execution Audit   → DETECTS bypasses
Layer 4: Production Gate        → PREVENTS broken deployment
```

### Key CORE Rules

| Rule | Requirement |
|------|-------------|
| CORE-008 | Tests BEFORE code (TDD) |
| CORE-011 | Type hints mandatory |
| CORE-012 | Google-style docstrings |
| CORE-013 | No bare except |
| CORE-026 | Git checkpoint before major changes |
| CORE-027 | Audit trail (AC_START → AC_COMPLETE) |

---

## 📁 File Placement (SSOT)

| Content | Location |
|---------|----------|
| Python Code | `cortex/`, `cortex_brain/` |
| Tests | `tests/` |
| Documentation | `docs/` |
| Wiring | `cortex/wiring/specifications/wiring.yaml` |

### Forbidden

- ❌ `.md` files outside `docs/`
- ❌ `.py` files in root
- ❌ Direct Python imports in production (use MCP)

---

## 🎼 Orchestrator Registry

**Source:** `GitBackedRegistry` from `cortex.wiring` → `wiring.yaml`

### Intent → Orchestrator → MCP Tool

| Intent | Orchestrator | MCP Tool |
|--------|--------------|----------|
| IMPLEMENT | TDDOrchestrator | `cortex_process_request` |
| FIX | IntentRouter | `cortex_process_request` |
| REFACTOR | RefactoringOrchestrator | `cortex_process_request` |
| ANALYZE | MasterOrchestrator | `cortex_lens_analyze` |
| TEST | TDDOrchestrator | `cortex_process_request` |

### Orchestrators (23 Total)

```
Core (6):     MasterOrchestrator, InteractionOrchestrator, IntentRouter,
              TDDOrchestrator, WorkflowOrchestrator, EnforcementOrchestrator

Domain (6):   RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator,
              ConversationOrchestrator, DocumentationOrchestrator, ChallengeEngine

Support (11): OnboardingOrchestrator, ToolDiscoveryOrchestrator, LENSOrchestrator, ...
```

---

## 🚀 Quick Commands

| Command | Action |
|---------|--------|
| `/implement {feature}` | TDD implementation |
| `/fix {issue}` | Bug fixing |
| `/refactor {target}` | Code improvement |
| `/analyze {scope}` | LENS analysis |
| `/recall {feature}` | Feature discovery |

---

## 🔗 Prompts & Agents

| File | Purpose |
|------|---------|
| [CORTEX.prompt.md](.github/prompts/CORTEX.prompt.md) | Production master prompt |
| [cortex-architect.prompt.md](.github/prompts/cortex-architect.prompt.md) | Design-phase prompt |
| [CORTEX.md](.github/agents/core/CORTEX.md) | Master agent |
| [cortex-architect.md](.github/agents/core/cortex-architect.md) | Design agent |
| [cortex-mcp-gateway.md](.github/agents/core/cortex-mcp-gateway.md) | MCP gateway agent |

---

## 📊 Observability

### Health Endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/wiring
curl http://localhost:8000/health/orchestrators
```

### Prometheus Metrics

- `cortex_orchestrator_count` — Orchestrators registered
- `cortex_tool_invocations_total` — Tool invocations
- `cortex_request_duration_seconds` — Latency histogram

---

## ✅ Before Every Operation

- [ ] Response header present
- [ ] DoR displayed and approved
- [ ] MCP tool invoked (not direct import)
- [ ] CORE rules applied
- [ ] Results inline (no file generation)

---

*Production instructions — MCP-first, SaaS-ready. See CORTEX.prompt.md for full protocol.*
