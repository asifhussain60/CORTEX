# Workflow Templates

Organized by domain for scalability (designed for 600+ templates).

## Directory Structure

```
templates/
├── tdd/                  # TDD lifecycle workflows (RED→GREEN→REFACTOR)
│   ├── tdd-feature-implementation.yaml
│   ├── tdd-api-service.yaml
│   ├── tdd-frontend-visual.yaml
│   ├── frontend-tdd-workflow.yaml
│   └── test-strategy-matrix.yaml          # Multi-tier test enforcement (unit→integration→security→smoke→regression→golden)
├── security/             # Security audit, hardening, compliance
│   ├── security-hardening.yaml
│   ├── security-compliance-audit.yaml
│   └── threat-model-analysis.yaml         # Standalone STRIDE/DREAD threat modelling brick
├── quality/              # Code quality, refactoring, uplift
│   ├── quality-uplift.yaml
│   ├── quality-code-uplift.yaml
│   ├── refactor-holistic-sweep.yaml
│   └── cross-phase-holistic-epilogue.yaml # Declarative epilogue (lint, dedup, security, cleanup)
├── lifecycle/            # Repo onboarding, migration, legacy rescue
│   ├── onboarding-workflow.yaml
│   ├── onboarding-repo-setup.yaml
│   ├── migration-modernize.yaml
│   ├── legacy-rescue.yaml
│   └── composite-execution-pipeline.yaml  # Generic pipeline-of-pipelines (lego connector)
├── governance/           # Execution gates, test promotion, compliance
│   ├── request-execution-plan-gate.yaml
│   └── golden-test-promotion.yaml
├── maintenance/          # Cleanup, dedup, health checks
│   ├── cleanup-deduplication.yaml
│   ├── review-post-phase-dedup.yaml
│   └── health-vacuum-pipeline.yaml
└── internal/             # CORTEX self-testing workflows
    └── cortex-site-validation.yaml
```

## Adding New Templates

1. Identify the domain category (or create a new subfolder)
2. Use `snake-case` or `kebab-case` YAML filenames (CORE-028)
3. Include `workflow.metadata` block with version, author, created date
4. Register in `cortex-master.yaml` with full path including subfolder
5. Add corresponding tests in `tests/`

## Category Guidelines

| Category | When to use |
|----------|-------------|
| `tdd/` | Any workflow centered on RED→GREEN→REFACTOR cycles |
| `security/` | Threat modeling, vulnerability scanning, compliance audits |
| `quality/` | Code quality metrics, refactoring, complexity reduction |
| `lifecycle/` | Repository onboarding, migration, legacy modernization |
| `governance/` | Execution gates, approval workflows, test promotion |
| `maintenance/` | Deduplication, cleanup, health checks, vacuum pipelines |
| `internal/` | CORTEX self-testing and internal validation workflows |
