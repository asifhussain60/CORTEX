# CORTEX Agents

**Version:** 4.0 | **Updated:** 2026-02-03 | **Architecture:** MCP-First SaaS

---

## 📁 Structure

```
agents/
├── core/                           # Production agents
│   ├── CORTEX.md                  # Master orchestrator agent
│   ├── cortex-architect.md        # Mode router + environment validator
│   ├── cortex-environment-setup.md # Environment validation agent
│   ├── cortex-auditor.md          # Codebase health auditor
│   ├── cortex-designer.md         # DESIGN mode: challenge + approval
│   ├── cortex-executor.md         # EXEC mode: direct implementation (NEW)
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
| **CORTEX** | `core/CORTEX.md` (load explicitly when needed) | Master orchestrator, production entry point | Production |
| **Architect** | `core/cortex-architect.md` (load explicitly when needed) | Mode router + pre-flight environment check | Routing |
| **Environment Setup** | `core/cortex-environment-setup.md` (load explicitly when needed) | Python environment validation | Pre-Flight |
| **Auditor** | `core/cortex-auditor.md` (load explicitly when needed) | Autonomous codebase health scan | Audit |
| **Designer** | `core/cortex-designer.md` (load explicitly when needed) | Challenge + approval for exploratory requests | Design |
| **Executor** | `core/cortex-executor.md` (load explicitly when needed) | Direct implementation (no challenge) | **Exec (NEW)** |
| **MCP Gateway** | `core/cortex-mcp-gateway.md` (load explicitly when needed) | MCP tool routing, SaaS gateway | Production |

---

## ⚡ EXEC vs DESIGN Mode

| Trigger | Mode | Agent | Challenge? |
|---------|------|-------|------------|
| `/implement {feature}` | EXEC | cortex-executor | ❌ No |
| `/fix {issue}` | EXEC | cortex-executor | ❌ No |
| `/exec {task}` | EXEC | cortex-executor | ❌ No |
| `/refactor {target}` | EXEC | cortex-executor | ❌ No |
| `/design {question}` | DESIGN | cortex-designer | ✅ Yes |
| Vague/exploratory | DESIGN | cortex-designer | ✅ Yes |

**Key Insight:** Challenge adds value for exploratory requests but creates friction for clear tasks.

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
| Executor | `cortex_git_history`, `cortex_manage_todo` (no challenge) |
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
| `../prompts/CORTEX.prompt.md` (load explicitly when needed) | CORTEX.md | Production master |
| `../prompts/cortex-architect.prompt.md` (load explicitly when needed) | cortex-architect.md + environment-setup.md | Tri-mode routing + environment validation |

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
