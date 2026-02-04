"""
Health Check Integration System - Phase 9

Provides comprehensive health verification for orchestrators:
- Individual orchestrator health checks
- Dependency chain validation
- System-wide health status
- Recovery recommendations
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Coroutine
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# HEALTH STATUS MODELS
# ============================================================================

class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a single health check"""
    orchestrator_name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    checks_performed: List[str]
    error: Optional[str] = None
    recovery_suggestions: List[str] = None

    def __post_init__(self):
        if self.recovery_suggestions is None:
            self.recovery_suggestions = []


@dataclass
class SystemHealthReport:
    """Complete system health status"""
    timestamp: datetime
    overall_status: HealthStatus
    orchestrator_results: Dict[str, HealthCheckResult]
    dependency_validation_passed: bool
    event_bus_status: HealthStatus
    total_orchestrators: int
    healthy_orchestrators: int
    degraded_orchestrators: int
    unhealthy_orchestrators: int

    def __post_init__(self):
        self.healthy_orchestrators = sum(
            1 for r in self.orchestrator_results.values()
            if r.status == HealthStatus.HEALTHY
        )
        self.degraded_orchestrators = sum(
            1 for r in self.orchestrator_results.values()
            if r.status == HealthStatus.DEGRADED
        )
        self.unhealthy_orchestrators = sum(
            1 for r in self.orchestrator_results.values()
            if r.status == HealthStatus.UNHEALTHY
        )


# ============================================================================
# HEALTH CHECK EXECUTOR
# ============================================================================

class HealthCheckExecutor:
    """
    Executes health checks on orchestrators.
    Supports both sync and async health check methods.
    """

    @staticmethod
    def execute_health_check(orchestrator: Any, timeout_seconds: int = 5) -> HealthCheckResult:
        """
        Execute health check on single orchestrator.
        Returns: HealthCheckResult with status and details
        """
        orch_name = orchestrator.__class__.__name__
        checks_performed = []
        error = None

        try:
            # Check 1: Has health_check method
            if not hasattr(orchestrator, 'health_check'):
                return HealthCheckResult(
                    orchestrator_name=orch_name,
                    status=HealthStatus.UNKNOWN,
                    message="No health_check method defined",
                    timestamp=datetime.now(),
                    checks_performed=['method_existence'],
                    recovery_suggestions=["Implement health_check() method on orchestrator"]
                )

            checks_performed.append('method_existence')

            # Check 2: Execute health_check
            health_check_method = getattr(orchestrator, 'health_check')
            result = None

            try:
                result = health_check_method()
                checks_performed.append('health_check_execution')
            except Exception as e:
                error = str(e)
                logger.warning(f"⚠️ Health check failed for {orch_name}: {e}")
                return HealthCheckResult(
                    orchestrator_name=orch_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check raised exception",
                    timestamp=datetime.now(),
                    checks_performed=checks_performed,
                    error=error,
                    recovery_suggestions=["Check orchestrator logs for details", "Restart orchestrator"]
                )

            # Check 3: Validate result
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                checks_performed.append('result_validation')
            elif isinstance(result, dict):
                status_key = result.get('status', 'unknown').lower()
                status = HealthStatus(status_key) if status_key in [s.value for s in HealthStatus] else HealthStatus.UNKNOWN
                checks_performed.append('result_validation')
            else:
                status = HealthStatus.DEGRADED
                error = f"Unexpected health_check return type: {type(result)}"

            message = result.get('message', 'OK') if isinstance(result, dict) else 'Healthy'

            return HealthCheckResult(
                orchestrator_name=orch_name,
                status=status,
                message=message,
                timestamp=datetime.now(),
                checks_performed=checks_performed,
                error=error
            )

        except Exception as e:
            logger.error(f"❌ Unexpected error during health check for {orch_name}: {e}")
            return HealthCheckResult(
                orchestrator_name=orch_name,
                status=HealthStatus.UNKNOWN,
                message="Unexpected error during health check",
                timestamp=datetime.now(),
                checks_performed=checks_performed,
                error=str(e),
                recovery_suggestions=["Check system logs", "Investigate orchestrator state"]
            )


# ============================================================================
# SYSTEM HEALTH MONITOR
# ============================================================================

