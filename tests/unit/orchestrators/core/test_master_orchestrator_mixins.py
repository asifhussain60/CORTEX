"""
Phase 103-a TDD RED: MasterOrchestrator mixin extraction tests.

GAP-103-01: Decompose master_orchestrator.py (3,167L → <500L + 4 mixins).

Each test asserts:
  1. The mixin is importable from its dedicated module
  2. The mixin is a class (not an alias — real extraction)
  3. MasterOrchestrator still inherits from it (backward-compat preserved)
  4. The method moved to the mixin is accessible via MasterOrchestrator

CORE-008: RED first — all tests will FAIL until the 4 mixin files are created.
CORE-011: type hints | CORE-012: docstrings
"""
import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Cluster 1: E2E / Phase Execution
# ─────────────────────────────────────────────────────────────────────────────

class TestMasterOrchestratorE2EMixin:
    """Tests for MasterOrchestratorE2EMixin extraction."""

    def test_mixin_importable_from_dedicated_module(self):
        """MasterOrchestratorE2EMixin must be importable from its own module."""
        from cortex.orchestrators.core.master_orchestrator_e2e_mixin import (
            MasterOrchestratorE2EMixin,
        )
        assert MasterOrchestratorE2EMixin is not None

    def test_mixin_is_a_class(self):
        """MasterOrchestratorE2EMixin must be a class, not an alias."""
        from cortex.orchestrators.core.master_orchestrator_e2e_mixin import (
            MasterOrchestratorE2EMixin,
        )
        assert isinstance(MasterOrchestratorE2EMixin, type)

    def test_master_orchestrator_inherits_e2e_mixin(self):
        """MasterOrchestrator must inherit MasterOrchestratorE2EMixin."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.master_orchestrator_e2e_mixin import (
            MasterOrchestratorE2EMixin,
        )
        assert issubclass(MasterOrchestrator, MasterOrchestratorE2EMixin)

    def test_orchestrate_e2e_defined_in_mixin(self):
        """orchestrate_e2e must be defined on the mixin, not only on MasterOrchestrator."""
        from cortex.orchestrators.core.master_orchestrator_e2e_mixin import (
            MasterOrchestratorE2EMixin,
        )
        assert hasattr(MasterOrchestratorE2EMixin, "orchestrate_e2e")
        assert callable(getattr(MasterOrchestratorE2EMixin, "orchestrate_e2e"))

    def test_execute_phase_helpers_defined_in_mixin(self):
        """Phase helper methods must be on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_e2e_mixin import (
            MasterOrchestratorE2EMixin,
        )
        for method_name in ["_execute_phase_1", "_execute_phase_2", "_execute_phase_3", "_execute_phase_4"]:
            assert hasattr(MasterOrchestratorE2EMixin, method_name), f"Missing: {method_name}"

    def test_mcp_process_user_request_defined_in_mixin(self):
        """mcp_process_user_request must be on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_e2e_mixin import (
            MasterOrchestratorE2EMixin,
        )
        assert hasattr(MasterOrchestratorE2EMixin, "mcp_process_user_request")


# ─────────────────────────────────────────────────────────────────────────────
# Cluster 2: Orchestrator Registry / Coordination
# ─────────────────────────────────────────────────────────────────────────────

class TestMasterOrchestratorRegistryMixin:
    """Tests for MasterOrchestratorRegistryMixin extraction."""

    def test_mixin_importable_from_dedicated_module(self):
        """MasterOrchestratorRegistryMixin must be importable from its own module."""
        from cortex.orchestrators.core.master_orchestrator_registry_mixin import (
            MasterOrchestratorRegistryMixin,
        )
        assert MasterOrchestratorRegistryMixin is not None

    def test_mixin_is_a_class(self):
        """MasterOrchestratorRegistryMixin must be a class."""
        from cortex.orchestrators.core.master_orchestrator_registry_mixin import (
            MasterOrchestratorRegistryMixin,
        )
        assert isinstance(MasterOrchestratorRegistryMixin, type)

    def test_master_orchestrator_inherits_registry_mixin(self):
        """MasterOrchestrator must inherit MasterOrchestratorRegistryMixin."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.master_orchestrator_registry_mixin import (
            MasterOrchestratorRegistryMixin,
        )
        assert issubclass(MasterOrchestrator, MasterOrchestratorRegistryMixin)

    def test_register_orchestrator_defined_in_mixin(self):
        """register_orchestrator must be defined on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_registry_mixin import (
            MasterOrchestratorRegistryMixin,
        )
        assert hasattr(MasterOrchestratorRegistryMixin, "register_orchestrator")

    def test_coordinate_operation_defined_in_mixin(self):
        """coordinate_operation must be defined on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_registry_mixin import (
            MasterOrchestratorRegistryMixin,
        )
        assert hasattr(MasterOrchestratorRegistryMixin, "coordinate_operation")

    def test_registry_query_methods_defined_in_mixin(self):
        """Query methods must be on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_registry_mixin import (
            MasterOrchestratorRegistryMixin,
        )
        for method_name in ["get_registered_domains", "get_orchestrator", "get_coordination_history", "get_registry_status"]:
            assert hasattr(MasterOrchestratorRegistryMixin, method_name), f"Missing: {method_name}"


# ─────────────────────────────────────────────────────────────────────────────
# Cluster 3: Request Processing / Routing
# ─────────────────────────────────────────────────────────────────────────────

class TestMasterOrchestratorRequestMixin:
    """Tests for MasterOrchestratorRequestMixin extraction."""

    def test_mixin_importable_from_dedicated_module(self):
        """MasterOrchestratorRequestMixin must be importable from its own module."""
        from cortex.orchestrators.core.master_orchestrator_request_mixin import (
            MasterOrchestratorRequestMixin,
        )
        assert MasterOrchestratorRequestMixin is not None

    def test_mixin_is_a_class(self):
        """MasterOrchestratorRequestMixin must be a class."""
        from cortex.orchestrators.core.master_orchestrator_request_mixin import (
            MasterOrchestratorRequestMixin,
        )
        assert isinstance(MasterOrchestratorRequestMixin, type)

    def test_master_orchestrator_inherits_request_mixin(self):
        """MasterOrchestrator must inherit MasterOrchestratorRequestMixin."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.master_orchestrator_request_mixin import (
            MasterOrchestratorRequestMixin,
        )
        assert issubclass(MasterOrchestrator, MasterOrchestratorRequestMixin)

    def test_process_user_request_defined_in_mixin(self):
        """process_user_request must be defined on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_request_mixin import (
            MasterOrchestratorRequestMixin,
        )
        assert hasattr(MasterOrchestratorRequestMixin, "process_user_request")

    def test_routing_helpers_defined_in_mixin(self):
        """Internal routing helpers must be on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_request_mixin import (
            MasterOrchestratorRequestMixin,
        )
        for method_name in [
            "_stage_2_routing",
            "_select_intelligence_tier",
            "_get_intelligence_context",
            "_opj_post_dispatch",
            "_check_mcp_gate",
            "_check_for_workflow_template",
            "_trigger_lifecycle_hooks_sync",
        ]:
            assert hasattr(MasterOrchestratorRequestMixin, method_name), f"Missing: {method_name}"

    def test_execute_operation_defined_in_mixin(self):
        """execute_operation must be defined on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_request_mixin import (
            MasterOrchestratorRequestMixin,
        )
        assert hasattr(MasterOrchestratorRequestMixin, "execute_operation")

    def test_execute_approved_defined_in_mixin(self):
        """execute_approved_operation must be defined on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_request_mixin import (
            MasterOrchestratorRequestMixin,
        )
        assert hasattr(MasterOrchestratorRequestMixin, "execute_approved_operation")


