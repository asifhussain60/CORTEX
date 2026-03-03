"""
GracefulDegradationFramework — component fallback orchestration.

Phase 103-f: extracted from resilience.py (1,876L) god-object.
"""
from __future__ import annotations

import logging
from datetime import datetime
from threading import RLock
from typing import Any, Callable, Dict, List, Optional, Tuple

from cortex.intelligence.memory.tier2_adaptive.resilience.models import (
    ComponentFailure,
)

logger = logging.getLogger(__name__)


class GracefulDegradationFramework:
    """
    Orchestrates graceful degradation when components fail.

    Manages fallback strategies and partial functionality modes
    to enable system continuation with reduced functionality.
    """

    def __init__(self) -> None:
        """Initialize framework with empty component registry."""
        self._components: Dict[str, Dict[str, Any]] = {}
        self._component_states: Dict[str, Dict[str, Any]] = {}
        self._lock: RLock = RLock()
        logger.info("GracefulDegradationFramework initialized")

    def register_component(
        self,
        name: str,
        primary_strategy: Callable[..., Any],
        fallback_strategies: List[Callable[..., Any]],
    ) -> None:
        """Register a component with fallback strategies."""
        with self._lock:
            if name in self._components:
                raise ValueError(f"Component '{name}' already registered")
            self._components[name] = {
                "primary": primary_strategy,
                "fallbacks": fallback_strategies,
            }
            self._component_states[name] = {
                "current_mode": "primary",
                "is_degraded": False,
                "failure_count": 0,
                "last_failure": None,
                "last_failure_reason": None,
                "registered_at": datetime.utcnow(),
            }
            logger.info(
                f"Component registered: {name} (primary + {len(fallback_strategies)} fallbacks)"
            )

    def execute_with_degradation(
        self,
        component_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, str]:
        """Execute component with automatic fallback on failure."""
        with self._lock:
            if component_name not in self._components:
                raise ValueError(f"Component '{component_name}' not registered")
            component = self._components[component_name]
            state = self._component_states[component_name]

        primary_exc: Optional[Exception] = None
        try:
            result: Any = component["primary"](*args, **kwargs)
            with self._lock:
                state["current_mode"] = "primary"
                state["is_degraded"] = False
                state["failure_count"] = 0
            logger.debug(f"Component '{component_name}' executed in primary mode")
            return result, "primary"
        except Exception as exc:
            primary_exc = exc
            logger.warning(f"Component '{component_name}' primary strategy failed: {exc}")
            with self._lock:
                state["failure_count"] += 1
                state["last_failure"] = datetime.utcnow()
                state["last_failure_reason"] = str(exc)

        fallbacks: List[Callable[..., Any]] = component["fallbacks"]
        last_exception: Optional[Exception] = primary_exc

        for fallback_index, fallback in enumerate(fallbacks, start=1):
            try:
                result = fallback(*args, **kwargs)
                with self._lock:
                    state["current_mode"] = f"fallback_{fallback_index}"
                    state["is_degraded"] = True
                logger.info(f"Component '{component_name}' using fallback_{fallback_index}")
                return result, f"fallback_{fallback_index}"
            except Exception as fallback_exc:
                logger.warning(
                    f"Component '{component_name}' fallback_{fallback_index} failed: {fallback_exc}"
                )
                last_exception = fallback_exc

        with self._lock:
            state["current_mode"] = "degraded"
            state["is_degraded"] = True

        raise ComponentFailure(
            component_name=component_name,
            reason="All fallback strategies exhausted",
            strategies_tried=len(fallbacks) + 1,
            last_exception=last_exception,
        )

    def is_degraded(self, component_name: str) -> bool:
        """Check if component is currently in degraded mode."""
        with self._lock:
            if component_name not in self._component_states:
                return False
            return self._component_states[component_name]["is_degraded"]

    def get_degradation_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered components."""
        with self._lock:
            return {
                name: {
                    "current_mode": state["current_mode"],
                    "is_degraded": state["is_degraded"],
                    "failure_count": state["failure_count"],
                    "last_failure": state["last_failure"],
                    "last_failure_reason": state["last_failure_reason"],
                }
                for name, state in self._component_states.items()
            }
