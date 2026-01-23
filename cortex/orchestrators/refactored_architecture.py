"""Architecture Refactoring - SRP & Dependency Injection.

REM-ARCH-001: Single Responsibility Principle
- Orchestrator: Orchestration coordination
- Scheduler: Schedule management
- LifecycleManager: Lifecycle operations
- PersistenceManager: State persistence

REM-ARCH-002: Dependency Inversion Principle
- Abstract interfaces for dependencies
- Dependency injection container
- Factory patterns
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """Execution context for orchestration."""
    
    execution_id: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class ExecutionResult:
    """Result of execution."""
    
    status: str  # success, failure, timeout
    output: Any
    metadata: Dict[str, Any]


class IScheduler(ABC):
    """Scheduler interface (REM-ARCH-001: SRP)."""
    
    @abstractmethod
    def schedule_task(self, task_id: str, task: Any, delay_ms: int = 0) -> bool:
        """Schedule a task for execution."""
        pass
    
    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        pass
    
    @abstractmethod
    def get_scheduled_tasks(self) -> List[str]:
        """Get list of scheduled task IDs."""
        pass


class ILifecycleManager(ABC):
    """Lifecycle manager interface (REM-ARCH-001: SRP)."""
    
    @abstractmethod
    def start(self) -> bool:
        """Start the orchestrator."""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop the orchestrator."""
        pass
    
    @abstractmethod
    def pause(self) -> bool:
        """Pause the orchestrator."""
        pass
    
    @abstractmethod
    def resume(self) -> bool:
        """Resume the orchestrator."""
        pass
    
    @abstractmethod
    def get_status(self) -> str:
        """Get current status."""
        pass


class IPersistenceManager(ABC):
    """Persistence manager interface (REM-ARCH-001: SRP)."""
    
    @abstractmethod
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save state to persistent storage."""
        pass
    
    @abstractmethod
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load state from persistent storage."""
        pass
    
    @abstractmethod
    def delete_state(self) -> bool:
        """Delete persisted state."""
        pass


