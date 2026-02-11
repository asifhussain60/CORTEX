"""
CORTEX Audit Cohesion MCP Tool
Phase 39 - Unified audit execution for P1.5 (Cohesion) + P1.6 (Future-Vision)
"""

# AC_START: AC-PHASE39-023
# Description: MCP tool registration for unified audit suite
# Related: P1.5-001 through P1.5-015, P1.6-001 through P1.6-002

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.orchestrators.audit.agent_health_validator import AgentHealthValidator
from cortex.orchestrators.audit.audit_mode_integrator import AUDITModeIntegrator
from cortex.orchestrators.audit.module_cohesion_validator import ModuleCohesionValidator
from cortex.orchestrators.audit.orchestrator_integrity_validator import (
    OrchestratorIntegrityValidator,
)
from cortex.orchestrators.audit.prompt_cohesion_validator import PromptCohesionValidator
from cortex.orchestrators.audit.team_collaboration_validator import (
    TeamCollaborationValidator,
)
from cortex.orchestrators.audit.tech_stack_evolution_planner import (
    TechStackEvolutionPlanner,
)
from cortex.orchestrators.audit.test_validity_validator import TestValidityValidator


def cortex_audit_cohesion(
    repo_root: Optional[str] = None,
    priority_filters: Optional[List[str]] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Execute unified audit suite for cohesion and future-vision checks.

    Args:
        repo_root: Repository root path (defaults to current directory)
        priority_filters: Filter by priority (e.g., ["P1.5", "P1.6"])
        verbose: Include detailed issue information

    Returns:
        Audit report with validation results

    Example:
        >>> result = cortex_audit_cohesion()
        >>> print(f"Status: {result['status']}")
        >>> print(f"Total issues: {result['summary']['total_issues']}")
    """
    start_time = time.time()

    # Resolve repo root
    root_path = Path(repo_root) if repo_root else Path.cwd()

    # Initialize integrator
    integrator = AUDITModeIntegrator(repo_root=root_path)

    # Register all Phase 39 validators (with repo_root parameter)
    integrator.register_validator(PromptCohesionValidator(root_path))
    integrator.register_validator(AgentHealthValidator(root_path))
    integrator.register_validator(OrchestratorIntegrityValidator(root_path))
    integrator.register_validator(ModuleCohesionValidator(root_path))
    integrator.register_validator(TestValidityValidator(root_path))
    integrator.register_validator(TeamCollaborationValidator(root_path))
    integrator.register_validator(TechStackEvolutionPlanner(root_path))

    # Run full audit
    report = integrator.run_full_audit()

    # Build response from Dict report
    return {
        "status": "success" if report["success"] else "issues_found",
        "execution_time_seconds": round(time.time() - start_time, 2),
        "summary": {
            "total_issues": report["summary"]["issues"],
            "validators_run": report["summary"]["validators"],
            "checks_executed": report["summary"]["checks"],
            "execution_duration": report["summary"]["time"],
            "meets_performance_target": report["success"]
        },
        "validation_results": report["issues"] if verbose else {
            "issue_count": report["summary"]["issues"]
        },
        "raw_report": report if verbose else None
    }


# MCP Tool Metadata
TOOL_METADATA = {
    "name": "cortex_audit_cohesion",
    "description": "Execute unified audit suite for Phase 39 cohesion and future-vision checks",
    "category": "audit",
    "phase": 39,
    "priority": "P1.5",
    "parameters": {
        "repo_root": {
            "type": "string",
            "description": "Repository root path (optional)",
            "required": False
        },
        "priority_filters": {
            "type": "array",
            "description": "Filter by priority (P1.5, P1.6)",
            "required": False
        },
        "verbose": {
            "type": "boolean",
            "description": "Include detailed issue information",
            "required": False,
            "default": False
        }
    },
    "returns": {
        "type": "object",
        "properties": {
            "status": "success | issues_found",
            "execution_time_seconds": "float",
            "summary": {
                "total_issues": "int",
                "validators_run": "int",
                "execution_duration": "float",
                "meets_performance_target": "bool"
            },
            "validation_results": "dict",
            "timestamp": "str"
        }
    },
    "examples": [
        {
            "description": "Run full Phase 39 audit",
            "code": 'cortex_audit_cohesion()'
        },
        {
            "description": "Run P1.5 checks only",
            "code": 'cortex_audit_cohesion(priority_filters=["P1.5"])'
        },
        {
            "description": "Run with verbose output",
            "code": 'cortex_audit_cohesion(verbose=True)'
        }
    ]
}

# AC_COMPLETE: AC-PHASE39-023 ✅ MCP tool registered with unified audit integration
