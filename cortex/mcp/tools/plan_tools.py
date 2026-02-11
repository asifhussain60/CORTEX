"""
Plan Lifecycle MCP Tools (Phase 54 S3).

Provides MCP tools for /plan command integration with phase lifecycle management.

MCP Tools:
- cortex_plan_setup: Pre-execution phase hook
- cortex_plan_execute_autonomous: Multi-stage autonomous execution
- cortex_plan_teardown: Post-execution cleanup + dashboard sync
- cortex_plan_sync: Manual dashboard synchronization

Author: Asif Hussain
Phase: 54 - MCP Unified Routing
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from cortex.mcp.decorators import mcp_tool
import logging

logger = logging.getLogger(__name__)


@mcp_tool(
    name="cortex_plan_setup",
    description="Pre-execution phase hook for phase lifecycle management",
    parameters={
        "phase_id": "string",
        "repo_path": "string",
        "mode": "string",
    }
)
def cortex_plan_setup(
    phase_id: str,
    repo_path: str = ".",
    mode: str = "production",
) -> Dict[str, Any]:
    """
    Pre-execution phase setup hook.
    
    Validates phase readiness, loads dependencies, and prepares execution context.
    
    Args:
        phase_id: Phase identifier (e.g., "phase-54")
        repo_path: Repository root path
        mode: Execution mode (production, test, dry-run)
        
    Returns:
        Dict with setup_complete, dependencies, context, warnings
    """
    try:
        from cortex.registry.phase_manager import PhaseManager
        
        manager = PhaseManager(repo_path=Path(repo_path))
        
        # Load phase from registry
        phase = manager.get_phase(phase_id)
        if not phase:
            return {
                "status": "error",
                "error": f"Phase not found: {phase_id}",
                "setup_complete": False
            }
        
        # Validate dependencies
        dependencies = manager.get_phase_dependencies(phase_id)
        dependency_status = manager.validate_dependencies(phase_id)
        
        # Check phase status
        if phase.get("status") == "completed":
            return {
                "status": "warning",
                "message": f"Phase {phase_id} already completed",
                "setup_complete": True,
                "allow_rerun": True
            }
        
        # Prepare execution context
        context = {
            "phase_id": phase_id,
            "title": phase.get("title", ""),
            "stages": phase.get("stages", []),
            "dependencies": dependencies,
            "dependency_status": dependency_status,
            "repo_path": repo_path,
            "mode": mode,
        }
        
        return {
            "status": "success",
            "setup_complete": True,
            "phase_id": phase_id,
            "dependencies": dependencies,
            "context": context,
            "warnings": [] if dependency_status else ["Some dependencies not met"]
        }
        
    except Exception as e:
        logger.error(f"Plan setup failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Setup failed: {str(e)}",
            "setup_complete": False
        }


@mcp_tool(
    name="cortex_plan_execute_autonomous",
    description="Multi-stage autonomous phase execution with progress tracking",
    parameters={
        "phase_id": "string",
        "repo_path": "string",
        "stages": "array",
        "max_time_minutes": "integer",
    }
)
def cortex_plan_execute_autonomous(
    phase_id: str,
    repo_path: str = ".",
    stages: Optional[List[str]] = None,
    max_time_minutes: int = 120,
) -> Dict[str, Any]:
    """
    Execute phase autonomously across multiple stages.
    
    Coordinates TDDOrchestrator, MasterOrchestrator, and EnforcementOrchestrator
    to complete phase implementation with tests, validation, and governance.
    
    Args:
        phase_id: Phase identifier
        repo_path: Repository root
        stages: Optional list of specific stages to execute (None = all)
        max_time_minutes: Maximum execution time
        
    Returns:
        Dict with execution_complete, stages_completed, test_results, metrics
    """
    try:
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.registry.phase_manager import PhaseManager
        
        manager = PhaseManager(repo_path=Path(repo_path))
        master = MasterOrchestrator.instance()
        
        # Load phase
        phase = manager.get_phase(phase_id)
        if not phase:
            return {
                "status": "error",
                "error": f"Phase not found: {phase_id}",
                "execution_complete": False
            }
        
        # Get stages to execute
        all_stages = phase.get("stages", [])
        stages_to_execute = stages if stages else [s.get("id") for s in all_stages]
        
        # Execute stages sequentially
        completed_stages = []
        test_results = []
        warnings = []
        
        for stage_id in stages_to_execute:
            try:
                # Find stage definition
                stage_def = next((s for s in all_stages if s.get("id") == stage_id), None)
                if not stage_def:
                    warnings.append(f"Stage not found: {stage_id}")
                    continue
                
                # Execute stage via MasterOrchestrator
                result = master.execute_operation(
                    operation_name="implement_stage",
                    parameters={
                        "phase_id": phase_id,
                        "stage_id": stage_id,
                        "stage_definition": stage_def,
                        "repo_path": repo_path
                    }
                )
                
                # Track completion
                completed_stages.append(stage_id)
                
                # Collect test results
                if isinstance(result, dict) and "tests" in result:
                    test_results.extend(result["tests"])
                    
            except Exception as stage_error:
                logger.error(f"Stage {stage_id} failed: {stage_error}")
                warnings.append(f"Stage {stage_id} failed: {str(stage_error)}")
                break  # Stop on first failure
        
        return {
            "status": "success" if len(completed_stages) == len(stages_to_execute) else "partial",
            "execution_complete": len(completed_stages) == len(stages_to_execute),
            "phase_id": phase_id,
            "stages_requested": stages_to_execute,
            "stages_completed": completed_stages,
            "test_results": test_results,
            "warnings": warnings,
            "metrics": {
                "completion_rate": len(completed_stages) / len(stages_to_execute) if stages_to_execute else 0,
                "tests_passed": len([t for t in test_results if t.get("passed")]),
                "tests_total": len(test_results)
            }
        }
        
    except Exception as e:
        logger.error(f"Autonomous execution failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Execution failed: {str(e)}",
            "execution_complete": False
        }


@mcp_tool(
    name="cortex_plan_teardown",
    description="Post-execution phase cleanup and dashboard synchronization",
    parameters={
        "phase_id": "string",
        "repo_path": "string",
        "execution_status": "string",
        "sync_dashboard": "boolean",
    }
)
def cortex_plan_teardown(
    phase_id: str,
    repo_path: str = ".",
    execution_status: str = "success",
    sync_dashboard: bool = True,
) -> Dict[str, Any]:
    """
    Post-execution teardown and cleanup.
    
    Updates phase status, syncs dashboard, commits progress, and
    performs cleanup operations.
    
    Args:
        phase_id: Phase identifier
        repo_path: Repository root
        execution_status: Execution result (success, partial, failed)
        sync_dashboard: Whether to sync dashboard
        
    Returns:
        Dict with teardown_complete, dashboard_synced, cleanup_actions
    """
    try:
        from cortex.registry.phase_manager import PhaseManager
        from cortex.dashboards.dashboard_generator import DashboardGenerator
        
        manager = PhaseManager(repo_path=Path(repo_path))
        
        # Update phase status
        if execution_status == "success":
            manager.mark_phase_complete(phase_id)
        else:
            manager.update_phase_status(phase_id, "in_progress")
        
        # Sync dashboard if requested
        dashboard_synced = False
        if sync_dashboard:
            try:
                generator = DashboardGenerator(repo_path=Path(repo_path))
                generator.sync_phase_status(phase_id)
                dashboard_synced = True
            except Exception as dash_error:
                logger.warning(f"Dashboard sync failed: {dash_error}")
        
        # Cleanup actions
        cleanup_actions = [
            "Phase status updated",
            "Registry synchronized",
        ]
        
        if dashboard_synced:
            cleanup_actions.append("Dashboard synchronized")
        
        return {
            "status": "success",
            "teardown_complete": True,
            "phase_id": phase_id,
            "execution_status": execution_status,
            "dashboard_synced": dashboard_synced,
            "cleanup_actions": cleanup_actions
        }
        
    except Exception as e:
        logger.error(f"Teardown failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Teardown failed: {str(e)}",
            "teardown_complete": False
        }


@mcp_tool(
    name="cortex_plan_sync",
    description="Manual dashboard synchronization for phase status",
    parameters={
        "phase_id": "string",
        "repo_path": "string",
        "force_refresh": "boolean",
    }
)
def cortex_plan_sync(
    phase_id: Optional[str] = None,
    repo_path: str = ".",
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """
    Manually synchronize dashboard with phase status.
    
    Updates dashboard to reflect current state of phases, stages, and tests.
    
    Args:
        phase_id: Optional specific phase to sync (None = all phases)
        repo_path: Repository root
        force_refresh: Force full dashboard regeneration
        
    Returns:
        Dict with sync_complete, phases_synced, dashboard_path
    """
    try:
        from cortex.dashboards.dashboard_generator import DashboardGenerator
        from cortex.registry.phase_manager import PhaseManager
        
        generator = DashboardGenerator(repo_path=Path(repo_path))
        manager = PhaseManager(repo_path=Path(repo_path))
        
        # Get phases to sync
        if phase_id:
            phases_to_sync = [phase_id]
        else:
            all_phases = manager.list_phases()
            phases_to_sync = [p.get("id") for p in all_phases]
        
        # Sync each phase
        synced_count = 0
        for pid in phases_to_sync:
            try:
                if force_refresh:
                    generator.regenerate_phase_dashboard(pid)
                else:
                    generator.sync_phase_status(pid)
                synced_count += 1
            except Exception as sync_error:
                logger.warning(f"Failed to sync phase {pid}: {sync_error}")
        
        return {
            "status": "success",
            "sync_complete": True,
            "phases_requested": len(phases_to_sync),
            "phases_synced": synced_count,
            "dashboard_path": str(generator.dashboard_root),
            "force_refresh": force_refresh
        }
        
    except Exception as e:
        logger.error(f"Dashboard sync failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Sync failed: {str(e)}",
            "sync_complete": False
        }
