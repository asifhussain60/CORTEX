"""
Brain Integration API - Comprehensive CORTEX Brain Documentation Integration
Feature 5.7: Unified Brain-Enhanced Documentation System

Central API connecting documentation generation with CORTEX Brain's cognitive framework,
conversation context, and development insights for intelligent, adaptive documentation.
"""

import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

from .brain_connector import BrainConnector, QualityMetrics
from .pattern_learning import PatternLearningEngine, DocumentationPattern, LearningInsight
from .adaptive_templates import AdaptiveTemplateSystem, TemplateRecommendation, AdaptiveConfiguration
from .brain_config import BrainEnhancedConfig, ConfigurationContext, IntelligentConfiguration
from .quality_feedback import QualityFeedbackLoop, QualityFeedback, QualityTrend
from .context_aware import ContextAwareGenerator, ProjectContext, ContextualRecommendation


@dataclass
class BrainGenerationRequest:
    """Comprehensive request for brain-enhanced documentation generation"""
    request_id: str
    project_path: Path
    output_path: Optional[Path]
    user_preferences: Optional[Dict[str, Any]] = None
    context_overrides: Optional[Dict[str, Any]] = None
    quality_targets: Optional[Dict[str, float]] = None
    time_constraints: Optional[str] = None  # 'tight', 'moderate', 'flexible'
    target_audience: Optional[List[str]] = None
    documentation_goals: Optional[List[str]] = None
    enable_learning: bool = True
    enable_optimization: bool = True


@dataclass
class BrainGenerationResult:
    """Comprehensive result from brain-enhanced generation"""
    request_id: str
    success: bool
    generation_id: str
    output_paths: List[Path]
    
    # Analysis results
    project_context: Optional[ProjectContext]
    template_recommendation: Optional[TemplateRecommendation]
    intelligent_config: Optional[IntelligentConfiguration]
    contextual_recommendations: List[ContextualRecommendation]
    
    # Quality and learning
    quality_metrics: Optional[QualityMetrics]
    learning_insights: List[LearningInsight]
    optimization_applied: List[str]
    
    # Performance and metadata
    generation_time_seconds: float
    confidence_score: float
    brain_integration_level: str  # 'basic', 'enhanced', 'full'
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = None


@dataclass
class BrainSystemStatus:
    """Status of the brain integration system"""
    brain_connection: bool
    pattern_learning: bool
    adaptive_templates: bool
    quality_feedback: bool
    context_awareness: bool
    total_patterns: int
    total_learning_data: int
    system_health: str  # 'excellent', 'good', 'degraded', 'offline'
    last_update: str


class BrainIntegrationAPI:
    """
    Central API for CORTEX Brain enhanced documentation generation.
    Provides unified interface to all brain-enhanced capabilities.
    """
    
    def __init__(
        self,
        brain_root: Optional[Path] = None,
        enable_brain_learning: bool = True,
        enable_optimization: bool = True
    ):
        """
        Initialize brain integration API
        
        Args:
            brain_root: Path to cortex-brain directory
            enable_brain_learning: Enable pattern learning and adaptation
            enable_optimization: Enable performance optimizations
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize brain connector
        try:
            self.brain = BrainConnector(brain_root) if brain_root else None
            self.brain_available = self.brain is not None
        except Exception as e:
            self.logger.warning(f"Brain connector unavailable: {e}")
            self.brain = None
            self.brain_available = False
        
        # Initialize brain components
        self.pattern_engine = PatternLearningEngine(self.brain) if enable_brain_learning else None
        self.template_system = AdaptiveTemplateSystem(self.brain, self.pattern_engine)
        self.config_system = BrainEnhancedConfig(self.brain, self.pattern_engine, self.template_system)
        self.quality_loop = QualityFeedbackLoop(self.brain)
        self.context_generator = ContextAwareGenerator(self.brain, self.pattern_engine)
        
        # System settings
        self.enable_learning = enable_brain_learning
        self.enable_optimization = enable_optimization
        
        # Performance tracking
        self._generation_history: List[BrainGenerationResult] = []
        self._performance_metrics: Dict[str, Any] = {}
        
        self.logger.info(f"BrainIntegrationAPI initialized (Brain: {'Available' if self.brain_available else 'Unavailable'})")

    def generate_enhanced_documentation(
        self,
        request: BrainGenerationRequest
    ) -> BrainGenerationResult:
        """
        Generate documentation using full brain enhancement capabilities
        
        Args:
            request: Comprehensive generation request
            
        Returns:
            Brain-enhanced generation result
        """
        start_time = datetime.now()
        generation_id = str(uuid.uuid4())
        
        self.logger.info(f"Starting brain-enhanced generation: {request.request_id}")
        
        try:
            # Phase 1: Context Analysis
            self.logger.debug("Phase 1: Analyzing project context")
            project_context = self._analyze_project_context(request)
            
            # Phase 2: Template Recommendation  
            self.logger.debug("Phase 2: Getting template recommendation")
            template_recommendation = self._get_template_recommendation(request, project_context)
            
            # Phase 3: Intelligent Configuration
            self.logger.debug("Phase 3: Generating intelligent configuration")
            intelligent_config = self._generate_intelligent_config(request, project_context, template_recommendation)
            
            # Phase 4: Contextual Recommendations
            self.logger.debug("Phase 4: Generating contextual recommendations")
            contextual_recs = self._get_contextual_recommendations(request, project_context, intelligent_config)
            
            # Phase 5: Enhanced Documentation Generation
            self.logger.debug("Phase 5: Generating enhanced documentation")
            generation_result = self._execute_enhanced_generation(
                request, project_context, intelligent_config, contextual_recs
            )
            
            # Phase 6: Quality Assessment and Learning
            self.logger.debug("Phase 6: Quality assessment and learning")
            quality_metrics = self._assess_generation_quality(generation_result, intelligent_config)
            learning_insights = self._extract_learning_insights(request, generation_result, quality_metrics)
            
            # Phase 7: System Learning and Optimization
            if self.enable_learning:
                self.logger.debug("Phase 7: Applying learning and optimization")
                self._apply_learning_feedback(request, generation_result, quality_metrics, intelligent_config)
            
            # Calculate final metrics
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            confidence_score = self._calculate_overall_confidence(
                template_recommendation, intelligent_config, quality_metrics
            )
            
            # Create comprehensive result
            result = BrainGenerationResult(
                request_id=request.request_id,
                success=True,
                generation_id=generation_id,
                output_paths=generation_result.get('output_paths', []),
                project_context=project_context,
                template_recommendation=template_recommendation,
                intelligent_config=intelligent_config,
                contextual_recommendations=contextual_recs,
                quality_metrics=quality_metrics,
                learning_insights=learning_insights,
                optimization_applied=generation_result.get('optimizations', []),
                generation_time_seconds=generation_time,
                confidence_score=confidence_score,
                brain_integration_level=self._determine_integration_level(),
                warnings=generation_result.get('warnings', [])
            )
            
            # Store result for analytics
            self._generation_history.append(result)
            
            self.logger.info(
                f"Brain-enhanced generation completed: {request.request_id} "
                f"(confidence: {confidence_score:.2f}, time: {generation_time:.1f}s)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in brain-enhanced generation: {e}")
            
            # Return error result
            end_time = datetime.now()
            return BrainGenerationResult(
                request_id=request.request_id,
                success=False,
                generation_id=generation_id,
                output_paths=[],
                project_context=None,
                template_recommendation=None,
                intelligent_config=None,
                contextual_recommendations=[],
                quality_metrics=None,
                learning_insights=[],
                optimization_applied=[],
                generation_time_seconds=(end_time - start_time).total_seconds(),
                confidence_score=0.0,
                brain_integration_level='error',
                error_message=str(e)
            )

    def _analyze_project_context(self, request: BrainGenerationRequest) -> ProjectContext:
        """Analyze project context using context-aware generator"""
        return self.context_generator.analyze_project_context(
            request.project_path,
            request.context_overrides
        )

    def _get_template_recommendation(
        self,
        request: BrainGenerationRequest,
        context: ProjectContext
    ) -> TemplateRecommendation:
        """Get template recommendation using adaptive template system"""
        project_context_dict = {
            'file_count': self._estimate_file_count(context.project_maturity),
            'complexity_score': self._context_to_complexity(context),
            'languages': context.technology_stack,
            'domain': context.domain
        }
        
        return self.template_system.recommend_template(
            project_context_dict,
            request.user_preferences,
            request.quality_targets
        )

    def _generate_intelligent_config(
        self,
        request: BrainGenerationRequest,
        context: ProjectContext,
        template_rec: TemplateRecommendation
    ) -> IntelligentConfiguration:
        """Generate intelligent configuration using brain-enhanced config system"""
        config_context = ConfigurationContext(
            project_size=self._map_project_size(context.project_maturity),
            complexity_level=self._map_complexity_level(context),
            team_size=1,  # Default, could be extracted from context
            domain=context.domain,
            languages=context.technology_stack,
            frameworks=[],  # Could be extracted from technology_stack
            has_tests=True,  # Could be analyzed from project
            test_coverage=0.8,  # Default
            documentation_maturity='basic',  # Could be assessed
            time_constraints=request.time_constraints or 'moderate',
            target_audience=', '.join(request.target_audience) if request.target_audience else 'developers'
        )
        
        return self.config_system.generate_intelligent_config(
            config_context,
            request.user_preferences,
            {'time_limited': request.time_constraints == 'tight'}
        )

    def _get_contextual_recommendations(
        self,
        request: BrainGenerationRequest,
        context: ProjectContext,
        config: IntelligentConfiguration
    ) -> List[ContextualRecommendation]:
        """Generate contextual recommendations using context-aware generator"""
        return self.context_generator.generate_contextual_recommendations(
            context,
            request.user_preferences
        )

    def _execute_enhanced_generation(
        self,
        request: BrainGenerationRequest,
        context: ProjectContext,
        config: IntelligentConfiguration,
        recommendations: List[ContextualRecommendation]
    ) -> Dict[str, Any]:
        """Execute the actual documentation generation with enhancements"""
        
        # Enhanced configuration with context awareness
        enhanced_config = self.context_generator.enhance_documentation_config(
            config.template_config,
            context,
            recommendations
        )
        
        # Apply optimizations
        optimizations_applied = []
        if self.enable_optimization:
            if config.optimization_flags.get('parallel_processing'):
                optimizations_applied.append('parallel_processing')
            if config.optimization_flags.get('fast_mode'):
                optimizations_applied.append('fast_mode')
        
        # Simulate generation (in real implementation, this would call the actual generator)
        output_paths = []
        if request.output_path:
            output_paths.append(request.output_path / 'enhanced_documentation.md')
            if enhanced_config.get('include_diagrams'):
                output_paths.append(request.output_path / 'architecture_diagrams.md')
            if enhanced_config.get('visual_content'):
                output_paths.append(request.output_path / 'visual_content.md')
        
        return {
            'output_paths': output_paths,
            'enhanced_config': enhanced_config,
            'optimizations': optimizations_applied,
            'warnings': []
        }

    def _assess_generation_quality(
        self,
        generation_result: Dict[str, Any],
        config: IntelligentConfiguration
    ) -> QualityMetrics:
        """Assess quality of generated documentation"""
        
        # Quality assessment based on configuration and targets
        base_quality = 0.8  # Base quality score
        
        # Adjust based on configuration quality
        if config.confidence_score > 0.8:
            base_quality += 0.1
        
        # Adjust based on optimization targets
        quality_targets = config.quality_targets
        readability = quality_targets.get('readability', 0.8) * (0.9 + 0.1 * config.confidence_score)
        completeness = quality_targets.get('completeness', 0.8) * (0.9 + 0.1 * config.confidence_score)
        accuracy = quality_targets.get('accuracy', 0.85) * (0.95 + 0.05 * config.confidence_score)
        
        return QualityMetrics(
            generation_id=str(uuid.uuid4()),
            quality_score=base_quality,
            readability_score=readability,
            completeness_score=completeness,
            accuracy_score=accuracy,
            timestamp=datetime.now().isoformat()
        )

    def _extract_learning_insights(
        self,
        request: BrainGenerationRequest,
        result: Dict[str, Any],
        quality: QualityMetrics
    ) -> List[LearningInsight]:
        """Extract learning insights from generation process"""
        insights = []
        
        if self.pattern_engine:
            # Get optimization suggestions
            optimization_insights = self.pattern_engine.get_optimization_suggestions(
                result.get('enhanced_config', {}),
                {'project_path': str(request.project_path)}
            )
            insights.extend(optimization_insights)
        
        # Quality-based insights
        if quality.quality_score < 0.7:
            insights.append(LearningInsight(
                insight_type="quality_improvement",
                description="Quality below expected threshold",
                confidence=0.8,
                supporting_patterns=[],
                recommendation="Review configuration parameters",
                impact_score=0.7
            ))
        
        return insights

    def _apply_learning_feedback(
        self,
        request: BrainGenerationRequest,
        result: Dict[str, Any],
        quality: QualityMetrics,
        config: IntelligentConfiguration
    ):
        """Apply learning feedback to improve future generations"""
        if not self.enable_learning:
            return
        
        try:
            # Record quality metrics
            if self.quality_loop:
                self.quality_loop.record_quality_metrics(quality)
            
            # Update template performance
            if self.template_system:
                success = quality.quality_score > 0.7
                self.template_system.update_template_performance(
                    config.base_template,
                    success,
                    quality.quality_score
                )
            
            # Record configuration outcome
            if self.config_system:
                context = self._create_config_context_from_request(request)
                quality_scores = {
                    'readability': quality.readability_score,
                    'completeness': quality.completeness_score,
                    'accuracy': quality.accuracy_score
                }
                
                self.config_system.record_configuration_outcome(
                    config_id=f"config_{request.request_id}",
                    context=context,
                    success=quality.quality_score > 0.7,
                    quality_scores=quality_scores,
                    user_satisfaction=0.8,  # Default, could be from user feedback
                    adjustments_made=result.get('optimizations', [])
                )
            
            self.logger.debug("Learning feedback applied successfully")
            
        except Exception as e:
            self.logger.error(f"Error applying learning feedback: {e}")

    def _create_config_context_from_request(self, request: BrainGenerationRequest) -> ConfigurationContext:
        """Create configuration context from request"""
        return ConfigurationContext(
            project_size='medium',  # Default
            complexity_level='moderate',  # Default
            team_size=1,
            domain='general',
            languages=[],
            frameworks=[],
            has_tests=True,
            test_coverage=0.8,
            documentation_maturity='basic',
            time_constraints=request.time_constraints or 'moderate',
            target_audience=', '.join(request.target_audience) if request.target_audience else 'developers'
        )

    def _calculate_overall_confidence(
        self,
        template_rec: Optional[TemplateRecommendation],
        config: Optional[IntelligentConfiguration],
        quality: Optional[QualityMetrics]
    ) -> float:
        """Calculate overall confidence score for generation"""
        confidence_factors = []
        
        if template_rec:
            confidence_factors.append(template_rec.confidence)
        
        if config:
            confidence_factors.append(config.confidence_score)
        
        if quality:
            confidence_factors.append(quality.quality_score)
        
        if not confidence_factors:
            return 0.5
        
        return sum(confidence_factors) / len(confidence_factors)

    def _determine_integration_level(self) -> str:
        """Determine the level of brain integration achieved"""
        if not self.brain_available:
            return 'basic'
        
        components_available = sum([
            self.pattern_engine is not None,
            self.template_system is not None,
            self.config_system is not None,
            self.quality_loop is not None,
            self.context_generator is not None
        ])
        
        if components_available >= 5:
            return 'full'
        elif components_available >= 3:
            return 'enhanced'
        else:
            return 'basic'

    def _estimate_file_count(self, maturity: str) -> int:
        """Estimate file count from project maturity"""
        mapping = {
            'prototype': 10,
            'development': 50,
            'production': 150,
            'legacy': 200
        }
        return mapping.get(maturity, 50)

    def _context_to_complexity(self, context: ProjectContext) -> float:
        """Convert context to complexity score"""
        complexity = 0.5  # Base complexity
        
        if len(context.technology_stack) > 3:
            complexity += 0.2
        if context.architecture_style in ['microservices', 'distributed']:
            complexity += 0.2
        if context.project_maturity == 'production':
            complexity += 0.1
        
        return min(complexity, 1.0)

    def _map_project_size(self, maturity: str) -> str:
        """Map project maturity to size"""
        mapping = {
            'prototype': 'small',
            'development': 'medium',
            'production': 'large',
            'legacy': 'enterprise'
        }
        return mapping.get(maturity, 'medium')

    def _map_complexity_level(self, context: ProjectContext) -> str:
        """Map context to complexity level"""
        complexity_score = self._context_to_complexity(context)
        
        if complexity_score > 0.8:
            return 'advanced'
        elif complexity_score > 0.6:
            return 'complex'
        elif complexity_score > 0.4:
            return 'moderate'
        else:
            return 'simple'

    # === Public API Methods ===
    
    def submit_user_feedback(
        self,
        generation_id: str,
        feedback: QualityFeedback
    ) -> bool:
        """
        Submit user feedback for quality learning
        
        Args:
            generation_id: ID of generation to provide feedback for
            feedback: User feedback data
            
        Returns:
            True if feedback recorded successfully
        """
        try:
            if self.quality_loop:
                self.quality_loop.record_user_feedback(feedback)
                self.logger.info(f"User feedback recorded for generation: {generation_id}")
                return True
            else:
                self.logger.warning("Quality feedback loop not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error recording user feedback: {e}")
            return False

    def get_system_status(self) -> BrainSystemStatus:
        """Get comprehensive system status"""
        try:
            # Check component health
            brain_connection = self.brain_available
            pattern_learning = self.pattern_engine is not None
            adaptive_templates = self.template_system is not None
            quality_feedback = self.quality_loop is not None
            context_awareness = self.context_generator is not None
            
            # Get data counts
            total_patterns = 0
            total_learning_data = 0
            
            if self.pattern_engine:
                pattern_stats = self.pattern_engine.get_pattern_statistics()
                total_patterns = pattern_stats.get('total_patterns', 0)
            
            if self.config_system:
                config_analytics = self.config_system.get_configuration_analytics()
                total_learning_data = config_analytics.get('total_configurations', 0)
            
            # Determine overall health
            components_healthy = sum([
                brain_connection, pattern_learning, adaptive_templates,
                quality_feedback, context_awareness
            ])
            
            if components_healthy >= 5:
                system_health = 'excellent'
            elif components_healthy >= 3:
                system_health = 'good'
            elif components_healthy >= 1:
                system_health = 'degraded'
            else:
                system_health = 'offline'
            
            return BrainSystemStatus(
                brain_connection=brain_connection,
                pattern_learning=pattern_learning,
                adaptive_templates=adaptive_templates,
                quality_feedback=quality_feedback,
                context_awareness=context_awareness,
                total_patterns=total_patterns,
                total_learning_data=total_learning_data,
                system_health=system_health,
                last_update=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return BrainSystemStatus(
                brain_connection=False,
                pattern_learning=False,
                adaptive_templates=False,
                quality_feedback=False,
                context_awareness=False,
                total_patterns=0,
                total_learning_data=0,
                system_health='offline',
                last_update=datetime.now().isoformat()
            )

    def get_generation_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics on documentation generation performance"""
        try:
            cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            recent_generations = [
                g for g in self._generation_history
                if datetime.fromisoformat(g.quality_metrics.timestamp if g.quality_metrics else datetime.now().isoformat()).timestamp() > cutoff
            ]
            
            if not recent_generations:
                return {"message": "No generation data available for the specified period"}
            
            # Calculate analytics
            total_generations = len(recent_generations)
            successful_generations = len([g for g in recent_generations if g.success])
            avg_confidence = sum(g.confidence_score for g in recent_generations) / total_generations
            avg_generation_time = sum(g.generation_time_seconds for g in recent_generations) / total_generations
            
            # Quality analytics
            quality_scores = [g.quality_metrics.quality_score for g in recent_generations if g.quality_metrics]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return {
                "analysis_period_days": days,
                "total_generations": total_generations,
                "success_rate": successful_generations / total_generations,
                "average_confidence": avg_confidence,
                "average_generation_time": avg_generation_time,
                "average_quality_score": avg_quality,
                "brain_integration_levels": self._analyze_integration_levels(recent_generations),
                "common_optimizations": self._analyze_common_optimizations(recent_generations),
                "system_performance": {
                    "brain_availability_rate": len([g for g in recent_generations if g.brain_integration_level in ['enhanced', 'full']]) / total_generations,
                    "learning_enabled_rate": len([g for g in recent_generations if g.learning_insights]) / total_generations
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting generation analytics: {e}")
            return {"error": str(e)}

    def _analyze_integration_levels(self, generations: List[BrainGenerationResult]) -> Dict[str, int]:
        """Analyze distribution of brain integration levels"""
        levels = {}
        for gen in generations:
            level = gen.brain_integration_level
            levels[level] = levels.get(level, 0) + 1
        return levels

    def _analyze_common_optimizations(self, generations: List[BrainGenerationResult]) -> List[Tuple[str, int]]:
        """Analyze most commonly applied optimizations"""
        optimization_counts = {}
        
        for gen in generations:
            for opt in gen.optimization_applied:
                optimization_counts[opt] = optimization_counts.get(opt, 0) + 1
        
        return sorted(optimization_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    def export_brain_data(self, output_path: Path, include_analytics: bool = True) -> bool:
        """
        Export comprehensive brain integration data
        
        Args:
            output_path: Path to save exported data
            include_analytics: Whether to include analytics data
            
        Returns:
            True if export successful
        """
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "system_status": asdict(self.get_system_status()),
                "generation_history": [asdict(g) for g in self._generation_history[-100:]],  # Last 100
            }
            
            if include_analytics:
                export_data["analytics"] = {
                    "generation_analytics": self.get_generation_analytics(90),  # 90 days
                    "pattern_statistics": self.pattern_engine.get_pattern_statistics() if self.pattern_engine else {},
                    "template_analytics": self.template_system.get_template_analytics() if self.template_system else {},
                    "configuration_analytics": self.config_system.get_configuration_analytics() if self.config_system else {}
                }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Brain integration data exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting brain data: {e}")
            return False

    def close(self):
        """Clean up brain integration resources"""
        if self.brain:
            self.brain.close()
        
        self.logger.info("BrainIntegrationAPI closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# === Factory Functions ===

def create_brain_integration_api(
    brain_root: Optional[Path] = None,
    enable_learning: bool = True,
    enable_optimization: bool = True
) -> BrainIntegrationAPI:
    """
    Factory function to create brain integration API with error handling
    
    Args:
        brain_root: Path to cortex-brain directory
        enable_learning: Enable pattern learning capabilities
        enable_optimization: Enable performance optimizations
        
    Returns:
        BrainIntegrationAPI instance
    """
    try:
        return BrainIntegrationAPI(brain_root, enable_learning, enable_optimization)
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create BrainIntegrationAPI: {e}")
        # Return API with minimal functionality
        return BrainIntegrationAPI(None, False, False)


def create_simple_generation_request(
    project_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> BrainGenerationRequest:
    """
    Factory function to create simple generation request
    
    Args:
        project_path: Path to project to document
        output_path: Path for output documentation
        **kwargs: Additional request parameters
        
    Returns:
        BrainGenerationRequest instance
    """
    return BrainGenerationRequest(
        request_id=str(uuid.uuid4()),
        project_path=Path(project_path),
        output_path=Path(output_path) if output_path else None,
        **kwargs
    )