# 🎯 Shared Orchestrator Infrastructure

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Copyright © 2026 Asif Hussain. All rights reserved.**

---

## 📖 Overview

Unified infrastructure for CORTEX orchestrators providing:
- **Progress Tracking** - JSON-based state management for epic/feature plans
- **HTML Viewer Generation** - Glassmorphism-compliant plan viewers with auto-refresh
- **Dependency Resolution** - Graph-based topological sorting and cycle detection
- **Validation Pipelines** - Rule-based validation with severity levels
- **Phase Management** - State machine for phase lifecycle transitions

**Used By:** Planning v5, ADO v2, Future Orchestrators

---

## 🚀 Quick Start

```python
from src.orchestrators.shared import (
    ProgressTracker,
    HTMLViewerGenerator,
    DependencyResolver,
    ValidationPipeline,
    PhaseManager
)

# Initialize progress tracker
tracker = ProgressTracker(
    Path("plan/tracking/progress-tracker.json"),
    plan_type="feature"
)

# Generate HTML viewer
config = ViewerConfig(
    mode=ViewerMode.FEATURE,
    plan_name="My Feature",
    plan_id="my-feature",
    output_path=Path("my-feature-plan-viewer.html"),
    tracking_json_path="tracking/progress-tracker.json"
)
viewer = HTMLViewerGenerator(config)
viewer.save()
```

---

## 📦 Modules

### 1. Progress Tracker (`progress_tracker.py`)

**Classes:**
- `ProgressState` - Enum of progress states (not-started, in-progress, completed, etc.)
- `PhaseProgress` - Progress data for a single phase
- `PlanProgress` - Progress data for entire plan (epic or feature)
- `ProgressTracker` - Main tracker with JSON persistence

**Key Features:**
- Automatic percentage calculation
- Dependency validation
- Epic/feature mode support
- ASCII progress bars
- Child plan aggregation (epic mode)

**Example:**
```python
tracker = ProgressTracker(json_path, "feature")
tracker.add_phase(PhaseProgress(0, "Discovery", ...))
tracker.update_phase(0, status=ProgressState.IN_PROGRESS, progress=50)
tracker.save()
```

---

### 2. HTML Viewer Generator (`html_viewer_generator.py`)

**Classes:**
- `ViewerMode` - Enum (EPIC, FEATURE)
- `ViewerConfig` - Configuration for viewer generation
- `HTMLViewerGenerator` - Generates glassmorphism-compliant HTML

**Key Features:**
- Epic viewer (multi-child plans)
- Feature viewer (phase timeline)
- Auto-refresh every 5s
- Modern animations (T1 subtle)
- Tailwind CSS styling
- WCAG AA compliant
- Mobile-first responsive

**Example:**
```python
config = ViewerConfig(
    mode=ViewerMode.EPIC,
    plan_name="CORTEX v5",
    plan_id="cortex-v5",
    output_path=Path("cortex-v5-plan-viewer.html"),
    tracking_json_path="tracking/epic-progress-tracker.json"
)
generator = HTMLViewerGenerator(config)
generator.save()
```

---

### 3. Dependency Resolver (`dependency_resolver.py`)

**Classes:**
- `DependencyType` - Enum (REQUIRED, OPTIONAL, PARALLEL)
- `DependencyNode` - Node in dependency graph
- `DependencyGraph` - Graph with topological sorting
- `DependencyResolver` - High-level convenience methods

**Key Features:**
- Topological sorting (execution order)
- Cycle detection (circular dependencies)
- Readiness checking (unblock phases)
- Critical path calculation
- Required/optional dependencies

**Example:**
```python
graph = DependencyResolver.create_phase_graph(phases)
order = graph.topological_sort()  # [0, 1, 2, 3]
ready = graph.get_ready_nodes({"0", "1"})  # [2]
path, duration = graph.calculate_critical_path(durations)
```

---

### 4. Validation Pipeline (`validation_pipeline.py`)

**Classes:**
- `ValidationSeverity` - Enum (ERROR, WARNING, INFO)
- `ValidationResult` - Result of single rule
- `ValidationReport` - Complete validation report
- `ValidationRule` - Base rule class
- `RequiredFieldRule` - Field presence validation
- `FormatRule` - Regex pattern matching
- `RangeRule` - Numeric range checking
- `CustomRule` - Custom validation logic
- `ValidationPipeline` - Chain multiple rules

**Key Features:**
- Severity levels (blocking vs non-blocking)
- Required field validation
- Format/regex validation
- Range validation
- Custom validators
- Detailed error reporting

**Example:**
```python
pipeline = (
    ValidationPipeline("plan")
    .add_required_field("plan_id")
    .add_format_rule("plan_id", r"^[a-z0-9-]+$", "lowercase with hyphens")
    .add_range_rule("progress", min_val=0, max_val=100)
    .add_custom_rule("valid_type", lambda d: d["type"] in ["epic", "feature"], "Invalid type")
)
report = pipeline.validate(data)
```

