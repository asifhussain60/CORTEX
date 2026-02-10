# Onboarding Orchestrator

**Status:** Production Ready | **Version:** 1.0.0 | **Category:** Specialized Orchestrators | **Module:** `cortex/orchestrators/onboarding/`

---

## Overview

The **Onboarding Orchestrator** manages the complete user onboarding journey in CORTEX, tracking progress through activities and ensuring comprehensive system familiarization.

### Purpose

- Orchestrate user onboarding workflows
- Track journey progress and completion
- Manage activity sequencing
- Validate prerequisite completion
- Generate progress reports
- Enable journey recovery

---

## Architecture

```
┌──────────────────────────────────────────────┐
│    Onboarding Orchestrator                   │
│    (Journey Management)                      │
└──────────────────────────────────────────────┘

┌─ JOURNEY CREATION
│  └─ Initialize user journey
│
├─ ACTIVITY MANAGEMENT
│  ├─ Add activities
│  ├─ Track completion
│  └─ Manage prerequisites
│
├─ PROGRESS TRACKING
│  ├─ Update progress
│  ├─ Calculate completion %
│  └─ Generate status
│
└─ COMPLETION HANDLING
   ├─ Validate all activities
   ├─ Mark journey complete
   └─ Provide summary
```

---

## Components

### Journey States

```python
class JourneyState(Enum):
    NEW = "new"              # Just created
    IN_PROGRESS = "in_progress"  # Started
    COMPLETED = "completed"  # All activities done
```

### Key Data Structures

```python
@dataclass
class Journey:
    journey_id: str          # Unique ID
    user_id: str             # User reference
    activities: List[str]    # Activity list
    state: JourneyState      # Current state
    activities_completed: int     # Count
    total_activities: int    # Total count
    _completed_indices: set  # Tracking
    created_at: datetime     # Creation time
    started_at: Optional[datetime]  # Start time
    completed_at: Optional[datetime]  # End time

@dataclass
class JourneyProgress:
    state: JourneyState
    activities_completed: int
    total_activities: int
    completion_percentage: float
    estimated_remaining_time: float
```

---

## How to Use It

### Basic Usage

```python
from cortex.orchestrators.onboarding.orchestrator import OnboardingOrchestrator

# Create orchestrator
orchestrator = OnboardingOrchestrator()

# Create new journey
journey = orchestrator.create_journey(
    user_id="user_123",
    activities=[
        "install_requirements",
        "configure_environment",
        "verify_setup",
        "run_first_test",
        "explore_features"
    ]
)

# Start journey
orchestrator.start_journey(journey.journey_id)

# Mark activities as complete
orchestrator.mark_activity_complete(journey.journey_id, 0)
orchestrator.mark_activity_complete(journey.journey_id, 1)
orchestrator.mark_activity_complete(journey.journey_id, 2)

# Check progress
progress = orchestrator.get_journey_progress(journey.journey_id)
print(f"Progress: {progress.completion_percentage}%")

# Mark journey complete
orchestrator.mark_journey_complete(journey.journey_id)
```

### Advanced Usage

#### Pattern 1: Conditional Activities

```python
journey = orchestrator.create_journey_with_conditions(
    user_id="user_123",
    base_activities=["install", "configure"],
    conditional_activities={
        "advanced_user": ["advanced_features", "optimization"],
        "beginner": ["basic_tutorial", "help_system"]
    },
    user_level="beginner"
)
```

#### Pattern 2: Progress Monitoring

```python
# Get detailed progress
progress = orchestrator.get_detailed_progress(journey_id)

print(f"State: {progress.state}")
print(f"Completed: {progress.activities_completed}/{progress.total_activities}")
print(f"Percentage: {progress.completion_percentage}%")
print(f"Estimated time remaining: {progress.estimated_remaining_time}min")
```

#### Pattern 3: Journey Validation

```python
# Validate journey can start
valid = orchestrator.validate_journey_prerequisites(journey_id)

# Get validation errors
errors = orchestrator.get_journey_errors(journey_id)
for error in errors:
    print(f"Error: {error.message}")
```

---

## Workflow Examples

### Workflow 1: Developer Onboarding

```python
journey = orchestrator.create_journey(
    user_id="dev_001",
    activities=[
        "clone_repository",
        "install_dependencies",
        "run_tests",
        "build_project",
        "review_architecture",
        "complete_first_feature"
    ]
)

# Guide through workflow
orchestrator.start_journey(journey.journey_id)
# User completes each step, marks as done
```

### Workflow 2: Admin Onboarding

```python
journey = orchestrator.create_journey(
    user_id="admin_001",
    activities=[
        "create_admin_account",
        "configure_governance",
        "set_up_audit",
        "configure_alerts",
        "test_workflows"
    ]
)
```

---

## Setup Orchestrator

**Module:** `cortex/orchestrators/onboarding/setup_orchestrator.py`

Handles automated environment setup.

```python
# Validate requirements
conflicts = setup_orchestrator.detect_version_conflicts(
    workspace_path="/path/to/workspace"
)

# Install dependencies
result = setup_orchestrator.auto_install_requirements()

# Security scan
scan = setup_orchestrator.scan_security(
    packages=result.installed_packages
)
```

---

## Integration Points

### Components

- **OnboardingOrchestrator**: Main orchestrator
- **SetupOrchestrator**: Environment setup
- **VSCodeConfigurator**: IDE configuration
- **ToolchainValidator**: Toolchain validation
- **MCPBootstrapper**: MCP setup
- **DependencyResolver**: Dependency resolution

### Dependencies

- Audit Logger
- State Manager
- Database

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `create_journey` | Create onboarding journey |
| `start_journey` | Start journey |
| `mark_activity_complete` | Mark activity done |
| `get_journey_progress` | Get progress |
| `complete_journey` | Mark journey complete |

---

## Performance

| Operation | Duration |
|-----------|----------|
| Create journey | 10-20ms |
| Start journey | 5-10ms |
| Mark complete | 2-5ms |
| Get progress | 1-3ms |

---

## Testing

- **Coverage:** 92%
- **Journey tracking:** 98%
- **Progress calculation:** 100%

---

## Related Documentation

- 📖 [Setup Process](../guides/setup-guide.md)
- 📖 [Getting Started](../01-getting-started/)

---

## Copyright & License


CORTEX Framework - Onboarding Orchestrator Module
Status: Production Ready | Version: 1.0.0

---

**Last Updated:** 2026-01-22 | **Author:** CORTEX Documentation Generator
