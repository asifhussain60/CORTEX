---
id: testing-strategy-pyramid
title: Testing strategy pyramid (preflight → smoke → unit → integration → golden)
purpose: Show how CORTEX structures tests for speed and confidence.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - scripts/run_tests.py
  - tests/
last_verified: 2026-03-09
diagram_type: Testing
render: ascii
render_html: true
d3_method: "d3.tree() — stacked pyramid with tier labels"
---

# Testing Strategy — Pyramid and Execution Tiers

```
                 GOLDEN (deterministic truth)
                /---------------------------\
               /         Integration         \
              /-------------------------------\
             /            Unit tests           \
            /----------------------------------\
           /             Smoke tests            \
          /-------------------------------------\
         /            Preflight (<10s)           \
        /----------------------------------------\
```
