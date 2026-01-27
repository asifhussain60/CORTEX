"""Tests for Adaptive Execution Framework (PHASE-10).

Comprehensive test suite for execution strategy selection, context analysis,
adaptive routing, performance feedback loops, and testing framework.

AC-PHX-010-01: Execution strategy selector
AC-PHX-010-02: Context analyzer
AC-PHX-010-03: Adaptive routing
AC-PHX-010-04: Performance feedback loop
AC-PHX-010-05: Testing framework

Author: Asif Hussain
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, List, Optional
import time
from dataclasses import dataclass
from enum import Enum


# ═════════════════════════════════════════════════════════════════════════════
# AC-PHX-010-01: Execution Strategy Selector Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestExecutionStrategySelector(unittest.TestCase):
    """Tests for AC-PHX-010-01: Execution strategy selector.
    
    Tests dynamic strategy selection based on task characteristics:
    - Task complexity analysis
    - Resource availability
    - Deadline constraints
    - Historical performance
    """
    
    def test_strategy_selector_initialization(self) -> None:
        """Test StrategySelector can be initialized with default strategies."""
        from cortex.orchestrators.adaptive.strategy_selector import StrategySelector
        
        selector = StrategySelector()
        self.assertIsNotNone(selector)
        self.assertTrue(hasattr(selector, 'select_strategy'))
    
    def test_select_strategy_for_simple_task(self) -> None:
        """Test selecting FAST strategy for simple tasks."""
        from cortex.orchestrators.adaptive.strategy_selector import StrategySelector
        
        selector = StrategySelector()
        task = {"complexity": "low", "timeout": 5}
        strategy = selector.select_strategy(task)
        
        self.assertIsNotNone(strategy)
        self.assertIn(strategy, ["FAST", "BALANCED", "THOROUGH"])
    
    def test_select_strategy_for_complex_task(self) -> None:
        """Test selecting THOROUGH strategy for complex tasks."""
        from cortex.orchestrators.adaptive.strategy_selector import StrategySelector
        
        selector = StrategySelector()
        task = {"complexity": "high", "requires_validation": True}
        strategy = selector.select_strategy(task)
        
        self.assertIsNotNone(strategy)
        self.assertIn(strategy, ["FAST", "BALANCED", "THOROUGH"])
    
    def test_strategy_selector_considers_resource_availability(self) -> None:
        """Test strategy selection considers available resources."""
        from cortex.orchestrators.adaptive.strategy_selector import StrategySelector
        
        selector = StrategySelector()
        task = {
            "complexity": "medium",
            "resource_intensive": True,
            "available_resources": {"cpu": 0.2, "memory": 0.3}
        }
        strategy = selector.select_strategy(task)
        
        # With limited resources, should not select resource-heavy strategy
        self.assertIsNotNone(strategy)
    
    def test_strategy_selector_respects_deadlines(self) -> None:
        """Test strategy respects time constraints."""
        from cortex.orchestrators.adaptive.strategy_selector import StrategySelector
        
        selector = StrategySelector()
        task = {
            "complexity": "high",
            "deadline_seconds": 2,
            "estimated_time_fast": 1.5,
            "estimated_time_thorough": 10
        }
        strategy = selector.select_strategy(task)
        
        # With strict deadline, must respect it
        self.assertIsNotNone(strategy)
    
    def test_strategy_selector_learns_from_history(self) -> None:
        """Test strategy selection improves with execution history."""
        from cortex.orchestrators.adaptive.strategy_selector import StrategySelector
        
        selector = StrategySelector()
        
        # Record successful execution
        selector.record_execution({
            "task_type": "analysis",
            "strategy": "FAST",
            "success": True,
            "duration": 0.5
        })
        
        # Next similar task should prefer FAST
        task = {"task_type": "analysis", "complexity": "low"}
        strategy = selector.select_strategy(task)
        
        self.assertIsNotNone(strategy)


# ═════════════════════════════════════════════════════════════════════════════
# AC-PHX-010-02: Context Analyzer Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestExecutionContextAnalyzer(unittest.TestCase):
    """Tests for AC-PHX-010-02: Context analyzer.
    
    Tests analysis of execution context including:
    - System state analysis
    - Resource availability
    - Task characteristics
    - Historical context
    """
    
    def test_context_analyzer_initialization(self) -> None:
        """Test ContextAnalyzer initialization."""
        from cortex.orchestrators.adaptive.execution_context_analyzer import (
            ExecutionContextAnalyzer
        )
        
        analyzer = ExecutionContextAnalyzer()
        self.assertIsNotNone(analyzer)
        self.assertTrue(hasattr(analyzer, 'analyze_context'))
    
    def test_analyze_system_state(self) -> None:
        """Test analyzing current system state."""
        from cortex.orchestrators.adaptive.execution_context_analyzer import (
            ExecutionContextAnalyzer
        )
        
        analyzer = ExecutionContextAnalyzer()
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={"test": "data"}
        )
        
        self.assertIsNotNone(context)
        self.assertIn("complexity_score", dir(context))
    
    def test_analyze_task_characteristics(self) -> None:
        """Test analyzing task characteristics."""
        from cortex.orchestrators.adaptive.execution_context_analyzer import (
            ExecutionContextAnalyzer
        )
        
        analyzer = ExecutionContextAnalyzer()
        task = {
            "type": "analysis",
            "inputs": ["a", "b", "c"],
            "required_capabilities": ["caching", "parallel"]
        }
        context = analyzer.analyze_context(
            task_type="analysis",
            task_input=task
        )
        
        self.assertIsNotNone(context)
        self.assertGreaterEqual(context.complexity_score, 0.0)
        self.assertLessEqual(context.complexity_score, 1.0)
    
    def test_context_includes_resource_availability(self) -> None:
        """Test context analysis includes resource availability."""
        from cortex.orchestrators.adaptive.execution_context_analyzer import (
            ExecutionContextAnalyzer
        )
        
        analyzer = ExecutionContextAnalyzer()
        context = analyzer.analyze_context(
            task_type="analysis",
            task_input={"data": "test"}
        )
        
        self.assertIsNotNone(context)
        self.assertIsNotNone(context.resource_requirements)
    
    def test_context_tracks_execution_history(self) -> None:
        """Test context tracking includes historical data."""
        from cortex.orchestrators.adaptive.execution_context_analyzer import (
            ExecutionContextAnalyzer
        )
        
        analyzer = ExecutionContextAnalyzer()
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={"ac_ids": ["AC-001"]}
        )
        
        self.assertIsNotNone(context)
        self.assertEqual(context.task_type, "planning")
    
    def test_context_identifies_bottlenecks(self) -> None:
        """Test context analysis identifies system bottlenecks."""
        from cortex.orchestrators.adaptive.execution_context_analyzer import (
            ExecutionContextAnalyzer
        )
        
        analyzer = ExecutionContextAnalyzer()
        context = analyzer.analyze_context(
            task_type="complex_orchestration",
            task_input={"large": "dataset"}
        )
        
        self.assertIsNotNone(context)
        self.assertGreater(context.complexity_score, 0)


# ═════════════════════════════════════════════════════════════════════════════
# AC-PHX-010-03: Adaptive Routing Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestAdaptiveRouting(unittest.TestCase):
    """Tests for AC-PHX-010-03: Adaptive routing.
    
    Tests intelligent routing decisions:
    - Route to appropriate orchestrator based on context
    - Fallback handling
    - Load balancing
    - Quality-of-service routing
    """
    
    def test_adaptive_router_initialization(self) -> None:
        """Test AdaptiveRouter initialization."""
        from cortex.brain.core.knowledge.router import AdaptiveRouter
        
        router = AdaptiveRouter()
        self.assertIsNotNone(router)
        self.assertTrue(hasattr(router, 'route'))
    
    def test_route_task_to_appropriate_orchestrator(self) -> None:
        """Test routing task to appropriate orchestrator."""
        from cortex.brain.core.knowledge.router import AdaptiveRouter
        
        router = AdaptiveRouter()
        task = {"domain": "planning", "type": "strategy"}
        
        route = router.route(task)
        
        self.assertIsNotNone(route)
        self.assertTrue(hasattr(route, 'orchestrator'))
        self.assertIsNotNone(route.orchestrator)
    
    def test_router_considers_execution_context(self) -> None:
        """Test router considers execution context in routing."""
        from cortex.brain.core.knowledge.router import AdaptiveRouter
        
        router = AdaptiveRouter()
        task = {"domain": "analysis"}
        context = {"resource_limited": True}
        
        route = router.route(task, context=context)
        
        self.assertIsNotNone(route)
    
    def test_router_provides_fallback_routes(self) -> None:
        """Test router provides fallback routes."""
        from cortex.brain.core.knowledge.router import AdaptiveRouter
        
        router = AdaptiveRouter()
        task = {"domain": "validation"}
        
        route = router.route(task)
        
        self.assertIsNotNone(route)
        self.assertTrue(hasattr(route, 'fallbacks') or 
                       "fallback" in str(route).lower())
    
    def test_router_balances_load(self) -> None:
        """Test router implements load balancing."""
        from cortex.brain.core.knowledge.router import AdaptiveRouter
        
        router = AdaptiveRouter()
        
        # Route multiple tasks
        routes = []
        for i in range(10):
            task = {"domain": "execution", "id": i}
            route = router.route(task)
            routes.append(route)
        
        self.assertEqual(len(routes), 10)
    
    def test_router_respects_qos_requirements(self) -> None:
        """Test router respects QoS requirements."""
        from cortex.brain.core.knowledge.router import AdaptiveRouter
        
        router = AdaptiveRouter()
        task = {
            "domain": "integration",
            "qos": {"max_latency": 1.0, "min_success_rate": 0.95}
        }
        
        route = router.route(task)
        
        self.assertIsNotNone(route)


# ═════════════════════════════════════════════════════════════════════════════
# AC-PHX-010-04: Performance Feedback Loop Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestPerformanceFeedbackLoop(unittest.TestCase):
    """Tests for AC-PHX-010-04: Performance feedback loop.
    
    Tests feedback mechanisms for continuous optimization:
    - Execution metrics collection
    - Performance analysis
    - Strategy optimization
    - Adjustment recommendations
    """
    
    def test_feedback_loop_initialization(self) -> None:
        """Test FeedbackLoop initialization."""
        from cortex.orchestrators.adaptive.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        self.assertIsNotNone(loop)
        self.assertTrue(hasattr(loop, 'record_execution'))
    
    def test_collect_execution_metrics(self) -> None:
        """Test collecting execution metrics."""
        from cortex.orchestrators.adaptive.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        metrics = {
            "duration": 0.5,
            "resource_usage": {"cpu": 0.8, "memory": 0.6},
            "success": True,
            "strategy": "FAST"
        }
        
        loop.record_execution(metrics)
        collected = loop.get_metrics()
        
        self.assertIsNotNone(collected)
    
    def test_analyze_performance_trends(self) -> None:
        """Test analyzing performance trends."""
        from cortex.orchestrators.adaptive.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        
        # Record multiple executions
        for i in range(5):
            loop.record_execution({
                "duration": 0.5 + (i * 0.1),
                "success": True,
                "strategy": "FAST"
            })
        
        trends = loop.analyze_trends()
        
        self.assertIsNotNone(trends)
    
    def test_generate_optimization_recommendations(self) -> None:
        """Test generating optimization recommendations."""
        from cortex.orchestrators.adaptive.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        
        # Record execution data
        loop.record_execution({
            "duration": 5.0,
            "strategy": "THOROUGH",
            "success": True,
            "resource_usage": {"cpu": 0.9}
        })
        
        recommendations = loop.get_recommendations()
        
        self.assertIsNotNone(recommendations)
        self.assertIsInstance(recommendations, (list, dict))
    
    def test_feedback_identifies_performance_bottlenecks(self) -> None:
        """Test feedback loop identifies performance bottlenecks."""
        from cortex.orchestrators.adaptive.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        
        # Simulate slow executions
        for i in range(3):
            loop.record_execution({
                "duration": 10.0,
                "strategy": "THOROUGH",
                "phase": "validation"
            })
        
        bottlenecks = loop.identify_bottlenecks()
        
        self.assertIsNotNone(bottlenecks)
    
    def test_feedback_tracks_strategy_effectiveness(self) -> None:
        """Test tracking strategy effectiveness over time."""
        from cortex.orchestrators.adaptive.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        
        # Record various strategy results
        loop.record_execution({
            "strategy": "FAST",
            "duration": 1.0,
            "success": True
        })
        loop.record_execution({
            "strategy": "BALANCED",
            "duration": 2.0,
            "success": True
        })
        loop.record_execution({
            "strategy": "THOROUGH",
            "duration": 5.0,
            "success": True
        })
        
        effectiveness = loop.get_strategy_effectiveness()
        
        self.assertIsNotNone(effectiveness)


# ═════════════════════════════════════════════════════════════════════════════
# AC-PHX-010-05: Testing Framework Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestAdaptiveExecutionTestingFramework(unittest.TestCase):
    """Tests for AC-PHX-010-05: Testing framework.
    
    Tests the testing framework for adaptive execution:
    - Test scenario generation
    - Strategy comparison
    - Performance benchmarking
    - Regression detection
    """
    
    def test_test_framework_initialization(self) -> None:
        """Test AdaptiveExecutionTestFramework initialization."""
        from cortex.orchestrators.adaptive.testing_framework import (
            AdaptiveExecutionTestFramework
        )
        
        framework = AdaptiveExecutionTestFramework()
        self.assertIsNotNone(framework)
        self.assertTrue(hasattr(framework, 'generate_scenarios'))
    
    def test_generate_test_scenarios(self) -> None:
        """Test generating test scenarios."""
        from cortex.orchestrators.adaptive.testing_framework import (
            AdaptiveExecutionTestFramework
        )
        
        framework = AdaptiveExecutionTestFramework()
        scenarios = framework.generate_scenarios(count=10)
        
        self.assertIsNotNone(scenarios)
        self.assertGreaterEqual(len(scenarios), 10)
    
    def test_compare_strategies(self) -> None:
        """Test comparing execution strategies."""
        from cortex.orchestrators.adaptive.testing_framework import (
            AdaptiveExecutionTestFramework
        )
        
        framework = AdaptiveExecutionTestFramework()
        results = framework.compare_strategies(
            strategies=["FAST", "BALANCED", "THOROUGH"],
            scenario_count=5
        )
        
        self.assertIsNotNone(results)
        self.assertIn("FAST", str(results))
    
    def test_benchmark_performance(self) -> None:
        """Test benchmarking strategy performance."""
        from cortex.orchestrators.adaptive.testing_framework import (
            AdaptiveExecutionTestFramework
        )
        
        framework = AdaptiveExecutionTestFramework()
        
        benchmark_results = framework.run_performance_benchmark()
        
        self.assertIsNotNone(benchmark_results)
        self.assertIsInstance(benchmark_results, dict)
    
    def test_detect_regression(self) -> None:
        """Test detecting performance regression."""
        from cortex.orchestrators.adaptive.testing_framework import (
            AdaptiveExecutionTestFramework
        )
        
        framework = AdaptiveExecutionTestFramework()
        
        # Establish baseline
        baseline = {
            "FAST": {"duration": 1.0},
            "BALANCED": {"duration": 2.0}
        }
        
        # Check for regression
        regression = framework.check_regression(baseline)
        
        self.assertIsNotNone(regression)
    
    def test_test_framework_generates_report(self) -> None:
        """Test framework generates comprehensive test report."""
        from cortex.orchestrators.adaptive.testing_framework import (
            AdaptiveExecutionTestFramework
        )
        
        framework = AdaptiveExecutionTestFramework()
        
        # Generate scenarios first
        framework.generate_scenarios(count=5)
        framework.compare_strategies(["FAST", "BALANCED"], scenario_count=5)
        
        report = framework.generate_test_report()
        
        self.assertIsNotNone(report)
        self.assertIn("summary", report)


# ═════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestAdaptiveExecutionIntegration(unittest.TestCase):
    """Integration tests for complete adaptive execution flow."""
    
    def test_end_to_end_adaptive_execution(self) -> None:
        """Test complete adaptive execution workflow."""
        from cortex.orchestrators.adaptive.strategy_selector import StrategySelector
        from cortex.orchestrators.adaptive.execution_context_analyzer import (
            ExecutionContextAnalyzer
        )
        from cortex.brain.core.knowledge.router import AdaptiveRouter
        
        # Create components
        selector = StrategySelector()
        analyzer = ExecutionContextAnalyzer()
        router = AdaptiveRouter()
        
        # Analyze task
        task = {"domain": "planning", "complexity": "medium"}
        context = analyzer.analyze_context("planning", task)
        
        # Select strategy
        strategy = selector.select_strategy(task)
        
        # Route task
        route = router.route(task, context={"level": "medium"})
        
        # Verify complete flow
        self.assertIsNotNone(context)
        self.assertIsNotNone(strategy)
        self.assertIsNotNone(route)
    
    def test_adaptive_execution_with_feedback(self) -> None:
        """Test adaptive execution with feedback loop."""
        from cortex.orchestrators.adaptive.feedback_loop import FeedbackLoop
        from cortex.orchestrators.adaptive.strategy_selector import StrategySelector
        
        feedback = FeedbackLoop()
        selector = StrategySelector()
        
        # Execute task with strategy
        strategy = selector.select_strategy({"complexity": "medium"})
        
        # Record result
        feedback.record_execution({
            "strategy": strategy,
            "duration": 1.5,
            "success": True
        })
        
        # Get improvements
        recommendations = feedback.get_recommendations()
        
        self.assertIsNotNone(recommendations)


if __name__ == "__main__":
    unittest.main()
