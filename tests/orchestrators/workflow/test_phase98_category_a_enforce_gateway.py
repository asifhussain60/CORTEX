"""
Phase 98 — Category A Gateway Activation: @enforce_gateway on TDD, Refactoring,
Debugger, SecurityVulnerability orchestrators.

These 4 orchestrators were classified as Category A (receive structured mode strings
like "IMPLEMENT", "REFACTOR", "DEBUG") but were missing @enforce_gateway on
execute_operation(). Phase 98 closes this gap.

AC-ID: AC-P98-GATEWAY-A-001
CORE-008: TDD mandatory — tests before implementation
CORE-064: Sweep Completeness — all 4 orchestrators checked
"""

from __future__ import annotations

import functools
from typing import Any

import pytest

from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin, enforce_gateway


def _has_enforce_gateway(cls: type, method_name: str) -> bool:
    """Check if a method is decorated with @enforce_gateway.

    Detects the functools.wraps wrapper injected by the decorator.
    """
    method = getattr(cls, method_name, None)
    if method is None:
        return False
    return hasattr(method, "__wrapped__")


class TestTDDOrchestratorPhase98:
    """TDD Orchestrator: Category A — PHASE90_GATEWAY_ENABLED=True, @enforce_gateway applied."""

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert issubclass(TDDOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_true_category_a(self) -> None:
        """Category A: receives 'TDD' / 'IMPLEMENT' mode strings from gateway."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert TDDOrchestrator.PHASE90_GATEWAY_ENABLED is True

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert _has_enforce_gateway(TDDOrchestrator, "execute_operation"), (
            "TDDOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )


class TestRefactoringOrchestratorPhase98:
    """Refactoring Orchestrator: Category A — PHASE90_GATEWAY_ENABLED=True, @enforce_gateway applied."""

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator
        assert issubclass(RefactoringOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_true_category_a(self) -> None:
        """Category A: receives 'REFACTOR' mode string from gateway."""
        from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator
        assert RefactoringOrchestrator.PHASE90_GATEWAY_ENABLED is True

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator
        assert _has_enforce_gateway(RefactoringOrchestrator, "execute_operation"), (
            "RefactoringOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )


class TestDebuggerOrchestratorPhase98:
    """Debugger Orchestrator: Category A — PHASE90_GATEWAY_ENABLED=True, @enforce_gateway applied."""

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert issubclass(DebuggerOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_true_category_a(self) -> None:
        """Category A: receives 'DEBUG' mode string from gateway."""
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert DebuggerOrchestrator.PHASE90_GATEWAY_ENABLED is True

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert _has_enforce_gateway(DebuggerOrchestrator, "execute_operation"), (
            "DebuggerOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )


class TestSecurityVulnerabilityOrchestratorPhase98:
    """SecurityVulnerability Orchestrator: PHASE90_GATEWAY_EXEMPT=True, @enforce_gateway armed.

    Security analysis is invoked by the enforcement pipeline — self-gating is
    circular. The decorator is applied for traceability and future promotion,
    but PHASE90_GATEWAY_EXEMPT=True bypasses actual routing.
    """

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.validation.security_vulnerability_orchestrator import SecurityVulnerabilityOrchestrator
        assert issubclass(SecurityVulnerabilityOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_exempt_is_true(self) -> None:
        """Exempt: enforcement pipeline invokes this — circular self-gating avoided."""
        from cortex.orchestrators.validation.security_vulnerability_orchestrator import SecurityVulnerabilityOrchestrator
        assert SecurityVulnerabilityOrchestrator.PHASE90_GATEWAY_EXEMPT is True

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.validation.security_vulnerability_orchestrator import SecurityVulnerabilityOrchestrator
        assert _has_enforce_gateway(SecurityVulnerabilityOrchestrator, "execute_operation"), (
            "SecurityVulnerabilityOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )
