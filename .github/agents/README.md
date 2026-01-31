# CORTEX Agents

**Version:** 2.0 | **Updated:** 2026-01-31 | **Architecture:** MCP-First SaaS

---

## 📁 Structure

```
agents/
├── core/                    # Production agents
│   ├── CORTEX.md           # Master orchestrator agent
│   ├── cortex-architect.md # Design-phase analysis agent
│   ├── cortex-mcp-gateway.md # MCP tool routing agent
│   └── cortex-docs-orchestrator.md # Internal docs HTML generator (not MCP-exposed)
└── archived/               # Obsolete agents (reference only)
    └── cortex-vacuum-agents.md
```

---

## 🎯 Active Agents

| Agent | File | Purpose | Mode |
|-------|------|---------|------|
| **CORTEX** | [CORTEX.md](core/CORTEX.md) | Master orchestrator, production entry point | Production |
| **Architect** | [cortex-architect.md](core/cortex-architect.md) | Design-phase analysis, aggressive challenge | Design |
| **MCP Gateway** | [cortex-mcp-gateway.md](core/cortex-mcp-gateway.md) | MCP tool routing, SaaS gateway | Production |

---

## 🌐 MCP-First Architecture

All agents route operations through MCP tools:

| Agent | Primary MCP Tools |
|-------|-------------------|
| CORTEX | `cortex_process_request`, `cortex_challenge` |
| Architect | `cortex_lens_analyze`, `cortex_detect_duplicates` |
| MCP Gateway | All tools via `/tools/{name}` |

---

## 🔗 Related Prompts

| Prompt | Agent | Purpose |
|--------|-------|---------|
| [CORTEX.prompt.md](../prompts/CORTEX.prompt.md) | CORTEX.md | Production master |
| [cortex-architect.prompt.md](../prompts/cortex-architect.prompt.md) | cortex-architect.md | Design analysis |

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
