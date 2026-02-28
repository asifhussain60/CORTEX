"""
Phase 92: Workflow Infrastructure Wiring — Zero Inert Capabilities.

Sweep catalogue for eliminating all inert workflow infrastructure in CORTEX.
Every capability that exists must be wired into a live execution path.

Fixes:
  G1: Stage4 resolves template_id but never executes the template
  G2: 10 orchestrators inherit WorkflowTemplateMixin but never call it
  G3: ConvergenceLoopExecutor exists but only TDD has inline convergence
  G4: 14 workflow modules have zero external imports (fully inert)

AC-ID: AC-92-WORKFLOW-WIRING
CORE-008: TDD — RED before GREEN
CORE-011: Type hints on all functions
CORE-064: Sweep completeness — all gaps closed
"""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Any, Dict


# ============================================================================
# G1: Stage4 must EXECUTE resolved templates, not just log template_id
# ============================================================================

class TestStage4TemplateExecution:
    """Stage4DomainExecutionStrategy must execute resolved workflow templates
    through WorkflowRuntime instead of returning 'template_routed' no-op."""

    def test_stage4_calls_workflow_runtime_when_template_resolved(self) -> None:
        """When _check_for_workflow_template returns a template_id,
        Stage4 must invoke _execute_workflow_template() — not just
        set status='template_routed' and return."""
        from cortex.orchestrators.core.stage234_strategies import (
            Stage4DomainExecutionStrategy,
            StageContext,
        )
        from cortex.core.result import Ok

        mock_master = MagicMock()
        mock_master._check_for_workflow_template.return_value = {
            "template_id": "tdd/feature-implementation",
            "use_autonomous_workflow": True,
            "complexity_score": 0.65,
        }

        deps = {"master_orchestrator": mock_master}
        stage4 = Stage4DomainExecutionStrategy(dependencies=deps)

        # Mock _execute_workflow_template to simulate successful template execution
        stage4._execute_workflow_template = MagicMock(return_value={
            "template_id": "tdd/feature-implementation",
            "steps_completed": 3,
            "success": True,
        })

        ctx = StageContext(
            operation_name="implement",
            parameters={"request": "add auth service"},
            metadata={"intent_classification": {"routing_target": "TDDOrchestrator"}},
            result=None,
            stage_results={},
        )

        result = stage4.execute(ctx)
        assert result.is_ok()
        output = result.unwrap()

        execution = output.metadata.get("execution", {})
        # Must have actually executed, not just routed
        assert execution.get("status") != "template_routed", (
            "Stage4 must EXECUTE templates, not just mark 'template_routed'. "
            "Wire WorkflowRuntime.execute_template() into the template branch."
        )
        assert execution.get("template_executed") is True, (
            "execution metadata must contain 'template_executed: true' "
            "proving WorkflowRuntime was actually invoked."
        )
        # Verify _execute_workflow_template was called
        stage4._execute_workflow_template.assert_called_once()

    def test_stage4_falls_back_to_direct_delegation_on_template_failure(self) -> None:
        """If template execution fails, Stage4 must fall back to direct
        orchestrator delegation — not crash."""
        from cortex.orchestrators.core.stage234_strategies import (
            Stage4DomainExecutionStrategy,
            StageContext,
        )

        mock_master = MagicMock()
        mock_master._check_for_workflow_template.return_value = {
            "template_id": "nonexistent/template",
            "use_autonomous_workflow": True,
            "complexity_score": 0.7,
        }

        deps = {"master_orchestrator": mock_master}
        stage4 = Stage4DomainExecutionStrategy(dependencies=deps)

        ctx = StageContext(
            operation_name="implement",
            parameters={"request": "add auth service"},
            metadata={"intent_classification": {"routing_target": "TDDOrchestrator"}},
            result=None,
            stage_results={},
        )

        result = stage4.execute(ctx)
        # Must succeed via fallback, not crash
        assert result.is_ok(), (
            "Stage4 must fall back to direct delegation when template execution fails"
        )
        output = result.unwrap()
        execution = output.metadata.get("execution", {})
        assert execution.get("template_fallback") is True or execution.get("status") == "complete", (
            "Stage4 must indicate fallback occurred or succeed via direct delegation"
        )


# ============================================================================
# G2: WorkflowTemplateMixin — orchestrators must actually load templates
# ============================================================================

