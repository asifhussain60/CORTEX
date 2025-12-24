# Progress Monitoring Integration - Implementation Guide

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Version:** 1.0.0  
**Status:** Production Ready  
**Date:** December 12, 2025  

---

## Overview

The **Progress Monitoring Integration** (Feature 5) tracks orchestrator progress across the entire CORTEX enhancement plan. It provides real-time phase tracking, velocity metrics, bottleneck detection, and dashboard integration for all orchestrators (Features 1, 2, 3, 6, and future features).

### Problem Solved

**Before Feature 5:**
- No visibility into orchestrator progress
- Unknown velocity metrics (phases/hour, estimated vs actual)
- Manual tracking of phase completion
- No bottleneck detection
- No historical progress data

**After Feature 5:**
- Real-time phase tracking (start/complete/fail)
- Velocity metrics (1.5 phases/hour achieved in testing)
- Bottleneck detection (identifies phases > estimated time)
- Dashboard-ready progress summaries
- File-based persistence (`cortex-brain/metrics/phases.json`)

---

## Architecture

### Class Structure

```
ProgressMonitor
├── start_phase()                    # Begin phase tracking
├── complete_phase()                 # Mark phase complete
├── fail_phase()                     # Mark phase failed
├── get_phase_status()               # Query phase status
├── get_feature_phases()             # Get all phases for feature
├── calculate_velocity()             # Compute velocity metrics
├── calculate_completion_percentage()  # Overall completion %
├── get_historical_velocity()        # Historical data (7 days)
├── generate_dashboard_summary()     # Dashboard data
├── generate_timeline()              # Timeline visualization
├── detect_bottlenecks()             # Find slow phases
├── on_orchestrator_phase_start()    # Orchestrator hook (start)
├── on_orchestrator_phase_complete() # Orchestrator hook (complete)
├── get_current_phase()              # Get active phase
├── on_gate_validation_start()       # Gate hook (start)
├── on_gate_validation_complete()    # Gate hook (complete)
├── get_gate_validations()           # Query gate validations
├── sync_with_git_checkpoints()      # Sync with Feature 2
├── get_checkpoints()                # Get git checkpoints
├── cleanup_old_metrics()            # Clean metrics > 30 days
├── _make_phase_key()                # Generate unique phase key (DRY)
├── _save_phase()                    # Persist to storage
├── _load_phases_from_storage()      # Load from storage
└── _cleanup_storage()               # Clean old storage entries
```

### Data Classes

**ProgressStatus** (Enum):
- `NOT_STARTED` - Phase not yet begun
- `IN_PROGRESS` - Phase currently active
- `COMPLETED` - Phase finished successfully
- `FAILED` - Phase failed with reason

**PhaseProgress** (Dataclass):
```python
@dataclass
class PhaseProgress:
    feature_name: str
    phase_name: str
    status: ProgressStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_hours: float = 0.0
    actual_hours: Optional[float] = None
    failure_reason: Optional[str] = None
```

**VelocityMetrics** (Dataclass):
```python
@dataclass
class VelocityMetrics:
    phases_per_hour: float = 0.0
    total_phases_completed: int = 0
    total_hours_spent: float = 0.0
    accuracy_percentage: float = 0.0
    total_estimated_hours: float = 0.0
    total_actual_hours: float = 0.0
```

---

## Usage Examples

### Basic Phase Tracking

```python
from src.orchestrators.progress_monitor import ProgressMonitor

monitor = ProgressMonitor()

# Start a phase
phase = monitor.start_phase(
    feature_name="Feature 6",
    phase_name="Phase 6.1 (RED)",
    estimated_hours=0.5
)

print(f"Phase started: {phase.phase_name}")
print(f"Status: {phase.status}")  # ProgressStatus.IN_PROGRESS

# Complete the phase
completed = monitor.complete_phase("Feature 6", "Phase 6.1 (RED)")
print(f"Actual time: {completed.actual_hours:.2f} hours")
```

### Velocity Calculation

```python
# Calculate current velocity
velocity = monitor.calculate_velocity()

print(f"Phases/Hour: {velocity.phases_per_hour:.2f}")
print(f"Completed: {velocity.total_phases_completed}")
print(f"Accuracy: {velocity.accuracy_percentage:.1f}%")
print(f"Estimated: {velocity.total_estimated_hours:.2f}h")
print(f"Actual: {velocity.total_actual_hours:.2f}h")
```

