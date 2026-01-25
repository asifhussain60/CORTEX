# ============================================================================
# PlannerOrchestrator Autonomous Execution with ASCII Progress Bars
# AC-PLANNER-ASYNC-001: Implementation Guide for Active → Executing Flow
# ============================================================================

"""
This document provides concrete code patterns for implementing the
autonomous execution flow with ASCII progress tracking.
"""

---

## IMPLEMENTATION ARCHITECTURE

### Phase 1: TEMP Creation (Synchronous)
```python
# In PlannerOrchestrator.create_temp_plan()
result = planner.create_temp_plan({
    "description": "Add type hints to util.py",
    "scope": "file",
    "impact": "low",
    "confidence": 0.95
})

# Returns: PlanYamlState.TEMP YAML with:
# - LENS classification: REFACTOR (0.90 confidence)
# - Git context: branch, status, recent commits
# - Challenges: [] (empty - no governance issues)
# - Execution gate: AUTO_EXECUTE (low impact + high confidence)
```

### Phase 2: Approval Flow (Synchronous)
```python
# Display DoR checklist to user
def display_dor_checklist(plan: Dict[str, Any]) -> bool:
    """
    Display Definition of Ready checklist.
    Returns: True if user approves, False otherwise
    """
    print("✓ Request description: ✅")
    print("✓ Scope defined (file): ✅")
    print("✓ Impact specified (low): ✅")
    print("✓ LENS classification: REFACTOR ✅")
    print("✓ Execution gate: AUTO_EXECUTE ✅")
    print("✓ No blocking challenges: ✅")
    print()
    print("Ready to approve? [Y/N]: ", end="")
    response = input().strip().upper()
    return response == "Y"

# If approved, move TEMP → ACTIVE
if display_dor_checklist(plan):
    result = planner.approve_plan(plan_id)
    # Plan is now ACTIVE and locked (no modifications allowed)
```

### Phase 3: Autonomous Execution (Asynchronous with Progress)
```python
# When user initiates execution or execution gate is AUTO_EXECUTE
async def execute_plan_with_progress(plan_id: str) -> Result:
    """
    Execute plan with ASCII progress tracking.
    Orchestrates full lifecycle from ACTIVE → EXECUTING → EXECUTED
    """
    
    # Phase 3a: Gate enforcement
    plan = planner.get_active_plan(plan_id)
    gate = ExecutionGate(**plan["execution_gates"])
    
    if gate.gate_type == ExecutionGateType.BLOCKED:
        return Err(f"Execution blocked: {gate.reason}")
    
    if gate.requires_confirmation and not get_user_confirmation():
        return Ok({"status": "awaiting_confirmation"})
    
    # Phase 3b: Initialize progress tracker
    progress_tracker = ProgressTracker(
        plan_id=plan_id,
        phases=EXECUTION_PHASES,  # 6 phases with weights
        total_estimated_time=estimate_execution_time(plan)
    )
    
    # Phase 3c: Mark as EXECUTING and start async execution
    plan["status"] = PlanYamlState.EXECUTING.value
    planner._update_plan_state(plan_id, plan)
    
    # Start execution in background thread
    execution_thread = threading.Thread(
        target=_execute_plan_background,
        args=(plan_id, progress_tracker),
        daemon=False
    )
    execution_thread.start()
    
    # Phase 3d: Display live progress bars
    while execution_thread.is_alive():
        display_progress_bar(progress_tracker)
        time.sleep(0.5)  # Refresh every 500ms
    
    # Phase 3e: Wait for completion and display final results
    execution_thread.join()
    result = progress_tracker.get_final_result()
    display_completion_summary(result)
    
    return result


def _execute_plan_background(plan_id: str, progress: ProgressTracker) -> None:
    """
    Background thread: Execute plan and update progress tracker.
    """
    try:
        plan = planner.get_active_plan(plan_id)
        classification = plan["classification"]
        handler_name = classification["handler"]
        
        # Get routing orchestrator
        registry = get_database_registry()
        handler_result = registry.get(handler_name)
        
        if handler_result.is_err():
            progress.mark_failed(f"Handler not found: {handler_name}")
            return
        
        handler = handler_result.unwrap()
        
        # Execute with progress updates
        for phase in progress.phases:
            progress.enter_phase(phase.name)
            
            # Phase-specific execution
            if phase.name == "INITIALIZE":
                _execute_phase_initialize(handler, progress)
            elif phase.name == "VALIDATE":
                _execute_phase_validate(plan, progress)
            elif phase.name == "PREPARE":
                _execute_phase_prepare(handler, plan, progress)
            elif phase.name == "EXECUTE":
                _execute_phase_execute(handler, plan, progress)
            elif phase.name == "VERIFY":
                _execute_phase_verify(plan, progress)
            elif phase.name == "FINALIZE":
                _execute_phase_finalize(plan_id, plan, progress)
        
        progress.mark_success()
        
    except Exception as e:
        progress.mark_failed(str(e))


def display_progress_bar(progress: ProgressTracker) -> None:
    """
    Display ASCII progress bar with live updates.
    """
    elapsed = progress.elapsed_seconds()
    eta = progress.estimated_remaining_seconds()
    percentage = progress.percentage()
    bar = progress.ascii_bar()
    
    output = f"""
┌────────────────────────────────────────────────────────────┐
│ 🚀 PLAN EXECUTION: {progress.plan_id}                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ PHASE: {progress.current_phase():15} {PHASE_EMOJIS[progress.current_phase()]}        │
│ Progress: {bar} {percentage:3.0f}%                     │
│                                                             │
│ Status: {progress.status_emoji()} {progress.status_text():20}             │
│ Duration: {elapsed:6.1f}s / {progress.total_estimated:6.1f}s estimate       │
│ ETA: {eta:6.1f}s remaining                                │
│                                                             │
│ Last Action: {progress.last_action:40}              │
│ Current Step: {progress.current_step:40}               │
│                                                             │
└────────────────────────────────────────────────────────────┘
    """
    
    # Clear screen and print (or use carriage return for in-place update)
    print("\r" * 4 + output)

```

