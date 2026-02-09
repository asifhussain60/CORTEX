"""
Plan Management MCP Tool - Phase 25 Stage 4 + Phase 40 Autonomous Execution

Exposes PLAN MODE operations via MCP for phase CRUD,
setup/teardown hooks, dashboard synchronization, and
AUTONOMOUS MULTI-STAGE EXECUTION with ASCII progress bars.

AC-ID: PHASE-25-STAGE-4-002
AC-ID: PHASE-40-AUTONOMOUS-EXECUTION-001
"""

from typing import Dict, Any, Callable, Optional
import logging
import asyncio
import sys
from pathlib import Path

from cortex.mcp.decorators import mcp_tool
from cortex.orchestrators.support.plan_orchestrator import PlanOrchestrator
from cortex.orchestrators.planning.autonomous_plan_executor import AutonomousPlanExecutor
from cortex.orchestrators.domain.autonomous_execution_engine import (
    AutonomousExecutionEngine,
    PlanSpecification,
    PhaseDefinition,
    ExecutionEvent,
    ExecutionEventType
)
from cortex.core.result import Result, Ok, Err

logger = logging.getLogger(__name__)

# Global orchestrator instance (lazy initialization)
_orchestrator_cache: Dict[str, PlanOrchestrator] = {}


def _get_orchestrator(registry_root: str = "cortex-registry/_cortex-master") -> PlanOrchestrator:
    """Get or create PlanOrchestrator instance."""
    if registry_root not in _orchestrator_cache:
        _orchestrator_cache[registry_root] = PlanOrchestrator(registry_root=registry_root)
    return _orchestrator_cache[registry_root]


@mcp_tool(
    name="cortex_plan_setup",
    description="Execute setup hook before phase implementation",
    category="plan_management"
)
def cortex_plan_setup(
    phase_id: str,
    registry_root: str = "cortex-registry/_cortex-master"
) -> Dict[str, Any]:
    """
    Execute setup hook before phase implementation.
    
    Steps:
    1. Load phase specification
    2. Verify no conflicts
    3. Run VacuumOrchestrator cleanup
    4. Create git checkpoint
    5. Initialize audit trail
    
    Args:
        phase_id: Phase ID to set up
        registry_root: Registry root path
        
    Returns:
        Dict with setup results:
        - success: bool
        - phase_id: str
        - checkpoint_created: bool
        - cleanup_performed: bool
        - error: str (if failed)
    """
    try:
        orchestrator = _get_orchestrator(registry_root)
        result = orchestrator.setup_phase(phase_id)
        
        if result.success:
            return {
                "success": True,
                "phase_id": result.phase_id,
                "checkpoint_created": result.checkpoint_created,
                "cleanup_performed": result.cleanup_performed,
                "message": f"✅ Setup complete for {phase_id}"
            }
        else:
            return {
                "success": False,
                "error": result.error_message,
                "message": f"❌ Setup failed for {phase_id}"
            }
            
    except Exception as e:
        logger.error(f"Setup hook failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Setup hook execution failed"
        }


@mcp_tool(
    name="cortex_plan_teardown",
    description="Execute teardown hook after phase completion",
    category="plan_management"
)
def cortex_plan_teardown(
    phase_id: str,
    registry_root: str = "cortex-registry/_cortex-master"
) -> Dict[str, Any]:
    """
    Execute teardown hook after phase completion.
    
    Steps:
    1. Verify deliverables
    2. Run VacuumOrchestrator cleanup
    3. Archive temporary files
    4. Update dashboard
    5. Log audit trail
    6. Commit changes
    
    Args:
        phase_id: Phase ID to tear down
        registry_root: Registry root path
        
    Returns:
        Dict with teardown results:
        - success: bool
        - artifacts_cleaned: int
        - dashboard_synced: bool
        - audit_logged: bool
        - error: str (if failed)
    """
    try:
        orchestrator = _get_orchestrator(registry_root)
        result = orchestrator.teardown_phase(phase_id)
        
        if result.success:
            return {
                "success": True,
                "artifacts_cleaned": result.artifacts_cleaned,
                "dashboard_synced": result.dashboard_synced,
                "audit_logged": result.audit_logged,
                "message": f"✅ Teardown complete for {phase_id}"
            }
        else:
            return {
                "success": False,
                "error": result.error_message,
                "message": f"❌ Teardown failed for {phase_id}"
            }
            
    except Exception as e:
        logger.error(f"Teardown hook failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Teardown hook execution failed"
        }


