"""
CORTEX 3.0 Load Balancer
========================

Intelligent load balancing and request distribution for high-performance
documentation generation with queue management and worker optimization.
"""

import time
import threading
import asyncio
import random
import statistics
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque
import heapq


logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"
    RESOURCE_USAGE = "resource_usage"
    ADAPTIVE = "adaptive"


class WorkerStatus(Enum):
    """Worker status states."""
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


@dataclass
class WorkerNode:
    """Represents a worker node in the load balancer."""
    worker_id: str
    capacity: int = 100  # Processing capacity (0-100)
    weight: float = 1.0  # Load balancing weight
    current_load: int = 0  # Current active requests
    total_processed: int = 0
    total_failed: int = 0
    avg_response_time_ms: float = 0.0
    last_health_check: float = field(default_factory=time.time)
    status: WorkerStatus = WorkerStatus.IDLE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def utilization(self) -> float:
        """Calculate current utilization percentage."""
        if self.capacity == 0:
            return 100.0
        return min(100.0, (self.current_load / self.capacity) * 100.0)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        total_requests = self.total_processed + self.total_failed
        if total_requests == 0:
            return 100.0
        return (self.total_processed / total_requests) * 100.0
    
    @property
    def is_healthy(self) -> bool:
        """Check if worker is healthy and available."""
        return (
            self.status in [WorkerStatus.ACTIVE, WorkerStatus.IDLE, WorkerStatus.BUSY] and
            self.success_rate >= 80.0 and  # At least 80% success rate
            time.time() - self.last_health_check < 60.0  # Health check within 1 minute
        )


