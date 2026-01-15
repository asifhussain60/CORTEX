"""Orchestrator Selection & Routing Engine for adaptive execution.

This module implements the RoutingEngine which routes tasks to appropriate
orchestrators based on execution context analysis.

AC-EX-001-02: Routing considers task type and complexity, multiple orchestrators
can be selected for composition, and routing decisions are logged for analysis.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RoutingDecision:
    """Represents a routing decision for a task.
    
    Attributes:
        primary_orchestrator: Primary orchestrator to handle the task
        fallback_orchestrators: Fallback orchestrators if primary fails
        composition_orchestrators: Orchestrators for composition (if needed)
        reason: Human-readable reason for the routing decision
        confidence_score: Confidence in this routing (0.0-1.0)
        optimization_hints: Optional hints for execution optimization
    """
    
    primary_orchestrator: str
    fallback_orchestrators: List[str]
    composition_orchestrators: List[str]
    reason: str
    confidence_score: float
    optimization_hints: Optional[Dict[str, Any]] = field(default=None)
    
    def __post_init__(self) -> None:
        """Validate routing decision after initialization.
        
        Raises:
            ValueError: If validation fails
        """
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        if not self.primary_orchestrator:
            raise ValueError("primary_orchestrator cannot be empty")
        if not self.reason:
            raise ValueError("reason cannot be empty")


class RoutingEngine:
    """Routes tasks to appropriate orchestrators based on execution context.
    
    The routing engine:
    - Analyzes task characteristics through ExecutionContextAnalyzer
    - Selects primary orchestrator based on capabilities and complexity
    - Identifies fallback orchestrators for resilience
    - Determines if composition is needed for complex tasks
    - Logs all routing decisions for analysis and optimization
    
    Routing Strategy:
    - Low complexity tasks → Simple orchestrators
    - Medium complexity → General purpose orchestrators
    - High complexity → Specialized domain orchestrators + composition
    - Unknown tasks → Fall back to MasterOrchestrator
    
    Example:
        >>> engine = RoutingEngine()
        >>> context = analyzer.analyze_context("planning", {...})
        >>> decision = engine.route_task("planning", context)
        >>> print(f"Route to: {decision.primary_orchestrator}")
    """
    
    def __init__(self) -> None:
        """Initialize the RoutingEngine.
        
        Sets up orchestrator profiles and routing rules.
        """
        self._orchestrator_profiles: Dict[str, Dict[str, Any]] = {
            "PlanningOrchestrator": {
                "capabilities": {"planning", "analysis", "parsing"},
                "max_complexity": 0.7,
                "strengths": ["planning", "analysis"],
                "weaknesses": ["orchestration", "delegation"],
                "resilience_level": "medium",
            },
            "MasterOrchestrator": {
                "capabilities": {"orchestration", "delegation", "composition"},
                "max_complexity": 1.0,
                "strengths": ["orchestration", "delegation", "composition"],
                "weaknesses": [],
                "resilience_level": "high",
            },
        }
        
        self._routing_log: List[Dict[str, Any]] = []
        self._routing_statistics = {
            "total_decisions": 0,
            "by_orchestrator": {},
            "by_complexity": {},
        }
    
    def route_task(
        self,
        task_type: str,
        context: Any,  # ExecutionContext
        preferences: Optional[Dict[str, Any]] = None,
    ) -> RoutingDecision:
        """Route a task to appropriate orchestrator(s).
        
        Analyzes the execution context and determines optimal routing,
        considering task type, complexity, capabilities, and fallback
        options for resilience.
        
        Args:
            task_type: Type of task
            context: ExecutionContext from analyzer
            preferences: Optional routing preferences (preferred_orchestrator, etc.)
            
        Returns:
            RoutingDecision with primary, fallback, and composition choices
            
        Raises:
            ValueError: If routing cannot be determined
        """
        if not task_type:
            raise ValueError("task_type cannot be empty")
        if context is None:
            raise ValueError("context cannot be None")
        
        if preferences is None:
            preferences = {}
        
        # Determine primary orchestrator
        primary = self._select_primary_orchestrator(context, preferences)
        
        # Determine fallback orchestrators
        fallbacks = self._select_fallback_orchestrators(primary, context)
        
        # Determine if composition is needed
        composition = self._determine_composition(context)
        
        # Generate routing reason
        reason = self._generate_routing_reason(
            primary, context, fallbacks, composition
        )
        
        # Calculate confidence
        confidence = self._calculate_routing_confidence(primary, context, composition)
        
        # Create routing decision
        decision = RoutingDecision(
            primary_orchestrator=primary,
            fallback_orchestrators=fallbacks,
            composition_orchestrators=composition,
            reason=reason,
            confidence_score=confidence,
            optimization_hints=preferences.get("hints"),
        )
        
        # Log the decision
        self._log_routing_decision(task_type, context, decision)
        
        return decision
    
    def _select_primary_orchestrator(
        self,
        context: Any,
        preferences: Dict[str, Any],
    ) -> str:
        """Select the primary orchestrator for a task.
        
        Args:
            context: ExecutionContext
            preferences: Routing preferences
            
        Returns:
            Primary orchestrator name
        """
        # Check for explicit preference
        if "preferred_orchestrator" in preferences:
            preferred = preferences["preferred_orchestrator"]
            if preferred in self._orchestrator_profiles:
                return preferred
        
        # Find orchestrators that can handle the task
        candidates = []
        for orch_name, profile in self._orchestrator_profiles.items():
            required_caps = context.required_capabilities
            orchestrator_caps = set(profile["capabilities"])
            
            if required_caps.issubset(orchestrator_caps):
                # Check if complexity is within limits
                if context.complexity_score <= profile["max_complexity"]:
                    candidates.append((orch_name, profile))
        
        if not candidates:
            # Fall back to MasterOrchestrator as universal handler
            return "MasterOrchestrator"
        
        # Select candidate with best complexity match (prefer exact matches)
        best = min(candidates, key=lambda x: abs(x[1]["max_complexity"] - context.complexity_score))
        return best[0]
    
    def _select_fallback_orchestrators(
        self,
        primary: str,
        context: Any,
    ) -> List[str]:
        """Select fallback orchestrators for resilience.
        
        Args:
            primary: Primary orchestrator
            context: ExecutionContext
            
        Returns:
            List of fallback orchestrator names
        """
        fallbacks = []
        
        for orch_name, profile in self._orchestrator_profiles.items():
            if orch_name == primary:
                continue
            
            # Check if orchestrator can handle task
            required_caps = context.required_capabilities
            orchestrator_caps = set(profile["capabilities"])
            
            if required_caps.issubset(orchestrator_caps):
                if context.complexity_score <= profile["max_complexity"]:
                    fallbacks.append(orch_name)
        
        # Ensure MasterOrchestrator is always a fallback if not primary
        if primary != "MasterOrchestrator" and "MasterOrchestrator" not in fallbacks:
            fallbacks.append("MasterOrchestrator")
        
        return fallbacks
    
    def _determine_composition(self, context: Any) -> List[str]:
        """Determine if task composition is needed.
        
        High-complexity tasks with multiple capability requirements benefit
        from composition, where multiple orchestrators work together.
        
        Args:
            context: ExecutionContext
            
        Returns:
            List of orchestrators for composition (empty if not needed)
        """
        # Composition needed for high-complexity tasks with multiple capability requirements
        if context.complexity_score >= 0.7 and len(context.required_capabilities) > 2:
            # Return orchestrators for composition
            return ["PlanningOrchestrator", "MasterOrchestrator"]
        
        return []
    
    def _generate_routing_reason(
        self,
        primary: str,
        context: Any,
        fallbacks: List[str],
        composition: List[str],
    ) -> str:
        """Generate human-readable routing reason.
        
        Args:
            primary: Primary orchestrator
            context: ExecutionContext
            fallbacks: Fallback orchestrators
            composition: Composition orchestrators
            
        Returns:
            Routing reason string
        """
        complexity_level = self._get_complexity_level(context.complexity_score)
        reason = f"Selected {primary} for {complexity_level} complexity task"
        
        if fallbacks:
            reason += f" (fallback: {', '.join(fallbacks)})"
        
        if composition:
            reason += f" with composition"
        
        return reason + f" - requires: {', '.join(context.required_capabilities)}"
    
    def _calculate_routing_confidence(
        self,
        primary: str,
        context: Any,
        composition: List[str],
    ) -> float:
        """Calculate confidence score for routing decision.
        
        Args:
            primary: Primary orchestrator
            context: ExecutionContext
            composition: Composition orchestrators
            
        Returns:
            Confidence score (0.0-1.0)
        """
        base_confidence = 0.8
        
        # Reduce confidence for high complexity without composition
        if context.complexity_score >= 0.7 and not composition:
            base_confidence -= 0.15
        
        # Increase confidence for MasterOrchestrator (universal handler)
        if primary == "MasterOrchestrator":
            base_confidence += 0.05
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _get_complexity_level(self, complexity: float) -> str:
        """Get human-readable complexity level.
        
        Args:
            complexity: Complexity score
            
        Returns:
            Complexity level string: 'low', 'medium', or 'high'
        """
        if complexity < 0.33:
            return "low"
        elif complexity < 0.67:
            return "medium"
        else:
            return "high"
    
    def _log_routing_decision(
        self,
        task_type: str,
        context: Any,
        decision: RoutingDecision,
    ) -> None:
        """Log a routing decision for analysis.
        
        Args:
            task_type: Type of task
            context: ExecutionContext
            decision: RoutingDecision
        """
        log_entry = {
            "task_type": task_type,
            "complexity": context.complexity_score,
            "priority": context.priority,
            "primary_orchestrator": decision.primary_orchestrator,
            "fallback_orchestrators": decision.fallback_orchestrators,
            "composition_orchestrators": decision.composition_orchestrators,
            "confidence": decision.confidence_score,
            "reason": decision.reason,
        }
        
        self._routing_log.append(log_entry)
        
        # Update statistics
        self._routing_statistics["total_decisions"] += 1
        
        primary = decision.primary_orchestrator
        if primary not in self._routing_statistics["by_orchestrator"]:
            self._routing_statistics["by_orchestrator"][primary] = 0
        self._routing_statistics["by_orchestrator"][primary] += 1
        
        complexity_level = self._get_complexity_level(context.complexity_score)
        if complexity_level not in self._routing_statistics["by_complexity"]:
            self._routing_statistics["by_complexity"][complexity_level] = 0
        self._routing_statistics["by_complexity"][complexity_level] += 1
    
    def get_routing_log(self) -> List[Dict[str, Any]]:
        """Get the routing decision log.
        
        Returns:
            List of routing decision log entries, each containing task metadata
            and routing decision information
        """
        return self._routing_log
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get routing statistics.
        
        Returns:
            Dictionary with routing statistics including total decisions,
            decisions by orchestrator, and decisions by complexity level
        """
        return self._routing_statistics
    
    def register_orchestrator(
        self,
        name: str,
        profile: Dict[str, Any],
    ) -> None:
        """Register a new orchestrator profile.
        
        Args:
            name: Orchestrator name
            profile: Orchestrator profile with capabilities, complexity limits, etc.
        """
        self._orchestrator_profiles[name] = profile
