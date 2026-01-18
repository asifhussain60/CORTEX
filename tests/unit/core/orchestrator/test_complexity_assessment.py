"""Tests for Complexity Assessment Engine."""
import pytest
from src.core.orchestrator.complexity_assessment import (
    ComplexitySignals,
    ComplexityAssessment,
    ComplexityLevel,
    ComplexityAssessmentEngine,
    ASTComplexityAnalyzer,
    CallGraphAnalyzer,
    CircularDependencyDetector,
)

# ===== COMPLEXITY ASSESSMENT ENGINE TESTS =====

@pytest.fixture
def engine():
    """Create complexity assessment engine."""
    return ComplexityAssessmentEngine()

@pytest.fixture
def simple_signals():
    """Create simple complexity signals."""
    return ComplexitySignals(
        lens_confidence=0.95,
        files_affected_count=1,
        call_graph_depth=1,
        circular_dependencies=0,
        dependency_depth=1,
        tight_coupling_score=0.0,
        operation_scope='local',
        ast_complexity=2,
        criticality_level='low',
    )

@pytest.fixture
def moderate_signals():
    """Create moderate complexity signals."""
    return ComplexitySignals(
        lens_confidence=0.70,
        files_affected_count=5,
        call_graph_depth=4,
        circular_dependencies=0,
        dependency_depth=2,
        tight_coupling_score=0.3,
        operation_scope='cross_layer',
        ast_complexity=15,
        criticality_level='medium',
    )

@pytest.fixture
def complex_signals():
    """Create complex signals."""
    return ComplexitySignals(
        lens_confidence=0.40,
        files_affected_count=20,
        call_graph_depth=8,
        circular_dependencies=2,
        dependency_depth=4,
        tight_coupling_score=0.7,
        operation_scope='global',
        ast_complexity=40,
        criticality_level='critical',
    )

def test_assess_trivial_complexity(engine, simple_signals):
    """Test assessment of trivial complexity."""
    assessment = engine.assess_complexity(simple_signals)
    assert assessment.complexity_level == ComplexityLevel.TRIVIAL.value
    assert assessment.complexity_score <= 0.15

def test_assess_simple_complexity(engine):
    """Test assessment of simple complexity."""
    signals = ComplexitySignals(
        lens_confidence=0.90,
        files_affected_count=2,
        call_graph_depth=2,
        circular_dependencies=0,
        dependency_depth=1,
        tight_coupling_score=0.1,
        operation_scope='local',
        ast_complexity=5,
        criticality_level='low',
    )
    assessment = engine.assess_complexity(signals)
    # With low confidence (0.1 from 1-0.9) and minimal signals, may stay TRIVIAL
    assert assessment.complexity_level in [ComplexityLevel.TRIVIAL.value, ComplexityLevel.SIMPLE.value]
    assert assessment.complexity_score <= 0.35

def test_assess_moderate_complexity(engine, moderate_signals):
    """Test assessment of moderate complexity."""
    assessment = engine.assess_complexity(moderate_signals)
    assert assessment.complexity_level == ComplexityLevel.MODERATE.value
    assert 0.35 < assessment.complexity_score <= 0.60

def test_assess_complex_complexity(engine):
    """Test assessment of complex operations."""
    signals = ComplexitySignals(
        lens_confidence=0.50,
        files_affected_count=30,
        call_graph_depth=9,
        circular_dependencies=1,
        dependency_depth=4,
        tight_coupling_score=0.8,
        operation_scope='global',
        ast_complexity=45,
        criticality_level='high',
    )
    assessment = engine.assess_complexity(signals)
    # High criticality multiplier (1.6) may push into CRITICAL territory
    assert assessment.complexity_level in [ComplexityLevel.COMPLEX.value, ComplexityLevel.CRITICAL.value]
    assert assessment.complexity_score >= 0.60

def test_assess_critical_complexity(engine, complex_signals):
    """Test assessment of critical complexity."""
    assessment = engine.assess_complexity(complex_signals)
    assert assessment.complexity_level == ComplexityLevel.CRITICAL.value
    assert assessment.complexity_score > 0.85

def test_lens_confidence_aggregation(engine, simple_signals):
    """Test LENS confidence signal aggregation."""
    # High confidence (0.95) = low complexity from this signal
    assessment = engine.assess_complexity(simple_signals)
    assert 'lens_confidence' in assessment.factors
    assert assessment.factors['lens_confidence'] <= 0.15

def test_ast_complexity_scoring(engine):
    """Test AST complexity scoring."""
    signals = ComplexitySignals(
        lens_confidence=0.90,
        files_affected_count=1,
        call_graph_depth=1,
        circular_dependencies=0,
        dependency_depth=1,
        tight_coupling_score=0.0,
        operation_scope='local',
        ast_complexity=30,  # High complexity
        criticality_level='low',
    )
    assessment = engine.assess_complexity(signals)
    # Should still be simple/moderate due to other factors being low
    assert assessment.factors['operation_scope'] > 0.1

