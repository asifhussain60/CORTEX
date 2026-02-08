"""
Phase 52 S6: LoadTestOrchestrator & Regression Detection - Test Specifications

RED Phase: Comprehensive test specifications for load test generation,
baseline tracking, performance regression detection, and SLA validation.

Acceptance Criteria:
- AC-PHASE52-S6-001: Generate k6/Locust test from OpenAPI spec
- AC-PHASE52-S6-002: Track performance baseline in git
- AC-PHASE52-S6-003: Block PRs with >10% regression
"""

import pytest
import json
import tempfile
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class LoadTestFramework(Enum):
    """Supported load testing frameworks."""
    K6 = "k6"
    LOCUST = "locust"


class SLAMetric(Enum):
    """SLA metrics to track."""
    P95_LATENCY = "p95_latency"      # 95th percentile latency (ms)
    P99_LATENCY = "p99_latency"      # 99th percentile latency (ms)
    ERROR_RATE = "error_rate"        # Percentage of failed requests
    THROUGHPUT = "throughput"        # Requests per second


class RegressionSeverity(Enum):
    """Regression severity classification."""
    CRITICAL = "critical"      # >50% regression
    HIGH = "high"              # 20-50% regression
    MEDIUM = "medium"          # 10-20% regression
    LOW = "low"                # 5-10% regression
    NONE = "none"              # <5% regression


@dataclass
class APIEndpoint:
    """API endpoint definition from OpenAPI spec."""
    path: str
    method: str
    description: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    request_body_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    weight: float = 1.0        # Traffic distribution weight


@dataclass
class LoadTestScenario:
    """Load test scenario configuration."""
    name: str
    endpoints: List[APIEndpoint]
    users: int = 10            # Number of concurrent users
    ramp_up_seconds: int = 60  # Time to reach target users
    duration_seconds: int = 300  # Test duration
    target_throughput: Optional[float] = None  # Requests per second
    framework: LoadTestFramework = LoadTestFramework.K6


@dataclass
class SLAThreshold:
    """SLA threshold for metric."""
    metric: SLAMetric
    threshold_value: float
    unit: str                  # "ms", "%", "req/s"


@dataclass
class LoadTestRun:
    """Results from single load test execution."""
    run_id: str
    scenario: LoadTestScenario
    started_at: datetime
    completed_at: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    p50_latency: float         # Milliseconds
    p95_latency: float
    p99_latency: float
    error_rate: float          # Percentage (0-100)
    throughput: float          # Requests per second
    sla_violations: List[str] = field(default_factory=list)  # List of violated SLAs


@dataclass
class PerformanceBaseline:
    """Stored performance baseline for comparison."""
    version: str               # Git commit SHA or version tag
    timestamp: datetime
    framework: LoadTestFramework
    scenario_name: str
    p50_latency: float
    p95_latency: float
    p99_latency: float
    error_rate: float
    throughput: float


@dataclass
class RegressionAnalysis:
    """Analysis of performance regression."""
    current_run: LoadTestRun
    baseline: PerformanceBaseline
    has_regression: bool
    severity: RegressionSeverity
    metrics_changed: Dict[str, Tuple[float, float, float]]  # metric -> (baseline, current, change_percent)
    recommendation: str


class K6TestGenerator:
    """Generate k6 load test scripts from OpenAPI spec."""
    
    def __init__(self):
        """Initialize k6 generator."""
        self.scenario: Optional[LoadTestScenario] = None
    
    def generate_script(self, scenario: LoadTestScenario) -> str:
        """
        Generate k6 JavaScript load test script.
        
        Args:
            scenario: LoadTestScenario with endpoints
        
        Returns:
            k6 script as JavaScript string
        """
        self.scenario = scenario
        
        script_parts = [
            "import http from 'k6/http';",
            "import { check, sleep } from 'k6';",
            "",
            "export let options = {",
            f"  stages: [",
            f"    {{ duration: '{scenario.ramp_up_seconds}s', target: {scenario.users} }},",
            f"    {{ duration: '{scenario.duration_seconds}s', target: {scenario.users} }},",
            f"    {{ duration: '10s', target: 0 }},",
            f"  ],",
            f"  thresholds: {{",
            f"    'http_req_duration': ['p(95)<500', 'p(99)<1000'],",
            f"    'http_req_failed': ['rate<0.1'],",
            f"  }},",
            f"}};",
            "",
            "export default function() {",
        ]
        
        # Add endpoint calls
        for endpoint in scenario.endpoints:
            script_parts.extend([
                f"  // {endpoint.description or endpoint.path}",
                f"  let res = http.{endpoint.method.lower()}('http://localhost:8000{endpoint.path}');",
                f"  check(res, {{",
                f"    'status is 200': (r) => r.status === 200,",
                f"    'response time < 500ms': (r) => r.timings.duration < 500,",
                f"  }});",
                f"  sleep(1);",
                "",
            ])
        
        script_parts.append("}")
        
        return "\n".join(script_parts)


