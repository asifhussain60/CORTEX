"""Orchestrator Routing Engine for adaptive task-to-orchestrator selection.

This module implements intelligent routing of tasks to appropriate orchestrators
based on execution context analysis. It supports both single orchestrator
selection and multi-orchestrator composition routing.

AC-EX-001-02: Routing considers task type and complexity, multiple
orchestrators can be selected for composition, and routing decisions are logged.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from cortex.orchestrators.adaptive.execution_context_analyzer import (
    ExecutionContext,
    ExecutionContextAnalyzer,
)


@dataclass
class RoutingDecision:
    """Represents a routing decision with metadata.
    
    Attributes:
        timestamp: When the decision was made
        task_type: Type of task routed
        complexity: Complexity score of the task
        selected_orchestrator: Primary orchestrator selected
        composed_orchestrators: Orchestrators selected for composition (if any)
        reasoning: Explanation for the selection
        resource_profile: Resource requirements that influenced selection
    """
    
    timestamp: datetime
    task_type: str
    complexity: float
    selected_orchestrator: str
    composed_orchestrators: Optional[List[str]] = None
    reasoning: str = ""
    resource_profile: Optional[Dict[str, Any]] = None


class OrchestratorRoutingEngine:
    """Routes tasks to appropriate orchestrators based on context.
    
    This engine analyzes execution contexts and determines which orchestrator(s)
    should handle the task. It supports:
    - Single orchestrator selection for simple tasks
    - Multi-orchestrator composition for complex tasks
    - Routing decision logging for analysis and optimization
    - Capability-aware matching
    
    Example:
        >>> engine = OrchestratorRoutingEngine()
        >>> context = engine._analyzer.analyze_context(
        ...     task_type="planning",
        ...     task_input={"ac_ids": ["AC-001-01"]}
        ... )
        >>> primary = engine.select_orchestrator(context)
        >>> print(f"Selected: {primary}")
    """
    
    def __init__(self) -> None:
        """Initialize the routing engine with context analyzer and decision log."""
        self._analyzer = ExecutionContextAnalyzer()
        self._decision_log: List[Dict[str, Any]] = []
        
        # Orchestrator selection heuristics
        self._task_orchestrator_map: Dict[str, List[str]] = {
            "simple_query": ["PlanningOrchestrator"],
            "simple_command": ["PlanningOrchestrator"],
            "analysis": ["PlanningOrchestrator"],
            "planning": ["PlanningOrchestrator"],
            "generation": ["PlanningOrchestrator"],
            "complex_orchestration": ["MasterOrchestrator"],
            "governance_check": ["PlanningOrchestrator"],
        }
    
    def select_orchestrator(self, context: ExecutionContext) -> str:
        """Select a single primary orchestrator for task execution.
        
        Uses execution context to determine the best orchestrator to handle
        the task. Selection considers:
        - Task type
        - Complexity score
        - Resource requirements
        - Required capabilities
        - Priority
        
        Args:
            context: ExecutionContext with task characteristics
            
        Returns:
            Name of selected orchestrator
            
        Raises:
            ValueError: If no suitable orchestrator found
        """
        # Get candidate orchestrators for task type
        candidates = self._get_candidate_orchestrators(context)
        
        # Filter by capability match
        capable_candidates = [
            orch for orch in candidates
            if self._analyzer.can_orchestrator_handle_task(orch, context)
        ]
        
        # If no perfect match, try all known orchestrators
        if not capable_candidates:
            all_orchs = list(self._analyzer._capability_registry.keys())
            capable_candidates = [
                orch for orch in all_orchs
                if self._analyzer.can_orchestrator_handle_task(orch, context)
            ]
        
        # If still no match, use highest-capability orchestrator
        if not capable_candidates:
            capable_candidates = ["MasterOrchestrator"]
        
        # Select best candidate based on complexity
        selected = self._select_best_orchestrator(
            capable_candidates,
            context,
        )
        
        # Log the decision
        self._log_routing_decision(context, selected, None)
        
        return selected
    
    def select_orchestrators_for_composition(
        self,
        context: ExecutionContext,
    ) -> List[str]:
        """Select multiple orchestrators for task composition.
        
        For complex tasks, this method selects multiple orchestrators that
        together can handle the task. The composition strategy depends on:
        - Task complexity
        - Required capabilities
        - Resource availability
        
        Args:
            context: ExecutionContext with task characteristics
            
        Returns:
            List of orchestrator names for composition
        """
        # Get primary orchestrator
        primary = self.select_orchestrator(context)
        
        composed = [primary]
        
        # For high-complexity tasks, add complementary orchestrators
        if context.complexity_score > 0.67:
            # Add orchestrator with different strengths
            all_orchs = list(self._analyzer._capability_registry.keys())
            
            for orch in all_orchs:
                if orch not in composed:
                    # Check for complementary capabilities
                    if self._are_capabilities_complementary(
                        primary,
                        orch,
                        context,
                    ):
                        composed.append(orch)
                        if len(composed) >= 3:  # Limit composition
                            break
        
        # Log composition decision
        self._log_routing_decision(context, primary, composed)
        
        return composed
    
    def get_routing_with_composition_info(
        self,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        """Get routing decision with detailed composition information.
        
        Args:
            context: ExecutionContext to route
            
        Returns:
            Dictionary with routing decision and composition info
        """
        primary = self.select_orchestrator(context)
        composed = self.select_orchestrators_for_composition(context)
        
        return {
            "primary": primary,
            "orchestrators": composed,
            "complexity": context.complexity_score,
            "task_type": context.task_type,
            "resources": context.resource_requirements,
            "capabilities_required": list(context.required_capabilities),
        }
    
    def get_routing_history(
        self,
        task_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get routing decision history, optionally filtered by task type.
        
        Args:
            task_type: Optional filter for specific task type
            
        Returns:
            List of routing decisions (most recent first)
        """
        if task_type is None:
            return list(reversed(self._decision_log))
        
        filtered = [
            d for d in self._decision_log
            if d.get("task_type") == task_type
        ]
        return list(reversed(filtered))
    
    def _get_candidate_orchestrators(
        self,
        context: ExecutionContext,
    ) -> List[str]:
        """Get candidate orchestrators for task type.
        
        Args:
            context: ExecutionContext
            
        Returns:
            List of orchestrator names to consider
        """
        # Check task-specific map first
        candidates = self._task_orchestrator_map.get(
            context.task_type,
            list(self._analyzer._capability_registry.keys()),
        )
        
        return candidates if candidates else list(
            self._analyzer._capability_registry.keys()
        )
    
    def _select_best_orchestrator(
        self,
        candidates: List[str],
        context: ExecutionContext,
    ) -> str:
        """Select best orchestrator from candidates.
        
        Selection criteria:
        - Capability match (must have all required capabilities)
        - Complexity suitability
        - Priority accommodation
        
        Args:
            candidates: List of candidate orchestrator names
            context: ExecutionContext
            
        Returns:
            Selected orchestrator name
        """
        if not candidates:
            return "MasterOrchestrator"
        
        if len(candidates) == 1:
            return candidates[0]
        
        # For simple tasks, prefer simpler orchestrators
        if context.complexity_score < 0.33:
            return candidates[0] if candidates else "PlanningOrchestrator"
        
        # For critical priority, prefer master orchestrator
        if context.priority == "CRITICAL":
            if "MasterOrchestrator" in candidates:
                return "MasterOrchestrator"
        
        # Default to first capable candidate
        return candidates[0]
    
    def _are_capabilities_complementary(
        self,
        orch1: str,
        orch2: str,
        context: ExecutionContext,
    ) -> bool:
        """Check if two orchestrators have complementary capabilities.
        
        Args:
            orch1: First orchestrator name
            orch2: Second orchestrator name
            context: ExecutionContext
            
        Returns:
            True if capabilities are complementary
        """
        caps1 = self._analyzer.get_orchestrator_capabilities(orch1)
        caps2 = self._analyzer.get_orchestrator_capabilities(orch2)
        
        # Complementary if each has some unique capabilities
        unique_in_1 = caps1 - caps2
        unique_in_2 = caps2 - caps1
        
        return len(unique_in_1) > 0 and len(unique_in_2) > 0
    
    def _log_routing_decision(
        self,
        context: ExecutionContext,
        primary: str,
        composed: Optional[List[str]],
    ) -> None:
        """Log a routing decision for analysis.
        
        Args:
            context: ExecutionContext routed
            primary: Primary orchestrator selected
            composed: Composed orchestrators if any
        """
        decision = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_type": context.task_type,
            "complexity": context.complexity_score,
            "complexity_level": self._analyzer.get_complexity_level(
                context.complexity_score
            ),
            "selected_orchestrator": primary,
            "composed_orchestrators": composed,
            "resources": context.resource_requirements,
            "priority": context.priority,
            "capabilities_required": list(context.required_capabilities),
        }
        
        self._decision_log.append(decision)
