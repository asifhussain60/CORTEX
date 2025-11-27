"""
Pattern Recommender - Phase 5.3: Pattern Recommendations & Feedback

Recommends existing patterns from current project when writing new code.
Captures user feedback to improve recommendations over time.
Enables pattern export/import for backup and migration.

IMPORTANT: Each solution has its own CORTEX brain - no cross-project sharing.
This system recommends patterns from WITHIN the same project only.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict


class FeedbackAction(Enum):
    """User feedback actions"""
    ACCEPT = "accept"  # User accepted recommendation
    REJECT = "reject"  # User rejected recommendation
    MODIFY = "modify"  # User modified recommendation
    DEFER = "defer"  # User deferred decision


class RecommendationSource(Enum):
    """Source of recommendation"""
    CURRENT_PROJECT = "current_project"  # From current project patterns
    CORTEX_CORE = "cortex_core"  # From CORTEX framework patterns
    IMPORTED = "imported"  # From imported pattern backup


@dataclass
class PatternRecommendation:
    """Represents a pattern recommendation"""
    recommendation_id: str
    pattern_id: str
    pattern_title: str
    pattern_category: str
    confidence: float
    source: RecommendationSource
    relevance_score: float = 0.0  # How relevant to current context
    usage_count: int = 0  # Times pattern has been used
    success_rate: float = 0.0  # Pattern success rate
    description: str = ""
    code_sample: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class UserFeedback:
    """User feedback on a recommendation"""
    feedback_id: str
    recommendation_id: str
    pattern_id: str
    action: FeedbackAction
    comment: Optional[str] = None
    modified_code: Optional[str] = None  # If user modified the pattern
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class PatternRecommender:
    """
    Recommends patterns from current project when writing new code.
    
    ARCHITECTURE NOTE: Each solution has its own CORTEX brain.
    This recommender works WITHIN a single project only - no cross-project features.
    
    Responsibilities:
    1. Recommend existing patterns from current project
    2. Score relevance based on context
    3. Capture and learn from user feedback
    4. Export/import patterns for backup/migration
    """
    
    def __init__(self, tier2_kg: Any = None, pattern_store: Any = None, project_namespace: str = "workspace.default"):
        """
        Initialize pattern recommender.
        
        Args:
            tier2_kg: Tier 2 Knowledge Graph for pattern storage
            pattern_store: Pattern store API for CRUD operations
            project_namespace: Namespace for this project (e.g., "workspace.myapp")
        """
        self.tier2_kg = tier2_kg
        self.pattern_store = pattern_store
        self.project_namespace = project_namespace
        self.feedback_history: Dict[str, List[UserFeedback]] = defaultdict(list)
        
    def recommend_patterns(self,
                          context: Dict[str, Any],
                          limit: int = 10,
                          min_confidence: float = 0.5,
                          include_cortex_core: bool = True) -> List[PatternRecommendation]:
        """
        Generate pattern recommendations for current context.
        
        Args:
            context: Context information (file, category, tags, etc.)
            limit: Maximum number of recommendations
            min_confidence: Minimum confidence threshold
            include_cortex_core: Include CORTEX core patterns
            
        Returns:
            List of pattern recommendations sorted by relevance
        """
        recommendations = []
        
        # Get patterns from current project
        project_patterns = self._get_project_patterns(min_confidence)
        
        for pattern in project_patterns:
            rec = self._create_recommendation(
                pattern,
                RecommendationSource.CURRENT_PROJECT,
                context
            )
            recommendations.append(rec)
        
        # Get CORTEX core patterns if requested
        if include_cortex_core:
            core_patterns = self._get_cortex_core_patterns(min_confidence)
            
            for pattern in core_patterns:
                rec = self._create_recommendation(
                    pattern,
                    RecommendationSource.CORTEX_CORE,
                    context
                )
                recommendations.append(rec)
        
        # Score recommendations by relevance
        for rec in recommendations:
            rec.relevance_score = self._calculate_relevance_score(rec, context)
        
        # Sort by relevance and limit
        recommendations.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return recommendations[:limit]
    
    def _get_project_patterns(self, min_confidence: float) -> List[Dict[str, Any]]:
        """Get all patterns from current project namespace"""
        if not self.pattern_store:
            return []
        
        try:
            patterns = self.pattern_store.search_patterns(
                query='*',
                namespace=self.project_namespace,
                limit=1000
            )
            
            # Filter by confidence
            return [p for p in patterns if p.get('confidence', 0) >= min_confidence]
            
        except Exception as e:
            print(f"Error getting patterns from {self.project_namespace}: {e}")
            return []
    
    def _get_cortex_core_patterns(self, min_confidence: float) -> List[Dict[str, Any]]:
        """Get CORTEX core patterns"""
        if not self.pattern_store:
            return []
        
        try:
            patterns = self.pattern_store.search_patterns(
                query='*',
                namespace='cortex',
                limit=100
            )
            
            # Filter by confidence
            return [p for p in patterns if p.get('confidence', 0) >= min_confidence]
            
        except Exception as e:
            print(f"Error getting CORTEX core patterns: {e}")
            return []
    
    def _create_recommendation(self,
                              pattern: Dict[str, Any],
                              source: RecommendationSource,
                              context: Dict[str, Any]) -> PatternRecommendation:
        """Create recommendation from pattern"""
        pattern_id = pattern['id']
        
        # Parse metadata
        metadata = pattern.get('metadata', {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        return PatternRecommendation(
            recommendation_id=f"rec_{pattern_id}_{int(datetime.utcnow().timestamp())}",
            pattern_id=pattern_id,
            pattern_title=pattern.get('title', 'Untitled'),
            pattern_category=pattern.get('category', 'general'),
            confidence=pattern.get('confidence', 0.5),
            source=source,
            usage_count=pattern.get('usage_count', 0),
            success_rate=self._calculate_success_rate(pattern),
            description=pattern.get('description', ''),
            code_sample=metadata.get('code_sample'),
            tags=metadata.get('tags', [])
        )
    
    def _calculate_success_rate(self, pattern: Dict[str, Any]) -> float:
        """Calculate success rate for a pattern"""
        metadata = pattern.get('metadata', {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        successes = metadata.get('success_count', 0)
        failures = metadata.get('failure_count', 0)
        total = successes + failures
        
        if total == 0:
            return 0.5  # Default 50% for untested patterns
        
        return successes / total
    
    def _calculate_relevance_score(self,
                                   recommendation: PatternRecommendation,
                                   context: Dict[str, Any]) -> float:
        """
        Calculate relevance score for a recommendation.
        
        Factors:
        - Category match (40%)
        - Tag overlap (30%)
        - Confidence (15%)
        - Success rate (10%)
        - Feedback accept rate (5%)
        """
        score = 0.0
        
        # Category match (40%)
        context_category = context.get('category', '').lower()
        if context_category and context_category == recommendation.pattern_category.lower():
            score += 0.4
        elif context_category and context_category in recommendation.pattern_category.lower():
            score += 0.2
        
        # Tag overlap (30%)
        context_tags = set(t.lower() for t in context.get('tags', []))
        pattern_tags = set(t.lower() for t in recommendation.tags)
        
        if context_tags and pattern_tags:
            overlap = len(context_tags & pattern_tags)
            max_overlap = max(len(context_tags), len(pattern_tags))
            score += 0.3 * (overlap / max_overlap)
        
        # Confidence (15%)
        score += 0.15 * recommendation.confidence
        
        # Success rate (10%)
        score += 0.1 * recommendation.success_rate
        
        # Feedback accept rate (5%)
        feedback_rate = self._calculate_accept_rate(recommendation.pattern_id)
        score += 0.05 * feedback_rate
        
        # Boost for project patterns (user's own patterns are more relevant)
        if recommendation.source == RecommendationSource.CURRENT_PROJECT:
            score *= 1.2  # 20% boost
        
        return min(1.0, score)  # Cap at 1.0
    
    def _calculate_accept_rate(self, pattern_id: str) -> float:
        """Calculate feedback accept rate for a pattern"""
        feedbacks = self.feedback_history.get(pattern_id, [])
        
        if not feedbacks:
            return 0.5  # Default 50% for patterns without feedback
        
        accepts = sum(1 for f in feedbacks if f.action == FeedbackAction.ACCEPT)
        total = len(feedbacks)
        
        return accepts / total
    
    def record_feedback(self,
                       recommendation_id: str,
                       pattern_id: str,
                       action: FeedbackAction,
                       comment: Optional[str] = None,
                       modified_code: Optional[str] = None) -> UserFeedback:
        """
        Record user feedback on a recommendation.
        
        Args:
            recommendation_id: Recommendation ID
            pattern_id: Pattern ID
            action: User action (accept/reject/modify/defer)
            comment: Optional user comment
            modified_code: Modified code if action is MODIFY
            
        Returns:
            UserFeedback object
        """
        feedback_id = f"fb_{recommendation_id}_{datetime.utcnow().timestamp()}"
        
        feedback = UserFeedback(
            feedback_id=feedback_id,
            recommendation_id=recommendation_id,
            pattern_id=pattern_id,
            action=action,
            comment=comment,
            modified_code=modified_code
        )
        
        # Store feedback
        self.feedback_history[pattern_id].append(feedback)
        
        # Update pattern confidence based on feedback
        self._update_confidence_from_feedback(pattern_id, action)
        
        # If modified, create a new pattern variant
        if action == FeedbackAction.MODIFY and modified_code:
            self._create_pattern_variant(pattern_id, modified_code)
        
        return feedback
    
    def _update_confidence_from_feedback(self, pattern_id: str, action: FeedbackAction):
        """Update pattern confidence based on user feedback"""
        if not self.pattern_store:
            return
        
        try:
            pattern = self.pattern_store.get_pattern(pattern_id)
            if not pattern:
                return
            
            current_confidence = pattern.get('confidence', 0.5)
            
            # Adjust confidence based on action
            if action == FeedbackAction.ACCEPT:
                new_confidence = min(1.0, current_confidence + 0.05)
            elif action == FeedbackAction.REJECT:
                new_confidence = max(0.0, current_confidence - 0.1)
            elif action == FeedbackAction.MODIFY:
                # Modified patterns get slight boost (user found it useful but adapted it)
                new_confidence = min(1.0, current_confidence + 0.02)
            else:  # DEFER
                new_confidence = current_confidence  # No change
            
            # Update confidence
            self.pattern_store.update_pattern_confidence(pattern_id, new_confidence)
            
        except Exception as e:
            print(f"Error updating confidence for {pattern_id}: {e}")
    
    def _create_pattern_variant(self, original_pattern_id: str, modified_code: str):
        """Create a new pattern variant based on user modification"""
        if not self.pattern_store:
            return
        
        try:
            original = self.pattern_store.get_pattern(original_pattern_id)
            if not original:
                return
            
            # Create variant pattern
            variant_id = f"{original_pattern_id}_variant_{hash(modified_code) & 0xFFFF:04x}"
            
            variant_data = {
                'id': variant_id,
                'title': f"{original.get('title', 'Pattern')} (Modified)",
                'category': original.get('category', 'general'),
                'description': f"User-modified variant of {original_pattern_id}",
                'confidence': 0.6,  # Start with moderate confidence
                'metadata': json.dumps({
                    'code_sample': modified_code,
                    'original_pattern_id': original_pattern_id,
                    'created_at': datetime.utcnow().isoformat()
                })
            }
            
            self.pattern_store.store_pattern(
                pattern_id=variant_id,
                pattern_data=variant_data,
                namespace=self.project_namespace
            )
            
        except Exception as e:
            print(f"Error creating pattern variant: {e}")
    
    def get_feedback_summary(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get feedback summary for a pattern.
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            Dictionary with feedback statistics
        """
        feedbacks = self.feedback_history.get(pattern_id, [])
        
        if not feedbacks:
            return {
                'total_feedbacks': 0,
                'accept_rate': 0.0,
                'reject_rate': 0.0,
                'modify_rate': 0.0,
                'defer_rate': 0.0
            }
        
        total = len(feedbacks)
        accepts = sum(1 for f in feedbacks if f.action == FeedbackAction.ACCEPT)
        rejects = sum(1 for f in feedbacks if f.action == FeedbackAction.REJECT)
        modifies = sum(1 for f in feedbacks if f.action == FeedbackAction.MODIFY)
        defers = sum(1 for f in feedbacks if f.action == FeedbackAction.DEFER)
        
        return {
            'total_feedbacks': total,
            'accept_rate': accepts / total,
            'reject_rate': rejects / total,
            'modify_rate': modifies / total,
            'defer_rate': defers / total,
            'recent_feedbacks': [
                {
                    'action': f.action.value,
                    'comment': f.comment,
                    'timestamp': f.timestamp
                }
                for f in sorted(feedbacks, key=lambda x: x.timestamp, reverse=True)[:5]
            ]
        }
    
    def export_patterns(self, output_path: str, format: str = 'json') -> bool:
        """
        Export patterns from current project for backup or migration.
        
        Args:
            output_path: Output file path
            format: Export format ('json' or 'yaml')
            
        Returns:
            True if export succeeded
        """
        patterns = self._get_project_patterns(min_confidence=0.0)
        
        export_data = {
            'project_namespace': self.project_namespace,
            'exported_at': datetime.utcnow().isoformat(),
            'patterns': patterns,
            'feedback': {
                pattern['id']: self.get_feedback_summary(pattern['id'])
                for pattern in patterns
            }
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if format == 'json':
                    json.dump(export_data, f, indent=2)
                elif format == 'yaml':
                    import yaml
                    yaml.dump(export_data, f)
                else:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error exporting patterns: {e}")
            return False
    
    def import_patterns(self,
                       import_path: str,
                       merge_strategy: str = 'skip') -> Dict[str, int]:
        """
        Import patterns from backup file.
        
        Args:
            import_path: Path to import file
            merge_strategy: 'skip' (skip existing), 'overwrite', or 'merge'
            
        Returns:
            Dictionary with import statistics
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            patterns = import_data.get('patterns', [])
            imported = 0
            skipped = 0
            updated = 0
            
            for pattern in patterns:
                pattern_id = pattern['id']
                existing = self.pattern_store.get_pattern(pattern_id) if self.pattern_store else None
                
                if existing and merge_strategy == 'skip':
                    skipped += 1
                    continue
                
                if existing and merge_strategy == 'merge':
                    # Merge confidence scores (weighted average)
                    old_conf = existing.get('confidence', 0.5)
                    new_conf = pattern.get('confidence', 0.5)
                    pattern['confidence'] = (old_conf + new_conf) / 2
                    updated += 1
                else:
                    imported += 1
                
                # Store in current project namespace
                if self.pattern_store:
                    self.pattern_store.store_pattern(
                        pattern_id=pattern_id,
                        pattern_data=pattern,
                        namespace=self.project_namespace
                    )
            
            return {
                'imported': imported,
                'updated': updated,
                'skipped': skipped,
                'total': len(patterns)
            }
            
        except Exception as e:
            return {'error': str(e), 'imported': 0}


if __name__ == "__main__":
    # Example usage
    recommender = PatternRecommender(project_namespace="workspace.myapp")
    
    # Get recommendations
    context = {
        'category': 'authentication',
        'tags': ['security', 'jwt', 'api']
    }
    
    recommendations = recommender.recommend_patterns(
        context=context,
        limit=5
    )
    
    print(f"Found {len(recommendations)} recommendations")
    for rec in recommendations:
        print(f"  - {rec.pattern_title} (relevance: {rec.relevance_score:.2f})")