class IExecutor(ABC):
    """Executor interface for decoupled execution."""
    
    @abstractmethod
    async def execute(
        self,
        task_name: str,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """Execute a task."""
        pass


class DependencyContainer:
    """Dependency injection container (REM-ARCH-002).
    
    Manages all dependencies and provides them to consumers.
    Supports factory patterns and singleton management.
    """
    
    def __init__(self) -> None:
        """Initialize dependency container."""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._interfaces: Dict[str, type] = {}
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance.
        
        Args:
            name: Service name
            instance: Singleton instance
        """
        self._singletons[name] = instance
        logger.debug(f"Registered singleton: {name}")
    
    def register_factory(self, name: str, factory: callable) -> None:
        """Register a factory function.
        
        Args:
            name: Service name
            factory: Factory function that creates instances
        """
        self._factories[name] = factory
        logger.debug(f"Registered factory: {name}")
    
    def register_interface(self, interface_name: str, interface_type: type) -> None:
        """Register an interface mapping.
        
        Args:
            interface_name: Interface name
            interface_type: Interface type/class
        """
        self._interfaces[interface_name] = interface_type
        logger.debug(f"Registered interface: {interface_name}")
    
    def get(self, name: str) -> Any:
        """Get a service instance.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not registered
        """
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]
        
        # Check factories
        if name in self._factories:
            return self._factories[name]()
        
        raise KeyError(f"Service not registered: {name}")
    
    def get_interface(self, interface_name: str) -> type:
        """Get an interface type.
        
        Args:
            interface_name: Interface name
            
        Returns:
            Interface type
            
        Raises:
            KeyError: If interface not registered
        """
        if interface_name not in self._interfaces:
            raise KeyError(f"Interface not registered: {interface_name}")
        return self._interfaces[interface_name]


class Orchestrator:
    """Orchestrator (refactored for SRP).
    
    Single responsibility: Orchestration coordination
    Delegates to specialized managers for other concerns.
    """
    
    def __init__(
        self,
        name: str,
        scheduler: IScheduler,
        lifecycle_manager: ILifecycleManager,
        persistence_manager: IPersistenceManager,
    ) -> None:
        """Initialize orchestrator with injected dependencies.
        
        Args:
            name: Orchestrator name
            scheduler: Scheduler implementation
            lifecycle_manager: Lifecycle manager implementation
            persistence_manager: Persistence manager implementation
        """
        self.name = name
        self._scheduler = scheduler
        self._lifecycle_manager = lifecycle_manager
        self._persistence_manager = persistence_manager
        self._context: Optional[ExecutionContext] = None
    
    def start(self) -> bool:
        """Start orchestration."""
        if not self._lifecycle_manager.start():
            logger.error(f"Failed to start orchestrator: {self.name}")
            return False
        
        logger.info(f"Orchestrator started: {self.name}")
        return True
    
    def stop(self) -> bool:
        """Stop orchestration."""
        if not self._lifecycle_manager.stop():
            logger.error(f"Failed to stop orchestrator: {self.name}")
            return False
        
        logger.info(f"Orchestrator stopped: {self.name}")
        return True
    
    def get_status(self) -> str:
        """Get orchestrator status."""
        return self._lifecycle_manager.get_status()


class Scheduler(IScheduler):
    """Scheduler implementation (REM-ARCH-001: SRP)."""
    
    def __init__(self) -> None:
        """Initialize scheduler."""
        self._scheduled_tasks: Dict[str, Any] = {}
    
    def schedule_task(self, task_id: str, task: Any, delay_ms: int = 0) -> bool:
        """Schedule a task for execution."""
        self._scheduled_tasks[task_id] = {
            "task": task,
            "delay_ms": delay_ms,
        }
        logger.debug(f"Task scheduled: {task_id} (delay={delay_ms}ms)")
        return True
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id in self._scheduled_tasks:
            del self._scheduled_tasks[task_id]
            logger.debug(f"Task cancelled: {task_id}")
            return True
        return False
    
    def get_scheduled_tasks(self) -> List[str]:
        """Get list of scheduled task IDs."""
        return list(self._scheduled_tasks.keys())


class LifecycleManager(ILifecycleManager):
    """Lifecycle manager implementation (REM-ARCH-001: SRP)."""
    
    def __init__(self) -> None:
        """Initialize lifecycle manager."""
        self._status = "STOPPED"
    
    def start(self) -> bool:
        """Start the orchestrator."""
        self._status = "RUNNING"
        logger.info("Lifecycle manager: started")
        return True
    
    def stop(self) -> bool:
        """Stop the orchestrator."""
        self._status = "STOPPED"
        logger.info("Lifecycle manager: stopped")
        return True
    
    def pause(self) -> bool:
        """Pause the orchestrator."""
        self._status = "PAUSED"
        logger.info("Lifecycle manager: paused")
        return True
    
    def resume(self) -> bool:
        """Resume the orchestrator."""
        self._status = "RUNNING"
        logger.info("Lifecycle manager: resumed")
        return True
    
    def get_status(self) -> str:
        """Get current status."""
        return self._status


class PersistenceManager(IPersistenceManager):
    """Persistence manager implementation (REM-ARCH-001: SRP)."""
    
    def __init__(self) -> None:
        """Initialize persistence manager."""
        self._persisted_state: Optional[Dict[str, Any]] = None
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save state to persistent storage."""
        self._persisted_state = state.copy()
        logger.info(f"State persisted: {len(state)} items")
        return True
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load state from persistent storage."""
        if self._persisted_state is None:
            logger.info("No persisted state found")
            return None
        return self._persisted_state.copy()
    
    def delete_state(self) -> bool:
        """Delete persisted state."""
        self._persisted_state = None
        logger.info("Persisted state deleted")
        return True


__all__ = [
    "IScheduler",
    "ILifecycleManager",
    "IPersistenceManager",
    "IExecutor",
    "DependencyContainer",
    "Orchestrator",
    "Scheduler",
    "LifecycleManager",
    "PersistenceManager",
    "ExecutionContext",
    "ExecutionResult",
]
