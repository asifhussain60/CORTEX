"""Testing Framework for Adaptive Execution.

This module provides a testing framework for validating and benchmarking
adaptive execution strategies, generating test scenarios, and detecting
performance regressions.

AC-PHX-010-05: Testing framework for:
- Test scenario generation
- Strategy comparison
- Performance benchmarking
- Regression detection

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import random
import string
import statistics


@dataclass
class TestScenario:
    """A test scenario for strategy comparison."""
    scenario_id: str
    task_type: str
    complexity: str
    deadline_seconds: float
    required_certainty: float
    input_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """Result of running a test."""
    scenario_id: str
    strategy: str
    duration: float
    success: bool
    resource_usage: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None


class AdaptiveExecutionTestFramework:
    """Framework for testing adaptive execution strategies.
    
    Provides tools for:
    - Generating test scenarios
    - Running strategy comparisons
    - Benchmarking performance
    - Detecting regressions
    
    Example:
        >>> framework = AdaptiveExecutionTestFramework()
        >>> scenarios = framework.generate_scenarios(count=10)
        >>> results = framework.compare_strategies(["FAST", "BALANCED"])
    """
    
    def __init__(self) -> None:
        """Initialize the testing framework."""
        self._scenarios: List[TestScenario] = []
        self._results: List[TestResult] = []
        self._baselines: Dict[str, Dict[str, Any]] = {}
    
    def generate_scenarios(self, count: int = 10) -> List[TestScenario]:
        """Generate test scenarios.
        
        Args:
            count: Number of scenarios to generate
            
        Returns:
            List of test scenarios
        """
        scenarios = []
        task_types = ["analysis", "planning", "execution", "validation"]
        complexities = ["low", "medium", "high"]
        
        for i in range(count):
            scenario = TestScenario(
                scenario_id=f"scenario-{i:03d}",
                task_type=random.choice(task_types),
                complexity=random.choice(complexities),
                deadline_seconds=random.uniform(1, 10),
                required_certainty=random.uniform(0.5, 1.0),
                input_size=random.randint(1, 20),
                metadata={"index": i}
            )
            scenarios.append(scenario)
        
        self._scenarios.extend(scenarios)
        return scenarios
    
    def compare_strategies(
        self,
        strategies: List[str],
        scenario_count: int = 5
    ) -> Dict[str, Any]:
        """Compare multiple strategies on generated scenarios.
        
        Args:
            strategies: List of strategy names to compare
            scenario_count: Number of scenarios to generate
            
        Returns:
            Comparison results
        """
        scenarios = self.generate_scenarios(count=scenario_count)
        
        results_by_strategy: Dict[str, List[TestResult]] = {s: [] for s in strategies}
        
        for scenario in scenarios:
            for strategy in strategies:
                # Simulate execution
                result = self._simulate_execution(scenario, strategy)
                results_by_strategy[strategy].append(result)
                self._results.append(result)
        
        # Analyze results
        comparison = {}
        for strategy, results in results_by_strategy.items():
            if results:
                successful = sum(1 for r in results if r.success)
                durations = [r.duration for r in results]
                
                comparison[strategy] = {
                    "count": len(results),
                    "success_rate": successful / len(results),
                    "avg_duration": statistics.mean(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "std_duration": statistics.stdev(durations) if len(durations) > 1 else 0,
                }
        
        return comparison
    
    def _simulate_execution(
        self,
        scenario: TestScenario,
        strategy: str
    ) -> TestResult:
        """Simulate task execution with a strategy.
        
        Args:
            scenario: Test scenario
            strategy: Strategy name
            
        Returns:
            Execution result
        """
        # Simulate execution time based on strategy and complexity
        base_time = {
            "low": 0.5,
            "medium": 1.5,
            "high": 3.0
        }.get(scenario.complexity, 1.0)
        
        strategy_multiplier = {
            "FAST": 0.8,
            "BALANCED": 1.0,
            "THOROUGH": 1.5
        }.get(strategy, 1.0)
        
        duration = base_time * strategy_multiplier
        duration += random.uniform(-0.2, 0.2)  # Add variance
        
        # Determine success based on deadline
        success = duration <= scenario.deadline_seconds
        
        # Simulate resource usage
        resource_usage = {
            "cpu": random.uniform(0.3, 0.9),
            "memory": random.uniform(0.2, 0.8)
        }
        
        return TestResult(
            scenario_id=scenario.scenario_id,
            strategy=strategy,
            duration=max(0.1, duration),
            success=success,
            resource_usage=resource_usage
        )
    
    def run_performance_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark.
        
        Returns:
            Benchmark results
        """
        strategies = ["FAST", "BALANCED", "THOROUGH"]
        comparison = self.compare_strategies(strategies, scenario_count=20)
        
        benchmark = {
            "timestamp": datetime.now().isoformat(),
            "scenario_count": 20,
            "strategies": comparison,
            "winner": max(
                comparison.keys(),
                key=lambda s: comparison[s]["success_rate"]
            ) if comparison else None,
        }
        
        return benchmark
    
    def check_regression(
        self,
        baseline: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check for performance regression.
        
        Args:
            baseline: Baseline performance metrics
            
        Returns:
            Regression analysis
        """
        if not self._results:
            return {"status": "no_results"}
        
        regressions = []
        
        # Group results by strategy
        by_strategy: Dict[str, List[TestResult]] = {}
        for result in self._results[-50:]:  # Check last 50
            if result.strategy not in by_strategy:
                by_strategy[result.strategy] = []
            by_strategy[result.strategy].append(result)
        
        for strategy, results in by_strategy.items():
            if strategy in baseline and results:
                baseline_duration = baseline[strategy].get("duration", 0)
                current_avg = statistics.mean([r.duration for r in results])
                
                # Check for significant regression (>20% slower)
                if current_avg > baseline_duration * 1.2:
                    regressions.append({
                        "strategy": strategy,
                        "baseline_duration": baseline_duration,
                        "current_duration": current_avg,
                        "regression_percent": (
                            (current_avg - baseline_duration) / baseline_duration * 100
                        )
                    })
        
        return {
            "has_regression": len(regressions) > 0,
            "regressions": regressions,
            "check_timestamp": datetime.now().isoformat(),
        }
    
    def set_baseline(self, strategy: str, metrics: Dict[str, Any]) -> None:
        """Set baseline metrics for a strategy.
        
        Args:
            strategy: Strategy name
            metrics: Baseline metrics
        """
        self._baselines[strategy] = metrics
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report.
        
        Returns:
            Test report dictionary
        """
        if not self._results:
            return {"status": "no_results"}
        
        # Aggregate results
        by_strategy: Dict[str, List[TestResult]] = {}
        for result in self._results:
            if result.strategy not in by_strategy:
                by_strategy[result.strategy] = []
            by_strategy[result.strategy].append(result)
        
        summary = {}
        for strategy, results in by_strategy.items():
            if results:
                successful = sum(1 for r in results if r.success)
                durations = [r.duration for r in results]
                
                summary[strategy] = {
                    "total_runs": len(results),
                    "success_count": successful,
                    "success_rate": successful / len(results),
                    "avg_duration": statistics.mean(durations),
                    "total_duration": sum(durations),
                }
        
        return {
            "report_generated": datetime.now().isoformat(),
            "total_tests": len(self._results),
            "summary": summary,
            "strategies_tested": list(by_strategy.keys()),
        }
    
    def clear_results(self) -> None:
        """Clear test results."""
        self._results.clear()
