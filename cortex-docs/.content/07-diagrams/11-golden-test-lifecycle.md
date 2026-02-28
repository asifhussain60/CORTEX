# Golden Test Lifecycle Diagram

---
title: Golden Test Lifecycle — Scoring, Promotion, and Maintenance
type: diagram
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/testing/quality_gate.py, tests/golden/
order: 11
---

> Shows how tests are scored, promoted to golden tier, maintained, and demoted when quality drops.

## Golden Test Lifecycle Flow

```
  NEW TEST
      │
      ▼
┌───────────────────┐     ┌──────────────────────────┐
│  QUALITY SCORING  │     │  Dimensions (v2.0)       │
│  TestQualityGate  │────▶│  Impact:      0–5        │
│                   │     │  Likelihood:  0–3        │
│                   │     │  Detection:   0–3        │
│                   │     │  Efficiency:  0–2        │
│                   │     │  Maintenance: 0 to −2    │
└────────┬──────────┘     └──────────────────────────┘
         │
    Score calculated
         │
    ┌────┴────┐
    │  ≥ 7?   │
    └────┬────┘
     YES │ NO
    ┌────┘ └────┐
    ▼           ▼
┌────────┐  ┌──────────┐
│ GOLDEN │  │  REVIEW  │  (4–6) or DELETE (< 4)
│  TIER  │  │  or DROP │
└───┬────┘  └──────────┘
    │
    ▼
┌────────────────────────────────────┐
│  GOLDEN MAINTENANCE               │
│  • CORE-055 contract enforced     │
│  • Must pass on every CI run      │
│  • Periodic re-scoring            │
│  • Score drops below 7 → DEMOTED  │
└────────────────────────────────────┘
```

**Detailed diagram:** `flat-files/diagrams/diagram-16-golden-test-lifecycle.md`
**Full documentation:** `flat-files/14-golden-tests.md`

---

*Source: `cortex/testing/quality_gate.py` · `cortex-registry/core/test-quality-gate.yaml`*