---

## PROGRESS TRACKER IMPLEMENTATION

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import time

class ExecutionPhase(Enum):
    INITIALIZE = "initialize"
    VALIDATE = "validate"
    PREPARE = "prepare"
    EXECUTE = "execute"
    VERIFY = "verify"
    FINALIZE = "finalize"

@dataclass
class PhaseConfig:
    name: str
    weight: int  # Percentage of total time
    description: str
    emoji: str

@dataclass
class ProgressTracker:
    plan_id: str
    phases: List[PhaseConfig]
    total_estimated: float  # Estimated total time in seconds
    
    start_time: float = field(default_factory=time.time)
    current_phase_index: int = 0
    phase_start_times: dict = field(default_factory=dict)
    last_action: str = "Initializing"
    current_step: str = "Starting execution"
    status_: str = "executing"  # executing, success, failure
    error_message: Optional[str] = None
    
    status_emoji_map = {
        "executing": "🔄",
        "success": "✅",
        "failure": "❌",
        "blocked": "🚫",
    }
    
    phase_emoji_map = {
        "INITIALIZE": "⚙️",
        "VALIDATE": "✓",
        "PREPARE": "📦",
        "EXECUTE": "▶️",
        "VERIFY": "🔍",
        "FINALIZE": "✨",
    }
    
    def enter_phase(self, phase_name: str) -> None:
        """Called when entering a new execution phase."""
        self.phase_start_times[phase_name] = time.time()
        # Find phase index
        for i, phase in enumerate(self.phases):
            if phase.name == phase_name:
                self.current_phase_index = i
                break
    
    def elapsed_seconds(self) -> float:
        """Total elapsed time since start."""
        return time.time() - self.start_time
    
    def percentage(self) -> float:
        """Calculate progress percentage based on phase weights."""
        elapsed = self.elapsed_seconds()
        return min(100.0, (elapsed / self.total_estimated) * 100)
    
    def estimated_remaining_seconds(self) -> float:
        """Estimate seconds remaining."""
        elapsed = self.elapsed_seconds()
        if self.percentage() > 0:
            estimated_total = elapsed / (self.percentage() / 100)
            remaining = max(0, estimated_total - elapsed)
            return remaining
        return self.total_estimated
    
    def current_phase(self) -> str:
        """Get current phase name."""
        if self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index].name
        return "COMPLETE"
    
    def ascii_bar(self, width: int = 40) -> str:
        """Generate ASCII progress bar."""
        percent = self.percentage() / 100
        filled = int(width * percent)
        bar = "═" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def status_emoji(self) -> str:
        """Return emoji for current status."""
        return self.status_emoji_map.get(self.status_, "❓")
    
    def status_text(self) -> str:
        """Return human-readable status text."""
        status_text_map = {
            "executing": "Executing",
            "success": "SUCCESS",
            "failure": "FAILED",
            "blocked": "BLOCKED",
        }
        return status_text_map.get(self.status_, "Unknown")
    
    def mark_success(self) -> None:
        """Mark execution as successful."""
        self.status_ = "success"
    
    def mark_failed(self, error: str) -> None:
        """Mark execution as failed."""
        self.status_ = "failure"
        self.error_message = error
    
    def update_action(self, action: str) -> None:
        """Update current action being performed."""
        self.last_action = action
    
    def update_step(self, step: str) -> None:
        """Update current step description."""
        self.current_step = step
    
    def get_final_result(self) -> dict:
        """Get final execution result."""
        return {
            "plan_id": self.plan_id,
            "status": self.status_,
            "total_duration_seconds": self.elapsed_seconds(),
            "error_message": self.error_message,
        }