class LocustTestGenerator:
    """Generate Locust load test scripts from OpenAPI spec."""
    
    def __init__(self):
        """Initialize Locust generator."""
        self.scenario: Optional[LoadTestScenario] = None
    
    def generate_script(self, scenario: LoadTestScenario) -> str:
        """
        Generate Locust Python load test script.
        
        Args:
            scenario: LoadTestScenario with endpoints
        
        Returns:
            Locust script as Python string
        """
        self.scenario = scenario
        
        script_parts = [
            "from locust import HttpUser, task, between",
            "",
            "class LoadTestUser(HttpUser):",
            f"    wait_time = between(0.5, 2.0)",
            "",
        ]
        
        # Add task methods
        for idx, endpoint in enumerate(scenario.endpoints):
            method_name = f"endpoint_{idx}"
            script_parts.extend([
                f"    @task({int(endpoint.weight * 10)})",
                f"    def {method_name}(self):",
                f"        # {endpoint.description or endpoint.path}",
                f"        self.client.{endpoint.method.lower()}('{endpoint.path}')",
                "",
            ])
        
        return "\n".join(script_parts)


class BaselineTracker:
    """Track performance baselines in git."""
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize baseline tracker.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.baseline_file = os.path.join(repo_path, ".performance_baselines.json")
    
    def save_baseline(self, run: LoadTestRun, version: str) -> PerformanceBaseline:
        """
        Save performance baseline from test run.
        
        Args:
            run: LoadTestRun with performance data
            version: Version identifier (commit SHA, tag, etc)
        
        Returns:
            Saved PerformanceBaseline
        """
        baseline = PerformanceBaseline(
            version=version,
            timestamp=datetime.now(),
            framework=run.scenario.framework,
            scenario_name=run.scenario.name,
            p50_latency=run.p50_latency,
            p95_latency=run.p95_latency,
            p99_latency=run.p99_latency,
            error_rate=run.error_rate,
            throughput=run.throughput
        )
        
        self.baselines[version] = baseline
        return baseline
    
    def get_baseline(self, version: str) -> Optional[PerformanceBaseline]:
        """
        Get baseline for version.
        
        Args:
            version: Version identifier
        
        Returns:
            PerformanceBaseline or None if not found
        """
        return self.baselines.get(version)
    
    def list_baselines(self) -> List[PerformanceBaseline]:
        """
        List all stored baselines.
        
        Returns:
            List of PerformanceBaseline objects
        """
        return list(self.baselines.values())


class RegressionDetector:
    """Detect performance regressions vs baseline."""
    
    def __init__(self, regression_threshold_percent: float = 10.0):
        """
        Initialize regression detector.
        
        Args:
            regression_threshold_percent: Threshold for regression (default 10%)
        """
        self.regression_threshold = regression_threshold_percent
    
    def analyze(self, current_run: LoadTestRun, baseline: PerformanceBaseline) -> RegressionAnalysis:
        """
        Analyze performance regression.
        
        Args:
            current_run: Current load test run
            baseline: Baseline to compare against
        
        Returns:
            RegressionAnalysis with findings
        """
        metrics_changed = {}
        has_regression = False
        
        # Compare P95 latency
        p95_change = ((current_run.p95_latency - baseline.p95_latency) / baseline.p95_latency) * 100
        metrics_changed["p95_latency"] = (baseline.p95_latency, current_run.p95_latency, p95_change)
        
        # Compare error rate
        error_change = ((current_run.error_rate - baseline.error_rate) / max(baseline.error_rate, 0.1)) * 100
        metrics_changed["error_rate"] = (baseline.error_rate, current_run.error_rate, error_change)
        
        # Compare throughput
        throughput_change = ((current_run.throughput - baseline.throughput) / baseline.throughput) * 100
        metrics_changed["throughput"] = (baseline.throughput, current_run.throughput, throughput_change)
        
        # Determine severity
        max_regression = max(abs(p95_change), abs(error_change), abs(-throughput_change))
        
        if max_regression >= 50:
            severity = RegressionSeverity.CRITICAL
            has_regression = True
        elif max_regression >= 20:
            severity = RegressionSeverity.HIGH
            has_regression = True
        elif max_regression >= 10:
            severity = RegressionSeverity.MEDIUM
            has_regression = True
        elif max_regression >= 5:
            severity = RegressionSeverity.LOW
            has_regression = True
        else:
            severity = RegressionSeverity.NONE
            has_regression = False
        
        # Generate recommendation
        if severity == RegressionSeverity.CRITICAL:
            recommendation = "CRITICAL: Block PR - Major performance regression detected"
        elif severity == RegressionSeverity.HIGH:
            recommendation = "HIGH: Investigate regression - Consider blocking PR"
        elif severity == RegressionSeverity.MEDIUM:
            recommendation = "MEDIUM: Performance regression detected - Needs review"
        elif severity == RegressionSeverity.LOW:
            recommendation = "LOW: Minor performance change - Monitor"
        else:
            recommendation = "NONE: No significant regression detected"
        
        return RegressionAnalysis(
            current_run=current_run,
            baseline=baseline,
            has_regression=has_regression,
            severity=severity,
            metrics_changed=metrics_changed,
            recommendation=recommendation
        )


