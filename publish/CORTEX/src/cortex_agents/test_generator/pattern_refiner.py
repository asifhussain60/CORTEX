"""
Pattern Refinement System

Updates pattern confidence based on test execution results and quality feedback.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

from .tier2_pattern_store import Tier2PatternStore, BusinessPattern
from .test_quality_scorer import PatternFeedback, QualityMetrics


@dataclass
class RefinementResult:
    """Result of pattern refinement operation"""
    patterns_promoted: int
    patterns_demoted: int
    patterns_archived: int
    confidence_adjustments: Dict[int, float]  # pattern_id -> new_confidence


class PatternRefiner:
    """
    Refines patterns based on feedback from test execution.
    
    Features:
    - Confidence updates (Bayesian)
    - Pattern promotion/demotion
    - Conflict resolution
    - Pattern archival (very low confidence)
    """
    
    def __init__(self, pattern_store: Tier2PatternStore):
        """
        Initialize pattern refiner.
        
        Args:
            pattern_store: Tier 2 pattern storage
        """
        self.pattern_store = pattern_store
        self.min_confidence_threshold = 0.2  # Archive below this
        self.promotion_threshold = 0.85  # High confidence
        self.demotion_threshold = 0.4  # Low confidence
    
    def refine_pattern(
        self,
        pattern_id: int,
        feedback: PatternFeedback
    ) -> float:
        """
        Refine a single pattern based on feedback.
        
        Args:
            pattern_id: Pattern to refine
            feedback: Quality feedback
            
        Returns:
            New confidence score
        """
        # Get current pattern by ID
        pattern = self.pattern_store.get_pattern_by_id(pattern_id)
        if not pattern:
            return 0.0
        
        # Calculate new confidence using Bayesian update
        prior_confidence = pattern.confidence
        evidence_strength = feedback.effectiveness
        
        # Bayesian formula: P(pattern|evidence) = P(evidence|pattern) * P(pattern) / P(evidence)
        # Simplified: weight prior with evidence
        new_confidence = (
            prior_confidence * 0.7 +  # Weight historical performance
            evidence_strength * 0.3    # Weight current evidence
        )
        
        # Apply promotion/demotion adjustments
        if feedback.should_promote:
            new_confidence = min(1.0, new_confidence * 1.1)  # 10% boost
        elif feedback.should_demote:
            new_confidence = max(0.1, new_confidence * 0.9)  # 10% penalty
        
        # Ensure bounds
        new_confidence = max(0.1, min(1.0, new_confidence))
        
        # Update in store
        self.pattern_store.update_pattern_usage(
            pattern_id,
            success=(feedback.effectiveness >= 0.7)
        )
        
        return new_confidence
    
    def refine_batch(
        self,
        feedback_list: List[PatternFeedback]
    ) -> RefinementResult:
        """
        Refine multiple patterns in batch.
        
        Args:
            feedback_list: List of pattern feedbacks
            
        Returns:
            Refinement results summary
        """
        promoted = 0
        demoted = 0
        archived = 0
        adjustments = {}
        
        for feedback in feedback_list:
            new_confidence = self.refine_pattern(feedback.pattern_id, feedback)
            adjustments[feedback.pattern_id] = new_confidence
            
            # Track promotion/demotion
            if new_confidence >= self.promotion_threshold:
                promoted += 1
            elif new_confidence <= self.demotion_threshold:
                demoted += 1
            
            # Archive very low confidence patterns
            if new_confidence < self.min_confidence_threshold:
                archived += 1
                # In production, would move to archive table
        
        return RefinementResult(
            patterns_promoted=promoted,
            patterns_demoted=demoted,
            patterns_archived=archived,
            confidence_adjustments=adjustments
        )
    
    def resolve_conflicts(
        self,
        domain: str,
        operation: str
    ) -> List[BusinessPattern]:
        """
        Resolve conflicting patterns for same domain/operation.
        
        Keeps highest confidence patterns, archives low-confidence conflicts.
        
        Args:
            domain: Pattern domain
            operation: Pattern operation
            
        Returns:
            Resolved patterns (kept patterns)
        """
        # Get all patterns for this domain/operation
        all_patterns = self.pattern_store.get_patterns_by_domain(
            domain=domain,
            min_confidence=0.0,
            limit=100
        )
        
        # Filter to matching operation
        matching = [
            p for p in all_patterns
            if p.operation == operation
        ]
        
        if len(matching) <= 1:
            return matching  # No conflict
        
        # Sort by confidence
        sorted_patterns = sorted(
            matching,
            key=lambda p: (p.confidence, p.success_count),
            reverse=True
        )
        
        # Keep top patterns, archive low-confidence duplicates
        keep_threshold = sorted_patterns[0].confidence * 0.7
        
        kept = []
        for pattern in sorted_patterns:
            if pattern.confidence >= keep_threshold:
                kept.append(pattern)
            # else: would archive in production
        
        return kept
    
    def analyze_pattern_effectiveness(
        self,
        domain: Optional[str] = None,
        min_usage_count: int = 5
    ) -> Dict[str, any]:
        """
        Analyze pattern effectiveness across domains.
        
        Args:
            domain: Filter by domain (optional)
            min_usage_count: Minimum usage for analysis
            
        Returns:
            Analysis results
        """
        if domain:
            patterns = self.pattern_store.get_patterns_by_domain(
                domain=domain,
                min_confidence=0.0,
                limit=1000
            )
        else:
            # Get all high-usage patterns
            stats = self.pattern_store.get_pattern_stats()
            patterns = []
            for d in stats['patterns_by_domain'].keys():
                patterns.extend(
                    self.pattern_store.get_patterns_by_domain(
                        domain=d,
                        min_confidence=0.0,
                        limit=100
                    )
                )
        
        # Filter by usage
        analyzed = [p for p in patterns if p.usage_count >= min_usage_count]
        
        if not analyzed:
            return {
                'total_patterns': 0,
                'average_confidence': 0.0,
                'success_rate': 0.0,
                'high_performers': [],
                'low_performers': []
            }
        
        # Calculate metrics
        total_success = sum(p.success_count for p in analyzed)
        total_usage = sum(p.usage_count for p in analyzed)
        
        success_rate = total_success / total_usage if total_usage > 0 else 0.0
        avg_confidence = sum(p.confidence for p in analyzed) / len(analyzed)
        
        # Identify high/low performers
        high_performers = [
            p for p in analyzed
            if p.confidence >= 0.8 and (p.success_count / p.usage_count) >= 0.8
        ]
        
        low_performers = [
            p for p in analyzed
            if p.confidence < 0.5 or (p.success_count / p.usage_count) < 0.5
        ]
        
        return {
            'total_patterns': len(analyzed),
            'average_confidence': avg_confidence,
            'success_rate': success_rate,
            'high_performers': len(high_performers),
            'low_performers': len(low_performers),
            'high_performer_patterns': high_performers[:5],  # Top 5
            'low_performer_patterns': low_performers[:5]  # Bottom 5
        }
    
    def continuous_learning(
        self,
        test_code: str,
        quality_metrics: QualityMetrics,
        func_info: Dict,
        pattern_store: Tier2PatternStore
    ) -> int:
        """
        Extract new patterns from high-quality test code.
        
        Args:
            test_code: Generated test code with high quality
            quality_metrics: Measured quality
            func_info: Function information
            pattern_store: Pattern storage
            
        Returns:
            Number of new patterns learned
        """
        # Only learn from high-quality tests
        if quality_metrics.overall_score < 0.8:
            return 0
        
        # Extract patterns from test code
        # (Would use PatternLearner here in production)
        # For now, return 0 - this is a placeholder for future enhancement
        return 0
