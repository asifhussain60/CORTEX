---
id: governance-sweep-completeness-core-064
title: Sweep completeness contract (CORE-064)
purpose: Explain why CORTEX avoids partial fixes by cataloguing every instance and closing them all.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/support/sweep_catalogue_orchestrator.py
  - cortex-registry/workflows/templates/primitives/
last_verified: 2026-03-09
diagram_type: Governance
render: ascii
render_html: true
d3_method: "d3.tree() — sweep tracking flowchart with catalogue table"
---

# Sweep Completeness — CORE-064 Lifecycle

```
 ISSUE DETECTED
      │
      ▼
 STEP 1: Catalogue all instances (workspace-wide)
      │
      ▼
 STEP 2: Fix loop per instance (RED → GREEN → REFACTOR → VALIDATE)
      │
      ▼
 STEP 3: Rescan
      │
      ├─ all instances closed? → YES → Sweep complete
      └─ NO → add new instances → loop
```