class SystemHealthMonitor:
    """
    Monitors overall system health by checking all orchestrators.
    Provides:
    - Parallel health checking
    - Dependency validation
    - Event bus health
    - Comprehensive health report
    """

    def __init__(self, orchestrators: Dict[str, Any], event_bus: Any = None):
        self.orchestrators = orchestrators
        self.event_bus = event_bus
        self.last_report: Optional[SystemHealthReport] = None

    def check_all_orchestrators(self, parallel: bool = True) -> Dict[str, HealthCheckResult]:
        """
        Check health of all orchestrators.
        Args:
            parallel: If True, run checks in parallel; if False, run sequentially
        Returns:
            Dict of {orchestrator_name: HealthCheckResult}
        """
        results = {}

        if parallel:
            # Parallel execution (use asyncio if available)
            results = self._check_orchestrators_parallel()
        else:
            # Sequential execution
            results = self._check_orchestrators_sequential()

        return results

    def _check_orchestrators_sequential(self) -> Dict[str, HealthCheckResult]:
        """Check orchestrators sequentially"""
        results = {}
        for orch_name, instance in self.orchestrators.items():
            result = HealthCheckExecutor.execute_health_check(instance)
            results[orch_name] = result
            status_icon = "✅" if result.status == HealthStatus.HEALTHY else "⚠️" if result.status == HealthStatus.DEGRADED else "❌"
            logger.info(f"{status_icon} {orch_name}: {result.status.value} - {result.message}")
        return results

    def _check_orchestrators_parallel(self) -> Dict[str, HealthCheckResult]:
        """Check orchestrators in parallel"""
        results = {}
        # For now, use sequential (parallel requires thread pool or async)
        # TODO: Implement with concurrent.futures or asyncio
        return self._check_orchestrators_sequential()

    def check_event_bus(self) -> HealthStatus:
        """Check event bus health"""
        if not self.event_bus:
            return HealthStatus.UNKNOWN

        try:
            if hasattr(self.event_bus, 'health_check'):
                result = self.event_bus.health_check()
                if isinstance(result, bool):
                    return HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                elif isinstance(result, dict):
                    status = result.get('status', 'unknown')
                    return HealthStatus(status.lower()) if status.lower() in [s.value for s in HealthStatus] else HealthStatus.UNKNOWN
            return HealthStatus.HEALTHY  # Assume healthy if no health_check
        except Exception as e:
            logger.warning(f"⚠️ Event bus health check failed: {e}")
            return HealthStatus.DEGRADED

    def validate_dependencies(self) -> bool:
        """
        Validate all orchestrator dependencies are healthy.
        Returns: True if all dependencies are healthy
        """
        # This would require tracking dependencies
        # For now, return True (TODO: implement full dependency validation)
        return True

    def generate_system_health_report(self) -> SystemHealthReport:
        """Generate comprehensive system health report"""
        # Check all orchestrators
        orch_results = self.check_all_orchestrators(parallel=False)

        # Check event bus
        event_bus_status = self.check_event_bus()

        # Validate dependencies
        deps_valid = self.validate_dependencies()

        # Determine overall status
        if all(r.status == HealthStatus.HEALTHY for r in orch_results.values()) and event_bus_status == HealthStatus.HEALTHY:
            overall_status = HealthStatus.HEALTHY
        elif any(r.status == HealthStatus.UNHEALTHY for r in orch_results.values()) or event_bus_status == HealthStatus.UNHEALTHY:
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED

        report = SystemHealthReport(
            timestamp=datetime.now(),
            overall_status=overall_status,
            orchestrator_results=orch_results,
            dependency_validation_passed=deps_valid,
            event_bus_status=event_bus_status,
            total_orchestrators=len(self.orchestrators),
            healthy_orchestrators=0,  # Set by __post_init__
            degraded_orchestrators=0,
            unhealthy_orchestrators=0,
        )

        self.last_report = report
        logger.info(f"✅ System health report: {overall_status.value} ({report.healthy_orchestrators}/{report.total_orchestrators} healthy)")
        return report

    def get_health_summary(self) -> str:
        """Get human-readable health summary"""
        if not self.last_report:
            return "No health report available"

        lines = [
            f"System Health Report",
            f"  Status: {self.last_report.overall_status.value.upper()}",
            f"  Timestamp: {self.last_report.timestamp}",
            f"  Orchestrators: {self.last_report.healthy_orchestrators}/{self.last_report.total_orchestrators} healthy",
            f"  Event Bus: {self.last_report.event_bus_status.value}",
        ]

        # List unhealthy orchestrators
        unhealthy = [r for r in self.last_report.orchestrator_results.values() if r.status != HealthStatus.HEALTHY]
        if unhealthy:
            lines.append("  Unhealthy Orchestrators:")
            for result in unhealthy:
                lines.append(f"    - {result.orchestrator_name}: {result.message}")
                for suggestion in result.recovery_suggestions:
                    lines.append(f"      → {suggestion}")

        return "\n".join(lines)
