# Component Relationships Diagram

**Purpose:** Dependencies and interactions between CORTEX components  
**Audience:** Architects, Developers  
**Last Updated:** 2026-02-10

---

## Component Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         COMPONENT DEPENDENCY GRAPH                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│                              ┌─────────────────┐                                        │
│                              │   MCP Server    │                                        │
│                              │                 │                                        │
│                              │  Entry Point    │                                        │
│                              └────────┬────────┘                                        │
│                                       │                                                  │
│                    ┌──────────────────┼──────────────────┐                              │
│                    │                  │                  │                               │
│                    ▼                  ▼                  ▼                               │
│           ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                        │
│           │    Tool     │    │    Auth     │    │   Metrics   │                        │
│           │   Registry  │    │  Middleware │    │  Collector  │                        │
│           └──────┬──────┘    └─────────────┘    └─────────────┘                        │
│                  │                                                                       │
│                  │ depends on                                                            │
│                  ▼                                                                       │
│    ┌─────────────────────────────────────────────────────────────────────┐             │
│    │                        MasterOrchestrator                            │             │
│    │                                                                      │             │
│    │  • Central coordination                                              │             │
│    │  • Request routing                                                   │             │
│    │  • Result aggregation                                                │             │
│    └───────────────────────────────┬──────────────────────────────────────┘             │
│                                    │                                                     │
│         ┌──────────────────────────┼──────────────────────────┐                         │
│         │                          │                          │                          │
│         ▼                          ▼                          ▼                          │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐                 │
│  │  IntentRouter   │      │  LENS Engine    │      │  Enforcement    │                 │
│  │                 │      │                 │      │  Orchestrator   │                 │
│  │ • Classification│      │ • Context       │      │                 │                 │
│  │ • Mapping       │      │ • Synthesis     │      │ • 7 Agents      │                 │
│  └────────┬────────┘      └────────┬────────┘      │ • 50+ Rules     │                 │
│           │                        │               └────────┬────────┘                 │
│           │                        │                        │                           │
│           │               ┌────────┴────────┐               │                           │
│           │               │                 │               │                           │
│           │               ▼                 ▼               │                           │
│           │        ┌───────────┐     ┌───────────┐         │                           │
│           │        │   Git     │     │   AST     │         │                           │
│           │        │  Analyzer │     │  Analyzer │         │                           │
│           │        └───────────┘     └───────────┘         │                           │
│           │                                                  │                           │
│           ▼                                                  ▼                           │
│    ┌──────────────────────────────────────────────────────────────────┐                │
│    │                     Domain Orchestrators                          │                │
│    │                                                                   │                │
│    │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │                │
│    │  │    TDD     │  │ Refactoring│  │  Planning  │  │  Challenge │ │                │
│    │  │Orchestrator│  │Orchestrator│  │Orchestrator│  │   Engine   │ │                │
│    │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘ │                │
│    │        │               │               │               │        │                │
│    └────────┼───────────────┼───────────────┼───────────────┼────────┘                │
│             │               │               │               │                          │
│             └───────────────┴───────────────┴───────────────┘                          │
│                                     │                                                   │
│                                     ▼                                                   │
│    ┌──────────────────────────────────────────────────────────────────┐                │
│    │                        Data Layer                                 │                │
│    │                                                                   │                │
│    │  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │                │
│    │  │   Redis    │  │ PostgreSQL │  │    Git     │                 │                │
│    │  │   Cache    │  │  Metrics   │  │  Registry  │                 │                │
│    │  └────────────┘  └────────────┘  └────────────┘                 │                │
│    │                                                                   │                │
│    └──────────────────────────────────────────────────────────────────┘                │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Orchestrator Relationships

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR RELATIONSHIPS                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│                              ┌─────────────────────┐                                    │
│                              │  MasterOrchestrator │                                    │
│                              │      (Hub)          │                                    │
│                              └──────────┬──────────┘                                    │
│                                         │                                                │
│              ┌────────────┬─────────────┼─────────────┬────────────┐                   │
│              │            │             │             │            │                    │
│              ▼            ▼             ▼             ▼            ▼                    │
│     ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │
│     │  Intent    │ │   LENS     │ │Enforcement │ │   TDD      │ │ Domain     │        │
│     │  Router    │ │Orchestrator│ │Orchestrator│ │Orchestrator│ │Orchestrat- │        │
│     │            │ │            │ │            │ │            │ │   ors      │        │
│     └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘        │
│           │              │              │              │              │                │
│           │              │              │              │              │                │
│  ┌────────┴────────┐     │     ┌────────┴────────┐     │     ┌───────┴───────┐       │
│  │                 │     │     │                 │     │     │               │        │
│  ▼                 ▼     │     ▼                 ▼     │     ▼               ▼        │
│ ┌───┐           ┌───┐    │   ┌───┐           ┌───┐    │   ┌───┐         ┌───┐       │
│ │TDD│           │REF│    │   │GOV│           │SEC│    │   │PLN│         │DOC│       │
│ └───┘           └───┘    │   └───┘           └───┘    │   └───┘         └───┘       │
│  │               │       │    │               │       │    │             │           │
│  └───────────────┘       │    └───────────────┘       │    └─────────────┘           │
│          │               │            │               │           │                   │
│          │               │            │               │           │                   │
│          └───────────────┴────────────┴───────────────┴───────────┘                   │
│                                      │                                                 │
│                                      ▼                                                 │
│                          ┌─────────────────────┐                                      │
│                          │    Shared Services  │                                      │
│                          │                     │                                      │
│                          │  • Cache Manager    │                                      │
│                          │  • Audit Logger     │                                      │
│                          │  • Metrics Reporter │                                      │
│                          └─────────────────────┘                                      │
│                                                                                          │
│  Legend:                                                                                │
│  ───────                                                                                │
│  TDD = TDDOrchestrator          REF = RefactoringOrchestrator                          │
│  GOV = GovernanceAgent          SEC = SecurityAgent                                     │
│  PLN = PlanningOrchestrator     DOC = DocumentationOrchestrator                        │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## LENS Component Relationships

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        LENS COMPONENT RELATIONSHIPS                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│                              ┌─────────────────────┐                                    │
│                              │   LENSOrchestrator  │                                    │
│                              │                     │                                    │
│                              │  • Coordinates      │                                    │
│                              │  • Aggregates       │                                    │
│                              └──────────┬──────────┘                                    │
│                                         │                                                │
│                    ┌────────────────────┼────────────────────┐                          │
│                    │                    │                    │                           │
│                    ▼                    ▼                    ▼                           │
│           ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│           │  AnalyzerPool   │  │   Synthesizer   │  │   CacheManager  │                │
│           │                 │  │                 │  │                 │                │
│           │ Manages 8       │  │ Merges results  │  │ L1/L2/L3 cache  │                │
│           │ analyzers       │  │                 │  │                 │                │
│           └────────┬────────┘  └────────┬────────┘  └────────┬────────┘                │
│                    │                    │                    │                           │
│   ┌────────────────┼────────────────────┼────────────────────┘                          │
│   │                │                    │                                                │
│   │    ┌───────────┴───────────┐        │                                                │
│   │    │                       │        │                                                │
│   ▼    ▼                       ▼        ▼                                                │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────────┐                                    │
│ │  Git   │ │  AST   │ │Comment │ │  LENSResult    │                                    │
│ │Analyzer│ │Analyzer│ │Analyzer│ │                │                                    │
│ └───┬────┘ └───┬────┘ └───┬────┘ │ Unified output │                                    │
│     │          │          │      │ from synthesis │                                    │
│     │          │          │      └────────────────┘                                    │
│     │          │          │                                                             │
│     ▼          ▼          ▼                                                             │
│ ┌────────┐ ┌────────┐ ┌────────┐                                                       │
│ │Pattern │ │Vision  │ │Config  │                                                       │
│ │Analyzer│ │Analyzer│ │Analyzer│                                                       │
│ └───┬────┘ └───┬────┘ └───┬────┘                                                       │
│     │          │          │                                                             │
│     ▼          ▼          ▼                                                             │
│ ┌────────┐ ┌────────┐                                                                  │
│ │Database│ │  API   │                                                                  │
│ │Analyzer│ │Analyzer│                                                                  │
│ └────────┘ └────────┘                                                                  │
│                                                                                          │
│  Data Flow:                                                                             │
│  ──────────                                                                             │
│  Target File ──► Analyzers (parallel) ──► Raw Results ──► Synthesizer ──► LENSResult  │
│                       │                                        ▲                        │
│                       │                                        │                        │
│                       └──── Cache Check ──────────────────────┘                        │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Dependency Matrix

