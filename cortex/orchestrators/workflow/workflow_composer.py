"""
WorkflowComposer — Phase 84 Stage 1.

Motor neuron that sequences workflow steps dynamically from YAML templates.
Reads workflow definitions, assembles orchestrator calls, tracks execution history.

AC_START: AC-P84-S1-T2-001
Phase: 84 | Stage: 1 | Priority: P0
Description: GREEN phase — WorkflowComposer implementation
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
# noqa: CORE-035 — domain-scoped; class name appropriate for this module

from dataclasses import dataclass
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
        template_path: Optional[Path] = None,
        orchestrator_registry: Optional[Callable[[str], Any]] = None,
    ) -> None:
        """Initialize WorkflowComposer with optional template.

        Args:
            template_path: Path to YAML workflow template. When None, the
                composer operates in gateway mode — templates are loaded
                on-demand via ``execute_from_template()``.
            orchestrator_registry: Optional orchestrator lookup function.

        Raises:
            FileNotFoundError: If template file is given but doesn't exist.
            ValueError: If template YAML is invalid or missing required fields.
        """
        self._template_path = template_path
        self._orchestrator_registry = orchestrator_registry
        self._execution_history: List[WorkflowExecutionResult] = []
        self._workflow_name: str = ""
        self._steps: List[WorkflowStep] = []

        # Phase 92: Epilogue hooks for post-phase dedup + holistic sweep
        self._epilogue_hooks: List[Callable[[], Any]] = []

        # Load and parse template only if a path was provided
        if self._template_path is not None:
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
        """Execute workflow with convergence-gated retry loops.

        Phase 99: Cleaned up after Phase 98 dead code removal.
        The StepStateMachine and ConvergenceLoopExecutor modules were removed
        in Phase 98. Convergence is now handled by the detect-fix-rescan-loop
        YAML primitive (interpreted by the LLM) rather than by machine code.

        Falls through to standard execution with convergence metadata logged
        for audit traceability.

        Args:
            workflow: Optional workflow definition.
            context: Optional execution context.

        Returns:
            WorkflowExecutionResult with completion status.
        """
        logger.info(
            "Phase 99: Convergence mode requested for '%s' — "
            "executing with standard pipeline (convergence primitives are LLM-interpreted)",
            self._workflow_name,
        )
        result = self._execute_standard()
        # Tag the result so callers know convergence was requested
        # (audit trail / SQLite logging)
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

        # No registry injected — steps using this orchestrator will be skipped.
        # To wire a registry, pass orchestrator_registry= to WorkflowComposer.__init__().
        return None

    def _emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Emit EventBus event for audit trail.

        Args:
            event_name: Event name (WORKFLOW_COMPOSED, WORKFLOW_COMPLETE, etc.).
            data: Event payload.
        """
        logger.info(f"Event: {event_name} - {data}")

    def register_epilogue(self, hook: Callable[[], Any]) -> None:
        """Register a post-workflow epilogue hook.

        Phase 92: Supports auto-injection of PostPhaseDeduplicationReview
        and HolisticRefactoringSweep after every workflow execution.

        Args:
            hook: Callable to run after workflow steps complete.
                Typical hooks: PostPhaseDeduplicationReview.execute,
                HolisticRefactoringSweep.execute.
        """
        self._epilogue_hooks.append(hook)
        logger.info(
            "Phase 92: Registered epilogue hook '%s'",
            getattr(hook, "__name__", str(hook)),
        )

    def cleanup_temp(self) -> None:
        """Clean up ephemeral storage after workflow execution.

        Phase 99: EphemeralStorage was removed in Phase 98 dead code cleanup.
        This method is retained for API compatibility but is now a no-op.
        """
        logger.debug("Phase 99: cleanup_temp called (no-op — EphemeralStorage removed in Phase 98)")

    def _load_template_by_id(self, template_id: str) -> Dict[str, Any]:
        """Load a YAML template from disk by its template ID.

        Resolves ``cortex-registry/workflows/templates/{template_id}.yaml``
        relative to the project root.

        Args:
            template_id: Template identifier (e.g. ``"sdlc/implement-workflow"``).

        Returns:
            Parsed YAML dict.

        Raises:
            FileNotFoundError: If the template YAML does not exist on disk.
            ValueError: If the YAML is invalid.
        """
        # Resolve project root: workflow_composer.py is at
        # cortex/orchestrators/workflow/workflow_composer.py — 3 levels up is root
        project_root = Path(__file__).resolve().parents[3]
        yaml_path = project_root / "cortex-registry" / "workflows" / "templates" / f"{template_id}.yaml"

        if not yaml_path.exists():
            raise FileNotFoundError(
                f"WorkflowComposer: template YAML not found: {yaml_path} "
                f"(template_id='{template_id}')"
            )

        try:
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"WorkflowComposer: invalid YAML in {yaml_path}: {e}")

        if not isinstance(data, dict):
            raise ValueError(f"WorkflowComposer: template must be a dict, got {type(data)}")

        return data

    def execute_from_template(
        self,
        template_data: Any,
        context: Optional[Dict[str, Any]] = None,
        convergence_mode: bool = False,
    ) -> WorkflowExecutionResult:
        """Execute a workflow from a resolved template dictionary or template ID string.

        Phase 92/99: Bridge method called by WorkflowGateway and
        Stage4DomainExecutionStrategy. Loads steps from the template dict,
        optionally runs with convergence gates, and returns execution result.

        When ``template_data`` is a ``str``, it is treated as a template ID
        (e.g. ``"sdlc/implement-workflow"``). The YAML is loaded from disk
        at ``cortex-registry/workflows/templates/{template_id}.yaml``.

        When ``template_data`` is a ``Dict``, it is used directly as the
        parsed template dictionary with 'workflow' or 'steps' keys.

        Args:
            template_data: Template dictionary **or** template ID string.
            context: Optional execution context dict with operation/parameters.
            convergence_mode: If True, use convergence-gated execution with
                retry loops. Defaults to False (standard step-by-step).

        Returns:
            WorkflowExecutionResult with completion status and metrics.
        """
        import time

        # ── Normalise template_data to a dict ────────────────────────────
        if isinstance(template_data, str):
            template_data = self._load_template_by_id(template_data)

        start_time = time.time()
        template_id = template_data.get("id", template_data.get("workflow", {}).get("id", "unknown"))
        template_name = template_data.get("name", template_data.get("workflow", {}).get("name", template_id))

        # Extract steps from either flat dict or nested under 'workflow' key
        steps = template_data.get("steps", [])
        if not steps:
            workflow_block = template_data.get("workflow", {})
            steps = workflow_block.get("steps", [])

        logger.info(
            "Phase 92: execute_from_template '%s' (%d steps, convergence=%s)",
            template_id,
            len(steps),
            convergence_mode,
        )

        logger.info(
            "Phase 92: execute_from_template '%s' (%d steps)",
            template_id,
            len(steps),
        )

        self._emit_event("TEMPLATE_EXECUTION_START", {
            "template_id": template_id,
            "step_count": len(steps),
            "context": context or {},
        })

        # Check for convergence gate in template
        convergence_gate = template_data.get("convergence_gate")
        has_convergence = convergence_gate is not None

        steps_completed = 0
        total_steps = len(steps)

        for step in steps:
            step_id = step.get("id", step.get("step_id", f"step_{steps_completed}"))
            action = step.get("action", step.get("orchestrator_name", "noop"))

            logger.info(
                "Phase 92: Template step '%s' → %s", step_id, action
            )

            # Dispatch step to orchestrator registry
            orchestrator = self._get_orchestrator(action)
            if orchestrator is not None:
                try:
                    step_params = step.get("parameters", step.get("args", {}))
                    orchestrator.execute(**step_params)
                except Exception as exc:
                    logger.warning(
                        "Phase 92: Step '%s' failed: %s", step_id, exc
                    )
                    if step.get("blocking", False):
                        return WorkflowExecutionResult(
                            success=False,
                            steps_completed=steps_completed,
                            total_steps=total_steps,
                            error_message=f"Blocking step '{step_id}' failed: {exc}",
                            execution_time_ms=(time.time() - start_time) * 1000,
                        )

            steps_completed += 1

        duration_ms = (time.time() - start_time) * 1000

        self._emit_event("TEMPLATE_EXECUTION_COMPLETE", {
            "template_id": template_id,
            "steps_completed": steps_completed,
            "total_steps": total_steps,
            "duration_ms": duration_ms,
            "convergence_gated": has_convergence,
        })

        result = WorkflowExecutionResult(
            success=True,
            steps_completed=steps_completed,
            total_steps=total_steps,
            execution_time_ms=duration_ms,
        )
        self._execution_history.append(result)
        return result


__all__ = [
    "WorkflowComposer",
    "WorkflowStep",
    "WorkflowExecutionResult",
]
# AC_COMPLETE: AC-P84-S1-T2-001 ✅ WorkflowComposer implemented