@mcp_tool(
    name="cortex_plan_resolve",
    description="Intelligently resolve phase operation from user request",
    category="plan_management"
)
def cortex_plan_resolve(
    user_request: str,
    registry_root: str = "cortex-registry/_cortex-master"
) -> Dict[str, Any]:
    """
    Intelligently resolve phase operation from user request.
    
    Uses 4-step algorithm:
    1. Load context (index.yaml)
    2. Semantic analysis (keywords, components)
    3. Phase matching (score each active phase)
    4. Operation decision (CREATE/UPDATE/DEPRECATE)
    
    Args:
        user_request: User's natural language request
        registry_root: Registry root path
        
    Returns:
        Dict with resolution result:
        - success: bool
        - operation: str (CREATE/UPDATE/DEPRECATE/COMPLETE)
        - matched_phase_idUnion[str, None]
        - match_score: float
        - rationale: str
        - confidence: float
        - error: str (if failed)
    """
    try:
        orchestrator = _get_orchestrator(registry_root)
        result = orchestrator.resolve_phase_operation(user_request)
        
        return {
            "success": True,
            "operation": result.operation.value,
            "matched_phase_id": result.matched_phase_id,
            "match_score": result.match_score,
            "rationale": result.rationale,
            "confidence": result.confidence,
            "message": f"🎯 Resolved: {result.operation.value.upper()}"
        }
        
    except Exception as e:
        logger.error(f"Phase resolution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Phase resolution failed"
        }


@mcp_tool(
    name="cortex_plan_sync",
    description="Manually trigger dashboard sync",
    category="plan_management"
)
def cortex_plan_sync(
    registry_root: str = "cortex-registry/_cortex-master"
) -> Dict[str, Any]:
    """
    Manually trigger dashboard sync.
    
    Updates:
    - plan-summary.json from index.yaml
    - dashboard HTML with current statistics
    
    Args:
        registry_root: Registry root path
        
    Returns:
        Dict with sync results:
        - success: bool
        - message: str
        - error: str (if failed)
    """
    try:
        orchestrator = _get_orchestrator(registry_root)
        success = orchestrator.sync_dashboard()
        
        if success:
            return {
                "success": True,
                "message": "✅ Dashboard synced successfully"
            }
        else:
            return {
                "success": False,
                "message": "❌ Dashboard sync failed"
            }
            
    except Exception as e:
        logger.error(f"Dashboard sync failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Dashboard sync execution failed"
        }


