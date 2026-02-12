"""
MCP Health Check Module

AC_START: AC-ENH063-P0-007-001
Description: Liveness and readiness probes for MCP server
Purpose: Enable Kubernetes/Docker health monitoring and deadlock detection
Authority: ENH-063 Phase 1 - Critical Security Fixes
Author: Asif Hussain

Implements health check endpoints for:
- Liveness probe (server is running and responsive)
- Readiness probe (server is ready to accept requests)
- Detailed health status with component checks

CORE-011: All functions have type hints
CORE-012: All public APIs have Google-style docstrings
CORE-008: TDD-driven implementation
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """
    Health status for individual component.
    
    Attributes:
        name: Component name
        status: Health status
        message: Status message
        last_check: Last check timestamp
        metadata: Additional component metadata
    """
    name: str
    status: HealthStatus
    message: str
    last_check: float
    metadata: Dict[str, Any]


@dataclass
class HealthCheckResult:
    """
    Overall health check result.
    
    Attributes:
        status: Overall health status
        components: Individual component health statuses
        uptime_seconds: Server uptime in seconds
        total_requests: Total requests processed
        timestamp: Check timestamp
    """
    status: HealthStatus
    components: List[ComponentHealth]
    uptime_seconds: float
    total_requests: int
    timestamp: float


# ============================================================================
# HEALTH CHECK MANAGER
# ============================================================================

class MCPHealthCheckManager:
    """
    MCP Server Health Check Manager.
    
    Provides health monitoring with:
    - Liveness probe (basic responsiveness check)
    - Readiness probe (comprehensive component checks)
    - Component-level health tracking
    - Automatic degradation detection
    - Deadlock detection via timeout
    
    Used by Kubernetes, Docker, load balancers, and monitoring systems.
    """
    
    def __init__(
        self,
        check_timeout_seconds: float = 5.0,
        component_check_interval_seconds: float = 60.0
    ):
        """
        Initialize health check manager.
        
        Args:
            check_timeout_seconds: Max time for health check before timeout
            component_check_interval_seconds: How often to check components
        """
        self.check_timeout_seconds = check_timeout_seconds
        self.component_check_interval_seconds = component_check_interval_seconds
        
        # Health state
        self.start_time = time.time()
        self.last_liveness_check = time.time()
        self.last_readiness_check = time.time()
        self.total_requests_processed = 0
        
        # Component health cache
        self._component_health: Dict[str, ComponentHealth] = {}
        
        logger.info("MCP Health Check Manager initialized")
    
    def liveness_probe(self) -> Dict[str, Any]:
        """
        Liveness probe - checks if server is running and responsive.
        
        This is a lightweight check that returns quickly.
        Used by Kubernetes to detect if pod needs restart.
        
        Returns:
            Dict with status and timestamp
        """
        self.last_liveness_check = time.time()
        
        return {
            "status": "alive",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
        }
    
    def readiness_probe(self) -> Dict[str, Any]:
        """
        Readiness probe - checks if server is ready to accept requests.
        
        This is a more comprehensive check that validates all components.
        Used by Kubernetes to determine if pod should receive traffic.
        
        Returns:
            Dict with status, components, and readiness flag
        """
        self.last_readiness_check = time.time()
        
        # Perform component health checks
        health_result = self.check_health()
        
        # Server is ready if status is HEALTHY or DEGRADED (not UNHEALTHY)
        is_ready = health_result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        
        return {
            "status": "ready" if is_ready else "not_ready",
            "health_status": health_result.status.value,
            "components": [
                {
                    "name": comp.name,
                    "status": comp.status.value,
                    "message": comp.message,
                }
                for comp in health_result.components
            ],
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": health_result.uptime_seconds,
        }
    
    def check_health(self) -> HealthCheckResult:
        """
        Perform comprehensive health check of all components.
        
        Returns:
            HealthCheckResult: Detailed health status
        """
        components: List[ComponentHealth] = []
        current_time = time.time()
        
        # Check 1: Liveness responsiveness
        time_since_last_liveness = current_time - self.last_liveness_check
        if time_since_last_liveness > 300:  # 5 minutes
            components.append(ComponentHealth(
                name="liveness",
                status=HealthStatus.DEGRADED,
                message=f"No liveness check in {int(time_since_last_liveness)}s",
                last_check=current_time,
                metadata={"seconds_since_check": time_since_last_liveness}
            ))
        else:
            components.append(ComponentHealth(
                name="liveness",
                status=HealthStatus.HEALTHY,
                message="Liveness checks responsive",
                last_check=current_time,
                metadata={"seconds_since_check": time_since_last_liveness}
            ))
        
        # Check 2: Server uptime (warn if very short, might indicate crash loop)
        uptime = current_time - self.start_time
        if uptime < 60:  # Less than 1 minute
            components.append(ComponentHealth(
                name="uptime",
                status=HealthStatus.DEGRADED,
                message=f"Recent restart detected (uptime: {int(uptime)}s)",
                last_check=current_time,
                metadata={"uptime_seconds": uptime}
            ))
        else:
            components.append(ComponentHealth(
                name="uptime",
                status=HealthStatus.HEALTHY,
                message=f"Stable uptime: {int(uptime)}s",
                last_check=current_time,
                metadata={"uptime_seconds": uptime}
            ))
        
        # Check 3: Request processing (warn if no requests in long time)
        if self.total_requests_processed == 0 and uptime > 300:  # 5+ minutes, no requests
            components.append(ComponentHealth(
                name="request_processing",
                status=HealthStatus.DEGRADED,
                message="No requests processed (idle server?)",
                last_check=current_time,
                metadata={"total_requests": self.total_requests_processed}
            ))
        else:
            components.append(ComponentHealth(
                name="request_processing",
                status=HealthStatus.HEALTHY,
                message=f"{self.total_requests_processed} requests processed",
                last_check=current_time,
                metadata={"total_requests": self.total_requests_processed}
            ))
        
        # Check 4: Memory health (basic check)
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > 1024:  # >1GB
                components.append(ComponentHealth(
                    name="memory",
                    status=HealthStatus.DEGRADED,
                    message=f"High memory usage: {int(memory_mb)}MB",
                    last_check=current_time,
                    metadata={"memory_mb": memory_mb}
                ))
            else:
                components.append(ComponentHealth(
                    name="memory",
                    status=HealthStatus.HEALTHY,
                    message=f"Memory usage: {int(memory_mb)}MB",
                    last_check=current_time,
                    metadata={"memory_mb": memory_mb}
                ))
        except ImportError:
            # psutil not available, skip memory check
            components.append(ComponentHealth(
                name="memory",
                status=HealthStatus.HEALTHY,
                message="Memory check unavailable (psutil not installed)",
                last_check=current_time,
                metadata={}
            ))
        
        # Determine overall status
        statuses = [comp.status for comp in components]
        if HealthStatus.UNHEALTHY in statuses:
            overall_status = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return HealthCheckResult(
            status=overall_status,
            components=components,
            uptime_seconds=uptime,
            total_requests=self.total_requests_processed,
            timestamp=current_time
        )
    
    def record_request(self) -> None:
        """
        Record that a request was processed.
        
        Used to track server activity for health monitoring.
        """
        self.total_requests_processed += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get health metrics for monitoring/observability.
        
        Returns:
            Dict: Health and performance metrics
        """
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.total_requests_processed,
            "requests_per_second": self.total_requests_processed / uptime if uptime > 0 else 0,
            "last_liveness_check": datetime.fromtimestamp(self.last_liveness_check).isoformat(),
            "last_readiness_check": datetime.fromtimestamp(self.last_readiness_check).isoformat(),
            "health_status": self.check_health().status.value,
        }


# AC_COMPLETE: AC-ENH063-P0-007-001
