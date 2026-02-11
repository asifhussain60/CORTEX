# Complex Planning Roadmap Template

**Purpose:** Advanced multi-wave, multi-track template demonstrating parallelism

**Structure:**
- 5 Waves
- 15 Total Phases
- 3 Parallel Tracks
- ~500 dev hours total
- Dependency management

## Usage

```python
from cortex.orchestrators.planning import (
    UnifiedPlanningOrchestrator,
    ROICompositeScorer,
    DependencyResolver,
    ParallelismCalculator,
)

# Load registry
with open("cortex/templates/planning/complex-roadmap/index.yaml") as f:
    registry = yaml.safe_load(f)

# Analyze before execution
scorer = ROICompositeScorer()
resolver = DependencyResolver()
calc = ParallelismCalculator()

# Execute orchestrator
orchestrator = UnifiedPlanningOrchestrator()
result = orchestrator.execute(registry)
```

## Wave Structure

```
Wave 1: Foundation (Track A)           [■■■]
  ├─ P-001: Infrastructure            [■■]
  ├─ P-002: Governance               [■]
  └─ P-003: CI/CD Setup              [■]

Wave 2: Core (Tracks A, B parallel)   [■■■][■■]
  ├─ P-004: API Design (A)           [■■]
  ├─ P-005: Backend Core (A)         [■■■]
  ├─ P-006: Frontend Setup (B)       [■]
  └─ P-007: UI Components (B)        [■]

Wave 3: Features (Tracks B, C)        [■■][■■■]
  ├─ P-008: Auth System (B)          [■]
  ├─ P-009: Dashboard (B)            [■]
  ├─ P-010: Reporting (C)            [■■]
  └─ P-011: Analytics (C)            [■■]

Wave 4: Integration (Track A)         [■■■]
  ├─ P-012: Backend Integration      [■■]
  └─ P-013: API Gateway              [■]

Wave 5: Release (All)                 [■]
  ├─ P-014: Stabilization            [■]
  └─ P-015: Release Ops              [■]
```

## Parallelism Analysis

- **Wave 1:** No parallelism (foundation must complete)
- **Wave 2:** 2 tracks parallel (backend + frontend)
- **Wave 3:** 2 tracks parallel (auth/dashboard + reporting)
- **Wave 4:** Sequential (integration depends on Wave 2, 3)
- **Wave 5:** Sequential (release depends on all)

**Maximum parallelism:** 3 concurrent phases

## Advanced Features

1. **ROI Scoring:** Waves ranked by (roi × 0.6) + (unblock × 0.3) + (risk × 0.1)
2. **Dependency Resolution:** Validates no cycles, computes critical path
3. **Parallelism Calculation:** Identifies independent tracks and resource bottlenecks
4. **Timeline Estimation:** Projects completion based on effort + parallelism

## Customization

1. Add/remove waves
2. Adjust phase dependencies
3. Modify effort estimates
4. Change ROI scoring weights
5. Add resource constraints

## Next Steps

- Use `scaled-50wave-roadmap` for enterprise CORTEX-style planning
- Integrate with CI/CD for automated phase execution
- Connect to dashboard for real-time progress tracking
