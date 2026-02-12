# Planning Orchestrator User Guide

**Version:** 1.0.0  
**Last Updated:** 2024-02-01  
**Author:** CORTEX Team

---

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Getting Started](#getting-started)
4. [Wave Planning Patterns](#wave-planning-patterns)
5. [ROI-Based Prioritization](#roi-based-prioritization)
6. [Dependency Management](#dependency-management)
7. [Parallel Execution](#parallel-execution)
8. [Template Library](#template-library)
9. [Best Practices](#best-practices)
10. [Advanced Topics](#advanced-topics)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The **Planning Orchestrator** is a sophisticated project management system within CORTEX that automates:

- **Phase decomposition** into executable units
- **ROI-based prioritization** using 5-dimensional scoring
- **Dependency resolution** with cycle detection
- **Parallel execution planning** to minimize calendar time
- **Progress tracking** with audit trails

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Automated Prioritization** | ROI scoring eliminates manual ranking debates |
| **Dependency Safety** | Topological sort prevents broken builds |
| **Faster Delivery** | Parallelism reduces calendar time by 40-60% |
| **Audit Trail** | Every phase tracked with AC markers |
| **Reusability** | Templates enable pattern reuse |

---

## Core Concepts

### Hierarchical Structure

```
INITIATIVE (I-)
  └─ PHASE (P-)
      └─ STAGE (S-)
          └─ TASK (T-)
```

**INITIATIVE:** 6-12 month strategic goal (e.g., "Migrate to Microservices")  
**PHASE:** 2-4 week milestone (e.g., "Implement Authentication Service")  
**STAGE:** 2-5 day work unit (e.g., "Build JWT Token Generation")  
**TASK:** 2-8 hour atomic work (e.g., "Write unit tests for token expiry")

### Wave-Based Execution

A **Wave** is a coordinated group of phases executed as a unit:

```yaml
wave:
  id: "wave-backend-001"
  name: "Backend API Development"
  phases:
    - phase-auth
    - phase-database
    - phase-caching
```

Waves enable:
- Batched execution with shared context
- Milestone-based releases
- Team coordination boundaries

### Execution Strategies

The Planning Orchestrator uses three strategy patterns (extracted in Wave 8 Stage 1):

1. **PhaseExecutionStrategy:** Execute individual phases with validation
2. **WaveOrchestrationStrategy:** Coordinate multi-phase waves with dependencies
3. **TrackParallelizationStrategy:** Parallelize independent tracks for speedup

---

## Getting Started

### Installation

```bash
# CORTEX is pre-installed with MCP
# Verify planning orchestrator available
python -m cortex.mcp.client tools | grep cortex_plan
```

### Your First Wave

Create a simple 3-phase wave:

```yaml
# my-first-wave.yaml
wave:
  id: "wave-first"
  name: "My First Feature"
  
  phases:
    - id: "phase-1"
      name: "Design"
      effort_hours: 4
      depends_on: []
      
      roi_metrics:
        architectural_impact: 0.6
        efficiency_gain: 0.5
        accuracy_improvement: 0.7
        effort_cost: 0.2
        blocking_severity: 0.9
      
      exit_criteria:
        - "Design document created"
        - "API contracts defined"
    
    - id: "phase-2"
      name: "Implementation"
      effort_hours: 8
      depends_on: ["phase-1"]
      
      roi_metrics:
        architectural_impact: 0.7
        efficiency_gain: 0.8
        accuracy_improvement: 0.9
        effort_cost: 0.5
        blocking_severity: 0.7
      
      exit_criteria:
        - "Tests passing"
        - "Code reviewed"
    
    - id: "phase-3"
      name: "Deployment"
      effort_hours: 2
      depends_on: ["phase-2"]
      
      roi_metrics:
        architectural_impact: 0.4
        efficiency_gain: 0.9
        accuracy_improvement: 0.8
        effort_cost: 0.1
        blocking_severity: 0.0
      
      exit_criteria:
        - "Deployed to production"
        - "Monitoring active"
```

### Execute the Wave

```python
from cortex.orchestrators.planning import PlanningOrchestrator

# Initialize orchestrator
orchestrator = PlanningOrchestrator()

# Load wave configuration
with open("my-first-wave.yaml") as f:
    wave_config = yaml.safe_load(f)

# Execute
result = orchestrator.execute_wave(wave_config)

if result.success:
    print(f"✅ Wave completed: {result.phases_completed}/{result.total_phases}")
else:
    print(f"❌ Wave failed: {result.error_message}")
```

---

## Wave Planning Patterns

### Pattern 1: Linear Dependency Chain

**Use Case:** Simple features with clear sequential steps

```yaml
# A → B → C → D
phases:
  - id: "A"
    depends_on: []
  - id: "B"
    depends_on: ["A"]
  - id: "C"
    depends_on: ["B"]
  - id: "D"
    depends_on: ["C"]
```

**Pros:** Simple, predictable  
**Cons:** Slow (no parallelism)  
**Calendar Time:** Sum of all phase durations

### Pattern 2: Parallel Branches

**Use Case:** Independent work streams (e.g., backend + frontend)

```yaml
# A → B → D
#   ↘ C ↗
phases:
  - id: "A"
    depends_on: []
  - id: "B"
    depends_on: ["A"]
  - id: "C"
    depends_on: ["A"]
  - id: "D"
    depends_on: ["B", "C"]
```

**Pros:** 40-50% faster with 2 parallel tracks  
**Cons:** Requires coordination at merge point D  
**Calendar Time:** max(path(A→B), path(A→C)) + D

### Pattern 3: Diamond Pattern

**Use Case:** Shared foundation + specialized modules + integration

```yaml
#     A
#   ↙  ↓  ↘
#  B   C   D
#   ↘  ↓  ↙
#     E
phases:
  - id: "A"
    name: "Foundation"
    depends_on: []
  
  - id: "B"
    name: "Module 1"
    depends_on: ["A"]
  
  - id: "C"
    name: "Module 2"
    depends_on: ["A"]
  
  - id: "D"
    name: "Module 3"
    depends_on: ["A"]
  
  - id: "E"
    name: "Integration"
    depends_on: ["B", "C", "D"]
```

**Pros:** Maximum parallelism (3x speedup)  
**Cons:** Complex coordination, merge conflicts  
**Calendar Time:** A + max(B, C, D) + E

### Pattern 4: Multi-Track Complex

**Use Case:** Large projects with multiple teams

See `cortex/templates/planning/complex_wave.yaml` for full example with:
- 3 tracks (Backend, Frontend, Infrastructure)
- 20 phases
- 40-60% calendar time reduction

---

## ROI-Based Prioritization

### The 5-Dimensional ROI Formula

```python
ROI = (arch_impact * 0.35) + 
      (efficiency * 0.25) + 
      (accuracy * 0.20) + 
      ((1 - effort) * 0.15) + 
      (blocking * 0.05)
```

### Dimension Descriptions

| Dimension | Weight | Description | Example High Value |
|-----------|--------|-------------|---------------------|
| **Architectural Impact** | 35% | Long-term system quality impact | Refactoring to microservices |
| **Efficiency Gain** | 25% | Performance or productivity improvement | Caching layer (10x speedup) |
| **Accuracy Improvement** | 20% | Correctness or reliability increase | Add type hints (catch bugs) |
| **Effort Cost** | 15% | Time/complexity required (inverted) | 2-hour task vs 2-week task |
| **Blocking Severity** | 5% | How many phases are blocked | Authentication (blocks all features) |

### Priority Tiers

ROI scores map to tiers:

```
≥ 0.70: HIGH      → Do immediately
0.50-0.69: MEDIUM → Schedule soon
0.35-0.49: LOW    → Do when resources available
< 0.35: DEFER     → Consider not doing
```

### Customizing Weights

For performance-critical projects, boost efficiency:

```python
from cortex.orchestrators.planning.models import ROIWeights, ROICompositeScorer

# Custom weights for performance project
weights = ROIWeights(
    architectural_impact=0.20,  # Lower priority
    efficiency_gain=0.50,       # PRIMARY FOCUS
    accuracy_improvement=0.15,
    effort_cost=0.10,
    blocking_severity=0.05
)

scorer = ROICompositeScorer(weights=weights)
```

---

## Dependency Management

### Defining Dependencies

```yaml
phases:
  - id: "phase-auth"
    depends_on: []  # No dependencies
  
  - id: "phase-api"
    depends_on: ["phase-auth"]  # Single dependency
  
  - id: "phase-integration"
    depends_on: ["phase-auth", "phase-api", "phase-database"]  # Multiple
```

### Cycle Detection

The dependency resolver automatically detects cycles:

```yaml
# ❌ INVALID: Circular dependency
phases:
  - id: "A"
    depends_on: ["B"]
  - id: "B"
    depends_on: ["C"]
  - id: "C"
    depends_on: ["A"]  # Creates cycle: A→B→C→A
```

**Error Output:**
```
ResolutionStatus.CIRCULAR_DEPENDENCY
circular_path: ["A", "B", "C", "A"]
```

### Missing Dependency Detection

```yaml
# ❌ INVALID: phase-unknown doesn't exist
phases:
  - id: "phase-api"
    depends_on: ["phase-unknown"]
```

**Error Output:**
```
ResolutionStatus.MISSING_DEPENDENCY
missing_dependencies: {"phase-api": ["phase-unknown"]}
```

### Transitive Dependencies

Get full dependency chain:

```python
from cortex.orchestrators.planning.models import DependencyResolver, DependencyGraph

graph = DependencyGraph.from_dict({
    "A": set(),
    "B": {"A"},
    "C": {"B"},
    "D": {"C"}
})

resolver = DependencyResolver()
transitive = resolver.get_transitive_dependencies("D", graph)

# Result: {"C", "B", "A"}
```

---

## Parallel Execution

### Execution Levels

The parallelism calculator groups phases into levels:

```python
from cortex.orchestrators.planning.models import ParallelismCalculator

# Example: Diamond pattern
graph = DependencyGraph.from_dict({
    "A": set(),
    "B": {"A"},
    "C": {"A"},
    "D": {"A"},
    "E": {"B", "C", "D"}
})

calculator = ParallelismCalculator()
plan = calculator.calculate(graph)

# Result:
# Level 0: ["A"]           (1 phase)
# Level 1: ["B", "C", "D"] (3 phases in parallel)
# Level 2: ["E"]           (1 phase)
```

### Speedup Potential

```python
# Sequential execution time
sequential_time = sum(phase_durations)  # 100 hours

# Parallel execution time
parallel_time = plan.estimate_execution_time(phase_durations)  # 60 hours

# Speedup
speedup = plan.speedup_potential  # 1.67x (67% faster)
```

### Resource Constraints

Limit parallelism based on team capacity:

```yaml
wave:
  max_parallel_tracks: 2  # Only 2 engineers available
  
phases:
  - id: "B"
    depends_on: ["A"]
    resource_pool: "backend_team"
    resource_count: 1
  
  - id: "C"
    depends_on: ["A"]
    resource_pool: "backend_team"
    resource_count: 1
  
  # B and C can run in parallel (2 ≤ max_parallel_tracks)
```

---

## Template Library

### simple_wave.yaml

**Use Case:** Small features (2-5 days)  
**Phases:** 5 (linear)  
**Pattern:** A → B → C → D → E  
**Best For:** Bug fixes, minor enhancements

```bash
cp cortex/templates/planning/simple_wave.yaml my-feature.yaml
# Edit phase names and metrics
```

### complex_wave.yaml

**Use Case:** Large features (4-8 weeks)  
**Phases:** 20 (multi-track)  
**Pattern:** 3 parallel tracks + merge points  
**Best For:** New services, major refactoring

```bash
cp cortex/templates/planning/complex_wave.yaml my-service.yaml
# Adapt tracks to your team structure
```

### cortex_50_wave.yaml

**Use Case:** Multi-year initiatives (12-18 months)  
**Phases:** 50 (organized into 10 epics)  
**Pattern:** Mega-project with milestone releases  
**Best For:** Platform development, system rewrites

```bash
# Use as reference, extract relevant epics
cat cortex/templates/planning/cortex_50_wave.yaml
```

---

## Best Practices

### 1. Right-Size Phases

❌ **Too Large:**
```yaml
- name: "Build entire backend"
  effort_hours: 200
```

✅ **Properly Sized:**
```yaml
- name: "Implement authentication endpoint"
  effort_hours: 8
```

**Rule of Thumb:** 4-12 hours per phase, 3-7 phases per wave

### 2. Use Clear Exit Criteria

❌ **Vague:**
```yaml
exit_criteria:
  - "Feature works"
```

✅ **Specific:**
```yaml
exit_criteria:
  - "Unit tests ≥95% coverage"
  - "Integration tests passing"
  - "Code review approved"
  - "Documentation complete"
```

### 3. Honest Effort Estimates

Include:
- Implementation time
- Testing time
- Code review time
- Documentation time
- Buffer for unknowns (20%)

```yaml
# 6h implementation + 2h tests + 1h review + 1h docs + 20% buffer
effort_hours: 12
```

### 4. Model Dependencies Accurately

Test your dependency graph:

```python
# Visualize dependencies before execution
from cortex.orchestrators.planning.models import DependencyResolver

resolver = DependencyResolver()
result = resolver.resolve(your_graph)

if not result.is_success:
    print(f"Graph invalid: {result.status}")
    print(f"Circular path: {result.circular_path}")
```

### 5. Monitor ROI Scores

Phases with HIGH priority (ROI ≥ 0.70) should be:
- Scheduled first
- Allocated best resources
- Reviewed more carefully

Phases with DEFER priority (ROI < 0.35) should be:
- Reconsidered (do you really need this?)
- Delegated or outsourced
- Simplified or removed

---

## Advanced Topics

### Custom ROI Weights

Different project types need different weights:

```python
# Performance-Critical System
perf_weights = ROIWeights(
    architectural_impact=0.15,
    efficiency_gain=0.55,      # FOCUS HERE
    accuracy_improvement=0.15,
    effort_cost=0.10,
    blocking_severity=0.05
)

# High-Reliability System (medical, aerospace)
reliability_weights = ROIWeights(
    architectural_impact=0.20,
    efficiency_gain=0.15,
    accuracy_improvement=0.50,  # FOCUS HERE
    effort_cost=0.10,
    blocking_severity=0.05
)

# Rapid Prototype
prototype_weights = ROIWeights(
    architectural_impact=0.10,  # Don't over-engineer
    efficiency_gain=0.30,
    accuracy_improvement=0.20,
    effort_cost=0.35,           # Favor quick wins
    blocking_severity=0.05
)
```

### Multi-Wave Orchestration

For large initiatives, chain waves:

```python
waves = [
    "wave-01-foundation.yaml",
    "wave-02-core-features.yaml",
    "wave-03-integration.yaml",
    "wave-04-deployment.yaml"
]

for wave_file in waves:
    with open(wave_file) as f:
        wave_config = yaml.safe_load(f)
    
    result = orchestrator.execute_wave(wave_config)
    
    if not result.success:
        print(f"❌ Wave {wave_file} failed, stopping")
        break
    
    # Checkpoint between waves
    orchestrator.checkpoint(wave_file)
```

### Dashboard Integration

Track progress visually:

```python
from cortex.orchestrators.planning import PlanningOrchestrator, DashboardGenerator

orchestrator = PlanningOrchestrator()
dashboard_gen = DashboardGenerator()

# Execute wave
result = orchestrator.execute_wave(wave_config)

# Generate dashboard
dashboard = dashboard_gen.generate(
    wave_id=wave_config["wave"]["id"],
    phases_completed=result.phases_completed,
    phases_total=result.total_phases,
    execution_time_hours=result.execution_time_hours
)

# View in browser
dashboard.serve(port=8080)
```

### Git Blacklist Integration

Wave 8 Stage 2 added git blacklist enforcement:

```yaml
# .cortex/registry-blacklist.yaml
blacklist:
  paths:
    - "cortex-registry/**"  # Never commit directly
  
  enforcement:
    mode: "blocking"
    pre_commit_hook: true
```

Pre-commit hook validates:
- No registry files in staging
- No accidental commits to blacklisted paths

---

## Troubleshooting

### Issue: Circular Dependency Detected

**Symptom:**
```
ResolutionStatus.CIRCULAR_DEPENDENCY
circular_path: ["phase-A", "phase-B", "phase-C", "phase-A"]
```

**Solution:**
1. Visualize dependency graph
2. Identify which dependency to remove
3. Usually the "weakest" dependency (lowest coupling)

**Example Fix:**
```yaml
# Before (circular)
- id: "phase-A"
  depends_on: ["phase-C"]
- id: "phase-B"
  depends_on: ["phase-A"]
- id: "phase-C"
  depends_on: ["phase-B"]

# After (remove A→C)
- id: "phase-A"
  depends_on: []  # FIX: Remove dependency on C
- id: "phase-B"
  depends_on: ["phase-A"]
- id: "phase-C"
  depends_on: ["phase-B"]
```

### Issue: Low Speedup Despite Parallelism

**Symptom:**
```
speedup_potential: 1.1x  # Expected 2x with 2 tracks
```

**Causes:**
1. **Long critical path:** One phase dominates execution time
2. **Poor phase distribution:** Unbalanced track loads
3. **Resource constraints:** Not enough parallel capacity

**Solution:**
```python
# Analyze critical path
plan = calculator.calculate(graph)
critical_path = plan.get_critical_path()

print(f"Critical path: {critical_path}")
print(f"Critical path duration: {sum(durations[p] for p in critical_path)}h")

# Break up long phases on critical path
```

### Issue: ROI Scores All Similar

**Symptom:**
```
Phase A: ROI 0.52
Phase B: ROI 0.51
Phase C: ROI 0.53
```

**Cause:** Metrics not differentiated enough

**Solution:** Use full 0.0-1.0 range

```yaml
# Be more opinionated
roi_metrics:
  architectural_impact: 0.9  # Critical foundation
  efficiency_gain: 0.3       # Modest improvement
  accuracy_improvement: 1.0  # Perfect reliability needed
  effort_cost: 0.1          # Very quick
  blocking_severity: 0.95    # Blocks everything
```

### Issue: Wave Execution Fails Mid-Way

**Symptom:**
```
Phase 3 of 7 failed: Tests not passing
```

**Recovery:**

```python
# Resume from checkpoint
result = orchestrator.execute_wave(
    wave_config,
    resume_from="phase-3",  # Skip completed phases
    force_rerun=False       # Don't re-run successful phases
)
```

---

## API Reference

### ROICompositeScorer

```python
from cortex.orchestrators.planning.models import (
    ROICompositeScorer,
    PhaseMetrics,
    ROIWeights,
    PriorityTier
)

# Initialize scorer
scorer = ROICompositeScorer(weights=None)  # Use defaults

# Calculate ROI
metrics = PhaseMetrics(
    architectural_impact=0.8,
    efficiency_gain=0.6,
    accuracy_improvement=0.7,
    effort_cost=0.4,
    blocking_severity=0.5
)

score = scorer.calculate(metrics)  # 0.0-1.0
tier = scorer.get_priority_tier(metrics)  # HIGH/MEDIUM/LOW/DEFER
```

### DependencyResolver

```python
from cortex.orchestrators.planning.models import (
    DependencyResolver,
    DependencyGraph,
    ResolutionStatus
)

# Create graph
graph = DependencyGraph.from_dict({
    "A": set(),
    "B": {"A"},
    "C": {"A", "B"}
})

# Resolve execution order
resolver = DependencyResolver()
result = resolver.resolve(graph)

if result.is_success:
    print(f"Execution order: {result.execution_order}")  # ["A", "B", "C"]
else:
    print(f"Resolution failed: {result.status}")
    if result.status == ResolutionStatus.CIRCULAR_DEPENDENCY:
        print(f"Circular path: {result.circular_path}")
```

### ParallelismCalculator

```python
from cortex.orchestrators.planning.models import ParallelismCalculator

calculator = ParallelismCalculator()

# Calculate execution plan
plan = calculator.calculate(graph)

# Analyze parallelism
for level in plan.execution_levels:
    print(f"Level {level.level_number}: {level.phases} (max {level.max_parallelism} parallel)")

# Estimate time savings
phase_durations = {"A": 8, "B": 6, "C": 4, "D": 10}
parallel_time = plan.estimate_execution_time(phase_durations)
sequential_time = sum(phase_durations.values())

print(f"Sequential: {sequential_time}h")
print(f"Parallel: {parallel_time}h")
print(f"Speedup: {plan.speedup_potential:.2f}x")
```

---

## Glossary

| Term | Definition |
|------|------------|
| **Wave** | Coordinated group of phases executed as a unit |
| **Phase** | 2-4 week milestone with clear deliverables |
| **Stage** | 2-5 day work unit within a phase |
| **Task** | 2-8 hour atomic work item |
| **ROI Score** | 0.0-1.0 value representing phase priority |
| **Dependency Graph** | DAG representing phase execution order |
| **Execution Level** | Group of phases that can run in parallel |
| **Critical Path** | Longest sequential path through dependency graph |
| **Speedup Potential** | Ratio of sequential to parallel execution time |
| **AC Marker** | Audit trail marker (AC_START, AC_COMPLETE) |

---

## Additional Resources

- **Code Examples:** `examples/planning/` directory
- **Templates:** `cortex/templates/planning/` directory
- **API Docs:** `docs/api/planning-orchestrator.md`
- **Video Tutorial:** [Coming Soon]
- **Community Forum:** [Coming Soon]

---

**Questions?** Open an issue or contact the CORTEX team.

**Contributing:** See `CONTRIBUTING.md` for guidelines on improving the Planning Orchestrator.
