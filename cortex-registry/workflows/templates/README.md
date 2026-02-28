# Workflow Templates

Organized by domain for scalability (designed for 600+ templates).
**Workflow Composer Spec:** `cortex-registry/workflows/workflow-composer-spec.yaml`

## 3-Tier Workflow Composer Architecture

| Tier | Purpose | Location |
|------|---------|----------|
| **Tier 1: Primitives** | Atomic, reusable steps (gates, loops, markers) | `primitives/` |
| **Tier 2: Mode Workflows** | One per execution mode (IMPLEMENT, FIX, REFACTOR, etc.) | Per-category dirs |
| **Tier 3: Composite Pipelines** | Multi-mode compositions (audit-fix, totalrecall) | `composites/` + `audit/` |

### Intent → Workflow Routing

| Intent | Workflow Template | Pre-Gate Primitive |
|--------|------------------|--------------------|
| IMPLEMENT | `sdlc/implement-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| FIX | `sdlc/fix-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| REFACTOR | `quality/refactor-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| AUDIT | `audit/audit-fix-pipeline.yaml` | — |
| VACUUM | `maintenance/vacuum-workflow.yaml` | — |
| HEALTH | `maintenance/health-check-workflow.yaml` | — |
| DEBUG | `debugging/multi-stack-debug-pipeline.yaml` | — |
| DIGEST | `lifecycle/digest-workflow.yaml` | — |
| TOTALRECALL | `lifecycle/totalrecall-workflow.yaml` | — |
| SYNC | `lifecycle/sync-workflow.yaml` | — |
| TRAIN | `lifecycle/train-workflow.yaml` | — |
| META-AUDIT | `governance/meta-audit-workflow.yaml` | — |
| STAGE0 | `governance/stage0-preflight-workflow.yaml` | — |

### Universal Primitives (injected into every code-modifying workflow)

| Primitive | Purpose |
|-----------|---------|
| `primitives/execution/ac-marker-emit.yaml` | AC_START / AC_COMPLETE markers |
| `primitives/execution/git-checkpoint.yaml` | Safe rollback point before changes |
| `primitives/governance/dor-display.yaml` | Definition of Ready display |
| `primitives/governance/holistic-validation-gate.yaml` | CORE-048 pre-execution gate |
| `primitives/governance/challenge-gate.yaml` | Risk-based alternative presentation |
| `primitives/governance/sweep-catalogue-open.yaml` | CORE-064 sweep tracking open |
| `primitives/governance/sweep-catalogue-close.yaml` | CORE-064 sweep tracking close |
| `primitives/validation/detect-fix-rescan-loop.yaml` | CORE-068 convergence gate |

## Directory Structure

```
templates/
├── primitives/           # Atomic reusable building blocks (tier 1)
│   ├── analysis/         # lens-ast-scan, lens-vision-scan
│   ├── execution/        # semantic-edit, file-extraction, audit-trace,
│   │                     # ac-marker-emit, git-checkpoint
│   ├── governance/       # holistic-validation-gate, challenge-gate,
│   │                     # dor-display, sweep-catalogue-open/close
│   └── validation/       # regression-test, detect-fix-rescan-loop,
│                         # duplicate-detection, dom-validation, css-zero-inline
├── sdlc/                 # Software development lifecycle (IMPLEMENT, FIX)
│   ├── implement-workflow.yaml
│   ├── fix-workflow.yaml
│   └── implementation-execution.yaml
├── composites/           # Composed templates (assembled by TemplateComposer)
│   ├── backend/          # csharp-refactor, csharp-security
│   └── frontend/         # css-extraction, html-refactor-validation
├── audit/                # Audit pipelines
│   └── audit-fix-pipeline.yaml   # 9-stage /audit fix production pipeline
├── debugging/            # Multi-stack debug pipeline
│   └── multi-stack-debug-pipeline.yaml
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
│   ├── refactor-workflow.yaml        # REFACTOR mode workflow
│   ├── quality-uplift.yaml
│   ├── quality-code-uplift.yaml
│   ├── refactor-holistic-sweep.yaml
│   ├── duplicate-validation.yaml
│   ├── dead-code-removal.yaml
│   └── cross-phase-holistic-epilogue.yaml
├── lifecycle/            # Repo onboarding, migration, lifecycle modes
│   ├── digest-workflow.yaml           # DIGEST mode
│   ├── totalrecall-workflow.yaml      # TOTALRECALL mode
│   ├── sync-workflow.yaml             # SYNC mode
│   ├── train-workflow.yaml            # TRAIN mode
│   ├── onboarding-workflow.yaml
│   ├── onboarding-repo-setup.yaml
│   ├── migration-modernize.yaml
│   ├── legacy-rescue.yaml
│   ├── service-decomposition-workflow.yaml
│   ├── master-plan-execution.yaml
│   ├── master-plan-orchestrator.yaml
│   └── composite-execution-pipeline.yaml
├── governance/           # Execution gates, meta-audit, stage0
│   ├── stage0-preflight-workflow.yaml  # Stage 0 pre-flight
│   ├── meta-audit-workflow.yaml        # META-AUDIT mode (25 checks)
│   ├── request-execution-plan-gate.yaml
│   ├── golden-test-promotion.yaml
│   └── master-plan-phase-lifecycle.yaml
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
| **Tier 1: Primitive** | `primitives/` | Atomic, independently testable building blocks. Reusable gates, loops, markers. Steps under `execution.steps` (canonical schema). |
| **Tier 2: Mode Workflow** | `sdlc/`, `quality/`, `maintenance/`, `governance/`, `lifecycle/`, `debugging/` | One per execution mode. Imports primitives via `primitive_ref`. Declares convergence predicates. |
| **Tier 3: Composite** | `composites/`, `audit/` | Auto-assembled by `TemplateComposer` from primitives + mode workflows. Multi-mode pipelines. |

**Specification:** See `cortex-registry/workflows/workflow-composer-spec.yaml` for the complete schema, principles, and validation rules.

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
| `primitives/` | Atomic operations reused across multiple workflows (gates, loops, markers) |
| `composites/` | TemplateComposer output — do not hand-author |
| `sdlc/` | IMPLEMENT and FIX mode workflows (TDD-centered) |
| `audit/` | Production-readiness scan pipelines |
| `debugging/` | Multi-stack debug pipeline (marker injection, capture, analysis) |
| `tdd/` | Any workflow centered on RED→GREEN→REFACTOR cycles |
| `security/` | Threat modeling, vulnerability scanning, compliance audits |
| `quality/` | Code quality metrics, refactoring, complexity reduction |
| `lifecycle/` | Repository onboarding, migration, digest, sync, train, totalrecall |
| `governance/` | Execution gates, stage0 preflight, meta-audit, test promotion |
| `maintenance/` | Deduplication, cleanup, health checks, vacuum pipelines |
| `backend/` | Language-specific backend refactor/security workflows |
| `frontend/` | Language-specific frontend refactor/CSS workflows |
| `internal/` | CORTEX self-testing and internal validation workflows |
| `testing/` | Test tier manifests and test strategy templates |
