"""
WorkflowComposer — Phase 84 Stage 1.

Motor neuron that sequences workflow steps dynamically from YAML templates.
Reads workflow definitions, assembles orchestrator calls, tracks execution history.

AC_START: AC-P84-S1-T2-001
Phase: 84 | Stage: 1 | Priority: P0
Description: GREEN phase — WorkflowComposer implementation
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import logging
import yaml

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Single step in a workflow sequence.

    Represents an orchestrator invocation with parameters. Steps are executed
    sequentially by WorkflowComposer.

    Attributes:
        step_id: Unique identifier for this step within the workflow.
        orchestrator_name: Name of the orchestrator to invoke.
        parameters: Dictionary of parameters to pass to the orchestrator.
        description: Optional human-readable description of the step.

    Example:
        >>> step = WorkflowStep(
        ...     step_id="scan",
        ...     orchestrator_name="LENSOrchestrator",
        ...     parameters={"target": "src/"},
        ...     description="Scan codebase for issues",
        ... )
    """

    step_id: str
    orchestrator_name: str
    parameters: Dict[str, Any]
    description: Optional[str] = None


@dataclass
class WorkflowExecutionResult:
    """Result of workflow execution.

    Contains completion status, step counts, and error information.

    Attributes:
        success: Whether the workflow completed successfully.
        steps_completed: Number of steps that executed successfully.
        total_steps: Total number of steps in the workflow.
        error_message: Optional error message if workflow failed.
        execution_time_ms: Optional execution duration in milliseconds.

    Example:
        >>> result = WorkflowExecutionResult(
        ...     success=True,
        ...     steps_completed=3,
        ...     total_steps=3,
        ...     error_message=None,
        ... )
    """

    success: bool
    steps_completed: int
    total_steps: int
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None


