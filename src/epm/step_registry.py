"""
Step Registry

Central registry for all onboarding steps.
Makes it trivial to add, remove, or reorder steps.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional
import logging
from .onboarding_step import OnboardingStep, StepStatus

logger = logging.getLogger(__name__)


class StepRegistry:
    """
    Registry for onboarding steps.
    
    Manages step registration, ordering, and dependency resolution.
    
    Example:
    ```python
    registry = StepRegistry()
    
    # Register steps
    registry.register(EnvironmentDetectionStep())
    registry.register(DependencyInstallationStep())
    registry.register(BrainInitializationStep())
    
    # Get execution order
    steps = registry.get_execution_order(profile="standard")
    
    # Execute steps in order
    for step in steps:
        result = step.execute(context)
    ```
    """
    
    def __init__(self):
        self._steps: Dict[str, OnboardingStep] = {}
        self._execution_order: List[str] = []
        self.logger = logging.getLogger("epm.registry")
    
    def register(self, step: OnboardingStep, position: Optional[int] = None) -> bool:
        """
        Register a step.
        
        Args:
            step: Step instance to register
            position: Optional position in execution order (None = append to end)
        
        Returns:
            True if registration successful, False if step_id conflicts
        """
        try:
            # Check for conflicts
            if step.step_id in self._steps:
                self.logger.warning(
                    f"Step {step.step_id} already registered, skipping"
                )
                return False
            
            # Register step
            self._steps[step.step_id] = step
            
            # Add to execution order
            if position is not None:
                self._execution_order.insert(position, step.step_id)
            else:
                self._execution_order.append(step.step_id)
            
            self.logger.info(f"Registered step: {step.step_id} ({step.name})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register step {step.step_id}: {e}")
            return False
    
    def unregister(self, step_id: str) -> bool:
        """
        Unregister a step.
        
        Args:
            step_id: Step ID to remove
        
        Returns:
            True if removal successful
        """
        if step_id not in self._steps:
            self.logger.warning(f"Step {step_id} not registered")
            return False
        
        # Remove from steps
        del self._steps[step_id]
        
        # Remove from execution order
        self._execution_order.remove(step_id)
        
        self.logger.info(f"Unregistered step: {step_id}")
        return True
    
    def get_step(self, step_id: str) -> Optional[OnboardingStep]:
        """Get step by ID"""
        return self._steps.get(step_id)
    
    def get_all_steps(self) -> List[OnboardingStep]:
        """Get all registered steps in execution order"""
        return [self._steps[sid] for sid in self._execution_order if sid in self._steps]
    
    def get_execution_order(
        self,
        profile: str = "standard",
        skip_completed: bool = False
    ) -> List[OnboardingStep]:
        """
        Get steps in execution order for a profile.
        
        Args:
            profile: Profile to filter for ("quick", "standard", "comprehensive")
            skip_completed: Whether to skip already-completed steps
        
        Returns:
            List of steps to execute, in dependency-resolved order
        """
        steps = []
        
        for step_id in self._execution_order:
            step = self._steps.get(step_id)
            
            if not step:
                continue
            
            # Check if step is required for profile
            if profile not in step.required_for_profiles:
                continue
            
            # Skip completed steps if requested
            if skip_completed and step.status == StepStatus.COMPLETED:
                continue
            
            steps.append(step)
        
        # Resolve dependencies (topological sort)
        return self._resolve_dependencies(steps)
    
    def _resolve_dependencies(
        self,
        steps: List[OnboardingStep]
    ) -> List[OnboardingStep]:
        """
        Resolve step dependencies using topological sort.
        
        Args:
            steps: List of steps to sort
        
        Returns:
            Steps in dependency-resolved order
        """
        # Build dependency graph
        step_map = {step.step_id: step for step in steps}
        in_degree = {step.step_id: 0 for step in steps}
        adjacency = {step.step_id: [] for step in steps}
        
        for step in steps:
            for dep_id in step.dependencies:
                if dep_id in step_map:
                    adjacency[dep_id].append(step.step_id)
                    in_degree[step.step_id] += 1
        
        # Topological sort (Kahn's algorithm)
        queue = [sid for sid in in_degree if in_degree[sid] == 0]
        sorted_ids = []
        
        while queue:
            current_id = queue.pop(0)
            sorted_ids.append(current_id)
            
            for neighbor_id in adjacency[current_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)
        
        # Check for cycles
        if len(sorted_ids) != len(steps):
            self.logger.error("Circular dependency detected in steps")
            return steps  # Return original order if cycle detected
        
        # Return sorted steps
        return [step_map[sid] for sid in sorted_ids]
    
    def reset_all(self) -> None:
        """Reset all steps to PENDING status"""
        for step in self._steps.values():
            step.reset()
    
    def get_stats(self) -> Dict[str, any]:
        """Get registry statistics"""
        total = len(self._steps)
        by_status = {status: 0 for status in StepStatus}
        
        for step in self._steps.values():
            by_status[step.status] += 1
        
        return {
            "total_steps": total,
            "pending": by_status[StepStatus.PENDING],
            "running": by_status[StepStatus.RUNNING],
            "completed": by_status[StepStatus.COMPLETED],
            "failed": by_status[StepStatus.FAILED],
            "skipped": by_status[StepStatus.SKIPPED]
        }
