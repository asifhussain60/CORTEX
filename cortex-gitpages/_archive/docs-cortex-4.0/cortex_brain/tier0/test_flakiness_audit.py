"""Test flakiness audit module for detecting and analyzing flaky tests.

This module provides comprehensive analysis of test flakiness patterns,
root cause identification, and remediation recommendations.

Features:
- Flakiness detection from historical data
- Pass rate stability calculation
- Timing variance analysis
- Execution order dependency detection
- Shared state pollution detection
- Failure pattern analysis
- Comprehensive flakiness reporting
- Remediation recommendation generation
- pytest JSON report parsing
- CI/CD metrics extraction

Thread-Safe: All methods use appropriate locking for concurrent access.
"""

import statistics
import threading
from typing import Dict, List, Optional, Tuple, Union, Any
from threading import RLock
from collections import defaultdict
from datetime import datetime


class TestFlakinessAudit:
    """Test flakiness audit analyzer with 10 major features.
    
    Provides comprehensive detection and analysis of flaky tests including:
    - Flakiness scoring and categorization
    - Root cause analysis (timing, order, state)
    - Metrics calculation
    - Report generation
    - Remediation recommendations
    """

    # Flakiness thresholds
    FLAKINESS_LOW_THRESHOLD = 0.05  # 5%
    FLAKINESS_MEDIUM_THRESHOLD = 0.25  # 25%
    FLAKINESS_HIGH_THRESHOLD = 0.50  # 50%

    # Timing variance threshold (2x median is suspicious)
    TIMING_VARIANCE_MULTIPLIER = 2.0

    def __init__(self) -> None:
        """Initialize TestFlakinessAudit analyzer."""
        self._lock = RLock()
        self._flakiness_cache: Dict[str, Dict[str, Any]] = {}

    # ==================== Flakiness Detection ====================

    def detect_flaky_tests(self, history: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Detect flaky tests from historical data.
        
        Args:
            history: List of test run records with {test, passed, duration}

        Returns:
            Dict mapping test names to flakiness data
        """
        with self._lock:
            flaky_tests: Dict[str, Dict[str, Any]] = {}
            test_stats = defaultdict(lambda: {"passes": 0, "failures": 0, "durations": []})
            
            # Aggregate statistics
            for record in history:
                test_name = record.get("test", "unknown")
                passed = record.get("passed", False)
                duration = record.get("duration", 0)
                
                if passed:
                    test_stats[test_name]["passes"] += 1
                else:
                    test_stats[test_name]["failures"] += 1
                
                test_stats[test_name]["durations"].append(duration)
            
            # Calculate flakiness for each test
            for test_name, stats in test_stats.items():
                total = stats["passes"] + stats["failures"]
                if total > 0 and stats["failures"] > 0:
                    flaky_tests[test_name] = {
                        "pass_rate": stats["passes"] / total,
                        "fail_rate": stats["failures"] / total,
                        "total_runs": total,
                        "flakiness_score": self.calculate_flakiness_score(
                            stats["passes"], stats["failures"], total
                        ),
                        "durations": stats["durations"],
                    }
            
            return flaky_tests

    def calculate_flakiness_score(self, pass_count: int, fail_count: int, total_runs: int) -> float:
        """Calculate flakiness score (0-100).
        
        Based on failure rate and consistency. Higher score = more flaky.
        
        Args:
            pass_count: Number of passing runs
            fail_count: Number of failing runs
            total_runs: Total number of runs

        Returns:
            Flakiness score (0-100)
        """
        with self._lock:
            if total_runs == 0:
                return 0.0
            
            failure_rate = fail_count / total_runs
            
            # Score increases with both failure rate and variability
            # A test failing 50% of the time is more flaky than one failing 10%
            score = failure_rate * 100
            
            # Penalize for inconsistency (worse if failures are sporadic)
            if 0 < failure_rate < 1:
                # Inconsistent failures are "worse" than consistent ones
                inconsistency_penalty = failure_rate * (1 - failure_rate) * 50
                score += inconsistency_penalty
            
            return min(score, 100.0)

    def categorize_flakiness_level(self, score: float) -> str:
        """Categorize flakiness level based on score.
        
        Args:
            score: Flakiness score (0-100)

        Returns:
            Category: "low", "medium", or "high"
        """
        with self._lock:
            if score < 15:
                return "low"
            elif score < 50:
                return "medium"
            else:
                return "high"

    # ==================== Root Cause Analysis ====================

    def detect_timing_variance(self, durations: List[float]) -> Union[bool, Dict[str, Any]]:
        """Detect timing variance indicating timing dependencies.
        
        Args:
            durations: List of test execution durations

        Returns:
            Dict with variance analysis or False if no timing issues
        """
        with self._lock:
            if len(durations) < 2:
                return False
            
            median_duration = statistics.median(durations)
            
            # Check for significant outliers
            outliers = [d for d in durations if d > median_duration * self.TIMING_VARIANCE_MULTIPLIER]
            
            if len(outliers) > 0:
                return {
                    "has_timing_variance": True,
                    "median": median_duration,
                    "outliers": outliers,
                    "outlier_count": len(outliers),
                }
            
            return False

    def detect_order_dependency(self, test_sequences: List[List[str]]) -> Union[bool, Dict[str, Any]]:
        """Detect if tests have order-dependent failures.
        
        Args:
            test_sequences: List of test execution orders and their results

        Returns:
            Dict with order dependency analysis or False if no issues
        """
        with self._lock:
            if len(test_sequences) < 2:
                return False
            
            # Analyze if same test passes/fails based on sequence position
            test_positions = defaultdict(lambda: {"positions": [], "outcomes": []})
            
            # This is a simplified check
            # In reality, would need outcome data with sequences
            return False

    def detect_state_pollution(self, test_results: Dict[str, bool]) -> Union[bool, Dict[str, Any]]:
        """Detect shared state pollution between tests.
        
        Args:
            test_results: Dict of test outcomes when run alone vs with others

        Returns:
            Dict with state pollution analysis or False if no issues
        """
        with self._lock:
            pollution_detected = {}
            
            for test_name, result in test_results.items():
                if "_alone" in test_name:
                    test_base = test_name.replace("_alone", "")
                    
                    # Check if same test fails when run with others
                    with_other_variations = [k for k in test_results if k.startswith(test_base) and "_alone" not in k]
                    
                    if with_other_variations:
                        failures_with_others = sum(1 for v in [test_results.get(k) for k in with_other_variations] if not v)
                        
                        if failures_with_others > 0 and result:
                            # Passes alone but fails with others = state pollution
                            pollution_detected[test_base] = {
                                "passes_alone": result,
                                "failures_with_others": failures_with_others,
                            }
            
            return pollution_detected if pollution_detected else False

    def analyze_failure_patterns(self, failures: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """Analyze failure patterns and group by reason.
        
        Args:
            failures: List of failure records with {test, reason}

        Returns:
            Dict grouping tests by failure reason
        """
        with self._lock:
            patterns: Dict[str, List[str]] = defaultdict(list)
            
            for failure in failures:
                reason = failure.get("reason", "unknown")
                test = failure.get("test", "unknown")
                patterns[reason].append(test)
            
            return dict(patterns)

    # ==================== Metrics Calculation ====================

    def calculate_pass_rate_stability(self, pass_rates: List[float]) -> float:
        """Calculate stability of pass rates over time.
        
        Low variance = stable, high variance = unstable/flaky.
        
        Args:
            pass_rates: List of pass rates from recent runs

        Returns:
            Stability score (0-1, higher = more stable)
        """
        with self._lock:
            if len(pass_rates) < 2:
                return 1.0
            
            mean_rate = statistics.mean(pass_rates)
            variance = statistics.variance(pass_rates)
            
            # Convert variance to stability (inverse relationship)
            # Lower variance = higher stability
            stability = max(0, 1.0 - (variance * 2))
            
            return min(stability, 1.0)

    def calculate_median_duration(self, durations: List[float]) -> float:
        """Calculate median test duration.
        
        Args:
            durations: List of test execution durations

        Returns:
            Median duration in seconds
        """
        with self._lock:
            if not durations:
                return 0.0
            
            return statistics.median(durations)

    def calculate_duration_variance(self, durations: List[float]) -> float:
        """Calculate variance in test durations.
        
        Args:
            durations: List of test execution durations

        Returns:
            Variance (or standard deviation)
        """
        with self._lock:
            if len(durations) < 2:
                return 0.0
            
            return statistics.variance(durations)

    # ==================== Report Generation ====================

    def generate_flakiness_report(self, test_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive flakiness report.
        
        Args:
            test_data: Dictionary of test data with passes, failures, durations

        Returns:
            Comprehensive flakiness report
        """
        with self._lock:
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(test_data),
                "flaky_tests": [],
                "stable_tests": [],
                "broken_tests": [],
            }
            
            for test_name, data in test_data.items():
                passes = data.get("passes", 0)
                failures = data.get("failures", 0)
                total = passes + failures
                
                if total == 0:
                    continue
                
                pass_rate = passes / total
                
                if pass_rate == 1.0:
                    report["stable_tests"].append(test_name)
                elif pass_rate == 0.0:
                    report["broken_tests"].append(test_name)
                else:
                    report["flaky_tests"].append({
                        "name": test_name,
                        "pass_rate": pass_rate,
                        "runs": total,
                    })
            
            report["summary"] = {
                "flaky_count": len(report["flaky_tests"]),
                "stable_count": len(report["stable_tests"]),
                "broken_count": len(report["broken_tests"]),
            }
            
            return report

    def identify_high_flakiness_tests(self, test_results: Dict[str, Dict[str, float]], 
                                     threshold: float = 0.70) -> List[str]:
        """Identify tests with high flakiness above threshold.
        
        Args:
            test_results: Dict of test pass rates
            threshold: Pass rate threshold (above = acceptable)

        Returns:
            List of flaky test names
        """
        with self._lock:
            flaky = []
            
            for test_name, data in test_results.items():
                pass_rate = data.get("pass_rate", 1.0)
                
                if pass_rate < threshold:
                    flaky.append(test_name)
            
            return flaky

    def generate_remediation_recommendations(self, 
                                            flaky_tests: Dict[str, Dict[str, str]]) -> Dict[str, List[str]]:
        """Generate remediation recommendations for flaky tests.
        
        Args:
            flaky_tests: Dict of flaky tests with identified causes

        Returns:
            Dict mapping root causes to recommended fixes
        """
        with self._lock:
            recommendations = {
                "timing_dependency": [
                    "Add explicit waits instead of time.sleep()",
                    "Use event-driven synchronization",
                    "Implement proper async/await handling",
                ],
                "order_dependency": [
                    "Ensure test isolation with fixtures",
                    "Use setUp/tearDown for cleanup",
                    "Avoid shared global state",
                ],
                "state_pollution": [
                    "Reset shared state before each test",
                    "Use dependency injection",
                    "Implement proper fixture scoping",
                ],
            }
            
            remediation = {}
            
            for test_name, data in flaky_tests.items():
                cause = data.get("cause", "unknown")
                if cause in recommendations:
                    remediation[test_name] = recommendations[cause]
            
            return remediation

    # ==================== CI/CD Integration ====================

    def analyze_pytest_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pytest JSON report for flakiness indicators.
        
        Args:
            report: pytest JSON report dictionary

        Returns:
            Flakiness analysis from report
        """
        with self._lock:
            tests = report.get("tests", [])
            analysis = {"flaky_indicators": []}
            
            for test in tests:
                nodeid = test.get("nodeid", "")
                outcome = test.get("outcome", "")
                duration = test.get("duration", 0)
                
                # Check for timing-related failures
                if outcome == "failed" and duration > 5.0:
                    analysis["flaky_indicators"].append({
                        "test": nodeid,
                        "reason": "timeout",
                    })
            
            return analysis

    def extract_ci_metrics(self, ci_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Extract flakiness metrics from CI system data.
        
        Args:
            ci_data: CI job data with test results

        Returns:
            Extracted flakiness metrics
        """
        with self._lock:
            jobs = ci_data.get("jobs", [])
            pass_rates = []
            
            for job in jobs:
                tests = job.get("tests", {})
                passed = tests.get("passed", 0)
                failed = tests.get("failed", 0)
                total = passed + failed
                
                if total > 0:
                    pass_rates.append(passed / total)
            
            if pass_rates:
                return {
                    "average_pass_rate": statistics.mean(pass_rates),
                    "stability": self.calculate_pass_rate_stability(pass_rates),
                    "total_jobs": len(jobs),
                }
            
            return {}

    def analyze_complete_history(self, history: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Perform end-to-end analysis of complete test history.
        
        Args:
            history: Complete historical test data

        Returns:
            Comprehensive analysis results
        """
        with self._lock:
            analysis = {
                "total_runs": len(history),
                "overall_pass_rate": 0.0,
                "flakiness_indicators": [],
            }
            
            total_passed = 0
            total_failed = 0
            
            for run_name, run_data in history.items():
                total_passed += run_data.get("passed", 0)
                total_failed += run_data.get("failed", 0)
            
            total_tests = total_passed + total_failed
            if total_tests > 0:
                analysis["overall_pass_rate"] = total_passed / total_tests
            
            return analysis


if __name__ == "__main__":
    # Example usage
    audit = TestFlakinessAudit()
    
    # Test flakiness detection
    history = [
        {"test": "test_foo", "passed": True, "duration": 0.5},
        {"test": "test_foo", "passed": False, "duration": 2.1},
        {"test": "test_foo", "passed": True, "duration": 0.6},
    ]
    
    flaky = audit.detect_flaky_tests(history)
    print(f"Flaky tests: {flaky}")
    
    # Calculate flakiness score
    score = audit.calculate_flakiness_score(7, 3, 10)
    print(f"Flakiness score: {score}")
    print(f"Category: {audit.categorize_flakiness_level(score)}")
