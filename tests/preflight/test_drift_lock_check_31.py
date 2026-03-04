"""Preflight: Drift Lock — Check #31 Architecture Runtime Connectivity (phase-126-b).

Permanent CI guardrail that enforces the invariants established by phase-126-b.
Fails immediately if any architectural runtime link regresses.

This is a LOCK file — it does not replace test_architecture_runtime_connectivity.py.
It adds a lightweight fast gate that runs even before the full preflight suite.

Drift lock ref: cortex-registry/governance/drift-locks/check-31-arch-connectivity-lock.yaml
Gap ref: GAP-126-02
Phase ref: phase-126-b
Tier: T0 (preflight) — fast, < 5 s
"""
import pathlib
import sys

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCK_YAML = (
    CORTEX_ROOT
    / "cortex-registry"
    / "governance"
    / "drift-locks"
    / "check-31-arch-connectivity-lock.yaml"
)
GOVERNANCE_YAML = CORTEX_ROOT / "cortex-registry" / "governance" / "core-rules.yaml"
IMPLEMENT_TEMPLATE = (
    CORTEX_ROOT
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "sdlc"
    / "implement-workflow.yaml"
)


class TestDriftLockCheck31:
    """Drift lock: Architecture Runtime Connectivity invariants must hold permanently.

    Each test maps to an enforced invariant in check-31-arch-connectivity-lock.yaml.
    Failure here means a regression has been introduced — fix, do not delete.
    """

    def test_drift_lock_yaml_exists(self) -> None:
        """INV-31-00: The drift lock YAML itself must exist.

        If this test fails, someone deleted the governance file — restore it.
        """
        assert DRIFT_LOCK_YAML.exists(), (
            f"DRIFT-LOCK REGRESSION: Governance file deleted: {DRIFT_LOCK_YAML}\n"
            "Restore from git: git checkout HEAD -- "
            "cortex-registry/governance/drift-locks/check-31-arch-connectivity-lock.yaml"
        )

    def test_drift_lock_interaction_orchestrator_importable(self) -> None:
        """INV-31-01a: InteractionOrchestrator must be importable.

        Regression: any import error in the IO chain (interaction_orchestrator,
        conversation_protocol, or its dependencies) breaks Stage-1 comprehension.
        """
        try:
            from cortex.orchestrators.core.interaction_orchestrator import (  # noqa: F401
                InteractionOrchestrator,
            )
        except ImportError as exc:
            pytest.fail(
                "DRIFT-LOCK CHECK-31 INV-31-01 REGRESSION: InteractionOrchestrator "
                f"import failed: {exc}\n"
                "Fix the import chain before committing."
            )

    def test_drift_lock_interaction_orchestrator_health_returns_healthy(self) -> None:
        """INV-31-01b: InteractionOrchestrator.health_check() must return healthy.

        Regression: health_check() returning non-healthy or raising means the
        orchestrator is broken at the base protocol level.
        """
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        class _StubConvProtocol:
            def start_turn(self, *a, **kw):
                pass

            def end_turn(self, *a, **kw):
                pass

        io = InteractionOrchestrator(
            conversation_protocol=_StubConvProtocol(), enable_challenges=False
        )
        health = io.health_check()
        assert isinstance(health, dict) and health.get("status") == "healthy", (
            f"DRIFT-LOCK CHECK-31 INV-31-01 REGRESSION: health_check() returned "
            f"{health!r} — expected dict with status='healthy'.\n"
            "Check IOrchestrator.health_check() default implementation."
        )

    def test_drift_lock_ast_analyzer_importable(self) -> None:
        """INV-31-02a: ASTAnalyzer must be importable.

        Regression: any import error in the LENS layer breaks all code
        intelligence features.
        """
        try:
            from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer  # noqa: F401
        except ImportError as exc:
            pytest.fail(
                "DRIFT-LOCK CHECK-31 INV-31-02 REGRESSION: ASTAnalyzer import "
                f"failed: {exc}\n"
                "Fix the LENS import chain before committing."
            )

    def test_drift_lock_ast_analyzer_returns_success(self) -> None:
        """INV-31-02b: ASTAnalyzer.analyze_file(Path) must return success=True.

        Regression: if analyze_file() returns a dataclass with success=False on
        a valid cortex source file, the LENS analysis layer is broken.
        """
        from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer, ASTAnalysisResult

        target = CORTEX_ROOT / "cortex" / "orchestrators" / "workflow" / "workflow_composer.py"
        assert target.exists(), (
            f"DRIFT-LOCK CHECK-31 INV-31-02 REGRESSION: Probe target deleted: {target}"
        )
        result = ASTAnalyzer().analyze_file(target)
        assert isinstance(result, ASTAnalysisResult), (
            f"DRIFT-LOCK CHECK-31 INV-31-02 REGRESSION: analyze_file() returned "
            f"{type(result).__name__} — expected ASTAnalysisResult dataclass."
        )
        assert result.success, (
            f"DRIFT-LOCK CHECK-31 INV-31-02 REGRESSION: ASTAnalyzer.analyze_file() "
            f"returned success=False on {target}.\nError: {result.error}"
        )

    def test_drift_lock_intelligence_facade_analyze_returns_status(self) -> None:
        """INV-31-03: IntelligenceFacade.analyze() must return dict with 'status'.

        Regression: if the facade returns None or a dict without 'status', the
        Intelligence layer is broken.
        """
        from cortex.intelligence.facade import get_intelligence_facade

        facade = get_intelligence_facade()
        target = str(
            CORTEX_ROOT / "cortex" / "orchestrators" / "workflow" / "workflow_composer.py"
        )
        result = facade.analyze(file_path=target, intent="INVESTIGATE")
        assert result is not None and isinstance(result, dict), (
            f"DRIFT-LOCK CHECK-31 INV-31-03 REGRESSION: IntelligenceFacade.analyze() "
            f"returned {result!r} — expected a non-None dict."
        )
        assert "status" in result, (
            f"DRIFT-LOCK CHECK-31 INV-31-03 REGRESSION: IntelligenceFacade.analyze() "
            f"result missing 'status' key. Got: {list(result.keys())}"
        )

    def test_drift_lock_governance_yaml_parseable(self) -> None:
        """INV-31-04: cortex-registry governance YAML must be parseable.

        Regression: if the primary governance YAML is deleted or corrupted,
        governance rule loading fails silently across all orchestrators.
        """
        import yaml

        assert GOVERNANCE_YAML.exists(), (
            f"DRIFT-LOCK CHECK-31 INV-31-04 REGRESSION: Governance YAML deleted: "
            f"{GOVERNANCE_YAML}"
        )
        try:
            data = yaml.safe_load(GOVERNANCE_YAML.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            pytest.fail(
                f"DRIFT-LOCK CHECK-31 INV-31-04 REGRESSION: governance-rules.yaml "
                f"YAML parse error: {exc}"
            )
        assert isinstance(data, dict) and data, (
            "DRIFT-LOCK CHECK-31 INV-31-04 REGRESSION: governance-rules.yaml "
            "parsed as empty or non-dict — file may be corrupt."
        )

    def test_drift_lock_implement_template_exists_and_parseable(self) -> None:
        """INV-31-05: IMPLEMENT workflow template must exist and be parseable.

        Regression: if the implement-workflow.yaml template is deleted or
        corrupted, WorkflowComposer cannot execute any IMPLEMENT operation.
        """
        import yaml

        assert IMPLEMENT_TEMPLATE.exists(), (
            f"DRIFT-LOCK CHECK-31 INV-31-05 REGRESSION: IMPLEMENT template deleted: "
            f"{IMPLEMENT_TEMPLATE}\n"
            "Restore from git: git checkout HEAD -- "
            "cortex-registry/workflows/templates/sdlc/implement-workflow.yaml"
        )
        try:
            data = yaml.safe_load(IMPLEMENT_TEMPLATE.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            pytest.fail(
                f"DRIFT-LOCK CHECK-31 INV-31-05 REGRESSION: implement-workflow.yaml "
                f"YAML parse error: {exc}"
            )
        assert data is not None, (
            "DRIFT-LOCK CHECK-31 INV-31-05 REGRESSION: implement-workflow.yaml "
            "parsed as None — file may be empty or corrupt."
        )

    def test_drift_lock_workflow_composer_resolves_implement_template(self) -> None:
        """INV-31-06: WorkflowComposer.execute_from_template must resolve IMPLEMENT.

        Regression: if the WorkflowComposer can no longer load and execute the
        IMPLEMENT template, the entire SDLC workflow pipeline is broken.
        """
        try:
            from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        except ImportError as exc:
            pytest.fail(
                f"DRIFT-LOCK CHECK-31 INV-31-06 REGRESSION: WorkflowComposer import "
                f"failed: {exc}"
            )

        composer = WorkflowComposer()
        try:
            result = composer.execute_from_template("sdlc/implement-workflow")
        except (FileNotFoundError, ImportError) as exc:
            pytest.fail(
                f"DRIFT-LOCK CHECK-31 INV-31-06 REGRESSION: execute_from_template("
                f"'sdlc/implement-workflow') raised {type(exc).__name__}: {exc}"
            )
        assert result is not None, (
            "DRIFT-LOCK CHECK-31 INV-31-06 REGRESSION: execute_from_template("
            "'sdlc/implement-workflow') returned None — template did not resolve."
        )
