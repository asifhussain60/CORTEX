---
id: architecture-system-architecture-layers
title: System architecture — layer view
purpose: Summarise CORTEX end-to-end architecture from IDE clients down to the registry.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/
  - cortex-registry/
last_verified: 2026-03-02
diagram_type: Architecture
render: ascii
---

# System Architecture — Layer View

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
                              │   cortex/mcp/ — tool registry   │
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
│  │IntentRouter │   │ TDD Orch.  │   │ Enforcement   │   │ Domain Orch. (n)  │          │
│  │(intent map) │   │ RED→GRN→RF │   │ (agents)      │   │ Refactor/Plan/... │          │
│  └─────────────┘   └────────────┘   └───────────────┘   └───────────────────┘          │
│                                                                                         │
│  Wired orchestrators: 258 files · core · domain · support · health · git · intelligence · persona · validation · workflow │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            INTELLIGENCE    │  LAYER                                     │
│                                            │                                            │
│     ┌─────────────────┐  ┌────────────────┐│ ┌─────────────────┐  ┌─────────────────┐   │
│     │      LENS       │  │  Brain Tiers   ││ │  Knowledge Base │  │ IntelligenceFacade│ │
│     │  analyzers      │  │  (P→R→A)       ││ │  cortex/        │  │  cortex/intel/  │   │
│     │  cortex/lens/   │  │                ││ │  knowledge/     │  │  facade.py      │   │
│     └─────────────────┘  └────────────────┘│ └─────────────────┘  └─────────────────┘   │
│                                            │                                            │
│  cortex/intelligence/ + cortex/lens/ + cortex/knowledge/ — canonical entry: IntelligenceFacade (cortex/intelligence/facade.py) │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            GOVERNANCE      │  LAYER                                     │
│                                            │                                            │
│  ┌───────────────┐  ┌─────────────────┐  ┌─┴──────────────┐  ┌──────────────────────┐   │
│  │ CORE Rules    │  │  Enforcement     │  │   Audit Logs   │  │  Sweep Catalogue     │   │
│  │ YAML          │  │  agents          │  │   (SQLite)     │  │  CORE-064            │   │
│  └───────────────┘  └─────────────────┘  └────────────────┘  └──────────────────────┘   │
│                                                                                         │
│  cortex/governance/ + cortex-registry/core/                                             │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            INFRASTRUCTURE  │  LAYER                                     │
│                                            │                                            │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │Tracing  │ │Metrics  │ │ Cache  │ │Resilience│ │ Security │ │ Config   │ │ Event   │ │
│  └─────────┘ └─────────┘ └────────┘ └─────────┘ └──────────┘ └──────────┘ └─────────┘ │
│                                                                                         │
│  cortex/infrastructure/                                                                 │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            REGISTRY        │  (Configuration as Code)                   │
│                                            │                                            │
│  cortex-registry/                          │                                            │
│  ├── core/             ← governance rules (YAML)                                         │
│  ├── patterns/         ← reusable design patterns                                       │
│  ├── workflows/        ← workflow templates                                             │
│  ├── planning/         ← master plan + phase files                                      │
│  └── knowledge-base/   ← domain knowledge                                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```
