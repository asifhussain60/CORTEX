"""
Resource Tracking and Leak Detection.

AC-INFRA-001-06: Provides comprehensive resource tracking,
automatic cleanup, and leak detection for connections, file
handles, locks, and other managed resources.
"""

from enum import Enum
from typing import Callable, Optional, Any, Dict, List, Set
from dataclasses import dataclass, field
import uuid
import time
import threading
import weakref
from datetime import datetime
import traceback


class ResourceType(Enum):
    """Types of tracked resources."""
    CONNECTION = "connection"
    FILE = "file"
    LOCK = "lock"
    MEMORY = "memory"
    NETWORK = "network"
    OTHER = "other"


@dataclass
class TrackedResource:
    """Information about a tracked resource."""
    id: str
    resource_type: ResourceType
    name: str
    created_at: float = field(default_factory=time.time)
    released_at: Optional[float] = None
    leak_timeout_seconds: float = 300.0  # 5 minutes default
    cleanup_func: Optional[Callable[[Any], None]] = None
    stack_trace: str = ""
    
    # Weak reference to actual resource
    _resource_ref: Optional[weakref.ref] = None
    
    def set_resource(self, resource: Any) -> None:
        """Set weak reference to resource."""
        try:
            self._resource_ref = weakref.ref(resource)
        except TypeError:
            # Some objects don't support weak references
            self._resource_ref = None
    
    def get_resource(self) -> Optional[Any]:
        """Get resource if still alive."""
        if self._resource_ref is None:
            return None
        return self._resource_ref()
    
    @property
    def is_alive(self) -> bool:
        """Check if resource is still alive."""
        return self.released_at is None
    
    @property
    def lifetime_seconds(self) -> float:
        """Get resource lifetime in seconds."""
        if self.released_at is not None:
            return self.released_at - self.created_at
        return time.time() - self.created_at
    
    @property
    def is_leaked(self) -> bool:
        """Check if resource appears to be leaked."""
        if not self.is_alive:
            return False
        return self.lifetime_seconds > self.leak_timeout_seconds


class ResourceLeakError(Exception):
    """Raised when resource leak is detected."""
    pass