class SLAValidator:
    """Validate load test results against SLA thresholds."""
    
    def __init__(self):
        """Initialize SLA validator."""
        self.thresholds: List[SLAThreshold] = []
    
    def add_threshold(self, metric: SLAMetric, threshold: float, unit: str) -> None:
        """
        Add SLA threshold.
        
        Args:
            metric: SLAMetric to validate
            threshold: Threshold value
            unit: Unit of measurement (ms, %, req/s)
        """
        self.thresholds.append(SLAThreshold(
            metric=metric,
            threshold_value=threshold,
            unit=unit
        ))
    
    def validate(self, run: LoadTestRun) -> Tuple[bool, List[str]]:
        """
        Validate run against SLA thresholds.
        
        Args:
            run: LoadTestRun to validate
        
        Returns:
            Tuple of (all_pass, violations_list)
        """
        violations = []
        
        for threshold in self.thresholds:
            if threshold.metric == SLAMetric.P95_LATENCY:
                if run.p95_latency > threshold.threshold_value:
                    violations.append(
                        f"P95 latency {run.p95_latency}ms exceeds threshold {threshold.threshold_value}ms"
                    )
            
            elif threshold.metric == SLAMetric.P99_LATENCY:
                if run.p99_latency > threshold.threshold_value:
                    violations.append(
                        f"P99 latency {run.p99_latency}ms exceeds threshold {threshold.threshold_value}ms"
                    )
            
            elif threshold.metric == SLAMetric.ERROR_RATE:
                if run.error_rate > threshold.threshold_value:
                    violations.append(
                        f"Error rate {run.error_rate}% exceeds threshold {threshold.threshold_value}%"
                    )
            
            elif threshold.metric == SLAMetric.THROUGHPUT:
                if run.throughput < threshold.threshold_value:
                    violations.append(
                        f"Throughput {run.throughput} req/s below threshold {threshold.threshold_value} req/s"
                    )
        
        return len(violations) == 0, violations


