"""
Phase 103-d: MCP Tool God Object Split — TDD RED tests.

Tests assert each MCP tool class is importable from its own dedicated module
AND from the original aggregator files (backward compatibility guaranteed).

CORE-008: Tests written before extraction (TDD RED gate).
SWEEP-103-GOD-OBJECT-DECOMPOSITION / GAP-103-07
"""
import pytest


# ── utilities.py split: 9 classes → 9 dedicated modules ─────────────────────

class TestCortexVerifyExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_verify_tool import CortexVerify  # noqa: F401
        assert CortexVerify is not None

    def test_same_class_as_utilities(self) -> None:
        from cortex.mcp.tools.cortex_verify_tool import CortexVerify as A
        from cortex.mcp.tools.utilities import CortexVerify as B
        assert A is B


class TestCortexAskExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_ask_tool import CortexAsk  # noqa: F401
        assert CortexAsk is not None

    def test_same_class_as_utilities(self) -> None:
        from cortex.mcp.tools.cortex_ask_tool import CortexAsk as A
        from cortex.mcp.tools.utilities import CortexAsk as B
        assert A is B


class TestCortexVacuumExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_vacuum_tool import CortexVacuum  # noqa: F401
        assert CortexVacuum is not None

    def test_same_class_as_utilities(self) -> None:
        from cortex.mcp.tools.cortex_vacuum_tool import CortexVacuum as A
        from cortex.mcp.tools.utilities import CortexVacuum as B
        assert A is B


class TestCortexToolsCatalogExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_tools_catalog_tool import CortexToolsCatalog  # noqa: F401
        assert CortexToolsCatalog is not None

    def test_same_class_as_utilities(self) -> None:
        from cortex.mcp.tools.cortex_tools_catalog_tool import CortexToolsCatalog as A
        from cortex.mcp.tools.utilities import CortexToolsCatalog as B
        assert A is B


class TestCortexTotalRecallExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_total_recall_tool import CortexTotalRecall  # noqa: F401
        assert CortexTotalRecall is not None

    def test_same_class_as_utilities(self) -> None:
        from cortex.mcp.tools.cortex_total_recall_tool import CortexTotalRecall as A
        from cortex.mcp.tools.utilities import CortexTotalRecall as B
        assert A is B


class TestCortexMetricsExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_metrics_tool import CortexMetrics  # noqa: F401
        assert CortexMetrics is not None

    def test_same_class_as_utilities(self) -> None:
        from cortex.mcp.tools.cortex_metrics_tool import CortexMetrics as A
        from cortex.mcp.tools.utilities import CortexMetrics as B
        assert A is B


class TestCortexCheckExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_check_tool import CortexCheck  # noqa: F401
        assert CortexCheck is not None

    def test_same_class_as_utilities(self) -> None:
        from cortex.mcp.tools.cortex_check_tool import CortexCheck as A
        from cortex.mcp.tools.utilities import CortexCheck as B
        assert A is B


class TestCortexVisionExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_vision_tool import CortexVision  # noqa: F401
        assert CortexVision is not None

    def test_same_class_as_utilities(self) -> None:
        from cortex.mcp.tools.cortex_vision_tool import CortexVision as A
        from cortex.mcp.tools.utilities import CortexVision as B
        assert A is B


class TestCortexOrchestratorToolExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_orchestrator_tool import CortexOrchestrator  # noqa: F401
        assert CortexOrchestrator is not None

    def test_same_class_as_utilities(self) -> None:
        from cortex.mcp.tools.cortex_orchestrator_tool import CortexOrchestrator as A
        from cortex.mcp.tools.utilities import CortexOrchestrator as B
        assert A is B


# ── operations.py split: 5 classes → 5 dedicated modules ────────────────────

class TestCortexDebugExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_debug_tool import CortexDebug  # noqa: F401
        assert CortexDebug is not None

    def test_same_class_as_operations(self) -> None:
        from cortex.mcp.tools.cortex_debug_tool import CortexDebug as A
        from cortex.mcp.tools.operations import CortexDebug as B
        assert A is B


class TestCortexRefactorExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_refactor_tool import CortexRefactor  # noqa: F401
        assert CortexRefactor is not None

    def test_same_class_as_operations(self) -> None:
        from cortex.mcp.tools.cortex_refactor_tool import CortexRefactor as A
        from cortex.mcp.tools.operations import CortexRefactor as B
        assert A is B


class TestCortexPlanExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_plan_tool import CortexPlan  # noqa: F401
        assert CortexPlan is not None

    def test_same_class_as_operations(self) -> None:
        from cortex.mcp.tools.cortex_plan_tool import CortexPlan as A
        from cortex.mcp.tools.operations import CortexPlan as B
        assert A is B


class TestCortexOnboardExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_onboard_tool import CortexOnboard  # noqa: F401
        assert CortexOnboard is not None

    def test_same_class_as_operations(self) -> None:
        from cortex.mcp.tools.cortex_onboard_tool import CortexOnboard as A
        from cortex.mcp.tools.operations import CortexOnboard as B
        assert A is B


class TestCortexDashboardExtracted:
    def test_importable_from_dedicated_module(self) -> None:
        from cortex.mcp.tools.cortex_dashboard_tool import CortexDashboard  # noqa: F401
        assert CortexDashboard is not None

    def test_same_class_as_operations(self) -> None:
        from cortex.mcp.tools.cortex_dashboard_tool import CortexDashboard as A
        from cortex.mcp.tools.operations import CortexDashboard as B
        assert A is B
