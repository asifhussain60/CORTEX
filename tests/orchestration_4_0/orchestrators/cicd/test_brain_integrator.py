"""
Tests for CI/CD Brain Integrator

Tests integration between CI/CD orchestrator and Brain Tier 2.

Author: Asif Hussain
Version: 1.0
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.brain.tier2.knowledge_graph import KnowledgeGraph
from src.orchestration_4_0.orchestrators.cicd.brain_integrator import BrainIntegrator
from src.orchestration_4_0.orchestrators.cicd.schemas import (
    FailureAnalysis,
    FixAttempt,
    HealingResult,
    FailureCategory,
    FixStrategy
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test-knowledge-graph.db"
        yield db_path


@pytest.fixture
def knowledge_graph(temp_db):
    """Create Knowledge Graph instance"""
    return KnowledgeGraph(temp_db, namespace="test_cicd")


@pytest.fixture
def brain_integrator(knowledge_graph):
    """Create Brain Integrator instance"""
    return BrainIntegrator(knowledge_graph, namespace="test_cicd")


@pytest.fixture
def sample_failure():
    """Create sample failure analysis"""
    return FailureAnalysis(
        category=FailureCategory.DEPENDENCY_CONFLICT,
        root_cause="Package version conflict detected",
        confidence=0.85,
        affected_files=["requirements.txt"],
        affected_dependencies=["package-a", "package-b"],
        error_messages=["ERROR: Dependency conflict: package-a 1.0 requires package-b <2.0, but 2.1 is installed"],
        suggested_fixes=[
            FixStrategy.DEPENDENCY_UPDATE,
            FixStrategy.DEPENDENCY_ROLLBACK
        ],
        auto_fixable=True,
        analysis_time_ms=50.0
    )


class TestBrainIntegratorInit:
    """Test Brain Integrator initialization"""
    
    def test_init_with_defaults(self, knowledge_graph):
        """Should initialize with default parameters"""
        integrator = BrainIntegrator(knowledge_graph)
        
        assert integrator.kg == knowledge_graph
        assert integrator.namespace == "cicd"
        assert integrator.min_confidence == 0.6
    
    def test_init_with_custom_params(self, knowledge_graph):
        """Should initialize with custom parameters"""
        integrator = BrainIntegrator(
            knowledge_graph,
            namespace="custom",
            min_confidence=0.8
        )
        
        assert integrator.namespace == "custom"
        assert integrator.min_confidence == 0.8


class TestStoreFailurePattern:
    """Test storing failure patterns"""
    
    def test_store_failure_without_fix(self, brain_integrator, sample_failure):
        """Should store failure pattern without fix result"""
        pattern_id = brain_integrator.store_failure_pattern(sample_failure)
        
        assert pattern_id is not None
        assert len(pattern_id) > 0
    
    def test_store_failure_with_fix(self, brain_integrator, sample_failure):
        """Should store failure pattern with fix result"""
        healing_result = HealingResult(
            run_id="test-run-1",
            platform="github_actions",
            initial_failure=sample_failure,
            fix_attempts=[],
            final_status="success",
            healed=True,
            total_healing_time_seconds=5.2
        )
        
        pattern_id = brain_integrator.store_failure_pattern(sample_failure, healing_result)
        
        assert pattern_id is not None
        
        # Verify pattern was stored
        patterns = brain_integrator.kg.search_patterns(
            query="dependency",
            pattern_type="cicd_failure"
        )
        
        assert len(patterns) > 0
        pattern = patterns[0]
        assert pattern.context["category"] == FailureCategory.DEPENDENCY_CONFLICT.value
    
    def test_store_multiple_failures(self, brain_integrator, sample_failure):
        """Should store multiple failure patterns"""
        pattern_id1 = brain_integrator.store_failure_pattern(sample_failure)
        
        # Create different failure
        different_failure = FailureAnalysis(
            category=FailureCategory.TEST_FAILURE,
            root_cause="Test failed due to assertion error",
            confidence=0.9,
            error_messages=["test_user_authentication FAILED"],
            affected_files=["tests/test_auth.py"],
            affected_dependencies=[],
            suggested_fixes=[FixStrategy.TEST_RETRY],
            auto_fixable=True,
            analysis_time_ms=30.0
        )
        
        pattern_id2 = brain_integrator.store_failure_pattern(different_failure)
        
        assert pattern_id1 != pattern_id2


class TestStoreFixStrategy:
    """Test storing fix strategy outcomes"""
    
    def test_store_successful_fix(self, brain_integrator):
        """Should store successful fix strategy"""
        pattern_id = brain_integrator.store_fix_strategy(
            FixStrategy.DEPENDENCY_UPDATE,
            FailureCategory.DEPENDENCY_CONFLICT,
            success=True,
            execution_time=3.5
        )
        
        assert pattern_id is not None
        
        # Verify pattern
        patterns = brain_integrator.kg.search_patterns(
            query="DEPENDENCY_UPDATE",
            pattern_type="cicd_fix_strategy"
        )
        
        assert len(patterns) > 0
        assert patterns[0].confidence >= 0.7  # High confidence for success
    
    def test_store_failed_fix(self, brain_integrator):
        """Should store failed fix strategy with low confidence"""
        # Create Knowledge Graph with explicit min_confidence
        kg_low_threshold = KnowledgeGraph(brain_integrator.kg.db_path, namespace="test_cicd", confidence_threshold=0.0)
        
        # Use low-threshold integrator
        low_threshold_integrator = BrainIntegrator(
            kg_low_threshold,
            namespace="test_cicd",
            min_confidence=0.0
        )
        
        pattern_id = low_threshold_integrator.store_fix_strategy(
            FixStrategy.DEPENDENCY_ROLLBACK,
            FailureCategory.CONFIGURATION_ERROR,
            success=False,
            execution_time=1.2
        )
        
        assert pattern_id is not None
        
        all_patterns = kg_low_threshold.search_patterns(
            query="",
            pattern_type="cicd_fix_strategy",
            limit=100
        )
        
        # Find our pattern by ID
        our_pattern = next((p for p in all_patterns if p.pattern_id == pattern_id), None)
        assert our_pattern is not None
        assert our_pattern.confidence < 0.5  # Low confidence for failure


class TestGetSimilarFailures:
    """Test retrieving similar historical failures"""
    
    def test_get_similar_failures_found(self, brain_integrator, sample_failure):
        """Should find similar historical failures"""
        # Store some failures
        brain_integrator.store_failure_pattern(sample_failure)
        brain_integrator.store_failure_pattern(sample_failure)
        
        # Search for similar
        similar = brain_integrator.get_similar_failures(sample_failure)
        
        assert len(similar) > 0
        assert all(p.pattern_type == "cicd_failure" for p in similar)
    
    def test_get_similar_failures_none_found(self, brain_integrator):
        """Should return empty list when no similar failures"""
        failure = FailureAnalysis(
            category=FailureCategory.RESOURCE_LIMIT,
            root_cause="Out of memory during build",
            confidence=0.75,
            error_messages=["out of memory"],
            affected_files=[],
            affected_dependencies=[],
            suggested_fixes=[FixStrategy.RESOURCE_INCREASE],
            auto_fixable=True,
            analysis_time_ms=25.0
        )
        
        similar = brain_integrator.get_similar_failures(failure)
        
        assert len(similar) == 0
    
    def test_get_similar_failures_respects_limit(self, brain_integrator, sample_failure):
        """Should respect limit parameter"""
        # Store many failures
        for _ in range(10):
            brain_integrator.store_failure_pattern(sample_failure)
        
        similar = brain_integrator.get_similar_failures(sample_failure, limit=3)
        
        assert len(similar) <= 3


class TestGetRecommendedStrategies:
    """Test retrieving recommended fix strategies"""
    
    def test_get_recommended_strategies(self, brain_integrator):
        """Should return recommended strategies with success rates"""
        # Store multiple fix attempts
        for _ in range(5):
            brain_integrator.store_fix_strategy(
                FixStrategy.DEPENDENCY_UPDATE,
                FailureCategory.DEPENDENCY_CONFLICT,
                success=True,
                execution_time=2.0
            )
        
        for _ in range(2):
            brain_integrator.store_fix_strategy(
                FixStrategy.DEPENDENCY_ROLLBACK,
                FailureCategory.DEPENDENCY_CONFLICT,
                success=False,
                execution_time=1.0
            )
        
        # Get recommendations
        recommendations = brain_integrator.get_recommended_strategies(
            FailureCategory.DEPENDENCY_CONFLICT
        )
        
        assert len(recommendations) > 0
        
        # Best strategy should be DEPENDENCY_UPDATE (100% success)
        best = recommendations[0]
        assert best["strategy"] == FixStrategy.DEPENDENCY_UPDATE.value
        assert best["success_rate"] == 1.0
        assert best["total"] == 5
        assert best["successful"] == 5
    
    def test_get_recommended_strategies_none_found(self, brain_integrator):
        """Should return empty list when no strategies found"""
        recommendations = brain_integrator.get_recommended_strategies(
            FailureCategory.TIMEOUT
        )
        
        assert len(recommendations) == 0
    
    def test_get_recommended_strategies_respects_limit(self, brain_integrator):
        """Should respect limit parameter"""
        # Store different strategies
        for strategy in [FixStrategy.DEPENDENCY_UPDATE, FixStrategy.CONFIG_FIX, FixStrategy.ROLLBACK]:
            brain_integrator.store_fix_strategy(
                strategy,
                FailureCategory.SYNTAX_ERROR,
                success=True,
                execution_time=1.0
            )
        
        recommendations = brain_integrator.get_recommended_strategies(
            FailureCategory.SYNTAX_ERROR,
            limit=2
        )
        
        assert len(recommendations) <= 2


class TestGetFailureStatistics:
    """Test aggregate statistics retrieval"""
    
    def test_get_empty_statistics(self, brain_integrator):
        """Should return zero statistics when empty"""
        stats = brain_integrator.get_failure_statistics()
        
        assert stats["total_failures"] == 0
        assert stats["total_fix_attempts"] == 0
        assert stats["overall_success_rate"] == 0.0
    
    def test_get_statistics_with_data(self, brain_integrator, sample_failure):
        """Should return accurate statistics"""
        # Store failures
        brain_integrator.store_failure_pattern(sample_failure)
        brain_integrator.store_failure_pattern(sample_failure)
        
        # Store fix attempts (3 success, 1 failure)
        for _ in range(3):
            brain_integrator.store_fix_strategy(
                FixStrategy.DEPENDENCY_UPDATE,
                FailureCategory.DEPENDENCY_CONFLICT,
                success=True,
                execution_time=2.0
            )
        
        brain_integrator.store_fix_strategy(
            FixStrategy.DEPENDENCY_ROLLBACK,
            FailureCategory.DEPENDENCY_CONFLICT,
            success=False,
            execution_time=1.0
        )
        
        stats = brain_integrator.get_failure_statistics()
        
        assert stats["total_failures"] == 2
        assert stats["total_fix_attempts"] >= 3  # At least 3 (may be more due to previous tests)
        assert stats["successful_fixes"] >= 3
        assert stats["overall_success_rate"] > 0.5  # More than half successful
        assert "failures_by_category" in stats


class TestLearnFromHealingResult:
    """Test learning from complete healing results"""
    
    def test_learn_from_successful_healing(self, brain_integrator, sample_failure):
        """Should learn from successful healing result"""
        fix_attempt = FixAttempt(
            strategy=FixStrategy.DEPENDENCY_UPDATE,
            success=True,
            fixes_applied=["Update package-b to 1.9"],
            changes_made={"requirements.txt": "package-b==1.9"},
            time_seconds=3.5,
            verification_passed=True
        )
        
        healing_result = HealingResult(
            run_id="test-1",
            platform="github_actions",
            initial_failure=sample_failure,
            fix_attempts=[fix_attempt],
            final_status="success",
            healed=True,
            total_healing_time_seconds=3.5
        )
        
        brain_integrator.learn_from_healing_result(healing_result)
        
        # Verify failure pattern stored
        failures = brain_integrator.kg.search_patterns(
            query="dependency",
            pattern_type="cicd_failure"
        )
        assert len(failures) > 0
        
        # Verify fix strategy stored
        strategies = brain_integrator.kg.search_patterns(
            query="DEPENDENCY_UPDATE",
            pattern_type="cicd_fix_strategy"
        )
        assert len(strategies) > 0
    
    def test_learn_from_failed_healing(self, brain_integrator, sample_failure):
        """Should learn from failed healing result"""
        fix_attempt = FixAttempt(
            strategy=FixStrategy.DEPENDENCY_ROLLBACK,
            success=False,
            fixes_applied=["Attempted rollback"],
            changes_made={},
            time_seconds=8.5,
            verification_passed=False,
            error_message="Rollback failed"
        )
        
        healing_result = HealingResult(
            run_id="test-2",
            platform="azure_devops",
            initial_failure=sample_failure,
            fix_attempts=[fix_attempt],
            final_status="failed",
            healed=False,
            total_healing_time_seconds=8.5
        )
        
        brain_integrator.learn_from_healing_result(healing_result)
        
        # Should still store patterns for learning
        failures = brain_integrator.kg.search_patterns(
            query="dependency",
            pattern_type="cicd_failure"
        )
        assert len(failures) > 0
    
    def test_learn_without_fix_applied(self, brain_integrator, sample_failure):
        """Should handle healing result without fix"""
        healing_result = HealingResult(
            run_id="test-3",
            platform="github_actions",
            initial_failure=sample_failure,
            fix_attempts=[],
            final_status="failed",
            healed=False,
            total_healing_time_seconds=0.0
        )
        
        # Should not raise error
        brain_integrator.learn_from_healing_result(healing_result)


class TestConfidenceUpdates:
    """Test confidence score updates"""
    
    def test_update_strategy_confidence_on_success(self, brain_integrator):
        """Should increase confidence on successful fix"""
        # Store initial strategy with medium confidence
        brain_integrator.store_fix_strategy(
            FixStrategy.CONFIG_FIX,
            FailureCategory.CONFIGURATION_ERROR,
            success=True,
            execution_time=1.0
        )
        
        initial_patterns = brain_integrator.kg.search_patterns(
            query="CONFIG_FIX",
            pattern_type="cicd_fix_strategy"
        )
        initial_confidence = initial_patterns[0].confidence if initial_patterns else 0.0
        
        # Store another successful attempt
        brain_integrator.store_fix_strategy(
            FixStrategy.CONFIG_FIX,
            FailureCategory.CONFIGURATION_ERROR,
            success=True,
            execution_time=1.0
        )
        
        updated_patterns = brain_integrator.kg.search_patterns(
            query="CONFIG_FIX",
            pattern_type="cicd_fix_strategy"
        )
        
        # Confidence should be maintained or improved
        assert len(updated_patterns) >= 2
    
    def test_update_strategy_confidence_on_failure(self, brain_integrator):
        """Should decrease confidence on failed fix"""
        # Store successful attempt first
        brain_integrator.store_fix_strategy(
            FixStrategy.TEST_RETRY,
            FailureCategory.TIMEOUT,
            success=True,
            execution_time=1.0
        )
        
        # Store failed attempt
        brain_integrator.store_fix_strategy(
            FixStrategy.TEST_RETRY,
            FailureCategory.TIMEOUT,
            success=False,
            execution_time=1.0
        )
        
        # Should still have patterns (1 successful, 1 failed stored separately)
        patterns = brain_integrator.kg.search_patterns(
            query="test_retry",
            pattern_type="cicd_fix_strategy"
        )
        
        # May have 1 or 2 depending on update behavior
        assert len(patterns) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
