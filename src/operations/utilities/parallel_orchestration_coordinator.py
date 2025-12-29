"""
Parallel Orchestration Coordinator

Enables concurrent execution of independent orchestration phases with:
- DAG-based dependency resolution
- Resource locking for concurrent safety
- Error isolation to prevent cascade failures
- Performance optimization (2-3x speedup for independent phases)

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable, Any
from collections import defaultdict, deque

try:
    import networkx as nx
except ImportError:
    nx = None

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPTIONS
# ============================================================================

class DependencyError(Exception):
    """Raised when dependency resolution fails (e.g., circular dependencies)."""
    pass


class ResourceLockError(Exception):
    """Raised when resource locking fails or times out."""
    pass


# ============================================================================
# PHASE DEFINITION
# ============================================================================

@dataclass
class PhaseDefinition:
    """
    Defines a phase for parallel orchestration.
    
    Attributes:
        phase_id: Unique identifier for the phase
        phase_func: Async function to execute for this phase
        dependencies: List of phase_ids that must complete before this phase
        resources: List of resource names this phase requires (for locking)
        timeout: Maximum execution time in seconds (None = no timeout)
        metadata: Additional metadata for the phase
    """
    phase_id: str
    phase_func: Callable
    dependencies: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# PARALLEL ORCHESTRATION COORDINATOR
# ============================================================================

class ParallelOrchestrationCoordinator:
    """
    Coordinates parallel execution of orchestration phases with dependency
    resolution, resource locking, and error isolation.
    
    Features:
    - Async parallel execution using asyncio.gather()
    - DAG-based dependency resolution with topological sort
    - Resource-level locking for concurrent safety
    - Error isolation (one phase failure doesn't cascade)
    - Performance optimization (2-3x speedup for independent phases)
    
    Usage:
        coordinator = ParallelOrchestrationCoordinator()
        
        phases = [
            PhaseDefinition(
                phase_id="phase1",
                phase_func=async_function1,
                dependencies=[],
                resources=["file_a"]
            ),
            PhaseDefinition(
                phase_id="phase2",
                phase_func=async_function2,
                dependencies=["phase1"],
                resources=["file_b"]
            )
        ]
        
        results = await coordinator.execute_parallel_phases(phases)
    """
    
    def __init__(self):
        """Initialize the parallel orchestration coordinator."""
        self._resource_locks: Dict[str, asyncio.Lock] = {}
        self._lock_acquisition_lock = asyncio.Lock()
        logger.info("ParallelOrchestrationCoordinator initialized")
    
    async def execute_parallel_phases(
        self,
        phases: List[PhaseDefinition],
        max_concurrent: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute phases in parallel with dependency resolution.
        
        Args:
            phases: List of PhaseDefinition objects to execute
            max_concurrent: Maximum number of concurrent phases (None = unlimited)
        
        Returns:
            Dictionary mapping phase_id to result or error
            For success: {phase_id: <result_value>}
            For error: {phase_id: {"error": <error_message>}}
            For skipped: {phase_id: {"status": "skipped", "reason": <reason>}}
        
        Raises:
            DependencyError: If dependency graph has circular dependencies
        """
        start_time = time.time()
        logger.info(f"🎭 Executing {len(phases)} phases in parallel")
        
        # Handle empty phase list
        if not phases:
            return {}
        
        # Build dependency graph
        graph = self._build_dependency_graph(phases)
        
        # Detect circular dependencies
        if self._detect_circular_dependencies(graph):
            raise DependencyError("Circular dependency detected in phase graph")
        
        # Get execution order (topological sort)
        execution_order = self._topological_sort(graph)
        logger.info(f"Execution order: {execution_order}")
        
        # Create phase lookup
        phase_map = {p.phase_id: p for p in phases}
        
        # Track results and completion
        results: Dict[str, Any] = {}
        completed_phases: Set[str] = set()
        failed_phases: Set[str] = set()
        
        # Execute phases in batches (respecting dependencies)
        while len(completed_phases) < len(phases):
            # Find phases ready to execute
            ready_phases = []
            for phase_id in execution_order:
                if phase_id in completed_phases:
                    continue
                
                phase_deps = phase_map[phase_id].dependencies
                
                # Check if any dependency failed
                if any(dep in failed_phases for dep in phase_deps):
                    # Skip this phase
                    results[phase_id] = {
                        "status": "skipped",
                        "reason": "Dependency failed"
                    }
                    completed_phases.add(phase_id)
                    logger.info(f"Phase {phase_id} skipped due to failed dependency")
                    continue
                
                # Check if all dependencies completed successfully
                if all(dep in completed_phases for dep in phase_deps):
                    ready_phases.append(phase_id)
            
            if not ready_phases:
                # No phases ready but not all completed = deadlock
                pending = set(execution_order) - completed_phases
                if pending:
                    raise DependencyError(f"Deadlock detected. Pending phases: {pending}")
                break
            
            # Limit concurrent execution if specified
            if max_concurrent:
                ready_phases = ready_phases[:max_concurrent]
            
            logger.info(f"Executing batch: {ready_phases}")
            
            # Execute ready phases in parallel
            tasks = [
                self._execute_phase_with_locks(phase_map[phase_id])
                for phase_id in ready_phases
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for phase_id, result in zip(ready_phases, batch_results):
                if isinstance(result, Exception):
                    results[phase_id] = {
                        "error": str(result)
                    }
                    failed_phases.add(phase_id)
                    logger.error(f"Phase {phase_id} failed: {result}")
                else:
                    results[phase_id] = result
                    logger.info(f"Phase {phase_id} completed successfully")
                
                completed_phases.add(phase_id)
        
        duration = time.time() - start_time
        success_count = len(completed_phases) - len(failed_phases)
        logger.info(
            f"✅ Parallel execution complete: {success_count}/{len(phases)} "
            f"successful in {duration:.2f}s"
        )
        
        return results
    
    async def _execute_phase_with_locks(self, phase: PhaseDefinition) -> Any:
        """
        Execute a single phase with resource locking.
        
        Args:
            phase: PhaseDefinition to execute
        
        Returns:
            Result from phase execution
        
        Raises:
            ResourceLockError: If resource lock acquisition fails
            asyncio.TimeoutError: If phase execution times out
        """
        # Acquire resource locks
        acquired_locks = []
        try:
            for resource in phase.resources:
                lock = await self._get_resource_lock(resource)
                await asyncio.wait_for(lock.acquire(), timeout=5.0)
                acquired_locks.append(lock)
                logger.debug(f"Phase {phase.phase_id} acquired lock on {resource}")
            
            # Execute phase with optional timeout
            if phase.timeout:
                result = await asyncio.wait_for(
                    phase.phase_func(),
                    timeout=phase.timeout
                )
            else:
                result = await phase.phase_func()
            
            return result
        
        except asyncio.TimeoutError as e:
            logger.error(f"Phase {phase.phase_id} timed out")
            raise
        
        except Exception as e:
            logger.error(f"Phase {phase.phase_id} failed: {e}")
            raise
        
        finally:
            # Release all acquired locks
            for lock in acquired_locks:
                lock.release()
                logger.debug(f"Phase {phase.phase_id} released lock")
    
    async def _get_resource_lock(self, resource: str) -> asyncio.Lock:
        """
        Get or create a lock for a resource.
        
        Args:
            resource: Resource name
        
        Returns:
            asyncio.Lock for the resource
        """
        async with self._lock_acquisition_lock:
            if resource not in self._resource_locks:
                self._resource_locks[resource] = asyncio.Lock()
            return self._resource_locks[resource]
    
    def acquire_resource_lock(self, resource: str):
        """
        Context manager for acquiring resource locks (async context manager).
        
        Usage:
            async with coordinator.acquire_resource_lock("file_a"):
                # ... do work with file_a
        
        Args:
            resource: Resource name to lock
        
        Returns:
            Async context manager for the resource lock
        """
        class ResourceLockContext:
            def __init__(self, coordinator, resource):
                self.coordinator = coordinator
                self.resource = resource
                self.lock = None
            
            async def __aenter__(self):
                self.lock = await self.coordinator._get_resource_lock(self.resource)
                await self.lock.acquire()
                return self.lock
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self.lock:
                    self.lock.release()
                return False
        
        return ResourceLockContext(self, resource)
    
    def _build_dependency_graph(self, phases: List[PhaseDefinition]) -> Dict[str, Set[str]]:
        """
        Build dependency graph from phases.
        
        Args:
            phases: List of PhaseDefinition objects
        
        Returns:
            Adjacency list representation: {phase_id: {dependent_phase_ids}}
        """
        graph = defaultdict(set)
        phase_ids = {p.phase_id for p in phases}
        
        for phase in phases:
            # Validate dependencies exist
            for dep in phase.dependencies:
                if dep not in phase_ids:
                    raise DependencyError(
                        f"Unknown dependency: Phase {phase.phase_id} depends on non-existent phase {dep}"
                    )
            
            # Build graph (reverse direction: dep -> phase)
            for dep in phase.dependencies:
                graph[dep].add(phase.phase_id)
            
            # Ensure phase exists in graph even if no dependencies
            if phase.phase_id not in graph:
                graph[phase.phase_id] = set()
        
        return graph
    
    def _detect_circular_dependencies(self, graph: Dict[str, Set[str]]) -> bool:
        """
        Detect circular dependencies using DFS with cycle detection.
        
        Args:
            graph: Adjacency list representation
        
        Returns:
            True if circular dependency detected, False otherwise
        """
        # Use networkx if available (more robust)
        if nx is not None:
            try:
                G = nx.DiGraph()
                for node, neighbors in graph.items():
                    for neighbor in neighbors:
                        G.add_edge(node, neighbor)
                
                # Find cycles
                try:
                    cycles = list(nx.simple_cycles(G))
                    if cycles:
                        logger.error(f"Circular dependencies detected: {cycles}")
                        return True
                    return False
                except nx.NetworkXNoCycle:
                    return False
            except Exception as e:
                logger.warning(f"networkx cycle detection failed: {e}, using fallback")
        
        # Fallback: Manual DFS cycle detection
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in graph}
        
        def has_cycle_dfs(node):
            color[node] = GRAY
            for neighbor in graph[node]:
                if color[neighbor] == GRAY:
                    return True
                if color[neighbor] == WHITE and has_cycle_dfs(neighbor):
                    return True
            color[node] = BLACK
            return False
        
        for node in graph:
            if color[node] == WHITE:
                if has_cycle_dfs(node):
                    return True
        
        return False
    
    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """
        Perform topological sort on dependency graph using Kahn's algorithm.
        
        Args:
            graph: Adjacency list representation
        
        Returns:
            List of phase_ids in execution order
        
        Raises:
            DependencyError: If graph has circular dependencies
        """
        # Calculate in-degrees (reverse the graph direction)
        in_degree = {node: 0 for node in graph}
        reverse_graph = defaultdict(set)
        
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                reverse_graph[neighbor].add(node)
                in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
        
        # Start with nodes that have no dependencies
        queue = deque([node for node in graph if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # Remove edges from this node
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If result doesn't contain all nodes, there's a cycle
        if len(result) != len(graph):
            raise DependencyError("Topological sort failed - circular dependencies detected")
        
        return result
