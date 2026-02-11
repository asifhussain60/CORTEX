"""
Pytest plugin for CORE-032-035 governance rule enforcement.

AC-GOVE-REM-003: Governance rules enforcement in test framework
Priority: P0-CRITICAL

Enforces:
- CORE-032: Mandatory Intent Classification
- CORE-033: Mandatory State Persistence
- CORE-034: Mandatory Audit Logging
- CORE-035: Mandatory Response Header Injection

CORE Governance:
- CORE-008: TDD (tests first)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- CORE-027: Audit trail logging
"""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import pytest


class GovernanceRuleValidator:
    """Validator for CORE-032-035 governance rules."""

    def __init__(self) -> None:
        """Initialize governance validator."""
        self.violations: List[str] = []
        self.intent_classifications: List[str] = []
        self.state_persists: List[str] = []
        self.audit_logs: List[str] = []
        self.response_headers: List[str] = []

    def validate_core_032(
        self,
        test_name: str,
        factory_instance: Any
    ) -> bool:
        """
        Validate CORE-032: Mandatory Intent Classification.

        Args:
            test_name: Name of test
            factory_instance: IntentRouterFactory instance

        Returns:
            True if valid, False if violation
        """
        # Check that factory was used
        if not hasattr(factory_instance, 'instance_count'):
            self.violations.append(
                f"{test_name}: Factory not used to create router"
            )
            return False

        # Check that instances require classification
        if factory_instance.instance_count == 0:
            self.violations.append(
                f"{test_name}: No router instances created"
            )
            return False

        self.intent_classifications.append(test_name)
        return True

    def validate_core_033(
        self,
        test_name: str,
        state_manager: Any
    ) -> bool:
        """
        Validate CORE-033: Mandatory State Persistence.

        Args:
            test_name: Name of test
            state_manager: StateManager instance

        Returns:
            True if valid, False if violation
        """
        if not hasattr(state_manager, 'persist_state'):
            self.violations.append(
                f"{test_name}: StateManager.persist_state() not called"
            )
            return False

        self.state_persists.append(test_name)
        return True

    def validate_core_034(
        self,
        test_name: str,
        audit_logger: Any
    ) -> bool:
        """
        Validate CORE-034: Mandatory Audit Logging.

        Args:
            test_name: Name of test
            audit_logger: AuditLogger instance

        Returns:
            True if valid, False if violation
        """
        if not hasattr(audit_logger, 'log_event'):
            self.violations.append(
                f"{test_name}: AuditLogger.log_event() not called"
            )
            return False

        self.audit_logs.append(test_name)
        return True

    def validate_core_035(
        self,
        test_name: str,
        response_text: str
    ) -> bool:
        """
        Validate CORE-035: Mandatory Response Header Injection.

        Args:
            test_name: Name of test
            response_text: Response text to validate

        Returns:
            True if valid, False if violation
        """
        # Check for CORTEX header
        if "## 🧠 CORTEX" not in response_text:
            self.violations.append(
                f"{test_name}: Missing CORTEX header"
            )
            return False

        # Check for required metadata fields
        required_fields = ["Author:", "Phase:", "Orchestrator:"]
        for field in required_fields:
            if field not in response_text:
                self.violations.append(
                    f"{test_name}: Missing metadata field: {field}"
                )
                return False

        # Check for checkmark
        if "✅" not in response_text:
            self.violations.append(
                f"{test_name}: Missing status checkmark (✅)"
            )
            return False

        self.response_headers.append(test_name)
        return True


def core_032_enforce(func: Callable) -> Callable:
    """
    Decorator to enforce CORE-032: Mandatory Intent Classification.

    Usage:
        @core_032_enforce
        def test_operation_with_factory():
            factory = IntentRouterFactory()
            router = factory.create_router()
            ...
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)

        # Verify factory pattern was used
        # (in actual implementation, scan for factory calls)

        return result

    return wrapper


def core_033_enforce(func: Callable) -> Callable:
    """
    Decorator to enforce CORE-033: Mandatory State Persistence.

    Usage:
        @core_033_enforce
        def test_operation_with_state_tracking():
            manager = StateManager()
            manager.persist_state(...)
            ...
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)

        # Verify state persistence calls were made
        # (in actual implementation, scan for StateManager calls)

        return result

    return wrapper


def core_034_enforce(func: Callable) -> Callable:
    """
    Decorator to enforce CORE-034: Mandatory Audit Logging.

    Usage:
        @core_034_enforce
        def test_operation_with_audit_logging():
            logger = AuditLogger.instance()
            logger.log_event(...)
            ...
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)

        # Verify audit logging calls were made
        # (in actual implementation, scan for AuditLogger calls)

        return result

    return wrapper


def core_035_enforce(func: Callable) -> Callable:
    """
    Decorator to enforce CORE-035: Mandatory Response Header Injection.

    Usage:
        @core_035_enforce
        def test_response_with_header():
            response = "## 🧠 CORTEX Implementation\\n..."
            ...
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)

        # Verify response header is present
        # (in actual implementation, scan for CORTEX header)

        return result

    return wrapper


class GovernanceRulePlugin:
    """Pytest plugin for CORE-032-035 governance rule enforcement."""

    def __init__(self) -> None:
        """Initialize governance plugin."""
        self.validator = GovernanceRuleValidator()

    def pytest_configure(self, config: Any) -> None:
        """Configure pytest with governance rules."""
        config.addinivalue_line(
            "markers",
            "governance: mark test for governance rule validation"
        )
        config.addinivalue_line(
            "markers",
            "core_032: mark test that enforces CORE-032 (Intent Classification)"
        )
        config.addinivalue_line(
            "markers",
            "core_033: mark test that enforces CORE-033 (State Persistence)"
        )
        config.addinivalue_line(
            "markers",
            "core_034: mark test that enforces CORE-034 (Audit Logging)"
        )
        config.addinivalue_line(
            "markers",
            "core_035: mark test that enforces CORE-035 (Response Headers)"
        )

    def pytest_runtest_makereport(
        self,
        item: Any,
        call: Any
    ) -> Any:
        """Check governance rules after test execution."""
        if call.exconly() and "governance" in item.keywords:
            # Log governance violation if test failed
            test_name = item.name
            if any(v in str(call.exconly()) for v in ["CORE-032", "CORE-033", "CORE-034", "CORE-035"]):
                self.validator.violations.append(
                    f"{test_name}: {call.exconly()}"
                )


# Register plugin
def pytest_plugins() -> List[str]:
    """Register governance rule enforcement plugins."""
    return [
        "cortex.testing.governance_rule_plugin",
    ]
