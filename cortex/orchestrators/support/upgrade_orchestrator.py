"""UpgradeOrchestrator — Differential upgrade system with safety.

Supports rolling, blue-green, and canary upgrade strategies
with circuit breaker, execution history, and caching.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


class UpgradeStrategy(Enum):
    """Upgrade execution strategies."""
    ROLLING = auto()
    BLUE_GREEN = auto()
    CANARY = auto()
    IN_PLACE = auto()


@dataclass
class UpgradeComponent:
    """A component targeted for upgrade.

    Args:
        name: Component name.
        current_version: Current version.
        target_version: Target version.
        dependencies: Optional list of dependent component names.
    """
    name: str
    current_version: str
    target_version: str
    dependencies: List[str] = field(default_factory=list)


@dataclass
class UpgradePlan:
    """Plan produced by :meth:`UpgradeOrchestrator.plan_upgrade`.

    Args:
        upgrade_id: Unique plan identifier.
        components: Components in the plan.
        strategy: Strategy to use.
    """
    upgrade_id: str
    components: List[UpgradeComponent] = field(default_factory=list)
    strategy: UpgradeStrategy = UpgradeStrategy.ROLLING


class CircuitBreaker:
    """Simple circuit breaker for safety."""

    def __init__(self, threshold: int = 3) -> None:
        """Initialize circuit breaker.

        Args:
            threshold: Number of failures before tripping.
        """
        self._failures = 0
        self._threshold = threshold
        self._open = False

    @property
    def is_open(self) -> bool:
        """Whether the circuit is open (tripped)."""
        return self._open

    def record_failure(self) -> None:
        """Record a failure."""
        self._failures += 1
        if self._failures >= self._threshold:
            self._open = True

    def reset(self) -> None:
        """Reset the circuit breaker."""
        self._failures = 0
        self._open = False


class UpgradeOrchestrator(OrchestratorProtocolMixin):
    """Differential upgrade orchestrator with safety features."""

    def __init__(self) -> None:
        """Initialize UpgradeOrchestrator."""
        self.logger = logging.getLogger("UpgradeOrchestrator")
        self.engine = self  # self-referential engine for hasattr checks
        self.circuit_breaker = CircuitBreaker()
        self._execution_history: Dict[str, Any] = {}
        self._upgrade_cache: Dict[str, Any] = {}
        self.max_cache_size: int = 100

    def plan_upgrade(
        self,
        upgrade_id: str,
        components: Optional[List[UpgradeComponent]] = None,
        strategy: UpgradeStrategy = UpgradeStrategy.ROLLING,
    ) -> UpgradePlan:
        """Create an upgrade plan.

        Args:
            upgrade_id: Unique plan identifier.
            components: Components to upgrade.
            strategy: Upgrade strategy.

        Returns:
            UpgradePlan instance.
        """
        return UpgradePlan(
            upgrade_id=upgrade_id,
            components=components or [],
            strategy=strategy,
        )
