"""
Plan Management MCP Tool - Phase 25 Stage 4

Exposes PLAN MODE operations via MCP for phase CRUD,
setup/teardown hooks, and dashboard synchronization.

AC-ID: PHASE-25-STAGE-4-002
"""

from typing import Dict, Any
import logging

from cortex.mcp.decorators import mcp_tool
from cortex.orchestrators.support.plan_orchestrator import PlanOrchestrator

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
        - matched_phase_id: str | None
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