| Component | Depends On | Depended By |
|-----------|-----------|-------------|
| MCPServer | ToolRegistry, Auth, Metrics | Clients |
| ToolRegistry | Tools, Metadata | MCPServer |
| MasterOrchestrator | IntentRouter, LENS, Enforcement | MCPServer |
| IntentRouter | — | MasterOrchestrator |
| LENSOrchestrator | Analyzers, Synthesizer, Cache | MasterOrchestrator |
| EnforcementOrchestrator | Agents, Rules | MasterOrchestrator |
| TDDOrchestrator | LENS, Governance | MasterOrchestrator |
| Redis | — | CacheManager, Sessions |
| PostgreSQL | — | Metrics, AuditLog |
| GitRegistry | Git | Orchestrator configs |

---

## Communication Patterns

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                       COMMUNICATION PATTERNS                                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  1. Request/Response (Synchronous)                                                      │
│  ─────────────────────────────────                                                      │
│                                                                                          │
│  Client ───request───► Server ───response───► Client                                   │
│                                                                                          │
│  Used by: MCP Server, Tool invocations                                                  │
│                                                                                          │
│                                                                                          │
│  2. Publish/Subscribe (Async Events)                                                   │
│  ────────────────────────────────────                                                   │
│                                                                                          │
│  Publisher ───event───► Event Bus ───event───► Subscriber 1                            │
│                              │                                                          │
│                              └───event───► Subscriber 2                                 │
│                                                                                          │
│  Used by: Cache invalidation, Audit logging                                             │
│                                                                                          │
│                                                                                          │
│  3. Pipeline (Data Transformation)                                                      │
│  ─────────────────────────────────                                                      │
│                                                                                          │
│  Stage 1 ───data───► Stage 2 ───data───► Stage 3 ───data───► Output                   │
│                                                                                          │
│  Used by: LENS analyzers, Synthesis pipeline                                            │
│                                                                                          │
│                                                                                          │
│  4. Scatter/Gather (Parallel)                                                           │
│  ────────────────────────────                                                           │
│                                                                                          │
│              ┌───► Worker 1 ───┐                                                        │
│              │                 │                                                         │
│  Scatter ────┼───► Worker 2 ───┼───► Gather ───► Result                                │
│              │                 │                                                         │
│              └───► Worker 3 ───┘                                                        │
│                                                                                          │
│  Used by: LENS parallel analysis, Multiple orchestrator execution                       │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- [Architecture Overview](architecture-overview.md) — System architecture
- [Request Lifecycle](request-lifecycle.md) — Request flow
- [Data Flow](data-flow.md) — Data movement

---

*Part of CORTEX Architecture Documentation*
