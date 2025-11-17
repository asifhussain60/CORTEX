# CORTEX Onboarding EPM - Implementation Guide

**Author:** Asif Hussain  
**Date:** 2025-11-15  
**Status:** Phase 1 Foundation Complete  
**Version:** 1.0.0

---

## 🎯 Overview

The Onboarding EPM (Execution Plan Module) provides an **extensible, step-based architecture** for guided onboarding flows. The design prioritizes **ease of adding/removing steps** without breaking existing functionality.

---

## 🏗️ Architecture

### Core Components

```
src/epm/
├── __init__.py                    # Public API
├── onboarding_step.py             # Base step classes
├── step_registry.py               # Step registration & ordering
├── onboarding_orchestrator.py    # Execution coordination
└── steps/                         # Concrete step implementations
    ├── environment_detection.py
    ├── dependency_installation.py
    ├── brain_initialization.py
    ├── agent_activation.py
    ├── integration_setup.py
    └── validation.py
```

### Design Principles

1. **Step Independence**: Each step is self-contained
2. **Dependency Resolution**: Automatic topological sort
3. **Profile Filtering**: Steps declare which profiles they support
4. **Graceful Degradation**: Optional steps can be skipped
5. **Progress Tracking**: Real-time state management
6. **Resume Capability**: Session persistence (planned)

---

## 📋 Adding a New Step

### 1. Create Step Class

```python
# src/epm/steps/my_new_step.py
from src.epm import OnboardingStep, StepResult, StepStatus, StepDisplayFormat
from typing import Dict, Any

class MyNewStep(OnboardingStep):
    def __init__(self):
        super().__init__(
            step_id="my_new_step",
            name="My New Step",
            description="What this step does",
            display_format=StepDisplayFormat.PROGRESS_BAR,
            estimated_duration=60,  # seconds
            skippable=True,  # Can be skipped on error
            required_for_profiles=["standard", "comprehensive"],  # Which profiles need it
            dependencies=["install_dependencies"]  # Steps that must complete first
        )
    
    def execute(self, context: Dict[str, Any]) -> StepResult:
        """Execute step logic"""
        try:
            # Your step implementation here
            result_data = self._do_work(context)
            
            return StepResult(
                success=True,
                status=StepStatus.COMPLETED,
                message="Step completed successfully",
                data=result_data,
                errors=[],
                warnings=[]
            )
        
        except Exception as e:
            return StepResult(
                success=False,
                status=StepStatus.FAILED,
                message=f"Step failed: {str(e)}",
                errors=[str(e)]
            )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> bool:
        """Check if step can run"""
        # Check if required dependencies are met
        return True
    
    def _do_work(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Actual step implementation"""
        # ... your logic ...
        return {"result": "data"}
```

### 2. Register Step

```python
# In orchestrator initialization or plugin
from src.epm import OnboardingOrchestrator
from src.epm.steps.my_new_step import MyNewStep

orchestrator = OnboardingOrchestrator()
orchestrator.registry.register(MyNewStep())
```

**That's it!** The step is now integrated and will execute in dependency-resolved order.

---

## 🔄 Removing a Step

### Option 1: Unregister Programmatically

```python
orchestrator.registry.unregister("my_step_id")
```

### Option 2: Don't Register It

Simply don't call `registry.register()` for that step.

### Option 3: Disable for Profiles

```python
class MyStep(OnboardingStep):
    def __init__(self):
        super().__init__(
            step_id="my_step",
            name="My Step",
            required_for_profiles=[]  # Not required for any profile = never executes
        )
```

---

## 📊 Step Lifecycle

```
PENDING → RUNNING → COMPLETED
                  ↘ FAILED
                  ↘ SKIPPED
```

### Execution Flow

1. **Orchestrator** gets steps from registry
2. **Filter by profile** (quick/standard/comprehensive)
3. **Resolve dependencies** (topological sort)
4. **For each step:**
   - Check `can_skip()` (prerequisites, profile match)
   - If skip: Mark SKIPPED, continue
   - Execute step: PENDING → RUNNING
   - On success: RUNNING → COMPLETED
   - On failure: RUNNING → FAILED (stop if not skippable)
