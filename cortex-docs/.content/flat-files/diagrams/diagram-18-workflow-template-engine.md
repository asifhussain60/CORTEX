# Workflow Template Engine — Composition and Execution
# How YAML templates compose from primitives into SDLC pipelines

```
 ═══════════════════════════════════════════════════════════════════════════════
  WORKFLOW TEMPLATE LIBRARY — 17 CATEGORIES
 ═══════════════════════════════════════════════════════════════════════════════

  cortex-registry/workflows/templates/
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                                                                          │
  │  PRIMITIVES (atomic)          TEMPLATES (composed)        COMPOSITES    │
  │  ┌──────────────────┐         ┌──────────────────┐       ┌───────────┐  │
  │  │ analysis/        │────────▶│ sdlc/            │──────▶│ composed- │  │
  │  │  lens-ast-scan   │         │  requirements    │       │ backend   │  │
  │  │  lens-vision     │         │  solution-design │       │ frontend  │  │
  │  ├──────────────────┤         │  implementation  │       └───────────┘  │
  │  │ execution/       │────────▶│  code-review     │                      │
  │  │  audit-trace     │         │  integration     │                      │
  │  │  semantic-edit   │         │  security        │                      │
  │  │  file-extraction │         │  release         │                      │
  │  ├──────────────────┤         ├──────────────────┤                      │
  │  │ governance/      │────────▶│ tdd/             │                      │
  │  │  sweep-open      │         │  feature-impl    │                      │
  │  │  sweep-close     │         │  api-service     │                      │
  │  │  dependency-guard│         │  frontend-visual │                      │
  │  ├──────────────────┤         ├──────────────────┤                      │
  │  │ validation/      │────────▶│ security/        │                      │
  │  │  detect-fix-loop │         │  compliance      │                      │
  │  │  regression-test │         │  hardening       │                      │
  │  │  duplicate-check │         │  threat-model    │                      │
  │  ├──────────────────┤         ├──────────────────┤                      │
  │  │ intelligence/    │────────▶│ quality/         │                      │
  │  │  knowledge-inject│         │  uplift          │                      │
  │  └──────────────────┘         │  dead-code       │                      │
  │                               │  refactor-sweep  │                      │
  │                               ├──────────────────┤                      │
  │                               │ lifecycle/       │                      │
  │                               │  onboarding      │                      │
  │                               │  legacy-rescue   │                      │
  │                               │  migration       │                      │
  │                               │  service-decomp  │                      │
  │                               ├──────────────────┤                      │
  │                               │ governance/      │                      │
  │                               │  golden-promote  │                      │
  │                               │  phase-lifecycle │                      │
  │                               │  review-gate     │                      │
  │                               └──────────────────┘                      │
  └──────────────────────────────────────────────────────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  TEMPLATE ANATOMY — How a Template Is Structured
 ═══════════════════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────┐
  │  Template YAML                                               │
  │                                                              │
  │  ┌────────────────────────────────────────────────────────┐  │
  │  │ HEADER: id, title, description                        │  │
  │  ├────────────────────────────────────────────────────────┤  │
  │  │ TRIGGERS: intents[], mode_keywords[]                  │  │
  │  ├────────────────────────────────────────────────────────┤  │
  │  │ KNOWLEDGE CONTEXT:                                    │  │
  │  │   primary → sdlc/*.yaml                               │  │
  │  │   supplementary → [security, architecture, testing]   │  │
  │  │   company_overrides → [company/domains/*.yaml]        │  │
  │  │   resolution_order → stack > sdlc > domain > generic  │  │
  │  ├────────────────────────────────────────────────────────┤  │
  │  │ WORKFLOW STEPS:                                       │  │
  │  │   step 1 ──▶ template_ref: primitives/analysis/...   │  │
  │  │          │   inputs: {{request.scope}}                │  │
  │  │          │   outputs: [workspace_model]               │  │
  │  │          ▼                                            │  │
  │  │   step 2 ──▶ template_ref: primitives/intelligence/..│  │
  │  │          │   inputs: {{step1.workspace_model}}        │  │
  │  │          ▼                                            │  │
  │  │   step 3 ──▶ template_ref: tdd/tdd-feature-impl      │  │
  │  │          │   gate: true (must pass to continue)       │  │
  │  │          ▼                                            │  │
  │  │   step N ──▶ governance validation                    │  │
  │  └────────────────────────────────────────────────────────┘  │
  └──────────────────────────────────────────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  CONVERGENCE LOOP — detect-fix-rescan-loop Primitive
 ═══════════════════════════════════════════════════════════════════════════════

       ┌─────────┐
       │ DETECT  │◀──────────────────────────────┐
       └────┬────┘                               │
            │ violations found?                  │
            │                                    │
       YES  │                              NO    │
            ▼                              ▼     │
       ┌─────────┐                  ┌──────────┐ │
       │   FIX   │                  │ COMPLETE │ │
       └────┬────┘                  │ (0 P0/P1)│ │
            │                       └──────────┘ │
            ▼                                    │
       ┌─────────┐                               │
       │ RESCAN  │───────────────────────────────┘
       └─────────┘
       (loop until p0_count == 0 && p1_count == 0)

  Used by: /audit fix Stages 7─8, quality/refactor-holistic-sweep.yaml
  Governance: CORE-064 (Sweep Completeness Contract)
```

**Source:** `cortex-registry/workflows/templates/` · `cortex/core/workflow_engine.py`
**Categories:** 17 (audit, backend, composites, frontend, governance, intelligence, internal, lifecycle, maintenance, primitives, quality, sdlc, security, tdd, testing)