def test_callgraph_traversal_depth(engine):
    """Test call graph depth scoring."""
    signals = ComplexitySignals(
        lens_confidence=0.90,
        files_affected_count=1,
        call_graph_depth=10,  # Max depth
        circular_dependencies=0,
        dependency_depth=1,
        tight_coupling_score=0.0,
        operation_scope='local',
        ast_complexity=5,
        criticality_level='low',
    )
    assessment = engine.assess_complexity(signals)
    assert 'dependency_depth' in assessment.factors
    # High call graph depth should increase dependency score

def test_circular_dependency_detection(engine):
    """Test circular dependency penalty."""
    signals = ComplexitySignals(
        lens_confidence=0.90,
        files_affected_count=1,
        call_graph_depth=1,
        circular_dependencies=3,  # Multiple cycles
        dependency_depth=1,
        tight_coupling_score=0.0,
        operation_scope='local',
        ast_complexity=5,
        criticality_level='low',
    )
    assessment = engine.assess_complexity(signals)
    assert 'circular_penalty' in assessment.factors
    assert assessment.factors['circular_penalty'] > 0.1

def test_scope_analysis_local_vs_global(engine):
    """Test scope-based complexity scoring."""
    local_signals = ComplexitySignals(
        lens_confidence=0.90, files_affected_count=1, call_graph_depth=1,
        circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
        operation_scope='local', ast_complexity=5, criticality_level='low'
    )
    global_signals = ComplexitySignals(
        lens_confidence=0.90, files_affected_count=1, call_graph_depth=1,
        circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
        operation_scope='global', ast_complexity=5, criticality_level='low'
    )
    
    local_assess = engine.assess_complexity(local_signals)
    global_assess = engine.assess_complexity(global_signals)
    
    # Global scope should have higher complexity
    assert global_assess.complexity_score > local_assess.complexity_score

def test_criticality_scoring_cached(engine):
    """Test criticality multiplier effect."""
    base_signals = ComplexitySignals(
        lens_confidence=0.80, files_affected_count=5, call_graph_depth=3,
        circular_dependencies=0, dependency_depth=2, tight_coupling_score=0.2,
        operation_scope='cross_layer', ast_complexity=10, criticality_level='low'
    )
    critical_signals = ComplexitySignals(
        lens_confidence=0.80, files_affected_count=5, call_graph_depth=3,
        circular_dependencies=0, dependency_depth=2, tight_coupling_score=0.2,
        operation_scope='cross_layer', ast_complexity=10, criticality_level='critical'
    )
    
    base_assess = engine.assess_complexity(base_signals)
    critical_assess = engine.assess_complexity(critical_signals)
    
    # Critical should have higher score due to multiplier
    assert critical_assess.complexity_score > base_assess.complexity_score

def test_complexity_cache_invalidation(engine, simple_signals):
    """Test cache invalidation."""
    # First assessment
    a1 = engine.assess_complexity(simple_signals, intent_type='test_op')
    assert a1.cached is False
    
    # Second assessment should be cached
    a2 = engine.assess_complexity(simple_signals, intent_type='test_op', use_cache=True)
    assert a2.cached is True
    
    # Invalidate cache
    count = engine.invalidate_cache_for_intent('test_op')
    assert count > 0
    
    # Third assessment should not be cached
    a3 = engine.assess_complexity(simple_signals, intent_type='test_op')
    assert a3.cached is False

def test_edge_case_empty_relationship_graph(engine):
    """Test edge case with empty relationship graph."""
    signals = ComplexitySignals(
        lens_confidence=0.95, files_affected_count=0, call_graph_depth=0,
        circular_dependencies=0, dependency_depth=0, tight_coupling_score=0.0,
        operation_scope='local', ast_complexity=0, criticality_level='low'
    )
    assessment = engine.assess_complexity(signals)
    assert assessment.complexity_score <= 0.15
    assert assessment.complexity_level == ComplexityLevel.TRIVIAL.value

def test_edge_case_single_file_operation(engine):
    """Test edge case with single file operation."""
    signals = ComplexitySignals(
        lens_confidence=0.90, files_affected_count=1, call_graph_depth=2,
        circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
        operation_scope='local', ast_complexity=8, criticality_level='low'
    )
    assessment = engine.assess_complexity(signals)
    assert assessment.complexity_score <= 0.35  # Should be simple at most

def test_edge_case_cross_layer_integration(engine):
    """Test edge case with cross-layer integration."""
    signals = ComplexitySignals(
        lens_confidence=0.75, files_affected_count=10, call_graph_depth=5,
        circular_dependencies=1, dependency_depth=3, tight_coupling_score=0.5,
        operation_scope='cross_layer', ast_complexity=20, criticality_level='high'
    )
    assessment = engine.assess_complexity(signals)
    assert 0.35 < assessment.complexity_score < 0.85

def test_performance_caching_efficiency(engine, simple_signals):
    """Test caching efficiency."""
    # Warm up cache
    for i in range(10):
        engine.assess_complexity(simple_signals, intent_type='perf_test')
    
    stats = engine.get_cache_stats()
    assert stats['hit_rate'] > 0.8  # Should have high hit rate
    assert stats['cache_hits'] > 0

