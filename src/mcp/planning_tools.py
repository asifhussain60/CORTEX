"""
CORTEX 6.0 - Planning MCP Tools

MCP tool wrappers for Planning Orchestrator v5 operations.
Provides 5 MCP tools for YAML-based plan management.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml


def planning_create(
    name: str,
    description: str,
    workspace_root: str = ".",
    stages: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Create a new YAML-based plan.
    
    Args:
        name: Plan name
        description: Plan description
        workspace_root: Path to workspace (default: current directory)
        stages: Optional list of stages to include
    
    Returns:
        Created plan with plan_id and file path
    """
    try:
        import uuid
        from datetime import datetime
        
        workspace = Path(workspace_root).resolve()
        plans_dir = workspace / "cortex-brain" / "tier1" / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)
        
        plan_id = f"plan-{uuid.uuid4()}"
        
        plan_data = {
            "plan_id": plan_id,
            "name": name,
            "description": description,
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "status": "DRAFT",
            "stages": stages or []
        }
        
        plan_path = plans_dir / f"{plan_id}.yaml"
        with open(plan_path, 'w') as f:
            yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False)
        
        return {
            "success": True,
            "plan_id": plan_id,
            "plan_path": str(plan_path),
            "status": "DRAFT"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def planning_execute(
    plan_id: str,
    workspace_root: str = ".",
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute a plan by ID.
    
    Args:
        plan_id: Plan ID to execute
        workspace_root: Path to workspace (default: current directory)
        dry_run: If True, simulate without making changes
    
    Returns:
        Execution status and results
    """
    try:
        from orchestrators.planning.planning_orchestrator import PlanningOrchestratorV5
        
        workspace = Path(workspace_root).resolve()
        
        orchestrator = PlanningOrchestratorV5(
            workspace_root=workspace,
            dry_run=dry_run
        )
        
        result = orchestrator.execute_plan(plan_id)
        
        return {
            "success": True,
            "dry_run": dry_run,
            "plan_id": plan_id,
            "status": result.status if hasattr(result, 'status') else "EXECUTED",
            "phases_completed": getattr(result, 'phases_completed', 0),
            "message": getattr(result, 'message', "Plan execution complete")
        }
    except ImportError:
        return {
            "success": False,
            "error": "Planning orchestrator not available"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def planning_list(
    workspace_root: str = ".",
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all plans in the workspace.
    
    Args:
        workspace_root: Path to workspace (default: current directory)
        status: Optional filter by status (DRAFT, IN_PROGRESS, COMPLETE)
    
    Returns:
        List of plans with metadata
    """
    try:
        workspace = Path(workspace_root).resolve()
        plans_dir = workspace / "cortex-brain" / "tier1" / "plans"
        
        if not plans_dir.exists():
            return {
                "success": True,
                "plans": [],
                "count": 0
            }
        
        plans = []
        for plan_file in plans_dir.glob("plan-*.yaml"):
            try:
                with open(plan_file) as f:
                    plan_data = yaml.safe_load(f)
                
                # Apply status filter
                if status and plan_data.get("status") != status:
                    continue
                
                plans.append({
                    "plan_id": plan_data.get("plan_id"),
                    "name": plan_data.get("name"),
                    "status": plan_data.get("status"),
                    "created": plan_data.get("created"),
                    "stages_count": len(plan_data.get("stages", []))
                })
            except Exception:
                continue
        
        return {
            "success": True,
            "plans": plans,
            "count": len(plans)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def planning_status(
    plan_id: str,
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Get detailed status of a specific plan.
    
    Args:
        plan_id: Plan ID to check
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        Detailed plan status including stage progress
    """
    try:
        workspace = Path(workspace_root).resolve()
        plan_path = workspace / "cortex-brain" / "tier1" / "plans" / f"{plan_id}.yaml"
        
        if not plan_path.exists():
            return {
                "success": False,
                "error": f"Plan not found: {plan_id}"
            }
        
        with open(plan_path) as f:
            plan_data = yaml.safe_load(f)
        
        # Calculate progress
        stages = plan_data.get("stages", [])
        completed = sum(1 for s in stages if s.get("status") == "COMPLETE")
        
        return {
            "success": True,
            "plan_id": plan_id,
            "name": plan_data.get("name"),
            "status": plan_data.get("status"),
            "description": plan_data.get("description"),
            "created": plan_data.get("created"),
            "total_stages": len(stages),
            "completed_stages": completed,
            "progress_percentage": (completed / len(stages) * 100) if stages else 0,
            "stages": [
                {
                    "name": s.get("name"),
                    "status": s.get("status", "PENDING")
                }
                for s in stages
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def planning_update(
    plan_id: str,
    workspace_root: str = ".",
    status: Optional[str] = None,
    stages: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Update an existing plan.
    
    Args:
        plan_id: Plan ID to update
        workspace_root: Path to workspace (default: current directory)
        status: New status (DRAFT, IN_PROGRESS, COMPLETE, CANCELLED)
        stages: Updated stages list
    
    Returns:
        Updated plan status
    """
    try:
        workspace = Path(workspace_root).resolve()
        plan_path = workspace / "cortex-brain" / "tier1" / "plans" / f"{plan_id}.yaml"
        
        if not plan_path.exists():
            return {
                "success": False,
                "error": f"Plan not found: {plan_id}"
            }
        
        with open(plan_path) as f:
            plan_data = yaml.safe_load(f)
        
        # Apply updates
        if status:
            plan_data["status"] = status
        if stages is not None:
            plan_data["stages"] = stages
        
        # Update timestamp
        from datetime import datetime
        plan_data["last_updated"] = datetime.now().isoformat()
        
        with open(plan_path, 'w') as f:
            yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False)
        
        return {
            "success": True,
            "plan_id": plan_id,
            "status": plan_data["status"],
            "message": "Plan updated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