5. **Generate report** with all results

---

## 🎨 Display Formats

Steps can specify how their output should be displayed:

```python
StepDisplayFormat.PROGRESS_BAR        # Simple progress indicator
StepDisplayFormat.ANIMATED_DIAGRAM    # Live mermaid diagram
StepDisplayFormat.SPLIT_DIAGRAM       # Left/right brain visualization
StepDisplayFormat.CHECKLIST           # Task completion list
StepDisplayFormat.STATUS_REPORT       # Detailed status table
StepDisplayFormat.ANIMATED_CARDS      # Metric cards with animation
StepDisplayFormat.TABLE               # Data in table format
StepDisplayFormat.TREE_VIEW           # Hierarchical data
StepDisplayFormat.INTERACTIVE_DASHBOARD  # Full dashboard
StepDisplayFormat.LIVE_RENDER         # Live updating content
StepDisplayFormat.TEXT_ONLY           # Plain text output
```

**Usage:**

```python
class MyStep(OnboardingStep):
    def __init__(self):
        super().__init__(
            display_format=StepDisplayFormat.ANIMATED_DIAGRAM,
            display_options={
                "diagram_type": "mermaid",
                "show_legend": True,
                "animate": True
            }
        )
```

---

## 🔗 Dependencies

### Declaring Dependencies

```python
class AgentActivationStep(OnboardingStep):
    def __init__(self):
        super().__init__(
            step_id="configure_agents",
            dependencies=[
                "initialize_brain",  # Must complete first
                "install_dependencies"  # Must complete first
            ]
        )
```

### Dependency Resolution

