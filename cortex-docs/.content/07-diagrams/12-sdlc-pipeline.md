# SDLC Workflow Pipeline Diagram

---
title: SDLC 7-Phase Pipeline — From Requirements to Deployment
type: diagram
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/domain/sdlc_workflow_orchestrator.py
order: 12
---

> The full software development lifecycle as executed by CORTEX's SDLCWorkflowOrchestrator.

## 7-Phase SDLC Pipeline

```
  USER REQUEST
      │
      ▼
┌──────────────────────────────────────────────────────────────────┐
│  SDLCWorkflowOrchestrator — Intent Mapping                      │
│                                                                  │
│  ANALYZE  → requirements-analysis.yaml                          │
│  DESIGN   → solution-design.yaml                                │
│  IMPLEMENT→ implementation-execution.yaml                       │
│  TEST     → testing-strategy.yaml                               │
│  SECURITY → security-review.yaml                                │
│  DEPLOY   → deployment-pipeline.yaml                            │
│  REVIEW   → code-review-checklist.yaml                          │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
  Phase 1          Phase 2          Phase 3          Phase 4
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│REQUIRE-  │───▶│ SOLUTION │───▶│ IMPLEMENT│───▶│ TESTING  │
│MENTS     │    │ DESIGN   │    │          │    │ & QA     │
│ANALYSIS  │    │          │    │ (TDD)    │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
  Phase 7          Phase 6          Phase 5            │
┌──────────┐    ┌──────────┐    ┌──────────┐          │
│ DEPLOY-  │◀───│ CODE     │◀───│ SECURITY │◀─────────┘
│ MENT     │    │ REVIEW   │    │ REVIEW   │
└──────────┘    └──────────┘    └──────────┘

  Security gates at EVERY phase transition
  Knowledge hydration from cortex-registry/knowledge/
```

**Detailed diagram:** `flat-files/diagrams/diagram-17-sdlc-pipeline.md`
**Full documentation:** `flat-files/16-sdlc-workflow-engine.md`

---

*Source: `cortex/orchestrators/domain/sdlc_workflow_orchestrator.py` · `cortex-registry/workflows/templates/sdlc/`*