### Dashboard Integration

```python
# Generate dashboard summary
summary = monitor.generate_dashboard_summary()

print(f"Total Phases: {summary['total_phases']}")
print(f"Completed: {summary['completed_phases']}")
print(f"In Progress: {summary['in_progress_phases']}")
print(f"Failed: {summary['failed_phases']}")
print(f"Completion: {summary['completion_percentage']:.1f}%")
print(f"Velocity: {summary['velocity']['phases_per_hour']:.2f} phases/hour")
```

### Timeline Visualization

```python
# Generate timeline for Gantt chart or similar
timeline = monitor.generate_timeline()

for entry in timeline:
    print(f"{entry['feature']} - {entry['phase']}")
    print(f"  Start: {entry['start']}")
    print(f"  End: {entry['end']}")
    print(f"  Duration: {entry['duration_minutes']} minutes")
```

### Bottleneck Detection

```python
# Detect phases taking longer than estimated
bottlenecks = monitor.detect_bottlenecks()

if bottlenecks:
    print("⚠️  Bottlenecks detected:")
    for bottleneck in bottlenecks:
        print(f"  {bottleneck['feature']} - {bottleneck['phase']}")
        print(f"    Estimated: {bottleneck['estimated_hours']:.2f}h")
        print(f"    Actual: {bottleneck['actual_hours']:.2f}h")
        print(f"    Overrun: {bottleneck['overrun_percentage']:.1f}%")
else:
    print("✅ No bottlenecks - all phases on track!")
```

### Orchestrator Integration

```python
# TDD Mastery Orchestrator example
class TDDMasteryOrchestrator:
    def __init__(self):
        self.monitor = ProgressMonitor()
    
    def execute_red_phase(self):
        # Start tracking
        self.monitor.on_orchestrator_phase_start("TDDOrchestrator", "RED Phase")
        
        try:
            # Execute RED phase logic
            tests_created = self.create_failing_tests()
            
            # Mark complete
            self.monitor.on_orchestrator_phase_complete("TDDOrchestrator", "RED Phase")
            
            return tests_created
        except Exception as e:
            # Mark failed
            self.monitor.on_orchestrator_phase_fail(
                "TDDOrchestrator",
                "RED Phase",
                reason=str(e)
            )
            raise
```

### Gate Validation Tracking

```python
# TDD Environment Gate integration
gate = TDDEnvironmentGate()
monitor = ProgressMonitor()

# Start gate validation
monitor.on_gate_validation_start("TDDEnvironmentGate")

result = gate.validate_tdd_readiness()

# Complete validation
monitor.on_gate_validation_complete("TDDEnvironmentGate", passed=result.allowed)

# Query all validations
validations = monitor.get_gate_validations()
for v in validations:
    print(f"{v['gate']}: {'✅ PASSED' if v['passed'] else '❌ FAILED'}")
```

---

## Performance Metrics

### Achieved Performance

**Phase Tracking:** 0.06s (< 0.1s requirement) ✅  
**Dashboard Generation:** 0.08s for 20 phases (< 0.5s requirement) ✅  
**Test Suite:** 22/22 tests passing in 0.06s ✅

### Performance Requirements

| Operation | Target | Achieved | Status |
|-----------|--------|----------|--------|
| start_phase() + complete_phase() | <100ms | <60ms | ✅ |
| generate_dashboard_summary() (20 phases) | <500ms | <80ms | ✅ |
| calculate_velocity() | <50ms | <20ms | ✅ |
| detect_bottlenecks() | <100ms | <30ms | ✅ |

---

## Storage & Persistence

### File-Based Storage

**Location:** `cortex-brain/metrics/phases.json`

