"""Tests for Orchestrator Selection & Routing Engine.

This module tests the RoutingEngine component which routes tasks to appropriate
orchestrators based on context analysis.

AC-EX-001-02: Routing considers task type and complexity, multiple orchestrators
can be selected for composition, and routing decisions are logged for analysis.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import unittest
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple
from unittest.mock import MagicMock, Mock, patch


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
    optimization_hints: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Validate routing decision after initialization."""
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
            Complexity level string
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
            List of routing decision log entries
        """
        return self._routing_log
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get routing statistics.
        
        Returns:
            Dictionary with routing statistics
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


class TestRoutingEngine(unittest.TestCase):
    """Tests for RoutingEngine."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.engine = RoutingEngine()
        
        # Create mock context
        self.mock_context = MagicMock()
        self.mock_context.task_type = "test"
        self.mock_context.complexity_score = 0.5
        self.mock_context.priority = "MEDIUM"
        self.mock_context.required_capabilities = {"planning", "analysis"}
    
    def test_routing_engine_initialization(self) -> None:
        """Test that routing engine initializes correctly."""
        self.assertIsNotNone(self.engine)
        self.assertGreater(len(self.engine._orchestrator_profiles), 0)
        self.assertEqual(len(self.engine._routing_log), 0)
    
    def test_route_task_low_complexity(self) -> None:
        """Test routing a low-complexity task."""
        context = MagicMock()
        context.complexity_score = 0.2
        context.priority = "LOW"
        context.required_capabilities = {"planning"}
        
        decision = self.engine.route_task("simple_query", context)
        
        self.assertIsNotNone(decision.primary_orchestrator)
        self.assertGreater(decision.confidence_score, 0.5)
        self.assertIn("low", decision.reason.lower())
    
    def test_route_task_medium_complexity(self) -> None:
        """Test routing a medium-complexity task."""
        context = MagicMock()
        context.complexity_score = 0.5
        context.priority = "MEDIUM"
        context.required_capabilities = {"planning", "analysis"}
        
        decision = self.engine.route_task("analysis", context)
        
        self.assertIsNotNone(decision.primary_orchestrator)
        self.assertGreater(decision.confidence_score, 0.5)
    
    def test_route_task_high_complexity(self) -> None:
        """Test routing a high-complexity task."""
        context = MagicMock()
        context.complexity_score = 0.8
        context.priority = "HIGH"
        context.required_capabilities = {"orchestration", "delegation", "composition"}
        
        decision = self.engine.route_task("complex_task", context)
        
        self.assertEqual(decision.primary_orchestrator, "MasterOrchestrator")
        self.assertGreater(len(decision.composition_orchestrators), 0)
    
    def test_fallback_orchestrators_selected(self) -> None:
        """Test that fallback orchestrators are selected."""
        context = MagicMock()
        context.complexity_score = 0.5
        context.priority = "MEDIUM"
        context.required_capabilities = {"planning"}
        
        decision = self.engine.route_task("task", context)
        
        self.assertGreater(len(decision.fallback_orchestrators), 0)
    
    def test_routing_with_preferences(self) -> None:
        """Test routing with explicit preferences."""
        context = MagicMock()
        context.complexity_score = 0.5
        context.priority = "MEDIUM"
        context.required_capabilities = {"planning"}
        
        preferences = {"preferred_orchestrator": "PlanningOrchestrator"}
        decision = self.engine.route_task("task", context, preferences)
        
        self.assertEqual(decision.primary_orchestrator, "PlanningOrchestrator")
    
    def test_routing_decision_validation(self) -> None:
        """Test RoutingDecision validation."""
        with self.assertRaises(ValueError):
            RoutingDecision(
                primary_orchestrator="",  # Invalid: empty
                fallback_orchestrators=[],
                composition_orchestrators=[],
                reason="test",
                confidence_score=0.5,
            )
    
    def test_routing_decision_confidence_validation(self) -> None:
        """Test RoutingDecision confidence validation."""
        with self.assertRaises(ValueError):
            RoutingDecision(
                primary_orchestrator="Test",
                fallback_orchestrators=[],
                composition_orchestrators=[],
                reason="test",
                confidence_score=1.5,  # Invalid: > 1.0
            )
    
    def test_routing_log_populated(self) -> None:
        """Test that routing log is populated."""
        context = MagicMock()
        context.complexity_score = 0.5
        context.priority = "MEDIUM"
        context.required_capabilities = {"planning"}
        
        self.engine.route_task("task1", context)
        self.engine.route_task("task2", context)
        
        log = self.engine.get_routing_log()
        self.assertEqual(len(log), 2)
    
    def test_routing_statistics_updated(self) -> None:
        """Test that routing statistics are updated."""
        context = MagicMock()
        context.complexity_score = 0.5
        context.priority = "MEDIUM"
        context.required_capabilities = {"planning"}
        
        self.engine.route_task("task", context)
        
        stats = self.engine.get_statistics()
        self.assertEqual(stats["total_decisions"], 1)
        self.assertGreater(len(stats["by_orchestrator"]), 0)
        self.assertGreater(len(stats["by_complexity"]), 0)
    
    def test_master_orchestrator_fallback(self) -> None:
        """Test that MasterOrchestrator serves as ultimate fallback."""
        context = MagicMock()
        context.complexity_score = 0.5
        context.priority = "MEDIUM"
        context.required_capabilities = {"unknown_capability"}
        
        decision = self.engine.route_task("task", context)
        
        # MasterOrchestrator should handle unknown capabilities
        self.assertEqual(decision.primary_orchestrator, "MasterOrchestrator")
    
    def test_composition_for_high_complexity_multi_capability(self) -> None:
        """Test composition selection for high-complexity multi-capability tasks."""
        context = MagicMock()
        context.complexity_score = 0.8
        context.priority = "CRITICAL"
        context.required_capabilities = {"planning", "analysis", "orchestration"}
        
        decision = self.engine.route_task("complex_task", context)
        
        self.assertGreater(len(decision.composition_orchestrators), 0)
    
    def test_routing_reason_contains_details(self) -> None:
        """Test that routing reason contains relevant details."""
        context = MagicMock()
        context.complexity_score = 0.5
        context.priority = "MEDIUM"
        context.required_capabilities = {"planning", "analysis"}
        
        decision = self.engine.route_task("task", context)
        
        self.assertIn(decision.primary_orchestrator, decision.reason)
        self.assertIn("complexity", decision.reason.lower())
    
    def test_invalid_task_type_raises_error(self) -> None:
        """Test that empty task_type raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.route_task("", self.mock_context)
    
    def test_none_context_raises_error(self) -> None:
        """Test that None context raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.route_task("task", None)
    
    def test_register_custom_orchestrator(self) -> None:
        """Test registering a custom orchestrator."""
        custom_profile = {
            "capabilities": {"custom_capability"},
            "max_complexity": 0.6,
            "strengths": ["custom"],
            "weaknesses": [],
            "resilience_level": "low",
        }
        
        self.engine.register_orchestrator("CustomOrchestrator", custom_profile)
        
        self.assertIn("CustomOrchestrator", self.engine._orchestrator_profiles)
    
    def test_confidence_score_range(self) -> None:
        """Test that confidence scores are always valid."""
        context = MagicMock()
        context.complexity_score = 0.5
        context.priority = "MEDIUM"
        context.required_capabilities = {"planning"}
        
        for _ in range(10):
            decision = self.engine.route_task("task", context)
            self.assertLessEqual(decision.confidence_score, 1.0)
            self.assertGreaterEqual(decision.confidence_score, 0.0)


if __name__ == "__main__":
    unittest.main()
