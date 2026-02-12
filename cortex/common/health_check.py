"""
cortex/common/health_check.py

Unified health check base class and utilities.

AC-REM-002-03: Consolidates health check implementations across codebase.
"""

import functools
import logging
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

T = TypeVar('T')


class HealthChecker(ABC):
    """Base class for component health checks.

    Provides a standardized interface for health verification
    across all system components.

    Example:
        class MyServiceChecker(HealthChecker):
            def validate(self) -> bool:
                return self._check_connection()

        checker = MyServiceChecker("my_service")
        if checker.is_healthy():
            print("Service is healthy")
    """

    def __init__(self, component_name: str) -> None:
        """Initialize health checker.

        Args:
            component_name: Name of the component being checked
        """
        self.component_name = component_name
        self.last_error: Optional[str] = None
        self._last_check_result: Optional[bool] = None

    @abstractmethod
    def validate(self) -> bool:
        """Perform health validation.

        Returns:
            True if component is healthy, False otherwise
        """
        pass

    def is_healthy(self) -> bool:
        """Check if component is healthy.

        Wrapper around validate() that caches result.

        Returns:
            True if healthy, False otherwise
        """
        try:
            self._last_check_result = self.validate()
            if not self._last_check_result and not self.last_error:
                self.last_error = "Validation returned False"
            return self._last_check_result
        except Exception as e:
            self.last_error = str(e)
            self._last_check_result = False
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get component health status as dict.

        Returns:
            Dict with component name, health status, and error if any
        """
        if self._last_check_result is None:
            self.is_healthy()

        status: Dict[str, Any] = {
            "component": self.component_name,
            "healthy": self._last_check_result,
        }

        if self.last_error:
            status["error"] = self.last_error

        return status


class DatabaseHealthCheck(HealthChecker):
    """Health check for SQLite database connectivity.

    Verifies database is accessible and responsive.
    """

    def __init__(
        self,
        database_path: Union[str, Path],
        timeout: float = 5.0,
    ) -> None:
        """Initialize database health check.

        Args:
            database_path: Path to SQLite database
            timeout: Connection timeout in seconds
        """
        super().__init__("database")
        self.database_path = database_path
        self.timeout = timeout

    def validate(self) -> bool:
        """Validate database connectivity.

        Returns:
            True if database is accessible
        """
        try:
            conn = sqlite3.connect(
                str(self.database_path),
                timeout=self.timeout,
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True
        except sqlite3.Error as e:
            self.last_error = f"Database error: {e}"
            return False
        except Exception as e:
            self.last_error = f"Unexpected error: {e}"
            return False


class CompositeHealthCheck:
    """Combines multiple health checkers.

    Runs all checks and reports overall system health.

    Example:
        composite = CompositeHealthCheck([
            DatabaseHealthCheck("db.sqlite"),
            ServiceHealthCheck("api"),
        ])

        if composite.is_healthy():
            print("All systems operational")
    """

    def __init__(self, checkers: List[HealthChecker]) -> None:
        """Initialize composite health check.

        Args:
            checkers: List of health checkers to combine
        """
        self.checkers = checkers

    def is_healthy(self) -> bool:
        """Check if all components are healthy.

        Returns:
            True if all checks pass, False if any fails
        """
        return all(checker.is_healthy() for checker in self.checkers)

    def get_all_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all components.

        Returns:
            List of status dicts from all checkers
        """
        return [checker.get_status() for checker in self.checkers]

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all health checks.

        Returns:
            Dict with overall health and individual component statuses
        """
        statuses = self.get_all_statuses()
        healthy_count = sum(1 for s in statuses if s["healthy"])

        return {
            "overall_healthy": healthy_count == len(statuses),
            "healthy_count": healthy_count,
            "total_count": len(statuses),
            "components": statuses,
        }


def health_check(
    component_name: str,
    log_failures: bool = True,
) -> Callable[[Callable[..., bool]], Callable[..., bool]]:
    """Decorator to convert function to health check.

    Wraps a function that returns bool, catching exceptions
    and optionally logging failures.

    Args:
        component_name: Name of the component being checked
        log_failures: If True, log failures

    Returns:
        Decorated function

    Example:
        @health_check("my_service")
        def check_service():
            response = requests.get("http://service/health")
            return response.status_code == 200
    """
    def decorator(func: Callable[..., bool]) -> Callable[..., bool]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> bool:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_failures:
                    logging.error(
                        f"Health check failed for {component_name}: {e}"
                    )
                return False
        return wrapper
    return decorator
