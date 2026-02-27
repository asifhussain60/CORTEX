# Workflow Template Tiers

## Overview

CORTEX workflow templates are organized in a **3-tier hierarchy**:

```
Primitive → Composite → Workflow
```

All templates live in `cortex-registry/workflows/templates/`.

## Tier 1: Primitives

**Location:** `templates/primitives/`

Atomic, reusable building blocks. Each primitive has a single responsibility.
Primitives are referenced (not duplicated) by higher tiers.

| Category     | Examples |
|--------------|----------|
| `analysis/`  | `lens-ast-scan.yaml`, `lens-vision-scan.yaml` |
| `execution/` | `audit-trace.yaml`, `file-extraction.yaml`, `semantic-edit.yaml` |
| `governance/`| `sweep-catalogue-open.yaml`, `sweep-catalogue-close.yaml`, `dependency-guard-migration.yaml` |
| `intelligence/` | `intelligence-injection.yaml` |
| `validation/` | `detect-fix-rescan-loop.yaml`, `regression-test.yaml`, `duplicate-detection.yaml` |

### Key Primitive: `audit-trace.yaml`

The `primitives/execution/audit-trace.yaml` primitive is consumed by all workflow templates
that need AC marker trace chain wiring. It ensures every orchestrator invocation produces
a paired `AC_START` / `AC_COMPLETE` entry in `.cortex-runtime/traces/orchestrator-traces.db`.

## Tier 2: Composites

**Location:** `templates/composites/`

Composed of multiple primitives. Represent a reusable workflow pattern for a domain.
Must not duplicate a top-level workflow file (CORE-035).

## Tier 3: Workflows

**Location:** `templates/<domain>/`

Full, intent-specific execution workflows. Each maps to a HEXA-MODE or intent type.

| Domain         | Workflow Examples |
|----------------|-------------------|
| `tdd/`         | `tdd-feature-implementation.yaml`, `tdd-api-service.yaml` |
| `security/`    | `security-compliance-audit.yaml`, `threat-model-analysis.yaml` |
| `lifecycle/`   | `onboarding-workflow.yaml`, `migration-modernize.yaml` |
| `backend/`     | `csharp-refactor-workflow.yaml`, `csharp-security-workflow.yaml` |
| `audit/`       | Audit templates |
| `governance/`  | `master-plan-phase-lifecycle.yaml`, `golden-test-promotion.yaml` |

## CORE-035 Rule

Two files must never exist for the same purpose. If a composite mirrors a top-level
workflow, the composite is deleted and the top-level is the canonical reference.

**Enforcement:** 4 composite duplicates deleted:
- `composites/backend/csharp-refactor.yaml` (mirrors `backend/csharp-refactor-workflow.yaml`)
- `composites/backend/csharp-security.yaml` (mirrors `backend/csharp-security-workflow.yaml`)
- `composites/frontend/html-refactor-validation.yaml` (mirrors `frontend/html-refactor-validation.yaml`)
- `composites/composed-data-pipeline-d01d9892.yaml` (auto-generated artefact — deleted)

## Golden Coverage

Workflow template E2E coverage is enforced by:
- `tests/golden/workflow/test_workflow_e2e_trace_golden.py` — intent trace chain tests
- `tests/golden/governance/test_workflow_template_governance.py` — CORE-035 compliance
- Holistic scenario `workflow_template_ref` field in S21, S22, S23

See also: `07-diagrams/10-golden-test-taxonomy.md`
