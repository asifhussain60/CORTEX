"""
Agent Learning Engine

Phase 5 Task 5.11: Enable agents to learn from execution history and improve over time.

Core Capabilities:
- Learn from agent execution + evaluation results
- Store learned patterns in Brain Tier 2 (knowledge graph)
- Retrieve recommendations based on similar past executions
- Adapt strategy weights based on success rates

Integration Points:
- Brain Tier 2 KnowledgeGraph (pattern storage)
- AgentEvaluator (learn from evaluation results)
- ContextValidator (enhance auto-retrieval)
- All orchestrators (retrieve recommendations)

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from src.tier2 import KnowledgeGraph
from src.orchestration_4_0.frameworks.agent_evaluator import (
    AgentEvaluator,
    EvaluationResult,
    EvaluationCategory
)

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Strategy categories for agent execution"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    NESTED = "nested"
    INCREMENTAL = "incremental"
    SKELETON = "skeleton"
    ADAPTIVE = "adaptive"


@dataclass
class ExecutionPattern:
    """Learned pattern from past execution"""
    pattern_id: str
    operation_type: str  # e.g., "plan", "tdd", "documentation"
    strategy_used: StrategyType
    context_params: Dict[str, Any]  # Contextual parameters (complexity, file_count, etc.)
    outcome_score: float  # Evaluation score (1-10)
    execution_time_seconds: float
    tokens_used: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True


@dataclass
class Recommendation:
    """Strategy recommendation based on learned patterns"""
    strategy: StrategyType
    confidence: float  # 0.0-1.0
    reasoning: str
    supporting_patterns: List[str]  # pattern_ids that support this recommendation
    expected_outcome: float  # Predicted outcome score (1-10)
    

class AgentLearningEngine:
    """
    Learn from agent execution history and improve decision-making over time.
    
    Uses exponential moving average for strategy weights with decay factor
    to prioritize recent patterns while retaining historical knowledge.
    """
    
    def __init__(self, knowledge_graph: Optional[KnowledgeGraph] = None):
        """
        Initialize learning engine.
        
        Args:
            knowledge_graph: Brain Tier 2 knowledge graph (default: auto-initialize)
        """
        self.knowledge_graph = knowledge_graph or KnowledgeGraph()
        self.strategy_weights: Dict[str, float] = {}  # strategy_key -> weight
        self.decay_factor = 0.95  # Exponential decay for old patterns
        self._load_strategy_weights()
        logger.info("🧠 Agent Learning Engine initialized")
    
    def learn_from_execution(
        self,
        operation_type: str,
        strategy: StrategyType,
        context: Dict[str, Any],
        evaluation: EvaluationResult,
        execution_time_seconds: float,
        tokens_used: Optional[int] = None
    ) -> ExecutionPattern:
        """
        Extract lessons from execution + evaluation results and store in Tier 2.
        
        Args:
            operation_type: Type of operation (e.g., "plan", "tdd", "documentation")
            strategy: Strategy used for execution
            context: Contextual parameters (complexity, file_count, etc.)
            evaluation: Evaluation result from AgentEvaluator
            execution_time_seconds: Execution duration
            tokens_used: Optional token count
            
        Returns:
            ExecutionPattern stored in knowledge graph
        """
        logger.info(f"📚 Learning from {operation_type} execution (strategy: {strategy.value})")
        
        # Create execution pattern
        pattern = ExecutionPattern(
            pattern_id=self._generate_pattern_id(operation_type, strategy, context),
            operation_type=operation_type,
            strategy_used=strategy,
            context_params=context,
            outcome_score=evaluation.score,
            execution_time_seconds=execution_time_seconds,
            tokens_used=tokens_used,
            success=(evaluation.score >= 6.0)  # Threshold for success
        )
        
        # Store pattern in Tier 2
        self._store_pattern(pattern)
        
        # Update strategy weights
        self.update_strategy_weights(
            operation_type,
            strategy,
            pattern.outcome_score
        )
        
        logger.info(f"✅ Learned pattern {pattern.pattern_id} (score: {pattern.outcome_score:.1f}/10)")
        return pattern
    
    def get_recommendations(
        self,
        operation_type: str,
        context: Dict[str, Any],
        top_k: int = 3
    ) -> List[Recommendation]:
        """
        Recommend strategies based on similar past executions.
        
        Uses cosine similarity on context parameters to find similar patterns,
        then ranks strategies by success rate and confidence.
        
        Args:
            operation_type: Type of operation (e.g., "plan", "tdd")
            context: Current context parameters
            top_k: Number of recommendations to return
            
        Returns:
            List of ranked recommendations with confidence scores
        """
        logger.info(f"🔍 Getting recommendations for {operation_type}")
        
        # Retrieve similar patterns from Tier 2
        similar_patterns = self._find_similar_patterns(operation_type, context)
        
        if not similar_patterns:
            logger.warning(f"⚠️ No historical patterns found for {operation_type}")
            return self._get_default_recommendations(operation_type)
        
        # Calculate strategy success rates
        strategy_stats = self._calculate_strategy_statistics(similar_patterns)
        
        # Rank strategies by weighted score
        recommendations = []
        for strategy, stats in strategy_stats.items():
            confidence = self._calculate_confidence(
                stats['success_rate'],
                stats['sample_count'],
                stats['avg_score']
            )
            
            recommendation = Recommendation(
                strategy=StrategyType(strategy),
                confidence=confidence,
                reasoning=self._generate_reasoning(stats, similar_patterns),
                supporting_patterns=[p['pattern_id'] for p in similar_patterns if p['strategy'] == strategy],
                expected_outcome=stats['avg_score']
            )
            recommendations.append(recommendation)
        
        # Sort by confidence and return top_k
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        
        logger.info(f"📋 Generated {len(recommendations)} recommendations (top {top_k} returned)")
        return recommendations[:top_k]
    
    def update_strategy_weights(
        self,
        operation_type: str,
        strategy: StrategyType,
        outcome_score: float
    ):
        """
        Adjust strategy weights based on execution success using exponential moving average.
        
        Formula: new_weight = decay * old_weight + (1 - decay) * normalized_score
        
        Args:
            operation_type: Type of operation
            strategy: Strategy used
            outcome_score: Evaluation score (1-10)
        """
        strategy_key = f"{operation_type}:{strategy.value}"
        normalized_score = outcome_score / 10.0  # Normalize to 0.0-1.0
        
        # Get current weight (default 0.5)
        current_weight = self.strategy_weights.get(strategy_key, 0.5)
        
        # Exponential moving average
        new_weight = (self.decay_factor * current_weight) + ((1 - self.decay_factor) * normalized_score)
        
        self.strategy_weights[strategy_key] = new_weight
        
        logger.debug(f"📊 Updated {strategy_key}: {current_weight:.3f} → {new_weight:.3f}")
        
        # Persist to Tier 2
        self._save_strategy_weights()
    
    def _store_pattern(self, pattern: ExecutionPattern):
        """Store execution pattern in Tier 2 knowledge graph"""
        pattern_data = {
            'pattern_id': pattern.pattern_id,
            'title': f"{pattern.operation_type} - {pattern.strategy_used.value}",
            'pattern_type': 'execution_history',
            'confidence': pattern.outcome_score / 10.0,  # Normalize to 0.0-1.0
            'context_json': json.dumps({
                'operation_type': pattern.operation_type,
                'strategy': pattern.strategy_used.value,
                'context_params': pattern.context_params,
                'outcome_score': pattern.outcome_score,
                'execution_time_seconds': pattern.execution_time_seconds,
                'tokens_used': pattern.tokens_used,
                'success': pattern.success,
                'timestamp': pattern.timestamp.isoformat()
            }),
            'scope': 'agent_learning',
            'namespaces': pattern.operation_type
        }
        
        self.knowledge_graph.add_pattern(**pattern_data)
    
    def _find_similar_patterns(
        self,
        operation_type: str,
        context: Dict[str, Any],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find similar patterns using Tier 2 full-text search + context similarity.
        
        Returns list of pattern dictionaries with similarity scores.
        """
        # Search by operation type
        search_results = self.knowledge_graph.search_patterns(
            query=operation_type,
            limit=limit
        )
        
        # Filter by pattern_type and calculate context similarity
        similar_patterns = []
        for result in search_results:
            try:
                pattern_context = json.loads(result.get('context_json', '{}'))
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Skipping pattern with invalid JSON: {result.get('pattern_id')}")
                continue
            
            # Only consider execution_history patterns
            if result.get('pattern_type') != 'execution_history':
                continue
            
            # Only consider matching operation types
            if pattern_context.get('operation_type') != operation_type:
                continue
            
            # Must have strategy field
            if 'strategy' not in pattern_context:
                logger.warning(f"⚠️ Skipping pattern without strategy: {result.get('pattern_id')}")
                continue
            
            # Calculate context similarity
            similarity = self._calculate_context_similarity(
                context,
                pattern_context.get('context_params', {})
            )
            
            similar_patterns.append({
                'pattern_id': result['pattern_id'],
                'strategy': pattern_context.get('strategy'),
                'outcome_score': pattern_context.get('outcome_score', 0),
                'success': pattern_context.get('success', False),
                'execution_time_seconds': pattern_context.get('execution_time_seconds', 0),
                'similarity': similarity
            })
        
        # Sort by similarity
        similar_patterns.sort(key=lambda p: p['similarity'], reverse=True)
        
        return similar_patterns
    
    def _calculate_context_similarity(
        self,
        context_a: Dict[str, Any],
        context_b: Dict[str, Any]
    ) -> float:
        """
        Calculate cosine similarity between two context dictionaries.
        
        Simple implementation: count matching keys with similar values.
        """
        if not context_a or not context_b:
            return 0.0
        
        common_keys = set(context_a.keys()) & set(context_b.keys())
        if not common_keys:
            return 0.0
        
        matching_count = 0
        for key in common_keys:
            val_a = context_a[key]
            val_b = context_b[key]
            
            # Exact match
            if val_a == val_b:
                matching_count += 1
            # Numeric similarity (within 20% tolerance)
            elif isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                if abs(val_a - val_b) / max(val_a, val_b, 1) < 0.2:
                    matching_count += 0.5
        
        return matching_count / len(common_keys)
    
    def _calculate_strategy_statistics(
        self,
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate success rate, average score, and sample count per strategy.
        
        Returns: {strategy_name: {success_rate, avg_score, sample_count}}
        """
        strategy_stats: Dict[str, Dict[str, Any]] = {}
        
        for pattern in patterns:
            strategy = pattern['strategy']
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    'total': 0,
                    'successes': 0,
                    'scores': []
                }
            
            strategy_stats[strategy]['total'] += 1
            if pattern['success']:
                strategy_stats[strategy]['successes'] += 1
            strategy_stats[strategy]['scores'].append(pattern['outcome_score'])
        
        # Calculate final statistics
        result = {}
        for strategy, stats in strategy_stats.items():
            result[strategy] = {
                'success_rate': stats['successes'] / stats['total'],
                'avg_score': sum(stats['scores']) / len(stats['scores']),
                'sample_count': stats['total']
            }
        
        return result
    
    def _calculate_confidence(
        self,
        success_rate: float,
        sample_count: int,
        avg_score: float
    ) -> float:
        """
        Calculate confidence score (0.0-1.0) based on success rate, sample size, and average score.
        
        Uses weighted combination with sample size penalty for low sample counts.
        """
        # Sample size confidence (sigmoid)
        sample_confidence = 1.0 / (1.0 + pow(2.718, -(sample_count - 5) / 3))
        
        # Weighted combination
        confidence = (
            0.5 * success_rate +
            0.3 * (avg_score / 10.0) +
            0.2 * sample_confidence
        )
        
        return min(confidence, 1.0)
    
    def _generate_reasoning(
        self,
        stats: Dict[str, float],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable reasoning for recommendation"""
        success_rate_pct = stats['success_rate'] * 100
        avg_score = stats['avg_score']
        sample_count = stats['sample_count']
        
        return (
            f"Based on {sample_count} similar executions: "
            f"{success_rate_pct:.0f}% success rate, "
            f"average score {avg_score:.1f}/10"
        )
    
    def _get_default_recommendations(self, operation_type: str) -> List[Recommendation]:
        """Return default recommendations when no patterns exist"""
        defaults = {
            'plan': StrategyType.INCREMENTAL,
            'tdd': StrategyType.SEQUENTIAL,
            'documentation': StrategyType.SEQUENTIAL
        }
        
        default_strategy = defaults.get(operation_type, StrategyType.ADAPTIVE)
        
        return [
            Recommendation(
                strategy=default_strategy,
                confidence=0.5,
                reasoning="No historical data - using default strategy",
                supporting_patterns=[],
                expected_outcome=7.0
            )
        ]
    
    def _generate_pattern_id(
        self,
        operation_type: str,
        strategy: StrategyType,
        context: Dict[str, Any]
    ) -> str:
        """Generate unique pattern ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        context_hash = hash(json.dumps(context, sort_keys=True)) % 10000
        return f"pattern_{operation_type}_{strategy.value}_{context_hash}_{timestamp}"
    
    def _load_strategy_weights(self):
        """Load strategy weights from Tier 2"""
        # Search for strategy_weights pattern
        results = self.knowledge_graph.search_patterns(
            query="strategy_weights",
            limit=1
        )
        
        if results and results[0].get('pattern_id') == 'strategy_weights':
            context = json.loads(results[0].get('context_json', '{}'))
            self.strategy_weights = context.get('weights', {})
            logger.info(f"📊 Loaded {len(self.strategy_weights)} strategy weights from Tier 2")
    
    def _save_strategy_weights(self):
        """Persist strategy weights to Tier 2"""
        pattern_data = {
            'pattern_id': 'strategy_weights',
            'title': 'Agent Strategy Weights',
            'pattern_type': 'strategy_weights',
            'confidence': 1.0,
            'context_json': json.dumps({
                'weights': self.strategy_weights,
                'last_updated': datetime.now().isoformat()
            }),
            'scope': 'agent_learning',
            'namespaces': 'system'
        }
        
        self.knowledge_graph.add_pattern(**pattern_data)