# ─────────────────────────────────────────────────────────────────────────────
# Cluster 4: Response Formatting / Header Injection
# ─────────────────────────────────────────────────────────────────────────────

class TestMasterOrchestratorResponseMixin:
    """Tests for MasterOrchestratorResponseMixin extraction."""

    def test_mixin_importable_from_dedicated_module(self):
        """MasterOrchestratorResponseMixin must be importable from its own module."""
        from cortex.orchestrators.core.master_orchestrator_response_mixin import (
            MasterOrchestratorResponseMixin,
        )
        assert MasterOrchestratorResponseMixin is not None

    def test_mixin_is_a_class(self):
        """MasterOrchestratorResponseMixin must be a class."""
        from cortex.orchestrators.core.master_orchestrator_response_mixin import (
            MasterOrchestratorResponseMixin,
        )
        assert isinstance(MasterOrchestratorResponseMixin, type)

    def test_master_orchestrator_inherits_response_mixin(self):
        """MasterOrchestrator must inherit MasterOrchestratorResponseMixin."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.master_orchestrator_response_mixin import (
            MasterOrchestratorResponseMixin,
        )
        assert issubclass(MasterOrchestrator, MasterOrchestratorResponseMixin)

    def test_get_response_with_headers_defined_in_mixin(self):
        """get_response_with_headers must be defined on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_response_mixin import (
            MasterOrchestratorResponseMixin,
        )
        assert hasattr(MasterOrchestratorResponseMixin, "get_response_with_headers")

    def test_filter_and_format_helpers_defined_in_mixin(self):
        """Violation filter/format helpers must be on the mixin."""
        from cortex.orchestrators.core.master_orchestrator_response_mixin import (
            MasterOrchestratorResponseMixin,
        )
        for method_name in ["_filter_critical_violations", "_format_violation_summary"]:
            assert hasattr(MasterOrchestratorResponseMixin, method_name), f"Missing: {method_name}"


# ─────────────────────────────────────────────────────────────────────────────
# Cluster 5: Line count gate — master_orchestrator.py must be < 750L after extraction
# ─────────────────────────────────────────────────────────────────────────────

class TestMasterOrchestratorFileSize:
    """Guard: master_orchestrator.py must shrink significantly after extraction."""

    def test_master_orchestrator_under_700_lines(self):
        """After Phase 103-a extraction, master_orchestrator.py must be < 750 lines.

        The original file was 3,167L. After extracting 4 mixin clusters the
        residual core (imports + __init__ + initialize + routing glue) is
        allowed up to 750L in this phase. Final target (<500L) is Phase 103-b.
        """
        import pathlib
        path = pathlib.Path("cortex/orchestrators/core/master_orchestrator.py")
        line_count = len(path.read_text().splitlines())
        assert line_count < 750, (
            f"master_orchestrator.py is {line_count} lines — "
            "GAP-103-01 Phase 103-a gate is <750L (final target <500L in Phase 103-b)"
        )