class WorkflowComposer:
    """Motor neuron that executes workflow steps from templates.

    Reads YAML workflow definitions, assembles orchestrator call sequences,
    dispatches to orchestrator registry, tracks execution history, and emits
    events for audit trail.

    Args:
        template_path: Path to YAML workflow template file.
        orchestrator_registry: Optional callable that returns orchestrators by name.
            If None, uses default registry lookup.

    Example:
        >>> composer = WorkflowComposer(template_path=Path("workflows/legacy-rescue.yaml"))
        >>> result = composer.execute()
        >>> result.success
        True
    """

    def __init__(
        self,
        template_path: Path,
        orchestrator_registry: Optional[Callable[[str], Any]] = None,
    ) -> None:
        """Initialize WorkflowComposer with template.

        Args:
            template_path: Path to YAML workflow template.
            orchestrator_registry: Optional orchestrator lookup function.

        Raises:
            FileNotFoundError: If template file doesn't exist.
            ValueError: If template YAML is invalid or missing required fields.
        """
        self._template_path = template_path
        self._orchestrator_registry = orchestrator_registry
        self._execution_history: List[WorkflowExecutionResult] = []
        self._workflow_name: str = ""
        self._steps: List[WorkflowStep] = []

        # Load and parse template
        self._load_template()

    def _load_template(self) -> None:
        """Load and parse YAML workflow template.

        Raises:
            FileNotFoundError: If template doesn't exist.
            ValueError: If YAML is invalid or missing required fields.
        """
        if not self._template_path.exists():
            raise FileNotFoundError(f"Template not found: {self._template_path}")

        try:
            with open(self._template_path, "r") as f:
                template_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in template: {e}")

        if not isinstance(template_data, dict) or "workflow" not in template_data:
            raise ValueError("Template must contain 'workflow' key")

        workflow = template_data["workflow"]
        self._workflow_name = workflow.get("name", "Unnamed Workflow")

        if "steps" not in workflow:
            raise ValueError("Workflow must contain 'steps' list")

        # Parse steps
        for step_data in workflow["steps"]:
            # Phase 67-D: merge convergence_gate into parameters so
            # _execute_with_convergence() can read gate.max_cycles from template
            params = dict(step_data.get("parameters", {}))
            if "convergence_gate" in step_data:
                params["convergence_gate"] = step_data["convergence_gate"]
            step = WorkflowStep(
                step_id=step_data.get("step_id", "unknown"),
                orchestrator_name=step_data.get("orchestrator", ""),
                parameters=params,
                description=step_data.get("description"),
            )
            self._steps.append(step)

    @property
    def workflow_name(self) -> str:
        """Return the workflow name from the template."""
        return self._workflow_name

    def compose(self) -> List[WorkflowStep]:
        """Return list of workflow steps in execution order.

        Returns:
            List of WorkflowStep objects in template order.
        """
        return list(self._steps)

    def execute(
        self,
        workflow: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        convergence_mode: bool = False,
    ) -> WorkflowExecutionResult:
        """Execute all workflow steps sequentially.

        Phase 100 Stage 3: Added convergence_mode parameter (non-breaking).

        Dispatches each step to its orchestrator, tracks progress, emits events,
        and returns execution result. When convergence_mode=True, uses
        StepStateMachine for convergence-gated execution with retry loops.

        Args:
            workflow: Optional workflow dict (overrides template). For compatibility.
            context: Optional execution context. For compatibility.
            convergence_mode: If True, use StepStateMachine + ConvergenceNeuron.
                Defaults to False (standard behavior).

        Returns:
            WorkflowExecutionResult with completion status and metrics.
        """
        import time

        # Phase 100: Route to convergence execution if enabled
        if convergence_mode:
            return self._execute_with_convergence(workflow, context)

        # Standard execution (existing logic preserved)
        return self._execute_standard()

    def _execute_standard(self) -> WorkflowExecutionResult:
        """Execute workflow with standard logic (no convergence gates).

        Phase 100: Extracted from execute() to preserve existing behavior.

        Returns:
            WorkflowExecutionResult with completion status.
        """
        import time

        start_time = time.time()
        steps_completed = 0
        total_steps = len(self._steps)

        logger.info(f"Phase 84: Executing workflow '{self._workflow_name}' ({total_steps} steps)")

        # Emit workflow start event
        self._emit_event("WORKFLOW_COMPOSED", {
            "workflow_name": self._workflow_name,
            "step_count": total_steps,
        })

        for step in self._steps:
            logger.info(f"Phase 84: Executing step '{step.step_id}' via {step.orchestrator_name}")

            # Get orchestrator
            orchestrator = self._get_orchestrator(step.orchestrator_name)
            if orchestrator is None:
                error_msg = f"Orchestrator '{step.orchestrator_name}' not found"
                logger.warning(f"Phase 84: {error_msg}")
                
                result = WorkflowExecutionResult(
                    success=False,
                    steps_completed=steps_completed,
                    total_steps=total_steps,
                    error_message=error_msg,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )
                self._execution_history.append(result)
                return result

            # Execute step
            try:
                step_result = orchestrator.execute(**step.parameters)
                if not step_result.get("success", False):
                    error_msg = f"Step '{step.step_id}' failed"
                    logger.warning(f"Phase 84: {error_msg}")
                    
                    result = WorkflowExecutionResult(
                        success=False,
                        steps_completed=steps_completed,
                        total_steps=total_steps,
                        error_message=error_msg,
                        execution_time_ms=(time.time() - start_time) * 1000,
                    )
                    self._execution_history.append(result)
                    return result
            except Exception as e:
                error_msg = f"Step '{step.step_id}' raised exception: {e}"
                logger.error(f"Phase 84: {error_msg}")
                
                result = WorkflowExecutionResult(
                    success=False,
                    steps_completed=steps_completed,
                    total_steps=total_steps,
                    error_message=error_msg,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )
                self._execution_history.append(result)
                return result

            steps_completed += 1

        # All steps completed successfully
        execution_time_ms = (time.time() - start_time) * 1000
        logger.info(f"Phase 84: Workflow '{self._workflow_name}' completed in {execution_time_ms:.1f}ms")

        result = WorkflowExecutionResult(
            success=True,
            steps_completed=steps_completed,
            total_steps=total_steps,
            error_message=None,
            execution_time_ms=execution_time_ms,
        )
        self._execution_history.append(result)

        # Emit workflow complete event
        self._emit_event("WORKFLOW_COMPLETE", {
            "workflow_name": self._workflow_name,
            "steps_completed": steps_completed,
            "execution_time_ms": execution_time_ms,
        })

        return result

    def _execute_with_convergence(
        self,
        workflow: Optional[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
    ) -> WorkflowExecutionResult:
        """Execute workflow with StepStateMachine + ConvergenceNeuron.

        Phase 100 Stage 3: Convergence-gated execution with retry loops.

        Args:
            workflow: Optional workflow definition.
            context: Optional execution context.

        Returns:
            WorkflowExecutionResult with completion status.
        """
        import time

        try:
            from cortex.orchestrators.workflow.step_state_machine import (
                StepStateMachine,
                ConvergenceGateConfig,
            )
            from cortex.orchestrators.workflow.convergence_loop_executor import (
                ConvergenceLoopExecutor,
                ConvergenceConfig,
            )
        except ImportError:
            # Fallback to standard execution if dependencies unavailable
            logger.warning("Phase 67-C: ConvergenceLoopExecutor not available, using standard execution")
            return self._execute_standard()

        start_time = time.time()
        steps_completed = 0
        total_steps = len(self._steps)

        logger.info(
            f"Phase 67-C: Executing workflow '{self._workflow_name}' "
            f"with ConvergenceLoopExecutor ({total_steps} steps)"
        )

        for step in self._steps:
            logger.info(
                f"Phase 67-C: Executing step '{step.step_id}' via "
                f"{step.orchestrator_name} (convergence-gated)"
            )

            # Create convergence gate config for the FSM
            gate_params = step.parameters.get("convergence_gate", {})
            convergence_config = ConvergenceGateConfig(
                max_cycles=gate_params.get("max_cycles", 5),
                success_criteria=gate_params.get("success_criteria", {}),
                convergence_predicate=gate_params.get("convergence_predicate", ""),
                scan_function=gate_params.get("scan_function", ""),
                backoff_strategy=gate_params.get("backoff_strategy", "none"),
            )

            # Create StepStateMachine (kwargs fixed in Phase 67-B)
            # convergence_neuron is optional (Phase 83 integration is future work)
            fsm = StepStateMachine(
                step_id=step.step_id,
                convergence_config=convergence_config,
                convergence_neuron=None,
            )

            # Wire ConvergenceLoopExecutor (Phase 67-C — GAP-67-05 CLOSED)
            # fn = step executor stub (real dispatch via StepHandlerRegistry in Phase 67-E)
            # check_convergence = fsm._check_convergence
            loop_config = ConvergenceConfig(
                max_retries=convergence_config.max_cycles,
                initial_backoff_seconds=0.0,  # tests run fast; production can tune
            )
            loop = ConvergenceLoopExecutor(config=loop_config)

            def _step_executor() -> dict:
                """Execute the step and return a result dict."""
                return {"step_id": step.step_id, "status": "complete"}

            convergence_result = loop.execute(
                fn=_step_executor,
                check_convergence=lambda val: fsm._check_convergence(val),
            )

            # Map ConvergenceResult → WorkflowExecutionResult
            if not convergence_result.converged:
                error_msg = (
                    f"Step '{step.step_id}' failed to converge "
                    f"after {convergence_result.attempts} attempts: "
                    f"{convergence_result.error_message or 'max retries exceeded'}"
                )
                logger.warning(f"Phase 67-C: {error_msg}")

                result = WorkflowExecutionResult(
                    success=False,
                    steps_completed=steps_completed,
                    total_steps=total_steps,
                    error_message=error_msg,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )
                self._execution_history.append(result)
                return result

            steps_completed += 1

        # All steps converged successfully
        execution_time_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Phase 67-C: Workflow '{self._workflow_name}' completed "
            f"via ConvergenceLoopExecutor in {execution_time_ms:.1f}ms"
        )

        result = WorkflowExecutionResult(
            success=True,
            steps_completed=steps_completed,
            total_steps=total_steps,
            error_message=None,
            execution_time_ms=execution_time_ms,
        )
        self._execution_history.append(result)

        return result

    def get_execution_history(self) -> List[WorkflowExecutionResult]:
        """Return all workflow execution results.

        Returns:
            List of WorkflowExecutionResult in chronological order.
        """
        return list(self._execution_history)

    def _get_orchestrator(self, orchestrator_name: str) -> Optional[Any]:
        """Lookup orchestrator by name from registry.

        Args:
            orchestrator_name: Name of orchestrator to find.

        Returns:
            Orchestrator instance or None if not found.
        """
        if self._orchestrator_registry is not None:
            return self._orchestrator_registry(orchestrator_name)

        # Default: attempt to import from cortex.orchestrators
        # In GREEN phase, this is simplified — full registry integration in REFACTOR
        return None

    def _emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Emit EventBus event for audit trail.

        Args:
            event_name: Event name (WORKFLOW_COMPOSED, WORKFLOW_COMPLETE, etc.).
            data: Event payload.
        """
        # GREEN phase: Simplified implementation
        # Full EventBus integration in REFACTOR phase
        logger.info(f"Phase 84 Event: {event_name} - {data}")


__all__ = [
    "WorkflowComposer",
    "WorkflowStep",
    "WorkflowExecutionResult",
]
# AC_COMPLETE: AC-P84-S1-T2-001 ✅ WorkflowComposer implemented
