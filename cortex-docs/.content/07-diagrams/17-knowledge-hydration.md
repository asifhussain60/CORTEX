# Knowledge Hydration Pipeline Diagram

---
title: Knowledge Hydration — Resolution and Context Assembly
type: diagram
audience: [Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex/knowledge/, cortex-registry/knowledge/
order: 17
---

> How CORTEX resolves domain knowledge from multiple stores and hydrates execution context.

## Knowledge Resolution Flow

```
  USER REQUEST
      │
      ▼
  ┌────────────────────────────────┐
  │  1. COMPANY OVERLAYS          │  cortex-registry/company/
  │     (highest priority)        │
  └────────────┬───────────────────┘
               │ miss?
               ▼
  ┌────────────────────────────────┐
  │  2. KNOWLEDGE BASE (static)   │  cortex-registry/knowledge-base/
  │     security/, governance/    │
  └────────────┬───────────────────┘
               │ miss?
               ▼
  ┌────────────────────────────────┐
  │  3. SDLC KNOWLEDGE (dynamic)  │  cortex-registry/knowledge/sdlc/
  │     domain-specific YAML      │
  └────────────┬───────────────────┘
               │ miss?
               ▼
  ┌────────────────────────────────┐
  │  4. PATTERN REGISTRY          │  cortex-registry/patterns/
  │     9 enterprise patterns     │
  └────────────┬───────────────────┘
               │ miss?
               ▼
  ┌────────────────────────────────┐
  │  5. LENS REAL-TIME ANALYSIS   │  cortex/lens/ (10 analyzers)
  │     (always runs)             │
  └────────────┬───────────────────┘
               │
               ▼
  ┌────────────────────────────────┐
  │  HYDRATED EXECUTION CONTEXT   │
  │  All knowledge merged for     │
  │  orchestrator consumption     │
  └────────────────────────────────┘
```

**Detailed diagram:** `flat-files/diagrams/diagram-22-knowledge-hydration.md`
**Full documentation:** `flat-files/19-enterprise-patterns-knowledge.md`

---

*Source: `cortex/knowledge/` · `cortex-registry/knowledge/` · `cortex-registry/knowledge-base/`*
