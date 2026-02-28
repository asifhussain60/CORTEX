"""Phase 89-a: Technology-Aware Intent Routing — RED tests.

Tests that IntentRouter and WorkflowComplexityRouter select technology-specific
workflow templates when technology keywords (html, css, csharp, typescript,
frontend, backend, dotnet) are present in user requests.

GAP-89-01: IntentRouter technology keywords
GAP-89-02: WorkflowComplexityRouter._select_template() technology-qualified map
GAP-89-03: Technology metadata propagation through Intent dataclass
GAP-89-17: HTML/CSS work should go through workflow gates
GAP-89-18: Operational intents in WorkflowComplexityRouter

CORE-008: TDD mandatory — RED phase (all tests must FAIL before implementation)
"""

from __future__ import annotations

import pytest

from cortex.orchestrators.core.intent_router.workflow_gate import (
    Intent,
    RoutingStrategy,
    WorkflowComplexityRouter,
)


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 1: WorkflowComplexityRouter technology-aware template selection
# (GAP-89-02)
# ══════════════════════════════════════════════════════════════════════════════


class TestWorkflowComplexityRouterTechnologyTemplates:
    """WorkflowComplexityRouter._select_template() must select technology-specific templates."""

    def _make_intent(
        self,
        operation: str,
        technology: str | None = None,
        files: int = 5,
        risk: str = "MEDIUM",
    ) -> Intent:
        """Helper to build an Intent with technology metadata."""
        metadata: dict = {}
        if technology is not None:
            metadata["technology"] = technology
        return Intent(
            operation_type=operation,
            target_files=[f"file{i}.py" for i in range(files)],
            dependencies=["dep1", "dep2", "dep3"],
            risk_level=risk,
            metadata=metadata,
        )

    def test_html_refactor_selects_html_template(self) -> None:
        """operation='refactor' + technology='html' → 'frontend/html-refactor-validation'."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent("refactor", technology="html")
        template_id = router._select_template(intent)
        assert template_id == "frontend/html-refactor-validation"

    def test_css_refactor_selects_css_template(self) -> None:
        """operation='refactor' + technology='css' → 'frontend/css-extraction-workflow'."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent("refactor", technology="css")
        template_id = router._select_template(intent)
        assert template_id == "frontend/css-extraction-workflow"

    def test_typescript_refactor_selects_ts_template(self) -> None:
        """operation='refactor' + technology='typescript' → 'frontend/typescript-refactor-workflow'."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent("refactor", technology="typescript")
        template_id = router._select_template(intent)
        assert template_id == "frontend/typescript-refactor-workflow"

    def test_csharp_refactor_selects_csharp_template(self) -> None:
        """operation='refactor' + technology='csharp' → 'backend/csharp-refactor-workflow'."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent("refactor", technology="csharp")
        template_id = router._select_template(intent)
        assert template_id == "backend/csharp-refactor-workflow"

    def test_csharp_security_selects_csharp_security_template(self) -> None:
        """operation='security' + technology='csharp' → 'backend/csharp-security-workflow'."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent("security", technology="csharp")
        template_id = router._select_template(intent)
        assert template_id == "backend/csharp-security-workflow"

    def test_css_create_selects_css_zero_inline_template(self) -> None:
        """operation='create' + technology='css' → 'frontend/css-zero-inline-workflow'."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent("create", technology="css")
        template_id = router._select_template(intent)
        assert template_id == "frontend/css-zero-inline-workflow"

    def test_no_technology_refactor_uses_generic_template(self) -> None:
        """operation='refactor' + no technology → 'quality/refactoring' (backward compat)."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent("refactor", technology=None)
        template_id = router._select_template(intent)
        assert template_id == "quality/refactoring"

    def test_unknown_technology_falls_back_to_generic(self) -> None:
        """operation='refactor' + technology='rust' (unknown) → 'quality/refactoring'."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent("refactor", technology="rust")
        template_id = router._select_template(intent)
        assert template_id == "quality/refactoring"


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 2: Technology detection from request text
# (GAP-89-01, GAP-89-03)
# ══════════════════════════════════════════════════════════════════════════════