```

---

## EXECUTION PHASE IMPLEMENTATIONS

```python
PHASE_CONFIGS = [
    PhaseConfig(name="INITIALIZE", weight=5, 
                description="Setting up execution environment", emoji="⚙️"),
    PhaseConfig(name="VALIDATE", weight=10,
                description="Validating inputs and preconditions", emoji="✓"),
    PhaseConfig(name="PREPARE", weight=15,
                description="Preparing work area and dependencies", emoji="📦"),
    PhaseConfig(name="EXECUTE", weight=50,
                description="Executing main operations", emoji="▶️"),
    PhaseConfig(name="VERIFY", weight=15,
                description="Verifying results and outputs", emoji="🔍"),
    PhaseConfig(name="FINALIZE", weight=5,
                description="Finalizing and recording results", emoji="✨"),
]

def _execute_phase_initialize(handler, progress: ProgressTracker) -> None:
    """Phase 1: Initialize execution environment."""
    progress.update_action("Initializing handler")
    progress.update_step("Loading execution context")
    
    # Simulate initialization work
    time.sleep(0.2)
    progress.update_step("Setting up logging and monitoring")
    time.sleep(0.1)

def _execute_phase_validate(plan: Dict, progress: ProgressTracker) -> None:
    """Phase 2: Validate inputs and preconditions."""
    progress.update_action("Validating plan structure")
    progress.update_step("Checking required fields")
    
    required_fields = ["request", "classification", "execution_gates"]
    for field in required_fields:
        if field not in plan:
            raise ValueError(f"Missing required field: {field}")
        time.sleep(0.1)
    
    progress.update_step("Verifying git context")
    time.sleep(0.1)

def _execute_phase_prepare(handler, plan: Dict, progress: ProgressTracker) -> None:
    """Phase 3: Prepare work area and dependencies."""
    progress.update_action("Preparing work area")
    progress.update_step("Creating temporary directories")
    time.sleep(0.2)
    
    progress.update_step("Loading dependencies")
    time.sleep(0.2)
    
    progress.update_step("Setting up execution sandbox")
    time.sleep(0.1)

