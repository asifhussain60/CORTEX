"""
WorkflowEngine — YAML-based workflow template execution.

Reads workflow YAML templates and orchestrates execution.

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import yaml


@dataclass
class ExecutionStage:
    """Represents a workflow execution stage."""
    
    id: str
    name: str
    description: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None


@dataclass
class ExecutionContext:
    """Context for workflow execution."""
    
    workflow_id: str
    template_path: Path
    stages: Dict[str, ExecutionStage] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed


class WorkflowEngine:
    """YAML-based workflow template execution engine."""
    
    def __init__(self, template_dir: Optional[Path] = None) -> None:
        """Initialize WorkflowEngine.
        
        Args:
            template_dir: Directory containing workflow templates.
        """
        self.template_dir = template_dir or Path.cwd()
        self.workflows: Dict[str, ExecutionContext] = {}
    
    def load_workflow(self, template_path: Path) -> ExecutionContext:
        """Load a workflow template from YAML file.
        
        Args:
            template_path: Path to workflow YAML file.
            
        Returns:
            ExecutionContext: Loaded workflow context.
            
        Raises:
            FileNotFoundError: If template file doesn't exist.
            yaml.YAMLError: If YAML parsing fails.
        """
        if not template_path.exists():
            raise FileNotFoundError(f"Workflow template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)
        
        if not template:
            raise ValueError(f"Empty workflow template: {template_path}")
        
        # Create execution context
        metadata = template.get('metadata', {})
        workflow_id = metadata.get('id', 'unnamed-workflow')
        
        context = ExecutionContext(
            workflow_id=workflow_id,
            template_path=template_path,
        )
        
        # Parse stages
        stages_config = template.get('stages', [])
        for stage_config in stages_config:
            stage = self._parse_stage(stage_config)
            context.stages[stage.id] = stage
        
        # Store variables
        context.variables = template.get('variables', {})
        
        self.workflows[workflow_id] = context
        return context
    
    @staticmethod
    def _parse_stage(stage_config: Dict[str, Any]) -> ExecutionStage:
        """Parse a stage definition from workflow YAML.
        
        Args:
            stage_config: Stage configuration dictionary.
            
        Returns:
            ExecutionStage: Parsed stage object.
        """
        return ExecutionStage(
            id=stage_config.get('id', 'unknown-stage'),
            name=stage_config.get('name', 'Unnamed Stage'),
            description=stage_config.get('description', ''),
            steps=stage_config.get('steps', []),
            depends_on=stage_config.get('depends_on', []),
        )
    
    def execute_workflow(self, workflow_id: str) -> ExecutionContext:
        """Execute a loaded workflow.
        
        Args:
            workflow_id: ID of workflow to execute.
            
        Returns:
            ExecutionContext: Updated context after execution.
            
        Raises:
            ValueError: If workflow not found.
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        context = self.workflows[workflow_id]
        context.status = "running"
        context.started_at = datetime.now()
        
        # Execute stages in order
        for stage_id, stage in context.stages.items():
            stage.status = "running"
            
            try:
                # Execute stage steps
                for step in stage.steps:
                    self._execute_step(step, context)
                
                stage.status = "completed"
            except Exception as e:
                stage.status = "failed"
                stage.error = str(e)
                context.status = "failed"
                break
        
        context.completed_at = datetime.now()
        if context.status != "failed":
            context.status = "completed"
        
        return context
    
    @staticmethod
    def _execute_step(step: Dict[str, Any], context: ExecutionContext) -> None:
        """Execute a single workflow step.
        
        Args:
            step: Step configuration.
            context: Execution context.
        """
        # Placeholder: actual implementation would dispatch to orchestrators
        operation = step.get('operation', 'noop')
        # Step execution logic here
    
    def get_execution_context(self, workflow_id: str) -> Optional[ExecutionContext]:
        """Get the execution context for a workflow.
        
        Args:
            workflow_id: ID of workflow.
            
        Returns:
            ExecutionContext if found, None otherwise.
        """
        return self.workflows.get(workflow_id)
    
    def get_stage_status(self, workflow_id: str, stage_id: str) -> Optional[str]:
        """Get the status of a specific stage.
        
        Args:
            workflow_id: ID of workflow.
            stage_id: ID of stage.
            
        Returns:
            Stage status if found, None otherwise.
        """
        context = self.workflows.get(workflow_id)
        if not context:
            return None
        
        stage = context.stages.get(stage_id)
        if not stage:
            return None
        
        return stage.status


# Singleton instance
_engine_instance: Optional[WorkflowEngine] = None


def get_workflow_engine(template_dir: Optional[Path] = None) -> WorkflowEngine:
    """Get or create the singleton WorkflowEngine instance.
    
    Args:
        template_dir: Optional directory for templates.
        
    Returns:
        WorkflowEngine: The singleton instance.
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = WorkflowEngine(template_dir)
    return _engine_instance
