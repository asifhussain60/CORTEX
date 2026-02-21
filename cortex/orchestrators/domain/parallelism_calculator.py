"""
Parallelism Calculator

Calculates parallel execution levels for phases based on dependency graph.
Groups independent phases into execution levels that can run concurrently.

Authority: Wave 8 Stage 3
"""

from dataclasses import dataclass
from typing import Dict, List, Set
from cortex.orchestrators.domain.dependency_resolver import (
    DependencyGraph,
    DependencyResolver,
)


@dataclass
class ExecutionLevel:
    """A level of phases that can execute in parallel"""
    level_number: int
    phases: List[str]
    max_parallelism: int  # Maximum number of phases in this level
    
    def __post_init__(self):
        """Validate level"""
        if self.level_number < 0:
            raise ValueError(f"Level number must be >= 0, got {self.level_number}")
        
        if not self.phases:
            raise ValueError("ExecutionLevel must have at least one phase")
        
        if self.max_parallelism < 1:
            raise ValueError(f"max_parallelism must be >= 1, got {self.max_parallelism}")
        
        # max_parallelism should equal or exceed number of phases
        if self.max_parallelism < len(self.phases):
            self.max_parallelism = len(self.phases)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "level_number": self.level_number,
            "phases": self.phases,
            "max_parallelism": self.max_parallelism,
        }


@dataclass
class ParallelExecutionPlan:
    """Complete parallel execution plan"""
    levels: List[ExecutionLevel]
    total_phases: int
    total_levels: int
    max_parallelism: int  # Maximum parallelism across all levels
    sequential_equivalent: int  # Total phases if run sequentially
    
    @property
    def speedup_potential(self) -> float:
        """
        Calculate theoretical speedup from parallelization.
        
        Returns:
            Ratio of sequential to parallel execution (e.g., 2.0 = 2x faster)
        """
        if self.total_levels == 0:
            return 1.0
        return self.sequential_equivalent / self.total_levels
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "levels": [level.to_dict() for level in self.levels],
            "total_phases": self.total_phases,
            "total_levels": self.total_levels,
            "max_parallelism": self.max_parallelism,
            "sequential_equivalent": self.sequential_equivalent,
            "speedup_potential": self.speedup_potential,
        }


class ParallelismCalculator:
    """
    Calculate parallel execution levels from dependency graph.
    
    Groups phases into execution levels where all phases in a level
    can run concurrently (no dependencies between them).
    
    Example:
        >>> graph = DependencyGraph.from_dict({
        ...     "A": [],
        ...     "B": [],
        ...     "C": ["A"],
        ...     "D": ["A"],
        ...     "E": ["B", "C"],
        ... })
        >>> calculator = ParallelismCalculator()
        >>> plan = calculator.calculate(graph)
        >>> for level in plan.levels:
        ...     print(f"Level {level.level_number}: {level.phases}")
        Level 0: ['A', 'B']
        Level 1: ['C', 'D']
        Level 2: ['E']
        >>> print(f"Speedup: {plan.speedup_potential:.2f}x")
        Speedup: 1.67x
    """
    
    def __init__(self) -> None:
        """Initialize calculator with resolver"""
        self.resolver = DependencyResolver()
    
    def calculate(self, graph: DependencyGraph) -> ParallelExecutionPlan:
        """
        Calculate parallel execution plan.
        
        Args:
            graph: Dependency graph
        
        Returns:
            ParallelExecutionPlan with execution levels
        
        Raises:
            ValueError: If graph has circular dependencies or missing phases
        """
        # First resolve to check for errors
        resolution = self.resolver.resolve(graph)
        
        if not resolution.is_success:
            if resolution.circular_path:
                raise ValueError(
                    f"Circular dependency detected: {' → '.join(resolution.circular_path)}"
                )
            if resolution.missing_dependencies:
                missing_str = ", ".join(
                    f"{phase}: {deps}" 
                    for phase, deps in resolution.missing_dependencies.items()
                )
                raise ValueError(f"Missing dependencies: {missing_str}")
        
        # Calculate execution levels
        levels = self._compute_execution_levels(graph)
        
        # Calculate statistics
        total_phases = len(graph.phases)
        total_levels = len(levels)
        max_parallelism = max(len(level.phases) for level in levels) if levels else 0
        
        return ParallelExecutionPlan(
            levels=levels,
            total_phases=total_phases,
            total_levels=total_levels,
            max_parallelism=max_parallelism,
            sequential_equivalent=total_phases,
        )
    
    def _compute_execution_levels(self, graph: DependencyGraph) -> List[ExecutionLevel]:
        """
        Compute execution levels using modified BFS.
        
        Args:
            graph: Dependency graph
        
        Returns:
            List of ExecutionLevel objects in order
        """
        # Calculate in-degrees (number of dependencies)
        in_degree = {phase: 0 for phase in graph.phases}
        
        for phase_id, deps in graph.dependencies.items():
            in_degree[phase_id] = len(deps)
        
        # Group phases by level
        levels: List[List[str]] = []
        processed = set()
        
        while len(processed) < len(graph.phases):
            # Find all phases that can execute now (dependencies satisfied)
            current_level = []
            
            for phase_id in graph.phases:
                if phase_id in processed:
                    continue
                
                # Check if all dependencies are processed
                deps = graph.dependencies.get(phase_id, set())
                if all(dep in processed for dep in deps):
                    current_level.append(phase_id)
            
            if not current_level:
                # Should not happen if graph is valid (no cycles)
                break
            
            # Sort for deterministic ordering
            current_level.sort()
            levels.append(current_level)
            processed.update(current_level)
        
        # Convert to ExecutionLevel objects
        execution_levels = []
        for level_num, phases in enumerate(levels):
            execution_levels.append(
                ExecutionLevel(
                    level_number=level_num,
                    phases=phases,
                    max_parallelism=len(phases),
                )
            )
        
        return execution_levels
    
    def estimate_execution_time(
        self,
        plan: ParallelExecutionPlan,
        phase_durations: Dict[str, float],
        overhead_per_level: float = 0.0,
    ) -> float:
        """
        Estimate total execution time with parallel execution.
        
        Args:
            plan: Parallel execution plan
            phase_durations: Dictionary of phase_id → duration (hours)
            overhead_per_level: Coordination overhead per level (hours)
        
        Returns:
            Estimated total execution time in hours
        """
        total_time = 0.0
        
        for level in plan.levels:
            # Time for this level = max duration of any phase in level
            level_time = max(
                phase_durations.get(phase, 0.0) for phase in level.phases
            )
            total_time += level_time + overhead_per_level
        
        return total_time
    
    def compare_sequential_vs_parallel(
        self,
        plan: ParallelExecutionPlan,
        phase_durations: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Compare sequential vs parallel execution times.
        
        Args:
            plan: Parallel execution plan
            phase_durations: Dictionary of phase_id → duration (hours)
        
        Returns:
            Dictionary with sequential_time, parallel_time, speedup
        """
        # Sequential: sum of all phase durations
        sequential_time = sum(phase_durations.values())
        
        # Parallel: max duration per level
        parallel_time = self.estimate_execution_time(plan, phase_durations)
        
        speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0
        
        return {
            "sequential_time": sequential_time,
            "parallel_time": parallel_time,
            "speedup": speedup,
            "time_saved": sequential_time - parallel_time,
        }
