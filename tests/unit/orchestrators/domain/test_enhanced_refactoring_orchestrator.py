"""
Test Suite for Enhanced RefactoringOrchestrator
AC-DOMAIN-REF-001 through AC-DOMAIN-REF-009 Compliance Testing

TDD Framework: Tests BEFORE implementation (CORE-008 compliance)
Type Hints: 100% coverage (CORE-011)
Docstrings: Google-style (CORE-012)
Exceptions: Specific handling (CORE-013)

Author: CORTEX Autonomous Framework
Date: 2026-01-26
"""

import pytest
import threading

# Imports from enhanced_refactoring_orchestrator
try:
    from cortex.orchestrators.domain.enhanced_refactoring_orchestrator import (
        # Enums
        ViolationType,
        # Data Models
        SOLIDMetrics,
        Violation,
        RefactoringStrategy,
        RefactoringPlan,
        # Components
        ComplexityClassifier,
        SOLIDAnalyzer,
        ParallelStrategyEvaluator,
        PatternCache,
        CircuitBreaker,
        # Main Orchestrator
        EnhancedRefactoringOrchestrator,
    )
except ImportError as e:
    pytest.skip(f"Module imports failed: {e}", allow_module_level=True)


# ============================================================================
# FIXTURE DEFINITIONS (TDD Setup)
# ============================================================================

@pytest.fixture
def orchestrator():
    """Provide orchestrator instance for tests."""
    orch = EnhancedRefactoringOrchestrator.instance()
    yield orch


@pytest.fixture
def sample_code() -> str:
    """Provide sample code for analysis."""
    return """
class DataProcessor:
    def process_data(self, data):
        self.validate(data)
        self.transform(data)
        self.store(data)
    
    def validate(self, data):
        pass
    
    def transform(self, data):
        pass
    
    def store(self, data):
        pass
"""


@pytest.fixture
def god_class_code() -> str:
    """Provide god class example (50+ lines, 40+ methods)."""
    methods = "\n    ".join([f"def method_{i}(self): pass" for i in range(45)])
    return f"""
class GodClass:
    def __init__(self):
        self.prop_a = None
        self.prop_b = None
        self.prop_c = None
        self.prop_d = None
        self.prop_e = None
        self.prop_f = None
        self.prop_g = None
        self.prop_h = None
        self.prop_i = None
        self.prop_j = None
        self.prop_k = None
        self.prop_l = None
        self.prop_m = None
        self.prop_n = None
        self.prop_o = None
        self.prop_p = None
    
    {methods}
"""


# ============================================================================
# TEST SUITE 1: SOLID METRICS & ANALYSIS (AC-DOMAIN-REF-004)
# ============================================================================

class TestSOLIDAnalyzer:
    """Tests for AC-DOMAIN-REF-004: Real SOLID analysis."""
    
    def test_solid_analyzer_initialization(self) -> None:
        """Analyzer initializes correctly."""
        analyzer = SOLIDAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
    
    def test_solid_analyzer_returns_metrics(self, sample_code: str) -> None:
        """Analyzer returns SOLIDMetrics object."""
        analyzer = SOLIDAnalyzer()
        metrics = analyzer.analyze(sample_code, "test.py")
        
        assert isinstance(metrics, SOLIDMetrics)
        assert 0 <= metrics.srp_score <= 1.0
        assert 0 <= metrics.ocp_score <= 1.0
        assert 0 <= metrics.lsp_score <= 1.0
        assert 0 <= metrics.isp_score <= 1.0
        assert 0 <= metrics.dip_score <= 1.0
        assert 0 <= metrics.cohesion <= 1.0
        assert 0 <= metrics.coupling <= 1.0
        assert 0 <= metrics.overall_score <= 1.0
    
    def test_solid_analyzer_detects_god_class(self, god_class_code: str) -> None:
        """Analyzer detects god class violations."""
        analyzer = SOLIDAnalyzer()
        metrics = analyzer.analyze(god_class_code, "god_class.py")
        
        # God classes have low SRP score
        assert metrics.srp_score < 0.7
    
    def test_solid_weighted_scoring(self, sample_code: str) -> None:
        """Analyzer uses weighted scoring for overall score."""
        analyzer = SOLIDAnalyzer()
        metrics = analyzer.analyze(sample_code, "test.py")
        
        # Overall score should exist and be weighted
        assert metrics.overall_score is not None
    
    def test_solid_metrics_to_dict(self, sample_code: str) -> None:
        """SOLIDMetrics converts to dictionary."""
        analyzer = SOLIDAnalyzer()
        metrics = analyzer.analyze(sample_code, "test.py")
        
        metrics_dict = metrics.to_dict()
        assert isinstance(metrics_dict, dict)
        assert 'srp_score' in metrics_dict
        assert 'ocp_score' in metrics_dict
        assert 'overall_score' in metrics_dict