---

### 5. Phase Manager (`phase_manager.py`)

**Classes:**
- `PhaseState` - Enum (NOT_STARTED, IN_PROGRESS, COMPLETED, BLOCKED, FAILED, DEFERRED, SKIPPED)
- `PhaseTransition` - Enum (START, COMPLETE, FAIL, BLOCK, UNBLOCK, DEFER, SKIP, RETRY)
- `PhaseTransitionEvent` - Event log entry
- `PhaseExecution` - Execution context for phase
- `PhaseManager` - Orchestrator phase coordinator

**Key Features:**
- State machine with 7 states
- Lifecycle hooks (before/after/error/complete)
- Retry logic with max attempts
- Block/unblock/defer phases
- Progress percentage calculation
- Transition history

**Example:**
```python
manager = PhaseManager("PlanningOrchestrator")
manager.register_phase(0, "Discovery", max_retries=3)
manager.register_hook("before_phase", on_start)
manager.start_phase(0)
manager.complete_phase(0)
```

---

## 🎯 Usage Patterns

### Pattern 1: Feature Plan Workflow

```python
# 1. Initialize
tracker = ProgressTracker(Path("plan/tracking/progress-tracker.json"), "feature")
manager = PhaseManager("MyOrchestrator")

# 2. Setup phases
for i, name in enumerate(["Discovery", "Analysis", "Implementation"]):
    tracker.add_phase(PhaseProgress(i, name, estimated_hours=2))
    manager.register_phase(i, name)

# 3. Execute
for i in range(3):
    manager.start_phase(i)
    tracker.update_phase(i, status=ProgressState.IN_PROGRESS)
    
    # ... do work ...
    
    manager.complete_phase(i)
    tracker.update_phase(i, status=ProgressState.COMPLETED, progress=100)
    tracker.save()

# 4. Generate viewer
config = ViewerConfig(ViewerMode.FEATURE, "My Plan", "my-plan", ...)
HTMLViewerGenerator(config).save()
```

### Pattern 2: Epic Plan Workflow

```python
# 1. Initialize epic
epic_tracker = ProgressTracker(Path("epic/tracking/epic-progress-tracker.json"), "epic")

# 2. Track child plans
for child_folder in epic_path.glob("*-*/"):
    child_tracker = ProgressTracker(child_folder / "tracking" / "progress-tracker.json", "feature")
    epic_tracker.add_child_plan(child_tracker.progress)

# 3. Aggregate progress
total = sum(c.overall_progress for c in epic_tracker.progress.child_plans)
epic_tracker.progress.overall_progress = total // len(epic_tracker.progress.child_plans)
epic_tracker.save()

# 4. Generate epic viewer
config = ViewerConfig(ViewerMode.EPIC, "My Epic", "my-epic", ...)
HTMLViewerGenerator(config).save()
```

### Pattern 3: Dependency Management

```python
# 1. Create graph
phases = [
    {"phase_number": 0, "dependencies": []},
    {"phase_number": 1, "dependencies": [0]},
    {"phase_number": 2, "dependencies": [1]},
]
graph = DependencyResolver.create_phase_graph(phases)

# 2. Validate
is_valid, errors = graph.validate()
if not is_valid:
    raise ValueError(f"Dependency errors: {errors}")

# 3. Execute in order
order = graph.topological_sort()
completed = set()

for phase_num in order:
    is_ready, blocking = graph.nodes[phase_num].is_ready(completed)
    if not is_ready:
        print(f"Blocked by: {blocking}")
        continue
    
    # Execute phase
    completed.add(phase_num)
```

---

## 📚 Complete Examples

See `examples.py` for 7 complete examples:

1. **Feature Plan Tracking** - Basic progress tracking
2. **Epic Plan Tracking** - Multi-child plan aggregation
3. **HTML Viewer Generation** - Epic + feature viewers
4. **Dependency Resolution** - Graph operations
5. **Validation Pipeline** - Rule-based validation
6. **Phase Manager** - State transitions and hooks
7. **Complete Integration** - Full workflow example

Run examples:
```bash
python src/orchestrators/shared/examples.py
```

---

## 🧪 Testing

**Test Coverage:** TBD (Sub-Plan 00C)

```bash
# Run tests
pytest tests/orchestrators/shared/

# Run with coverage
pytest --cov=src/orchestrators/shared tests/orchestrators/shared/
```

---

## 📖 API Reference

### ProgressTracker

```python
class ProgressTracker:
    def __init__(self, tracking_file: Path, plan_type: str = "feature")
    def add_phase(self, phase: PhaseProgress) -> None
    def update_phase(self, phase_number: int, status: ProgressState = None, 
                     progress: int = None, tasks_completed: int = None) -> None
    def add_child_plan(self, child_progress: PlanProgress) -> None
    def get_phase(self, phase_number: int) -> Optional[PhaseProgress]
    def get_next_phase(self) -> Optional[PhaseProgress]
    def validate_dependencies(self, phase_number: int) -> Tuple[bool, List[str]]
    def save(self) -> None
    def get_progress_bar(self, width: int = 10) -> str
    def get_summary(self) -> Dict[str, Any]
```

