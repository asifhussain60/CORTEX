# CORTEX Agents

**Version:** 3.0 | **Updated:** 2026-02-03 | **Architecture:** MCP-First SaaS

---

## 📁 Structure

```
agents/
├── core/                           # Production agents
│   ├── CORTEX.md                  # Master orchestrator agent
│   ├── cortex-architect.md        # Mode router + environment validator
│   ├── cortex-environment-setup.md # Environment validation agent (NEW)
│   ├── cortex-auditor.md          # Codebase health auditor
│   ├── cortex-designer.md         # TDD + challenge specialist
│   └── cortex-mcp-gateway.md      # MCP tool routing agent
├── education/                      # Educational agents
│   ├── cortex-ask-coordinator.md
│   └── truth-verifier.md
└── archived/                       # Obsolete agents (reference only)
    └── cortex-vacuum-agents.md
```

---

## 🎯 Active Agents

| Agent | File | Purpose | Mode |
|-------|------|---------|------|
| **CORTEX** | [CORTEX.md](core/CORTEX.md) | Master orchestrator, production entry point | Production |
| **Architect** | [cortex-architect.md](core/cortex-architect.md) | Mode router + pre-flight environment check | Routing |
| **Environment Setup** | [cortex-environment-setup.md](core/cortex-environment-setup.md) | Python environment validation | Pre-Flight |
| **Auditor** | [cortex-auditor.md](core/cortex-auditor.md) | Autonomous codebase health scan | Audit |
| **Designer** | [cortex-designer.md](core/cortex-designer.md) | TDD + mandatory challenge | Design |
| **MCP Gateway** | [cortex-mcp-gateway.md](core/cortex-mcp-gateway.md) | MCP tool routing, SaaS gateway | Production |

---

## 🌐 MCP-First Architecture

All agents route operations through MCP tools:

| Agent | Primary MCP Tools |
|-------|-------------------|
| CORTEX | `cortex_process_request`, `cortex_challenge` |
| Architect | `cortex_verify_environment` (routing only) |
| Environment Setup | `cortex_verify_environment` |
| Auditor | `cortex_lens_analyze`, `cortex_detect_duplicates` |
| Designer | `cortex_git_history`, `cortex_manage_todo`, `cortex_ast_analyze` |
| MCP Gateway | All tools via `/tools/{name}` |

---

## 🔄 Request Flow

```
User Request
     ↓
CORTEX.md (master)
     ↓
cortex-architect.md (router)
     ↓
PRE-FLIGHT CHECK (cortex_verify_environment)
     ↓
✅ READY → cortex-auditor.md OR cortex-designer.md
❌ NOT READY → cortex-environment-setup.md (HALT)
```

---

## 🔗 Related Prompts

| Prompt | Agent | Purpose |
|--------|-------|---------|
| [CORTEX.prompt.md](../prompts/CORTEX.prompt.md) | CORTEX.md | Production master |
| [cortex-architect.prompt.md](../prompts/cortex-architect.prompt.md) | cortex-architect.md + environment-setup.md | Tri-mode routing + environment validation |

---

*v3.0 — Environment validation agent for pre-flight checks.*

---

## 📊 Orchestrator Integration

Agents coordinate 23 orchestrators via GitBackedRegistry:

```
Core (6):     MasterOrchestrator, InteractionOrchestrator, IntentRouter,
              TDDOrchestrator, WorkflowOrchestrator, EnforcementOrchestrator

Domain (6):   RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator,
              ConversationOrchestrator, DocumentationOrchestrator, ChallengeEngine

Support (11): OnboardingOrchestrator, ToolDiscoveryOrchestrator, LENSOrchestrator,
              UpgradeOrchestrator, RollbackOrchestrator, SetupOrchestrator, ...
```

---

## 🗄️ Archived Agents

Located in `/archived/` — kept for historical reference only.

| Agent | Reason Archived |
|-------|-----------------|
| cortex-vacuum-agents.md | Cleanup complete, no longer needed |

**Note:** Deprecated agents (`cortex-review.md`, `cortex-builder.md`, etc.) were deleted in Phase 8.3 consolidation.

---

*MCP-first agents — production-ready, SaaS architecture.*
