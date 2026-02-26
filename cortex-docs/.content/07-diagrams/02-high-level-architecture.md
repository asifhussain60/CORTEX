# High-Level Architecture

---
title: High-Level Architecture Diagram
type: diagram
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-25
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
│              cortex/mcp/ — 39 active tools                      │
│                              │                                  │
│         cortex_request_lifecycle (primary entry point)          │
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
│    51 wired orchestrators: 17 core · 7 domain · 23 support · 4 git       │
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
│    │ 35 Active    │    │Enforcement │    │   Audit DB    │      │
│    │ CORE Rules   │    │ Agents     │    │  (SQLite WAL) │      │
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
│    ├── core/tier0-skull/ ← skull-rules.yaml (CORE rules, YAML) │
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
| MCP Gateway | **39 active tools** (39 active) | `cortex/mcp/tools/` |
| Orchestration | **51 wired** orchestrators (17 core, 7 domain, 23 support, 4 git) | `cortex/orchestrators/` |
| Intelligence | 8 LENS analyzers + brain tiers | `cortex/lens/` + `cortex/intelligence/` |
| Governance | **38 CORE rules** | `cortex/governance/` + `cortex-registry/core/` |
| Infrastructure | 50+ modules | `cortex/infrastructure/` |
| Registry | Rules, patterns, workflows | `cortex-registry/` |
| Tests | **15,739** collected | `tests/` |

---

*Verified against live directory structure · 25 February 2026*
