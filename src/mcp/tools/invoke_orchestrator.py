"""
Universal Orchestrator Invocation Tool.

MCP tool for invoking autonomous orchestrators with user requests.
Handles orchestrator loading, execution, error propagation, and result formatting.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from src.mcp.server import mcp_tool
from src.mcp.registry import OrchestratorRegistry


logger = logging.getLogger(__name__)


# Global registry instance (initialized on first use)
_registry: Optional[OrchestratorRegistry] = None


def get_registry() -> OrchestratorRegistry:
    """
    Get or initialize the global orchestrator registry.
    
    Returns:
        OrchestratorRegistry instance
    """
    global _registry
    if _registry is None:
        config_path = "cortex-brain/config/mcp-server.yaml"
        _registry = OrchestratorRegistry(config_path)
        logger.info(f"Initialized orchestrator registry from {config_path}")
    return _registry


@mcp_tool
def invoke_orchestrator(
    orchestrator_name: str,
    user_request: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Invoke an autonomous orchestrator with a user request.
    
    This is the universal MCP tool for CORTEX autonomous orchestrator execution.
    CORTEX routes the intent, invokes this tool, and STOPS. The orchestrator
    Python code executes autonomously.
    
    Args:
        orchestrator_name: Name of orchestrator (e.g., "planning_system")
        user_request: User's natural language request
        options: Optional execution parameters (e.g., {"mode": "supervised"})
    
    Returns:
        Dictionary with execution results:
        {
            "status": "success" | "error",
            "orchestrator": "planning_system",
            "execution_time": 3.2,
            "artifacts": ["path/to/plan.md", ...],
            "summary": "Created plan with 5 phases...",
            "progress": {"current_phase": 3, "total_phases": 5},
            "error": "Error message if status is error"
        }
    
    Raises:
        ValueError: If orchestrator not found or invalid parameters
        RuntimeError: If orchestrator execution fails critically
    """
    start_time = time.time()
    options = options or {}
    
    logger.info(f"Invoking orchestrator: {orchestrator_name}")
    logger.info(f"User request: {user_request[:100]}...")
    
    # Get registry
    try:
        registry = get_registry()
    except Exception as e:
        error_msg = f"Failed to initialize orchestrator registry: {e}"
        logger.error(error_msg)
        return {
            "status": "error",
            "orchestrator": orchestrator_name,
            "execution_time": time.time() - start_time,
            "error": error_msg
        }
    
    # Check if orchestrator exists
    if not registry.exists(orchestrator_name):
        available = ", ".join(registry.list_orchestrators())
        error_msg = (
            f"Orchestrator '{orchestrator_name}' not found. "
            f"Available: {available}"
        )
        logger.error(error_msg)
        return {
            "status": "error",
            "orchestrator": orchestrator_name,
            "execution_time": time.time() - start_time,
            "error": error_msg
        }
    
    # Get orchestrator definition
    definition = registry.get(orchestrator_name)
    if definition.type != "autonomous":
        error_msg = (
            f"Orchestrator '{orchestrator_name}' is not autonomous "
            f"(type: {definition.type}). Only autonomous orchestrators "
            "can be invoked via MCP."
        )
        logger.error(error_msg)
        return {
            "status": "error",
            "orchestrator": orchestrator_name,
            "execution_time": time.time() - start_time,
            "error": error_msg
        }
    
    # Instantiate orchestrator
    try:
        orchestrator = registry.instantiate(orchestrator_name)
        if orchestrator is None:
            error_msg = f"Failed to instantiate orchestrator '{orchestrator_name}'"
            logger.error(error_msg)
            return {
                "status": "error",
                "orchestrator": orchestrator_name,
                "execution_time": time.time() - start_time,
                "error": error_msg
            }
    except Exception as e:
        error_msg = f"Error instantiating orchestrator '{orchestrator_name}': {e}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "error",
            "orchestrator": orchestrator_name,
            "execution_time": time.time() - start_time,
            "error": error_msg
        }
    
    # Execute orchestrator
    try:
        logger.info(f"Executing orchestrator: {orchestrator_name}")
        
        # Call orchestrator's execute method with user request and options
        result = orchestrator.execute(
            user_request=user_request,
            options=options
        )
        
        execution_time = time.time() - start_time
        
        logger.info(
            f"Orchestrator '{orchestrator_name}' completed in {execution_time:.2f}s"
        )
        
        # Handle OrchestratorResult object (has .data attribute) or dict
        if hasattr(result, 'data'):
            result_data = result.data or {}
            artifacts = result_data.get("artifacts", [])
            summary = result.message or "Execution completed"
            metadata = result_data
        else:
            # Legacy dict format
            result_data = result or {}
            artifacts = result_data.get("artifacts", [])
            summary = result_data.get("summary", "Execution completed")
            metadata = result_data.get("metadata", {})
        
        # Format result
        return {
            "status": "success",
            "orchestrator": orchestrator_name,
            "execution_time": execution_time,
            "artifacts": artifacts,
            "summary": summary,
            "progress": result_data.get("progress", {}),
            "metadata": metadata
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Orchestrator execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            "status": "error",
            "orchestrator": orchestrator_name,
            "execution_time": execution_time,
            "error": error_msg,
            "traceback": str(e)
        }


def reload_registry() -> Dict[str, Any]:
    """
    Reload the orchestrator registry (for hot-reload support).
    
    Returns:
        Dictionary with reload status and statistics
    """
    global _registry
    
    try:
        if _registry is None:
            _registry = get_registry()
        else:
            _registry.reload()
        
        stats = _registry.get_statistics()
        
        return {
            "status": "success",
            "message": "Registry reloaded successfully",
            "statistics": stats
        }
        
    except Exception as e:
        error_msg = f"Failed to reload registry: {e}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "error",
            "error": error_msg
        }


def list_orchestrators() -> Dict[str, Any]:
    """
    List all registered orchestrators.
    
    Returns:
        Dictionary with orchestrator list and statistics
    """
    try:
        registry = get_registry()
        stats = registry.get_statistics()
        
        orchestrators = {}
        for name in registry.list_orchestrators():
            definition = registry.get(name)
            orchestrators[name] = {
                "type": definition.type,
                "class": definition.class_name,
                "description": definition.description
            }
        
        return {
            "status": "success",
            "orchestrators": orchestrators,
            "statistics": stats
        }
        
    except Exception as e:
        error_msg = f"Failed to list orchestrators: {e}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "error",
            "error": error_msg
        }