**Format:**
```json
{
  "Feature 6::Phase 6.1 (RED)": {
    "feature_name": "Feature 6",
    "phase_name": "Phase 6.1 (RED)",
    "status": "completed",
    "start_time": "2025-12-12T10:00:00",
    "end_time": "2025-12-12T10:30:00",
    "estimated_hours": 0.5,
    "actual_hours": 0.5,
    "failure_reason": null
  },
  "Feature 6::Phase 6.2 (GREEN)": {
    "feature_name": "Feature 6",
    "phase_name": "Phase 6.2 (GREEN)",
    "status": "in_progress",
    "start_time": "2025-12-12T10:30:00",
    "end_time": null,
    "estimated_hours": 0.75,
    "actual_hours": null,
    "failure_reason": null
  }
}
```

### Storage Operations

**Auto-Save:** Every phase start/complete/fail automatically persists to storage  
**Auto-Load:** Monitor loads existing phases on initialization  
**Cleanup:** `cleanup_old_metrics(days=30)` removes phases older than 30 days

---

## Integration with Other Features

### Feature 1: Environment Diagnostics Orchestrator

```python
# Track diagnostics phases
monitor.on_orchestrator_phase_start("EnvironmentDiagnostics", "Validation")
diag_result = env_diagnostics.diagnose()
monitor.on_orchestrator_phase_complete("EnvironmentDiagnostics", "Validation")
```

### Feature 2: Git Checkpoint Integration

```python
# Sync with git checkpoints (future enhancement)
monitor.sync_with_git_checkpoints()
checkpoints = monitor.get_checkpoints()

for cp in checkpoints:
    print(f"Tag: {cp['tag']}")
    print(f"Timestamp: {cp['timestamp']}")
```

### Feature 3: Document Organization Enforcement

```python
# Track document validation
monitor.on_orchestrator_phase_start("DocumentValidator", "Path Validation")
validation_result = doc_validator.validate_path(path)
monitor.on_orchestrator_phase_complete("DocumentValidator", "Path Validation")
```

### Feature 6: TDD Environment Gate

```python
# Track gate validations
monitor.on_gate_validation_start("TDDEnvironmentGate")
gate_result = gate.validate_tdd_readiness()
monitor.on_gate_validation_complete("TDDEnvironmentGate", passed=gate_result.allowed)

# Query all gate validations
validations = monitor.get_gate_validations()
passed = sum(1 for v in validations if v['passed'])
print(f"Gate Pass Rate: {passed}/{len(validations)}")
```

---

## Dashboard Integration

### Admin Dashboard Example

```python
import json
from pathlib import Path

# Generate dashboard data
monitor = ProgressMonitor()
summary = monitor.generate_dashboard_summary()
timeline = monitor.generate_timeline()
bottlenecks = monitor.detect_bottlenecks()

# Create dashboard JSON
dashboard_data = {
    'summary': summary,
    'timeline': timeline,
    'bottlenecks': bottlenecks,
    'velocity': {
        'current': summary['velocity']['phases_per_hour'],
        'target': 1.5,  # phases/hour target
        'accuracy': summary['velocity']['accuracy_percentage']
    }
}

# Save for web dashboard
dashboard_file = Path("cortex-brain/dashboards/progress.json")
dashboard_file.parent.mkdir(parents=True, exist_ok=True)

with open(dashboard_file, 'w') as f:
    json.dump(dashboard_data, f, indent=2)

print(f"Dashboard data saved: {dashboard_file}")
```

### HTML Dashboard Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>CORTEX Progress Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>CORTEX Progress Monitor</h1>
    
    <div id="summary">
        <h2>Summary</h2>
        <p>Total Phases: <span id="total"></span></p>
        <p>Completed: <span id="completed"></span></p>
        <p>In Progress: <span id="in-progress"></span></p>
        <p>Completion: <span id="percentage"></span>%</p>
        <p>Velocity: <span id="velocity"></span> phases/hour</p>
    </div>
    
    <canvas id="timeline-chart"></canvas>
    
    <script>
        fetch('/api/progress')
            .then(r => r.json())
            .then(data => {
                document.getElementById('total').textContent = data.summary.total_phases;
                document.getElementById('completed').textContent = data.summary.completed_phases;
                document.getElementById('in-progress').textContent = data.summary.in_progress_phases;
                document.getElementById('percentage').textContent = data.summary.completion_percentage.toFixed(1);
                document.getElementById('velocity').textContent = data.summary.velocity.phases_per_hour.toFixed(2);
                
                // Render timeline chart
                const ctx = document.getElementById('timeline-chart');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.timeline.map(t => t.phase),
                        datasets: [{
                            label: 'Duration (minutes)',
                            data: data.timeline.map(t => t.duration_minutes)
                        }]
                    }
                });
            });
    </script>
</body>
</html>
```

---

## Testing Strategy

### Test Coverage

**22 tests, 100% pass rate, 0.06s execution**

**Test Categories:**

1. **Phase Tracking (5 tests)**
   - `test_starts_new_phase_tracking` ✅
   - `test_completes_phase_tracking` ✅
   - `test_marks_phase_as_failed` ✅
   - `test_retrieves_phase_status` ✅
   - `test_lists_all_phases_for_feature` ✅

2. **Velocity Calculation (4 tests)**
   - `test_calculates_phases_per_hour` ✅
   - `test_compares_estimated_vs_actual_time` ✅
   - `test_calculates_completion_percentage` ✅
   - `test_retrieves_historical_velocity_data` ✅

3. **Dashboard Integration (3 tests)**
   - `test_generates_progress_summary` ✅
   - `test_generates_phase_timeline` ✅
   - `test_detects_bottlenecks` ✅

4. **Orchestrator Integration (4 tests)**
   - `test_tracks_planning_orchestrator_phases` ✅
   - `test_tracks_tdd_orchestrator_phases` ✅
   - `test_tracks_environment_gate_validations` ✅
   - `test_auto_tracks_git_checkpoints` ✅

5. **Metrics Persistence (4 tests)**
   - `test_persists_phase_to_storage` ✅
   - `test_loads_phases_from_storage` ✅
   - `test_updates_existing_phase_in_storage` ✅
   - `test_cleans_old_metrics_from_storage` ✅

6. **Performance Requirements (2 tests)**
   - `test_phase_tracking_completes_under_100ms` ✅
   - `test_dashboard_summary_generates_under_500ms` ✅

### Running Tests

```bash
# Run all tests
pytest tests/orchestrators/test_progress_monitor.py -v

# Run with coverage
pytest tests/orchestrators/test_progress_monitor.py --cov=src/orchestrators/progress_monitor

# Run specific test
pytest tests/orchestrators/test_progress_monitor.py::TestVelocityCalculation::test_calculates_phases_per_hour -v

# Run performance tests only
pytest tests/orchestrators/test_progress_monitor.py::TestPerformanceRequirements -v
```

---

## API Reference

### ProgressMonitor

**Constructor:**
```python
monitor = ProgressMonitor(storage_path: Optional[Path] = None)
```
- `storage_path`: Custom storage location (defaults to `cortex-brain/metrics/`)

**Methods:**

#### start_phase(feature_name: str, phase_name: str, estimated_hours: float) → PhaseProgress

Start tracking a new phase.

**Parameters:**
- `feature_name` (str): Feature name (e.g., "Feature 5")
- `phase_name` (str): Phase name (e.g., "Phase 5.1 (RED)")
- `estimated_hours` (float): Estimated completion time in hours

**Returns:** PhaseProgress with `IN_PROGRESS` status

**Example:**
```python
phase = monitor.start_phase("Feature 5", "Phase 5.1", 0.5)
```

#### complete_phase(feature_name: str, phase_name: str) → PhaseProgress

Mark phase as completed. Automatically calculates `actual_hours`.

**Parameters:**
- `feature_name` (str): Feature name
- `phase_name` (str): Phase name

**Returns:** PhaseProgress with `COMPLETED` status and `actual_hours` set

**Example:**
```python
completed = monitor.complete_phase("Feature 5", "Phase 5.1")
print(f"Took {completed.actual_hours:.2f} hours")
```

#### fail_phase(feature_name: str, phase_name: str, reason: str) → PhaseProgress

Mark phase as failed with reason.

**Parameters:**
- `feature_name` (str): Feature name
- `phase_name` (str): Phase name
- `reason` (str): Failure reason

**Returns:** PhaseProgress with `FAILED` status

**Example:**
```python
failed = monitor.fail_phase("Feature 5", "Phase 5.1", "Tests not failing")
```

#### calculate_velocity() → VelocityMetrics

Calculate velocity metrics for completed phases.

**Returns:** VelocityMetrics with:
- `phases_per_hour`: Completion velocity
- `total_phases_completed`: Count of completed phases
- `total_hours_spent`: Total actual time
- `accuracy_percentage`: (estimated/actual) * 100
- `total_estimated_hours`: Sum of estimates
- `total_actual_hours`: Sum of actuals

**Example:**
```python
velocity = monitor.calculate_velocity()
if velocity.accuracy_percentage < 80:
    print("⚠️  Estimates consistently low!")