class ResourceTracker:
    """
    Comprehensive resource tracking with leak detection.
    
    Tracks resources throughout their lifecycle, provides
    automatic cleanup, and detects potential leaks. Thread-safe
    for concurrent access.
    """
    
    def __init__(
        self,
        leak_detection_enabled: bool = True,
        leak_check_interval_seconds: float = 60.0,
    ):
        """
        Initialize resource tracker.
        
        Args:
            leak_detection_enabled: Whether to enable leak detection
            leak_check_interval_seconds: Interval for leak checks
        """
        self._resources: Dict[str, TrackedResource] = {}
        self._lock = threading.RLock()
        self._leak_detection_enabled = leak_detection_enabled
        self._leak_check_interval = leak_check_interval_seconds
        self._shutdown = threading.Event()  # Use Event for interruptible wait
        
        # Metrics
        self._total_created = 0
        self._total_released = 0
        self._leak_warnings: List[str] = []
        
        # Start leak detection thread
        if leak_detection_enabled:
            self._leak_detection_thread = threading.Thread(
                target=self._leak_detection_loop,
                daemon=True
            )
            self._leak_detection_thread.start()
    
    def register(
        self,
        resource: Any,
        resource_type: ResourceType,
        name: str,
        cleanup_func: Optional[Callable[[Any], None]] = None,
        leak_timeout_seconds: float = 300.0,
    ) -> str:
        """
        Register a resource for tracking.
        
        Args:
            resource: Resource to track
            resource_type: Type of resource
            name: Human-readable resource name
            cleanup_func: Optional cleanup function
            leak_timeout_seconds: Timeout before considering leaked
            
        Returns:
            Resource ID for later release
        """
        resource_id = str(uuid.uuid4())
        
        tracked = TrackedResource(
            id=resource_id,
            resource_type=resource_type,
            name=name,
            cleanup_func=cleanup_func,
            leak_timeout_seconds=leak_timeout_seconds,
            stack_trace=self._capture_stack_trace(),
        )
        tracked.set_resource(resource)
        
        with self._lock:
            self._resources[resource_id] = tracked
            self._total_created += 1
        
        return resource_id
    
    def release(self, resource_id: str) -> None:
        """
        Release a tracked resource.
        
        Args:
            resource_id: ID of resource to release
        """
        with self._lock:
            tracked = self._resources.get(resource_id)
            if tracked is None or not tracked.is_alive:
                return  # Already released or invalid
            
            # Call cleanup function
            if tracked.cleanup_func is not None:
                resource = tracked.get_resource()
                if resource is not None:
                    try:
                        tracked.cleanup_func(resource)
                    except Exception as e:
                        # Log error but don't fail
                        pass
            
            # Mark as released
            tracked.released_at = time.time()
            self._total_released += 1
    
    def track(
        self,
        resource: Any,
        resource_type: ResourceType,
        name: str,
        cleanup_func: Optional[Callable[[Any], None]] = None,
    ) -> "ResourceContext":
        """
        Track resource with context manager.
        
        Args:
            resource: Resource to track
            resource_type: Type of resource
            name: Human-readable resource name
            cleanup_func: Optional cleanup function
            
        Returns:
            Context manager for automatic cleanup
        """
        return ResourceContext(self, resource, resource_type, name, cleanup_func)
    
    def get_active_count(self, resource_type: Optional[ResourceType] = None) -> int:
        """
        Get count of active resources.
        
        Args:
            resource_type: Optional filter by type
            
        Returns:
            Count of active resources
        """
        with self._lock:
            if resource_type is None:
                return sum(1 for r in self._resources.values() if r.is_alive)
            return sum(
                1 for r in self._resources.values()
                if r.is_alive and r.resource_type == resource_type
            )
    
    def get_total_active_count(self) -> int:
        """Get total count of all active resources."""
        return self.get_active_count()
    
    def get_leaked_resources(self) -> List[TrackedResource]:
        """
        Get list of potentially leaked resources.
        
        Returns:
            List of leaked resources
        """
        with self._lock:
            return [r for r in self._resources.values() if r.is_leaked]
    
    def get_leak_warnings(self) -> List[str]:
        """
        Get list of leak warnings.
        
        Returns:
            List of warning messages
        """
        with self._lock:
            return list(self._leak_warnings)
    
    def get_resource_info(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific resource.
        
        Args:
            resource_id: ID of resource
            
        Returns:
            Resource information or None if not found
        """
        with self._lock:
            tracked = self._resources.get(resource_id)
            if tracked is None:
                return None
            
            return {
                "id": tracked.id,
                "type": tracked.resource_type.value,
                "name": tracked.name,
                "created_at": tracked.created_at,
                "released_at": tracked.released_at,
                "lifetime_seconds": tracked.lifetime_seconds,
                "is_alive": tracked.is_alive,
                "is_leaked": tracked.is_leaked,
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get resource tracking metrics.
        
        Returns:
            Metrics including counts by type
        """
        with self._lock:
            active_by_type = {}
            for resource_type in ResourceType:
                count = sum(
                    1 for r in self._resources.values()
                    if r.is_alive and r.resource_type == resource_type
                )
                if count > 0:
                    active_by_type[resource_type.value] = count
            
            return {
                "total_created": self._total_created,
                "total_released": self._total_released,
                "total_active": self.get_total_active_count(),
                "active_by_type": active_by_type,
                "total_leaked": len(self.get_leaked_resources()),
                "leak_warnings_count": len(self._leak_warnings),
            }
    
    def shutdown(self) -> None:
        """Shutdown tracker and force cleanup of all resources."""
        self._shutdown.set()  # Signal thread to stop
        
        # Wait for leak detection thread to finish
        if hasattr(self, '_leak_detection_thread') and self._leak_detection_thread.is_alive():
            self._leak_detection_thread.join(timeout=1.0)
        
        with self._lock:
            # Release all active resources
            active_ids = [
                r.id for r in self._resources.values()
                if r.is_alive
            ]
            
            for resource_id in active_ids:
                self.release(resource_id)
    
    def _leak_detection_loop(self) -> None:
        """Background thread for leak detection."""
        while not self._shutdown.wait(timeout=self._leak_check_interval):
            self._check_for_leaks()
    
    def _check_for_leaks(self) -> None:
        """Check for leaked resources and issue warnings."""
        leaked = self.get_leaked_resources()
        
        for resource in leaked:
            warning = (
                f"Resource leak detected: {resource.name} "
                f"({resource.resource_type.value}) "
                f"alive for {resource.lifetime_seconds:.1f}s"
            )
            
            with self._lock:
                if warning not in self._leak_warnings:
                    self._leak_warnings.append(warning)
    
    def _capture_stack_trace(self) -> str:
        """Capture current stack trace for debugging."""
        return "".join(traceback.format_stack()[:-1])


class ResourceContext:
    """Context manager for automatic resource cleanup."""
    
    def __init__(
        self,
        tracker: ResourceTracker,
        resource: Any,
        resource_type: ResourceType,
        name: str,
        cleanup_func: Optional[Callable[[Any], None]] = None,
    ):
        """
        Initialize resource context.
        
        Args:
            tracker: Resource tracker
            resource: Resource to track
            resource_type: Type of resource
            name: Human-readable resource name
            cleanup_func: Optional cleanup function
        """
        self._tracker = tracker
        self._resource = resource
        self._resource_type = resource_type
        self._name = name
        self._cleanup_func = cleanup_func
        self._resource_id: Optional[str] = None
    
    def __enter__(self) -> Any:
        """Enter context and register resource."""
        self._resource_id = self._tracker.register(
            resource=self._resource,
            resource_type=self._resource_type,
            name=self._name,
            cleanup_func=self._cleanup_func,
        )
        return self._resource
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and release resource."""
        if self._resource_id is not None:
            self._tracker.release(self._resource_id)
