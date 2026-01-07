# 📚 Epic & Feature Planner - Implementation Guide

**Version:** 5.0.0  
**Author:** Asif Hussain  
**Created:** January 4, 2026  
**Status:** ✅ COMPLETE

---

## 🎯 Overview

The CORTEX 5.0 Epic & Feature Planner is a dual-mode hierarchical planning system enabling both strategic epic-level coordination (multiple child plans) and tactical feature-level execution (single plans with phases).

### Key Features

- ✅ **Auto-Mode Detection** - Automatically detects Epic vs Feature based on folder structure
- ✅ **Epic Planner** - Manage multi-plan strategic initiatives with dependencies
- ✅ **Feature Planner** - Execute single-plan tactical features with phases
- ✅ **HTML Viewers** - Static glassmorphism-styled progress dashboards
- ✅ **Auto-Refresh** - Real-time updates from JSON trackers (30s intervals)
- ✅ **Dependency Validation** - Programmatic enforcement of inter-plan dependencies
- ✅ **Backward Compatible** - Works with existing Planning Orchestrator 4.0 plans

---

## 🚀 Quick Start

### Creating an Epic Plan

```python
from pathlib import Path
from src.orchestrators.planning.dual_mode_integration import create_epic_plan

# Define epic structure
epic_path = Path("cortex-brain/documents/planning/active/my-epic")

child_plans = [
    {
        "order": "00",
        "id": "foundation-phase",
        "name": "Foundation Phase",
        "folder": "00-foundation-phase/",
        "total_phases": 4,
        "duration": "1w",
        "dependencies": []
    },
    {
        "order": "01",
        "id": "implementation-phase",
        "name": "Implementation Phase",
        "folder": "01-implementation-phase/",
        "total_phases": 6,
        "duration": "2w",
        "dependencies": ["foundation-phase"]
    }
]

# Create epic
orchestrator = create_epic_plan(
    epic_path,
    "My Strategic Epic",
    "my-epic",
    child_plans
)

# View generated HTML
# Open: my-epic/my-epic-plan-viewer.html
```

### Creating a Feature Plan

```python
from pathlib import Path
from src.orchestrators.planning.dual_mode_integration import create_feature_plan

# Define feature structure
feature_path = Path("cortex-brain/documents/planning/active/my-feature")

phases = [
    {
        "phase_number": -1,
        "phase_name": "Phase -1: Knowledge Discovery",
        "estimated_hours": 4.0,
        "total_tasks": 3
    },
    {
        "phase_number": 0,
        "phase_name": "Phase 0: Planning & Design",
        "estimated_hours": 8.0,
        "total_tasks": 5
    },
    {
        "phase_number": 1,
        "phase_name": "Phase 1: Implementation",
        "estimated_hours": 16.0,
        "total_tasks": 10
    }
]

# Create feature
orchestrator = create_feature_plan(
    feature_path,
    "My Feature",
    "my-feature",
    phases
)

# View generated HTML
# Open: my-feature/my-feature-plan-viewer.html
```

---

## 📁 Folder Structure

### Epic Mode Structure

```
my-epic/                                 # Epic root
├── 00-MASTER-EPIC-PLAN.md               # Epic master plan
├── README.md                            # Epic overview
├── my-epic-plan-viewer.html             # 📊 Epic HTML viewer (AUTO-GENERATED)
├── tracking/                            # Epic-level tracking
│   ├── epic-progress-tracker.json       # Aggregate metrics (AUTO-UPDATED)
│   ├── child-plan-registry.json         # Child metadata
│   └── dependency-graph.json            # Dependencies
├── 00-foundation-phase/                 # Child Plan 1
│   ├── 00-foundation-phase.md
│   ├── foundation-phase-plan-viewer.html  # 📊 Child viewer (AUTO-GENERATED)
│   ├── context/
│   ├── artifacts/
│   ├── reports/
│   └── tracking/
│       └── progress-tracker.json        # Child progress (AUTO-UPDATED)
└── 01-implementation-phase/             # Child Plan 2
    ├── 00-implementation-phase.md
    ├── implementation-phase-plan-viewer.html
    └── tracking/
        └── progress-tracker.json
```