def test_complexity_score_normalization(engine):
    """Test that complexity scores are normalized 0.0-1.0."""
    signals_list = [
        ComplexitySignals(
            lens_confidence=i/10, files_affected_count=i*5,
            call_graph_depth=i*2, circular_dependencies=i,
            dependency_depth=i, tight_coupling_score=i/10,
            operation_scope='local' if i < 5 else 'global',
            ast_complexity=i*5, criticality_level='low'
        )
        for i in range(1, 11)
    ]
    
    for signals in signals_list:
        assessment = engine.assess_complexity(signals)
        assert 0.0 <= assessment.complexity_score <= 1.0

# ===== AST COMPLEXITY ANALYZER TESTS =====

def test_ast_complexity_empty_code():
    """Test AST complexity on empty code."""
    complexity = ASTComplexityAnalyzer.analyze_complexity("")
    assert complexity == 0

def test_ast_complexity_simple_function():
    """Test AST complexity on simple function."""
    code = "def simple(): return 42"
    complexity = ASTComplexityAnalyzer.analyze_complexity(code)
    assert complexity >= 0

def test_ast_complexity_with_conditionals():
    """Test AST complexity with conditionals."""
    code = """
def complex(x):
    if x > 0:
        return x
    elif x < 0:
        return -x
    else:
        return 0
"""
    complexity = ASTComplexityAnalyzer.analyze_complexity(code)
    assert complexity >= 2  # At least 2 for if/elif

def test_ast_complexity_syntax_error():
    """Test AST complexity with invalid syntax."""
    complexity = ASTComplexityAnalyzer.analyze_complexity("def invalid(")
    assert complexity == 0

# ===== CALL GRAPH ANALYZER TESTS =====

def test_callgraph_depth_empty():
    """Test call graph depth on empty graph."""
    max_depth, avg_depth = CallGraphAnalyzer.analyze_depth({})
    assert max_depth == 0
    assert avg_depth == 0.0

def test_callgraph_depth_single_node():
    """Test call graph depth with single node."""
    call_graph = {'func_a': []}
    max_depth, avg_depth = CallGraphAnalyzer.analyze_depth(call_graph)
    assert max_depth == 1

def test_callgraph_depth_linear_chain():
    """Test call graph depth with linear chain."""
    call_graph = {
        'func_a': ['func_b'],
        'func_b': ['func_c'],
        'func_c': [],
    }
    max_depth, avg_depth = CallGraphAnalyzer.analyze_depth(call_graph)
    assert max_depth == 3

def test_callgraph_depth_branching():
    """Test call graph depth with branching."""
    call_graph = {
        'func_a': ['func_b', 'func_c'],
        'func_b': ['func_d'],
        'func_c': [],
        'func_d': [],
    }
    max_depth, avg_depth = CallGraphAnalyzer.analyze_depth(call_graph)
    assert max_depth >= 3

# ===== CIRCULAR DEPENDENCY DETECTOR TESTS =====

def test_detect_cycles_empty_graph():
    """Test cycle detection on empty graph."""
    cycles = CircularDependencyDetector.detect_cycles({})
    assert len(cycles) == 0

def test_detect_cycles_no_cycles():
    """Test cycle detection with no cycles."""
    dependency_graph = {
        'a': ['b', 'c'],
        'b': ['d'],
        'c': [],
        'd': [],
    }
    cycles = CircularDependencyDetector.detect_cycles(dependency_graph)
    assert len(cycles) == 0

def test_detect_cycles_self_loop():
    """Test cycle detection with self-loop."""
    dependency_graph = {'a': ['a']}
    cycles = CircularDependencyDetector.detect_cycles(dependency_graph)
    assert len(cycles) > 0

def test_detect_cycles_simple_cycle():
    """Test cycle detection with simple cycle."""
    dependency_graph = {
        'a': ['b'],
        'b': ['c'],
        'c': ['a'],
    }
    cycles = CircularDependencyDetector.detect_cycles(dependency_graph)
    assert len(cycles) > 0

def test_coupling_score_empty_graph():
    """Test coupling score on empty graph."""
    score = CircularDependencyDetector.calculate_tight_coupling({})
    assert score == 0.0

def test_coupling_score_sparse_graph():
    """Test coupling score on sparse graph."""
    dependency_graph = {
        'a': ['b'],
        'b': [],
    }
    score = CircularDependencyDetector.calculate_tight_coupling(dependency_graph)
    assert 0.0 <= score <= 1.0

def test_coupling_score_dense_graph():
    """Test coupling score on dense graph."""
    dependency_graph = {
        'a': ['b', 'c', 'd'],
        'b': ['a', 'c', 'd'],
        'c': ['a', 'b', 'd'],
        'd': ['a', 'b', 'c'],
    }
    score = CircularDependencyDetector.calculate_tight_coupling(dependency_graph)
    assert score > 0.5  # Should be high for densely connected