@mcp_tool(
    name="cortex_plan_execute_autonomous",
    description="Execute entire phase autonomously through all stages with ASCII progress bars",
    category="plan_management"
)
def cortex_plan_execute_autonomous(
    phase_id: str,
    registry_root: str = "cortex-registry/_cortex-master",
    timeout_per_stage: int = 1800,  # 30 min per stage
    show_progress: bool = True
) -> Dict[str, Any]:
    """
    Execute entire phase autonomously through ALL stages without stopping.
    
    Features:
    - Zero user approval gates (runs to completion)
    - ASCII progress bars for each stage
    - Automatic TDD RED→GREEN→REFACTOR cycles
    - Real-time progress updates
    - Governance enforcement at each stage
    - Auto-commit at stage boundaries
    - Dashboard auto-sync on completion
    
    Execution Pattern:
    1. Setup hook (cortex_plan_setup)
    2. Load phase specification from registry
    3. Execute each stage sequentially:
       - [██░░░░░░░░]  10% Stage 1: Requirements Analysis
       - [████░░░░░░]  40% Stage 2: Design & Architecture
       - [██████░░░░]  60% Stage 3: Implementation (TDD)
       - [████████░░]  80% Stage 4: Testing & Validation
       - [██████████] 100% Stage 5: Documentation & Completion
    4. Teardown hook (cortex_plan_teardown)
    5. Dashboard sync
    
    Args:
        phase_id: Phase ID to execute (e.g., "phase-38", "phase-40")
        registry_root: Registry root path
        timeout_per_stage: Timeout in seconds per stage (default 30min)
        show_progress: Whether to show ASCII progress bars
        
    Returns:
        Dict with execution results:
        - success: bool
        - phase_id: str
        - stages_completed: int
        - total_stages: int
        - duration_seconds: float
        - test_results: dict (passed, failed, coverage)
        - progress_log: list[str] (ASCII progress bars + status)
        - error: str (if failed)
    
    Example Output:
        {
            "success": True,
            "phase_id": "phase-40",
            "stages_completed": 5,
            "total_stages": 5,
            "duration_seconds": 1834.2,
            "test_results": {
                "passed": 156,
                "failed": 0,
                "coverage": 94.5
            },
            "progress_log": [
                "[██████████] 100% ✅ Stage 1: Requirements Analysis (12.3s)",
                "[██████████] 100% ✅ Stage 2: Design & Architecture (45.1s)",
                "[██████████] 100% ✅ Stage 3: Implementation (TDD) (1456.8s)",
                "[██████████] 100% ✅ Stage 4: Testing & Validation (234.5s)",
                "[██████████] 100% ✅ Stage 5: Documentation (85.5s)"
            ],
            "message": "✅ Phase 40 completed autonomously in 30.6 minutes"
        }
    """
    try:
        # Phase 0: Setup hook
        setup_result = cortex_plan_setup(phase_id, registry_root)
        if not setup_result["success"]:
            return {
                "success": False,
                "error": f"Setup failed: {setup_result.get('error', 'Unknown')}",
                "message": "❌ Setup hook failed"
            }
        
        # Phase 1: Load phase specification
        registry_path = Path(registry_root)
        phase_file = registry_path / "phases" / "active" / f"{phase_id}.yaml"
        
        if not phase_file.exists():
            # Try completed phases
            for year in ["2026", "2025"]:
                phase_file = registry_path / "phases" / "completed" / year / f"{phase_id}.yaml"
                if phase_file.exists():
                    break
        
        if not phase_file.exists():
            return {
                "success": False,
                "error": f"Phase file not found: {phase_id}",
                "message": f"❌ Phase {phase_id} not found in registry"
            }
        
        import yaml
        with open(phase_file, 'r', encoding='utf-8') as f:
            phase_plan = yaml.safe_load(f)
        
        # Phase 2: Build execution plan
        stages = phase_plan.get("stages", [])
        if not stages:
            # Fallback: use tasks as stages
            tasks = phase_plan.get("tasks", [])
            if not tasks:
                return {
                    "success": False,
                    "error": "No stages or tasks defined in phase",
                    "message": f"❌ Phase {phase_id} has no executable stages"
                }
            stages = [{"name": task, "description": task} for task in tasks[:10]]  # Max 10
        
        total_stages = len(stages)
        estimated_hours = phase_plan.get("estimated_hours", total_stages * 0.5)
        duration_per_stage = int((estimated_hours / total_stages) * 60)  # Convert to minutes
        
        # Phase 3: Create PlanSpecification for AutonomousExecutionEngine
        from datetime import datetime
        plan_spec = PlanSpecification(
            plan_id=phase_id,
            name=phase_plan.get("title", f"Phase {phase_id}"),
            description=phase_plan.get("description", ""),
            created_at=datetime.now().isoformat(),
            total_phases=total_stages,
            phases=[
                PhaseDefinition(
                    phase_num=idx + 1,
                    name=stage.get("name", f"Stage {idx + 1}"),
                    description=stage.get("description", ""),
                    duration_estimate=duration_per_stage,
                    deliverables=stage.get("deliverables", []),
                )
                for idx, stage in enumerate(stages)
            ]
        )
        
        # Phase 4: Initialize AutonomousExecutionEngine
        engine = AutonomousExecutionEngine(timeout_per_phase=timeout_per_stage)
        
        # Progress tracking
        progress_log = []
        
        def progress_callback(event: ExecutionEvent):
            """Capture progress events and generate ASCII bars."""
            if not show_progress:
                return
            
            if event.event_type == ExecutionEventType.PHASE_STARTED:
                progress_bar = _generate_progress_bar(0, total_stages, event.phase_num)
                progress_log.append(f"{progress_bar} 🔵 {event.message}")
                print(f"\n{progress_bar} 🔵 {event.message}", flush=True)
                
            elif event.event_type == ExecutionEventType.PHASE_COMPLETE:
                progress_bar = _generate_progress_bar(event.phase_num, total_stages, total_stages)
                duration = event.data.get("duration_seconds", 0)
                progress_log.append(f"{progress_bar} ✅ {event.message} ({duration:.1f}s)")
                print(f"{progress_bar} ✅ {event.message} ({duration:.1f}s)", flush=True)
                
            elif event.event_type == ExecutionEventType.EXECUTION_COMPLETE:
                progress_log.append(f"\n🎉 Execution complete! Total: {event.elapsed_seconds}s")
                print(f"\n🎉 Execution complete! Total: {event.elapsed_seconds}s", flush=True)
        
        # Phase 5: Execute autonomously  
        # Note: execute_plan_autonomously has @inject_orchestrator_context decorator
        # which may convert it to sync. Try calling directly first.
        try:
            # Try as async
            if asyncio.iscoroutinefunction(engine.execute_plan_autonomously):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        engine.execute_plan_autonomously(
                            plan=plan_spec,
                            progress_callback=progress_callback
                        )
                    )
                finally:
                    loop.close()
            else:
                # Call as sync
                result = engine.execute_plan_autonomously(
                    plan=plan_spec,
                    progress_callback=progress_callback
                )
        except Exception as exec_error:
            return {
                "success": False,
                "error": str(exec_error),
                "progress_log": progress_log,
                "message": f"❌ Execution engine error: {exec_error}"
            }
        
        # Check result type
        if hasattr(result, 'is_err') and result.is_err():  # type: ignore
            return {
                "success": False,
                "error": result.unwrap_err() if hasattr(result, 'unwrap_err') else str(result),  # type: ignore
                "progress_log": progress_log,
                "message": f"❌ Phase {phase_id} execution failed"
            }
        
        exec_result = result.unwrap() if hasattr(result, 'unwrap') else result  # type: ignore
        
        # Phase 6: Teardown hook
        teardown_result = cortex_plan_teardown(phase_id, registry_root)
        if not teardown_result["success"]:
            logger.warning(f"Teardown warning: {teardown_result.get('error', 'Unknown')}")
        
        # Phase 7: Dashboard sync
        sync_result = cortex_plan_sync(registry_root)
        if not sync_result["success"]:
            logger.warning(f"Dashboard sync warning: {sync_result.get('error', 'Unknown')}")
        
        # Success response
        if isinstance(exec_result, dict):
            duration_minutes = exec_result.get("total_duration_seconds", 0) / 60
            
            return {
                "success": True,
                "phase_id": phase_id,
                "stages_completed": exec_result.get("phases_completed", 0),
                "total_stages": total_stages,
                "duration_seconds": exec_result.get("total_duration_seconds", 0),
                "test_results": exec_result.get("checkpoint", {}).get("test_results", {}),
                "progress_log": progress_log,
                "dashboard_synced": sync_result["success"],
                "message": f"✅ Phase {phase_id} completed autonomously in {duration_minutes:.1f} minutes"
            }
        else:
            return {
                "success": False,
                "error": "Unexpected result type from execution engine",
                "progress_log": progress_log,
                "message": f"❌ Phase {phase_id} execution returned invalid result"
            }
        
    except Exception as e:
        logger.error(f"Autonomous execution failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"❌ Autonomous execution failed for {phase_id}"
        }


def _generate_progress_bar(completed: int, total: int, current: int) -> str:
    """
    Generate ASCII progress bar.
    
    Args:
        completed: Number of completed stages
        total: Total number of stages
        current: Current stage number
        
    Returns:
        ASCII progress bar string: [████░░░░░░] 40%
    """
    percentage = int((completed / total) * 100) if total > 0 else 0
    filled = int((completed / total) * 10) if total > 0 else 0
    empty = 10 - filled
    
    bar = f"[{'█' * filled}{'░' * empty}] {percentage:3d}%"
    return bar


