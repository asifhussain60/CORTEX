"""
DevelopmentRouter Middleware - Enforce CORE-019 Governance Rule

CORE-019: All Development Must Go Through TDD-Master Orchestrator
  - ALL feature development MUST route through TDD-Master v1
  - Direct coding without TDD is blocked
  - Ensures RED→GREEN→REFACTOR cycle for all changes
  - Required for Phase 2 (Orchestration Core) default workflow

Author: CORTEX Governance System
Version: 1.0.0
Created: 2026-01-12
"""

import logging
from typing import Optional, Callable, Any, Tuple
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)


class DevelopmentType(Enum):
    """Types of development activities."""

    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    INFRASTRUCTURE = "infrastructure"
    TEST = "test"
    DOCUMENTATION = "documentation"


class DevelopmentRouter:
    """Middleware to enforce CORE-019 TDD-Master requirement for all development."""

    # Activities that MUST go through TDD-Master
    TDD_REQUIRED_TYPES = {
        DevelopmentType.FEATURE,
        DevelopmentType.BUGFIX,
        DevelopmentType.REFACTOR,
        DevelopmentType.INFRASTRUCTURE,
    }

    # Activities that CAN bypass TDD-Master
    BYPASS_ALLOWED_TYPES = {
        DevelopmentType.DOCUMENTATION,
    }

    def __init__(self):
        self.tdd_master_available = self._check_tdd_master_available()

    def _check_tdd_master_available(self) -> bool:
        """
        Check if TDD-Master orchestrator is available.

        Returns:
            True if TDD-Master is available
        """
        try:
            # Try to import TDD-Master orchestrator
            from src.orchestrators.core import tdd_master

            logger.info("✅ TDD-Master orchestrator is available")
            return True
        except ImportError:
            logger.warning("⚠️  TDD-Master orchestrator not yet available")
            return False

    def should_route_to_tdd_master(
        self, dev_type: DevelopmentType
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if a development activity should route to TDD-Master.

        Args:
            dev_type: Type of development activity

        Returns:
            Tuple of (should_route: bool, reason: str or None)
        """
        if dev_type in self.TDD_REQUIRED_TYPES:
            if not self.tdd_master_available:
                return (
                    False,
                    "CORE-019 WARNING: TDD-Master not yet implemented. "
                    "Phase 2 orchestration core required for this feature.",
                )
            return True, f"Route {dev_type.value} development through TDD-Master"

        if dev_type in self.BYPASS_ALLOWED_TYPES:
            return False, f"{dev_type.value} activity can bypass TDD-Master"

        return (
            False,
            f"Unknown development type: {dev_type}. Cannot determine routing.",
        )

    def validate_development_request(
        self, dev_type: DevelopmentType, context: dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a development request against CORE-019 rules.

        Args:
            dev_type: Type of development
            context: Development context (e.g., feature name, bug ID)

        Returns:
            Tuple of (is_valid: bool, reason: str or None)
        """
        should_route, reason = self.should_route_to_tdd_master(dev_type)

        if should_route and not self.tdd_master_available:
            return (
                False,
                "CORE-019 VIOLATION: Direct development forbidden. "
                "Must route through TDD-Master orchestrator.",
            )

        return True, reason

    def get_tdd_master_command(self, dev_type: DevelopmentType, context: dict) -> str:
        """
        Generate the TDD-Master command for a development activity.

        Args:
            dev_type: Type of development
            context: Development context

        Returns:
            TDD-Master command string
        """
        feature_name = context.get('feature_name', 'unnamed')
        description = context.get('description', '')

        if dev_type == DevelopmentType.FEATURE:
            return (
                f"python3 -m src.main 'implement {feature_name}' "
                f"--tdd-master --description '{description}'"
            )
        elif dev_type == DevelopmentType.BUGFIX:
            return (
                f"python3 -m src.main 'fix {feature_name}' "
                f"--tdd-master --bug-id {context.get('bug_id', '')}"
            )
        elif dev_type == DevelopmentType.REFACTOR:
            return (
                f"python3 -m src.main 'refactor {feature_name}' "
                f"--tdd-master --scope {context.get('scope', 'local')}"
            )
        elif dev_type == DevelopmentType.INFRASTRUCTURE:
            return (
                f"python3 -m src.main 'build-infrastructure {feature_name}' "
                f"--tdd-master --component {context.get('component', '')}"
            )
        else:
            return f"python3 -m src.main 'process {feature_name}'"

    def log_routing_decision(
        self,
        dev_type: DevelopmentType,
        context: dict,
        routed_to_tdd: bool,
    ) -> None:
        """
        Log routing decision for audit trail.

        Args:
            dev_type: Type of development
            context: Development context
            routed_to_tdd: Whether routed to TDD-Master
        """
        if routed_to_tdd:
            logger.info(
                f"📌 CORE-019 ENFORCED: {dev_type.value} development "
                f"routed to TDD-Master (context: {context})"
            )
        else:
            logger.info(
                f"✅ CORE-019 BYPASS: {dev_type.value} development "
                f"bypasses TDD-Master (context: {context})"
            )


def enforce_tdd_master_routing(dev_type: DevelopmentType):
    """
    Decorator to enforce TDD-Master routing on development functions.

    Args:
        dev_type: Type of development activity
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            router = DevelopmentRouter()

            # Get context from kwargs
            context = kwargs.get('context', {})

            # Validate development request
            is_valid, reason = router.validate_development_request(dev_type, context)

            if not is_valid:
                logger.error(f"🚫 Development routing failed: {reason}")
                raise DevelopmentRoutingError(reason)

            # Log routing decision
            should_route, _ = router.should_route_to_tdd_master(dev_type)
            router.log_routing_decision(dev_type, context, should_route)

            # Execute the wrapped function
            return func(*args, **kwargs)

        return wrapper

    return decorator


class DevelopmentRoutingError(Exception):
    """Exception raised when development routing violates CORE-019."""

    pass


# Public API
def route_development(dev_type: DevelopmentType, context: dict) -> Tuple[bool, str]:
    """
    Route a development activity (returns routing decision and command).

    Args:
        dev_type: Type of development
        context: Development context

    Returns:
        Tuple of (should_use_tdd_master: bool, command: str)
    """
    router = DevelopmentRouter()
    should_route, reason = router.should_route_to_tdd_master(dev_type)

    if should_route:
        command = router.get_tdd_master_command(dev_type, context)
        router.log_routing_decision(dev_type, context, True)
        return True, command
    else:
        router.log_routing_decision(dev_type, context, False)
        return False, reason


def validate_tdd_master_available() -> bool:
    """Check if TDD-Master is available."""
    router = DevelopmentRouter()
    return router.tdd_master_available