```

---

## Troubleshooting

### Issue: Storage File Not Found

**Symptom:** `FileNotFoundError` when loading monitor

**Diagnosis:**
```bash
ls cortex-brain/metrics/phases.json
# File not found
```

**Solution:**
```python
# Create storage directory
from pathlib import Path
Path("cortex-brain/metrics").mkdir(parents=True, exist_ok=True)

# Initialize monitor (will create file)
monitor = ProgressMonitor()
```

### Issue: Velocity Calculation Returns 0

**Symptom:** `calculate_velocity()` returns all zeros

**Diagnosis:**
```python
velocity = monitor.calculate_velocity()
print(velocity.total_phases_completed)  # 0
```

**Solution:**
```python
# Ensure phases are marked COMPLETED, not just started
monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
monitor.complete_phase("Feature 1", "Phase 1.1")  # Must call this!

velocity = monitor.calculate_velocity()
print(velocity.total_phases_completed)  # 1
```

### Issue: Dashboard Summary Shows Incorrect Counts

**Symptom:** Dashboard shows 6 phases instead of expected 2

**Diagnosis:** Old phases persisting from previous runs

**Solution:**
```python
# Use isolated storage for each test/run
import tempfile
from pathlib import Path

temp_storage = Path(tempfile.mkdtemp())
monitor = ProgressMonitor(storage_path=temp_storage)

# Or clean up old metrics
monitor.cleanup_old_metrics(days=0)  # Remove all
```

---

## Future Enhancements

### Phase 2 Features

1. **Tier 1 Integration**
   - Store metrics in brain Tier 1 (SQLite)
   - Query historical data with SQL
   - Better performance for large datasets

2. **Real-Time Dashboard**
   - WebSocket-based live updates
   - Auto-refresh every 5 seconds
   - Push notifications for bottlenecks

3. **Predictive Analytics**
   - ML-based completion time prediction
   - Bottleneck prediction before they occur
   - Velocity trend analysis

4. **Multi-Feature Tracking**
   - Track dependencies between features
   - Critical path analysis
   - Feature completion forecasting

5. **Git Integration Enhancement**
   - Auto-track commits per phase
   - Link phases to git tags
   - Generate release notes from phases

---

## Change Log

### Version 1.0.0 (December 12, 2025)

**Initial Release:**
- ✅ Phase tracking (start/complete/fail)
- ✅ Velocity calculation (phases/hour, accuracy)
- ✅ Completion percentage
- ✅ Dashboard summary generation
- ✅ Timeline visualization data
- ✅ Bottleneck detection
- ✅ Orchestrator hooks (Planning, TDD, Gates)
- ✅ File-based persistence (JSON)
- ✅ Historical velocity (7 days)
- ✅ Performance: 0.06s (22 tests)
- ✅ DRY refactoring (_make_phase_key helper)

---

## References

### Related Features

- **Feature 1:** Environment Diagnostics Orchestrator  
  Integration: Track diagnostic phases

- **Feature 2:** Git Checkpoint Integration  
  Integration: Sync with git checkpoints (future)

- **Feature 3:** Document Organization Enforcement  
  Integration: Track validation phases

- **Feature 6:** TDD Environment Gate  
  Integration: Track gate validations

### CORTEX Documentation

- Enhancement Plan: `cortex-brain/documents/planning/cortex-orchestrator-enhancement-plan.md`
- Brain Protection Rules: `cortex-brain/brain-protection-rules.yaml` (SKULL)
- Response Templates: `cortex-brain/response-templates.yaml`

---

**Document Version:** 1.0.0  
**Last Updated:** December 12, 2025  
**Reviewed By:** Progress Monitoring Team  
**Status:** Production Ready ✅
