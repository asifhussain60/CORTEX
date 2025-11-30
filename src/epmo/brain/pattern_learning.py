"""
Pattern Learning Engine - Adaptive Documentation Pattern Learning
Feature 5.2: Learning from Documentation Patterns and User Feedback

Analyzes successful documentation approaches, learns from user feedback, and suggests
improvements based on historical data and quality metrics.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from .brain_connector import BrainConnector, PatternRecord, QualityMetrics


@dataclass
class DocumentationPattern:
    """Learned documentation pattern"""
    pattern_id: str
    pattern_type: str  # 'template', 'content', 'structure', 'visual'
    success_rate: float
    context_tags: List[str]
    quality_score: float
    usage_frequency: int
    description: str
    example_config: Optional[Dict] = None
    created_at: Optional[str] = None
    last_successful: Optional[str] = None


@dataclass
class LearningInsight:
    """Learning insight from pattern analysis"""
    insight_type: str
    description: str
    confidence: float
    supporting_patterns: List[str]
    recommendation: str
    impact_score: float


class PatternLearningEngine:
    """
    Learns from documentation generation patterns and user feedback to improve
    future documentation generation through adaptive optimization.
    """
    
    def __init__(self, brain_connector: Optional[BrainConnector] = None):
        """
        Initialize pattern learning engine
        
        Args:
            brain_connector: Connection to CORTEX Brain (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain_connector
        
        # In-memory pattern cache for performance
        self._pattern_cache: Dict[str, DocumentationPattern] = {}
        self._insight_cache: Dict[str, LearningInsight] = {}
        self._cache_expires = datetime.now() + timedelta(hours=1)
        
        self.logger.info("PatternLearningEngine initialized")

    def analyze_successful_patterns(
        self, 
        min_success_rate: float = 0.75,
        min_usage_count: int = 3
    ) -> List[DocumentationPattern]:
        """
        Analyze patterns with high success rates to identify best practices
        
        Args:
            min_success_rate: Minimum success rate threshold
            min_usage_count: Minimum usage count for reliability
            
        Returns:
            List of successful documentation patterns
        """
        if not self.brain:
            self.logger.warning("No brain connector - using cached patterns only")
            return list(self._pattern_cache.values())
        
        try:
            # Get patterns from brain
            brain_patterns = self.brain.get_documentation_patterns(
                category='documentation',
                min_confidence=min_success_rate
            )
            
            successful_patterns = []
            
            for pattern in brain_patterns:
                if pattern.usage_count < min_usage_count:
                    continue
                    
                success_rate = self._calculate_success_rate(pattern)
                if success_rate >= min_success_rate:
                    doc_pattern = DocumentationPattern(
                        pattern_id=pattern.pattern_id,
                        pattern_type=self._classify_pattern_type(pattern),
                        success_rate=success_rate,
                        context_tags=pattern.tags,
                        quality_score=pattern.confidence,
                        usage_frequency=pattern.usage_count,
                        description=pattern.description,
                        created_at=pattern.created_at,
                        last_successful=pattern.last_used
                    )
                    successful_patterns.append(doc_pattern)
            
            # Cache patterns for performance
            for pattern in successful_patterns:
                self._pattern_cache[pattern.pattern_id] = pattern
            
            self.logger.info(f"Analyzed {len(successful_patterns)} successful patterns")
            return successful_patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {e}")
            return []

    def _calculate_success_rate(self, pattern: PatternRecord) -> float:
        """Calculate success rate from pattern metrics"""
        total_attempts = pattern.success_count + pattern.failure_count
        if total_attempts == 0:
            return pattern.confidence
        
        return pattern.success_count / total_attempts

    def _classify_pattern_type(self, pattern: PatternRecord) -> str:
        """Classify pattern into documentation type categories"""
        if 'template' in pattern.name.lower() or 'template' in pattern.tags:
            return 'template'
        elif 'visual' in pattern.tags or 'diagram' in pattern.tags:
            return 'visual'
        elif 'structure' in pattern.tags or 'organization' in pattern.tags:
            return 'structure'
        else:
            return 'content'

    def learn_from_feedback(
        self,
        generation_id: str,
        quality_metrics: QualityMetrics,
        generation_config: Dict[str, Any]
    ):
        """
        Learn from user feedback and quality metrics
        
        Args:
            generation_id: Unique ID for documentation generation
            quality_metrics: Quality scores and feedback
            generation_config: Configuration used for generation
        """
        try:
            # Record quality metrics in brain
            if self.brain:
                self.brain.record_documentation_quality(quality_metrics)
            
            # Extract learning insights
            insights = self._extract_insights_from_feedback(
                quality_metrics, 
                generation_config
            )
            
            # Update pattern scores based on feedback
            self._update_pattern_scores(generation_config, quality_metrics)
            
            self.logger.info(f"Processed feedback for generation {generation_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing feedback: {e}")

    def _extract_insights_from_feedback(
        self, 
        metrics: QualityMetrics,
        config: Dict[str, Any]
    ) -> List[LearningInsight]:
        """Extract actionable insights from quality feedback"""
        insights = []
        
        # Quality score insights
        if metrics.quality_score < 0.6:
            if metrics.readability_score < 0.6:
                insight = LearningInsight(
                    insight_type="readability",
                    description="Low readability detected - consider simpler templates",
                    confidence=0.8,
                    supporting_patterns=[],
                    recommendation="Use readability-optimized templates",
                    impact_score=0.7
                )
                insights.append(insight)
                
            if metrics.completeness_score < 0.6:
                insight = LearningInsight(
                    insight_type="completeness",
                    description="Incomplete documentation - enhance content generation",
                    confidence=0.85,
                    supporting_patterns=[],
                    recommendation="Include more comprehensive sections",
                    impact_score=0.8
                )
                insights.append(insight)
        
        return insights

    def _update_pattern_scores(
        self, 
        config: Dict[str, Any], 
        metrics: QualityMetrics
    ):
        """Update pattern confidence scores based on usage outcomes"""
        # This would update pattern scores in the brain database
        # For now, update local cache
        pattern_hash = self._config_to_pattern_hash(config)
        
        if pattern_hash in self._pattern_cache:
            pattern = self._pattern_cache[pattern_hash]
            
            # Adaptive scoring based on quality metrics
            quality_factor = (metrics.quality_score - 0.5) * 2  # Scale to -1 to 1
            pattern.quality_score += quality_factor * 0.1  # Small incremental updates
            pattern.quality_score = max(0.0, min(1.0, pattern.quality_score))
            
            pattern.usage_frequency += 1

    def _config_to_pattern_hash(self, config: Dict[str, Any]) -> str:
        """Create a hash ID from configuration for pattern tracking"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:12]

    def get_optimization_suggestions(
        self, 
        current_config: Dict[str, Any],
        project_context: Optional[Dict[str, Any]] = None
    ) -> List[LearningInsight]:
        """
        Get suggestions for optimizing documentation generation
        
        Args:
            current_config: Current generation configuration
            project_context: Project context for targeted suggestions
            
        Returns:
            List of optimization insights and recommendations
        """
        if datetime.now() > self._cache_expires:
            self._refresh_insights_cache()
        
        suggestions = []
        
        # Analyze current config against successful patterns
        successful_patterns = self.analyze_successful_patterns()
        
        for pattern in successful_patterns:
            if self._is_similar_context(current_config, pattern, project_context):
                suggestion = self._generate_suggestion(pattern, current_config)
                if suggestion:
                    suggestions.append(suggestion)
        
        # Add insights from feedback analysis
        suggestions.extend(self._insight_cache.values())
        
        # Sort by impact score
        suggestions.sort(key=lambda x: x.impact_score, reverse=True)
        
        return suggestions[:10]  # Top 10 suggestions

    def _is_similar_context(
        self, 
        config: Dict[str, Any], 
        pattern: DocumentationPattern,
        project_context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if pattern is applicable to current context"""
        if not project_context:
            return True
        
        # Check tag overlap
        config_tags = set(config.get('tags', []))
        pattern_tags = set(pattern.context_tags)
        
        overlap = len(config_tags & pattern_tags)
        return overlap >= 2  # At least 2 matching tags

    def _generate_suggestion(
        self, 
        pattern: DocumentationPattern,
        current_config: Dict[str, Any]
    ) -> Optional[LearningInsight]:
        """Generate optimization suggestion from successful pattern"""
        if pattern.success_rate <= 0.8:
            return None
            
        return LearningInsight(
            insight_type="optimization",
            description=f"Pattern '{pattern.description}' shows {pattern.success_rate:.1%} success rate",
            confidence=pattern.quality_score,
            supporting_patterns=[pattern.pattern_id],
            recommendation=f"Consider adopting {pattern.pattern_type} approach",
            impact_score=pattern.success_rate * pattern.quality_score
        )

    def _refresh_insights_cache(self):
        """Refresh cached insights from brain data"""
        self._insight_cache.clear()
        
        if not self.brain:
            return
            
        # Get recent corrections for learning
        corrections = self.brain.get_recent_corrections(days=30)
        
        for correction in corrections:
            if 'documentation' in correction.get('error_description', '').lower():
                insight = LearningInsight(
                    insight_type="correction",
                    description=f"Avoid: {correction.get('error_description', 'Unknown error')}",
                    confidence=0.9,
                    supporting_patterns=[],
                    recommendation=correction.get('correction_applied', 'See correction log'),
                    impact_score=0.8
                )
                self._insight_cache[correction['correction_id']] = insight
        
        self._cache_expires = datetime.now() + timedelta(hours=1)

    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get learning statistics and metrics"""
        patterns = self.analyze_successful_patterns()
        
        if not patterns:
            return {"total_patterns": 0, "message": "No patterns analyzed yet"}
        
        pattern_types = {}
        total_usage = 0
        avg_quality = 0
        
        for pattern in patterns:
            pattern_types[pattern.pattern_type] = pattern_types.get(pattern.pattern_type, 0) + 1
            total_usage += pattern.usage_frequency
            avg_quality += pattern.quality_score
        
        return {
            "total_patterns": len(patterns),
            "pattern_types": pattern_types,
            "total_usage": total_usage,
            "average_quality": avg_quality / len(patterns),
            "success_rate_range": {
                "min": min(p.success_rate for p in patterns),
                "max": max(p.success_rate for p in patterns),
                "avg": sum(p.success_rate for p in patterns) / len(patterns)
            },
            "cached_insights": len(self._insight_cache),
            "cache_expires": self._cache_expires.isoformat()
        }

    def export_learned_patterns(self, output_path: Path) -> bool:
        """
        Export learned patterns for backup or analysis
        
        Args:
            output_path: Path to save patterns JSON
            
        Returns:
            True if successful
        """
        try:
            patterns = self.analyze_successful_patterns()
            insights = list(self._insight_cache.values())
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "patterns": [asdict(p) for p in patterns],
                "insights": [asdict(i) for i in insights],
                "statistics": self.get_pattern_statistics()
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Patterns exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting patterns: {e}")
            return False