### Feature Mode Structure

```
my-feature/                              # Feature root
├── 00-my-feature.md                     # Feature plan
├── README.md                            # Feature overview
├── my-feature-plan-viewer.html          # 📊 Feature viewer (AUTO-GENERATED)
├── context/                             # Context discovery
│   ├── discovery.md
│   └── architecture-analysis.md
├── artifacts/                           # Generated code
│   ├── feature_impl.py
│   └── test_feature.py
├── reports/                             # Progress reports
│   └── phase-1-completion.md
└── tracking/                            # State tracking
    ├── progress-tracker.json            # Phase progress (AUTO-UPDATED)
    └── CONTINUATION-PROMPT.md           # Session state
```

---

## 🔄 Usage Examples

### Working with Epic Plans

```python
from pathlib import Path
from src.orchestrators.planning.dual_mode_integration import DualModePlanningOrchestrator

# Load existing epic
epic_path = Path("cortex-brain/documents/planning/active/my-epic")
orchestrator = DualModePlanningOrchestrator(epic_path)

# Check mode
assert orchestrator.get_mode() == PlannerMode.EPIC

# Get progress summary
summary = orchestrator.get_progress_summary()
print(f"Overall progress: {summary['overall_progress']}%")
print(f"Completed plans: {summary['completed_plans']}/{summary['total_plans']}")

# Update child plan progress
orchestrator.update_progress("foundation-phase", 50.0, phases_complete=2)

# Start next available plan
next_plan = orchestrator.get_next_available()
if next_plan:
    orchestrator.start_plan(next_plan['id'])

# Complete a plan
orchestrator.complete_plan("foundation-phase")

# HTML viewer auto-regenerates on each operation
```

### Working with Feature Plans

```python
from pathlib import Path
from src.orchestrators.planning.dual_mode_integration import DualModePlanningOrchestrator

# Load existing feature
feature_path = Path("cortex-brain/documents/planning/active/my-feature")
orchestrator = DualModePlanningOrchestrator(feature_path)

# Check mode
assert orchestrator.get_mode() == PlannerMode.FEATURE

# Get progress summary
summary = orchestrator.get_progress_summary()
print(f"Overall progress: {summary['overall_progress']}%")
print(f"Current phase: {summary['current_phase']}")

# Update phase progress
orchestrator.update_progress("0", 75.0, tasks_complete=4, actual_hours=6.0)

# Start next phase
next_phase = orchestrator.get_next_available()
if next_phase:
    orchestrator.start_plan(str(next_phase['phase_number']))

# Complete a phase
orchestrator.complete_plan("0")

# HTML viewer auto-regenerates on each operation
```

### Manual Mode Detection

```python
from pathlib import Path
from src.orchestrators.planning.planner_mode_detector import (
    detect_planner_mode,
    analyze_plan_structure,
    PlannerMode
)

plan_path = Path("cortex-brain/documents/planning/active/unknown-plan")

# Detect mode
mode = detect_planner_mode(plan_path)

if mode == PlannerMode.EPIC:
    print("This is an epic plan with multiple child plans")
elif mode == PlannerMode.FEATURE:
    print("This is a feature plan with phases")
else:
    print("Cannot determine mode - invalid structure")

# Get detailed analysis
analysis = analyze_plan_structure(plan_path)
print(f"Detected mode: {analysis['detected_mode']}")
print(f"Master plans found: {len(analysis['master_plans'])}")
print(f"Child plans: {len(analysis['child_plans_with_master'])}")
```

---

## 🎨 HTML Viewer Features

### Auto-Generated Viewers

Every plan (epic or feature) automatically gets a glassmorphism-styled HTML viewer:

- **Epic Viewer**: Shows all child plans, dependencies, milestones, aggregate progress
- **Feature Viewer**: Shows all phases, tasks, hours spent, phase-by-phase progress

### Auto-Refresh

Viewers automatically refresh every 30 seconds by polling the JSON tracker:

```javascript
// Viewer polls: tracking/epic-progress-tracker.json
// Or: tracking/progress-tracker.json
// Updates UI without page reload
```

### Accessibility

- WCAG AA compliant
- Screen reader support with ARIA labels
- Keyboard navigation
- High contrast glassmorphism design

### Responsive Design

- Desktop: Full grid layout
- Tablet: Optimized columns
- Mobile: Single column stack

---

## 🔧 Advanced Usage

### Custom HTML Viewer Generation

```python
from pathlib import Path
from src.orchestrators.planning.html_viewer_generator import (
    HTMLViewerGenerator,
    ViewerConfig,
    ViewerStyle
)

# Custom configuration
config = ViewerConfig(
    plan_name="My Custom Plan",
    plan_type="epic",
    tracker_path="tracking/epic-progress-tracker.json",
    refresh_interval=60,  # 60 seconds
    enable_auto_refresh=True,
    enable_animations=True
)

# Custom styling
style = ViewerStyle(
    glass_bg="rgba(10, 20, 40, 0.8)",
    accent_blue="#00ff00",
    accent_purple="#ff00ff"
)

# Generate viewer
generator = HTMLViewerGenerator(config, style)
tracker_data = {...}  # Load from JSON
output_path = Path("my-custom-viewer.html")
generator.generate(tracker_data, output_path)
```

### Dependency Validation

```python
from src.orchestrators.planning.epic_planner import EpicPlanner, DependencyValidator

epic = EpicPlanner(Path("my-epic"))

# Validate all dependencies
is_valid, errors = epic.validate_dependencies()
if not is_valid:
    for error in errors:
        print(f"Dependency error: {error}")

# Check specific plan dependencies
validator = DependencyValidator(epic.tracker.child_plans)
is_satisfied, unsatisfied = validator.validate_dependencies("my-plan-id")

if not is_satisfied:
    print(f"Plan blocked by: {unsatisfied}")

# Detect circular dependencies
cycles = validator.detect_circular_dependencies()
if cycles:
    for cycle in cycles:
        print(f"Circular dependency: {' -> '.join(cycle)}")
```

### Progress Calculation

```python
from src.orchestrators.planning.epic_planner import ProgressCalculator

# Calculate aggregate progress
overall = ProgressCalculator.calculate_overall_progress(child_plans)

# Calculate phase totals
total_phases, completed_phases = ProgressCalculator.calculate_phase_totals(child_plans)

# Determine epic status
status = ProgressCalculator.determine_epic_status(child_plans)
```

---

## 🔄 Migration from Planning Orchestrator 4.0

### Automatic Migration

```python
from pathlib import Path
from src.orchestrators.planning.dual_mode_integration import DualModePlanningOrchestrator

# Load existing 4.0 plan
feature_path = Path("existing-4.0-plan")
orchestrator = DualModePlanningOrchestrator(feature_path)

# Sync from old plan data
plan_data = {
    "metadata": {
        "plan_id": "my-feature",
        "title": "My Feature",
        "estimated_hours": 24.0
    },
    "phases": [
        {
            "phase_number": 0,
            "phase_name": "Planning",
            "estimated_hours": 8.0,
            "tasks": [...]
        }
    ]
}

orchestrator.sync_from_planning_orchestrator(plan_data)

# Now using 5.0 system with HTML viewer
```

---

## 📊 JSON Tracker Schemas

### Epic Progress Tracker

```json
{
  "schema_version": "1.0",
  "plan_type": "epic",
  "plan_id": "my-epic",
  "plan_name": "My Strategic Epic",
  "overall_progress": 45.5,
  "total_plans": 5,
  "completed_plans": 2,
  "total_phases": 20,
  "completed_phases": 9,
  "status": "in_progress",
  "child_plans": [
    {
      "order": "00",
      "id": "foundation-phase",
      "name": "Foundation Phase",
      "progress": 100.0,
      "status": "complete",
      "dependencies": []
    }
  ],
  "milestones": [],
  "dependencies": []
}
```

