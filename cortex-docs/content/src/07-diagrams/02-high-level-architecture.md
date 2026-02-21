# High-Level Architecture

---
title: High-Level Architecture Diagram
type: diagram
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-20
source_of_truth: cortex/ directory structure
order: 2
---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        IDE CLIENTS                              │
│         VS Code          Cursor        Claude Desktop           │
└──────────────┬──────────────┬──────────────┬────────────────────┘
               │              │              │
               └──────────────┼──────────────┘
                              │
                    JSON-RPC 2.0 (stdio)
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                    MCP GATEWAY                                  │
│              cortex/mcp/ — 23 tools                             │
│                              │                                  │
│         cortex_process_request (mandatory entry)                │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   ORCHESTRATION LAYER                           │
│                              │                                  │
│    ┌─────────────────────────┼─────────────────────────┐        │
│    │           MasterOrchestrator                      │        │
│    │    (4-stage: Interaction → Intent →                │        │
│    │     Intelligence → Execution)                     │        │
│    └─────────────┬───────────┼───────────┬─────────────┘        │
│                  │           │           │                       │
│    ┌─────────────┴──┐  ┌────┴────┐  ┌───┴──────────┐           │
│    │ IntentRouter   │  │   TDD   │  │   Domain     │           │
│    │ (12 intents)   │  │ Orch.   │  │ Orchestrators│           │
│    └────────────────┘  └─────────┘  └──────────────┘           │
│                                                                 │
│    52 orchestrators across 10 domains                           │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   INTELLIGENCE LAYER                            │
│                              │                                  │
│    ┌──────────────┐    ┌─────┴──────┐    ┌───────────────┐      │
│    │    LENS      │    │   Brain    │    │  Knowledge    │      │
│    │ 8 analyzers  │    │  Tiers    │    │  Base         │      │
│    │ 300-800ms    │    │ P→R→A     │    │              │      │
│    └──────────────┘    └───────────┘    └───────────────┘      │
│                                                                 │
│    cortex/intelligence/ + cortex/lens/ + cortex/knowledge/      │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   GOVERNANCE LAYER                              │
│                              │                                  │
│    ┌──────────────┐    ┌─────┴──────┐    ┌───────────────┐      │
│    │ 17 Active    │    │ 8 Enforce- │    │   Audit DB    │      │
│    │ CORE Rules   │    │ ment Agents│    │  (SQLite WAL) │      │
│    └──────────────┘    └───────────┘    └───────────────┘      │
│                                                                 │
│    cortex/governance/ + cortex-registry/core/                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                          │
│                              │                                  │
│    ┌─────────┐  ┌────────┐  ┌──────┐  ┌──────────┐  ┌───────┐  │
│    │ Tracing │  │Metrics │  │Cache │  │Resilience│  │Security│ │
│    │OTel    │  │Prom.  │  │Mgr  │  │CircuitBr.│  │Redact. │ │
│    └─────────┘  └────────┘  └──────┘  └──────────┘  └───────┘  │
│                                                                 │
│    cortex/infrastructure/ (50+ modules)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   REGISTRY (Configuration)                      │
│                              │                                  │
│    cortex-registry/                                             │
│    ├── core/governance/   ← CORE rules (YAML)                  │
│    ├── patterns/          ← 9 enterprise patterns               │
│    ├── workflows/         ← Lifecycle + production templates    │
│    ├── planning/          ← Refactor master plan                │
│    └── knowledge-base/    ← Domain knowledge                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Counts

| Layer | Components | Location |
|-------|------------|----------|
| MCP Gateway | 23 tools | `cortex/mcp/tools/` |
| Orchestration | 52 orchestrators, 10 domains | `cortex/orchestrators/` |
| Intelligence | 8 LENS analyzers + brain tiers | `cortex/lens/` + `cortex/intelligence/` |
| Governance | 17 rules, 8 agents | `cortex/governance/` + `cortex-registry/core/` |
| Infrastructure | 50+ modules | `cortex/infrastructure/` |
| Registry | Rules, patterns, workflows | `cortex-registry/` |
| Tests | 15,333 collected | `tests/` |

---

*Verified against live directory structure · 20 February 2026*
