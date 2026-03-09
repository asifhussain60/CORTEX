---
id: audit-audit-fix-pipeline
title: /audit fix pipeline (9 stages)
purpose: Explain the audit → fix → rescan convergence loop and verification stage.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex-registry/workflows/templates/audit/
  - cortex/orchestrators/
last_verified: 2026-03-09
diagram_type: Workflow
render: ascii
render_html: true
d3_method: "d3.tree() — vertical flowchart with convergence loop"
---

# Audit Fix Pipeline — 9-Stage Flow

```
                                 /audit fix
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE -1: ENVIRONMENT READINESS                                     │
│  • Python check + requirements sync                                  │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 2: PRODUCTION SCAN                                             │
│  • Wiring · MCP · governance · intelligence · infra · logs             │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGES 7–8: AUTO-FIX CONVERGENCE LOOP                                │
│    DETECT → FIX → RESCAN (loop until P0=0 and P1=0)                   │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 9: TESTS + COMPLETE                                            │
│  • preflight tests + status summary                                   │
└──────────────────────────────────────────────────────────────────────┘
```

Note: This is a conceptual diagram for docs/training and intentionally avoids exact internal counts.