class LoadTestOrchestrator:
    """Orchestrate load testing, baseline tracking, and regression detection."""
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize load test orchestrator.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path
        self.baseline_tracker = BaselineTracker(repo_path)
        self.regression_detector = RegressionDetector()
        self.sla_validator = SLAValidator()
        self.test_runs: List[LoadTestRun] = []
    
    def generate_test_script(self, scenario: LoadTestScenario) -> str:
        """
        Generate load test script for scenario.
        
        Args:
            scenario: LoadTestScenario to generate test for
        
        Returns:
            Test script as string
        """
        if scenario.framework == LoadTestFramework.K6:
            generator = K6TestGenerator()
            return generator.generate_script(scenario)
        elif scenario.framework == LoadTestFramework.LOCUST:
            generator = LocustTestGenerator()
            return generator.generate_script(scenario)
        else:
            raise ValueError(f"Unsupported framework: {scenario.framework}")
    
    def save_test_script(self, scenario: LoadTestScenario, output_path: str) -> str:
        """
        Save generated test script to file.
        
        Args:
            scenario: LoadTestScenario to generate test for
            output_path: Path to save script
        
        Returns:
            Path to saved script
        """
        script = self.generate_test_script(scenario)
        
        with open(output_path, 'w') as f:
            f.write(script)
        
        return output_path
    
    def record_run(self, run: LoadTestRun) -> None:
        """
        Record load test run.
        
        Args:
            run: LoadTestRun to record
        """
        self.test_runs.append(run)
    
    def save_baseline(self, run: LoadTestRun, version: str) -> PerformanceBaseline:
        """
        Save performance baseline.
        
        Args:
            run: LoadTestRun with data
            version: Version identifier
        
        Returns:
            Saved PerformanceBaseline
        """
        return self.baseline_tracker.save_baseline(run, version)
    
    def detect_regression(self, current_run: LoadTestRun, baseline_version: str) -> Optional[RegressionAnalysis]:
        """
        Detect regression vs baseline.
        
        Args:
            current_run: Current LoadTestRun
            baseline_version: Version to compare against
        
        Returns:
            RegressionAnalysis or None if baseline not found
        """
        baseline = self.baseline_tracker.get_baseline(baseline_version)
        if baseline is None:
            return None
        
        return self.regression_detector.analyze(current_run, baseline)
    
    def validate_sla(self, run: LoadTestRun) -> Tuple[bool, List[str]]:
        """
        Validate run against SLA thresholds.
        
        Args:
            run: LoadTestRun to validate
        
        Returns:
            Tuple of (all_pass, violations)
        """
        return self.sla_validator.validate(run)


# ============================================================================
# Test Specifications (RED Phase)
# ============================================================================

class TestK6TestGenerator:
    """AC-PHASE52-S6-001: Generate k6 load tests"""
    
    def test_generate_k6_script(self):
        """Generate k6 load test script."""
        endpoint = APIEndpoint(
            path="/api/users",
            method="GET",
            description="Get users",
            weight=1.0
        )
        
        scenario = LoadTestScenario(
            name="User API Load Test",
            endpoints=[endpoint],
            users=50,
            ramp_up_seconds=60,
            duration_seconds=300,
            framework=LoadTestFramework.K6
        )
        
        generator = K6TestGenerator()
        script = generator.generate_script(scenario)
        
        assert script is not None
        assert len(script) > 0
        assert "import http from 'k6/http'" in script
        assert "import { check, sleep } from 'k6'" in script
        assert "export default function()" in script
    
    def test_k6_script_includes_endpoints(self):
        """Verify k6 script includes all endpoints."""
        endpoints = [
            APIEndpoint(path="/api/users", method="GET"),
            APIEndpoint(path="/api/posts", method="GET"),
            APIEndpoint(path="/api/comments", method="POST"),
        ]
        
        scenario = LoadTestScenario(
            name="Multi-endpoint test",
            endpoints=endpoints,
            framework=LoadTestFramework.K6
        )
        
        generator = K6TestGenerator()
        script = generator.generate_script(scenario)
        
        for endpoint in endpoints:
            assert endpoint.path in script
            assert endpoint.method.lower() in script
    
    def test_k6_script_includes_thresholds(self):
        """Verify k6 script includes SLA thresholds."""
        endpoint = APIEndpoint(path="/api/test", method="GET")
        scenario = LoadTestScenario(
            name="Threshold test",
            endpoints=[endpoint],
            framework=LoadTestFramework.K6
        )
        
        generator = K6TestGenerator()
        script = generator.generate_script(scenario)
        
        assert "thresholds" in script
        assert "p(95)<500" in script
        assert "p(99)<1000" in script


class TestLocustTestGenerator:
    """AC-PHASE52-S6-001: Generate Locust load tests"""
    
    def test_generate_locust_script(self):
        """Generate Locust load test script."""
        endpoint = APIEndpoint(
            path="/api/users",
            method="GET",
            description="Get users"
        )
        
        scenario = LoadTestScenario(
            name="Locust User Test",
            endpoints=[endpoint],
            framework=LoadTestFramework.LOCUST
        )
        
        generator = LocustTestGenerator()
        script = generator.generate_script(scenario)
        
        assert script is not None
        assert len(script) > 0
        assert "from locust import HttpUser, task, between" in script
        assert "class LoadTestUser(HttpUser):" in script
    
    def test_locust_script_includes_endpoints(self):
        """Verify Locust script includes all endpoints."""
        endpoints = [
            APIEndpoint(path="/api/users", method="GET", weight=2.0),
            APIEndpoint(path="/api/posts", method="GET", weight=1.0),
        ]
        
        scenario = LoadTestScenario(
            name="Multi-endpoint Locust",
            endpoints=endpoints,
            framework=LoadTestFramework.LOCUST
        )
        
        generator = LocustTestGenerator()
        script = generator.generate_script(scenario)
        
        for endpoint in endpoints:
            assert endpoint.path in script


