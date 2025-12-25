# Execution Orchestrator Guide

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Status:** ✅ Production Ready  
**Updated:** December 25, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Execution Modes](#execution-modes)
4. [Plan Execution](#plan-execution)
5. [Phase Management](#phase-management)
6. [Multi-Agent Collaboration](#multi-agent-collaboration)
7. [Sub-Orchestrator Integration](#sub-orchestrator-integration)
8. [Validation & Safety](#validation--safety)
9. [Rollback & Recovery](#rollback--recovery)
10. [Best Practices](#best-practices)

---

## 🎯 Overview

### What is ExecutionOrchestrator?

`ExecutionOrchestrator` is a specialized orchestrator for executing multi-phase plans with advanced features:

- ✅ **Dynamic Phase Registration:** Phases extracted from execution plans
- ✅ **Adaptive Execution:** AUTONOMOUS, SUPERVISED, MANUAL modes
- ✅ **Self-Healing:** 3 automatic retry attempts per phase
- ✅ **Multi-Agent Collaboration:** Sequential, parallel, nested patterns (Phase 5)
- ✅ **Context Validation:** Pre-execution checks with auto-retrieval
- ✅ **Safety Guardrails:** Risk assessment and mitigation
- ✅ **Rollback Support:** Git checkpoints with phase-level restoration
- ✅ **Sub-Orchestrator Routing:** TDD, Planning, Documentation integration

### Phase 5 Enhancements (23% → 95% Agentic Alignment)

```
BEFORE (v1.0):  23% agentic alignment
    - Manual phase execution
    - No multi-agent support
    - Basic error handling

AFTER (v2.0):   95% agentic alignment
    - Autonomous multi-phase execution
    - Sequential/parallel/nested agents
    - Context validation + auto-retrieval
    - Enhanced safety guardrails
    - Structured output (Pydantic)
```

---

## 🚀 Quick Start

### Basic Usage

```python
from src.orchestration_4_0.orchestrators.execution import ExecutionOrchestrator
from src.operations.modules.orchestration.adaptive_execution import ExecutionMode

# Create orchestrator
orchestrator = ExecutionOrchestrator(
    logger=logger,
    config={
        "execution_mode": ExecutionMode.SUPERVISED,
        "max_retries": 3,
        "enable_rollback": True
    }
)

# Execute plan
execution_plan = {
    "name": "user-authentication",
    "phases": [
        {"name": "discovery", "description": "Analyze requirements"},
        {"name": "design", "description": "Design solution"},
        {"name": "implementation", "description": "Implement features"},
        {"name": "testing", "description": "Run tests"},
        {"name": "validation", "description": "Validate completion"}
    ]
}

result = orchestrator.execute(context={
    "plan": execution_plan,
    "workspace": "/path/to/workspace"
})

# Check result
print(f"Success: {result.success}")
print(f"Phases completed: {result.phases_completed}")
print(f"Duration: {result.total_duration_ms}ms")
```

### With Planning System 2.0

```python
from src.orchestrators.planning import PlanningOrchestrator

# Generate plan
planning_orchestrator = PlanningOrchestrator(config={
    "autonomous_execution": True  # Auto-execute after generation
})

result = planning_orchestrator.execute(
    feature_name="payment-gateway"
)

# Plan generated AND executed automatically
print(f"Plan path: {result.data['plan_path']}")
print(f"Execution summary: {result.data['execution_summary']}")
```

---

## 🎛️ Execution Modes

### Mode Comparison

| Mode | Automation | Approval | Rollback | Use Case |
|------|-----------|----------|----------|----------|
| **AUTONOMOUS** | Full | None | Automatic | CI/CD, overnight runs |
| **SUPERVISED** | Partial | At gates | Manual | Development, staging |
| **MANUAL** | None | Every step | Manual | Production, complex changes |

### AUTONOMOUS Mode

**Full automation with self-healing (3 retries):**

```python
from src.operations.modules.orchestration.adaptive_execution import ExecutionMode

config = {
    "execution_mode": ExecutionMode.AUTONOMOUS,
    "max_retries": 3,
    "enable_rollback": True,
    "auto_checkpoint": True
}

orchestrator = ExecutionOrchestrator(config=config)
result = orchestrator.execute(context={
    "plan": execution_plan,
    "workspace": workspace_path
})

# Automatic features:
# - 3 retry attempts per phase failure
# - Auto-checkpoint after each phase
# - Auto-rollback on critical errors
# - Self-healing with exponential backoff
```

**Benefits:**
- ✅ Hands-free execution
- ✅ Works overnight/weekends
- ✅ Automatic recovery from transient failures
- ✅ Consistent execution patterns

### SUPERVISED Mode

**Human approval at phase gates:**

```python
config = {
    "execution_mode": ExecutionMode.SUPERVISED,
    "approval_required_at": ["implementation", "deployment"]
}

orchestrator = ExecutionOrchestrator(config=config)

# Execution pauses at "implementation" and "deployment"
# User must approve to continue
result = orchestrator.execute(context={
    "plan": execution_plan,
    "workspace": workspace_path
})
```

**Approval Flow:**
```
Discovery → Design → [PAUSE: Approve Implementation?] → Implementation
    → Testing → [PAUSE: Approve Deployment?] → Deployment → Complete
```

**Benefits:**
- ✅ Control over critical phases
- ✅ Review before risky operations
- ✅ Learn from execution patterns

### MANUAL Mode

**Step-by-step with user control:**

```python
config = {
    "execution_mode": ExecutionMode.MANUAL
}

orchestrator = ExecutionOrchestrator(config=config)

# User triggers each phase
for phase in execution_plan["phases"]:
    # User decision: execute this phase?
    if user_approves(phase["name"]):
        orchestrator.execute_phase(phase["name"])
```

**Benefits:**
- ✅ Maximum control
- ✅ Ideal for complex migrations
- ✅ Production-safe

---

## 📦 Plan Execution

### Execution Context

```python
context = {
    # REQUIRED
    "plan": {
        "name": "feature-name",
        "phases": [
            {"name": "phase1", "description": "..."},
            {"name": "phase2", "description": "..."}
        ]
    },
    
    # OPTIONAL
    "workspace": "/path/to/workspace",
    "execution_mode": ExecutionMode.AUTONOMOUS,
    "validators": {
        "phase1": validator_function
    },
    "sub_orchestrators": {
        "tdd": tdd_orchestrator,
        "planning": planning_orchestrator
    }
}

result = orchestrator.execute(context=context)
```

### Execution Result

```python
from src.orchestration_4_0.orchestrators.execution import ExecutionResult

result = orchestrator.execute(context)

# Result structure
result.success                  # bool: Overall success
result.phases_completed         # List[str]: Completed phase names
result.phase_results            # List[PhaseResult]: Per-phase details
result.total_duration_ms        # float: Total execution time
result.execution_mode           # ExecutionMode: Mode used
result.context                  # Dict: Original context
result.errors                   # List[str]: Error messages
result.warnings                 # List[str]: Warning messages

# Phase-specific results
for phase_result in result.phase_results:
    print(f"Phase: {phase_result.phase_name}")
    print(f"Status: {phase_result.status.value}")
    print(f"Duration: {phase_result.duration_ms}ms")
    if phase_result.errors:
        print(f"Errors: {phase_result.errors}")
```

### Progress Tracking

```python
# Visual feedback during execution
orchestrator.execute(context)

# Output (with engagement hints):
# 🎭 Orchestrator engaged: execution [workspace:my-project]
# 🎭 Phase transition: → DISCOVERY
# ✅ Phase complete: DISCOVERY (1.2s)
# 🎭 Phase transition: → DESIGN
# ✅ Phase complete: DESIGN (2.4s)
# 🎭 Phase transition: → IMPLEMENTATION
# ✅ Phase complete: IMPLEMENTATION (15.7s)
# 🎭 Orchestrator completing: ✅ ALL PHASES COMPLETE
```

---

## 🔄 Phase Management

### Dynamic Phase Registration

Phases are automatically registered from the execution plan:

```python
execution_plan = {
    "name": "payment-gateway",
    "phases": [
        {
            "name": "discovery",
            "description": "Analyze payment requirements",
            "dependencies": [],
            "validators": ["requirement_validator"]
        },
        {
            "name": "design",
            "description": "Design payment architecture",
            "dependencies": ["discovery"],
            "sub_orchestrator": "planning"
        },
        {
            "name": "tdd_red",
            "description": "Write failing tests",
            "dependencies": ["design"],
            "sub_orchestrator": "tdd"
        },
        {
            "name": "implementation",
            "description": "Implement payment logic",
            "dependencies": ["tdd_red"]
        },
        {
            "name": "tdd_green",
            "description": "Pass tests",
            "dependencies": ["implementation"],
            "sub_orchestrator": "tdd"
        },
        {
            "name": "tdd_refactor",
            "description": "Refactor code",
            "dependencies": ["tdd_green"],
            "sub_orchestrator": "tdd"
        }
    ]
}

# Phases auto-registered and executed in order
orchestrator.execute(context={"plan": execution_plan})
```

### Phase Dependencies

```python
# Phases with dependencies execute in correct order
# Dependency resolution via topological sort

phases = [
    {"name": "A", "dependencies": []},
    {"name": "B", "dependencies": ["A"]},
    {"name": "C", "dependencies": ["A"]},
    {"name": "D", "dependencies": ["B", "C"]}
]

# Execution order: A → (B, C in parallel) → D
```

### Phase Validators

```python
def validate_discovery_phase(phase_result):
    """Custom phase validator."""
    if "requirements" not in phase_result.output:
        return ValidationResult(
            valid=False,
            errors=["Requirements not documented"]
        )
    return ValidationResult(valid=True)

# Register validator
orchestrator.register_validator(
    phase_name="discovery",
    validator=validate_discovery_phase
)

# Validator runs after phase completes
result = orchestrator.execute(context)
```

---

## 🤝 Multi-Agent Collaboration

### Sequential Chat (Pipeline Pattern)

Execute orchestrators in sequence, passing context forward:

```python
# Sequential execution: TDD → Implementation → QA
result = await orchestrator.execute_sequential_chat(
    orchestrator_names=["tdd", "implementation", "qa"],
    context={"feature": "user-auth"}
)

# Flow:
# 1. TDD orchestrator generates tests
# 2. Implementation orchestrator uses tests context
# 3. QA orchestrator validates implementation
```

**Use Cases:**
- Feature implementation workflows
- Code generation pipelines
- Documentation generation chains

### Parallel Group Chat (Concurrent Pattern)

Execute orchestrators in parallel with result synthesis:

```python
# Parallel execution: Multiple design approaches
result = await orchestrator.execute_parallel_group_chat(
    orchestrator_names=["design_approach_1", "design_approach_2", "design_approach_3"],
    context={"requirements": requirements_doc},
    synthesize=True  # Combine results
)

# All approaches execute concurrently
# Results synthesized into best solution
```

**Use Cases:**
- Multiple design alternatives
- Parallel test execution
- Concurrent code reviews

### Nested Chat (Hierarchical Pattern)

Execute hierarchical teams of orchestrators:

```python
# Nested teams: Frontend + Backend + DevOps
team_structure = {
    "frontend": ["react", "styling", "testing"],
    "backend": ["api", "database", "auth"],
    "devops": ["cicd", "monitoring", "deployment"]
}

result = await orchestrator.execute_nested_chat(
    team_structure=team_structure,
    context={"feature": "payment-gateway"}
)

# Teams execute in parallel
# Within each team, sequential execution
```

**Use Cases:**
- Full-stack feature development
- Microservices deployment
- Complex system integration

---

## 🧩 Sub-Orchestrator Integration

### Register Sub-Orchestrators

```python
from src.orchestrators.tdd import TDDOrchestratorV4
from src.orchestrators.planning import PlanningOrchestrator
from src.orchestrators.documentation import DocumentationOrchestrator

# Create sub-orchestrators
tdd_orchestrator = TDDOrchestratorV4(config={})
planning_orchestrator = PlanningOrchestrator(config={})
doc_orchestrator = DocumentationOrchestrator(config={})

# Register with execution orchestrator
orchestrator.register_sub_orchestrator("tdd", tdd_orchestrator)
orchestrator.register_sub_orchestrator("planning", planning_orchestrator)
orchestrator.register_sub_orchestrator("documentation", doc_orchestrator)

# Use in phases
execution_plan = {
    "phases": [
        {"name": "plan", "sub_orchestrator": "planning"},
        {"name": "tdd_red", "sub_orchestrator": "tdd"},
        {"name": "implement", "sub_orchestrator": None},  # Custom logic
        {"name": "document", "sub_orchestrator": "documentation"}
    ]
}
```

### Sub-Orchestrator Execution

```python
# When phase has sub_orchestrator:
# 1. Context passed to sub-orchestrator
# 2. Sub-orchestrator executes
# 3. Result merged back into main context

# Example: TDD phase
phase = {"name": "tdd_red", "sub_orchestrator": "tdd"}

# Execution orchestrator:
sub_orch = orchestrator.sub_orchestrators["tdd"]
sub_result = sub_orch.execute(context=phase_context)

# Result available for next phase
```

### Custom Sub-Orchestrators

```python
class CustomSubOrchestrator(BaseOrchestrator):
    """Custom sub-orchestrator for specialized logic."""
    
    def execute(self) -> OrchestratorResult:
        # Custom implementation
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Custom logic complete",
            data={"custom_key": "custom_value"}
        )

# Register and use
custom_orch = CustomSubOrchestrator(config={})
orchestrator.register_sub_orchestrator("custom", custom_orch)
```

---

## 🛡️ Validation & Safety

### Context Validation (Phase 5)

```python
# Automatic context validation before execution
result = await orchestrator.enhanced_setup(context)

# Validation checks:
# - Required fields present
# - Context quality sufficient
# - Missing data retrievable
# - Schema compliance

if result.is_valid:
    print(f"Context valid: {result.quality_score}/100")
    print(f"Auto-retrieved: {result.auto_retrieved_items}")
else:
    print(f"Missing: {result.missing_required}")
    print(f"Quality issues: {result.quality_issues}")
```

### Safety Guardrails (Phase 5)

```python
# Automatic safety checks if enabled
config = {
    "enable_safety_checks": True
}

orchestrator = ExecutionOrchestrator(config=config)

# Safety checks assess:
# - Risk level (low, medium, high, critical)
# - Unsafe operations
# - Data loss potential
# - System impact

# High-risk operations require approval
result = orchestrator.execute(context)
# ⚠️ Execution requires approval: HIGH risk
```

### Custom Validators

```python
def custom_phase_validator(phase_result: PhaseResult) -> ValidationResult:
    """Validate phase output."""
    errors = []
    
    # Check required outputs
    if "test_results" not in phase_result.output:
        errors.append("Test results missing")
    
    # Check quality metrics
    coverage = phase_result.output.get("coverage", 0)
    if coverage < 90:
        errors.append(f"Coverage too low: {coverage}% (need 90%+)")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors
    )

# Register validator
orchestrator.register_validator("testing", custom_phase_validator)
```

---

## ↩️ Rollback & Recovery

### Automatic Rollback

```python
# AUTONOMOUS mode: Auto-rollback on failure
config = {
    "execution_mode": ExecutionMode.AUTONOMOUS,
    "enable_rollback": True,
    "auto_checkpoint": True
}

orchestrator = ExecutionOrchestrator(config=config)
result = orchestrator.execute(context)

if not result.success:
    # Automatically rolled back to last checkpoint
    print(f"Rolled back: {result.data.get('rolled_back')}")
    print(f"Checkpoint: {result.data.get('checkpoint_restored')}")
```

### Git Checkpoints (Planning Integration)

```python
from src.orchestrators.planning import PlanningOrchestrator

# Planning orchestrator creates git checkpoints per phase
orchestrator = PlanningOrchestrator(config={
    "git_checkpoints_enabled": True,
    "autonomous_execution": True
})

result = orchestrator.execute(feature_name="user-auth")

# Execution fails at phase 5
# Rollback: git checkout checkpoint_phase4_abc123

# 13 checkpoint methods available:
# - create_checkpoint_for_phase()
# - restore_checkpoint()
# - list_checkpoints()
# - create_emergency_checkpoint()
# - etc.
```

### Manual Recovery

```python
# List available checkpoints
checkpoints = orchestrator.list_checkpoints()
for cp in checkpoints:
    print(f"{cp['checkpoint_id']}: {cp['phase']} at {cp['timestamp']}")

# Restore specific checkpoint
success = orchestrator.restore_checkpoint("checkpoint_123")

if success:
    # Continue execution from restored phase
    result = orchestrator.execute(context)
```

### Retry Logic

```python
# Automatic retries with exponential backoff
config = {
    "max_retries": 3,
    "retry_delay_seconds": 5.0,
    "retry_backoff_multiplier": 2.0
}

# Retry schedule:
# Attempt 1: immediate
# Attempt 2: +5s delay
# Attempt 3: +10s delay (5 * 2)
# Attempt 4: +20s delay (10 * 2)
```

---

## ✅ Best Practices

### 1. Use Appropriate Execution Mode

```python
# Development: SUPERVISED (learn patterns)
config = {"execution_mode": ExecutionMode.SUPERVISED}

# CI/CD: AUTONOMOUS (full automation)
config = {"execution_mode": ExecutionMode.AUTONOMOUS}

# Production: MANUAL (maximum control)
config = {"execution_mode": ExecutionMode.MANUAL}
```

### 2. Enable Checkpoints for Long Operations

```python
# For plans with >5 phases, enable checkpoints
config = {
    "enable_rollback": True,
    "auto_checkpoint": True
}
```

### 3. Register Validators for Critical Phases

```python
# Validate before deployment
orchestrator.register_validator("deployment", deployment_validator)

# Validate after testing
orchestrator.register_validator("testing", coverage_validator)
```

### 4. Use Sub-Orchestrators for Specialized Logic

```python
# TDD orchestrator for test phases
orchestrator.register_sub_orchestrator("tdd", tdd_orchestrator)

# Don't reinvent the wheel - use existing orchestrators
```

### 5. Handle Errors Gracefully

```python
result = orchestrator.execute(context)

if not result.success:
    # Log errors
    for error in result.errors:
        logger.error(f"Execution error: {error}")
    
    # Check if rollback occurred
    if result.data.get("rolled_back"):
        logger.info("Auto-rollback successful")
    
    # Attempt manual recovery
    recovery_result = attempt_recovery(result)
```

### 6. Monitor Phase Progress

```python
# Log phase transitions for observability
# Engagement hints automatically logged:
# 🎭 Phase transition: DISCOVER → DESIGN
# 🎭 Phase transition: DESIGN → IMPLEMENT

# Add custom metrics
for phase_result in result.phase_results:
    metrics.record_phase_duration(
        phase_result.phase_name,
        phase_result.duration_ms
    )
```

### 7. Structure Plans Clearly

```python
# Good plan structure
execution_plan = {
    "name": "descriptive-name",
    "version": "1.0",
    "phases": [
        {
            "name": "discovery",
            "description": "Clear description",
            "dependencies": [],
            "success_criteria": ["criteria1", "criteria2"]
        }
    ]
}

# Bad plan structure
execution_plan = {
    "phases": [{"name": "do_stuff"}]  # Too vague
}
```

### 8. Test Execution Locally First

```python
# Test with MANUAL mode before AUTONOMOUS
config = {"execution_mode": ExecutionMode.MANUAL}
orchestrator = ExecutionOrchestrator(config=config)

# Step through phases
for phase in execution_plan["phases"]:
    result = orchestrator.execute_phase(phase["name"])
    if not result.success:
        break  # Fix issues before full automation
```

---

## 📚 Additional Resources

### Documentation
- **Base Orchestrator Guide:** `cortex-brain/documents/guides/BASE-ORCHESTRATOR-DEVELOPER-GUIDE.md`
- **Migration Guide:** `cortex-brain/documents/guides/CORTEX-3.0-TO-4.0-MIGRATION-GUIDE.md`
- **Release Notes:** `cortex-brain/documents/guides/RELEASE-NOTES-v4.0-GA.md`
- **API Docs:** `docs/orchestration_4_0/execution_orchestrator/`

### Examples
- **Execution Orchestrator Source:** `src/orchestration_4_0/orchestrators/execution/execution_orchestrator.py`
- **Planning Integration:** `src/orchestrators/planning/planning_orchestrator.py`
- **TDD Integration:** `src/orchestrators/tdd/tdd_orchestrator_v4_migrated.py`

### Related Systems
- **Planning System 2.0:** `planning-system-2.0-manifest.yaml`
- **TDD Mastery v4.0:** `src/orchestrators/tdd/`
- **Adaptive Execution:** `src/operations/modules/orchestration/adaptive_execution.py`

---

## 🔗 Quick Reference

### Essential Imports
```python
from src.orchestration_4_0.orchestrators.execution import (
    ExecutionOrchestrator,
    ExecutionResult,
    PhaseResult,
    PhaseStatus
)
from src.operations.modules.orchestration.adaptive_execution import ExecutionMode
```

### Minimal Usage
```python
orchestrator = ExecutionOrchestrator(config={
    "execution_mode": ExecutionMode.SUPERVISED
})

result = orchestrator.execute(context={
    "plan": execution_plan,
    "workspace": workspace_path
})
```

### Full-Featured Usage
```python
orchestrator = ExecutionOrchestrator(
    logger=logger,
    config={
        "execution_mode": ExecutionMode.AUTONOMOUS,
        "max_retries": 3,
        "enable_rollback": True,
        "auto_checkpoint": True,
        "enable_safety_checks": True
    },
    knowledge_graph=knowledge_graph
)

# Register sub-orchestrators
orchestrator.register_sub_orchestrator("tdd", tdd_orchestrator)
orchestrator.register_sub_orchestrator("planning", planning_orchestrator)

# Register validators
orchestrator.register_validator("testing", test_validator)

# Execute with full features
result = await orchestrator.enhanced_setup(context)
result = orchestrator.execute(context)
```

---

**Happy Executing! 🚀**

**Version:** 1.0.0  
**Last Updated:** December 25, 2025  
**Author:** Asif Hussain
