# RGR Quality Cycle

---
title: Red-Green-Refactor — Two-Level Quality Assurance
type: orchestration
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/core/tdd_orchestrator.py
order: 14
---

> CORTEX implements a two-level RGR cycle: unit-level per feature and sweep-level across the codebase.

---

## Level 1 — Unit RGR (TDDOrchestrator)

For every IMPLEMENT/FIX request:

1. **RED:** Write a failing test that defines the desired behaviour (CORE-008)
2. **GREEN:** Implement the minimum code to make the test pass
3. **REFACTOR:** Clean up while all tests stay green

This cycle repeats for each feature or fix within a single request.

## Level 2 — Sweep RGR (SweepCatalogueOrchestrator)

For codebase-wide quality (CORE-064):

1. **DETECT:** Scan the entire codebase for issue instances
2. **FIX:** Apply remediation using Level 1 RGR for each fix
3. **RESCAN:** Verify all instances are resolved; loop if new ones found

The sweep loop continues until `p0_count == 0 and p1_count == 0`.

## How They Compose

```
Sweep RGR (Level 2)
  └── For each issue instance:
        └── Unit RGR (Level 1)
              └── RED → GREEN → REFACTOR
```

Level 1 runs inside Level 2. Every individual fix follows TDD, and the sweep ensures exhaustive coverage.

---

**Full documentation:** `flat-files/18-rgr-quality-cycle.md`
**Diagram:** `07-diagrams/14-rgr-cycle.md`