### HTMLViewerGenerator

```python
class HTMLViewerGenerator:
    def __init__(self, config: ViewerConfig)
    def generate(self) -> str  # Returns HTML content
    def save(self) -> None  # Writes to config.output_path
```

### DependencyResolver

```python
class DependencyResolver:
    @staticmethod
    def create_phase_graph(phases: List[Dict]) -> DependencyGraph
    
    @staticmethod
    def create_plan_graph(plans: List[Dict]) -> DependencyGraph
    
    @staticmethod
    def get_execution_order(items: List[Dict]) -> List[str]

class DependencyGraph:
    def add_node(self, node: DependencyNode) -> None
    def add_dependency(self, from_node: str, to_node: str, 
                       dep_type: DependencyType = REQUIRED) -> None
    def detect_cycles(self) -> List[List[str]]
    def topological_sort(self) -> List[str]
    def get_ready_nodes(self, completed_nodes: Set[str]) -> List[str]
    def get_blocking_nodes(self, node_id: str, completed: Set[str]) -> List[str]
    def calculate_critical_path(self, durations: Dict[str, float]) -> Tuple[List[str], float]
    def validate(self) -> Tuple[bool, List[str]]
```

### ValidationPipeline

```python
class ValidationPipeline:
    def __init__(self, name: str = "validation")
    def add_rule(self, rule: ValidationRule) -> 'ValidationPipeline'
    def add_required_field(self, field: str, severity: ValidationSeverity = ERROR) -> 'ValidationPipeline'
    def add_format_rule(self, field: str, pattern: str, description: str) -> 'ValidationPipeline'
    def add_range_rule(self, field: str, min_val: float = None, max_val: float = None) -> 'ValidationPipeline'
    def add_custom_rule(self, name: str, validator: Callable, message: str, severity: ValidationSeverity = ERROR) -> 'ValidationPipeline'
    def validate(self, data: Dict[str, Any]) -> ValidationReport
    def validate_batch(self, items: List[Dict[str, Any]]) -> List[ValidationReport]
```

### PhaseManager

```python
class PhaseManager:
    def __init__(self, orchestrator_name: str)
    def register_phase(self, phase_number: int, phase_name: str, max_retries: int = 3) -> None
    def get_phase(self, phase_number: int) -> Optional[PhaseExecution]
    def start_phase(self, phase_number: int, reason: str = None) -> bool
    def complete_phase(self, phase_number: int, reason: str = None, **metadata) -> bool
    def fail_phase(self, phase_number: int, error: str, **metadata) -> bool
    def retry_phase(self, phase_number: int) -> bool
    def block_phase(self, phase_number: int, reason: str) -> bool
    def unblock_phase(self, phase_number: int) -> bool
    def defer_phase(self, phase_number: int, reason: str) -> bool
    def skip_phase(self, phase_number: int, reason: str) -> bool
    def get_next_phase(self) -> Optional[PhaseExecution]
    def is_all_complete(self) -> bool
    def get_progress_percentage(self) -> int
    def register_hook(self, hook_type: str, callback: Callable) -> None
    def get_summary(self) -> Dict[str, Any]
```

---

## 🎯 Integration Guide

### For Planning Orchestrator v5

**Replace:**
```python
# OLD: Custom progress tracking
self.current_phase = 0
self.phase_status = {}
def update_progress(self, phase_num, status):
    self.phase_status[phase_num] = status
```

**With:**
```python
# NEW: Shared progress tracker
from src.orchestrators.shared import ProgressTracker, ProgressState
self.tracker = ProgressTracker(self.tracking_file, "feature")
self.tracker.update_phase(0, status=ProgressState.IN_PROGRESS)
```

### For ADO Orchestrator v2

**Replace:**
```python
# OLD: Custom work item tracking
self.story_points_completed = 0
self.total_story_points = 0
```

**With:**
```python
# NEW: Shared progress tracker
self.sprint_tracker = ProgressTracker(self.sprint_tracking_file, "feature")
# Track work items as phases
```

---

## 📝 License

Copyright © 2026 Asif Hussain. All rights reserved.

---

## 🔗 Related Documentation

- [CORTEX Master Orchestrator](../../.github/prompts/CORTEX.prompt.md)
- [Planning System v5 Manifest](../../cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml)
- [ADO Orchestrator v2 Manifest](../../cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml)
- [Glassmorphism Design Standard](../../cortex-brain/documents/standards/glassmorphism-design-standard.md)
- [CORTEX-5.0 Master Plan](../../cortex-brain/documents/planning/active/CORTEX-5.0/00-MASTER-REMEDIATION-PLAN.md)