@dataclass
class LoadBalancingMetrics:
    """Load balancing performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    total_workers: int = 0
    active_workers: int = 0
    avg_worker_utilization: float = 0.0
    requests_per_second: float = 0.0
    strategy_switches: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100.0


@dataclass
class RequestContext:
    """Context information for load balancing decisions."""
    request_id: str
    priority: int = 0  # Higher = more important
    estimated_complexity: float = 1.0  # Complexity multiplier
    required_capabilities: List[str] = field(default_factory=list)
    timeout_ms: Optional[float] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class LoadBalancer:
    """
    Intelligent load balancer for documentation generation workers with
    multiple balancing strategies, health monitoring, and adaptive optimization.
    """
    
    def __init__(
        self,
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.ADAPTIVE,
        health_check_interval: float = 30.0,
        max_retries: int = 3,
        enable_circuit_breaker: bool = True,
        circuit_breaker_threshold: int = 5
    ):
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.max_retries = max_retries
        self.enable_circuit_breaker = enable_circuit_breaker
        self.circuit_breaker_threshold = circuit_breaker_threshold
        
        # Worker management
        self._workers: Dict[str, WorkerNode] = {}
        self._worker_lock = threading.RLock()
        
        # Load balancing state
        self._round_robin_index = 0
        self._response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Metrics and monitoring
        self._metrics = LoadBalancingMetrics()
        self._request_history: deque = deque(maxlen=1000)
        
        # Health monitoring
        self._health_monitor_running = False
        self._health_monitor_thread: Optional[threading.Thread] = None
        
        # Circuit breaker state
        self._circuit_breaker_state: Dict[str, Dict[str, Any]] = {}
        
        # Strategy adaptation
        self._strategy_performance: Dict[LoadBalancingStrategy, Dict[str, float]] = {
            strategy: {'avg_response_time': 0.0, 'success_rate': 100.0, 'sample_count': 0}
            for strategy in LoadBalancingStrategy
        }
        self._adaptive_window = deque(maxlen=100)
        
        # Request processing callbacks
        self._request_callbacks: List[Callable] = []
    
    def add_worker(
        self,
        worker_id: str,
        capacity: int = 100,
        weight: float = 1.0,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a worker node to the load balancer.
        
        Args:
            worker_id: Unique worker identifier
            capacity: Worker processing capacity (0-100)
            weight: Load balancing weight
            capabilities: Worker capabilities/specializations
            metadata: Additional worker metadata
        """
        with self._worker_lock:
            worker_metadata = metadata or {}
            if capabilities:
                worker_metadata['capabilities'] = capabilities
            
            worker = WorkerNode(
                worker_id=worker_id,
                capacity=capacity,
                weight=weight,
                metadata=worker_metadata,
                status=WorkerStatus.ACTIVE
            )
            
            self._workers[worker_id] = worker
            self._metrics.total_workers += 1
            
            # Initialize circuit breaker state
            if self.enable_circuit_breaker:
                self._circuit_breaker_state[worker_id] = {
                    'failures': 0,
                    'last_failure': 0,
                    'state': 'closed',  # closed, open, half-open
                    'next_attempt': 0
                }
        
        logger.info(f"Added worker {worker_id} with capacity {capacity}")
    
    def remove_worker(self, worker_id: str) -> bool:
        """
        Remove a worker node from the load balancer.
        
        Args:
            worker_id: Worker identifier to remove
            
        Returns:
            True if worker was removed successfully
        """
        with self._worker_lock:
            if worker_id in self._workers:
                del self._workers[worker_id]
                self._metrics.total_workers -= 1
                
                # Clean up circuit breaker state
                self._circuit_breaker_state.pop(worker_id, None)
                
                logger.info(f"Removed worker {worker_id}")
                return True
            return False
    
    def select_worker(self, context: Optional[RequestContext] = None) -> Optional[str]:
        """
        Select the best worker for a request based on the current strategy.
        
        Args:
            context: Request context for intelligent selection
            
        Returns:
            Selected worker ID or None if no workers available
        """
        with self._worker_lock:
            # Filter healthy workers
            healthy_workers = {
                worker_id: worker for worker_id, worker in self._workers.items()
                if worker.is_healthy and self._is_circuit_breaker_closed(worker_id)
            }
            
            if not healthy_workers:
                logger.warning("No healthy workers available")
                return None
            
            # Apply capability filtering if specified
            if context and context.required_capabilities:
                capable_workers = {}
                for worker_id, worker in healthy_workers.items():
                    worker_caps = worker.metadata.get('capabilities', [])
                    if all(cap in worker_caps for cap in context.required_capabilities):
                        capable_workers[worker_id] = worker
                
                if capable_workers:
                    healthy_workers = capable_workers
                elif context.required_capabilities:
                    logger.warning(f"No workers with required capabilities: {context.required_capabilities}")
            
            # Select worker based on strategy
            selected_worker = None
            
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                selected_worker = self._select_round_robin(healthy_workers)
            
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                selected_worker = self._select_least_connections(healthy_workers)
            
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                selected_worker = self._select_weighted_round_robin(healthy_workers)
            
            elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
                selected_worker = self._select_by_response_time(healthy_workers)
            
            elif self.strategy == LoadBalancingStrategy.RESOURCE_USAGE:
                selected_worker = self._select_by_resource_usage(healthy_workers)
            
            elif self.strategy == LoadBalancingStrategy.ADAPTIVE:
                selected_worker = self._select_adaptive(healthy_workers, context)
            
            # Update worker state
            if selected_worker:
                worker = self._workers[selected_worker]
                worker.current_load += 1
                if worker.current_load >= worker.capacity:
                    worker.status = WorkerStatus.BUSY
                elif worker.current_load > 0:
                    worker.status = WorkerStatus.ACTIVE
        
        return selected_worker
    
    def record_request_completion(
        self,
        worker_id: str,
        success: bool,
        response_time_ms: float,
        context: Optional[RequestContext] = None
    ) -> None:
        """
        Record completion of a request for performance tracking.
        
        Args:
            worker_id: Worker that processed the request
            success: Whether the request was successful
            response_time_ms: Request processing time
            context: Original request context
        """
        with self._worker_lock:
            if worker_id not in self._workers:
                return
            
            worker = self._workers[worker_id]
            
            # Update worker metrics
            worker.current_load = max(0, worker.current_load - 1)
            
            if success:
                worker.total_processed += 1
                self._metrics.successful_requests += 1
                
                # Reset circuit breaker on success
                if self.enable_circuit_breaker:
                    circuit_state = self._circuit_breaker_state.get(worker_id, {})
                    circuit_state['failures'] = 0
                    circuit_state['state'] = 'closed'
            else:
                worker.total_failed += 1
                self._metrics.failed_requests += 1
                
                # Update circuit breaker on failure
                if self.enable_circuit_breaker:
                    self._update_circuit_breaker(worker_id)
            
            # Update response times
            self._response_times[worker_id].append(response_time_ms)
            if self._response_times[worker_id]:
                worker.avg_response_time_ms = statistics.mean(self._response_times[worker_id])
            
            # Update worker status
            if worker.current_load == 0:
                worker.status = WorkerStatus.IDLE
            elif worker.current_load < worker.capacity:
                worker.status = WorkerStatus.ACTIVE
            
            # Update global metrics
            self._metrics.total_requests += 1
            self._update_global_metrics()
            
            # Record for adaptive strategy
            if self.strategy == LoadBalancingStrategy.ADAPTIVE:
                self._adaptive_window.append({
                    'worker_id': worker_id,
                    'response_time': response_time_ms,
                    'success': success,
                    'timestamp': time.time()
                })
        
        # Notify callbacks
        for callback in self._request_callbacks:
            try:
                callback(worker_id, success, response_time_ms, context)
            except Exception as e:
                logger.warning(f"Request callback error: {e}")
    
    def get_worker_stats(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for a specific worker."""
        with self._worker_lock:
            worker = self._workers.get(worker_id)
            if not worker:
                return None
            
            return {
                'worker_id': worker.worker_id,
                'status': worker.status.value,
                'capacity': worker.capacity,
                'current_load': worker.current_load,
                'utilization': worker.utilization,
                'total_processed': worker.total_processed,
                'total_failed': worker.total_failed,
                'success_rate': worker.success_rate,
                'avg_response_time_ms': worker.avg_response_time_ms,
                'weight': worker.weight,
                'is_healthy': worker.is_healthy,
                'last_health_check': worker.last_health_check,
                'capabilities': worker.metadata.get('capabilities', [])
            }
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get comprehensive load balancer statistics."""
        with self._worker_lock:
            # Update metrics
            self._update_global_metrics()
            
            # Worker statistics
            worker_stats = []
            for worker in self._workers.values():
                worker_stats.append({
                    'id': worker.worker_id,
                    'status': worker.status.value,
                    'utilization': worker.utilization,
                    'success_rate': worker.success_rate,
                    'avg_response_time_ms': worker.avg_response_time_ms
                })
            
            return {
                'strategy': self.strategy.value,
                'metrics': {
                    'total_requests': self._metrics.total_requests,
                    'successful_requests': self._metrics.successful_requests,
                    'failed_requests': self._metrics.failed_requests,
                    'success_rate': self._metrics.success_rate,
                    'avg_response_time_ms': self._metrics.avg_response_time_ms,
                    'requests_per_second': self._metrics.requests_per_second,
                    'total_workers': self._metrics.total_workers,
                    'active_workers': self._metrics.active_workers,
                    'avg_worker_utilization': self._metrics.avg_worker_utilization
                },
                'workers': worker_stats,
                'circuit_breaker_state': self._get_circuit_breaker_summary(),
                'strategy_performance': self._get_strategy_performance()
            }
    
    def start_health_monitoring(self) -> None:
        """Start health monitoring for workers."""
        if self._health_monitor_running:
            return
        
        self._health_monitor_running = True
        self._health_monitor_thread = threading.Thread(
            target=self._health_monitoring_loop,
            daemon=True
        )
        self._health_monitor_thread.start()
        
        logger.info("Load balancer health monitoring started")
    
    def stop_health_monitoring(self) -> None:
        """Stop health monitoring."""
        self._health_monitor_running = False
        if self._health_monitor_thread:
            self._health_monitor_thread.join(timeout=5.0)
        
        logger.info("Load balancer health monitoring stopped")
    
    def add_request_callback(self, callback: Callable) -> None:
        """Add callback for request completion events."""
        self._request_callbacks.append(callback)
    
    def _select_round_robin(self, workers: Dict[str, WorkerNode]) -> str:
        """Round robin selection strategy."""
        worker_ids = list(workers.keys())
        selected_id = worker_ids[self._round_robin_index % len(worker_ids)]
        self._round_robin_index += 1
        return selected_id
    
    def _select_least_connections(self, workers: Dict[str, WorkerNode]) -> str:
        """Least connections selection strategy."""
        return min(workers.keys(), key=lambda wid: workers[wid].current_load)
    
    def _select_weighted_round_robin(self, workers: Dict[str, WorkerNode]) -> str:
        """Weighted round robin selection strategy."""
        # Create weighted list
        weighted_workers = []
        for worker_id, worker in workers.items():
            weight_count = max(1, int(worker.weight * 10))
            weighted_workers.extend([worker_id] * weight_count)
        
        if weighted_workers:
            selected_id = weighted_workers[self._round_robin_index % len(weighted_workers)]
            self._round_robin_index += 1
            return selected_id
        
        return list(workers.keys())[0]
    
    def _select_by_response_time(self, workers: Dict[str, WorkerNode]) -> str:
        """Select worker with best average response time."""
        return min(
            workers.keys(),
            key=lambda wid: workers[wid].avg_response_time_ms or float('inf')
        )
    
    def _select_by_resource_usage(self, workers: Dict[str, WorkerNode]) -> str:
        """Select worker with lowest resource utilization."""
        return min(workers.keys(), key=lambda wid: workers[wid].utilization)
    
    def _select_adaptive(self, workers: Dict[str, WorkerNode], context: Optional[RequestContext]) -> str:
        """Adaptive selection based on historical performance and current context."""
        # If we have context with priority, consider that
        if context and context.priority > 5:  # High priority request
            # Use best performing worker for high priority
            return self._select_by_response_time(workers)
        
        # For normal requests, use a combination of factors
        scores = {}
        for worker_id, worker in workers.items():
            # Combine multiple factors with weights
            response_time_score = 1.0 / (worker.avg_response_time_ms + 1)  # Lower is better
            utilization_score = 1.0 - (worker.utilization / 100.0)  # Lower utilization is better
            success_rate_score = worker.success_rate / 100.0  # Higher is better
            
            # Weighted combination
            composite_score = (
                0.4 * response_time_score +
                0.3 * utilization_score +
                0.3 * success_rate_score
            )
            
            scores[worker_id] = composite_score
        
        # Select worker with highest composite score
        return max(scores.keys(), key=lambda wid: scores[wid])
    
    def _is_circuit_breaker_closed(self, worker_id: str) -> bool:
        """Check if circuit breaker allows requests to this worker."""
        if not self.enable_circuit_breaker:
            return True
        
        circuit_state = self._circuit_breaker_state.get(worker_id, {})
        state = circuit_state.get('state', 'closed')
        
        if state == 'closed':
            return True
        elif state == 'open':
            # Check if enough time has passed to try again
            if time.time() > circuit_state.get('next_attempt', 0):
                circuit_state['state'] = 'half-open'
                return True
            return False
        elif state == 'half-open':
            return True
        
        return False
    
    def _update_circuit_breaker(self, worker_id: str) -> None:
        """Update circuit breaker state after a failure."""
        if not self.enable_circuit_breaker:
            return
        
        circuit_state = self._circuit_breaker_state.setdefault(worker_id, {
            'failures': 0,
            'last_failure': 0,
            'state': 'closed',
            'next_attempt': 0
        })
        
        circuit_state['failures'] += 1
        circuit_state['last_failure'] = time.time()
        
        if (circuit_state['failures'] >= self.circuit_breaker_threshold and 
            circuit_state['state'] == 'closed'):
            # Open circuit breaker
            circuit_state['state'] = 'open'
            circuit_state['next_attempt'] = time.time() + 60.0  # Try again after 1 minute
            
            logger.warning(f"Circuit breaker opened for worker {worker_id}")
    
    def _update_global_metrics(self) -> None:
        """Update global load balancer metrics."""
        if not self._workers:
            return
        
        # Count active workers
        self._metrics.active_workers = sum(
            1 for worker in self._workers.values()
            if worker.status in [WorkerStatus.ACTIVE, WorkerStatus.BUSY, WorkerStatus.IDLE]
        )
        
        # Calculate average utilization
        utilizations = [worker.utilization for worker in self._workers.values()]
        self._metrics.avg_worker_utilization = statistics.mean(utilizations) if utilizations else 0.0
        
        # Calculate average response time
        all_response_times = []
        for worker_times in self._response_times.values():
            all_response_times.extend(worker_times)
        
        if all_response_times:
            self._metrics.avg_response_time_ms = statistics.mean(all_response_times)
        
        # Calculate requests per second (rough estimate)
        if len(self._request_history) > 1:
            time_span = self._request_history[-1] - self._request_history[0]
            if time_span > 0:
                self._metrics.requests_per_second = len(self._request_history) / time_span
    
    def _get_circuit_breaker_summary(self) -> Dict[str, str]:
        """Get summary of circuit breaker states."""
        summary = {}
        for worker_id, state in self._circuit_breaker_state.items():
            summary[worker_id] = state.get('state', 'closed')
        return summary
    
    def _get_strategy_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for different strategies."""
        return {
            strategy.value: metrics
            for strategy, metrics in self._strategy_performance.items()
        }
    
    def _health_monitoring_loop(self) -> None:
        """Health monitoring loop for workers."""
        logger.info("Health monitoring loop started")
        
        while self._health_monitor_running:
            try:
                current_time = time.time()
                
                with self._worker_lock:
                    for worker_id, worker in self._workers.items():
                        # Simple health check based on last update
                        if current_time - worker.last_health_check > 120.0:  # 2 minutes
                            worker.status = WorkerStatus.UNHEALTHY
                            logger.warning(f"Worker {worker_id} marked as unhealthy")
                
                time.sleep(self.health_check_interval)
            
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(self.health_check_interval)
        
        logger.info("Health monitoring loop stopped")


# Global load balancer instance
default_load_balancer = LoadBalancer()