# RGR Quality Cycle Diagram

---
title: Red-Green-Refactor — Two-Level Quality Cycle
type: diagram
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/core/tdd_orchestrator.py
order: 14
---

> The two-level RGR cycle: unit-level per feature + sweep-level across the codebase.

## Two-Level RGR Architecture

```
  ┌─────────────────────────────────────────────────────────────┐
  │  LEVEL 1 — Unit RGR (per feature, TDDOrchestrator)         │
  │                                                             │
  │         ┌─────┐                                             │
  │    ┌───▶│ RED │ Write failing test (CORE-008)               │
  │    │    └──┬──┘                                             │
  │    │       ▼                                                │
  │    │    ┌───────┐                                           │
  │    │    │ GREEN │ Implement minimum to pass                 │
  │    │    └──┬────┘                                           │
  │    │       ▼                                                │
  │    │    ┌──────────┐                                        │
  │    └────┤ REFACTOR │ Clean up, all tests pass               │
  │         └──────────┘                                        │
  │                                                             │
  │  Repeat for each feature/fix within a single request        │
  └─────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  LEVEL 2 — Sweep RGR (codebase-wide, CORE-064)            │
  │                                                             │
  │    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
  │    │  DETECT  │───▶│   FIX    │───▶│  RESCAN  │            │
  │    │ (scan)   │    │ (apply)  │    │ (verify) │            │
  │    └──────────┘    └──────────┘    └─────┬────┘            │
  │                                          │                  │
  │         Loop until p0==0 && p1==0 ◀──────┘                 │
  │                                                             │
  │  SweepCatalogueOrchestrator ensures exhaustive coverage    │
  └─────────────────────────────────────────────────────────────┘
```

**Detailed diagram:** `flat-files/diagrams/diagram-19-rgr-cycle.md`
**Full documentation:** `flat-files/18-rgr-quality-cycle.md`

---

*Source: `cortex/orchestrators/core/tdd_orchestrator.py` · `cortex/orchestrators/support/sweep_catalogue_orchestrator.py`*
