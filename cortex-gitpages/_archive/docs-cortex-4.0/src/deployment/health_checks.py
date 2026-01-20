"""Health Checks & Readiness Validation System"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Callable


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    status: HealthStatus
    message: str
    response_time_ms: float


class HealthChecker:
    def __init__(self):
        self.checks: List = []
    
    def add_check(self, name: str, check_fn: Callable) -> None:
        self.checks.append((name, check_fn))
    
    def perform_checks(self) -> HealthCheckResult:
        all_healthy = all(check_fn() for _, check_fn in self.checks)
        status = HealthStatus.HEALTHY if all_healthy else HealthStatus.UNHEALTHY
        return HealthCheckResult(status, "OK" if all_healthy else "Failed", 1.0)
    
    def get_check_count(self) -> int:
        return len(self.checks)


class ReadinessProbe:
    def __init__(self):
        self.initialized = False
        self.dependencies_ready = False
    
    def init(self) -> bool:
        self.initialized = True
        return True
    
    def check_dependencies(self) -> bool:
        self.dependencies_ready = True
        return True
    
    def is_ready(self) -> bool:
        return self.initialized and self.dependencies_ready


class LoadBalancerIntegration:
    def __init__(self):
        self.health_checker = HealthChecker()
        self.readiness_probe = ReadinessProbe()
    
    def register_instance(self) -> bool:
        self.readiness_probe.init()
        self.readiness_probe.check_dependencies()
        return self.readiness_probe.is_ready()
    
    def deregister_instance(self) -> bool:
        return True
    
    def sync_health_status(self) -> HealthStatus:
        result = self.health_checker.perform_checks()
        return result.status