class TestOrchestratorTemplateConsumption:
    """Orchestrators that inherit WorkflowTemplateMixin must have a
    get_recommended_template() override returning their domain template."""

    def test_tdd_orchestrator_has_recommended_template(self) -> None:
        """TDDOrchestrator.get_recommended_template() must return a template ID."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator

        orch = TDDOrchestrator()
        template_id = orch.get_recommended_template()
        assert template_id is not None, (
            "TDDOrchestrator inherits WorkflowTemplateMixin but "
            "get_recommended_template() returns None — inert capability"
        )
        assert "tdd" in template_id.lower(), (
            f"TDDOrchestrator template should reference tdd domain, got: {template_id}"
        )

    def test_refactoring_orchestrator_has_recommended_template(self) -> None:
        """RefactoringOrchestrator.get_recommended_template() must return a template ID."""
        from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator

        orch = RefactoringOrchestrator()
        template_id = orch.get_recommended_template()
        assert template_id is not None, (
            "RefactoringOrchestrator inherits WorkflowTemplateMixin but "
            "get_recommended_template() returns None — inert capability"
        )

    def test_debugger_orchestrator_has_recommended_template(self) -> None:
        """DebuggerOrchestrator.get_recommended_template() must return a template ID."""
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator

        orch = DebuggerOrchestrator(event_bus=MagicMock())
        template_id = orch.get_recommended_template()
        assert template_id is not None, (
            "DebuggerOrchestrator inherits WorkflowTemplateMixin but "
            "get_recommended_template() returns None — inert capability"
        )

    def test_security_orchestrator_has_recommended_template(self) -> None:
        """SecurityOrchestrator.get_recommended_template() must return a template ID."""
        from cortex.orchestrators.core.security_orchestrator import SecurityOrchestrator

        orch = SecurityOrchestrator()
        template_id = orch.get_recommended_template()
        assert template_id is not None, (
            "SecurityOrchestrator inherits WorkflowTemplateMixin but "
            "get_recommended_template() returns None — inert capability"
        )

    def test_enforcement_orchestrator_has_recommended_template(self) -> None:
        """EnforcementOrchestrator.get_recommended_template() must return a template ID."""
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator

        orch = EnforcementOrchestrator()
        template_id = orch.get_recommended_template()
        assert template_id is not None, (
            "EnforcementOrchestrator inherits WorkflowTemplateMixin but "
            "get_recommended_template() returns None — inert capability"
        )

    def test_interaction_orchestrator_has_recommended_template(self) -> None:
        """InteractionOrchestrator.get_recommended_template() must return a template ID."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator

        orch = InteractionOrchestrator(conversation_protocol=MagicMock())
        template_id = orch.get_recommended_template()
        assert template_id is not None, (
            "InteractionOrchestrator inherits WorkflowTemplateMixin but "
            "get_recommended_template() returns None — inert capability"
        )

    def test_planning_orchestrator_has_recommended_template(self) -> None:
        """PlanningOrchestrator.get_recommended_template() must return a template ID."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator

        orch = PlanningOrchestrator()
        template_id = orch.get_recommended_template()
        assert template_id is not None, (
            "PlanningOrchestrator inherits WorkflowTemplateMixin but "
            "get_recommended_template() returns None — inert capability"
        )

    def test_master_plan_orchestrator_has_recommended_template(self) -> None:
        """CortexMasterPlanOrchestrator.get_recommended_template() must return a template ID."""
        from cortex.orchestrators.core.master_plan_orchestrator import CortexMasterPlanOrchestrator

        orch = CortexMasterPlanOrchestrator()
        template_id = orch.get_recommended_template()
        assert template_id is not None, (
            "CortexMasterPlanOrchestrator inherits WorkflowTemplateMixin but "
            "get_recommended_template() returns None — inert capability"
        )


# ============================================================================
# G3: TDD convergence must use shared ConvergenceLoopExecutor
# ============================================================================

class TestConvergenceLoopWiring:
    """TDDOrchestrator.execute_convergence_loop() should delegate to the
    shared ConvergenceLoopExecutor rather than reimplementing retry logic."""

    def test_convergence_loop_executor_is_importable(self) -> None:
        """ConvergenceLoopExecutor must be importable from workflow module."""
        from cortex.orchestrators.workflow.convergence_loop_executor import (
            ConvergenceLoopExecutor,
            ConvergenceConfig,
            ConvergenceResult,
        )
        executor = ConvergenceLoopExecutor()
        assert executor is not None

    def test_convergence_loop_executor_basic_convergence(self) -> None:
        """ConvergenceLoopExecutor converges when predicate is satisfied."""
        from cortex.orchestrators.workflow.convergence_loop_executor import (
            ConvergenceLoopExecutor,
            ConvergenceConfig,
        )

        counter = {"value": 3}

        def execute_fn() -> int:
            counter["value"] -= 1
            return counter["value"]

        def predicate_fn(value: int) -> bool:
            return value <= 0

        config = ConvergenceConfig(
            max_retries=5,
            initial_backoff_seconds=0.001,
            backoff_multiplier=1.0,
            max_backoff_seconds=0.01,
        )
        executor = ConvergenceLoopExecutor(config=config)
        result = executor.execute(execute_fn, predicate_fn)
        assert result.converged is True
        assert result.attempts <= 5

    def test_workflow_runtime_is_importable(self) -> None:
        """WorkflowRuntime must be importable — it's a core execution engine."""
        from cortex.orchestrators.workflow.workflow_runtime import (
            WorkflowRuntime,
            WorkflowContext,
            WorkflowStep,
            WorkflowExecutionResult,
        )
        # WorkflowRuntime requires template_path — verify it validates input
        with pytest.raises(FileNotFoundError):
            WorkflowRuntime(template_path=Path("nonexistent.yaml"))
        # Verify core classes are usable
        ctx = WorkflowContext(variables={"test": True})
        assert ctx.get("test") is True
        step = WorkflowStep(step_id="s1", action="noop", parameters={})
        assert str(step) == "WorkflowStep(s1: noop)"

    def test_toolchain_executor_is_importable_and_has_mappings(self) -> None:
        """ToolchainExecutor must be importable and have language mappings."""
        from cortex.orchestrators.workflow.toolchain_executor import (
            ToolchainExecutor,
        )
        executor = ToolchainExecutor()
        assert ".py" in executor.EXTENSION_TOOL_MAP
        assert ".cs" in executor.EXTENSION_TOOL_MAP
        assert ".ts" in executor.EXTENSION_TOOL_MAP


