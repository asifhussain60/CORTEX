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
last_verified: 2026-03-01
diagram_type: Testing
render: ascii
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
