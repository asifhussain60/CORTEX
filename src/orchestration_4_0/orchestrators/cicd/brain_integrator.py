"""
Brain Integrator for CI/CD Self-Healing Orchestrator

Integrates CI/CD orchestrator with Brain Tier 2 for pattern learning.

Author: Asif Hussain
Version: 1.0
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

from ....brain.tier2.knowledge_graph import KnowledgeGraph, Pattern
from .schemas import (
    FailureAnalysis,
    FixAttempt,
    HealingResult,
    FailureCategory,
    FixStrategy
)


class BrainIntegrator:
    """
    Integrates CI/CD orchestrator with Brain Tier 2 for pattern learning.
    
    Features:
    - Store failure patterns in Knowledge Graph
    - Learn from successful fix strategies
    - Retrieve historical patterns for similar failures
    - Track fix strategy success rates
    - Cross-repo pattern learning
    """
    
    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        namespace: str = "cicd",
        min_confidence: float = 0.6,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Brain integrator.
        
        Args:
            knowledge_graph: Tier 2 Knowledge Graph instance
            namespace: Namespace for CI/CD patterns
            min_confidence: Minimum confidence for pattern retrieval
            logger: Optional logger instance
        """
        self.kg = knowledge_graph
        self.namespace = namespace
        self.min_confidence = min_confidence
        self.logger = logger or logging.getLogger(__name__)
        
        self.logger.debug(f"BrainIntegrator initialized (namespace: {namespace})")
    
    def store_failure_pattern(
        self,
        failure: FailureAnalysis,
        fix_result: Optional[HealingResult] = None
    ) -> str:
        """
        Store failure pattern in Knowledge Graph.
        
        Args:
            failure: Failure analysis
            fix_result: Optional healing result if fix was attempted
            
        Returns:
            Pattern ID
        """
        context = {
            "category": failure.category if isinstance(failure.category, str) else failure.category.value,
            "confidence": failure.confidence,
            "root_cause": failure.root_cause,
            "error_messages": failure.error_messages,
            "affected_files": failure.affected_files,
            "affected_dependencies": failure.affected_dependencies
        }
        
        # Add fix information if available
        if fix_result and len(fix_result.fix_attempts) > 0:
            # Use first successful fix or last attempt
            successful_fix = next(
                (fa for fa in fix_result.fix_attempts if fa.success),
                fix_result.fix_attempts[-1]
            )
            context["fix_applied"] = successful_fix.strategy if isinstance(successful_fix.strategy, str) else successful_fix.strategy.value
            context["success"] = fix_result.healed
            context["attempts"] = len(fix_result.fix_attempts)
        
        pattern_id = self.kg.store_pattern(
            title=f"CI/CD Failure: {context['category']}",
            pattern_type="cicd_failure",
            context=context,
            confidence=failure.confidence
        )
        
        self.logger.debug(f"Stored failure pattern: {pattern_id}")
        return pattern_id
    
    def store_fix_strategy(
        self,
        strategy: FixStrategy,
        failure_category: FailureCategory,
        success: bool,
        execution_time: float
    ) -> str:
        """
        Store fix strategy outcome for learning.
        
        Args:
            strategy: Fix strategy used
            failure_category: Category of failure
            success: Whether fix was successful
            execution_time: Time taken to execute fix
            
        Returns:
            Pattern ID
        """
        context = {
            "strategy": strategy if isinstance(strategy, str) else strategy.value,
            "failure_category": failure_category if isinstance(failure_category, str) else failure_category.value,
            "success": success,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        pattern_id = self.kg.store_pattern(
            title=f"Fix Strategy: {context['strategy']}",
            pattern_type="cicd_fix_strategy",
            context=context,
            confidence=1.0 if success else 0.3
        )
        
        # Update pattern confidence based on historical success
        self._update_strategy_confidence(strategy, failure_category, success)
        
        self.logger.debug(f"Stored fix strategy: {pattern_id} (success: {success})")
        return pattern_id
    
    def get_similar_failures(
        self,
        failure: FailureAnalysis,
        limit: int = 5
    ) -> List[Pattern]:
        """
        Retrieve similar historical failures from Knowledge Graph.
        
        Args:
            failure: Current failure analysis
            limit: Maximum number of patterns to return
            
        Returns:
            List of similar failure patterns
        """
        # Search by category and root cause
        category_str = failure.category if isinstance(failure.category, str) else failure.category.value
        search_query = f"{category_str} {failure.root_cause}"
        
        patterns = self.kg.search_patterns(
            query=search_query,
            pattern_type="cicd_failure",
            limit=limit
        )
        
        # Filter by minimum confidence
        filtered = [p for p in patterns if p.confidence >= self.min_confidence]
        
        self.logger.debug(f"Found {len(filtered)} similar failures")
        return filtered
    
    def get_recommended_strategies(
        self,
        failure_category: FailureCategory,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get recommended fix strategies based on historical success.
        
        Args:
            failure_category: Category of current failure
            limit: Maximum number of strategies to return
            
        Returns:
            List of recommended strategies with confidence scores
        """
        patterns = self.kg.search_patterns(
            query=failure_category if isinstance(failure_category, str) else failure_category.value,
            pattern_type="cicd_fix_strategy",
            limit=limit * 2  # Get more, then filter
        )
        
        # Group by strategy and calculate success rates
        strategy_stats: Dict[str, Dict[str, Any]] = {}
        
        category_str = failure_category if isinstance(failure_category, str) else failure_category.value
        
        for pattern in patterns:
            context = pattern.context
            if context.get("failure_category") != category_str:
                continue
            
            strategy = context.get("strategy")
            if not strategy:
                continue
            
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "strategy": strategy,
                    "total": 0,
                    "successful": 0,
                    "avg_execution_time": 0.0,
                    "confidence": 0.0
                }
            
            stats = strategy_stats[strategy]
            stats["total"] += 1
            if context.get("success"):
                stats["successful"] += 1
            
            # Running average of execution time
            current_avg = stats["avg_execution_time"]
            new_time = context.get("execution_time", 0.0)
            stats["avg_execution_time"] = (
                (current_avg * (stats["total"] - 1) + new_time) / stats["total"]
            )
        
        # Calculate success rates and sort
        recommendations = []
        for strategy, stats in strategy_stats.items():
            if stats["total"] > 0:
                success_rate = stats["successful"] / stats["total"]
                stats["success_rate"] = success_rate
                stats["confidence"] = min(success_rate, pattern.confidence)
                recommendations.append(stats)
        
        # Sort by success rate (desc) then execution time (asc)
        recommendations.sort(
            key=lambda x: (-x["success_rate"], x["avg_execution_time"])
        )
        
        result = recommendations[:limit]
        self.logger.debug(f"Recommended {len(result)} strategies for {failure_category.value}")
        return result
    
    def _update_strategy_confidence(
        self,
        strategy: FixStrategy,
        failure_category: FailureCategory,
        success: bool
    ):
        """
        Update confidence scores for strategy patterns.
        
        Uses exponential moving average to adapt to recent performance.
        
        Args:
            strategy: Fix strategy
            failure_category: Failure category
            success: Whether fix succeeded
        """
        # Quote the search query to prevent FTS5 syntax errors
        search_str = f'"{strategy if isinstance(strategy, str) else strategy.value}" "{failure_category if isinstance(failure_category, str) else failure_category.value}"'
        
        patterns = self.kg.search_patterns(
            query=search_str,
            pattern_type="cicd_fix_strategy",
            limit=10
        )
        
        strategy_str = strategy if isinstance(strategy, str) else strategy.value
        
        for pattern in patterns:
            if pattern.context.get("strategy") == strategy_str:
                # Exponential moving average: 0.3 weight to new observation
                new_confidence = pattern.confidence * 0.7 + (1.0 if success else 0.0) * 0.3
                self.kg.update_pattern_confidence(pattern.pattern_id, new_confidence)
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """
        Get aggregate statistics on failures and fixes.
        
        Returns:
            Dictionary with statistics
        """
        all_failures = self.kg.search_patterns(
            query="",
            pattern_type="cicd_failure",
            limit=1000
        )
        
        all_strategies = self.kg.search_patterns(
            query="",
            pattern_type="cicd_fix_strategy",
            limit=1000
        )
        
        # Analyze failures
        category_counts: Dict[str, int] = {}
        for pattern in all_failures:
            category = pattern.context.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Analyze fix success
        total_fixes = len(all_strategies)
        successful_fixes = sum(
            1 for p in all_strategies if p.context.get("success", False)
        )
        
        success_rate = successful_fixes / total_fixes if total_fixes > 0 else 0.0
        
        return {
            "total_failures": len(all_failures),
            "failures_by_category": category_counts,
            "total_fix_attempts": total_fixes,
            "successful_fixes": successful_fixes,
            "overall_success_rate": success_rate,
            "patterns_stored": len(all_failures) + len(all_strategies)
        }
    
    def learn_from_healing_result(self, result: HealingResult):
        """
        Learn from complete healing result (failure + fix outcome).
        
        This is the primary learning method called after each healing attempt.
        
        Args:
            result: Complete healing result
        """
        if not result.initial_failure:
            self.logger.warning("No initial failure in healing result")
            return
        
        # Store failure pattern
        pattern_id = self.store_failure_pattern(
            result.initial_failure,
            result
        )
        
        # Store fix strategies from fix_attempts
        for fix_attempt in result.fix_attempts:
            strategy_enum = fix_attempt.strategy if isinstance(fix_attempt.strategy, str) else fix_attempt.strategy.value
            category_enum = result.initial_failure.category if isinstance(result.initial_failure.category, str) else result.initial_failure.category.value
            
            self.store_fix_strategy(
                strategy_enum,
                category_enum,
                fix_attempt.success and fix_attempt.verification_passed,
                fix_attempt.time_seconds
            )
        
        self.logger.info(
            f"Learned from healing result: {pattern_id} "
            f"(healed: {result.healed}, attempts: {len(result.fix_attempts)})"
        )