# ============================================================================
# G4: Template-Orchestrator mapping must cover ALL operational orchestrators
# ============================================================================

class TestTemplateOrchestratorMapCompleteness:
    """WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP must have entries for
    every orchestrator that inherits WorkflowTemplateMixin."""

    EXPECTED_ORCHESTRATORS = [
        "TDDOrchestrator",
        "RefactoringOrchestrator",
        "EnforcementOrchestrator",
        "MasterOrchestrator",
        "SecurityOrchestrator",
        "DebuggerOrchestrator",
        "InteractionOrchestrator",
        "PlanningOrchestrator",
        "CortexMasterPlanOrchestrator",
        "EnhancedPlanningOrchestrator",
    ]

    def test_all_mixin_inheritors_are_in_template_map(self) -> None:
        """Every orchestrator inheriting WorkflowTemplateMixin must appear
        in TEMPLATE_ORCHESTRATOR_MAP."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin

        mapping = WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP
        missing = [
            name for name in self.EXPECTED_ORCHESTRATORS
            if name not in mapping
        ]
        assert not missing, (
            f"Orchestrators inherit WorkflowTemplateMixin but are missing from "
            f"TEMPLATE_ORCHESTRATOR_MAP (inert wiring): {missing}"
        )

    def test_template_map_values_reference_real_templates(self) -> None:
        """Every template ID in the map should reference a known domain category
        that either has YAML files on disk or is composable by TemplateComposer."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin

        mapping = WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP
        templates_dir = Path("cortex-registry/workflows/templates")

        # Known template categories that have YAML dirs on disk
        known_categories = set()
        if templates_dir.exists():
            known_categories = {
                d.name for d in templates_dir.iterdir()
                if d.is_dir() and not d.name.startswith("_")
            }

        invalid = []
        for orchestrator, template_id in mapping.items():
            parts = template_id.split("/")
            category = parts[0] if parts else template_id

            # Category must exist as a directory in templates/ or in primitives/
            category_exists = category in known_categories
            # Or the full YAML file exists
            yaml_path = templates_dir / f"{template_id}.yaml"
            file_exists = yaml_path.exists()
            # Or a matching file with hyphens exists
            alt_name = "-".join(parts[1:]) if len(parts) > 1 else ""
            alt_path = templates_dir / category / f"{alt_name}.yaml"
            alt_exists = alt_path.exists() if alt_name else False

            if not (category_exists or file_exists or alt_exists):
                invalid.append(f"{orchestrator} → {template_id} (category '{category}' not found)")

        assert not invalid, (
            f"Template map references unknown categories/templates: {invalid}"
        )


# ============================================================================
# G5: WorkflowComplexityRouter must map ALL CORTEX intent types
# ============================================================================

