# Workflow Template Tiers

**Updated:** 2026-02-24 (Phase 63 — SWEEP-63-GOLDEN-RENAISSANCE)

This is the flat-file mirror of `01-capabilities/09-workflow-template-tiers.md`.

## 3-Tier Hierarchy

```
Primitive → Composite → Workflow
```

## Tier 1: Primitives (`templates/primitives/`)

Atomic building blocks. Single responsibility each.

- `execution/audit-trace.yaml` — AC marker trace chain wiring (CORE requirement)
- `execution/file-extraction.yaml` — file content extraction
- `execution/semantic-edit.yaml` — semantic code edit
- `analysis/lens-ast-scan.yaml` — LENS AST scan
- `governance/sweep-catalogue-open.yaml` — open SWEEP catalogue
- `governance/sweep-catalogue-close.yaml` — close SWEEP catalogue
- `validation/detect-fix-rescan-loop.yaml` — convergence loop primitive

## Tier 2: Composites (`templates/composites/`)

Multi-primitive patterns. Must not duplicate top-level workflows (CORE-035).

## Tier 3: Workflows (`templates/<domain>/`)

Full intent-specific workflows:
- `tdd/tdd-feature-implementation.yaml` — IMPLEMENT intent
- `security/security-compliance-audit.yaml` — AUDIT intent
- `lifecycle/onboarding-workflow.yaml` — ONBOARD intent

## CORE-035 Enforcement (Phase 63-E)

4 composite duplicates deleted:
- composites/backend/csharp-refactor.yaml
- composites/backend/csharp-security.yaml
- composites/frontend/html-refactor-validation.yaml
- composites/composed-data-pipeline-d01d9892.yaml

## Golden Coverage

Enforced by:
- `tests/golden/workflow/test_workflow_e2e_trace_golden.py`
- `tests/golden/governance/test_workflow_template_governance.py`
- Scenarios S21/S22/S23 include `workflow_template_ref` field

Full detail: `01-capabilities/09-workflow-template-tiers.md`