class TestTechnologyDetection:
    """WorkflowComplexityRouter must detect technology from request metadata and file patterns."""

    def test_detect_technology_from_metadata(self) -> None:
        """Technology explicitly set in metadata should be used."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=["index.html"],
            dependencies=[],
            risk_level="MEDIUM",
            metadata={"technology": "html"},
        )
        tech = router.detect_technology(intent)
        assert tech == "html"

    def test_detect_technology_from_html_files(self) -> None:
        """File extensions .html should detect technology='html'."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=["index.html", "about.html"],
            dependencies=[],
            risk_level="MEDIUM",
            metadata={},
        )
        tech = router.detect_technology(intent)
        assert tech == "html"

    def test_detect_technology_from_css_files(self) -> None:
        """File extensions .css should detect technology='css'."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=["styles.css", "theme.css"],
            dependencies=[],
            risk_level="MEDIUM",
            metadata={},
        )
        tech = router.detect_technology(intent)
        assert tech == "css"

    def test_detect_technology_from_cs_files(self) -> None:
        """File extensions .cs should detect technology='csharp'."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=["Program.cs", "Startup.cs"],
            dependencies=[],
            risk_level="MEDIUM",
            metadata={},
        )
        tech = router.detect_technology(intent)
        assert tech == "csharp"

    def test_detect_technology_from_ts_files(self) -> None:
        """File extensions .ts/.tsx should detect technology='typescript'."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=["app.tsx", "utils.ts"],
            dependencies=[],
            risk_level="MEDIUM",
            metadata={},
        )
        tech = router.detect_technology(intent)
        assert tech == "typescript"

    def test_detect_technology_from_py_files(self) -> None:
        """File extensions .py should detect technology='python'."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=["main.py", "utils.py"],
            dependencies=[],
            risk_level="MEDIUM",
            metadata={},
        )
        tech = router.detect_technology(intent)
        assert tech == "python"

    def test_detect_technology_none_for_mixed_files(self) -> None:
        """Mixed file extensions with no majority should return None."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=["main.py", "index.html", "app.ts"],
            dependencies=[],
            risk_level="MEDIUM",
            metadata={},
        )
        tech = router.detect_technology(intent)
        assert tech is None

    def test_metadata_technology_overrides_file_detection(self) -> None:
        """Explicit metadata technology takes precedence over file extension inference."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=["main.py"],
            dependencies=[],
            risk_level="MEDIUM",
            metadata={"technology": "html"},
        )
        tech = router.detect_technology(intent)
        assert tech == "html"


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 3: End-to-end routing with technology context
# (GAP-89-02, GAP-89-17)
# ══════════════════════════════════════════════════════════════════════════════