class TestBaselineTracker:
    """AC-PHASE52-S6-002: Track performance baseline"""
    
    def test_save_baseline(self):
        """Save performance baseline."""
        from datetime import datetime, timedelta
        
        run = LoadTestRun(
            run_id="run_001",
            scenario=LoadTestScenario(name="Test", endpoints=[]),
            started_at=datetime.now(),
            completed_at=datetime.now() + timedelta(seconds=300),
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            p50_latency=100.0,
            p95_latency=250.0,
            p99_latency=500.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        tracker = BaselineTracker()
        baseline = tracker.save_baseline(run, "v1.0.0")
        
        assert baseline is not None
        assert baseline.version == "v1.0.0"
        assert baseline.p95_latency == 250.0
    
    def test_get_baseline(self):
        """Retrieve saved baseline."""
        from datetime import datetime, timedelta
        
        run = LoadTestRun(
            run_id="run_002",
            scenario=LoadTestScenario(name="Test", endpoints=[]),
            started_at=datetime.now(),
            completed_at=datetime.now() + timedelta(seconds=300),
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            p50_latency=100.0,
            p95_latency=250.0,
            p99_latency=500.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        tracker = BaselineTracker()
        tracker.save_baseline(run, "v1.0.0")
        
        retrieved = tracker.get_baseline("v1.0.0")
        assert retrieved is not None
        assert retrieved.version == "v1.0.0"
    
    def test_list_baselines(self):
        """List all baselines."""
        from datetime import datetime, timedelta
        
        tracker = BaselineTracker()
        
        for i in range(3):
            run = LoadTestRun(
                run_id=f"run_{i:03d}",
                scenario=LoadTestScenario(name="Test", endpoints=[]),
                started_at=datetime.now(),
                completed_at=datetime.now() + timedelta(seconds=300),
                total_requests=1000,
                successful_requests=990,
                failed_requests=10,
                p50_latency=100.0,
                p95_latency=250.0,
                p99_latency=500.0,
                error_rate=1.0,
                throughput=3.33
            )
            tracker.save_baseline(run, f"v1.{i}.0")
        
        baselines = tracker.list_baselines()
        assert len(baselines) == 3


class TestRegressionDetection:
    """AC-PHASE52-S6-003: Block PRs with >10% regression"""
    
    def test_detect_regression_high_latency(self):
        """Detect regression in P95 latency."""
        from datetime import datetime, timedelta
        
        # Baseline
        baseline = PerformanceBaseline(
            version="v1.0.0",
            timestamp=datetime.now(),
            framework=LoadTestFramework.K6,
            scenario_name="Test",
            p50_latency=100.0,
            p95_latency=250.0,
            p99_latency=500.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        # Current with 30% regression
        current_run = LoadTestRun(
            run_id="run_current",
            scenario=LoadTestScenario(name="Test", endpoints=[]),
            started_at=datetime.now(),
            completed_at=datetime.now() + timedelta(seconds=300),
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            p50_latency=100.0,
            p95_latency=325.0,  # 30% increase
            p99_latency=500.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        detector = RegressionDetector(regression_threshold_percent=10.0)
        analysis = detector.analyze(current_run, baseline)
        
        assert analysis.has_regression is True
        assert analysis.severity == RegressionSeverity.HIGH
    
    def test_no_regression_within_threshold(self):
        """No regression when within threshold."""
        from datetime import datetime, timedelta
        
        baseline = PerformanceBaseline(
            version="v1.0.0",
            timestamp=datetime.now(),
            framework=LoadTestFramework.K6,
            scenario_name="Test",
            p50_latency=100.0,
            p95_latency=250.0,
            p99_latency=500.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        # Current with 3% improvement
        current_run = LoadTestRun(
            run_id="run_current",
            scenario=LoadTestScenario(name="Test", endpoints=[]),
            started_at=datetime.now(),
            completed_at=datetime.now() + timedelta(seconds=300),
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            p50_latency=100.0,
            p95_latency=242.5,  # 3% improvement
            p99_latency=500.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        detector = RegressionDetector()
        analysis = detector.analyze(current_run, baseline)
        
        assert analysis.has_regression is False
        assert analysis.severity == RegressionSeverity.NONE


class TestSLAValidator:
    """SLA threshold validation"""
    
    def test_validate_latency_sla_pass(self):
        """Validate P95 latency SLA passes."""
        from datetime import datetime, timedelta
        
        validator = SLAValidator()
        validator.add_threshold(SLAMetric.P95_LATENCY, 500.0, "ms")
        
        run = LoadTestRun(
            run_id="run_001",
            scenario=LoadTestScenario(name="Test", endpoints=[]),
            started_at=datetime.now(),
            completed_at=datetime.now() + timedelta(seconds=300),
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            p50_latency=100.0,
            p95_latency=250.0,  # Below threshold
            p99_latency=400.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        passed, violations = validator.validate(run)
        assert passed is True
        assert len(violations) == 0
    
    def test_validate_latency_sla_fail(self):
        """Validate P95 latency SLA fails."""
        from datetime import datetime, timedelta
        
        validator = SLAValidator()
        validator.add_threshold(SLAMetric.P95_LATENCY, 200.0, "ms")
        
        run = LoadTestRun(
            run_id="run_001",
            scenario=LoadTestScenario(name="Test", endpoints=[]),
            started_at=datetime.now(),
            completed_at=datetime.now() + timedelta(seconds=300),
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            p50_latency=100.0,
            p95_latency=250.0,  # Above threshold
            p99_latency=400.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        passed, violations = validator.validate(run)
        assert passed is False
        assert len(violations) > 0


class TestLoadTestOrchestrator:
    """AC-PHASE52-S6-001+002+003: Full orchestrator integration"""
    
    def test_orchestrator_generates_script(self):
        """Orchestrator can generate test scripts."""
        endpoint = APIEndpoint(path="/api/test", method="GET")
        scenario = LoadTestScenario(
            name="Test",
            endpoints=[endpoint],
            framework=LoadTestFramework.K6
        )
        
        orchestrator = LoadTestOrchestrator()
        script = orchestrator.generate_test_script(scenario)
        
        assert script is not None
        assert len(script) > 0
    
    def test_orchestrator_saves_script(self):
        """Orchestrator can save test script to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            endpoint = APIEndpoint(path="/api/test", method="GET")
            scenario = LoadTestScenario(
                name="Test",
                endpoints=[endpoint],
                framework=LoadTestFramework.K6
            )
            
            orchestrator = LoadTestOrchestrator(tmpdir)
            script_path = os.path.join(tmpdir, "test_script.js")
            
            result = orchestrator.save_test_script(scenario, script_path)
            
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
    
    def test_orchestrator_tracks_baselines(self):
        """Orchestrator tracks performance baselines."""
        from datetime import datetime, timedelta
        
        orchestrator = LoadTestOrchestrator()
        
        run = LoadTestRun(
            run_id="run_001",
            scenario=LoadTestScenario(name="Test", endpoints=[]),
            started_at=datetime.now(),
            completed_at=datetime.now() + timedelta(seconds=300),
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            p50_latency=100.0,
            p95_latency=250.0,
            p99_latency=500.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        baseline = orchestrator.save_baseline(run, "v1.0.0")
        
        assert baseline is not None
        assert baseline.version == "v1.0.0"
    
    def test_orchestrator_detects_regression(self):
        """Orchestrator detects performance regression."""
        from datetime import datetime, timedelta
        
        orchestrator = LoadTestOrchestrator()
        
        # Save baseline
        baseline_run = LoadTestRun(
            run_id="run_baseline",
            scenario=LoadTestScenario(name="Test", endpoints=[]),
            started_at=datetime.now(),
            completed_at=datetime.now() + timedelta(seconds=300),
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            p50_latency=100.0,
            p95_latency=250.0,
            p99_latency=500.0,
            error_rate=1.0,
            throughput=3.33
        )
        orchestrator.save_baseline(baseline_run, "v1.0.0")
        
        # Current with regression
        current_run = LoadTestRun(
            run_id="run_current",
            scenario=LoadTestScenario(name="Test", endpoints=[]),
            started_at=datetime.now(),
            completed_at=datetime.now() + timedelta(seconds=300),
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            p50_latency=100.0,
            p95_latency=325.0,  # 30% regression
            p99_latency=500.0,
            error_rate=1.0,
            throughput=3.33
        )
        
        analysis = orchestrator.detect_regression(current_run, "v1.0.0")
        
        assert analysis is not None
        assert analysis.has_regression is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
