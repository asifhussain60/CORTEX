# Workflow Templates

Organized by domain for scalability (designed for 600+ templates).

## Directory Structure

```
templates/
├── primitives/           # Atomic reusable building blocks (tier 1)
│   ├── analysis/         # lens-ast-scan, lens-vision-scan
│   ├── execution/        # semantic-edit, file-extraction, audit-trace
│   └── validation/       # regression-test, detect-fix-rescan-loop,
│                         # duplicate-detection, dom-validation, css-zero-inline
├── composites/           # Composed templates (assembled by TemplateComposer)
│   ├── backend/          # csharp-refactor, csharp-security
│   └── frontend/         # css-extraction, html-refactor-validation
├── audit/                # Audit pipelines
│   └── audit-fix-pipeline.yaml   # 9-stage /audit fix production pipeline
├── tdd/                  # TDD lifecycle workflows (RED→GREEN→REFACTOR)
│   ├── tdd-feature-implementation.yaml
│   ├── tdd-api-service.yaml
│   ├── tdd-frontend-visual.yaml
│   ├── frontend-tdd-workflow.yaml
│   └── test-strategy-matrix.yaml   # Multi-tier test enforcement
├── security/             # Security audit, hardening, compliance
│   ├── security-hardening.yaml
│   ├── security-compliance-audit.yaml
│   └── threat-model-analysis.yaml   # Standalone STRIDE/DREAD threat modelling brick
├── quality/              # Code quality, refactoring, uplift
│   ├── quality-uplift.yaml
│   ├── quality-code-uplift.yaml
│   ├── refactor-holistic-sweep.yaml
│   ├── duplicate-validation.yaml
│   ├── dead-code-removal.yaml
│   └── cross-phase-holistic-epilogue.yaml   # Declarative epilogue (lint, dedup, security, cleanup)
├── lifecycle/            # Repo onboarding, migration, legacy rescue
│   ├── onboarding-workflow.yaml
│   ├── onboarding-repo-setup.yaml
│   ├── migration-modernize.yaml
│   ├── legacy-rescue.yaml
│   ├── service-decomposition-workflow.yaml
│   ├── master-plan-execution.yaml
│   ├── master-plan-orchestrator.yaml
│   └── composite-execution-pipeline.yaml   # Generic pipeline-of-pipelines (lego connector)
├── governance/           # Execution gates, test promotion, compliance
│   ├── request-execution-plan-gate.yaml
│   └── golden-test-promotion.yaml
├── maintenance/          # Cleanup, dedup, health checks
│   ├── cleanup-deduplication.yaml
│   ├── review-post-phase-dedup.yaml
│   └── health-vacuum-unified-pipeline.yaml
├── backend/              # Language-specific backend workflows
│   ├── csharp-refactor-workflow.yaml
│   └── csharp-security-workflow.yaml
├── frontend/             # Language-specific frontend workflows
│   ├── css-extraction-workflow.yaml
│   ├── css-zero-inline-workflow.yaml
│   ├── html-refactor-validation.yaml
│   └── typescript-refactor-workflow.yaml
└── internal/             # CORTEX self-testing workflows
    └── cortex-site-validation.yaml
```

## Template Tiers

| Tier | Location | Description |
|------|----------|-------------|
| **Primitive** | `primitives/` | Atomic, independently testable building blocks. Used by `TemplateComposer` via `PrimitiveScanner`. Steps are stored under `execution.steps` (canonical schema). |
| **Composite** | `composites/` | Auto-assembled by `TemplateComposer` from primitives. Persisted for reuse. Do not hand-author. |
| **Workflow** | All other dirs | Full end-to-end workflows composed of primitives + domain logic |

## Adding New Templates

1. Identify the domain category (or create a new subfolder)
2. Use `snake-case` or `kebab-case` YAML filenames (CORE-028)
3. Include `workflow.metadata` block with version, author, created date
4. **Primitives only:** put steps under `execution.steps` (not root-level `steps:`) — this is the canonical schema read by `PrimitiveScanner`
5. Register in `cortex-master.yaml` with full path including subfolder
6. Add corresponding tests in `tests/`

## Category Guidelines

| Category | When to use |
|----------|-------------|
| `primitives/` | Atomic operations reused across multiple workflows |
| `composites/` | TemplateComposer output — do not hand-author |
| `audit/` | Production-readiness scan pipelines |
| `tdd/` | Any workflow centered on RED→GREEN→REFACTOR cycles |
| `security/` | Threat modeling, vulnerability scanning, compliance audits |
| `quality/` | Code quality metrics, refactoring, complexity reduction |
| `lifecycle/` | Repository onboarding, migration, legacy modernization |
| `governance/` | Execution gates, approval workflows, test promotion |
| `maintenance/` | Deduplication, cleanup, health checks, vacuum pipelines |
| `backend/` | Language-specific backend refactor/security workflows |
| `frontend/` | Language-specific frontend refactor/CSS workflows |
| `internal/` | CORTEX self-testing and internal validation workflows |
