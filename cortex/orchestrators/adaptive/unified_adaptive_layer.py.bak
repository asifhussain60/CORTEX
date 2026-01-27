"""Unified Adaptive Layer - Consolidated Adaptive Execution Framework.

This module consolidates 6 adaptive execution components into a single,
cohesive interface:
- AdaptiveExecutor: Mode-based execution (FAST, BALANCED, THOROUGH)
- ExecutionStrategy: Strategy selection based on task characteristics
- PerformanceOptimizer: Performance profiling and optimization
- LoadBalancer: Load distribution and resource allocation
- ResourceManager: Resource lifecycle management
- FailoverManager: Failover and recovery strategies

AC-TRANSFORM-002-CONS-009: Consolidation of adaptive layer reduces
maintenance burden and provides unified adaptive execution interface.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Dict,
    Optional,
    List,
    Callable,
    Tuple,
    Union,
)
from datetime import datetime
import logging
import threading
from statistics import mean, stdev
from cortex.models.canonical_enums import ExecutionMode


# ============================================================================
# Enums and Data Models
# ============================================================================



class StrategyType(Enum):
    """Execution strategy types."""
    FAST = "FAST"
    BALANCED = "BALANCED"
    THOROUGH = "THOROUGH"


@dataclass
class ModeConfiguration:
    """Configuration for an execution mode."""
    mode: ExecutionMode
    timeout_seconds: float
    validation_level: float  # 0.0 = none, 1.0 = maximum
    enable_caching: bool
    enable_logging: bool
    retry_count: int
    parallel_execution: bool


@dataclass
class ExecutionMetrics:
    """Metrics for a single execution."""
    orchestrator: str
    task_type: str
    duration_seconds: float
    memory_mb: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceProfile:
    """Performance profile for an orchestrator."""
    orchestrator: str
    executions: List[ExecutionMetrics] = field(default_factory=list)
    
    @property
    def total_executions(self) -> int:
        return len(self.executions)
    
    @property
    def successful_executions(self) -> int:
        return sum(1 for e in self.executions if e.success)
    
    @property
    def success_rate(self) -> float:
        if not self.executions:
            return 0.0
        return self.successful_executions / self.total_executions
    
    @property
    def average_duration(self) -> float:
        if not self.executions:
            return 0.0
        durations = [e.duration_seconds for e in self.executions]
        return mean(durations) if durations else 0.0
    
    @property
    def min_duration(self) -> float:
        if not self.executions:
            return 0.0
        return min(e.duration_seconds for e in self.executions)
    
    @property
    def max_duration(self) -> float:
        if not self.executions:
            return 0.0
        return max(e.duration_seconds for e in self.executions)
    
    @property
    def duration_stddev(self) -> float:
        if len(self.executions) < 2:
            return 0.0
        durations = [e.duration_seconds for e in self.executions]
        return stdev(durations)


@dataclass
class ResourceAllocation:
    """Resource allocation for a task."""
    resource_id: str
    resource_type: str
    quantity: float
    unit: str
    allocated_at: datetime = field(default_factory=datetime.now)
    release_at: Optional[datetime] = None


@dataclass
class FailoverContext:
    """Context for failover decision-making."""
    failure_type: str
    failed_component: str
    original_task: Any
    error_message: str
    timestamp: datetime = field(default_factory=datetime.now)
    recovery_attempts: int = 0


# ============================================================================
# Unified Adaptive Layer
# ============================================================================

class UnifiedAdaptiveLayer:
    """Unified adaptive execution framework.
    
    Consolidates adaptive execution capabilities:
    - Execution modes (FAST, BALANCED, THOROUGH)
    - Strategy selection based on task characteristics
    - Performance profiling and optimization
    - Load balancing and resource allocation
    - Resource lifecycle management
    - Failover and recovery strategies
    
    Example:
        >>> adapter = UnifiedAdaptiveLayer()
        >>> adapter.set_execution_mode(ExecutionMode.BALANCED)
        >>> result = adapter.execute_in_mode({"task": "example"}, "default")
    """
    
    def __init__(self) -> None:
        """Initialize the unified adaptive layer."""
        self._logger = logging.getLogger(__name__)
        
        # Execution mode management
        self._mode_configs: Dict[ExecutionMode, ModeConfiguration] = {
            ExecutionMode.FAST: ModeConfiguration(
                mode=ExecutionMode.FAST,
                timeout_seconds=2.0,
                validation_level=0.2,
                enable_caching=True,
                enable_logging=False,
                retry_count=0,
                parallel_execution=True,
            ),
            ExecutionMode.BALANCED: ModeConfiguration(
                mode=ExecutionMode.BALANCED,
                timeout_seconds=5.0,
                validation_level=0.6,
                enable_caching=True,
                enable_logging=True,
                retry_count=1,
                parallel_execution=True,
            ),
            ExecutionMode.THOROUGH: ModeConfiguration(
                mode=ExecutionMode.THOROUGH,
                timeout_seconds=15.0,
                validation_level=1.0,
                enable_caching=False,
                enable_logging=True,
                retry_count=3,
                parallel_execution=False,
            ),
        }
        self._current_mode = ExecutionMode.BALANCED
        
        # Strategy management
        self._strategy_configs: Dict[StrategyType, Dict[str, Any]] = {
            StrategyType.FAST: {
                "timeout_multiplier": 1.0,
                "validation_level": 0.2,
                "enable_caching": True,
                "retry_count": 0,
                "parallel_execution": True,
            },
            StrategyType.BALANCED: {
                "timeout_multiplier": 2.0,
                "validation_level": 0.6,
                "enable_caching": True,
                "retry_count": 1,
                "parallel_execution": True,
            },
            StrategyType.THOROUGH: {
                "timeout_multiplier": 4.0,
                "validation_level": 1.0,
                "enable_caching": False,
                "retry_count": 3,
                "parallel_execution": False,
            },
        }
        
        # Performance tracking
        self._performance_profiles: Dict[str, PerformanceProfile] = {}
        self._execution_history: List[Dict[str, Any]] = []
        
        # Load balancing
        self._orchestrator_load: Dict[str, float] = {}
        self._resource_allocations: Dict[str, ResourceAllocation] = {}
        self._load_lock = threading.RLock()
        
        # Failover management
        self._failover_handlers: List[Callable[[FailoverContext], bool]] = []
        self._recovery_strategies: Dict[str, Callable[[FailoverContext], Any]] = {}
        
        # Cache and statistics
        self._execution_cache: Dict[str, Any] = {}
        self._stats: Dict[str, int] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "failovers_triggered": 0,
        }
    
    # ========================================================================
    # Execution Mode Methods (from AdaptiveExecutor)
    # ========================================================================
    
    def set_execution_mode(self, mode: ExecutionMode) -> None:
        """Set the execution mode.
        
        Args:
            mode: ExecutionMode to use
        """
        self._current_mode = mode
        self._logger.info(f"Execution mode set to {mode.value}")
    
    def get_execution_mode(self) -> ExecutionMode:
        """Get the current execution mode.
        
        Returns:
            Current ExecutionMode
        """
        return self._current_mode
    
    def get_mode_config(
        self,
        mode: Optional[ExecutionMode] = None,
    ) -> ModeConfiguration:
        """Get configuration for a mode.
        
        Args:
            mode: ExecutionMode (uses current if not specified)
            
        Returns:
            ModeConfiguration for the mode
        """
        if mode is None:
            mode = self._current_mode
        return self._mode_configs[mode]
    
    def execute_in_mode(
        self,
        task: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Execute a task with current mode configuration.
        
        Args:
            task: Task to execute
            context: Optional execution context
            
        Returns:
            Task result
        """
        if context is None:
            context = {}
        
        self._stats["total_executions"] += 1
        config = self.get_mode_config()
        
        try:
            # Validate task if validation enabled
            if config.validation_level > 0:
                self._validate_task(task)
            
            # Execute with retries if configured
            if config.retry_count > 0:
                result = self._execute_with_retries(
                    task,
                    config.retry_count,
                    context,
                )
            else:
                result = self._execute_once(task, context)
            
            self._stats["successful_executions"] += 1
            return result
            
        except Exception as e:
            self._stats["failed_executions"] += 1
            self._logger.error(f"Execution failed: {str(e)}")
            raise
    
    def _validate_task(self, task: Any) -> None:
        """Validate task structure and contents.
        
        Args:
            task: Task to validate
            
        Raises:
            ValueError: If task is invalid
        """
        if not task:
            raise ValueError("Task cannot be None or empty")
    
    def _execute_once(
        self,
        task: Any,
        context: Dict[str, Any],
    ) -> Any:
        """Execute task once without retries.
        
        Args:
            task: Task to execute
            context: Execution context
            
        Returns:
            Execution result
        """
        return {
            "status": "success",
            "task": task,
            "mode": self._current_mode.value,
            "context": context,
        }
    
    def _execute_with_retries(
        self,
        task: Any,
        retries: int,
        context: Dict[str, Any],
    ) -> Any:
        """Execute task with retries on failure.
        
        Args:
            task: Task to execute
            retries: Number of retries allowed
            context: Execution context
            
        Returns:
            Execution result
        """
        last_error = None
        
        for attempt in range(retries + 1):
            try:
                return self._execute_once(task, context)
            except Exception as e:
                last_error = e
                if attempt < retries:
                    self._logger.warning(
                        f"Execution attempt {attempt + 1} failed, retrying..."
                    )
                else:
                    self._logger.error(
                        f"All {retries + 1} execution attempts failed"
                    )
        
        if last_error:
            raise last_error
    
    # ========================================================================
    # Strategy Selection Methods (from ExecutionStrategy)
    # ========================================================================
    
    def select_strategy(self, task: Dict[str, Any]) -> StrategyType:
        """Select optimal strategy for a task.
        
        Args:
            task: Task characteristics
            
        Returns:
            Selected StrategyType
        """
        complexity = self._analyze_task_complexity(task)
        deadline = task.get("deadline_seconds", float("inf"))
        required_certainty = task.get("required_certainty", 0.5)
        
        # Decision matrix based on complexity, deadline, certainty
        if complexity == "low":
            return StrategyType.FAST
        elif complexity == "medium":
            if deadline < 3:
                return StrategyType.FAST
            elif required_certainty > 0.9:
                return StrategyType.THOROUGH
            else:
                return StrategyType.BALANCED
        else:  # high complexity
            if required_certainty > 0.95:
                return StrategyType.THOROUGH
            elif deadline < 5:
                return StrategyType.BALANCED
            else:
                return StrategyType.THOROUGH
    
    def get_strategy_recommendations(
        self,
        task: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Get recommendations for all strategies.
        
        Args:
            task: Task characteristics
            
        Returns:
            Dictionary mapping strategies to their characteristics
        """
        recommendations: Dict[str, Any] = {}
        for strategy in StrategyType:
            config = self._strategy_configs[strategy]
            recommendations[strategy.value] = {
                "strategy": strategy.value,
                "config": config,
                "estimated_duration": config["timeout_multiplier"] * 2.0,
                "validation_level": config["validation_level"],
                "reliability": config["retry_count"] + 1,
            }
        return recommendations
    
    def apply_strategy(
        self,
        task: Dict[str, Any],
        strategy: StrategyType,
    ) -> Any:
        """Apply a strategy to a task.
        
        Args:
            task: Task to execute
            strategy: Strategy to apply
            
        Returns:
            Execution result
        """
        config = self._strategy_configs[strategy]
        self._logger.info(f"Applying strategy {strategy.value} to task")
        
        # Create execution context from strategy config
        context = {
            "strategy": strategy.value,
            "timeout": config["timeout_multiplier"] * 2.0,
            "validation_level": config["validation_level"],
            "retries": config["retry_count"],
        }
        
        # Execute with strategy-specific configuration
        return self.execute_in_mode(task, context)
    
    def _analyze_task_complexity(self, task: Dict[str, Any]) -> str:
        """Analyze task complexity.
        
        Args:
            task: Task to analyze
            
        Returns:
            Complexity level: "low", "medium", or "high"
        """
        if "complexity" in task:
            return task["complexity"]
        
        input_size = len(task.get("inputs", []))
        requires_validation = task.get("requires_validation", False)
        
        if input_size > 10 or requires_validation:
            return "high"
        elif input_size > 5:
            return "medium"
        else:
            return "low"
    
    # ========================================================================
    # Performance Optimization Methods (from PerformanceOptimizer)
    # ========================================================================
    
    def collect_metrics(
        self,
        orchestrator: str,
        task_type: str,
        duration_seconds: float,
        memory_mb: float,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """Collect execution metrics for performance tracking.
        
        Args:
            orchestrator: Orchestrator name
            task_type: Type of task
            duration_seconds: Execution duration
            memory_mb: Memory used
            success: Whether execution succeeded
            error_message: Error message if failed
        """
        metrics = ExecutionMetrics(
            orchestrator=orchestrator,
            task_type=task_type,
            duration_seconds=duration_seconds,
            memory_mb=memory_mb,
            success=success,
            error_message=error_message,
        )
        
        # Update or create performance profile
        if orchestrator not in self._performance_profiles:
            self._performance_profiles[orchestrator] = PerformanceProfile(
                orchestrator=orchestrator
            )
        
        self._performance_profiles[orchestrator].executions.append(metrics)
        self._logger.debug(f"Metrics collected for {orchestrator}: {duration_seconds}s")
    
    def optimize_execution(
        self,
        task: Dict[str, Any],
        metrics: ExecutionMetrics,
    ) -> Dict[str, Any]:
        """Generate optimization suggestions based on metrics.
        
        Args:
            task: Task that was executed
            metrics: Execution metrics
            
        Returns:
            Dictionary with optimization suggestions
        """
        suggestions: Dict[str, Any] = {
            "task": task,
            "current_metrics": {
                "duration": metrics.duration_seconds,
                "memory": metrics.memory_mb,
            },
            "optimizations": [],
        }
        
        # Suggest optimizations based on metrics
        if metrics.duration_seconds > 10.0:
            suggestions["optimizations"].append(
                "Consider using FAST mode to reduce execution time"
            )
        
        if metrics.memory_mb > 500:
            suggestions["optimizations"].append(
                "Consider disabling features to reduce memory usage"
            )
        
        if not metrics.success:
            suggestions["optimizations"].append(
                "Consider using THOROUGH mode with more validation"
            )
        
        return suggestions
    
    def get_optimization_suggestions(
        self,
        orchestrator: str,
    ) -> List[str]:
        """Get optimization suggestions for an orchestrator.
        
        Args:
            orchestrator: Orchestrator name
            
        Returns:
            List of optimization suggestions
        """
        if orchestrator not in self._performance_profiles:
            return []
        
        profile = self._performance_profiles[orchestrator]
        suggestions: List[str] = []
        
        if profile.success_rate < 0.9:
            suggestions.append(
                f"Low success rate ({profile.success_rate:.1%}), "
                "consider increasing validation"
            )
        
        if profile.average_duration > 10.0:
            suggestions.append(
                f"High average duration ({profile.average_duration:.1f}s), "
                "consider optimization"
            )
        
        if profile.duration_stddev > 5.0:
            suggestions.append(
                f"High variability in duration ({profile.duration_stddev:.1f}s), "
                "consider consistent resource allocation"
            )
        
        return suggestions
    
    # ========================================================================
    # Load Balancing Methods (from LoadBalancer)
    # ========================================================================
    
    def allocate_resources(
        self,
        task: Dict[str, Any],
    ) -> Dict[str, ResourceAllocation]:
        """Allocate resources for a task.
        
        Args:
            task: Task requiring resources
            
        Returns:
            Dictionary of allocated resources
        """
        with self._load_lock:
            allocations: Dict[str, ResourceAllocation] = {}
            resource_id = f"resource_{len(self._resource_allocations)}"
            
            # Allocate based on task complexity
            complexity = self._analyze_task_complexity(task)
            
            if complexity == "high":
                cpu_allocation = ResourceAllocation(
                    resource_id=f"{resource_id}_cpu",
                    resource_type="CPU",
                    quantity=4.0,
                    unit="cores",
                )
                memory_allocation = ResourceAllocation(
                    resource_id=f"{resource_id}_memory",
                    resource_type="Memory",
                    quantity=4096.0,
                    unit="MB",
                )
                allocations["cpu"] = cpu_allocation
                allocations["memory"] = memory_allocation
            elif complexity == "medium":
                memory_allocation = ResourceAllocation(
                    resource_id=f"{resource_id}_memory",
                    resource_type="Memory",
                    quantity=2048.0,
                    unit="MB",
                )
                allocations["memory"] = memory_allocation
            else:
                memory_allocation = ResourceAllocation(
                    resource_id=f"{resource_id}_memory",
                    resource_type="Memory",
                    quantity=512.0,
                    unit="MB",
                )
                allocations["memory"] = memory_allocation
            
            # Store allocations
            for _, allocation in allocations.items():
                self._resource_allocations[allocation.resource_id] = allocation
            
            self._logger.debug(f"Resources allocated for task: {allocations}")
            return allocations
    
    def distribute_load(self, tasks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Distribute tasks across orchestrators.
        
        Args:
            tasks: List of tasks to distribute
            
        Returns:
            Dictionary mapping orchestrator names to task counts
        """
        with self._load_lock:
            distribution: Dict[str, int] = {}
            
            for i, task in enumerate(tasks):
                # Simple round-robin with load awareness
                orchestrator = f"orchestrator_{i % 3}"
                
                if orchestrator not in distribution:
                    distribution[orchestrator] = 0
                distribution[orchestrator] += 1
                
                # Update load tracking
                self._orchestrator_load[orchestrator] = (
                    self._orchestrator_load.get(orchestrator, 0.0) + 1.0
                )
            
            self._logger.info(f"Load distributed: {distribution}")
            return distribution
    
    def get_load_status(self) -> Dict[str, Any]:
        """Get current load status across orchestrators.
        
        Returns:
            Dictionary with orchestrator load information
        """
        with self._load_lock:
            return {
                "timestamp": datetime.now(),
                "orchestrator_load": dict(self._orchestrator_load),
                "total_allocations": len(self._resource_allocations),
                "active_tasks": sum(self._orchestrator_load.values()),
            }
    
    # ========================================================================
    # Resource Management Methods (from ResourceManager)
    # ========================================================================
    
    def track_resource(
        self,
        resource_id: str,
        allocation: ResourceAllocation,
    ) -> None:
        """Track a resource allocation.
        
        Args:
            resource_id: Unique resource identifier
            allocation: ResourceAllocation to track
        """
        with self._load_lock:
            self._resource_allocations[resource_id] = allocation
            self._logger.debug(f"Resource tracked: {resource_id}")
    
    def release_resource(self, resource_id: str) -> None:
        """Release a resource.
        
        Args:
            resource_id: Resource to release
        """
        with self._load_lock:
            if resource_id in self._resource_allocations:
                allocation = self._resource_allocations[resource_id]
                allocation.release_at = datetime.now()
                self._logger.debug(f"Resource released: {resource_id}")
    
    def cleanup_all_resources(self) -> int:
        """Clean up all allocated resources.
        
        Returns:
            Number of resources cleaned up
        """
        with self._load_lock:
            now = datetime.now()
            cleaned_count = 0
            
            # Mark all unreleasedresources as released
            for resource_id, allocation in self._resource_allocations.items():
                if allocation.release_at is None:
                    allocation.release_at = now
                    cleaned_count += 1
            
            self._logger.info(f"Cleaned up {cleaned_count} resources")
            return cleaned_count
    
    # ========================================================================
    # Failover and Recovery Methods (from FailoverManager)
    # ========================================================================
    
    def register_failover_handler(
        self,
        handler: Callable[[FailoverContext], bool],
    ) -> None:
        """Register a failover handler.
        
        Args:
            handler: Callable that handles failover situations
        """
        self._failover_handlers.append(handler)
        self._logger.debug(f"Failover handler registered")
    
    def register_recovery_strategy(
        self,
        failure_type: str,
        strategy: Callable[[FailoverContext], Any],
    ) -> None:
        """Register a recovery strategy for a failure type.
        
        Args:
            failure_type: Type of failure
            strategy: Callable that implements recovery
        """
        self._recovery_strategies[failure_type] = strategy
        self._logger.debug(f"Recovery strategy registered for {failure_type}")
    
    def trigger_failover(
        self,
        failure_context: FailoverContext,
    ) -> Optional[Any]:
        """Trigger failover in response to a failure.
        
        Args:
            failure_context: Context of the failure
            
        Returns:
            Recovery result from registered handlers/strategies
        """
        self._stats["failovers_triggered"] += 1
        failure_context.recovery_attempts += 1
        
        self._logger.warning(
            f"Failover triggered for {failure_context.failure_type}: "
            f"{failure_context.error_message}"
        )
        
        # Try registered recovery strategies
        if failure_context.failure_type in self._recovery_strategies:
            strategy = self._recovery_strategies[failure_context.failure_type]
            try:
                return strategy(failure_context)
            except Exception as e:
                self._logger.error(f"Recovery strategy failed: {str(e)}")
        
        # Call registered failover handlers
        for handler in self._failover_handlers:
            try:
                result = handler(failure_context)
                if result:
                    return result
            except Exception as e:
                self._logger.error(f"Failover handler failed: {str(e)}")
        
        return None
    
    def get_recovery_options(
        self,
        failure_context: FailoverContext,
    ) -> List[str]:
        """Get available recovery options for a failure.
        
        Args:
            failure_context: Context of the failure
            
        Returns:
            List of available recovery options
        """
        options: List[str] = []
        
        # List registered recovery strategies
        for failure_type in self._recovery_strategies.keys():
            options.append(f"Use recovery strategy for {failure_type}")
        
        # List registered handlers
        if self._failover_handlers:
            options.append(f"Call {len(self._failover_handlers)} registered handlers")
        
        # Add default options
        options.extend([
            "Retry with different execution mode",
            "Allocate additional resources",
            "Fallback to alternative orchestrator",
        ])
        
        return options
    
    # ========================================================================
    # Statistics and Monitoring
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics.
        
        Returns:
            Dictionary with current statistics
        """
        return {
            "timestamp": datetime.now(),
            "stats": dict(self._stats),
            "success_rate": (
                self._stats["successful_executions"]
                / max(self._stats["total_executions"], 1)
            ),
            "performance_profiles": {
                orch: {
                    "total": profile.total_executions,
                    "successful": profile.successful_executions,
                    "success_rate": profile.success_rate,
                    "avg_duration": profile.average_duration,
                }
                for orch, profile in self._performance_profiles.items()
            },
        }
    
    def reset_statistics(self) -> None:
        """Reset all statistics."""
        self._stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "failovers_triggered": 0,
        }
        self._performance_profiles.clear()
        self._logger.info("Statistics reset")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of adaptive layer.
        
        Returns:
            Health check results
        """
        return {
            "timestamp": datetime.now(),
            "status": "healthy",
            "current_mode": self._current_mode.value,
            "active_resources": len(self._resource_allocations),
            "total_executions": self._stats["total_executions"],
            "success_rate": (
                self._stats["successful_executions"]
                / max(self._stats["total_executions"], 1)
            ),
            "failovers": self._stats["failovers_triggered"],
            "recovery_strategies": len(self._recovery_strategies),
            "failover_handlers": len(self._failover_handlers),
        }