The registry automatically:
1. Builds dependency graph
2. Performs topological sort (Kahn's algorithm)
3. Returns steps in proper execution order
4. Detects circular dependencies

**Example:**

```
Steps registered:
- validate_installation (depends: configure_agents, setup_integrations)
- configure_agents (depends: initialize_brain)
- initialize_brain (depends: install_dependencies)
- install_dependencies (depends: detect_environment)
- detect_environment (no dependencies)
- setup_integrations (depends: install_dependencies)

Execution order:
1. detect_environment
2. install_dependencies
3. initialize_brain
4. setup_integrations  ← Can run in parallel with configure_agents
5. configure_agents
6. validate_installation
```

---

## 📦 Context & Data Flow

### Context Structure

```python
context = {
    "profile": "standard",  # quick/standard/comprehensive
    "project_root": Path("/path/to/project"),
    "user_preferences": {...},
    "previous_results": {
        "detect_environment": {
            "platform": "Windows",
            "python_version": "3.11.5"
        },
        "install_dependencies": {
            "packages_installed": 42
        }
    }
}
```

### Accessing Previous Results

```python
class MyStep(OnboardingStep):
    def execute(self, context: Dict[str, Any]) -> StepResult:
        # Get results from previous step
        env_data = context["previous_results"].get("detect_environment", {})
        platform = env_data.get("platform", "unknown")
        
        # Use in current step
        if platform == "Windows":
            # Windows-specific logic
            pass
```

---

## 🎯 Profiles

### Three Built-in Profiles

| Profile | Duration | Target Audience | Steps |
|---------|----------|-----------------|-------|
| **QUICK** | 5-7 min | Experienced users | Essential only |
| **STANDARD** | 10-15 min | Most users | Core features + demos |
| **COMPREHENSIVE** | 20-30 min | Leadership, deep dive | Everything |

### Profile Filtering

```python
class MyStep(OnboardingStep):
    def __init__(self):
        super().__init__(
            required_for_profiles=["standard", "comprehensive"]
            # Not required for "quick" profile
        )
```

---

## ⚡ Progress Tracking

### Real-time Progress

```python
orchestrator = OnboardingOrchestrator()
session = orchestrator.start_onboarding(profile=OnboardingProfile.STANDARD)

# Get progress during execution
progress = orchestrator.get_progress()
# {
#     "progress_percent": 45.5,
#     "total_steps": 6,
#     "completed_steps": 3,
#     "failed_steps": 0,
#     "skipped_steps": 1,
#     "current_step": "configure_agents",
#     "elapsed_time_seconds": 127.3
# }
```

### Execution Report

```python
report = orchestrator.generate_report()
# {
#     "session_id": "uuid-here",
#     "profile": "standard",
#     "total_steps": 6,
#     "completed_steps": 5,
#     "failed_steps": 0,
#     "skipped_steps": 1,
#     "step_results": {
#         "detect_environment": {
#             "success": True,
#             "duration_seconds": 28.4,
#             "message": "Environment detected successfully"
#         },
#         ...
#     }
# }
```

---

## 🛡️ Error Handling

### Skippable vs Critical Steps

```python
class OptionalStep(OnboardingStep):
    def __init__(self):
        super().__init__(
            skippable=True  # Failure won't stop onboarding
        )

class CriticalStep(OnboardingStep):
    def __init__(self):
        super().__init__(
            skippable=False  # Failure stops onboarding
        )
```

### Graceful Degradation

```python
class MyStep(OnboardingStep):
    def execute(self, context: Dict[str, Any]) -> StepResult:
        warnings = []
        
        # Try optional feature
        try:
            self._optional_feature()
        except Exception as e:
            warnings.append(f"Optional feature failed: {e}")
            # Continue anyway
        
        # Required functionality
        result = self._required_work()
        
        return StepResult(
            success=True,
            status=StepStatus.COMPLETED,
            message="Step completed with warnings",
            warnings=warnings
        )
```

---

## 🔮 Future Enhancements

### Phase 2: Advanced Features (Planned)

1. **Session Persistence**
   - Save session state to disk
   - Resume from any point
   - Recovery from crashes

2. **Live Visualization**
   - Mermaid diagram rendering
   - Progress animations
   - Interactive dashboards

3. **Plugin Integration**
   - Steps as plugins
   - Dynamic step discovery
   - Third-party step extensions

4. **User Interaction**
   - Pause/resume controls
   - Step preview
   - Custom step selection

---

## 📝 Example: Full Onboarding Flow

```python
from src.epm import OnboardingOrchestrator, OnboardingProfile
from src.epm.steps import (
    EnvironmentDetectionStep,
    DependencyInstallationStep,
    BrainInitializationStep,
    AgentActivationStep,
    IntegrationSetupStep,
    ValidationStep
)

# Initialize orchestrator
orchestrator = OnboardingOrchestrator(project_root=Path("."))

# Register all steps (order doesn't matter - dependencies resolve it)
orchestrator.registry.register(ValidationStep())  # Will run last
orchestrator.registry.register(EnvironmentDetectionStep())  # Will run first
orchestrator.registry.register(AgentActivationStep())
orchestrator.registry.register(BrainInitializationStep())
orchestrator.registry.register(IntegrationSetupStep())
orchestrator.registry.register(DependencyInstallationStep())

# Start onboarding
session = orchestrator.start_onboarding(
    profile=OnboardingProfile.STANDARD,
    context={
        "user_name": "Jane Developer",
        "skip_git_setup": False
    }
)

# Get results
report = orchestrator.generate_report()
print(f"Completed: {report['completed_steps']}/{report['total_steps']}")
print(f"Duration: {report['end_time'] - report['start_time']}")
```

---

## 🎓 Best Practices

1. **Keep Steps Small**: Each step should do one thing well
2. **Declare Dependencies Explicitly**: Don't assume execution order
3. **Handle Errors Gracefully**: Return StepResult with errors, don't raise
4. **Provide Meaningful Messages**: Users see step.result.message
5. **Use Display Formats**: Enhance UX with appropriate visualization
6. **Test Independently**: Each step should be unit-testable
7. **Document Prerequisites**: Make requirements clear in description

---

## 📚 Next Steps

### To Complete Onboarding EPM:

1. **Implement Concrete Steps** (Phase 2)
   - Environment detection
   - Dependency installation
   - Brain initialization
   - Agent activation
   - Integration setup
   - Validation

2. **Add Visualization** (Phase 3)
   - Mermaid diagram rendering
   - Progress animations
   - Interactive UI

3. **Integration** (Phase 4)
   - Plugin interface
   - Command registration
   - Entry point integration

---

**Foundation Complete!** ✅  
The extensible step architecture is ready for step implementations.

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms
