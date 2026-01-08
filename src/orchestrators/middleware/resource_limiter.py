"""
Resource Limiter Middleware - CORTEX 6.0

Implements resource limits and quotas for orchestrator operations.

Author: CORTEX Autonomous Executor
Feature: feat05-resilience Phase 1
Correlation ID: FEAT05-P1-T1.1
"""

import time
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
from contextlib import contextmanager

from src.orchestrators.audit_logger import AuditLogger, AuditLevel, AuditCategory


class ResourceType(Enum):
    """Types of resources that can be limited."""
    MEMORY = "memory"
    CPU = "cpu"
    CONCURRENT_OPERATIONS = "concurrent_operations"
    FILE_HANDLES = "file_handles"


@dataclass
class ResourceQuota:
    """Resource quota configuration."""
    resource_type: ResourceType
    limit: int
    current: int = 0
    hard_limit: bool = True  # If True, reject when limit reached; if False, warn only


class ResourceLimiter:
    """
    Manages resource limits and quotas for CORTEX operations.
    
    Features:
    - Per-resource-type quotas
    - Hard and soft limits
    - Automatic resource tracking
    - Audit logging integration
    """
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        """Initialize resource limiter."""
        self.audit_logger = audit_logger or AuditLogger()
        self._quotas: Dict[ResourceType, ResourceQuota] = {}
        self._lock = threading.RLock()
        
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.MIDDLEWARE,
            component="resource_limiter",
            operation="initialize",
            correlation_id="FEAT05-P1-T1.1",
            context={"status": "initialized"}
        )
    
    def set_quota(self, resource_type: ResourceType, limit: int, hard_limit: bool = True):
        """Set resource quota."""
        with self._lock:
            self._quotas[resource_type] = ResourceQuota(
                resource_type=resource_type,
                limit=limit,
                hard_limit=hard_limit
            )
            
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.MIDDLEWARE,
                component="resource_limiter",
                operation="set_quota",
                correlation_id="FEAT05-P1-T1.1",
                context={
                    "resource_type": resource_type.value,
                    "limit": limit,
                    "hard_limit": hard_limit
                }
            )
    
    def acquire_resource(self, resource_type: ResourceType, amount: int = 1) -> bool:
        """
        Acquire resource.
        
        Returns:
            True if resource acquired, False if limit reached (for hard limits)
        """
        with self._lock:
            if resource_type not in self._quotas:
                return True  # No quota set, allow
            
            quota = self._quotas[resource_type]
            new_usage = quota.current + amount
            
            if new_usage > quota.limit:
                if quota.hard_limit:
                    self.audit_logger.log(
                        level=AuditLevel.WARNING,
                        category=AuditCategory.MIDDLEWARE,
                        component="resource_limiter",
                        operation="acquire_resource_rejected",
                        correlation_id="FEAT05-P1-T1.1",
                        context={
                            "resource_type": resource_type.value,
                            "requested": amount,
                            "current": quota.current,
                            "limit": quota.limit
                        }
                    )
                    return False
                else:
                    # Soft limit - allow but warn
                    self.audit_logger.log(
                        level=AuditLevel.WARNING,
                        category=AuditCategory.MIDDLEWARE,
                        component="resource_limiter",
                        operation="acquire_resource_over_soft_limit",
                        correlation_id="FEAT05-P1-T1.1",
                        context={
                            "resource_type": resource_type.value,
                            "requested": amount,
                            "current": quota.current,
                            "limit": quota.limit
                        }
                    )
            
            quota.current = new_usage
            return True
    
    def release_resource(self, resource_type: ResourceType, amount: int = 1):
        """Release resource."""
        with self._lock:
            if resource_type not in self._quotas:
                return
            
            quota = self._quotas[resource_type]
            quota.current = max(0, quota.current - amount)
    
    @contextmanager
    def resource_scope(self, resource_type: ResourceType, amount: int = 1):
        """Context manager for resource acquisition/release."""
        acquired = self.acquire_resource(resource_type, amount)
        if not acquired:
            raise ResourceLimitExceeded(
                f"Resource limit exceeded for {resource_type.value}"
            )
        
        try:
            yield
        finally:
            self.release_resource(resource_type, amount)
    
    def get_usage(self, resource_type: ResourceType) -> Dict[str, int]:
        """Get current resource usage."""
        with self._lock:
            if resource_type not in self._quotas:
                return {"current": 0, "limit": 0, "available": 0}
            
            quota = self._quotas[resource_type]
            return {
                "current": quota.current,
                "limit": quota.limit,
                "available": quota.limit - quota.current
            }
    
    def reset_quota(self, resource_type: ResourceType):
        """Reset resource quota to zero usage."""
        with self._lock:
            if resource_type in self._quotas:
                self._quotas[resource_type].current = 0


class ResourceLimitExceeded(Exception):
    """Raised when a hard resource limit is exceeded."""
    pass