class TestEndToEndTechnologyRouting:
    """Full route() flow should select technology-specific templates for complex tasks."""

    def test_complex_html_refactor_routes_to_html_template(self) -> None:
        """Complex HTML refactor should use frontend/html-refactor-validation template."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=[f"page{i}.html" for i in range(6)],
            dependencies=["dep1", "dep2", "dep3"],
            risk_level="HIGH",
            metadata={"technology": "html"},
        )
        decision = router.route(intent)
        # Complexity should be >= MODERATE for 6 files + 3 deps + HIGH risk
        assert decision.template_id == "frontend/html-refactor-validation"

    def test_complex_csharp_refactor_routes_to_csharp_template(self) -> None:
        """Complex C# refactor should use backend/csharp-refactor-workflow template."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=[f"Service{i}.cs" for i in range(6)],
            dependencies=["dep1", "dep2", "dep3", "dep4"],
            risk_level="HIGH",
            metadata={"technology": "csharp"},
        )
        decision = router.route(intent)
        assert decision.template_id == "backend/csharp-refactor-workflow"

    def test_simple_html_fix_routes_to_direct_orchestrator(self) -> None:
        """Simple HTML fix (low complexity) should route to direct orchestrator, not template."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="fix",
            target_files=["index.html"],
            dependencies=[],
            risk_level="LOW",
            metadata={"technology": "html"},
        )
        decision = router.route(intent)
        assert decision.route == RoutingStrategy.DIRECT_ORCHESTRATOR

    def test_generic_refactor_without_tech_uses_quality_template(self) -> None:
        """Generic refactor without technology context → quality/refactoring."""
        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="refactor",
            target_files=[f"file{i}.py" for i in range(6)],

            dependencies=["dep1", "dep2", "dep3"],
            risk_level="HIGH",
            metadata={},
        )
        decision = router.route(intent)
        if decision.route == RoutingStrategy.WORKFLOW_TEMPLATE:
            assert decision.template_id == "quality/refactoring"


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 4: _select_orchestrator() completeness — all 18 execution modes
# (GAP-89-19: Full CORTEX tooling canvas coverage)
# ══════════════════════════════════════════════════════════════════════════════


class TestSelectOrchestratorCompleteness:
    """_select_orchestrator() must map ALL 18 execution modes to named orchestrators."""

    def _make_intent(self, operation: str) -> Intent:
        return Intent(
            operation_type=operation,
            target_files=["file.py"],
            dependencies=[],
            risk_level="LOW",
            metadata={},
        )

    @pytest.mark.parametrize(
        "operation,expected_orchestrator",
        [
            # Core operational
            ("implement", "TDDOrchestrator"),
            ("create", "TDDOrchestrator"),
            ("fix", "RefactoringOrchestrator"),
            ("refactor", "RefactoringOrchestrator"),
            ("test", "TDDOrchestrator"),
            # Analysis
            ("analyze", "AnalysisOrchestrator"),
            ("investigate", "InvestigationOrchestrator"),
            ("audit", "HealthOrchestrator"),
            # Planning & Design
            ("design", "ArchitectOrchestrator"),
            ("plan", "PlanningOrchestrator"),
            # Content
            ("document", "DocumentationOrchestrator"),
            ("digest", "DigestSessionOrchestrator"),
            # Support
            ("security", "SecurityOrchestrator"),
            ("deploy", "DeploymentOrchestrator"),
            ("update", "RefactoringOrchestrator"),
            # NEW: Previously unmapped modes
            ("vacuum", "VacuumOrchestrator"),
            ("debug", "DebuggerOrchestrator"),
            ("health", "HealthOrchestrator"),
            ("sync", "GitOrchestrator"),
            ("train", "TrainerOrchestrator"),
            ("totalrecall", "MasterOrchestrator"),
            ("rca", "InvestigationOrchestrator"),
            ("golden_test", "TDDOrchestrator"),
            ("onboard", "RepositoryOnboardingOrchestrator"),
            ("rephrase", "RequestRephraseOrchestrator"),
        ],
    )
    def test_operation_maps_to_correct_orchestrator(
        self, operation: str, expected_orchestrator: str
    ) -> None:
        """Each operation type must map to its canonical orchestrator."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent(operation)
        result = router._select_orchestrator(intent)
        assert result == expected_orchestrator, (
            f"Operation '{operation}' mapped to '{result}', expected '{expected_orchestrator}'"
        )

    def test_default_fallback_is_interaction_orchestrator(self) -> None:
        """Unknown operations must fallback to InteractionOrchestrator (LENS comprehension)."""
        router = WorkflowComplexityRouter()
        intent = self._make_intent("xyzzy_unknown_operation")
        result = router._select_orchestrator(intent)
        assert result == "InteractionOrchestrator", (
            f"Default fallback is '{result}', expected 'InteractionOrchestrator'"
        )