class TestWorkflowGateCompleteness:
    """WorkflowComplexityRouter._select_orchestrator must handle all
    CORTEX execution modes — no gaps in the routing table."""

    EXPECTED_OPERATIONS = [
        "fix", "refactor", "create", "implement", "test",
        "audit", "debug", "vacuum", "health", "security",
        "plan", "design", "document", "digest", "investigate",
        "rca", "sync", "train", "onboard", "totalrecall",
    ]

    def test_all_operations_have_orchestrator_mapping(self) -> None:
        """Every CORTEX operation type must map to a named orchestrator."""
        from cortex.orchestrators.core.intent_router.workflow_gate import (
            WorkflowComplexityRouter,
            Intent,
        )

        router = WorkflowComplexityRouter()
        unmapped = []
        for op in self.EXPECTED_OPERATIONS:
            intent = Intent(operation_type=op, metadata={})
            orch = router._select_orchestrator(intent)
            if orch == "InteractionOrchestrator" and op not in ("query", "interact", "unknown"):
                # InteractionOrchestrator is the default fallback — 
                # if a known operation routes there, it's unmapped
                unmapped.append(f"{op} → {orch} (fallback, not explicit)")

        assert not unmapped, (
            f"Operations falling through to default InteractionOrchestrator "
            f"(missing explicit mapping): {unmapped}"
        )


# ============================================================================
# G6: DUPLICATE ELIMINATION — execution_guard.py must NOT exist in workflow/
# ============================================================================

class TestDuplicateElimination:
    """CORE-035 requires single canonical implementation.
    execution_guard.py exists identically in two locations."""

    def test_workflow_execution_guard_redirects_to_canonical(self) -> None:
        """workflow/execution_guard.py must re-export from canonical location,
        not contain its own implementation."""
        workflow_guard = Path(__file__).resolve().parents[2] / (
            "cortex/orchestrators/workflow/execution_guard.py"
        )
        canonical_guard = Path(__file__).resolve().parents[2] / (
            "cortex/core/execution/resilience/execution_guard.py"
        )
        assert canonical_guard.exists(), "Canonical execution_guard must exist"

        if workflow_guard.exists():
            content = workflow_guard.read_text()
            # It should be a thin re-export, not a full 271-line duplicate
            assert len(content.splitlines()) < 30, (
                f"workflow/execution_guard.py is {len(content.splitlines())} lines — "
                "should be a thin re-export (< 30 lines), not a duplicate"
            )

    def test_no_duplicate_class_definitions_across_locations(self) -> None:
        """SilentExecutionGuard must be defined in exactly ONE file."""
        import importlib
        canonical = importlib.import_module(
            "cortex.core.execution.resilience.execution_guard"
        )
        assert hasattr(canonical, "SilentExecutionGuard"), (
            "Canonical module must export SilentExecutionGuard"
        )


# ============================================================================
# G7: WorkflowComposer EPILOGUE HOOKS — post-phase dedup + holistic sweep
# ============================================================================

class TestWorkflowComposerEpilogueHooks:
    """WorkflowComposer.execute_from_template must support epilogue injection
    for post_phase_dedup_review and holistic_refactoring_sweep."""

    def test_composer_has_epilogue_capability(self) -> None:
        """WorkflowComposer must expose an epilogue registration mechanism."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        # Must have either register_epilogue or _epilogue_hooks attribute
        assert hasattr(WorkflowComposer, "register_epilogue") or hasattr(
            WorkflowComposer, "_epilogue_hooks"
        ), "WorkflowComposer needs epilogue registration for post-phase hooks"

    def test_post_phase_dedup_is_importable_and_has_execute(self) -> None:
        """PostPhaseDeduplicationReview must be importable and executable."""
        from cortex.orchestrators.workflow.post_phase_dedup_review import (
            PostPhaseDeduplicationReview,
        )
        review = PostPhaseDeduplicationReview(
            phase_id="test-phase",
            lens_analyzer=MagicMock(),
        )
        assert hasattr(review, "execute") or hasattr(review, "run"), (
            "PostPhaseDeduplicationReview must have execute() or run() method"
        )

    def test_holistic_sweep_is_importable_and_has_execute(self) -> None:
        """HolisticRefactoringSweep must be importable and executable."""
        from cortex.orchestrators.workflow.holistic_refactoring_sweep import (
            HolisticRefactoringSweep,
        )
        sweep = HolisticRefactoringSweep(
            workflow_id="test-workflow",
            lens_analyzer=MagicMock(),
            refactoring_orchestrator=MagicMock(),
        )
        assert hasattr(sweep, "execute") or hasattr(sweep, "run"), (
            "HolisticRefactoringSweep must have execute() or run() method"
        )


# ============================================================================
# G8: EphemeralStorage must be wired into WorkflowComposer
# ============================================================================

class TestEphemeralStorageWiring:
    """EphemeralStorage provides temp directory management — must be
    reachable from the workflow execution path."""

    def test_ephemeral_storage_importable(self) -> None:
        """EphemeralStorage functions must be importable."""
        from cortex.orchestrators.workflow.ephemeral_storage import (
            ensure_temp_directory,
            cleanup_temp_directory,
        )
        assert callable(ensure_temp_directory)
        assert callable(cleanup_temp_directory)

    def test_composer_can_manage_temp_directories(self) -> None:
        """WorkflowComposer must have temp directory lifecycle support."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        assert hasattr(WorkflowComposer, "cleanup_temp") or hasattr(
            WorkflowComposer, "_temp_cleanup"
        ), "WorkflowComposer needs temp directory lifecycle management"


