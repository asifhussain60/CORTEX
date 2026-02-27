"""
Phase 80-c — GAP-80-03: OrchestratorProtocolMixin return type alignment.

Tests that the four mixin default methods return Result (Ok or Err)
instances, satisfying the IOrchestrator ABC contract.

CORE-008: Tests written first (RED phase).
"""

import pytest


class TestOrchestratorProtocolMixinResultTypes:
    """Tests for GAP-80-03: mixin methods must return Result[T], not plain dicts."""

    def _make_mixin(self):
        """Return a bare OrchestratorProtocolMixin instance."""
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        return OrchestratorProtocolMixin()

    def test_mixin_initialize_returns_result(self):
        """initialize() must return an Ok or Err instance, not a plain dict."""
        from cortex.core.result import Ok, Err
        mixin = self._make_mixin()
        result = mixin.initialize()
        assert isinstance(result, (Ok, Err)), (
            f"initialize() returned {type(result).__name__}, expected Ok or Err"
        )

    def test_mixin_get_mcp_tools_returns_result(self):
        """get_mcp_tools() must return an Ok or Err instance."""
        from cortex.core.result import Ok, Err
        mixin = self._make_mixin()
        result = mixin.get_mcp_tools()
        assert isinstance(result, (Ok, Err)), (
            f"get_mcp_tools() returned {type(result).__name__}, expected Ok or Err"
        )

    def test_mixin_execute_operation_returns_result(self):
        """execute_operation() must return an Ok or Err instance."""
        from cortex.core.result import Ok, Err
        mixin = self._make_mixin()
        result = mixin.execute_operation("test_op", {})
        assert isinstance(result, (Ok, Err)), (
            f"execute_operation() returned {type(result).__name__}, expected Ok or Err"
        )

    def test_mixin_get_audit_trail_returns_result(self):
        """get_audit_trail() must return an Ok or Err instance."""
        from cortex.core.result import Ok, Err
        mixin = self._make_mixin()
        result = mixin.get_audit_trail()
        assert isinstance(result, (Ok, Err)), (
            f"get_audit_trail() returned {type(result).__name__}, expected Ok or Err"
        )

    def test_mixin_initialize_ok_value_is_dict(self):
        """initialize() Ok value should be a dict with 'status' key."""
        from cortex.core.result import Ok
        mixin = self._make_mixin()
        result = mixin.initialize()
        assert isinstance(result, Ok)
        assert "status" in result.value

    def test_mixin_get_audit_trail_ok_value_is_list(self):
        """get_audit_trail() Ok value should be a list."""
        from cortex.core.result import Ok
        mixin = self._make_mixin()
        result = mixin.get_audit_trail()
        assert isinstance(result, Ok)
        assert isinstance(result.value, list)
