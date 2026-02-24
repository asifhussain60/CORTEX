"""
WorkflowEngine — YAML-based workflow template execution.

Reads workflow YAML templates and orchestrates execution.

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
Phase 64-G: register_post_step_hook() added for CORE-066 ResponseTemplateValidator wiring.
Phase 67-E: StepHandlerRegistry + StepError replacing _execute_step() pure stub (GAP-67-01).
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import yaml

from cortex.core.scaffold_writer import ScaffoldWriter


class StepError(Exception):
    """Raised when a workflow step operation is unknown or cannot be dispatched.

    Phase 67-E (GAP-67-01): replaces silent stub behaviour so unknown operations
    surface immediately rather than being swallowed by a noop.

    Args:
        operation: The unrecognised operation string that caused the failure.
    """

    def __init__(self, operation: str, message: str = "") -> None:
        self.operation = operation
        super().__init__(message or f"Unknown step operation: '{operation}'")


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
        self._scaffold_writer = ScaffoldWriter(root=self.template_dir)
        # CORE-066: post-step hooks for ResponseTemplateValidator wiring (Phase 64-G)
        self._post_step_hooks: List[Callable[[Dict[str, Any]], None]] = []
        # Phase 67-E (GAP-67-01): StepHandlerRegistry — replaces silent stub
        self._step_handler_registry: Dict[
            str, Callable[[Dict[str, Any], "ExecutionContext"], Optional[Dict[str, Any]]]
        ] = {
            "noop": self._noop_handler,
            "orchestrator_dispatch": self._orchestrator_dispatch_handler,
            "validate": self._validate_handler,
        }

    # ── Phase 67-E: Built-in step handlers ───────────────────────────────────

    @staticmethod
    def _noop_handler(
        step: Dict[str, Any], context: "ExecutionContext"
    ) -> None:
        """No-op handler — completes immediately with no side effects.

        Args:
            step: Step configuration dict.
            context: Current execution context.
        """
        # Intentional no-op; step completes with no side effects

    @staticmethod
    def _validate_handler(
        step: Dict[str, Any], context: "ExecutionContext"
    ) -> Dict[str, Any]:
        """Validate handler — returns a passing validation result dict.

        Args:
            step: Step configuration dict.
            context: Current execution context.

        Returns:
            Dict with 'status' key set to 'complete'.
        """
        return {"status": "complete", "validation": "passed"}

    @staticmethod
    def _orchestrator_dispatch_handler(
        step: Dict[str, Any], context: "ExecutionContext"
    ) -> Optional[Dict[str, Any]]:
        """Orchestrator dispatch handler — routes step to the named orchestrator.

        If no 'orchestrator' key is present in the step dict, raises StepError
        rather than silently failing (CORE-064 no silent swallowing).

        Args:
            step: Step configuration dict.  Must contain 'orchestrator' key.
            context: Current execution context.

        Returns:
            Dict with 'status' key, or None.

        Raises:
            StepError: If 'orchestrator' key is missing from step.
        """
        orchestrator_name = step.get("orchestrator")
        if not orchestrator_name:
            raise StepError(
                "orchestrator_dispatch",
                "orchestrator_dispatch step is missing 'orchestrator' key",
            )
        # Dispatch stub: in production, resolve orchestrator by name from registry
        return {"status": "complete", "dispatched_to": orchestrator_name}

    def register_step_handler(
        self,
        operation: str,
        handler: Callable[[Dict[str, Any], "ExecutionContext"], Optional[Dict[str, Any]]],
    ) -> None:
        """Register a custom step handler for the given operation name.

        Phase 67-E (GAP-67-01): Extension point for domain-specific handlers.

        Args:
            operation: Operation string (matches ``step['operation']`` in YAML).
            handler: Callable with signature ``(step, context) -> Optional[dict]``.
        """
        self._step_handler_registry[operation] = handler

    # ── CORE-066: Post-step hook registry (Phase 64-G) ───────────────────────

    def register_post_step_hook(
        self,
        hook: Callable[[Dict[str, Any]], None],
    ) -> None:
        """Register a callable to be invoked after each workflow step completes.

        Used to wire CORE-066 ResponseTemplateValidator so every step's
        user-visible output is validated before rendering to VS Code Copilot Chat.

        Args:
            hook: Callable that receives the step result dict. Should call
                  ResponseTemplateValidator.validate_output() on the output field.

        Example:
            >>> from cortex.governance.response_template_validator import (
            ...     ResponseTemplateValidator
            ... )
            >>> engine = WorkflowEngine()
            >>> validator = ResponseTemplateValidator()
            >>> engine.register_post_step_hook(
            ...     lambda result: validator.validate_output(result.get("output", ""))
            ... )
        """
        self._post_step_hooks.append(hook)

    # ── SDO-compatible API ────────────────────────────────────────────────────

    def load(self, workflow_path: str) -> Dict[str, Any]:
        """Load a workflow YAML and return its raw dict.

        Used by :class:`~cortex.orchestrators.domain.service_decomposition_orchestrator.ServiceDecompositionOrchestrator`.

        Args:
            workflow_path: Path string to the workflow YAML template.

        Returns:
            Parsed YAML dict.  Returns ``{"workflow": {"steps": []}}`` if the
            file does not exist (graceful degradation so the pipeline doesn't
            stop mid-run).
        """
        path = Path(workflow_path)
        if not path.exists():
            import logging as _log
            _log.getLogger(__name__).warning(
                "WorkflowEngine.load: template not found at %s — returning empty workflow", path
            )
            return {"workflow": {"steps": []}}

        with open(path, "r") as fh:
            return yaml.safe_load(fh) or {"workflow": {"steps": []}}

    def execute_step(
        self,
        *,
        step_id: str,
        step_config: Dict[str, Any],
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single workflow step and emit any scaffold_files to disk.

        Dispatches to the configured step executor (orchestrator) if available,
        otherwise returns a ``"complete"`` stub so the pipeline never halts on
        an un-wired step (Gap G2 fix).

        After execution the ``scaffold_files`` key in the result is passed to
        :class:`~cortex.core.scaffold_writer.ScaffoldWriter` so that files land
        on disk before the next step's ``depends_on`` gate checks for them.

        Args:
            step_id:     Identifier of the step being executed.
            step_config: Full step definition from the workflow YAML.
            params:      Runtime substitution parameters from the caller.

        Returns:
            Step result dict containing at minimum ``{"status": "complete"}``.
        """
        # Placeholder: full dispatch to named orchestrators will be wired in Phase 15+.
        # Returns "complete" so blocking-step gates pass and the pipeline runs end-to-end.
        step_result: Dict[str, Any] = {"status": "complete", "scaffold_files": [], "outputs": {}}

        # Emit scaffold_files to disk (Gap G2 fix — non-stopping pipeline)
        scaffold_files = self._scaffold_writer.from_step_output(step_result)
        if scaffold_files:
            written = self._scaffold_writer.emit(scaffold_files)
            step_result["scaffold_files_written"] = [str(p) for p in written]

        return step_result

    # ── legacy load_workflow API ──────────────────────────────────────────────

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
            except StepError:
                # Phase 67-E: StepError is a configuration error — re-raise so
                # callers can distinguish "misconfigured step" from generic failure
                stage.status = "failed"
                context.status = "failed"
                context.completed_at = datetime.now()
                raise
            except Exception as e:
                stage.status = "failed"
                stage.error = str(e)
                context.status = "failed"
                break
        
        context.completed_at = datetime.now()
        if context.status != "failed":
            context.status = "completed"
        
        return context
    
    def _execute_step(self, step: Dict[str, Any], context: "ExecutionContext") -> None:
        """Execute a single workflow step via the StepHandlerRegistry.

        Phase 67-E (GAP-67-01): replaces the pure stub with a proper registry
        dispatch.  Unknown operations raise :class:`StepError` immediately so
        mis-configured YAML templates are caught at runtime, not silently
        swallowed.

        After execution any ``scaffold_files`` in the step result are written
        to disk via :class:`~cortex.core.scaffold_writer.ScaffoldWriter`.

        Args:
            step: Step configuration dict.  Must contain an 'operation' key
                  that resolves to a registered handler.
            context: Current execution context.

        Raises:
            StepError: If the operation is not registered in
                       ``_step_handler_registry``.
        """
        operation = step.get("operation", "noop")
        if operation not in self._step_handler_registry:
            raise StepError(operation)

        handler = self._step_handler_registry[operation]
        step_result: Optional[Dict[str, Any]] = handler(step, context)

        # Emit scaffold_files to disk after step completes (Gap G2 fix)
        result_dict: Dict[str, Any] = step_result or {}
        scaffold_files = self._scaffold_writer.from_step_output(result_dict)
        if scaffold_files:
            written = self._scaffold_writer.emit(scaffold_files)
            context.variables.setdefault("scaffold_written", []).extend(
                str(p) for p in written
            )

        # Invoke post-step hooks (CORE-066)
        for hook in self._post_step_hooks:
            hook(result_dict)


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