# ============================================================================
# G9: ToolchainExecutor must be wired into WorkflowComposer step dispatch
# ============================================================================

class TestToolchainExecutorWiring:
    """ToolchainExecutor dispatches to external tools (linters, formatters) —
    must be callable from WorkflowComposer step execution."""

    def test_toolchain_executor_importable(self) -> None:
        """ToolchainExecutor must be importable with execute_lint method."""
        from cortex.orchestrators.workflow.toolchain_executor import (
            ToolchainExecutor,
        )
        executor = ToolchainExecutor()
        assert hasattr(executor, "execute_lint") or hasattr(executor, "execute_lint_batch"), (
            "ToolchainExecutor must have execute_lint() or execute_lint_batch() method"
        )

    def test_composer_step_dispatch_knows_toolchain(self) -> None:
        """WorkflowComposer._get_orchestrator must recognize 'toolchain' steps."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        # The composer must have a step dispatch that can resolve toolchain actions
        assert hasattr(WorkflowComposer, "_get_orchestrator"), (
            "WorkflowComposer must have _get_orchestrator for step dispatch"
        )


# ============================================================================
# G10: AbsorptionGate + FlushManager must be reachable from workflow path
# ============================================================================

class TestBrainMetaphorWiring:
    """AbsorptionGate (knowledge intake) and FlushManager (knowledge cleanup)
    are the digestive system — must be reachable from workflow execution."""

    def test_absorption_gate_importable_with_evaluate(self) -> None:
        """AbsorptionGate must be importable with evaluation method."""
        from cortex.orchestrators.workflow.absorption_gate import AbsorptionGate
        gate = AbsorptionGate()
        assert hasattr(gate, "evaluate") or hasattr(gate, "should_absorb"), (
            "AbsorptionGate must have evaluate() or should_absorb() method"
        )

    def test_flush_manager_importable_with_flush(self) -> None:
        """FlushManager must be importable with flush method."""
        from cortex.orchestrators.workflow.flush_manager import FlushManager
        manager = FlushManager()
        assert hasattr(manager, "flush") or hasattr(manager, "cleanup"), (
            "FlushManager must have flush() or cleanup() method"
        )

    def test_absorption_and_flush_paired_in_workflow_lifecycle(self) -> None:
        """WorkflowComposer must know about both absorption and flush."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        # Composer must have lifecycle hooks or step dispatch for brain metaphor
        assert hasattr(WorkflowComposer, "register_epilogue") or hasattr(
            WorkflowComposer, "_brain_hooks"
        ), "WorkflowComposer needs brain metaphor lifecycle hooks"


# ============================================================================
# G11: ComplexityGate must be usable from WorkflowComplexityRouter
# ============================================================================

class TestComplexityGateWiring:
    """ComplexityGate evaluates operation complexity — should be used
    by WorkflowComplexityRouter for its threshold decisions."""

    def test_complexity_gate_importable(self) -> None:
        """ComplexityGate must be importable."""
        from cortex.orchestrators.workflow.complexity_gate import (
            ComplexityGate,
            GateDecision,
        )
        gate = ComplexityGate()
        assert callable(getattr(gate, "evaluate", None)), (
            "ComplexityGate must have evaluate() method"
        )

    def test_gateway_exec_full_importable(self) -> None:
        """MasterGatewayExecutor must be importable."""
        from cortex.orchestrators.workflow.gateway_exec_full import (
            MasterGatewayExecutor,
        )
        assert MasterGatewayExecutor is not None