def _execute_phase_execute(handler, plan: Dict, progress: ProgressTracker) -> None:
    """Phase 4: Execute main operations (longest phase)."""
    progress.update_action(f"Executing via {plan['classification']['handler']}")
    
    # Simulate orchestrator execution with multiple steps
    steps = [
        "Parsing request context",
        "Analyzing scope and impact",
        "Executing transformation",
        "Applying changes",
        "Running tests",
    ]
    
    for step in steps:
        progress.update_step(step)
        time.sleep(1.0)  # Simulate work

def _execute_phase_verify(plan: Dict, progress: ProgressTracker) -> None:
    """Phase 5: Verify results and outputs."""
    progress.update_action("Verifying execution results")
    progress.update_step("Checking output validity")
    time.sleep(0.3)
    
    progress.update_step("Running post-execution tests")
    time.sleep(0.3)
    
    progress.update_step("Validating no regressions")
    time.sleep(0.2)

def _execute_phase_finalize(plan_id: str, plan: Dict,
                            progress: ProgressTracker) -> None:
    """Phase 6: Finalize and record results."""
    progress.update_action("Recording execution results")
    progress.update_step("Updating plan state to EXECUTED")
    
    plan["status"] = PlanYamlState.EXECUTED.value
    plan["execution_history"].append({
        "executed_at": datetime.now().isoformat(),
        "duration_ms": int(progress.elapsed_seconds() * 1000),
        "result": "success" if progress.status_ == "success" else "failure",
    })
    
    progress.update_step("Moving to executed_plans directory")
    time.sleep(0.1)
    
    progress.update_step("Generating completion summary")
    time.sleep(0.05)

```

---

## CONFIRMATION GATE IMPLEMENTATION

```python
def display_confirmation_gate(plan: Dict) -> bool:
    """
    Display confirmation gate for operations that require it.
    Returns: True if user confirms, False otherwise
    """
    gate = ExecutionGate(**plan["execution_gates"])
    
    if not gate.requires_confirmation:
        return True  # No confirmation needed
    
    classification = plan["classification"]
    impact = plan["request"].get("impact", "medium")
    
    confirmation_text = f"""
╔════════════════════════════════════════════════════════════╗
║ ⚠️  EXECUTION CONFIRMATION REQUIRED                        ║
╠════════════════════════════════════════════════════════════╣
║                                                             ║
║ Plan: {plan['plan_id']:40}                      ║
║ Intent: {classification['intent']:45} ║
║                                                             ║
║ IMPACT: {'🔴 HIGH' if impact == 'high' else '🟡 MEDIUM' if impact == 'medium' else '🟢 LOW':45} ║
║ CONFIDENCE: {classification['confidence']:.1%}{' ':40}             ║
║ GATE TYPE: {gate.gate_type.value:36}                ║
║                                                             ║
║ {gate.reason[:55]:56}║
║                                                             ║
║ ⏱️  Estimated Duration: {gate.estimated_duration_seconds or 'N/A':33}             ║
║                                                             ║
║ Do you want to proceed? [Y/N]:                             ║
║                                                             ║
╚════════════════════════════════════════════════════════════╝
    """
    
    print(confirmation_text)
    response = input(">>> ").strip().upper()
    return response == "Y"

