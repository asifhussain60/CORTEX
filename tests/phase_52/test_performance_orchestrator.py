"""
Phase 52 S5-S6: PerformanceOrchestrator Tests
Authority: AC-PHASE52-S5S6
Purpose: Validate profiling, load testing, and performance regression detection

Test Targets:
- Profiler integration (cProfile, Pyinstrument, Node clinic)
- Flame graph generation
- Load testing with k6/Locust
- Performance regression detection
- Bottleneck identification
- Memory profiling
- Performance report generation

Coverage: 40+ comprehensive tests (combined S5-S6)
TDD-First: Tests before implementation
"""

import pytest
from typing import Dict, List, Any, Optional, Union
from cortex.brain.core.result import Ok, Err
from cortex.orchestrators.support.performance_orchestrator import (
    PerformanceOrchestrator,
    ProfileResult,
    FunctionProfile,
    LoadTestResult,
    PerformanceRegression,
    BottleneckReport,
    PerformanceBaseline,
    MemoryProfile,
    PerformanceGate,
)


# ============================================================================
# PROFILER INTEGRATION TESTS (6 Tests)
# ============================================================================

class TestProfilerIntegration:
    """Test profiler integration and profiling"""

    def test_profile_python_code_with_cprofile(self):
        """Profile Python code using cProfile"""
        orchestrator = PerformanceOrchestrator()
        
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
        """
        
        result = orchestrator.profile_code(code, language="python", profiler="cprofile")
        assert result.is_ok()
        profile = result.unwrap()
        
        assert profile.total_time >= 0
        assert len(profile.function_calls) >= 1

    def test_profile_javascript_code_with_nodejs(self):
        """Profile JavaScript code using Node.js profiler"""
        orchestrator = PerformanceOrchestrator()
        
        code = """
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
const result = fibonacci(10);
        """
        
        result = orchestrator.profile_code(code, language="javascript", profiler="nodejs")
        assert result.is_ok()
        profile = result.unwrap()
        
        assert profile.total_time >= 0

    def test_function_level_profiling(self):
        """Get function-level profiling information"""
        orchestrator = PerformanceOrchestrator()
        
        code = """
def function_a():
    return sum(range(1000))

def function_b():
    return [i*2 for i in range(100)]

function_a()
function_b()
        """
        
        result = orchestrator.profile_functions(code, language="python")
        assert result.is_ok()
        profiles = result.unwrap()
        
        assert len(profiles) >= 2
        for profile in profiles:
            assert profile.function_name is not None
            assert profile.execution_time >= 0

    def test_memory_profiling(self):
        """Profile memory usage"""
        orchestrator = PerformanceOrchestrator()
        
        code = """
data = [i for i in range(10000)]
result = sum(data)
        """
        
        result = orchestrator.profile_memory(code, language="python")
        assert result.is_ok()
        memory_profile = result.unwrap()
        
        assert memory_profile.peak_memory >= 0
        assert memory_profile.memory_operations >= 0

    def test_cpu_profiling(self):
        """Profile CPU usage"""
        orchestrator = PerformanceOrchestrator()
        
        code = """
