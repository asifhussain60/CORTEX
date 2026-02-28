---
title: Workflow Template Library — Reusable YAML Execution Patterns
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex-registry/workflows/templates/ + cortex/core/workflow_engine.py
order: 17
---

# Workflow Template Library — Reusable YAML Execution Patterns

> **Workflow templates are CORTEX's playbook library.** Every repeatable operation — from TDD cycles to security audits to release gates — is codified as a YAML template, version-controlled alongside your code, and executed by the WorkflowEngine through a finite state machine.

---

## Why YAML Workflows?

Code changes. Requirements change. But the _patterns_ of how engineering work gets done are remarkably stable: analyze → design → implement → test → review → release. CORTEX codifies these patterns as YAML templates so they can be:

- **Version-controlled** alongside the codebase (not locked in a CI tool)
- **Composed** from atomic primitives into complex pipelines
- **Customized** per team via company overrides
- **Audited** — every execution is traced via AC markers to SQLite

---

## Template Library Structure

The library lives at `cortex-registry/workflows/templates/` and is organized into 17 categories:

```
cortex-registry/workflows/templates/
├── audit/                     ← Audit pipelines (audit-fix-pipeline.yaml)
├── backend/                   ← Backend-specific workflows
├── composites/                ← Composed multi-template pipelines
│   ├── backend/               ← Backend composite workflows
│   └── frontend/              ← Frontend composite workflows
├── frontend/                  ← Frontend-specific workflows
├── governance/                ← Governance lifecycle templates
│   ├── golden-test-promotion.yaml
│   ├── holistic-file-review-gate.yaml
│   ├── master-plan-phase-lifecycle.yaml
│   ├── phase-59-sweep-catalogue.yaml
│   └── request-execution-plan-gate.yaml
├── intelligence/              ← Intelligence pipeline workflows
├── internal/                  ← Internal CORTEX maintenance workflows
├── lifecycle/                 ← Full lifecycle workflows
│   ├── composite-execution-pipeline.yaml
│   ├── legacy-rescue.yaml
│   ├── master-plan-execution.yaml
│   ├── migration-modernize.yaml
│   ├── onboarding-repo-setup.yaml
│   └── service-decomposition-workflow.yaml
├── maintenance/               ← Maintenance and cleanup workflows
├── primitives/                ← Atomic building blocks (5 categories)
│   ├── analysis/              ← LENS scans, vision analysis
│   ├── execution/             ← File operations, semantic edits, audit traces
│   ├── governance/            ← Sweep catalogue lifecycle, dependency guards
│   ├── intelligence/          ← Knowledge injection
│   └── validation/            ← Detect-fix-rescan loop, regression tests, duplicate detection
├── quality/                   ← Quality improvement workflows
│   ├── cross-phase-holistic-epilogue.yaml
│   ├── dead-code-removal.yaml
│   ├── duplicate-validation.yaml
│   ├── quality-code-uplift.yaml
│   └── refactor-holistic-sweep.yaml
├── sdlc/                      ← Full SDLC lifecycle (7 phases)
│   ├── requirements-analysis.yaml
│   ├── solution-design.yaml
│   ├── implementation-execution.yaml
│   ├── code-review-gate.yaml
│   ├── integration-verification.yaml
│   ├── security-assessment.yaml
│   └── release-readiness.yaml
├── security/                  ← Security-focused workflows
│   ├── security-compliance-audit.yaml
│   ├── security-hardening.yaml
│   └── threat-model-analysis.yaml
├── tdd/                       ← TDD-specific workflows
│   ├── tdd-feature-implementation.yaml
│   ├── tdd-api-service.yaml
│   ├── tdd-frontend-visual.yaml
│   ├── frontend-tdd-workflow.yaml
│   └── test-strategy-matrix.yaml
└── testing/                   ← Test management workflows
    ├── test-quality-enforcement.yaml
    └── test-tier-manifest.yaml
```

---

## Template Anatomy

Every workflow template follows a consistent structure:

```yaml
id: sdlc-implementation-execution
title: "Implementation Execution Workflow"
description: |
  TDD-driven implementation workflow with knowledge context injection.

triggers:
  intents: ["IMPLEMENT", "BUILD", "CREATE"]
  mode_keywords: ["implement", "build", "create"]

knowledge_context:
  primary: "sdlc/test-strategy-selection.yaml"
  supplementary:
    - "testing-validation/tdd-best-practices.yaml"
    - "sdlc/security-by-design.yaml"
  company_overrides:
    - "company/domains/api-standards.yaml"
  resolution_order: "stack-specific > sdlc > domain > generic"

workflow:
  steps:
    - id: lens_scan
      name: "LENS Analysis"
      template_ref: "primitives/analysis/lens-ast-scan.yaml"
      inputs:
        scope: "{{request.scope}}"
      outputs: ["workspace_model"]

    - id: tdd_cycle
      name: "TDD Implementation"
      template_ref: "tdd/tdd-feature-implementation.yaml"
      inputs:
        workspace_model: "{{lens_scan.workspace_model}}"

    - id: governance_gate
      name: "Governance Validation"
      gate: true
      pass_condition: "zero_p0_violations"
```

### Key Fields

| Field | Purpose |
|-------|---------|
| `triggers.intents` | Which intents activate this template |
| `knowledge_context` | Knowledge YAMLs to inject before execution |
| `knowledge_context.resolution_order` | Priority when knowledge sources conflict |
| `workflow.steps[].template_ref` | Reference to a primitive or sub-template |
| `workflow.steps[].gate` | If `true`, this step must pass before continuing |
| `workflow.steps[].inputs/outputs` | Data flow between steps using `{{}}` interpolation |

---

## Execution Engine

The `WorkflowEngine` at `cortex/core/workflow_engine.py` reads template YAML and executes steps through a finite state machine:

```
PENDING → RUNNING → COMPLETED
                  → FAILED → RETRY (if retriable)
                  → BLOCKED (if gate fails)
```

Each step transition emits AC markers (`AC_START`, `AC_COMPLETE`) and records to the SQLite audit trail.

### Convergence Loop

The detect-fix-rescan-loop primitive at `primitives/validation/detect-fix-rescan-loop.yaml` implements CORE-064:

1. **Detect** — scan for violations
2. **Fix** — apply remediation
3. **Rescan** — check if violations remain
4. **Loop** — repeat until `p0_count == 0 && p1_count == 0`

This primitive is used by `/audit fix` (Stages 7–8) and by quality uplift workflows.

---

## Composites — Multi-Template Pipelines

Composite templates in `composites/` chain multiple templates into larger workflows. For example, a backend implementation composite might chain:

1. `sdlc/requirements-analysis.yaml` → understand the request
2. `sdlc/solution-design.yaml` → select architecture
3. `tdd/tdd-api-service.yaml` → implement with TDD
4. `sdlc/code-review-gate.yaml` → validate quality
5. `sdlc/security-assessment.yaml` → security gate
6. `sdlc/integration-verification.yaml` → integration tests

Each composite is generated with a unique hash ID (e.g., `composed-design-5099cb46.yaml`) ensuring traceability.

---

## Company Customization

Teams customize workflows through company override YAMLs in `cortex-registry/knowledge/`:

```yaml
# cortex-registry/knowledge/company/domains/api-standards.yaml
rules:
  - All REST APIs must use OpenAPI 3.0 specs
  - Authentication via OAuth2 with JWT tokens
  - Rate limiting mandatory on all public endpoints
```

Company overrides always win when they conflict with generic SDLC knowledge. The resolution order (`stack-specific > sdlc > domain > generic`) ensures team-specific rules take precedence.