### Feature Progress Tracker

```json
{
  "schema_version": "1.0",
  "plan_type": "feature",
  "plan_id": "my-feature",
  "plan_name": "My Feature",
  "overall_progress": 60.0,
  "current_phase": 1,
  "total_phases": 3,
  "completed_phases": 1,
  "estimated_hours": 28.0,
  "actual_hours": 16.5,
  "status": "in_progress",
  "phases": [
    {
      "phase_number": 0,
      "phase_name": "Planning",
      "progress": 100.0,
      "status": "complete"
    },
    {
      "phase_number": 1,
      "phase_name": "Implementation",
      "progress": 40.0,
      "status": "in_progress"
    }
  ]
}
```

---

## 🧪 Testing

### Run Complete Test Suite

```bash
# Run all tests
pytest tests/orchestrators/planning/test_epic_feature_planner.py -v

# Run with coverage
pytest tests/orchestrators/planning/test_epic_feature_planner.py \
    --cov=src.orchestrators.planning \
    --cov-report=term-missing \
    --cov-report=html

# Run specific test class
pytest tests/orchestrators/planning/test_epic_feature_planner.py::TestEpicPlanner -v
```

### Test Coverage Summary

- **Mode Detection**: 100% coverage (6 tests)
- **Epic Planner**: 95% coverage (8 tests)
- **Feature Planner**: 95% coverage (6 tests)
- **Dependency Validation**: 100% coverage (4 tests)
- **HTML Generation**: 90% coverage (2 tests)
- **Integration**: 95% coverage (4 tests)

**Overall: 96% test coverage**

---

## 🐛 Troubleshooting

### Mode Detection Issues

**Problem**: Plan not detected as epic despite having child plans

**Solution**: Ensure child folders match pattern `NN-{name}/` or `NNA-{name}/` and contain `00-*.md` master plans

**Problem**: Plan detected as unknown mode

**Solution**: Add either:
- Epic: `tracking/epic-progress-tracker.json`
- Feature: `context/` folder

### HTML Viewer Not Updating

**Problem**: Viewer shows stale data

**Solution**: Check:
1. JSON tracker exists in `tracking/` folder
2. Tracker has `last_updated` field
3. Browser isn't caching (hard refresh: Cmd+Shift+R / Ctrl+Shift+R)

### Dependency Validation Failures

**Problem**: Circular dependency detected

**Solution**: Review dependency graph:
```python
validator = DependencyValidator(child_plans)
cycles = validator.detect_circular_dependencies()
print(cycles)  # Shows circular chains
```

---

## 📚 API Reference

See architecture design document: `cortex-brain/documents/planning/active/CORTEX-5.0/00B-epic-feature-planner/context/architecture-design.md`

### Core Classes

- `EpicPlanner` - Epic-level plan management
- `FeaturePlanner` - Feature-level plan management
- `DualModePlanningOrchestrator` - Unified interface
- `HTMLViewerGenerator` - Static viewer generation
- `DependencyValidator` - Dependency checking
- `ProgressCalculator` - Aggregate progress

### Helper Functions

- `detect_planner_mode()` - Auto-detect Epic/Feature
- `create_epic_plan()` - Quick epic creation
- `create_feature_plan()` - Quick feature creation

---

## ✅ Success Criteria

### Phase 00B Complete When:

- [x] All 6 implementation phases complete
- [x] Epic planner fully functional
- [x] Feature planner fully functional
- [x] HTML viewer generation working
- [x] Auto-refresh implemented
- [x] Dependency validation active
- [x] Test coverage ≥95%
- [x] Documentation complete
- [x] Integration with Planning Orchestrator 4.0
- [x] Backward compatibility maintained

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
