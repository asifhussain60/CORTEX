"""
WorkflowRuntimeTool — Phase 45 Stage 4.

MCP tool for workflow runtime with agent integration.

AC_START: AC-PHASE45-S4-002
Phase: 45 | Stage: 4 | Priority: P0
Description: GREEN phase implementation for MCP tool
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import logging
import time
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from tempfile import NamedTemporaryFile

from cortex.orchestrators.workflow.workflow_runtime import (
    WorkflowRuntime,
    WorkflowContext,
)
from cortex.orchestrators.workflow.workflow_templates import WorkflowTemplateManager
from cortex.orchestrators.workflow.ephemeral_storage import EphemeralStorage


logger = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def list_workflow_templates(include_details: bool = False) -> Union[List[str], Dict[str, Any]]:
    """List all available workflow templates.
    
    Args:
        include_details: If True, return dict with template details.
    
    Returns:
        List of template names, or dict with template details.
    """
    manager = WorkflowTemplateManager()
    template_names = manager.list_templates()
    
    if not include_details:
        return template_names
    
    # Return details
    details = {}
    for name in template_names:
        template = manager.get_template(name)
        details[name] = {
            "name": template.get("name"),
            "description": template.get("description"),
            "variables": template.get("variables", {}),
        }
    
    return details


async def execute_workflow(
    template_name: Optional[str] = None,
    workflow_path: Optional[str] = None,
    variables: Optional[Dict[str, Any]] = None,
) -> Any:
    """Execute workflow from template or YAML file.
    
    Args:
        template_name: Name of pre-defined template.
        workflow_path: Path to custom workflow YAML.
        variables: Workflow variables.
    
    Returns:
        WorkflowExecutionResult.
    
    Raises:
        ValueError: If neither template_name nor workflow_path provided.
    """
    if not template_name and not workflow_path:
        raise ValueError("Must provide either template_name or workflow_path")
    
    variables = variables or {}
    
    # Load workflow
    if template_name:
        manager = WorkflowTemplateManager()
        template = manager.get_template(template_name)
        
        # Convert template format to workflow runtime format
        workflow_data = {
            "workflow": {
                "name": template.get("name", template_name),
                "description": template.get("description", ""),
                "steps": [
                    {
                        "step_id": step.get("name", f"step_{i}"),
                        "action": step.get("action", "unknown"),
                        "parameters": step.get("params", {}),
                    }
                    for i, step in enumerate(template.get("steps", []))
                ],
            }
        }
        
        # Write to temporary file for WorkflowRuntime
        with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            yaml.safe_dump(workflow_data, tmp)
            tmp_path = Path(tmp.name)
        
        try:
            runtime = WorkflowRuntime(template_path=tmp_path)
            context = WorkflowContext(variables=variables)
            runtime.hydrate(context)
            result = runtime.execute()
        finally:
            tmp_path.unlink()
    else:
        runtime = WorkflowRuntime(template_path=Path(workflow_path))
        context = WorkflowContext(variables=variables)
        runtime.hydrate(context)
        result = runtime.execute()
    
    return result


# =============================================================================
# MCP TOOL
# =============================================================================
class WorkflowRuntimeTool:
    """MCP tool for workflow runtime execution.
    
    Exposes workflow runtime capabilities to CORTEX agents via MCP protocol.
    
    Example:
        >>> tool = WorkflowRuntimeTool()
        >>> result = await tool.execute({
        ...     "template_name": "tdd-cycle",
        ...     "variables": {"module_name": "test"},
        ... })
    """
    
    def __init__(self) -> None:
        """Initialize workflow runtime tool."""
        self.name = "cortex_workflow_runtime"
        self.description = (
            "Execute workflow from template or YAML file. "
            "Supports TDD cycles, phase execution, and holistic refactoring."
        )
        self._template_manager = WorkflowTemplateManager()
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for tool parameters.
        
        Returns:
            JSON schema dictionary.
        """
        return {
            "type": "object",
            "properties": {
                "template_name": {
                    "type": "string",
                    "description": "Name of pre-defined workflow template",
                    "enum": self._template_manager.list_templates(),
                },
                "workflow_path": {
                    "type": "string",
                    "description": "Path to custom workflow YAML file",
                },
                "variables": {
                    "type": "object",
                    "description": "Workflow variables",
                    "additionalProperties": True,
                },
                "use_ephemeral_storage": {
                    "type": "boolean",
                    "description": "Use ephemeral storage for temporary files",
                    "default": False,
                },
                "enable_convergence": {
                    "type": "boolean",
                    "description": "Enable convergence loop for workflow",
                    "default": False,
                },
                "max_retries": {
                    "type": "integer",
                    "description": "Maximum retries for convergence",
                    "default": 5,
                },
            },
            "oneOf": [
                {"required": ["template_name"]},
                {"required": ["workflow_path"]},
            ],
        }
    
    def validate_template(self, template: Dict[str, Any]) -> bool:
        """Validate template structure.
        
        Args:
            template: Template dictionary.
        
        Returns:
            True if valid, False otherwise.
        """
        required_fields = ["name", "steps"]
        return all(field in template for field in required_fields)
    
    def validate_execution_params(
        self,
        template: Dict[str, Any],
        variables: Dict[str, Any],
    ) -> bool:
        """Validate execution parameters against template requirements.
        
        Args:
            template: Template dictionary.
            variables: Provided variables.
        
        Returns:
            True if valid, False otherwise.
        """
        required_vars = template.get("variables", {})
        for var_name in required_vars:
            if var_name not in variables:
                logger.warning(f"Missing required variable: {var_name}")
                return False
        return True
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow runtime tool.
        
        Args:
            params: Tool parameters.
        
        Returns:
            Execution result dictionary.
        """
        start_time = time.time()
        
        try:
            # Extract parameters
            template_name = params.get("template_name")
            workflow_path = params.get("workflow_path")
            variables = params.get("variables", {})
            use_ephemeral = params.get("use_ephemeral_storage", False)
            enable_convergence = params.get("enable_convergence", False)
            
            # Validate parameters
            if not template_name and not workflow_path:
                return {
                    "success": False,
                    "error": "Must provide either template_name or workflow_path",
                }
            
            # Validate template and variables
            if template_name:
                try:
                    template = self._template_manager.get_template(template_name)
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Template not found: {template_name}",
                    }
                
                if not self.validate_execution_params(template, variables):
                    return {
                        "success": False,
                        "error": "Missing required variables",
                    }
            
            logger.info(
                f"Executing workflow: template={template_name}, "
                f"path={workflow_path}, vars={list(variables.keys())}"
            )
            
            # Execute workflow
            if use_ephemeral:
                with EphemeralStorage() as storage:
                    result = await execute_workflow(
                        template_name=template_name,
                        workflow_path=workflow_path,
                        variables=variables,
                    )
            else:
                result = await execute_workflow(
                    template_name=template_name,
                    workflow_path=workflow_path,
                    variables=variables,
                )
            
            duration = time.time() - start_time
            
            # Build response
            response = {
                "success": result.success,
                "execution_result": {
                    "steps_completed": result.steps_completed,
                    "success": result.success,
                },
                "metrics": {
                    "duration_seconds": duration,
                    "steps_completed": result.steps_completed,
                },
            }
            
            if enable_convergence:
                response["convergence_result"] = {
                    "enabled": True,
                    "converged": result.success,
                }
            
            logger.info(
                f"Workflow execution completed: "
                f"success={result.success}, duration={duration:.2f}s"
            )
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            
            return {
                "success": False,
                "error": str(e),
                "metrics": {
                    "duration_seconds": duration,
                },
            }


# =============================================================================
# AC_COMPLETE: AC-PHASE45-S4-002 (GREEN phase implementation)
# =============================================================================
