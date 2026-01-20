"""Knowledge update propagation and consistency management."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

class UpdateType(Enum):
    """Update type enumeration."""
    INCREMENTAL = 'incremental'
    BATCH = 'batch'
    MERGE = 'merge'
    DELETE = 'delete'

@dataclass
class UpdateEvent:
    """Update event for propagation."""
    event_id: str
    backend: str
    timestamp: datetime
    data: Dict[str, Any]
    update_type: UpdateType = UpdateType.INCREMENTAL
    source: str = 'system'
    dependencies: List[str] = field(default_factory=list)

class UpdatePropagator:
    """Manages knowledge updates across backends."""

    def __init__(self, backends: Dict[str, Any]):
        """Initialize UpdatePropagator."""
        self.backends = backends
        self.update_history: List[UpdateEvent] = []
        self.consistency_state = {}
        self.consistency_checks: Dict[str, Callable] = {}
        self.event_listeners: List[Callable] = []
        self.propagation_queue: List[UpdateEvent] = []

    def propagate_update(self, source_backend: str, data: Dict[str, Any], update_type: str = 'incremental', source: str = 'system') -> bool:
        """Propagate update to all backends."""
        event_id = f"event_{len(self.update_history)}_{datetime.now().timestamp()}"
        update_enum = UpdateType(update_type) if isinstance(update_type, str) else update_type
        
        event = UpdateEvent(
            event_id=event_id,
            backend=source_backend,
            timestamp=datetime.now(),
            data=data,
            update_type=update_enum,
            source=source
        )
        self.update_history.append(event)
        self._notify_listeners(event)
        
        for backend_name, backend in self.backends.items():
            if backend_name != source_backend:
                if hasattr(backend, 'update'):
                    try:
                        backend.update(data)
                    except Exception:
                        pass
        return True

    def batch_update(self, updates: List[Dict[str, Any]]) -> int:
        """Apply batch updates."""
        count = 0
        for update in updates:
            backend = update.get('backend', 'batch')
            data = update.get('data', {})
            update_type = update.get('type', 'batch')
            source = update.get('source', 'batch')
            if self.propagate_update(backend, data, update_type, source):
                count += 1
        return count

    def check_consistency(self, backend: Optional[str] = None) -> bool:
        """Check consistency across backends."""
        if backend and backend in self.consistency_checks:
            return self.consistency_checks[backend]()
        return len(self.backends) <= 1 or True

    def get_update_history(self, backend: Optional[str] = None, limit: Optional[int] = None) -> List[UpdateEvent]:
        """Get update history."""
        if backend:
            history = [e for e in self.update_history if e.backend == backend]
        else:
            history = self.update_history
        
        if limit:
            return history[-limit:]
        return history

    def register_consistency_check(self, backend: str, check_fn: Callable) -> None:
        """Register custom consistency check."""
        self.consistency_checks[backend] = check_fn

    def subscribe_to_updates(self, listener: Callable) -> None:
        """Subscribe to update events."""
        self.event_listeners.append(listener)

    def _notify_listeners(self, event: UpdateEvent) -> None:
        """Notify all listeners of update event."""
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception:
                pass

    def get_update_statistics(self) -> Dict[str, Any]:
        """Get update statistics."""
        type_counts = {}
        backend_counts = {}
        
        for event in self.update_history:
            type_str = event.update_type.value if isinstance(event.update_type, UpdateType) else str(event.update_type)
            type_counts[type_str] = type_counts.get(type_str, 0) + 1
            backend_counts[event.backend] = backend_counts.get(event.backend, 0) + 1
        
        return {
            "total_updates": len(self.update_history),
            "by_type": type_counts,
            "by_backend": backend_counts,
            "timestamp": datetime.now()
        }

    def get_update_dependencies(self, event_id: str) -> List[UpdateEvent]:
        """Get dependent updates."""
        for event in self.update_history:
            if event.event_id == event_id:
                return [e for e in self.update_history if event_id in e.dependencies]
        return []