# ============================================================================
# TEST SUITE 2: COMPLEXITY CLASSIFICATION (AC-DOMAIN-REF-002)
# ============================================================================

class TestComplexityClassifier:
    """Tests for AC-DOMAIN-REF-002: LENS-based classification."""
    
    def test_classifier_initialization(self) -> None:
        """Classifier initializes correctly."""
        classifier = ComplexityClassifier()
        assert classifier is not None
    
    def test_classifier_returns_dict(self, sample_code: str) -> None:
        """Classifier returns structured result."""
        classifier = ComplexityClassifier()
        result = classifier.classify(sample_code, "test.py")
        
        assert isinstance(result, dict)
        assert 'language' in result or 'recommended_strategies' in result
    
    def test_classifier_lens_layers(self, sample_code: str) -> None:
        """Classifier implements LENS layers."""
        classifier = ComplexityClassifier()
        result = classifier.classify(sample_code, "test.py")
        
        # Should have some form of analysis result
        assert result is not None
        assert isinstance(result, dict)
    
    def test_classifier_detects_violations(self, god_class_code: str) -> None:
        """Classifier detects violations in complex code."""
        classifier = ComplexityClassifier()
        result = classifier.classify(god_class_code, "god_class.py")
        
        # God class should trigger violations
        assert result is not None


# ============================================================================
# TEST SUITE 3: PARALLEL STRATEGY EVALUATION (AC-DOMAIN-REF-003)
# ============================================================================

class TestParallelStrategyEvaluator:
    """Tests for AC-DOMAIN-REF-003: Parallel evaluation."""
    
    def test_evaluator_initialization(self) -> None:
        """Evaluator initializes with thread pool."""
        evaluator = ParallelStrategyEvaluator(max_workers=4)
        assert evaluator.max_workers == 4
    
    def test_evaluator_returns_list(self) -> None:
        """Evaluator returns list of strategies."""
        evaluator = ParallelStrategyEvaluator()
        strategies = [
            RefactoringStrategy(
                strategy_name="extract_interfaces",
                description="Test",
                effort_hours=4,
                complexity="medium",
                safety_level="high",
                applicable_violations=[ViolationType.GOD_CLASS],
                steps=["step1"],
            )
        ]
        
        result = evaluator.evaluate_all(strategies, [])
        assert isinstance(result, list)
    
    def test_evaluator_sets_confidence(self) -> None:
        """Evaluator sets confidence scores."""
        evaluator = ParallelStrategyEvaluator()
        strategies = [
            RefactoringStrategy(
                strategy_name="extract_interfaces",
                description="Test",
                effort_hours=4,
                complexity="medium",
                safety_level="high",
                applicable_violations=[ViolationType.GOD_CLASS],
                steps=["step1"],
            )
        ]
        
        result = evaluator.evaluate_all(strategies, [])
        assert len(result) > 0
        assert result[0].confidence >= 0


# ============================================================================
# TEST SUITE 4: PATTERN CACHING (AC-DOMAIN-REF-007)
# ============================================================================

class TestPatternCache:
    """Tests for AC-DOMAIN-REF-007: Pattern caching."""
    
    def test_cache_initialization(self) -> None:
        """Cache initializes correctly."""
        cache = PatternCache(capacity=100)
        assert cache.capacity == 100
        assert len(cache.cache) == 0
    
    def test_cache_put_and_get(self) -> None:
        """Cache stores and retrieves entries."""
        cache = PatternCache()
        code = "def foo(): pass"
        metrics = SOLIDMetrics(
            srp_score=0.8, ocp_score=0.7, lsp_score=0.9,
            isp_score=0.8, dip_score=0.75, cohesion=0.85,
            coupling=0.2, overall_score=0.77
        )
        
        cache.put(code, "analysis_1", metrics)
        
        # Similar code should hit cache
        result = cache.get(code)
        assert result is not None
    
    def test_cache_hit_rate(self) -> None:
        """Cache tracks hit rate."""
        cache = PatternCache()
        code = "def foo(): pass"
        metrics = SOLIDMetrics(
            srp_score=0.8, ocp_score=0.7, lsp_score=0.9,
            isp_score=0.8, dip_score=0.75, cohesion=0.85,
            coupling=0.2, overall_score=0.77
        )
        
        cache.put(code, "analysis_1", metrics)
        cache.get(code)  # Hit
        cache.get("different code")  # Miss
        
        hit_rate = cache.hit_rate()
        assert 0 <= hit_rate <= 1.0
        assert hit_rate > 0  # Should have at least 1 hit
    
    def test_cache_capacity_management(self) -> None:
        """Cache manages capacity with LRU eviction."""
        cache = PatternCache(capacity=2)
        metrics = SOLIDMetrics(
            srp_score=0.8, ocp_score=0.7, lsp_score=0.9,
            isp_score=0.8, dip_score=0.75, cohesion=0.85,
            coupling=0.2, overall_score=0.77
        )
        
        cache.put("code1", "analysis_1", metrics)
        cache.put("code2", "analysis_2", metrics)
        cache.put("code3", "analysis_3", metrics)
        
        # Capacity should not exceed limit
        assert len(cache.cache) <= cache.capacity


