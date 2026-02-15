# User Planning Orchestrator Guide

**Version:** 1.0 | **Updated:** 2026-02-12 | **Authority:** Wave 8 Stage 4

---

## Quick Start (15 minutes)

### Step 1: Use a Template

Choose a template:
- **Simple:** 1 wave, 3 phases, sequential (5 mins setup)
- **Complex:** 5 waves, 15 phases, parallel tracks (10 mins setup)

### Step 2: Copy Template

```bash
# Copy simple template to your project
cp -r cortex/templates/planning/simple-roadmap/ my-project/planning-registry/

# Edit for your use case
cd my-project/planning-registry/
edit index.yaml         # Update wave definitions
edit phases/active/     # Update phase details
```

### Step 3: Execute Orchestrator

```python
from cortex.orchestrators.planning import (
    ROICompositeScorer,
    DependencyResolver,
    ParallelismCalculator,
)
import yaml

# Load your registry
with open("planning-registry/index.yaml") as f:
    registry = yaml.safe_load(f)

# Analyze before execution
scorer = ROICompositeScorer()
resolver = DependencyResolver()
calc = ParallelismCalculator()

# Execute orchestration
result = orchestrator.execute(registry)
print(f"Execution status: {result.status}")
print(f"Progress: {result.progress}%")
```

---

## In-Depth Workflow

### Phase 1: Plan Your Waves

Define your high-level delivery plan:

```yaml
waves:
  - wave_id: "WAVE-1"
    title: "Foundation"
    effort_hours: 80
    depends_on: []
    
  - wave_id: "WAVE-2"
    title: "Core Features"
    effort_hours: 150
    depends_on: ["WAVE-1"]
    
  - wave_id: "WAVE-3"
    title: "Advanced Features"
    effort_hours: 120
    depends_on: ["WAVE-2"]
```

**Questions to answer:**
- How many waves needed? (typical: 3-10)
- What's the dependency chain?
- Which waves can run in parallel?
- Effort per wave? (40-200 hours typical)

### Phase 2: Define Phases Within Waves

Each wave contains multiple phases:

```yaml
waves:
  - wave_id: "WAVE-1"
    phases:
      - phase_id: "P-001"
        title: "Infrastructure Setup"
        effort_hours: 40
        depends_on: []
      
      - phase_id: "P-002"
        title: "CI/CD Configuration"
        effort_hours: 40
        depends_on: ["P-001"]
```

**Best practices:**
- Keep phases <50 hours (1-2 week sprints)
- Document dependencies clearly
- Include success criteria
- Identify risks

### Phase 3: Calculate ROI & Prioritization

Use ROI Composite Scorer:

```python
from cortex.orchestrators.planning.models import ROICompositeScorer, ScoringInput

scorer = ROICompositeScorer()

waves = [
    ScoringInput("WAVE-1", roi_value=9, unblock_value=8, risk_level=4),
    ScoringInput("WAVE-2", roi_value=7, unblock_value=3, risk_level=5),
]

results = scorer.score_waves(waves)
prioritized = scorer.prioritize_by_score(results)

for result in prioritized:
    print(f"{result.rank}. {result.wave_id}: {result.composite_score:.2f}")
```

**ROI Calculation:**
```
composite_score = (roi × 0.6) + (unblock × 0.3) + (risk × 0.1)

Where:
  roi:     Business value (0-10)
  unblock: Waves unblocked by this wave (0-10)
  risk:    Implementation risk (0-10, lower is better)
```

### Phase 4: Resolve Dependencies

Validate your dependency graph:

```python
from cortex.orchestrators.planning.models import DependencyResolver, WaveDependency

resolver = DependencyResolver()

waves = [
    WaveDependency("WAVE-1", depends_on=[]),
    WaveDependency("WAVE-2", depends_on=["WAVE-1"]),
    WaveDependency("WAVE-3", depends_on=["WAVE-2"]),
]

result = resolver.resolve(waves)

if result.valid:
    print(f"Execution order: {result.execution_order}")
    print(f"Critical path: {result.critical_path_length} waves")
    print(f"Gating waves: {result.gates}")
else:
    print(f"Cycles detected: {result.cycles}")
```

**Key outputs:**
- `execution_order`: Valid topological sort
- `critical_path_length`: Longest dependency chain
- `gates`: Waves that block others

### Phase 5: Calculate Parallelism

Identify parallel tracks:

```python
from cortex.orchestrators.planning.models import (
    ParallelismCalculator,
    ResourceConstraints,
    WaveResourceUsage,
)

calc = ParallelismCalculator()

wave_dependencies = {
    "WAVE-1": [],
    "WAVE-2": ["WAVE-1"],
    "WAVE-3": ["WAVE-1"],
    "WAVE-4": ["WAVE-2", "WAVE-3"],
}

result = calc.calculate_parallelism(wave_dependencies)

print(f"Max parallel waves: {result.max_parallelism}")
print(f"Tracks: {result.track_count}")
print(f"Critical path: {result.critical_path_waves}")
```

