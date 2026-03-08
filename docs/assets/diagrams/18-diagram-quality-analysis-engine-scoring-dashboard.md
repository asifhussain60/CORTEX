---
id: quality-analysis-engine-scoring-dashboard
title: Quality Analysis Engine — multi-dimensional scoring
purpose: Show how the Quality Analysis Engine aggregates five quality dimensions into a composite score with trend tracking and Code Review Orchestrator integration.
audience:
  - Quality Engineers
  - Software Developers
  - Business Leaders
source_of_truth:
  - cortex/orchestrators/domain/quality_analysis_engine.py
  - cortex/intelligence/quality/scoring.py
last_verified: 2026-03-04
diagram_type: Intelligence
render: ascii
---

# Quality Analysis Engine — Multi-Dimensional Scoring

## From Raw Metrics to Composite Quality Intelligence

```
 ═══════════════════════════════════════════════════════════════════════════════
  CORTEX QUALITY ANALYSIS ENGINE — 5-DIMENSION SCORING DASHBOARD
 ═══════════════════════════════════════════════════════════════════════════════

  Codebase Snapshot + Code Review Findings
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  DIMENSION ANALYZERS (independent, parallel)                         │
  │                                                                      │
  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
  │  │ 1. STRUCTURAL   │  │ 2. TEST         │  │ 3. DOCUMENTA-  │     │
  │  │    COMPLEXITY    │  │    COVERAGE     │  │    TION        │     │
  │  │                  │  │                  │  │                │     │
  │  │ Cyclomatic       │  │ Branch coverage  │  │ Docstring      │     │
  │  │ Coupling         │  │ Mutation score   │  │ coverage       │     │
  │  │ Cohesion         │  │ Edge-case gaps   │  │ API docs       │     │
  │  │ Depth            │  │ Integration %    │  │ README fresh   │     │
  │  │                  │  │                  │  │                │     │
  │  │   Score: 82/100  │  │   Score: 91/100  │  │   Score: 78/100│     │
  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
  │                                                                      │
  │  ┌─────────────────┐  ┌─────────────────┐                          │
  │  │ 4. DEPENDENCY   │  │ 5. GOVERNANCE   │                          │
  │  │    HEALTH       │  │    COMPLIANCE   │                          │
  │  │                  │  │                  │                          │
  │  │ Outdated deps    │  │ CORE rule pass  │                          │
  │  │ Known CVEs       │  │ Naming conven.  │                          │
  │  │ Circular deps    │  │ Type hints      │                          │
  │  │ License risk     │  │ Error handling  │                          │
  │  │                  │  │                  │                          │
  │  │   Score: 85/100  │  │   Score: 94/100  │                          │
  │  └─────────────────┘  └─────────────────┘                          │
  └──────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  COMPOSITE QUALITY SCORE                                             │
  │                                                                      │
  │            ┌─────────────────────────────────┐                       │
  │            │       OVERALL: 87 / 100          │                       │
  │            │                                   │                       │
  │            │   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░          │                       │
  │            │                                   │                       │
  │            │   Weighted average of 5 dims      │                       │
  │            └─────────────────────────────────┘                       │
  │                                                                      │
  │  Dimension Breakdown:                                                │
  │  Structural    ▓▓▓▓▓▓▓▓░░  82   ▲ +3 vs last week                  │
  │  Test Coverage ▓▓▓▓▓▓▓▓▓░  91   ── stable                          │
  │  Documentation ▓▓▓▓▓▓▓░░░  78   ▼ -2 (new APIs undocumented)       │
  │  Dependencies  ▓▓▓▓▓▓▓▓░░  85   ▲ +1 (CVE patched)                │
  │  Governance    ▓▓▓▓▓▓▓▓▓░  94   ▲ +2 (new rules adopted)          │
  └──────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  TREND TRACKING & ALERTING                                           │
  │                                                                      │
  │  Week 1 ──── Week 2 ──── Week 3 ──── Week 4 ──── Week 5             │
  │    82          84          85          86          87                 │
  │     ╲          ╱╲          ╱╲          ╱╲          ╱                  │
  │      ╲────────╱  ╲────────╱  ╲────────╱  ╲────────╱                  │
  │                                                                      │
  │  Alerts:                                                             │
  │  ⚠ Documentation below 80 threshold → notify team lead              │
  │  ✅ Governance compliance above 90 → positive signal emitted         │
  └──────────────────────────────────────────────────────────────────────┘
```

## Integration Points

```
  Quality Analysis Engine
         │
         ├── Code Review Orchestrator (per-review scoring)
         ├── URS Learning Loop (quality trend → reinforcement signals)
         ├── Governance Engine (compliance dimension data)
         ├── Health Orchestrator (quality as health metric)
         └── cortex_review MCP tool (inline quality badge)
```
