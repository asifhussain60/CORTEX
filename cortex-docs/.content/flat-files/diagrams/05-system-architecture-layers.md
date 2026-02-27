# System Architecture — Layer View
# Shows the six-layer architecture stack from IDE clients to registry

```
                              ┌─────────────────────────────────┐
                              │         IDE CLIENTS             │
                              │  VS Code · Cursor · Claude      │
                              └──────────────┬──────────────────┘
                                             │
                                   JSON-RPC 2.0 (stdio)
                                             │
                              ┌──────────────┴──────────────────┐
                              │         MCP GATEWAY             │
                              │   cortex/mcp/ — 39 tools        │
                              │   cortex_request_lifecycle      │
                              └──────────────┬──────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            ORCHESTRATION   │  LAYER                                     │
│                                            │                                            │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                         MasterOrchestrator (4-stage)                               │  │
│  │   Interaction → Intent Classification → Intelligence Prefetch → Execution          │  │
│  └──────────┬─────────────────┬────────────────────┬──────────────────┬───────────────┘  │
│             │                 │                    │                  │                   │
│  ┌──────────┴──┐   ┌─────────┴──┐   ┌────────────┴──┐   ┌──────────┴────────┐          │
│  │IntentRouter │   │ TDD Orch.  │   │ Enforcement   │   │ Domain Orch. (7)  │          │
│  │(12 intents) │   │ RED→GRN→RF │   │ (10 agents)   │   │ Refactor/Plan/... │          │
│  └─────────────┘   └────────────┘   └───────────────┘   └───────────────────┘          │
│                                                                                         │
│  51 wired orchestrators:  17 core  ·  7 domain  ·  23 support  ·  4 git                 │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            INTELLIGENCE    │  LAYER                                     │
│                                            │                                            │
│     ┌─────────────────┐  ┌────────────────┐│ ┌─────────────────┐  ┌─────────────────┐   │
│     │      LENS       │  │  Brain Tiers   ││ │  Knowledge Base │  │  Domain Brain   │   │
│     │  10 analyzers   │  │  Perception    ││ │  cortex/        │  │  cortex/intel/  │   │
│     │  300–800ms      │  │  Reasoning     ││ │  knowledge/     │  │  domain_brain/  │   │
│     │  cortex/lens/   │  │  Action        ││ │                 │  │                 │   │
│     └─────────────────┘  └────────────────┘│ └─────────────────┘  └─────────────────┘   │
│                                            │                                            │
│  cortex/intelligence/ + cortex/lens/ + cortex/knowledge/                                │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            GOVERNANCE      │  LAYER                                     │
│                                            │                                            │
│  ┌───────────────┐  ┌─────────────────┐  ┌─┴──────────────┐  ┌──────────────────────┐   │
│  │ 38 CORE Rules │  │  10 Enforcement │  │   CortexAudit  │  │  SweepCatalogue     │   │
│  │ skull-rules   │  │  Agents         │  │   DB (SQLite)  │  │  CORE-064           │   │
│  │ .yaml         │  │                 │  │   WAL mode     │  │                     │   │
│  └───────────────┘  └─────────────────┘  └────────────────┘  └──────────────────────┘   │
│                                                                                         │
│  cortex/governance/ + cortex-registry/core/tier0-skull/                                 │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            INFRASTRUCTURE  │  LAYER                                     │
│                                            │                                            │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌─────┴───┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │OpenTel. │ │Promeths │ │ Cache  │ │Circuit  │ │ Secret   │ │ Config   │ │ Event   │ │
│  │Tracing  │ │Metrics  │ │Manager │ │Breaker  │ │Redaction │ │Provider  │ │Bus      │ │
│  └─────────┘ └─────────┘ └────────┘ └─────────┘ └──────────┘ └──────────┘ └─────────┘ │
│                                                                                         │
│  cortex/infrastructure/ (50+ modules)                                                   │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            REGISTRY        │  (Configuration as Code)                   │
│                                            │                                            │
│  cortex-registry/                          │                                            │
│  ├── core/tier0-skull/    skull-rules.yaml │(38 CORE rules in YAML)                     │
│  ├── patterns/            9 enterprise patterns (mediator, strategy, observer…)          │
│  ├── workflows/templates/ Lifecycle + production + audit templates                       │
│  ├── planning/            Master plan index + dedicated files                            │
│  └── knowledge-base/      Domain knowledge (security, architecture, testing…)            │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```
