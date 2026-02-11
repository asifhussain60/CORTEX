# Simple Planning Roadmap Template

**Purpose:** Minimal 3-phase single-wave template for getting started with UnifiedPlanningOrchestrator

**Structure:**
- 1 Wave
- 3 Sequential Phases
- No parallel tracks
- ~120 dev hours total

## Usage

```python
from cortex.orchestrators.planning import UnifiedPlanningOrchestrator
import yaml

# Load template
with open("cortex/templates/planning/simple-roadmap/index.yaml") as f:
    registry = yaml.safe_load(f)

# Execute
orchestrator = UnifiedPlanningOrchestrator()
result = orchestrator.execute(registry)
print(f"Wave completion: {result.progress}%")
```

## File Structure

```
cortex/templates/planning/simple-roadmap/
├── README.md                              (this file)
├── index.yaml                             (wave + phase definitions)
└── phases/active/
    ├── P-001-foundation.yaml              (Phase 1: Infrastructure setup)
    ├── P-002-core-feature.yaml            (Phase 2: Core feature impl)
    └── P-003-stabilization.yaml           (Phase 3: Testing + polish)
```

## Phase Definitions

### Phase 1: Foundation (40 hours)
- Set up infrastructure
- Configure dependencies
- Establish governance rules

### Phase 2: Core Feature (50 hours)
- Implement main functionality
- Create user-facing APIs
- Write integration tests

### Phase 3: Stabilization (30 hours)
- Performance optimization
- Documentation
- Release preparation

## Next Steps

1. **Customize:** Edit phase YAMLs with your own requirements
2. **Extend:** Add more phases or parallel tracks using complex-roadmap template
3. **Scale:** Use scaled-50wave-roadmap for enterprise planning

## Reference

- Main orchestrator: `cortex/orchestrators/planning/`
- Models: `cortex/orchestrators/planning/models/`
  - `ROICompositeScorer`: Wave prioritization
  - `DependencyResolver`: Dependency analysis
  - `ParallelismCalculator`: Parallelism detection
- User guide: `docs/guides/user-planning-orchestrator.md`