```

---

## COMPLETE WORKFLOW EXAMPLE

```python
async def complete_workflow_example():
    """
    End-to-end example: User request → TEMP → ACTIVE → EXECUTING → EXECUTED
    """
    planner = PlannerOrchestrator.instance()
    planner.initialize()
    
    # Step 1: Create TEMP plan
    print("\n" + "="*60)
    print("STEP 1: Creating TEMP plan from user request")
    print("="*60)
    
    user_request = {
        "description": "Add type hints to util.py module",
        "scope": "file",
        "impact": "low",
        "confidence": 0.95,
    }
    
    temp_result = planner.create_temp_plan(user_request)
    if temp_result.is_err():
        print(f"❌ Failed to create TEMP plan: {temp_result.unwrap_err()}")
        return
    
    plan = temp_result.unwrap()
    plan_id = plan["plan_id"]
    print(f"✅ TEMP plan created: {plan_id}")
    print(f"   Status: {plan['status']}")
    print(f"   Intent: {plan['classification']['intent']}")
    print(f"   Challenges: {len(plan['challenges'])}")
    
    # Step 2: Display DoR and get approval
    print("\n" + "="*60)
    print("STEP 2: DoR Validation & Approval")
    print("="*60)
    
    # Display TEMP YAML context
    print("\n📋 TEMP PLAN CONTEXT:")
    print(yaml.dump(plan, default_flow_style=False))
    
    # Check for blocking challenges
    blocking_challenges = [c for c in plan['challenges'] 
                          if c.get('can_proceed_without_addressing', False) == False]
    
    if blocking_challenges:
        print("\n🚨 BLOCKING CHALLENGES:")
        for challenge in blocking_challenges:
            print(f"  - {challenge['title']}")
            print(f"    Recommendation: {challenge['recommendation']}")
    else:
        print("\n✅ No blocking challenges")
    
    # Approval flow
    if not display_dor_checklist(plan):
        print("❌ User rejected the plan")
        return
    
    # Step 3: Move to ACTIVE
    print("\n" + "="*60)
    print("STEP 3: Moving to ACTIVE state (locked)")
    print("="*60)
    
    approval_result = planner.approve_plan(plan_id)
    if approval_result.is_err():
        print(f"❌ Approval failed: {approval_result.unwrap_err()}")
        return
    
    active_plan = approval_result.unwrap()
    print(f"✅ Plan approved and moved to ACTIVE")
    print(f"   Status: {active_plan['status']}")
    print(f"   Execution Gate: {active_plan['execution_gates']['gate_type']}")
    
    # Step 4: Execute with progress tracking
    print("\n" + "="*60)
    print("STEP 4: Autonomous Execution with ASCII Progress")
    print("="*60 + "\n")
    
    execution_result = await execute_plan_with_progress(plan_id)
    
    if execution_result.is_err():
        print(f"❌ Execution failed: {execution_result.unwrap_err()}")
        return
    
    # Step 5: Display completion summary
    print("\n" + "="*60)
    print("STEP 5: Execution Complete")
    print("="*60)
    
    result = execution_result.unwrap()
    print(f"✅ Plan executed successfully")
    print(f"   Duration: {result.get('total_duration_seconds', 0):.2f}s")
    print(f"   Status: {result.get('status')}")
    
    # Step 6: Verify EXECUTED state
    final_plan = planner.get_plan_status(plan_id).unwrap()
    print(f"\n📝 Final plan status: {final_plan['status']}")
    print(f"   Moved to executed_plans/")

# Run the workflow
if __name__ == "__main__":
    asyncio.run(complete_workflow_example())

```

---

## KEY DESIGN PATTERNS

### 1. Synchronous Approval → Asynchronous Execution
```
TEMP Creation (sync)
    ↓
DoR Validation (sync, interactive)
    ↓
Approval (sync, blocking)
    ↓
ACTIVE Lock (sync)
    ↓
Execution (async, non-blocking)
    ├── Background thread
    ├── Progress updates
    └── Live ASCII display
```

### 2. Progress Tracking
- **Phases**: 6 weighted phases with expected duration
- **Live Updates**: Every 500ms with ASCII refresh
- **Calculation**: Percentage = (elapsed / estimated) * 100
- **ETA**: Estimated remaining based on current velocity

### 3. Gate Enforcement
```
TEMP State: No gates (read-write, can modify)
↓
ACTIVE State: Approval gate locked (read-only, cannot modify)
↓
EXECUTING State: Execution gate (auto/confirm/blocked)
↓
EXECUTED State: Immutable (archived for reference)
```

---

## BENEFITS OF THIS ARCHITECTURE

✅ **User Control**: Multi-stage approval before automation kicks in
✅ **Transparency**: Full context visible before execution
✅ **Safety**: Challenging challenges prevent mistakes
✅ **Efficiency**: Auto-execute for low-risk, high-confidence operations
✅ **Feedback**: Real-time ASCII progress for user confidence
✅ **Governance**: Every transition audited with AC-IDs
✅ **Integration**: Routed via InteractionOrchestrator for high-stakes decisions

