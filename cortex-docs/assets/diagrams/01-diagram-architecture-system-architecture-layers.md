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
last_verified: 2026-03-01
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
│  Wired orchestrators: core · domain · support · git                                     │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│                            INTELLIGENCE    │  LAYER                                     │
│                                            │                                            │
│     ┌─────────────────┐  ┌────────────────┐│ ┌─────────────────┐  ┌─────────────────┐   │
│     │      LENS       │  │  Brain Tiers   ││ │  Knowledge Base │  │  Domain Brain   │   │
│     │  analyzers      │  │  (P→R→A)       ││ │  cortex/        │  │  cortex/intel/  │   │
│     │  cortex/lens/   │  │                ││ │  knowledge/     │  │  domain_brain/  │   │
│     └─────────────────┘  └────────────────┘│ └─────────────────┘  └─────────────────┘   │
│                                            │                                            │
│  cortex/intelligence/ + cortex/lens/ + cortex/knowledge/                                │
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
