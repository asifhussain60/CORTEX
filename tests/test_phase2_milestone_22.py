"""
Tests for Phase 2 Milestone 2.2 - Test Quality Scoring and Pattern Refinement

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import os
from datetime import datetime

from src.cortex_agents.test_generator.test_quality_scorer import (
    TestQualityScorer,
    QualityMetrics,
    PatternFeedback
)
from src.cortex_agents.test_generator.pattern_refiner import (
    PatternRefiner,
    RefinementResult
)
from src.cortex_agents.test_generator.tier2_pattern_store import (
    Tier2PatternStore,
    BusinessPattern
)


class TestQualityScorerTests:
    """Test quality scoring system"""
    
    @pytest.fixture
    def scorer(self):
        return TestQualityScorer()
    
    def test_score_high_quality_tests(self, scorer):
        """Test scoring of high-quality test code"""
        test_code = '''
def test_login_valid_credentials():
    user = authenticate('test@example.com', 'password123')
    assert user is not None
    assert user.is_authenticated == True  # Use ==
    assert user.email == 'test@example.com'

def test_login_invalid_password():
    with pytest.raises(AuthenticationError):
        authenticate('test@example.com', 'wrong')

def test_login_empty_password():
    with pytest.raises(ValueError):
        authenticate('test@example.com', '')

def test_login_none_email():
    with pytest.raises(ValueError):
        authenticate(None, 'password')
'''
        
        metrics = scorer.score_test_code(test_code)
        
        assert metrics.test_count == 4
        assert metrics.assertion_strength >= 0.6  # Has strong == assertions
        assert metrics.has_exception_tests is True
        assert metrics.overall_score >= 0.45  # Good quality (no boundary tests)
    
    def test_score_low_quality_tests(self, scorer):
        """Test scoring of low-quality test code"""
        test_code = '''
def test_something():
    result = do_something()
    assert result  # Weak assertion

def test_another():
    value = calculate()
    assert True  # Very weak
'''
        
        metrics = scorer.score_test_code(test_code)
        
        assert metrics.test_count == 2
        assert metrics.assertion_strength < 0.5  # Weak assertions
        assert metrics.has_exception_tests is False
        assert metrics.overall_score < 0.5  # Low quality
    
    def test_identify_edge_case_tests(self, scorer):
        """Test edge case identification"""
        test_code = '''
def test_calculate_empty_list():
    assert calculate([]) == 0

def test_calculate_none_input():
    with pytest.raises(ValueError):
        calculate(None)

def test_calculate_negative_values():
    assert calculate([-1, -2]) == -3

def test_calculate_max_value():
    assert calculate([sys.maxsize]) == sys.maxsize
'''
        
        metrics = scorer.score_test_code(test_code)
        
        assert metrics.edge_case_count >= 3  # empty, none, negative, max
        assert metrics.edge_case_coverage >= 0.25  # 4 edge cases / (4 tests * 3) = 0.33
    
    def test_generate_pattern_feedback_good(self, scorer):
        """Test feedback generation for good pattern"""
        test_code = '''
def test_validate_email():
    assert validate_email('test@example.com') == True  # Use ==
    assert '@' in 'test@example.com'

def test_validate_email_invalid():
    assert validate_email('notanemail') == False  # Use ==

def test_validate_email_empty():
    with pytest.raises(ValueError):
        validate_email('')
'''
        
        metrics = scorer.score_test_code(test_code)
        feedback = scorer.generate_pattern_feedback(1, test_code, metrics)
        
        # With improved assertions, should score better
        assert feedback.effectiveness >= 0.5
        assert len(feedback.issues) <= 2  # May still have some issues
    
    def test_generate_pattern_feedback_poor(self, scorer):
        """Test feedback generation for poor pattern"""
        test_code = '''
def test_something():
    result = do_something()
    assert result
'''
        
        metrics = scorer.score_test_code(test_code)
        feedback = scorer.generate_pattern_feedback(1, test_code, metrics)
        
        assert feedback.effectiveness < 0.5
        assert feedback.should_demote is True
        assert len(feedback.issues) > 0
        assert len(feedback.suggestions) > 0
    
    def test_calculate_quality_improvement(self, scorer):
        """Test quality improvement calculation"""
        baseline = QualityMetrics(
            assertion_strength=0.4,
            edge_case_coverage=0.3,
            assertion_count=2,
            edge_case_count=1,
            test_count=2,
            has_exception_tests=False,
            has_boundary_tests=False,
            overall_score=0.35
        )
        
        current = QualityMetrics(
            assertion_strength=0.9,
            edge_case_coverage=0.8,
            assertion_count=10,
            edge_case_count=8,
            test_count=5,
            has_exception_tests=True,
            has_boundary_tests=True,
            overall_score=0.875
        )
        
        improvement = scorer.calculate_quality_improvement(baseline, current)
        
        assert improvement == pytest.approx(2.5, rel=0.1)  # ~2.5x improvement


class TestPatternRefinerTests:
    """Test pattern refinement system"""
    
    @pytest.fixture
    def refiner_with_store(self):
        """Create pattern refiner with temp storage"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        store = Tier2PatternStore(db_path)
        refiner = PatternRefiner(store)
        
        yield refiner, store
        
        store.close()
        os.unlink(db_path)
    
    def test_refine_pattern_promote(self, refiner_with_store):
        """Test pattern promotion on good feedback"""
        refiner, store = refiner_with_store
        
        # Store initial pattern
        pattern = BusinessPattern(
            None, 'authentication', 'login', 'postcondition',
            'User authenticated', 'assert user.is_authenticated',
            0.7, 0, 0, datetime.now().isoformat(), None, {}
        )
        pattern_id = store.store_pattern(pattern)
        
        # Provide good feedback
        feedback = PatternFeedback(
            pattern_id=pattern_id,
            effectiveness=0.9,
            issues=[],
            suggestions=[],
            should_promote=True,
            should_demote=False
        )
        
        new_confidence = refiner.refine_pattern(pattern_id, feedback)
        
        assert new_confidence > 0.7  # Should increase
        assert new_confidence <= 1.0
    
    def test_refine_pattern_demote(self, refiner_with_store):
        """Test pattern demotion on poor feedback"""
        refiner, store = refiner_with_store
        
        # Store initial pattern
        pattern = BusinessPattern(
            None, 'validation', 'email', 'precondition',
            'Email valid', 'assert email',
            0.6, 0, 0, datetime.now().isoformat(), None, {}
        )
        pattern_id = store.store_pattern(pattern)
        
        # Provide poor feedback
        feedback = PatternFeedback(
            pattern_id=pattern_id,
            effectiveness=0.3,
            issues=['Weak assertion', 'No edge cases'],
            suggestions=['Use specific assertions'],
            should_promote=False,
            should_demote=True
        )
        
        new_confidence = refiner.refine_pattern(pattern_id, feedback)
        
        assert new_confidence < 0.6  # Should decrease
        assert new_confidence >= 0.1  # But not below minimum
    
    def test_refine_batch(self, refiner_with_store):
        """Test batch refinement"""
        refiner, store = refiner_with_store
        
        # Store multiple patterns
        pattern_ids = []
        for i in range(5):
            pattern = BusinessPattern(
                None, 'calculation', f'operation_{i}', 'postcondition',
                f'Result correct {i}', f'assert result == expected_{i}',
                0.5 + (i * 0.1), 0, 0, datetime.now().isoformat(), None, {}
            )
            pattern_ids.append(store.store_pattern(pattern))
        
        # Generate feedback list
        feedbacks = [
            PatternFeedback(
                pattern_id=pid,
                effectiveness=0.8 if i >= 3 else 0.3,  # High for last 2, low for first 2
                issues=[],
                suggestions=[],
                should_promote=(i >= 3),  # Promote last 2
                should_demote=(i < 2)     # Demote first 2
            )
            for i, pid in enumerate(pattern_ids)
        ]
        
        result = refiner.refine_batch(feedbacks)
        
        assert result.patterns_promoted >= 1
        assert len(result.confidence_adjustments) == 5
    
    def test_analyze_pattern_effectiveness(self, refiner_with_store):
        """Test pattern effectiveness analysis"""
        refiner, store = refiner_with_store
        
        # Store patterns with usage stats
        for i in range(10):
            pattern = BusinessPattern(
                None, 'authentication', f'operation_{i}', 'postcondition',
                f'Description {i}', f'assert condition_{i}',
                0.5 + (i * 0.05),  # Varying confidence
                10 + i,  # Usage count
                8 + i,   # Success count (80%+ success rate)
                datetime.now().isoformat(), None, {}
            )
            store.store_pattern(pattern)
        
        analysis = refiner.analyze_pattern_effectiveness(
            domain='authentication',
            min_usage_count=5
        )
        
        assert analysis['total_patterns'] >= 10
        assert analysis['average_confidence'] > 0.0
        assert analysis['success_rate'] >= 0.8
        assert analysis['high_performers'] >= 1


