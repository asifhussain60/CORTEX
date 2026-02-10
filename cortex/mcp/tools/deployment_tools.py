"""
Deployment MCP Tool - Production Deployment Orchestration

AC-ID: HOLISTIC-REGISTRY-002
Purpose: Expose DeploymentOrchestrator via MCP for production deployment
         Bridge the gap identified in orchestrator registry analysis

Author: Asif Hussain  
Date: 2026-02-10
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from typing import Dict, Any, Optional
import logging

from cortex.core.result import Result, Ok, Err

logger = logging.getLogger(__name__)


def cortex_deploy_to_production(
    deployment_type: str = "full",
    target_branch_cortex: str = "CORTEX",
    target_branch_main: str = "main",
    version_bump_type: str = "patch",
    dry_run: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Deploy CORTEX to production with comprehensive validation.
    
    This MCP tool exposes the DeploymentOrchestrator capabilities
    to handle "deploy to production" requests automatically.
    
    Args:
        deployment_type: Type of deployment (full, patch, hotfix)
        target_branch_cortex: Target CORTEX branch (default: CORTEX)
        target_branch_main: Target main branch (default: main)
        version_bump_type: Version bump type (major, minor, patch)
        dry_run: If True, simulate deployment without actual changes
        **kwargs: Additional deployment configuration
        
    Returns:
        Dictionary with deployment results and status
        
    Example:
        result = cortex_deploy_to_production(
            deployment_type="full",
            version_bump_type="minor",
            dry_run=False
        )
        if result["success"]:
            print(f"Deployed version {result['version_new']}")
    """
    try:
        # Import DeploymentOrchestrator
        from cortex.orchestrators.core.deployment_orchestrator import (
            DeploymentOrchestrator, 
            DeploymentConfig
        )
        
        # Create deployment configuration
        config = DeploymentConfig(
            deployment_type=deployment_type,
            target_branch_cortex=target_branch_cortex,
            target_branch_main=target_branch_main,
            version_bump_type=version_bump_type,
            dry_run=dry_run,
            **kwargs
        )
        
        # Initialize deployment orchestrator
        orchestrator = DeploymentOrchestrator()
        
        # Execute deployment
        logger.info(f"Starting {deployment_type} deployment (dry_run={dry_run})")
        
        result = orchestrator.deploy_to_production(config)
        
        # Convert result to dictionary
        response = {
            "success": result.success,
            "phase_reached": result.phase_reached,
            "duration_seconds": result.duration_seconds,
            "version_old": result.version_old,
            "version_new": result.version_new,
            "ac_id": result.ac_id,
        }
        
        # Add detailed results if available
        if result.pre_flight:
            response["pre_flight"] = {
                "passed": result.pre_flight.passed,
                "readiness_score": result.pre_flight.readiness_score,
                "test_results": result.pre_flight.test_results,
                "challenges": result.pre_flight.challenges,
            }
        
        if result.errors:
            response["errors"] = result.errors
        
        if result.cortex_branch:
            response["cortex_branch"] = {
                "success": result.cortex_branch.success,
                "commits_pushed": result.cortex_branch.commits_pushed,
                "files_modified": result.cortex_branch.files_modified,
            }
        
        if result.main_branch:
            response["main_branch"] = {
                "success": result.main_branch.success,
                "commits_pushed": result.main_branch.commits_pushed,
                "files_modified": result.main_branch.files_modified,
            }
        
        logger.info(f"Deployment {'completed' if result.success else 'failed'}")
        
        return response
        
    except ImportError as e:
        error_msg = f"DeploymentOrchestrator not available: {e}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "phase_reached": "import_error",
        }
    
    except Exception as e:
        error_msg = f"Deployment failed: {e}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "error": error_msg,
            "phase_reached": "execution_error",
        }


def cortex_deployment_health_check() -> Dict[str, Any]:
    """
    Check deployment readiness and health.
    
    Returns:
        Dictionary with health check results
    """
    try:
        from cortex.mcp.tools.deployment.health_checker import HealthChecker
        
        checker = HealthChecker()
        health = checker.check_deployment_readiness()
        
        return {
            "success": True,
            "health": health,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def cortex_deployment_canary(
    version: str,
    percentage: int = 10
) -> Dict[str, Any]:
    """
    Start canary deployment.
    
    Args:
        version: Version to deploy
        percentage: Percentage of traffic (10, 50, or 100)
        
    Returns:
        Dictionary with canary deployment results
    """
    try:
        from cortex.mcp.tools.deployment.canary_deployer import CanaryDeployer
        
        deployer = CanaryDeployer()
        
        if percentage == 10:
            result = deployer.start_canary(version)
        else:
            result = deployer.promote(percentage)
        
        return {
            "success": True,
            "canary_result": result,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }