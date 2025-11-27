"""
Brain-Enhanced Configuration System - Intelligent Parameter Adaptation
Feature 5.4: Context-Aware Configuration Management

Intelligently adapts documentation generation parameters based on project context,
team preferences, historical patterns, and quality metrics from CORTEX Brain.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

from .brain_connector import BrainConnector
from .pattern_learning import PatternLearningEngine
from .adaptive_templates import AdaptiveTemplateSystem, TemplateRecommendation


@dataclass
class ConfigurationContext:
    """Context information for intelligent configuration"""
    project_size: str  # 'small', 'medium', 'large', 'enterprise'
    complexity_level: str  # 'simple', 'moderate', 'complex', 'advanced'
    team_size: int
    domain: str  # 'web', 'backend', 'data_science', 'enterprise', 'research'
    languages: List[str]
    frameworks: List[str]
    has_tests: bool
    test_coverage: float
    documentation_maturity: str  # 'none', 'basic', 'good', 'excellent'
    time_constraints: str  # 'tight', 'moderate', 'flexible'
    target_audience: str  # 'developers', 'stakeholders', 'mixed'


@dataclass
class IntelligentConfiguration:
    """AI-optimized configuration for documentation generation"""
    template_config: Dict[str, Any]
    generation_params: Dict[str, Any]
    quality_targets: Dict[str, float]
    optimization_flags: Dict[str, bool]
    contextual_adjustments: Dict[str, Any]
    confidence_score: float
    reasoning: str
    base_template: str  # Template name used for this configuration
    fallback_config: Optional[Dict[str, Any]] = None


@dataclass
class ConfigurationLearning:
    """Learning data from configuration usage"""
    config_id: str
    context_hash: str
    success_rate: float
    quality_achieved: float
    user_satisfaction: float
    usage_count: int
    last_used: str
    adjustments_made: List[str]


class BrainEnhancedConfig:
    """
    Intelligent configuration system that learns from CORTEX Brain patterns
    to optimize documentation generation parameters for specific contexts.
    """
    
    def __init__(
        self,
        brain_connector: Optional[BrainConnector] = None,
        pattern_engine: Optional[PatternLearningEngine] = None,
        template_system: Optional[AdaptiveTemplateSystem] = None
    ):
        """
        Initialize brain-enhanced configuration system
        
        Args:
            brain_connector: Connection to CORTEX Brain
            pattern_engine: Pattern learning engine
            template_system: Adaptive template system
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain_connector
        self.pattern_engine = pattern_engine or PatternLearningEngine(brain_connector)
        self.template_system = template_system or AdaptiveTemplateSystem(brain_connector, pattern_engine)
        
        # Configuration learning cache
        self._config_learning: Dict[str, ConfigurationLearning] = {}
        self._load_configuration_learning()
        
        # Base configuration templates
        self.base_configs = self._initialize_base_configs()
        
        self.logger.info("BrainEnhancedConfig initialized")

    def _initialize_base_configs(self) -> Dict[str, Dict]:
        """Initialize base configuration templates for different contexts"""
        return {
            'minimal_fast': {
                'sections': ['overview', 'usage'],
                'include_diagrams': False,
                'include_health': False,
                'detail_level': 'basic',
                'visual_content': False,
                'processing_speed': 'fast'
            },
            'balanced_standard': {
                'sections': ['overview', 'architecture', 'usage', 'health'],
                'include_diagrams': True,
                'include_health': True,
                'detail_level': 'standard',
                'visual_content': True,
                'processing_speed': 'moderate'
            },
            'comprehensive_quality': {
                'sections': ['overview', 'architecture', 'components', 'dependencies', 'usage', 'health', 'metrics'],
                'include_diagrams': True,
                'include_health': True,
                'detail_level': 'comprehensive',
                'visual_content': True,
                'processing_speed': 'thorough',
                'include_code_samples': True,
                'quality_focus': True
            },
            'stakeholder_presentation': {
                'sections': ['overview', 'architecture', 'benefits', 'metrics'],
                'include_diagrams': True,
                'include_health': True,
                'detail_level': 'executive',
                'visual_content': True,
                'visual_priority': True,
                'business_focus': True
            }
        }

    def generate_intelligent_config(
        self,
        context: ConfigurationContext,
        user_preferences: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> IntelligentConfiguration:
        """
        Generate intelligent configuration based on context and learned patterns
        
        Args:
            context: Project and team context
            user_preferences: User/team preferences
            constraints: Time, resource, or other constraints
            
        Returns:
            Optimized configuration with reasoning
        """
        try:
            # Analyze context and get base configuration
            context_analysis = self._analyze_context(context)
            base_config = self._select_base_config(context, constraints)
            
            # Get template recommendation from adaptive system
            template_recommendation = self._get_template_recommendation(context, user_preferences)
            
            # Apply learned optimizations
            learned_optimizations = self._apply_learned_optimizations(context, base_config)
            
            # Context-specific adjustments
            contextual_adjustments = self._generate_contextual_adjustments(
                context, context_analysis, constraints
            )
            
            # Quality targets based on context and patterns
            quality_targets = self._determine_quality_targets(context, template_recommendation)
            
            # Optimization flags for processing
            optimization_flags = self._determine_optimization_flags(context, constraints)
            
            # Combine all configurations
            final_config = self._merge_configurations(
                base_config,
                template_recommendation,
                learned_optimizations,
                contextual_adjustments,
                user_preferences
            )
            
            # Calculate confidence score
            confidence = self._calculate_configuration_confidence(
                context, template_recommendation, len(learned_optimizations)
            )
            
            # Generate reasoning explanation
            reasoning = self._generate_reasoning(
                context, template_recommendation, learned_optimizations, contextual_adjustments
            )
            
            # Create fallback configuration
            fallback_config = self._create_fallback_config(context)
            
            intelligent_config = IntelligentConfiguration(
                template_config=final_config,
                generation_params=self._extract_generation_params(final_config),
                quality_targets=quality_targets,
                optimization_flags=optimization_flags,
                contextual_adjustments=contextual_adjustments,
                confidence_score=confidence,
                reasoning=reasoning,
                base_template=template_recommendation.template_name,
                fallback_config=fallback_config
            )
            
            self.logger.info(f"Generated intelligent config with confidence: {confidence:.2f}")
            return intelligent_config
            
        except Exception as e:
            self.logger.error(f"Error generating intelligent config: {e}")
            return self._create_safe_fallback_config(context)

    def _analyze_context(self, context: ConfigurationContext) -> Dict[str, Any]:
        """Analyze context to understand requirements and constraints"""
        analysis = {}
        
        # Project complexity assessment
        complexity_score = 0
        if context.project_size in ['large', 'enterprise']:
            complexity_score += 0.3
        if context.complexity_level in ['complex', 'advanced']:
            complexity_score += 0.4
        if len(context.languages) > 3:
            complexity_score += 0.2
        if len(context.frameworks) > 2:
            complexity_score += 0.1
        
        analysis['complexity_score'] = min(complexity_score, 1.0)
        
        # Quality requirements assessment  
        quality_needs = 0.7  # Default
        if context.target_audience == 'stakeholders':
            quality_needs += 0.2
        if context.documentation_maturity in ['good', 'excellent']:
            quality_needs += 0.1
        if context.test_coverage > 0.8:
            quality_needs += 0.1
            
        analysis['quality_needs'] = min(quality_needs, 1.0)
        
        # Performance requirements
        if context.time_constraints == 'tight':
            analysis['speed_priority'] = True
            analysis['quality_trade_off'] = 0.8
        elif context.time_constraints == 'flexible':
            analysis['speed_priority'] = False  
            analysis['quality_trade_off'] = 1.0
        else:
            analysis['speed_priority'] = False
            analysis['quality_trade_off'] = 0.9
        
        # Content requirements
        analysis['needs_technical_depth'] = context.target_audience in ['developers', 'mixed']
        analysis['needs_visual_appeal'] = context.target_audience in ['stakeholders', 'mixed']
        analysis['needs_comprehensive_coverage'] = context.project_size in ['large', 'enterprise']
        
        return analysis

    def _select_base_config(
        self, 
        context: ConfigurationContext, 
        constraints: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select appropriate base configuration template"""
        
        # Time-constrained scenarios
        if context.time_constraints == 'tight':
            return self.base_configs['minimal_fast'].copy()
        
        # Stakeholder-focused scenarios  
        if context.target_audience == 'stakeholders':
            return self.base_configs['stakeholder_presentation'].copy()
        
        # High-quality scenarios
        if (context.documentation_maturity in ['good', 'excellent'] and 
            context.time_constraints != 'tight'):
            return self.base_configs['comprehensive_quality'].copy()
        
        # Default to balanced approach
        return self.base_configs['balanced_standard'].copy()

    def _get_template_recommendation(
        self, 
        context: ConfigurationContext,
        preferences: Optional[Dict[str, Any]]
    ) -> TemplateRecommendation:
        """Get template recommendation from adaptive template system"""
        project_context = {
            'file_count': self._estimate_file_count(context.project_size),
            'complexity_score': self._context_to_complexity_score(context),
            'languages': context.languages,
            'test_coverage': context.test_coverage,
            'domain': context.domain
        }
        
        return self.template_system.recommend_template(
            project_context, preferences
        )

    def _estimate_file_count(self, project_size: str) -> int:
        """Estimate file count from project size description"""
        size_mapping = {
            'small': 15,
            'medium': 50, 
            'large': 150,
            'enterprise': 500
        }
        return size_mapping.get(project_size, 50)

    def _context_to_complexity_score(self, context: ConfigurationContext) -> float:
        """Convert context to complexity score"""
        complexity_mapping = {
            'simple': 0.2,
            'moderate': 0.5,
            'complex': 0.7, 
            'advanced': 0.9
        }
        return complexity_mapping.get(context.complexity_level, 0.5)

    def _apply_learned_optimizations(
        self, 
        context: ConfigurationContext, 
        base_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply optimizations learned from previous successful configurations"""
        optimizations = {}
        
        # Get learning data for similar contexts
        similar_configs = self._find_similar_configs(context)
        
        if similar_configs:
            # Use highest-performing configuration's optimizations
            best_config = max(similar_configs, key=lambda c: c.success_rate * c.quality_achieved)
            
            if best_config.success_rate > 0.8:
                # Apply successful adjustments
                for adjustment in best_config.adjustments_made:
                    if adjustment.startswith('enable_'):
                        feature = adjustment[7:]  # Remove 'enable_'
                        optimizations[feature] = True
                    elif adjustment.startswith('disable_'):
                        feature = adjustment[8:]  # Remove 'disable_'
                        optimizations[feature] = False
                    elif adjustment.startswith('increase_'):
                        feature = adjustment[9:]  # Remove 'increase_'
                        current_val = base_config.get(feature, 0)
                        if isinstance(current_val, (int, float)):
                            optimizations[feature] = current_val * 1.2
                    elif adjustment.startswith('decrease_'):
                        feature = adjustment[9:]  # Remove 'decrease_'
                        current_val = base_config.get(feature, 1)
                        if isinstance(current_val, (int, float)):
                            optimizations[feature] = current_val * 0.8
        
        # Pattern-based optimizations
        if self.pattern_engine:
            suggestions = self.pattern_engine.get_optimization_suggestions(
                base_config, self._context_to_dict(context)
            )
            
            for suggestion in suggestions:
                if suggestion.impact_score > 0.7:
                    # High-impact suggestions get applied
                    if 'enable' in suggestion.recommendation.lower():
                        feature = suggestion.recommendation.split('enable ')[-1]
                        optimizations[feature] = True
        
        return optimizations

    def _find_similar_configs(self, context: ConfigurationContext) -> List[ConfigurationLearning]:
        """Find configuration learning data for similar contexts"""
        context_vector = self._context_to_vector(context)
        similar_configs = []
        
        for config in self._config_learning.values():
            stored_vector = self._hash_to_vector(config.context_hash)
            if stored_vector and self._vector_similarity(context_vector, stored_vector) > 0.7:
                similar_configs.append(config)
        
        return similar_configs

    def _context_to_vector(self, context: ConfigurationContext) -> List[float]:
        """Convert context to feature vector for similarity comparison"""
        vector = []
        
        # Project size encoding
        size_encoding = {'small': 0.2, 'medium': 0.5, 'large': 0.8, 'enterprise': 1.0}
        vector.append(size_encoding.get(context.project_size, 0.5))
        
        # Complexity encoding
        complexity_encoding = {'simple': 0.25, 'moderate': 0.5, 'complex': 0.75, 'advanced': 1.0}
        vector.append(complexity_encoding.get(context.complexity_level, 0.5))
        
        # Team size (normalized)
        vector.append(min(context.team_size / 20.0, 1.0))
        
        # Test coverage
        vector.append(context.test_coverage)
        
        # Binary features
        vector.append(1.0 if context.has_tests else 0.0)
        vector.append(1.0 if context.target_audience == 'stakeholders' else 0.0)
        vector.append(1.0 if context.time_constraints == 'tight' else 0.0)
        
        return vector

    def _hash_to_vector(self, context_hash: str) -> Optional[List[float]]:
        """Convert stored context hash back to vector (placeholder implementation)"""
        # In full implementation, this would decode the hash to the original vector
        # For now, return None to indicate unavailable
        return None

    def _vector_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between context vectors"""
        if len(v1) != len(v2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude_a = sum(a * a for a in v1) ** 0.5
        magnitude_b = sum(b * b for b in v2) ** 0.5
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)

    def _generate_contextual_adjustments(
        self,
        context: ConfigurationContext,
        analysis: Dict[str, Any],
        constraints: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate context-specific configuration adjustments"""
        adjustments = {}
        
        # Speed optimizations for time constraints
        if context.time_constraints == 'tight':
            adjustments['fast_mode'] = True
            adjustments['skip_heavy_analysis'] = True
            adjustments['concurrent_processing'] = True
        
        # Quality optimizations for stakeholders
        if context.target_audience == 'stakeholders':
            adjustments['enhanced_visuals'] = True
            adjustments['executive_summary'] = True
            adjustments['business_metrics'] = True
        
        # Complexity handling
        if analysis.get('complexity_score', 0) > 0.7:
            adjustments['detailed_architecture'] = True
            adjustments['dependency_analysis'] = True
            adjustments['component_breakdown'] = True
        
        # Team size adjustments
        if context.team_size > 10:
            adjustments['team_attribution'] = True
            adjustments['responsibility_mapping'] = True
        
        # Domain-specific adjustments
        if context.domain == 'web':
            adjustments['ui_component_focus'] = True
        elif context.domain == 'data_science':
            adjustments['data_flow_diagrams'] = True
        elif context.domain == 'enterprise':
            adjustments['enterprise_patterns'] = True
            adjustments['scalability_focus'] = True
        
        return adjustments

    def _determine_quality_targets(
        self,
        context: ConfigurationContext,
        template_rec: TemplateRecommendation
    ) -> Dict[str, float]:
        """Determine quality targets based on context and template recommendation"""
        base_targets = {
            'readability': 0.8,
            'completeness': 0.8,
            'accuracy': 0.85,
            'visual_quality': 0.75,
            'structure_quality': 0.8
        }
        
        # Adjust based on context
        if context.target_audience == 'stakeholders':
            base_targets['visual_quality'] = 0.9
            base_targets['readability'] = 0.9
        
        if context.documentation_maturity in ['good', 'excellent']:
            for metric in base_targets:
                base_targets[metric] = min(0.95, base_targets[metric] + 0.1)
        
        # Adjust based on template recommendation confidence
        confidence_boost = (template_rec.confidence - 0.5) * 0.2
        for metric in base_targets:
            base_targets[metric] = min(0.98, base_targets[metric] + confidence_boost)
        
        # Time constraint adjustments
        if context.time_constraints == 'tight':
            base_targets['completeness'] *= 0.9
            base_targets['visual_quality'] *= 0.85
        
        return base_targets

    def _determine_optimization_flags(
        self,
        context: ConfigurationContext,
        constraints: Optional[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Determine optimization flags for processing"""
        flags = {
            'parallel_processing': context.project_size in ['large', 'enterprise'],
            'caching_enabled': True,
            'incremental_updates': True,
            'quality_validation': context.documentation_maturity != 'none',
            'performance_monitoring': True,
            'adaptive_learning': True
        }
        
        # Constraint-based flags
        if constraints:
            if constraints.get('memory_limited'):
                flags['memory_optimization'] = True
                flags['streaming_mode'] = True
            if constraints.get('time_limited'):
                flags['fast_mode'] = True
                flags['skip_optional_analysis'] = True
        
        return flags

    def _merge_configurations(
        self,
        base_config: Dict[str, Any],
        template_rec: TemplateRecommendation,
        learned_opts: Dict[str, Any],
        contextual_adj: Dict[str, Any],
        preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge all configuration sources into final configuration"""
        final_config = base_config.copy()
        
        # Apply template customizations
        final_config.update(template_rec.customizations)
        
        # Apply learned optimizations
        final_config.update(learned_opts)
        
        # Apply contextual adjustments
        final_config.update(contextual_adj)
        
        # Apply user preferences (highest priority)
        if preferences:
            final_config.update(preferences)
        
        # Ensure configuration consistency
        final_config = self._validate_and_fix_config(final_config)
        
        return final_config

    def _validate_and_fix_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix configuration inconsistencies"""
        # Ensure required fields exist
        defaults = {
            'sections': ['overview', 'usage'],
            'include_diagrams': True,
            'include_health': True,
            'detail_level': 'standard'
        }
        
        for key, default_value in defaults.items():
            if key not in config:
                config[key] = default_value
        
        # Fix logical inconsistencies
        if config.get('fast_mode') and config.get('detail_level') == 'comprehensive':
            config['detail_level'] = 'standard'
        
        if not config.get('include_diagrams') and config.get('visual_priority'):
            config['include_diagrams'] = True
        
        return config

    def _calculate_configuration_confidence(
        self,
        context: ConfigurationContext,
        template_rec: TemplateRecommendation,
        learned_optimizations_count: int
    ) -> float:
        """Calculate confidence score for the generated configuration"""
        confidence = 0.0
        
        # Base confidence from template recommendation
        confidence += template_rec.confidence * 0.4
        
        # Boost from learned optimizations
        optimization_boost = min(learned_optimizations_count * 0.1, 0.3)
        confidence += optimization_boost
        
        # Context clarity bonus
        if context.time_constraints != 'moderate':  # Clear constraints
            confidence += 0.1
        if context.target_audience in ['developers', 'stakeholders']:  # Clear audience
            confidence += 0.1
        
        # Documentation maturity factor
        maturity_mapping = {'none': 0, 'basic': 0.05, 'good': 0.1, 'excellent': 0.15}
        confidence += maturity_mapping.get(context.documentation_maturity, 0)
        
        return min(confidence, 0.95)  # Cap at 95%

    def _generate_reasoning(
        self,
        context: ConfigurationContext,
        template_rec: TemplateRecommendation,
        learned_opts: Dict[str, Any],
        contextual_adj: Dict[str, Any]
    ) -> str:
        """Generate human-readable reasoning for configuration choices"""
        reasoning_parts = []
        
        # Template choice reasoning
        reasoning_parts.append(f"Selected {template_rec.template_name} template: {template_rec.reasoning}")
        
        # Context-based reasoning
        if context.time_constraints == 'tight':
            reasoning_parts.append("Optimized for speed due to tight time constraints")
        if context.target_audience == 'stakeholders':
            reasoning_parts.append("Enhanced visual quality for stakeholder presentation")
        if context.project_size in ['large', 'enterprise']:
            reasoning_parts.append("Comprehensive coverage for large project scale")
        
        # Learning-based reasoning
        if learned_opts:
            reasoning_parts.append(f"Applied {len(learned_opts)} learned optimizations from similar projects")
        
        # Contextual adjustments reasoning
        key_adjustments = [k for k in contextual_adj.keys() if not k.startswith('skip_')]
        if key_adjustments:
            reasoning_parts.append(f"Context-specific features: {', '.join(key_adjustments[:3])}")
        
        return ". ".join(reasoning_parts) + "."

    def _create_fallback_config(self, context: ConfigurationContext) -> Dict[str, Any]:
        """Create safe fallback configuration"""
        return {
            'sections': ['overview', 'usage'],
            'include_diagrams': False,
            'include_health': False,
            'detail_level': 'basic',
            'processing_mode': 'safe',
            'fallback_reason': 'Generated as safe fallback option'
        }

    def _create_safe_fallback_config(self, context: ConfigurationContext) -> IntelligentConfiguration:
        """Create safe fallback when generation fails"""
        fallback_config = self._create_fallback_config(context)
        
        return IntelligentConfiguration(
            template_config=fallback_config,
            generation_params={'mode': 'safe', 'timeout': 300},
            quality_targets={'readability': 0.7, 'completeness': 0.6, 'accuracy': 0.8},
            optimization_flags={'safe_mode': True},
            contextual_adjustments={},
            confidence_score=0.5,
            reasoning="Safe fallback configuration due to error in intelligent generation",
            base_template="minimal_fast"
        )

    def _extract_generation_params(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract generation parameters from configuration"""
        return {
            'timeout': 600 if config.get('detail_level') == 'comprehensive' else 300,
            'parallel_processing': config.get('parallel_processing', True),
            'caching': config.get('caching_enabled', True),
            'quality_validation': config.get('quality_validation', True),
            'fast_mode': config.get('fast_mode', False)
        }

    def _context_to_dict(self, context: ConfigurationContext) -> Dict[str, Any]:
        """Convert context to dictionary for compatibility"""
        return asdict(context)

    def _load_configuration_learning(self):
        """Load configuration learning data from brain or cache"""
        # In full implementation, this would load from brain database
        # For now, initialize empty
        self._config_learning = {}

    def record_configuration_outcome(
        self,
        config_id: str,
        context: ConfigurationContext,
        success: bool,
        quality_scores: Dict[str, float],
        user_satisfaction: float,
        adjustments_made: Optional[List[str]] = None
    ):
        """
        Record outcome of configuration usage for learning
        
        Args:
            config_id: Unique configuration identifier
            context: Context where configuration was used
            success: Whether generation was successful
            quality_scores: Quality metrics achieved
            user_satisfaction: User satisfaction rating (0-1)
            adjustments_made: List of adjustments made during usage
        """
        try:
            context_hash = str(hash(json.dumps(asdict(context), sort_keys=True)))
            
            if config_id in self._config_learning:
                # Update existing learning data
                learning = self._config_learning[config_id]
                learning.usage_count += 1
                
                # Update success rate (exponential moving average)
                current_success = 1.0 if success else 0.0
                learning.success_rate = learning.success_rate * 0.8 + current_success * 0.2
                
                # Update quality (average of quality scores)
                avg_quality = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0.7
                learning.quality_achieved = learning.quality_achieved * 0.8 + avg_quality * 0.2
                
                # Update satisfaction
                learning.user_satisfaction = learning.user_satisfaction * 0.8 + user_satisfaction * 0.2
                
                # Add new adjustments
                if adjustments_made:
                    learning.adjustments_made.extend(adjustments_made)
                    # Keep only unique adjustments
                    learning.adjustments_made = list(set(learning.adjustments_made))
                
                learning.last_used = datetime.now().isoformat()
                
            else:
                # Create new learning entry
                avg_quality = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0.7
                
                learning = ConfigurationLearning(
                    config_id=config_id,
                    context_hash=context_hash,
                    success_rate=1.0 if success else 0.0,
                    quality_achieved=avg_quality,
                    user_satisfaction=user_satisfaction,
                    usage_count=1,
                    last_used=datetime.now().isoformat(),
                    adjustments_made=adjustments_made or []
                )
                
                self._config_learning[config_id] = learning
            
            self.logger.info(f"Recorded configuration outcome: {config_id}")
            
        except Exception as e:
            self.logger.error(f"Error recording configuration outcome: {e}")

    def get_configuration_analytics(self) -> Dict[str, Any]:
        """Get analytics on configuration performance and learning"""
        if not self._config_learning:
            return {"message": "No configuration learning data available"}
        
        total_usage = sum(c.usage_count for c in self._config_learning.values())
        avg_success_rate = sum(c.success_rate for c in self._config_learning.values()) / len(self._config_learning)
        avg_quality = sum(c.quality_achieved for c in self._config_learning.values()) / len(self._config_learning)
        avg_satisfaction = sum(c.user_satisfaction for c in self._config_learning.values()) / len(self._config_learning)
        
        # Find best performing configuration
        best_config = max(
            self._config_learning.values(),
            key=lambda c: c.success_rate * c.quality_achieved * c.user_satisfaction
        )
        
        return {
            "total_configurations": len(self._config_learning),
            "total_usage": total_usage,
            "average_success_rate": avg_success_rate,
            "average_quality": avg_quality,
            "average_satisfaction": avg_satisfaction,
            "best_performing": {
                "config_id": best_config.config_id,
                "success_rate": best_config.success_rate,
                "quality_achieved": best_config.quality_achieved,
                "user_satisfaction": best_config.user_satisfaction,
                "usage_count": best_config.usage_count
            },
            "common_adjustments": self._analyze_common_adjustments()
        }

    def _analyze_common_adjustments(self) -> List[Tuple[str, int]]:
        """Analyze most common adjustments made to configurations"""
        adjustment_counts = {}
        
        for learning in self._config_learning.values():
            for adjustment in learning.adjustments_made:
                adjustment_counts[adjustment] = adjustment_counts.get(adjustment, 0) + 1
        
        # Sort by frequency
        return sorted(adjustment_counts.items(), key=lambda x: x[1], reverse=True)[:10]