class TestMilestone22Integration:
    """Integration tests for complete Milestone 2.2 workflow"""
    
    def test_quality_scoring_to_refinement_workflow(self):
        """Test complete workflow: Score → Feedback → Refine"""
        # Setup
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            store = Tier2PatternStore(db_path)
            scorer = TestQualityScorer()
            refiner = PatternRefiner(store)
            
            # Store pattern
            pattern = BusinessPattern(
                None, 'authentication', 'login', 'postcondition',
                'User authenticated', 'assert user.is_authenticated',
                0.6, 0, 0, datetime.now().isoformat(), None, {}
            )
            pattern_id = store.store_pattern(pattern)
            
            # Generate test code (simulated)
            test_code = '''
def test_login_valid():
    user = authenticate('test@example.com', 'pass')
    assert user is not None
    assert user.is_authenticated == True  # Use ==

def test_login_invalid():
    with pytest.raises(AuthenticationError):
        authenticate('test@example.com', 'wrong')

def test_login_empty_password():
    with pytest.raises(ValueError):
        authenticate('test@example.com', '')
'''
            
            # Step 1: Score quality
            metrics = scorer.score_test_code(test_code)
            assert metrics.overall_score >= 0.4  # Reasonable quality
            
            # Step 2: Generate feedback
            feedback = scorer.generate_pattern_feedback(pattern_id, test_code, metrics)
            assert feedback.effectiveness >= 0.4  # Reasonable effectiveness
            
            # Step 3: Refine pattern
            new_confidence = refiner.refine_pattern(pattern_id, feedback)
            assert new_confidence >= 0.3  # Should be updated based on feedback
            
            # Verify pattern was updated
            updated = store.search_patterns('login', domain='authentication', min_confidence=0.0)
            assert len(updated) > 0
            assert updated[0].usage_count >= 1  # Tracked
            
            store.close()
        finally:
            os.unlink(db_path)
    
    def test_quality_improvement_tracking(self):
        """Test tracking quality improvement over iterations"""
        scorer = TestQualityScorer()
        
        # Baseline (Phase 1 level)
        baseline_code = '''
def test_function():
    result = my_function()
    assert result == 'success'  # Use strong == assertion
'''
        baseline_metrics = scorer.score_test_code(baseline_code)
        assert baseline_metrics.overall_score > 0, "Baseline should have non-zero score"
        
        # Phase 2 enhanced (with feedback loop)
        enhanced_code = '''
def test_function_valid_input():
    result = my_function('valid')
    assert result is not None
    assert result.status == 'success'
    assert isinstance(result, Response)

def test_function_invalid_input():
    with pytest.raises(ValueError):
        my_function(None)

def test_function_empty_input():
    result = my_function('')
    assert result.status == 'empty'

def test_function_boundary_max():
    result = my_function('x' * 1000)
    assert result is not None
'''
        enhanced_metrics = scorer.score_test_code(enhanced_code)
        
        # Calculate improvement
        improvement = scorer.calculate_quality_improvement(baseline_metrics, enhanced_metrics)
        
        # Should show noticeable improvement (>1.5x)
        assert improvement >= 1.5, f"Quality improvement {improvement:.2f}x below 1.5x minimum"
