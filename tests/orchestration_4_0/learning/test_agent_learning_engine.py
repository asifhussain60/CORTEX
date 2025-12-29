"""
Tests for Agent Learning Engine (Task 5.11)

Tests pattern learning, recommendation system, strategy weighting,
and Tier 2 integration.

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.orchestration_4_0.learning.agent_learning_engine import (
    AgentLearningEngine,
    ExecutionPattern,
    Recommendation,
    StrategyType
)
from src.orchestration_4_0.frameworks.agent_evaluator import (
    EvaluationResult,
    EvaluationCategory
)


@pytest.fixture
def mock_knowledge_graph():
    """Create mock knowledge graph"""
    kg = Mock()
    kg.add_pattern = Mock()
    kg.search_patterns = Mock(return_value=[])
    return kg


@pytest.fixture
def learning_engine(mock_knowledge_graph):
    """Create learning engine with mocked KG"""
    return AgentLearningEngine(knowledge_graph=mock_knowledge_graph)


@pytest.fixture
def sample_evaluation():
    """Sample evaluation result"""
    return EvaluationResult(
        agent_name="TestAgent",
        category=EvaluationCategory.REASONING,
        score=8.5,
        reasoning="Good execution quality",
        metrics={'tokens': 1000}
    )


@pytest.fixture
def sample_context():
    """Sample execution context"""
    return {
        'complexity': 'HIGH',
        'file_count': 25,
        'language': 'Python'
    }


class TestAgentLearningEngineInit:
    """Test initialization"""
    
    def test_init_with_custom_kg(self, mock_knowledge_graph):
        """Should initialize with custom knowledge graph"""
        engine = AgentLearningEngine(knowledge_graph=mock_knowledge_graph)
        assert engine.knowledge_graph == mock_knowledge_graph
        assert engine.decay_factor == 0.95
        assert isinstance(engine.strategy_weights, dict)
    
    def test_init_auto_kg(self):
        """Should auto-initialize knowledge graph"""
        engine = AgentLearningEngine()
        assert engine.knowledge_graph is not None
    
    def test_load_strategy_weights(self, mock_knowledge_graph):
        """Should load existing strategy weights from Tier 2"""
        mock_knowledge_graph.search_patterns.return_value = [{
            'pattern_id': 'strategy_weights',
            'context_json': json.dumps({
                'weights': {'plan:incremental': 0.85}
            })
        }]
        
        engine = AgentLearningEngine(knowledge_graph=mock_knowledge_graph)
        assert 'plan:incremental' in engine.strategy_weights
        assert engine.strategy_weights['plan:incremental'] == 0.85


class TestLearnFromExecution:
    """Test execution pattern learning"""
    
    def test_learn_from_successful_execution(
        self,
        learning_engine,
        sample_evaluation,
        sample_context
    ):
        """Should create and store pattern for successful execution"""
        pattern = learning_engine.learn_from_execution(
            operation_type="plan",
            strategy=StrategyType.INCREMENTAL,
            context=sample_context,
            evaluation=sample_evaluation,
            execution_time_seconds=120.5,
            tokens_used=1000
        )
        
        assert isinstance(pattern, ExecutionPattern)
        assert pattern.operation_type == "plan"
        assert pattern.strategy_used == StrategyType.INCREMENTAL
        assert pattern.outcome_score == 8.5
        assert pattern.success is True  # >= 6.0 threshold
        assert pattern.execution_time_seconds == 120.5
        assert pattern.tokens_used == 1000
        
        # Should call knowledge graph twice (pattern + strategy weights)
        assert learning_engine.knowledge_graph.add_pattern.call_count == 2
    
    def test_learn_from_failed_execution(
        self,
        learning_engine,
        sample_context
    ):
        """Should mark pattern as unsuccessful for low scores"""
        failed_eval = EvaluationResult(
            agent_name="TestAgent",
            category=EvaluationCategory.REASONING,
            score=4.0,  # Below threshold
            reasoning="Poor execution"
        )
        
        pattern = learning_engine.learn_from_execution(
            operation_type="tdd",
            strategy=StrategyType.SEQUENTIAL,
            context=sample_context,
            evaluation=failed_eval,
            execution_time_seconds=60.0
        )
        
        assert pattern.success is False
        assert pattern.outcome_score == 4.0
    
    def test_pattern_storage_format(
        self,
        learning_engine,
        sample_evaluation,
        sample_context
    ):
        """Should store pattern with correct format in Tier 2"""
        learning_engine.learn_from_execution(
            operation_type="documentation",
            strategy=StrategyType.PARALLEL,
            context=sample_context,
            evaluation=sample_evaluation,
            execution_time_seconds=45.0
        )
        
        # Check add_pattern calls (should be 2: pattern + weights)
        assert learning_engine.knowledge_graph.add_pattern.call_count == 2
        
        # First call should be the execution pattern
        first_call_args = learning_engine.knowledge_graph.add_pattern.call_args_list[0]
        stored_data = first_call_args[1]  # kwargs
        assert stored_data['pattern_type'] == 'execution_history'
        assert stored_data['scope'] == 'agent_learning'
        
        # Check context_json structure
        context_json = json.loads(stored_data['context_json'])
        assert context_json['operation_type'] == 'documentation'
        assert context_json['strategy'] == 'parallel'
        assert 'outcome_score' in context_json
        assert 'timestamp' in context_json


class TestGetRecommendations:
    """Test recommendation system"""
    
    def test_get_recommendations_with_history(
        self,
        learning_engine,
        sample_context
    ):
        """Should return ranked recommendations based on past patterns"""
        # Mock similar patterns
        learning_engine.knowledge_graph.search_patterns.return_value = [
            {
                'pattern_id': 'p1',
                'pattern_type': 'execution_history',
                'context_json': json.dumps({
                    'operation_type': 'plan',
                    'strategy': 'incremental',
                    'context_params': sample_context,
                    'outcome_score': 9.0,
                    'success': True,
                    'execution_time_seconds': 100
                })
            },
            {
                'pattern_id': 'p2',
                'pattern_type': 'execution_history',
                'context_json': json.dumps({
                    'operation_type': 'plan',
                    'strategy': 'incremental',
                    'context_params': sample_context,
                    'outcome_score': 8.5,
                    'success': True,
                    'execution_time_seconds': 90
                })
            },
            {
                'pattern_id': 'p3',
                'pattern_type': 'execution_history',
                'context_json': json.dumps({
                    'operation_type': 'plan',
                    'strategy': 'skeleton',
                    'context_params': sample_context,
                    'outcome_score': 6.0,
                    'success': True,
                    'execution_time_seconds': 50
                })
            }
        ]
        
        recommendations = learning_engine.get_recommendations(
            operation_type='plan',
            context=sample_context,
            top_k=2
        )
        
        assert len(recommendations) == 2
        assert all(isinstance(r, Recommendation) for r in recommendations)
        
        # Incremental should rank higher (better scores)
        assert recommendations[0].strategy == StrategyType.INCREMENTAL
        assert recommendations[0].confidence > recommendations[1].confidence
        assert len(recommendations[0].supporting_patterns) == 2  # p1 and p2
    
    def test_get_recommendations_no_history(
        self,
        learning_engine,
        sample_context
    ):
        """Should return default recommendations when no patterns exist"""
        # Empty search results
        learning_engine.knowledge_graph.search_patterns.return_value = []
        
        recommendations = learning_engine.get_recommendations(
            operation_type='plan',
            context=sample_context
        )
        
        assert len(recommendations) == 1
        assert recommendations[0].strategy == StrategyType.INCREMENTAL  # Default for 'plan'
        assert recommendations[0].confidence == 0.5
        assert "No historical data" in recommendations[0].reasoning
    
    def test_recommendation_confidence_calculation(
        self,
        learning_engine,
        sample_context
    ):
        """Should calculate confidence based on success rate and sample size"""
        # Mock patterns with varying success
        learning_engine.knowledge_graph.search_patterns.return_value = [
            {
                'pattern_id': f'p{i}',
                'pattern_type': 'execution_history',
                'context_json': json.dumps({
                    'operation_type': 'tdd',
                    'strategy': 'sequential',
                    'context_params': sample_context,
                    'outcome_score': 8.0 if i < 8 else 5.0,  # 80% success rate
                    'success': i < 8,
                    'execution_time_seconds': 100
                })
            }
            for i in range(10)
        ]
        
        recommendations = learning_engine.get_recommendations(
            operation_type='tdd',
            context=sample_context
        )
        
        # High success rate should yield high confidence
        assert recommendations[0].confidence > 0.7
        assert recommendations[0].expected_outcome > 7.0


class TestUpdateStrategyWeights:
    """Test strategy weighting algorithm"""
    
    def test_update_new_strategy(self, learning_engine):
        """Should initialize new strategy weight with first outcome"""
        learning_engine.update_strategy_weights(
            operation_type="plan",
            strategy=StrategyType.INCREMENTAL,
            outcome_score=8.0
        )
        
        strategy_key = "plan:incremental"
        assert strategy_key in learning_engine.strategy_weights
        
        # EMA: 0.95 * 0.5 + 0.05 * 0.8 = 0.515
        expected = 0.95 * 0.5 + 0.05 * 0.8
        assert abs(learning_engine.strategy_weights[strategy_key] - expected) < 0.001
    
    def test_update_existing_strategy(self, learning_engine):
        """Should apply exponential moving average to existing weight"""
        strategy_key = "tdd:sequential"
        learning_engine.strategy_weights[strategy_key] = 0.7
        
        learning_engine.update_strategy_weights(
            operation_type="tdd",
            strategy=StrategyType.SEQUENTIAL,
            outcome_score=9.0
        )
        
        # EMA: 0.95 * 0.7 + 0.05 * 0.9 = 0.71
        expected = 0.95 * 0.7 + 0.05 * 0.9
        assert abs(learning_engine.strategy_weights[strategy_key] - expected) < 0.001
    
    def test_weight_decay_over_time(self, learning_engine):
        """Should decay weights with decay factor"""
        learning_engine.update_strategy_weights(
            operation_type="plan",
            strategy=StrategyType.SKELETON,
            outcome_score=10.0
        )
        
        weight_after_first = learning_engine.strategy_weights["plan:skeleton"]
        
        # Update with lower score
        learning_engine.update_strategy_weights(
            operation_type="plan",
            strategy=StrategyType.SKELETON,
            outcome_score=5.0
        )
        
        weight_after_second = learning_engine.strategy_weights["plan:skeleton"]
        
        # Weight should have decreased
        assert weight_after_second < weight_after_first
    
    def test_persists_weights_to_tier2(self, learning_engine):
        """Should save weights to knowledge graph"""
        learning_engine.update_strategy_weights(
            operation_type="documentation",
            strategy=StrategyType.PARALLEL,
            outcome_score=7.5
        )
        
        # Should call add_pattern to persist
        learning_engine.knowledge_graph.add_pattern.assert_called()
        
        # Check last call was for strategy_weights
        last_call = learning_engine.knowledge_graph.add_pattern.call_args
        assert last_call[1]['pattern_id'] == 'strategy_weights'


class TestContextSimilarity:
    """Test context similarity calculation"""
    
    def test_exact_match(self, learning_engine):
        """Should return 1.0 for identical contexts"""
        context_a = {'complexity': 'HIGH', 'file_count': 25}
        context_b = {'complexity': 'HIGH', 'file_count': 25}
        
        similarity = learning_engine._calculate_context_similarity(context_a, context_b)
        assert similarity == 1.0
    
    def test_partial_match(self, learning_engine):
        """Should return partial score for some matching keys"""
        context_a = {'complexity': 'HIGH', 'file_count': 25, 'language': 'Python'}
        context_b = {'complexity': 'HIGH', 'file_count': 30, 'language': 'JavaScript'}
        
        similarity = learning_engine._calculate_context_similarity(context_a, context_b)
        assert 0.0 < similarity < 1.0
    
    def test_numeric_tolerance(self, learning_engine):
        """Should accept numeric values within 20% tolerance"""
        context_a = {'file_count': 100}
        context_b = {'file_count': 110}  # 10% difference
        
        similarity = learning_engine._calculate_context_similarity(context_a, context_b)
        assert similarity == 0.5  # Partial match for numeric tolerance
    
    def test_no_common_keys(self, learning_engine):
        """Should return 0.0 for completely different contexts"""
        context_a = {'complexity': 'HIGH'}
        context_b = {'language': 'Python'}
        
        similarity = learning_engine._calculate_context_similarity(context_a, context_b)
        assert similarity == 0.0
    
    def test_empty_contexts(self, learning_engine):
        """Should handle empty contexts gracefully"""
        similarity = learning_engine._calculate_context_similarity({}, {})
        assert similarity == 0.0


class TestPatternGeneration:
    """Test pattern ID generation"""
    
    def test_unique_pattern_ids(self, learning_engine):
        """Should generate unique pattern IDs"""
        import time
        context = {'complexity': 'HIGH'}
        
        id1 = learning_engine._generate_pattern_id("plan", StrategyType.INCREMENTAL, context)
        time.sleep(1.1)  # Ensure different timestamp (seconds precision)
        id2 = learning_engine._generate_pattern_id("plan", StrategyType.INCREMENTAL, context)
        
        # Should be different due to timestamp
        assert id1 != id2, f"Expected different IDs but got: {id1} == {id2}"
        assert id1.startswith("pattern_plan_incremental")
        assert id2.startswith("pattern_plan_incremental")
    
    def test_pattern_id_includes_context_hash(self, learning_engine):
        """Should include context hash in pattern ID"""
        context1 = {'complexity': 'HIGH'}
        context2 = {'complexity': 'LOW'}
        
        id1 = learning_engine._generate_pattern_id("tdd", StrategyType.SEQUENTIAL, context1)
        id2 = learning_engine._generate_pattern_id("tdd", StrategyType.SEQUENTIAL, context2)
        
        # Different contexts should produce different hashes
        assert id1.split('_')[3] != id2.split('_')[3]  # context_hash part


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_learn_with_zero_tokens(
        self,
        learning_engine,
        sample_evaluation,
        sample_context
    ):
        """Should handle executions with no token count"""
        pattern = learning_engine.learn_from_execution(
            operation_type="plan",
            strategy=StrategyType.ADAPTIVE,
            context=sample_context,
            evaluation=sample_evaluation,
            execution_time_seconds=50.0,
            tokens_used=None  # No tokens
        )
        
        assert pattern.tokens_used is None
    
    def test_recommendations_with_non_execution_patterns(
        self,
        learning_engine,
        sample_context
    ):
        """Should filter out non-execution_history patterns"""
        learning_engine.knowledge_graph.search_patterns.return_value = [
            {
                'pattern_id': 'other_pattern',
                'pattern_type': 'workflow_template',  # Wrong type
                'context_json': json.dumps({})
            }
        ]
        
        recommendations = learning_engine.get_recommendations(
            operation_type='plan',
            context=sample_context
        )
        
        # Should fall back to defaults
        assert len(recommendations) == 1
        assert "No historical data" in recommendations[0].reasoning
    
    def test_malformed_pattern_json(
        self,
        learning_engine,
        sample_context
    ):
        """Should handle malformed JSON gracefully"""
        learning_engine.knowledge_graph.search_patterns.return_value = [
            {
                'pattern_id': 'bad_pattern',
                'pattern_type': 'execution_history',
                'context_json': '{"operation_type": "plan"}'  # Valid but incomplete JSON
            }
        ]
        
        # Should not crash - will skip patterns without required fields
        recommendations = learning_engine.get_recommendations(
            operation_type='plan',
            context=sample_context
        )
        
        # Should fall back to defaults since pattern is incomplete
        assert isinstance(recommendations, list)
        assert len(recommendations) >= 1


class TestPerformance:
    """Test performance requirements"""
    
    @pytest.mark.slow
    def test_recommendation_retrieval_speed(
        self,
        learning_engine,
        sample_context
    ):
        """Should retrieve recommendations in <50ms"""
        import time
        
        # Mock 20 patterns
        learning_engine.knowledge_graph.search_patterns.return_value = [
            {
                'pattern_id': f'p{i}',
                'pattern_type': 'execution_history',
                'context_json': json.dumps({
                    'operation_type': 'plan',
                    'strategy': 'incremental',
                    'context_params': sample_context,
                    'outcome_score': 8.0,
                    'success': True,
                    'execution_time_seconds': 100
                })
            }
            for i in range(20)
        ]
        
        start = time.time()
        recommendations = learning_engine.get_recommendations(
            operation_type='plan',
            context=sample_context
        )
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 50  # Target: <50ms
        assert len(recommendations) > 0
    
    def test_pattern_storage_size(self, learning_engine, sample_evaluation, sample_context):
        """Should store patterns efficiently"""
        pattern = learning_engine.learn_from_execution(
            operation_type="plan",
            strategy=StrategyType.INCREMENTAL,
            context=sample_context,
            evaluation=sample_evaluation,
            execution_time_seconds=100.0,
            tokens_used=1000
        )
        
        # Check stored JSON size
        call_args = learning_engine.knowledge_graph.add_pattern.call_args
        context_json = call_args[1]['context_json']
        
        # Should be < 1KB per pattern
        assert len(context_json) < 1024