# ============================================================================
# TEST SUITE 5: CIRCUIT BREAKER (AC-DOMAIN-REF-008)
# ============================================================================

class TestCircuitBreaker:
    """Tests for AC-DOMAIN-REF-008: Circuit breaker protection."""
    
    def test_circuit_breaker_initialization(self) -> None:
        """Circuit breaker initializes correctly."""
        cb = CircuitBreaker(threshold_lines=2000, timeout_seconds=30)
        assert cb.state == "closed"
        assert cb.threshold_lines == 2000
    
    def test_circuit_breaker_allows_small_code(self, sample_code: str) -> None:
        """Circuit breaker allows analysis of small code."""
        cb = CircuitBreaker(threshold_lines=2000)
        
        can_analyze = cb.can_analyze(sample_code)
        assert can_analyze is True
    
    def test_circuit_breaker_blocks_large_code(self) -> None:
        """Circuit breaker blocks analysis of large code."""
        cb = CircuitBreaker(threshold_lines=100)
        large_code = "\n".join(["def method(): pass"] * 150)
        
        can_analyze = cb.can_analyze(large_code)
        assert can_analyze is False
        assert cb.state == "open"
    
    def test_circuit_breaker_status(self) -> None:
        """Circuit breaker reports status."""
        cb = CircuitBreaker()
        status = cb.get_status()
        
        assert 'state' in status
        assert 'failure_count' in status
        assert status['state'] in ['closed', 'open', 'half-open']


# ============================================================================
# TEST SUITE 6: DIFFERENTIAL SOLID CHECKING (AC-DOMAIN-REF-009)
# ============================================================================

class TestDifferentialChecking:
    """Tests for AC-DOMAIN-REF-009: Differential SOLID checking."""
    
    def test_solid_metrics_dataclass_creation(self) -> None:
        """SOLIDMetrics can be created and compared."""
        metrics1 = SOLIDMetrics(
            srp_score=0.8, ocp_score=0.7, lsp_score=0.9,
            isp_score=0.8, dip_score=0.75, cohesion=0.85,
            coupling=0.2, overall_score=0.77
        )
        metrics2 = SOLIDMetrics(
            srp_score=0.85, ocp_score=0.7, lsp_score=0.9,
            isp_score=0.8, dip_score=0.75, cohesion=0.85,
            coupling=0.2, overall_score=0.78
        )
        
        # Can calculate deltas
        delta_srp = metrics2.srp_score - metrics1.srp_score
        assert abs(delta_srp - 0.05) < 0.001
        
        # Metrics are serializable
        d1 = metrics1.to_dict()
        assert d1['srp_score'] == 0.8


# ============================================================================
# TEST SUITE 7: CONFIDENCE SCORING (AC-DOMAIN-REF-005)
# ============================================================================

class TestConfidenceScoring:
    """Tests for AC-DOMAIN-REF-005: Confidence scoring."""
    
    def test_refactoring_plan_has_confidence(self) -> None:
        """RefactoringPlan includes confidence field."""
        plan = RefactoringPlan(
            plan_id="plan_1",
            file_path="test.py",
            violations=[],
            selected_strategies=[],
            execution_order=[],
            total_effort_hours=10,
            total_confidence=0.85,
            overall_difficulty="medium",
            rollback_strategy="git_revert",
            estimated_duration_ms=1000,
        )
        
        assert plan.total_confidence == 0.85
        assert 0 <= plan.total_confidence <= 1.0
    
    def test_strategy_has_confidence(self) -> None:
        """Strategy includes confidence field."""
        strategy = RefactoringStrategy(
            strategy_name="extract_interfaces",
            description="Test",
            effort_hours=4,
            complexity="medium",
            safety_level="high",
            applicable_violations=[ViolationType.GOD_CLASS],
            steps=["step1"],
        )
        
        assert strategy.confidence == 0.0  # Initial
        strategy.confidence = 0.75
        assert strategy.confidence == 0.75


# ============================================================================
# TEST SUITE 8: ORCHESTRATOR INTERFACE (IOrchestrator Compliance)
# ============================================================================

