"""Orphaned resource detection and automatic cleanup.

Detects and cleans up resources left in inconsistent state by failures:
dangling locks, incomplete operations, stale state.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
import logging
import threading
import time


logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    """Type of resource that can be orphaned."""
    LOCK = "LOCK"
    OPERATION = "OPERATION"
    STATE = "STATE"
    SESSION = "SESSION"


@dataclass
class OrphanedResource:
    """Record of potentially orphaned resource.
    
    Args:
        resource_id: Unique resource identifier
        resource_type: Type of resource
        created_at: When resource was created
        last_activity: Last activity timestamp
        metadata: Additional resource information
    """
    resource_id: str
    resource_type: ResourceType
    created_at: datetime
    last_activity: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_orphaned(
        self,
        lock_threshold_minutes: int = 10,
        operation_threshold_hours: int = 1,
        state_threshold_hours: int = 24
    ) -> bool:
        """Check if resource is orphaned based on inactivity.
        
        Args:
            lock_threshold_minutes: Lock timeout in minutes
            operation_threshold_hours: Operation timeout in hours
            state_threshold_hours: State timeout in hours
            
        Returns:
            True if resource is orphaned
        """
        now = datetime.utcnow()
        inactive_duration = now - self.last_activity
        
        if self.resource_type == ResourceType.LOCK:
            return inactive_duration > timedelta(minutes=lock_threshold_minutes)
        elif self.resource_type == ResourceType.OPERATION:
            return inactive_duration > timedelta(hours=operation_threshold_hours)
        elif self.resource_type == ResourceType.STATE:
            return inactive_duration > timedelta(hours=state_threshold_hours)
        else:
            return False


@dataclass
class CleanupStrategy:
    """Strategy for cleaning up specific resource type.
    
    Args:
        resource_type: Type of resource
        action: Cleanup action to perform
        description: Human-readable description
        verify_liveness: Whether to verify resource not active
    """
    resource_type: ResourceType
    action: str
    description: str
    verify_liveness: bool = True
    
    @classmethod
    def for_resource_type(cls, resource_type: ResourceType) -> "CleanupStrategy":
        """Get cleanup strategy for resource type.
        
        Args:
            resource_type: Resource type
            
        Returns:
            Cleanup strategy
        """
        strategies = {
            ResourceType.LOCK: cls(
                resource_type=ResourceType.LOCK,
                action="release_lock",
                description="Force release orphaned lock",
                verify_liveness=True
            ),
            ResourceType.OPERATION: cls(
                resource_type=ResourceType.OPERATION,
                action="mark_failed",
                description="Mark stuck operation as failed",
                verify_liveness=True
            ),
            ResourceType.STATE: cls(
                resource_type=ResourceType.STATE,
                action="reset_state",
                description="Reset inconsistent state",
                verify_liveness=False
            ),
        }
        return strategies[resource_type]


@dataclass
class CleanupResult:
    """Result of cleanup operation.
    
    Args:
        success: Whether cleanup succeeded
        resource_id: Resource that was cleaned
        message: Result message
        retry_count: Number of retries attempted
        timestamp: When cleanup was performed
    """
    success: bool
    resource_id: str
    message: str
    retry_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class CleanupError(Exception):
    """Raised when cleanup cannot be performed."""
    pass


class LockManager(Protocol):
    """Protocol for lock management."""
    
    def get_all_locks(self) -> List[Dict[str, Any]]:
        """Get all active locks."""
        ...
    
    def release_lock(self, lock_id: str, force: bool = False) -> None:
        """Release lock."""
        ...
    
    def is_lock_held(self, lock_id: str) -> bool:
        """Check if lock is held."""
        ...


class OperationTracker(Protocol):
    """Protocol for operation tracking."""
    
    def get_all_operations(self) -> List[Dict[str, Any]]:
        """Get all tracked operations."""
        ...
    
    def mark_operation_failed(self, operation_id: str, reason: str) -> None:
        """Mark operation as failed."""
        ...


class OrphanedResourceCleaner:
    """Detects and cleans up orphaned resources.
    
    Args:
        lock_manager: Lock management interface
        operation_tracker: Operation tracking interface
        scan_interval_seconds: How often to scan for orphans
        lock_threshold_minutes: Lock timeout threshold
        operation_threshold_hours: Operation timeout threshold
    """
    
    def __init__(
        self,
        lock_manager: LockManager,
        operation_tracker: OperationTracker,
        scan_interval_seconds: int = 300,
        lock_threshold_minutes: int = 10,
        operation_threshold_hours: int = 1
    ):
        self.lock_manager = lock_manager
        self.operation_tracker = operation_tracker
        self.scan_interval_seconds = scan_interval_seconds
        self.lock_threshold_minutes = lock_threshold_minutes
        self.operation_threshold_hours = operation_threshold_hours
        
        self._audit_trail: Dict[str, List[Dict[str, Any]]] = {}
        self._scan_thread: Optional[threading.Thread] = None
        self._stop_scan = threading.Event()
    
    def scan_for_orphans(self) -> List[OrphanedResource]:
        """Scan for orphaned resources.
        
        Returns:
            List of orphaned resources detected
        """
        orphans: List[OrphanedResource] = []
        
        # Scan locks
        try:
            locks = self.lock_manager.get_all_locks()
            for lock_data in locks:
                resource = self._parse_lock_resource(lock_data)
                if resource and resource.is_orphaned(
                    lock_threshold_minutes=self.lock_threshold_minutes
                ):
                    orphans.append(resource)
        except Exception as e:
            logger.error(f"Error scanning locks: {e}")
        
        # Scan operations
        try:
            operations = self.operation_tracker.get_all_operations()
            for op_data in operations:
                resource = self._parse_operation_resource(op_data)
                if resource and resource.is_orphaned(
                    operation_threshold_hours=self.operation_threshold_hours
                ):
                    orphans.append(resource)
        except Exception as e:
            logger.error(f"Error scanning operations: {e}")
        
        logger.info(f"Scan detected {len(orphans)} orphaned resources")
        return orphans
    
    def cleanup_resource(
        self,
        resource: OrphanedResource,
        retry_count: int = 0,
        cascade: bool = False
    ) -> CleanupResult:
        """Clean up orphaned resource.
        
        Args:
            resource: Resource to clean up
            retry_count: Current retry attempt
            cascade: Whether to clean up related resources
            
        Returns:
            Cleanup result
        """
        strategy = CleanupStrategy.for_resource_type(resource.resource_type)
        
        # Verify liveness before cleanup
        if strategy.verify_liveness:
            if self._is_resource_active(resource):
                msg = f"Resource {resource.resource_id} still active, skipping cleanup"
                logger.warning(msg)
                return CleanupResult(
                    success=False,
                    resource_id=resource.resource_id,
                    message=msg,
                    retry_count=retry_count
                )
        
        # Execute cleanup
        try:
            self._execute_cleanup(resource, strategy)
            
            # Cascade to related resources if requested
            if cascade:
                self._cascade_cleanup(resource)
            
            # Record audit
            self._record_audit(resource, strategy, success=True)
            
            msg = f"Successfully cleaned up {resource.resource_type} {resource.resource_id}"
            logger.info(msg)
            
            return CleanupResult(
                success=True,
                resource_id=resource.resource_id,
                message=msg,
                retry_count=retry_count
            )
        
        except Exception as e:
            msg = f"Cleanup failed for {resource.resource_id}: {e}"
            logger.error(msg)
            
            self._record_audit(resource, strategy, success=False, error=str(e))
            
            return CleanupResult(
                success=False,
                resource_id=resource.resource_id,
                message=msg,
                retry_count=retry_count
            )
    
    def force_cleanup(
        self,
        resource_id: str,
        resource_type: ResourceType,
        reason: str
    ) -> CleanupResult:
        """Force cleanup with operator override.
        
        Args:
            resource_id: Resource to clean up
            resource_type: Type of resource
            reason: Reason for forced cleanup
            
        Returns:
            Cleanup result
        """
        logger.warning(f"Forced cleanup of {resource_type} {resource_id}: {reason}")
        
        resource = OrphanedResource(
            resource_id=resource_id,
            resource_type=resource_type,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            metadata={"forced": True, "reason": reason}
        )
        
        strategy = CleanupStrategy.for_resource_type(resource_type)
        strategy.verify_liveness = False  # Skip liveness check for forced cleanup
        
        try:
            self._execute_cleanup(resource, strategy)
            
            msg = f"Forced cleanup successful: {reason}"
            self._record_audit(resource, strategy, success=True, forced=True, reason=reason)
            
            return CleanupResult(
                success=True,
                resource_id=resource_id,
                message=msg
            )
        except Exception as e:
            msg = f"Forced cleanup failed: {e}"
            self._record_audit(resource, strategy, success=False, error=str(e))
            
            return CleanupResult(
                success=False,
                resource_id=resource_id,
                message=msg
            )
    
    def get_audit_trail(self, resource_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for resource.
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            List of audit events
        """
        return self._audit_trail.get(resource_id, [])
    
    def start_automatic_scan(self) -> None:
        """Start automatic scanning thread."""
        if self._scan_thread and self._scan_thread.is_alive():
            logger.warning("Automatic scan already running")
            return
        
        self._stop_scan.clear()
        self._scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._scan_thread.start()
        logger.info("Started automatic orphan scanning")
    
    def stop_automatic_scan(self) -> None:
        """Stop automatic scanning thread."""
        if not self._scan_thread or not self._scan_thread.is_alive():
            return
        
        self._stop_scan.set()
        self._scan_thread.join(timeout=5)
        logger.info("Stopped automatic orphan scanning")
    
    def _parse_lock_resource(self, lock_data: Dict[str, Any]) -> Optional[OrphanedResource]:
        """Parse lock data into resource."""
        try:
            return OrphanedResource(
                resource_id=lock_data["lock_id"],
                resource_type=ResourceType.LOCK,
                created_at=datetime.fromisoformat(lock_data["acquired_at"]),
                last_activity=datetime.fromisoformat(lock_data["last_heartbeat"]),
                metadata={"owner": lock_data.get("owner")}
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing lock data: {e}")
            return None
    
    def _parse_operation_resource(self, op_data: Dict[str, Any]) -> Optional[OrphanedResource]:
        """Parse operation data into resource."""
        try:
            return OrphanedResource(
                resource_id=op_data["operation_id"],
                resource_type=ResourceType.OPERATION,
                created_at=datetime.fromisoformat(op_data["started_at"]),
                last_activity=datetime.fromisoformat(op_data["last_update"]),
                metadata={"status": op_data.get("status")}
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing operation data: {e}")
            return None
    
    def _is_resource_active(self, resource: OrphanedResource) -> bool:
        """Verify if resource is still active."""
        if resource.resource_type == ResourceType.LOCK:
            return self.lock_manager.is_lock_held(resource.resource_id)
        # Add other resource type checks as needed
        return False
    
    def _execute_cleanup(self, resource: OrphanedResource, strategy: CleanupStrategy) -> None:
        """Execute cleanup action for resource."""
        if resource.resource_type == ResourceType.LOCK:
            self.lock_manager.release_lock(resource.resource_id, force=True)
        elif resource.resource_type == ResourceType.OPERATION:
            inactive_hours = (datetime.utcnow() - resource.last_activity).total_seconds() / 3600
            reason = f"Orphaned: no activity for {inactive_hours:.1f} hours"
            self.operation_tracker.mark_operation_failed(resource.resource_id, reason=reason)
        else:
            raise CleanupError(f"Unsupported resource type: {resource.resource_type}")
    
    def _cascade_cleanup(self, resource: OrphanedResource) -> None:
        """Clean up related resources."""
        # Clean up associated lock for operation
        if resource.resource_type == ResourceType.OPERATION:
            lock_id = resource.metadata.get("lock_id")
            if lock_id:
                try:
                    self.lock_manager.release_lock(lock_id, force=True)
                    logger.info(f"Cascaded cleanup of lock {lock_id}")
                except Exception as e:
                    logger.error(f"Failed to cascade cleanup lock {lock_id}: {e}")
    
    def _record_audit(
        self,
        resource: OrphanedResource,
        strategy: CleanupStrategy,
        success: bool,
        forced: bool = False,
        reason: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Record cleanup in audit trail."""
        if resource.resource_id not in self._audit_trail:
            self._audit_trail[resource.resource_id] = []
        
        inactive_duration = datetime.utcnow() - resource.last_activity
        
        self._audit_trail[resource.resource_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "cleanup_executed",
            "resource_id": resource.resource_id,
            "resource_type": resource.resource_type.value,
            "action": strategy.action,
            "success": success,
            "forced": forced,
            "reason": reason,
            "error": error,
            "justification": f"Resource inactive for {inactive_duration}"
        })
    
    def _scan_loop(self) -> None:
        """Background scanning loop."""
        while not self._stop_scan.is_set():
            try:
                orphans = self.scan_for_orphans()
                
                # Cleanup orphaned resources
                for resource in orphans:
                    self.cleanup_resource(resource)
                
            except Exception as e:
                logger.error(f"Error in scan loop: {e}")
            
            # Wait for next scan
            self._stop_scan.wait(self.scan_interval_seconds)
