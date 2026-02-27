"""
Phase 80-f — GAP-80-06: Singleton EnforcementOrchestrator in _governance_gate().

Tests that consecutive calls to _governance_gate() use the SAME
EnforcementOrchestrator instance (not a fresh one each time).

CORE-008: Tests written first (RED phase).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch
import threading

import pytest


class TestGovernanceGateSingleton:
    """Tests for GAP-80-06: singleton EnforcementOrchestrator in _governance_gate."""

    def _make_mixin(self):
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        return OrchestratorProtocolMixin()

    def test_governance_gate_no_new_construction_on_repeat_calls(self):
        """EnforcementOrchestrator constructor called at most once across N calls."""
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator
        mixin = self._make_mixin()
        call_count = []

        original_init = EnforcementOrchestrator.__init__

        def counting_init(self_inner, *args, **kwargs):
            call_count.append(1)
            original_init(self_inner, *args, **kwargs)

        with patch.object(EnforcementOrchestrator, "__init__", counting_init):
            for _ in range(5):
                mixin._governance_gate("test_op")

        # Constructor should be called at most once (singleton)
        assert len(call_count) <= 1, (
            f"EnforcementOrchestrator constructed {len(call_count)} times "
            f"across 5 _governance_gate() calls — expected ≤1 (singleton)"
        )

    def test_governance_gate_returns_bool(self):
        """_governance_gate() must return a bool."""
        mixin = self._make_mixin()
        result = mixin._governance_gate("test_op")
        assert isinstance(result, bool)

    def test_governance_gate_singleton_function_exists(self):
        """_get_enforcement_orchestrator factory function must exist at module level."""
        import cortex.core.orchestrator_protocol_mixin as mod
        assert hasattr(mod, "_get_enforcement_orchestrator"), (
            "Module-level _get_enforcement_orchestrator() factory is missing"
        )

    def test_get_enforcement_orchestrator_returns_same_instance(self):
        """_get_enforcement_orchestrator() must return the same instance on repeat calls."""
        import cortex.core.orchestrator_protocol_mixin as mod
        if not hasattr(mod, "_get_enforcement_orchestrator"):
            pytest.skip("_get_enforcement_orchestrator not yet implemented")
        inst1 = mod._get_enforcement_orchestrator()
        inst2 = mod._get_enforcement_orchestrator()
        assert inst1 is inst2, (
            "_get_enforcement_orchestrator() returned different instances"
        )

    def test_governance_gate_thread_safe(self):
        """Concurrent calls to _governance_gate() all get the same singleton."""
        import cortex.core.orchestrator_protocol_mixin as mod
        if not hasattr(mod, "_get_enforcement_orchestrator"):
            pytest.skip("_get_enforcement_orchestrator not yet implemented")

        instances = []
        barrier = threading.Barrier(5)

        def call_factory():
            barrier.wait()
            instances.append(id(mod._get_enforcement_orchestrator()))

        threads = [threading.Thread(target=call_factory) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(set(instances)) == 1, (
            f"Thread-safety violation: got {len(set(instances))} distinct instances"
        )