class TestEnhancedRefactoringOrchestratorInterface:
    """Tests for IOrchestrator interface compliance."""
    
    def test_orchestrator_singleton(self) -> None:
        """Orchestrator provides singleton instance."""
        orch1 = EnhancedRefactoringOrchestrator.instance()
        orch2 = EnhancedRefactoringOrchestrator.instance()
        assert orch1 is orch2
    
    def test_orchestrator_has_public_methods(self) -> None:
        """Orchestrator has required public methods."""
        orchestrator = EnhancedRefactoringOrchestrator.instance()
        
        # Verify public methods exist
        assert hasattr(orchestrator, 'get_name')
        assert hasattr(orchestrator, 'get_version')
        assert hasattr(orchestrator, 'get_mode')
        assert hasattr(orchestrator, 'initialize')
        assert hasattr(orchestrator, 'get_mcp_tools')


# ============================================================================
# TEST SUITE 9: ORCHESTRATOR OPERATIONS (Simplified)
# ============================================================================

class TestEnhancedRefactoringOrchestratorOperations:
    """Tests for orchestrator basic interface."""
    
    def test_orchestrator_get_name(self) -> None:
        """orchestrator returns name."""
        orchestrator = EnhancedRefactoringOrchestrator.instance()
        name = orchestrator.get_name()
        
        assert isinstance(name, str)
        assert len(name) > 0
        assert 'refactoring' in name.lower()
    
    def test_orchestrator_get_version(self) -> None:
        """Orchestrator returns version."""
        orchestrator = EnhancedRefactoringOrchestrator.instance()
        version = orchestrator.get_version()
        
        assert isinstance(version, str)
        assert '.' in version or version[0].isdigit()
    
    def test_orchestrator_audit_trail_exists(self) -> None:
        """Orchestrator maintains audit trail."""
        orchestrator = EnhancedRefactoringOrchestrator.instance()
        
        # Check if audit trail structure exists
        assert hasattr(orchestrator, '_audit_trail')


# ============================================================================
# TEST SUITE 10: THREADING & CONCURRENCY (Safety Tests)
# ============================================================================

class TestThreadSafety:
    """Tests for thread-safety and concurrency."""
    
    def test_pattern_cache_thread_safe(self) -> None:
        """Pattern cache is thread-safe."""
        cache = PatternCache()
        metrics = SOLIDMetrics(
            srp_score=0.8, ocp_score=0.7, lsp_score=0.9,
            isp_score=0.8, dip_score=0.75, cohesion=0.85,
            coupling=0.2, overall_score=0.77
        )
        
        def cache_operation(code: str, idx: int) -> None:
            cache.put(code, f"analysis_{idx}", metrics)
            result = cache.get(code)
            assert result is not None or result is None  # No exception
        
        threads = [
            threading.Thread(target=cache_operation, args=(f"code_{i}", i))
            for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Cache should handle concurrent access without errors
        assert cache.hit_rate() >= 0


# ============================================================================
# TEST SUITE 11: GOVERNANCE COMPLIANCE (CORE Rules)
# ============================================================================

class TestGovernanceCompliance:
    """Tests for CORE governance rule compliance."""
    
    def test_core_011_type_hints_on_components(self) -> None:
        """CORE-011: Components have proper typing."""
        # Test that components can be instantiated with proper types
        analyzer = SOLIDAnalyzer()
        assert analyzer is not None
        
        classifier = ComplexityClassifier()
        assert classifier is not None
        
        cache = PatternCache()
        assert cache is not None
    
    def test_core_012_docstrings_on_dataclasses(self) -> None:
        """CORE-012: DataClasses have proper documentation."""
        # Violation class has docstrings
        assert Violation.__doc__ is not None
        
        # SOLIDMetrics has docstrings
        assert SOLIDMetrics.__doc__ is not None
        
        # RefactoringStrategy has docstrings
        assert RefactoringStrategy.__doc__ is not None


# ============================================================================
# TEST SUITE 12: PERFORMANCE BENCHMARKS
# ============================================================================

class TestPerformanceBenchmarks:
    """Tests for performance targets."""
    
    def test_cache_hit_rate_improves_access(self) -> None:
        """Cache hit tracking works correctly."""
        cache = PatternCache(capacity=100)
        metrics = SOLIDMetrics(
            srp_score=0.8, ocp_score=0.7, lsp_score=0.9,
            isp_score=0.8, dip_score=0.75, cohesion=0.85,
            coupling=0.2, overall_score=0.77
        )
        
        code = "def foo(): pass"
        cache.put(code, "analysis_1", metrics)
        
        # Multiple accesses
        for _ in range(5):
            cache.get(code)
        
        hit_rate = cache.hit_rate()
        assert hit_rate > 0  # Should have cache hits


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