**Parallelism benefits:**
- Reduce total timeline
- Better resource utilization
- Identify bottlenecks

### Phase 6: Integrate with CI/CD

Execute phases in your pipeline:

```yaml
# .github/workflows/plan-execution.yml
name: Execute Planning Waves

on:
  schedule:
    - cron: '0 9 * * MON'  # Monday morning

jobs:
  execute-wave:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Load registry
        run: |
          python3 <<EOF
          from cortex.orchestrators.planning import UnifiedPlanningOrchestrator
          import yaml
          
          with open("planning-registry/index.yaml") as f:
              registry = yaml.safe_load(f)
          
          orchestrator = UnifiedPlanningOrchestrator()
          result = orchestrator.execute(registry)
          
          print(f"::notice::Wave execution complete: {result.status}")
          EOF
      
      - name: Update dashboard
        run: |
          # Connect to monitoring dashboard
          python3 scripts/update_planning_dashboard.py
```

---

## Common Patterns

### Pattern 1: Sequential Waves

One wave after another (safe, longer timeline):

```yaml
Wave 1 → Wave 2 → Wave 3 → Wave 4
```

Use when:
- Each wave depends on previous
- Resources are limited
- Risk management is critical

### Pattern 2: Parallel Tracks

Multiple tracks that can run together:

```yaml
Track A: Wave 1 → Wave 2 → Wave 4
Track B: Wave 1 → Wave 3 → Wave 4
```

Use when:
- Independent features
- Resources available
- Different teams per track

### Pattern 3: Diamond Dependencies

Multiple waves converge:

```yaml
Wave 1 → Wave 2 ┐
         Wave 3 ┴→ Wave 4
```

Use when:
- Feature depends on multiple foundation items
- Strong gating required

---

## Best Practices

### 1. Realistic Effort Estimation

- Break down work into concrete tasks
- Include testing, documentation, deployment
- Add 20% buffer for unknowns
- Track actual vs. estimated

### 2. Clear Dependencies

- Document why dependencies exist
- Identify blocking vs. soft dependencies
- Validate no cycles
- Keep dependency chain short

### 3. Measurable Success Criteria

Each phase should have:
- ✅ Definition of "done"
- ✅ Quality metrics (tests passing, coverage)
- ✅ Acceptance criteria
- ✅ Rollback plan (if needed)

### 4. Risk Management

Identify for each wave:
- Technical risks (new tech, complexity)
- Resource risks (availability, skills)
- Timeline risks (dependencies, bottlenecks)
- Mitigation strategies

### 5. Regular Reviews

- Weekly progress checks
- Adjust effort estimates
- Identify blockers early
- Update dependencies as needed

---

## Anti-Patterns (Avoid)

❌ **Over-estimation:** "This might take 500 hours" (leads to blocking)
❌ **Circular dependencies:** Wave A depends on B, B depends on A
❌ **Unrealistic parallelism:** Assuming everything can run in parallel
❌ **No success criteria:** "When do we know it's done?"
❌ **Single-threaded:** One person on all waves (no parallelism)

---

## Reference

### Models

- **ROICompositeScorer:** Wave-level prioritization
  ```python
  scorer = ROICompositeScorer()
  result = scorer.calculate_score(ScoringInput(...))
  ```

- **DependencyResolver:** Dependency graph validation
  ```python
  resolver = DependencyResolver()
  result = resolver.resolve(waves)
  ```

- **ParallelismCalculator:** Parallelization analysis
  ```python
  calc = ParallelismCalculator()
  result = calc.calculate_parallelism(wave_dependencies)
  ```

### Templates

- `cortex/templates/planning/simple-roadmap/` (getting started)
- `cortex/templates/planning/complex-roadmap/` (advanced)
- `cortex/templates/planning/scaled-50wave-roadmap/` (enterprise)

### Integration Examples

- Python: `examples/planning/create_wave_plan.py`
- YAML: `examples/planning/user-roadmap.yaml`
- CI/CD: `.github/workflows/plan-execution.yml`

---

## Troubleshooting

**Q: Circular dependency detected**
A: Check depends_on fields for cycles. Use graph visualization to find loop.

**Q: Parallelism too low**
A: Check dependencies - some might be unnecessarily strict. Consider splitting waves.

**Q: Timeline too long**
A: Increase parallelism, reduce wave size, or add resources.

**Q: Too many phases**
A: Consolidate related work, reduce granularity.

---

## Support

For issues or questions:
- Check templates in `cortex/templates/planning/`
- Review YAML schema in model docstrings
- Run integration tests: `pytest tests/integration/test_user_planning_templates.py`

---

**Wave 8 Stage 4 Deliverable** | Released 2026-02-12
