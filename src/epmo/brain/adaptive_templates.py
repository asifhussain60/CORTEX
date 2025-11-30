"""
Adaptive Template System - Intelligent Template Selection and Optimization
Feature 5.3: Brain-Enhanced Template Management

Uses CORTEX Brain patterns to intelligently select and optimize documentation templates
based on project context, team preferences, and historical success patterns.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

from .brain_connector import BrainConnector
from .pattern_learning import PatternLearningEngine, DocumentationPattern


@dataclass
class TemplateRecommendation:
    """Template recommendation with confidence scoring"""
    template_name: str
    confidence: float
    reasoning: str
    success_rate: float
    usage_count: int
    context_match: float
    customizations: Dict[str, Any]
    pattern_id: Optional[str] = None


@dataclass 
class AdaptiveConfiguration:
    """Adaptive configuration for template generation"""
    base_template: str
    optimizations: Dict[str, Any]
    context_adjustments: Dict[str, Any] 
    quality_targets: Dict[str, float]
    learning_weight: float = 0.3  # How much to weight learning vs defaults


class AdaptiveTemplateSystem:
    """
    Intelligent template system that learns from usage patterns and adapts
    template selection and configuration based on CORTEX Brain knowledge.
    """
    
    def __init__(
        self, 
        brain_connector: Optional[BrainConnector] = None,
        pattern_engine: Optional[PatternLearningEngine] = None
    ):
        """
        Initialize adaptive template system
        
        Args:
            brain_connector: Connection to CORTEX Brain
            pattern_engine: Pattern learning engine for insights
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain_connector
        self.pattern_engine = pattern_engine or PatternLearningEngine(brain_connector)
        
        # Default template configurations
        self.default_templates = {
            'minimal': {
                'sections': ['overview', 'usage'],
                'include_diagrams': False,
                'include_health': False,
                'detail_level': 'basic'
            },
            'standard': {
                'sections': ['overview', 'architecture', 'usage', 'health'],
                'include_diagrams': True,
                'include_health': True, 
                'detail_level': 'comprehensive'
            },
            'comprehensive': {
                'sections': ['overview', 'architecture', 'components', 'dependencies', 'usage', 'health', 'metrics'],
                'include_diagrams': True,
                'include_health': True,
                'detail_level': 'detailed',
                'include_code_samples': True
            },
            'visual_focus': {
                'sections': ['overview', 'architecture', 'components'],
                'include_diagrams': True,
                'include_health': True,
                'detail_level': 'comprehensive',
                'visual_priority': True,
                'diagram_types': ['architecture', 'dependency', 'class']
            }
        }
        
        # Template performance cache
        self._template_performance: Dict[str, Dict] = {}
        self._load_template_performance()
        
        self.logger.info("AdaptiveTemplateSystem initialized")

    def recommend_template(
        self,
        project_context: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None,
        quality_requirements: Optional[Dict[str, float]] = None
    ) -> TemplateRecommendation:
        """
        Recommend optimal template based on context and learned patterns
        
        Args:
            project_context: Project characteristics and context
            user_preferences: User/team preferences
            quality_requirements: Required quality thresholds
            
        Returns:
            Template recommendation with reasoning
        """
        try:
            # Get successful patterns for context
            context_tags = self._extract_context_tags(project_context)
            successful_patterns = self.pattern_engine.analyze_successful_patterns()
            
            # Score all templates against context and patterns  
            template_scores = {}
            
            for template_name, template_config in self.default_templates.items():
                score = self._score_template_for_context(
                    template_name, 
                    template_config,
                    project_context,
                    successful_patterns,
                    user_preferences
                )
                template_scores[template_name] = score
            
            # Select best template
            best_template = max(template_scores, key=lambda t: template_scores[t]['total_score'])
            best_score = template_scores[best_template]
            
            # Generate customizations based on patterns
            customizations = self._generate_customizations(
                best_template,
                project_context,
                successful_patterns
            )
            
            recommendation = TemplateRecommendation(
                template_name=best_template,
                confidence=best_score['total_score'],
                reasoning=best_score['reasoning'],
                success_rate=best_score['success_rate'],
                usage_count=best_score['usage_count'],
                context_match=best_score['context_match'],
                customizations=customizations,
                pattern_id=best_score.get('pattern_id')
            )
            
            self.logger.info(f"Recommended template: {best_template} (confidence: {recommendation.confidence:.2f})")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error recommending template: {e}")
            # Fallback to standard template
            return TemplateRecommendation(
                template_name='standard',
                confidence=0.5,
                reasoning="Fallback recommendation due to error",
                success_rate=0.8,
                usage_count=0,
                context_match=0.5,
                customizations={}
            )

    def _extract_context_tags(self, context: Dict[str, Any]) -> List[str]:
        """Extract relevant tags from project context"""
        tags = []
        
        # Project size
        file_count = context.get('file_count', 0)
        if file_count > 100:
            tags.append('large_project')
        elif file_count > 20:
            tags.append('medium_project') 
        else:
            tags.append('small_project')
        
        # Technology stack
        languages = context.get('languages', [])
        tags.extend(languages)
        
        # Project type
        if any(lang in ['html', 'css', 'javascript'] for lang in languages):
            tags.append('web_project')
        if 'python' in languages:
            tags.append('python_project')
        if any(lang in ['java', 'c#', 'c++'] for lang in languages):
            tags.append('enterprise_project')
        
        # Complexity indicators
        complexity = context.get('complexity_score', 0.5)
        if complexity > 0.7:
            tags.append('high_complexity')
        elif complexity > 0.4:
            tags.append('medium_complexity')
        else:
            tags.append('low_complexity')
        
        return tags

    def _score_template_for_context(
        self,
        template_name: str,
        template_config: Dict[str, Any],
        context: Dict[str, Any],
        patterns: List[DocumentationPattern],
        preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Score template suitability for given context"""
        
        # Base scores
        context_match = self._calculate_context_match(template_config, context)
        pattern_support = self._calculate_pattern_support(template_name, patterns)
        preference_alignment = self._calculate_preference_alignment(template_config, preferences)
        
        # Historical performance
        performance = self._template_performance.get(template_name, {})
        success_rate = performance.get('success_rate', 0.8)
        usage_count = performance.get('usage_count', 0)
        
        # Combined scoring with weights
        total_score = (
            context_match * 0.4 +
            pattern_support * 0.3 +
            preference_alignment * 0.2 + 
            success_rate * 0.1
        )
        
        # Boost for frequently successful templates
        if usage_count > 5 and success_rate > 0.8:
            total_score += 0.1
        
        # Reasoning explanation
        reasoning_parts = []
        if context_match > 0.7:
            reasoning_parts.append("strong context match")
        if pattern_support > 0.6:
            reasoning_parts.append("supported by successful patterns")
        if preference_alignment > 0.8:
            reasoning_parts.append("aligns with preferences")
        if success_rate > 0.8:
            reasoning_parts.append("proven track record")
        
        reasoning = f"Recommended because: {', '.join(reasoning_parts) or 'balanced choice'}"
        
        return {
            'total_score': total_score,
            'context_match': context_match,
            'pattern_support': pattern_support,
            'preference_alignment': preference_alignment,
            'success_rate': success_rate,
            'usage_count': usage_count,
            'reasoning': reasoning
        }

    def _calculate_context_match(self, template_config: Dict, context: Dict) -> float:
        """Calculate how well template matches project context"""
        score = 0.0
        
        # Project size matching
        file_count = context.get('file_count', 0)
        detail_level = template_config.get('detail_level', 'basic')
        
        if file_count > 50 and detail_level in ['comprehensive', 'detailed']:
            score += 0.3
        elif file_count <= 50 and detail_level in ['basic', 'standard']:
            score += 0.3
        
        # Complexity matching
        complexity = context.get('complexity_score', 0.5)
        include_diagrams = template_config.get('include_diagrams', False)
        
        if complexity > 0.6 and include_diagrams:
            score += 0.3
        elif complexity <= 0.4 and not include_diagrams:
            score += 0.2
        
        # Health monitoring matching
        has_tests = context.get('test_coverage', 0) > 0
        include_health = template_config.get('include_health', False)
        
        if has_tests and include_health:
            score += 0.2
        elif not has_tests and not include_health:
            score += 0.1
        
        # Visual focus matching
        has_ui = any(lang in ['javascript', 'typescript', 'html', 'css'] 
                    for lang in context.get('languages', []))
        visual_priority = template_config.get('visual_priority', False)
        
        if has_ui and visual_priority:
            score += 0.2
        
        return min(score, 1.0)

    def _calculate_pattern_support(self, template_name: str, patterns: List[DocumentationPattern]) -> float:
        """Calculate pattern support for template"""
        if not patterns:
            return 0.5  # Neutral when no patterns available
        
        template_patterns = [p for p in patterns if template_name in p.context_tags or 
                           template_name in p.description.lower()]
        
        if not template_patterns:
            return 0.4  # Slightly lower for unproven templates
        
        # Average success rate of supporting patterns
        avg_success = sum(p.success_rate for p in template_patterns) / len(template_patterns)
        
        # Weight by pattern confidence
        weighted_score = sum(p.success_rate * p.quality_score for p in template_patterns)
        weighted_score /= sum(p.quality_score for p in template_patterns)
        
        return (avg_success + weighted_score) / 2

    def _calculate_preference_alignment(self, template_config: Dict, preferences: Optional[Dict]) -> float:
        """Calculate alignment with user preferences"""
        if not preferences:
            return 0.5  # Neutral when no preferences specified
        
        score = 0.0
        total_checks = 0
        
        # Check preference alignment
        pref_mappings = {
            'include_diagrams': 'diagrams',
            'include_health': 'health_metrics', 
            'detail_level': 'detail_level',
            'include_code_samples': 'code_examples'
        }
        
        for config_key, pref_key in pref_mappings.items():
            if pref_key in preferences and config_key in template_config:
                total_checks += 1
                if preferences[pref_key] == template_config[config_key]:
                    score += 1
                elif pref_key == 'detail_level':
                    # Partial score for detail level proximity
                    detail_order = ['basic', 'standard', 'comprehensive', 'detailed']
                    pref_idx = detail_order.index(preferences[pref_key]) if preferences[pref_key] in detail_order else 1
                    config_idx = detail_order.index(template_config[config_key]) if template_config[config_key] in detail_order else 1
                    distance = abs(pref_idx - config_idx)
                    score += max(0, 1 - distance * 0.3)
        
        return score / total_checks if total_checks > 0 else 0.5

    def _generate_customizations(
        self,
        template_name: str,
        context: Dict[str, Any],
        patterns: List[DocumentationPattern]
    ) -> Dict[str, Any]:
        """Generate template customizations based on context and patterns"""
        customizations = {}
        
        # Context-based customizations
        complexity = context.get('complexity_score', 0.5)
        file_count = context.get('file_count', 0)
        
        # Adjust section inclusion based on project size
        if file_count > 100:
            customizations['additional_sections'] = ['performance', 'scaling']
        elif file_count < 10:
            customizations['simplified_sections'] = True
        
        # Complexity-based adjustments
        if complexity > 0.8:
            customizations['enhanced_diagrams'] = True
            customizations['detailed_architecture'] = True
        
        # Pattern-based customizations
        relevant_patterns = [p for p in patterns if 
                           any(tag in context.get('languages', []) for tag in p.context_tags)]
        
        if relevant_patterns:
            # Use most successful pattern's example config
            best_pattern = max(relevant_patterns, key=lambda p: p.success_rate)
            if best_pattern.example_config:
                customizations.update(best_pattern.example_config)
        
        # Language-specific customizations
        languages = context.get('languages', [])
        if 'python' in languages:
            customizations['code_style'] = 'python'
        if any(lang in ['html', 'css', 'javascript'] for lang in languages):
            customizations['include_ui_components'] = True
        
        return customizations

    def create_adaptive_configuration(
        self, 
        recommendation: TemplateRecommendation,
        context: Dict[str, Any]
    ) -> AdaptiveConfiguration:
        """
        Create adaptive configuration from template recommendation
        
        Args:
            recommendation: Template recommendation
            context: Project context
            
        Returns:
            Adaptive configuration for documentation generation
        """
        base_config = self.default_templates[recommendation.template_name].copy()
        
        # Apply customizations
        optimizations = recommendation.customizations.copy()
        
        # Context adjustments based on learning
        context_adjustments = {}
        if recommendation.confidence > 0.8:
            context_adjustments['confidence_boost'] = True
        if recommendation.success_rate > 0.9:
            context_adjustments['proven_approach'] = True
        
        # Quality targets based on pattern success
        quality_targets = {
            'readability': 0.8,
            'completeness': 0.85,
            'accuracy': 0.9
        }
        
        # Adjust targets based on recommendation strength
        if recommendation.confidence > 0.8:
            for metric in quality_targets:
                quality_targets[metric] = min(0.95, quality_targets[metric] + 0.05)
        
        return AdaptiveConfiguration(
            base_template=recommendation.template_name,
            optimizations=optimizations,
            context_adjustments=context_adjustments,
            quality_targets=quality_targets,
            learning_weight=min(0.5, recommendation.confidence)
        )

    def _load_template_performance(self):
        """Load template performance data from brain or cache"""
        if self.brain:
            # Load from brain knowledge graph
            knowledge = self.brain.load_knowledge_graph()
            template_data = knowledge.get('template_performance', {})
            
            for template_name, performance in template_data.items():
                self._template_performance[template_name] = performance
        
        # Default performance for templates without data
        for template_name in self.default_templates:
            if template_name not in self._template_performance:
                self._template_performance[template_name] = {
                    'success_rate': 0.8,
                    'usage_count': 0,
                    'avg_quality': 0.75
                }

    def update_template_performance(
        self,
        template_name: str, 
        success: bool,
        quality_score: float
    ):
        """
        Update template performance metrics based on usage outcome
        
        Args:
            template_name: Name of template used
            success: Whether generation was successful
            quality_score: Quality score achieved
        """
        if template_name not in self._template_performance:
            self._template_performance[template_name] = {
                'success_rate': 0.8,
                'usage_count': 0,
                'avg_quality': 0.75,
                'total_successes': 0
            }
        
        perf = self._template_performance[template_name]
        
        # Update usage count
        perf['usage_count'] += 1
        
        # Update success tracking
        if success:
            perf['total_successes'] = perf.get('total_successes', 0) + 1
        
        # Recalculate success rate
        perf['success_rate'] = perf['total_successes'] / perf['usage_count']
        
        # Update average quality (exponential moving average)
        current_avg = perf['avg_quality']
        perf['avg_quality'] = current_avg * 0.8 + quality_score * 0.2
        
        self.logger.debug(f"Updated {template_name} performance: {perf}")

    def get_template_analytics(self) -> Dict[str, Any]:
        """Get analytics on template performance and usage"""
        total_usage = sum(perf['usage_count'] for perf in self._template_performance.values())
        
        if total_usage == 0:
            return {"message": "No template usage data available"}
        
        # Calculate analytics
        best_template = max(
            self._template_performance.items(),
            key=lambda x: x[1]['success_rate'] * x[1]['avg_quality']
        )
        
        most_used = max(
            self._template_performance.items(),
            key=lambda x: x[1]['usage_count']
        )
        
        return {
            "total_usage": total_usage,
            "best_performing": {
                "name": best_template[0],
                "success_rate": best_template[1]['success_rate'],
                "avg_quality": best_template[1]['avg_quality']
            },
            "most_used": {
                "name": most_used[0],
                "usage_count": most_used[1]['usage_count']
            },
            "template_performance": self._template_performance,
            "available_templates": list(self.default_templates.keys())
        }