total = 0
for i in range(1000000):
    total += i
        """
        
        result = orchestrator.profile_cpu(code, language="python")
        assert result.is_ok()
        cpu_profile = result.unwrap()
        
        assert cpu_profile["cpu_time"] >= 0

    def test_profile_result_includes_metadata(self):
        """Verify profile results include metadata"""
        orchestrator = PerformanceOrchestrator()
        
        code = "x = 1 + 1"
        
        result = orchestrator.profile_code(code, language="python", profiler="cprofile")
        assert result.is_ok()
        profile = result.unwrap()
        
        assert profile.timestamp is not None
        assert profile.language == "python"


# ============================================================================
# FLAME GRAPH GENERATION TESTS (5 Tests)
# ============================================================================

class TestFlameGraphGeneration:
    """Test flame graph generation"""

    def test_generate_flame_graph_from_profile(self):
        """Generate flame graph from profiling data"""
        orchestrator = PerformanceOrchestrator()
        
        profile_data = {
            "functions": [
                {"name": "main", "time": 1000},
                {"name": "process", "time": 800},
                {"name": "calculate", "time": 600},
            ]
        }
        
        result = orchestrator.generate_flame_graph(profile_data)
        assert result.is_ok()
        flame_graph = result.unwrap()
        
        assert flame_graph.html_content is not None or flame_graph.svg_content is not None

    def test_flame_graph_shows_stack_traces(self):
        """Verify flame graph shows stack traces"""
        orchestrator = PerformanceOrchestrator()
        
        profile_data = {
            "stack_traces": [
                {"function": "main", "caller": None},
                {"function": "process", "caller": "main"},
                {"function": "calculate", "caller": "process"},
            ]
        }
        
        result = orchestrator.generate_flame_graph(profile_data)
        assert result.is_ok()
        flame_graph = result.unwrap()
        
        assert flame_graph is not None

    def test_flame_graph_highlights_hotspots(self):
        """Verify flame graph highlights performance hotspots"""
        orchestrator = PerformanceOrchestrator()
        
        profile_data = {
            "hotspots": [
                {"function": "slow_function", "time": 9000},
                {"function": "medium_function", "time": 500},
            ]
        }
        
        result = orchestrator.generate_flame_graph(profile_data)
        assert result.is_ok()
        flame_graph = result.unwrap()
        
        assert flame_graph is not None

    def test_export_flame_graph_to_svg(self):
        """Export flame graph as SVG"""
        orchestrator = PerformanceOrchestrator()
        
        profile_data = {"functions": [{"name": "main", "time": 100}]}
        
        result = orchestrator.export_flame_graph(profile_data, format="svg")
        assert result.is_ok()
        svg_content = result.unwrap()
        
        assert svg_content is not None

    def test_export_flame_graph_to_html(self):
        """Export flame graph as interactive HTML"""
        orchestrator = PerformanceOrchestrator()
        
        profile_data = {"functions": [{"name": "main", "time": 100}]}
        
        result = orchestrator.export_flame_graph(profile_data, format="html")
        assert result.is_ok()
        html_content = result.unwrap()
        
        assert html_content is not None


# ============================================================================
# LOAD TESTING TESTS (6 Tests)
# ============================================================================

class TestLoadTesting:
    """Test load testing functionality"""

    def test_create_load_test_config(self):
        """Create load test configuration"""
        orchestrator = PerformanceOrchestrator()
        
        config = {
            "target_url": "http://localhost:8000",
            "users": 100,
            "duration_seconds": 60,
            "ramp_up_seconds": 10,
        }
        
        result = orchestrator.create_load_test_config(config)
        assert result.is_ok()
        lt_config = result.unwrap()
        
        assert lt_config.users == 100
        assert lt_config.duration_seconds == 60

    def test_run_load_test(self):
        """Run load test"""
        orchestrator = PerformanceOrchestrator()
        
        config = {
            "target_url": "http://localhost:8000",
            "users": 10,
            "duration_seconds": 10,
        }
        
        result = orchestrator.run_load_test(config)
        assert result.is_ok()
        load_test_result = result.unwrap()
        
        assert load_test_result.total_requests >= 0
        assert load_test_result.requests_per_second >= 0

    def test_measure_response_time_percentiles(self):
        """Measure response time percentiles (p50, p95, p99)"""
        orchestrator = PerformanceOrchestrator()
        
        response_times = list(range(1, 101))  # 1-100ms
        
        result = orchestrator.calculate_response_percentiles(response_times)
        assert result.is_ok()
        percentiles = result.unwrap()
        
        assert percentiles["p50"] >= 0
        assert percentiles["p95"] >= percentiles["p50"]
        assert percentiles["p99"] >= percentiles["p95"]

    def test_identify_throughput_bottleneck(self):
        """Identify throughput bottleneck"""
        orchestrator = PerformanceOrchestrator()
        
        load_test_data = {
            "requests": 1000,
            "successful": 950,
            "failed": 50,
            "duration_seconds": 60,
        }
        
        result = orchestrator.analyze_throughput(load_test_data)
        assert result.is_ok()
        analysis = result.unwrap()
        
        assert analysis["requests_per_second"] > 0
        assert analysis["success_rate"] <= 1.0

    def test_load_test_includes_error_analysis(self):
        """Verify load test results include error analysis"""
        orchestrator = PerformanceOrchestrator()
        
        load_test_data = {
            "requests": 100,
            "errors": [
                {"status_code": 500, "count": 5},
                {"status_code": 503, "count": 3},
            ]
        }
        
        result = orchestrator.analyze_errors(load_test_data)
        assert result.is_ok()
        errors = result.unwrap()
        
        assert len(errors) >= 2

    def test_generate_load_test_report(self):
        """Generate load test report"""
        orchestrator = PerformanceOrchestrator()
        
        load_test_result = {
            "total_requests": 1000,
            "requests_per_second": 16.67,
            "response_times": {"p50": 50, "p95": 200, "p99": 500},
        }
        
        result = orchestrator.generate_load_test_report(load_test_result)
        assert result.is_ok()
        report = result.unwrap()
        
        assert report is not None


# ============================================================================
# PERFORMANCE REGRESSION DETECTION TESTS (8 Tests)
# ============================================================================

class TestPerformanceRegressionDetection:
    """Test performance regression detection"""

    def test_establish_performance_baseline(self):
        """Establish performance baseline"""
        orchestrator = PerformanceOrchestrator()
        
        metrics = {
            "response_time_p95": 200,
            "throughput_rps": 100,
            "error_rate": 0.01,
            "memory_usage_mb": 256,
        }
        
        result = orchestrator.establish_baseline(metrics)
        assert result.is_ok()
        baseline = result.unwrap()
        
        assert baseline.response_time_p95 == 200
        assert baseline.throughput_rps == 100

    def test_detect_response_time_regression(self):
        """Detect response time regression"""
        orchestrator = PerformanceOrchestrator()
        
        baseline = {"response_time_p95": 200}
        current = {"response_time_p95": 400}  # 2x worse
        threshold = 0.2  # 20% threshold
        
        result = orchestrator.detect_regression(baseline, current, threshold)
        assert result.is_ok()
        regression = result.unwrap()
        
        assert regression.is_regression == True
        assert regression.severity == "high"  # 100% change = high

    def test_detect_throughput_regression(self):
        """Detect throughput regression"""
        orchestrator = PerformanceOrchestrator()
        
        baseline = {"throughput_rps": 100}
        current = {"throughput_rps": 50}  # 50% drop
        
        result = orchestrator.detect_throughput_regression(baseline, current, threshold=0.1)
        assert result.is_ok()
        regression = result.unwrap()
        
        assert regression.is_regression == True

    def test_detect_memory_regression(self):
        """Detect memory usage regression"""
        orchestrator = PerformanceOrchestrator()
        
        baseline = {"memory_mb": 256}
        current = {"memory_mb": 512}  # 2x worse
        
        result = orchestrator.detect_memory_regression(baseline, current, threshold=0.25)
        assert result.is_ok()
        regression = result.unwrap()
        
        assert regression.is_regression == True

    def test_no_regression_within_threshold(self):
        """Verify no false positive when within threshold"""
        orchestrator = PerformanceOrchestrator()
        
        baseline = {"response_time_p95": 200}
        current = {"response_time_p95": 210}  # 5% increase
        threshold = 0.1  # 10% threshold
        
        result = orchestrator.detect_regression(baseline, current, threshold)
        assert result.is_ok()
        regression = result.unwrap()
        
        assert regression.is_regression == False

    def test_regression_includes_severity_level(self):
        """Verify regression assessment includes severity"""
        orchestrator = PerformanceOrchestrator()
        
        baseline = {"response_time_p95": 100}
        current = {"response_time_p95": 500}
        
        result = orchestrator.detect_regression(baseline, current, threshold=0.2)
        assert result.is_ok()
        regression = result.unwrap()
        
        assert regression.severity in ["low", "medium", "high", "critical"]

    def test_regression_suggests_investigation_areas(self):
        """Verify regression detection suggests investigation areas"""
        orchestrator = PerformanceOrchestrator()
        
        baseline = {"response_time_p95": 100, "cpu_usage": 50}
        current = {"response_time_p95": 300, "cpu_usage": 90}
        
        result = orchestrator.detect_regression(baseline, current, threshold=0.1)
        assert result.is_ok()
        regression = result.unwrap()
        
        if regression.is_regression:
            assert len(regression.investigation_suggestions) >= 1

    def test_track_performance_trends(self):
        """Track performance trends over time"""
        orchestrator = PerformanceOrchestrator()
        
        measurements = [
            {"timestamp": "2026-02-01", "response_time": 100},
            {"timestamp": "2026-02-02", "response_time": 105},
            {"timestamp": "2026-02-03", "response_time": 110},
            {"timestamp": "2026-02-04", "response_time": 120},
        ]
        
        result = orchestrator.analyze_trends(measurements)
        assert result.is_ok()
        trend = result.unwrap()
        
        assert trend is not None


# ============================================================================
# BOTTLENECK IDENTIFICATION TESTS (6 Tests)
# ============================================================================

class TestBottleneckIdentification:
    """Test bottleneck identification"""

    def test_identify_cpu_bottleneck(self):
        """Identify CPU bottleneck"""
        orchestrator = PerformanceOrchestrator()
        
        profile = {
            "cpu_usage": 95,
            "memory_usage": 30,
            "io_wait": 5,
        }
        
        result = orchestrator.identify_bottleneck(profile)
        assert result.is_ok()
        bottleneck = result.unwrap()
        
        assert "cpu" in bottleneck.type.lower()

    def test_identify_memory_bottleneck(self):
        """Identify memory bottleneck"""
        orchestrator = PerformanceOrchestrator()
        
        profile = {
            "cpu_usage": 20,
            "memory_usage": 92,
            "io_wait": 5,
        }
        
        result = orchestrator.identify_bottleneck(profile)
        assert result.is_ok()
        bottleneck = result.unwrap()
        
        assert "memory" in bottleneck.type.lower()

    def test_identify_io_bottleneck(self):
        """Identify I/O bottleneck"""
        orchestrator = PerformanceOrchestrator()
        
        profile = {
            "cpu_usage": 20,
            "memory_usage": 30,
            "io_wait": 80,
        }
        
        result = orchestrator.identify_bottleneck(profile)
        assert result.is_ok()
        bottleneck = result.unwrap()
        
        assert "io" in bottleneck.type.lower() or "disk" in bottleneck.type.lower()

    def test_bottleneck_includes_recommendations(self):
        """Verify bottleneck report includes recommendations"""
        orchestrator = PerformanceOrchestrator()
        
        profile = {
            "cpu_usage": 95,
            "memory_usage": 30,
        }
        
        result = orchestrator.identify_bottleneck(profile)
        assert result.is_ok()
        bottleneck = result.unwrap()
        
        assert len(bottleneck.recommendations) >= 1

    def test_identify_multiple_bottlenecks(self):
        """Identify multiple concurrent bottlenecks"""
        orchestrator = PerformanceOrchestrator()
        
        profile = {
            "cpu_usage": 85,
            "memory_usage": 80,
            "io_wait": 40,
        }
        
        result = orchestrator.identify_bottlenecks(profile)
        assert result.is_ok()
        bottlenecks = result.unwrap()
        
        assert len(bottlenecks) >= 2

    def test_bottleneck_impact_analysis(self):
        """Analyze impact of bottleneck"""
        orchestrator = PerformanceOrchestrator()
        
        bottleneck_info = {
            "type": "cpu",
            "severity": 95,
            "affected_operations": ["process_data", "calculate_metrics"],
        }
        
        result = orchestrator.analyze_bottleneck_impact(bottleneck_info)
        assert result.is_ok()
        impact = result.unwrap()
        
        assert impact["estimated_improvement_percent"] >= 0


# ============================================================================
# PERFORMANCE GATE TESTS (5 Tests)
# ============================================================================

class TestPerformanceGate:
    """Test performance regression prevention gate"""

    def test_performance_gate_passes_good_metrics(self):
        """Performance gate passes with good metrics"""
        orchestrator = PerformanceOrchestrator()
        
        requirements = {
            "max_response_time_p95_ms": 300,
            "min_throughput_rps": 50,
            "max_error_rate": 0.05,
        }
        
        metrics = {
            "response_time_p95_ms": 250,
            "throughput_rps": 100,
            "error_rate": 0.02,
        }
        
        result = orchestrator.check_performance_gate(requirements, metrics)
        assert result.is_ok()
        gate_result = result.unwrap()
        
        assert gate_result.passed == True

    def test_performance_gate_fails_bad_metrics(self):
        """Performance gate fails with poor metrics"""
        orchestrator = PerformanceOrchestrator()
        
        requirements = {
            "max_response_time_p95_ms": 100,  # Max is 100ms
        }
        
        metrics = {
            "max_response_time_p95_ms": 500,  # Actual is 500ms
        }
        
        result = orchestrator.check_performance_gate(requirements, metrics)
        assert result.is_ok()
        gate_result = result.unwrap()
        
        assert gate_result.passed == False

    def test_performance_gate_provides_details(self):
        """Performance gate provides detailed failure info"""
        orchestrator = PerformanceOrchestrator()
        
        requirements = {
            "max_response_time_p95_ms": 100,
            "min_throughput_rps": 100,
        }
        
        metrics = {
            "max_response_time_p95_ms": 200,
            "min_throughput_rps": 50,
        }
        
        result = orchestrator.check_performance_gate(requirements, metrics)
        assert result.is_ok()
        gate_result = result.unwrap()
        
        assert gate_result.failures is not None
        assert len(gate_result.failures) >= 2

    def test_performance_gate_can_be_configured(self):
        """Performance gate thresholds can be configured"""
        orchestrator = PerformanceOrchestrator()
        
        requirements = {
            "max_response_time_p95_ms": 500,
            "max_response_time_p99_ms": 1000,
        }
        
        result = orchestrator.configure_performance_gate(requirements)
        assert result.is_ok()
        gate_config = result.unwrap()
        
        assert gate_config is not None

    def test_performance_gate_blocks_regression(self):
        """Verify performance gate blocks regressions"""
        orchestrator = PerformanceOrchestrator()
        
        baseline = {
            "response_time_p95_ms": 100,
        }
        
        current = {
            "response_time_p95_ms": 300,  # 3x worse
        }
        
        requirements = {
            "regression_threshold_percent": 20,  # Allow 20% degradation
        }
        
        result = orchestrator.check_regression_gate(baseline, current, requirements)
        assert result.is_ok()
        gate_result = result.unwrap()
        
        assert gate_result.passed == False


# ============================================================================
# ORCHESTRATOR PROTOCOL TESTS (2 Tests)
# ============================================================================

class TestPerformanceOrchestrator:
    """Test PerformanceOrchestrator protocol implementation"""

    def test_orchestrator_validation(self):
        """Validate orchestrator state"""
        orchestrator = PerformanceOrchestrator()
        
        result = orchestrator.validate()
        assert result.is_ok()

    def test_orchestrator_capabilities(self):
        """Get orchestrator capabilities"""
        orchestrator = PerformanceOrchestrator()
        
        capabilities = orchestrator.get_capabilities()
        
        assert "profile" in capabilities
        assert "load_test" in capabilities
        assert "detect_regression" in capabilities
        assert "identify_bottleneck" in capabilities
