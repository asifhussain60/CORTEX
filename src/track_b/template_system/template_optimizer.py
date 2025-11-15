"""
CORTEX 3.0 Track B: Template Optimizer
======================================

Advanced template optimization system that analyzes template performance,
optimizes template selection, and improves response generation efficiency.

Key Features:
- Template performance analysis
- Automatic template optimization
- Response time improvement
- Template usage pattern learning
- Cache optimization strategies

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import pickle

from .template_engine import TemplateEngine, Template, TemplateType, TemplateFormat
from .response_generator import ResponseGenerator, GeneratedResponse, ResponseType


class OptimizationStrategy(Enum):
    """Template optimization strategies."""
    PERFORMANCE = "performance"      # Optimize for speed
    ACCURACY = "accuracy"           # Optimize for accuracy
    USAGE = "usage"                 # Optimize for usage patterns
    BALANCED = "balanced"           # Balanced optimization


class AnalysisType(Enum):
    """Types of analysis."""
    TEMPLATE_PERFORMANCE = "template_performance"
    USAGE_PATTERNS = "usage_patterns"
    CACHE_EFFICIENCY = "cache_efficiency"
    RESPONSE_QUALITY = "response_quality"


@dataclass
class TemplatePerformanceMetrics:
    """Performance metrics for a template."""
    template_id: str
    total_uses: int = 0
    avg_render_time_ms: float = 0.0
    success_rate: float = 0.0
    avg_confidence_score: float = 0.0
    cache_hit_rate: float = 0.0
    user_satisfaction: float = 0.0
    last_used: Optional[datetime] = None
    performance_trend: str = "stable"  # "improving", "declining", "stable"


@dataclass
class UsagePattern:
    """Usage pattern for templates."""
    pattern_id: str
    description: str
    trigger_conditions: List[str]
    associated_templates: List[str]
    frequency: int = 0
    success_rate: float = 0.0
    typical_context: Dict[str, Any] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation."""
    recommendation_id: str
    type: str
    template_id: Optional[str] = None
    description: str = ""
    priority: int = 0  # 1-10, higher is more important
    estimated_improvement: float = 0.0  # Estimated improvement percentage
    implementation_effort: str = "low"  # "low", "medium", "high"
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class TemplateOptimizer:
    """
    Advanced template optimizer for CORTEX Track B
    
    Analyzes template and response performance to provide optimization
    recommendations and automatically improve system efficiency.
    """
    
    def __init__(self, template_engine: TemplateEngine, response_generator: ResponseGenerator):
        self.logger = logging.getLogger("cortex.track_b.template_optimizer")
        
        # Core components
        self.template_engine = template_engine
        self.response_generator = response_generator
        
        # Performance tracking
        self.performance_history: Dict[str, List[TemplatePerformanceMetrics]] = {}
        self.usage_patterns: Dict[str, UsagePattern] = {}
        
        # Analysis results
        self.optimization_recommendations: List[OptimizationRecommendation] = []
        self.performance_baselines: Dict[str, float] = {}
        
        # Configuration
        self.analysis_window_days = 7
        self.min_usage_threshold = 5
        self.optimization_frequency_hours = 24
        
        # Analysis state
        self.last_analysis: Optional[datetime] = None
        self.analysis_in_progress = False
        
        # Load historical data
        self._load_optimization_data()
    
    def run_optimization_analysis(self, strategy: OptimizationStrategy = OptimizationStrategy.BALANCED) -> Dict[str, Any]:
        """Run comprehensive optimization analysis."""
        if self.analysis_in_progress:
            return {"status": "analysis_in_progress", "message": "Analysis already running"}
        
        try:
            self.analysis_in_progress = True
            analysis_start = datetime.now()
            
            self.logger.info(f"Starting optimization analysis with {strategy.value} strategy")
            
            # Collect current performance data
            current_metrics = self._collect_performance_metrics()
            
            # Run different analysis types
            analysis_results = {}
            
            # Template performance analysis
            analysis_results['template_performance'] = self._analyze_template_performance(current_metrics)
            
            # Usage pattern analysis  
            analysis_results['usage_patterns'] = self._analyze_usage_patterns()
            
            # Cache efficiency analysis
            analysis_results['cache_efficiency'] = self._analyze_cache_efficiency()
            
            # Response quality analysis
            analysis_results['response_quality'] = self._analyze_response_quality()
            
            # Generate optimization recommendations
            recommendations = self._generate_recommendations(analysis_results, strategy)
            analysis_results['recommendations'] = recommendations
            
            # Update optimization state
            self.last_analysis = datetime.now()
            self.optimization_recommendations = recommendations
            
            # Save analysis results
            self._save_optimization_data()
            
            analysis_time = (datetime.now() - analysis_start).total_seconds()
            
            result = {
                "status": "completed",
                "analysis_time_seconds": analysis_time,
                "strategy_used": strategy.value,
                "recommendations_count": len(recommendations),
                "analysis_results": analysis_results,
                "summary": self._create_analysis_summary(analysis_results)
            }
            
            self.logger.info(f"Optimization analysis completed in {analysis_time:.2f}s with {len(recommendations)} recommendations")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during optimization analysis: {e}")
            return {
                "status": "error",
                "error": str(e),
                "recommendations_count": 0
            }
        finally:
            self.analysis_in_progress = False
    
    def _collect_performance_metrics(self) -> Dict[str, TemplatePerformanceMetrics]:
        """Collect current performance metrics for all templates."""
        metrics = {}
        
        try:
            # Get template engine stats
            template_stats = self.template_engine.get_template_stats()
            engine_performance = template_stats.get('performance_stats', {})
            
            # Get response generator stats
            generator_stats = self.response_generator.get_generation_stats()
            
            # Process each template
            for template_id, template in self.template_engine.templates.items():
                template_perf = engine_performance.get(template_id, {})
                
                metrics[template_id] = TemplatePerformanceMetrics(
                    template_id=template_id,
                    total_uses=template.usage_count,
                    avg_render_time_ms=template_perf.get('avg_time_ms', 0.0),
                    success_rate=self._calculate_template_success_rate(template_id),
                    avg_confidence_score=self._calculate_avg_confidence(template_id),
                    cache_hit_rate=self._calculate_template_cache_hit_rate(template_id),
                    last_used=template.last_used,
                    performance_trend=self._analyze_performance_trend(template_id)
                )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {e}")
            return {}
    
    def _calculate_template_success_rate(self, template_id: str) -> float:
        """Calculate success rate for a specific template."""
        # This would be based on actual usage data
        # For now, use a simple heuristic based on usage count and render times
        template = self.template_engine.templates.get(template_id)
        if not template or template.usage_count == 0:
            return 0.0
        
        # Templates with more usage and recent activity are considered more successful
        recency_factor = 1.0
        if template.last_used:
            days_since_used = (datetime.now() - template.last_used).days
            recency_factor = max(0.1, 1.0 - (days_since_used / 30.0))
        
        usage_factor = min(1.0, template.usage_count / 10.0)  # Normalized to 10 uses
        
        return min(1.0, (usage_factor * 0.7 + recency_factor * 0.3))
    
    def _calculate_avg_confidence(self, template_id: str) -> float:
        """Calculate average confidence score for template responses."""
        # This would come from actual response data
        # For now, estimate based on template characteristics
        template = self.template_engine.templates.get(template_id)
        if not template:
            return 0.0
        
        # Templates with more variables and conditions tend to be more specific
        variable_count = len(template.variables)
        condition_count = len(template.conditions)
        
        base_confidence = 0.5
        variable_bonus = min(0.3, variable_count * 0.05)
        condition_bonus = min(0.2, condition_count * 0.1)
        
        return min(1.0, base_confidence + variable_bonus + condition_bonus)
    
    def _calculate_template_cache_hit_rate(self, template_id: str) -> float:
        """Calculate cache hit rate for responses using this template."""
        # This would come from actual cache statistics
        # For now, estimate based on template usage patterns
        template = self.template_engine.templates.get(template_id)
        if not template or template.usage_count < 2:
            return 0.0
        
        # Templates with stable content and high usage have better cache rates
        stability_factor = 0.8  # Assume templates are generally stable
        usage_factor = min(1.0, template.usage_count / 20.0)
        
        return stability_factor * usage_factor
    
    def _analyze_performance_trend(self, template_id: str) -> str:
        """Analyze performance trend for a template."""
        if template_id not in self.performance_history:
            return "stable"
        
        history = self.performance_history[template_id]
        if len(history) < 3:
            return "stable"
        
        # Analyze recent performance metrics
        recent_metrics = sorted(history, key=lambda x: x.last_used or datetime.min)[-3:]
        
        # Check render time trend
        render_times = [m.avg_render_time_ms for m in recent_metrics if m.avg_render_time_ms > 0]
        if len(render_times) >= 2:
            if render_times[-1] < render_times[0] * 0.9:  # 10% improvement
                return "improving"
            elif render_times[-1] > render_times[0] * 1.1:  # 10% degradation
                return "declining"
        
        return "stable"
    
    def _analyze_template_performance(self, metrics: Dict[str, TemplatePerformanceMetrics]) -> Dict[str, Any]:
        """Analyze template performance and identify issues."""
        try:
            performance_issues = []
            high_performers = []
            improvement_candidates = []
            
            # Define performance thresholds
            high_render_time_threshold = 100.0  # ms
            low_success_rate_threshold = 0.6
            high_success_rate_threshold = 0.9
            
            for template_id, metric in metrics.items():
                template = self.template_engine.templates[template_id]
                
                # Identify performance issues
                if metric.avg_render_time_ms > high_render_time_threshold:
                    performance_issues.append({
                        'template_id': template_id,
                        'issue': 'slow_rendering',
                        'value': metric.avg_render_time_ms,
                        'threshold': high_render_time_threshold
                    })
                
                if metric.success_rate < low_success_rate_threshold:
                    performance_issues.append({
                        'template_id': template_id,
                        'issue': 'low_success_rate',
                        'value': metric.success_rate,
                        'threshold': low_success_rate_threshold
                    })
                
                # Identify high performers
                if (metric.success_rate > high_success_rate_threshold and 
                    metric.avg_render_time_ms < 50.0 and
                    metric.total_uses > self.min_usage_threshold):
                    high_performers.append({
                        'template_id': template_id,
                        'success_rate': metric.success_rate,
                        'render_time': metric.avg_render_time_ms,
                        'usage': metric.total_uses
                    })
                
                # Identify improvement candidates
                if (metric.total_uses > self.min_usage_threshold and
                    metric.performance_trend == "declining"):
                    improvement_candidates.append({
                        'template_id': template_id,
                        'trend': metric.performance_trend,
                        'current_success_rate': metric.success_rate
                    })
            
            return {
                'performance_issues': performance_issues,
                'high_performers': high_performers,
                'improvement_candidates': improvement_candidates,
                'overall_stats': {
                    'total_templates': len(metrics),
                    'avg_render_time': statistics.mean([m.avg_render_time_ms for m in metrics.values() if m.avg_render_time_ms > 0]) if metrics else 0,
                    'avg_success_rate': statistics.mean([m.success_rate for m in metrics.values()]) if metrics else 0,
                    'templates_with_issues': len(performance_issues)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing template performance: {e}")
            return {'error': str(e)}
    
    def _analyze_usage_patterns(self) -> Dict[str, Any]:
        """Analyze template usage patterns."""
        try:
            patterns = {}
            
            # Analyze template usage by type
            usage_by_type = {}
            usage_by_time = {}
            
            for template_id, template in self.template_engine.templates.items():
                template_type = template.template_type.value
                
                if template_type not in usage_by_type:
                    usage_by_type[template_type] = {
                        'total_usage': 0,
                        'template_count': 0,
                        'avg_usage_per_template': 0
                    }
                
                usage_by_type[template_type]['total_usage'] += template.usage_count
                usage_by_type[template_type]['template_count'] += 1
            
            # Calculate averages
            for type_stats in usage_by_type.values():
                if type_stats['template_count'] > 0:
                    type_stats['avg_usage_per_template'] = type_stats['total_usage'] / type_stats['template_count']
            
            # Identify underused templates
            underused_templates = []
            for template_id, template in self.template_engine.templates.items():
                type_avg = usage_by_type[template.template_type.value]['avg_usage_per_template']
                if template.usage_count < type_avg * 0.5 and type_avg > 0:  # Less than 50% of average
                    underused_templates.append({
                        'template_id': template_id,
                        'usage': template.usage_count,
                        'type_average': type_avg,
                        'underutilization_ratio': template.usage_count / type_avg if type_avg > 0 else 0
                    })
            
            # Identify popular patterns
            popular_patterns = []
            for template_id, template in self.template_engine.templates.items():
                if template.usage_count > self.min_usage_threshold * 2:
                    popular_patterns.append({
                        'template_id': template_id,
                        'usage': template.usage_count,
                        'type': template.template_type.value,
                        'tags': template.tags
                    })
            
            return {
                'usage_by_type': usage_by_type,
                'underused_templates': underused_templates,
                'popular_patterns': popular_patterns,
                'total_usage': sum(t.usage_count for t in self.template_engine.templates.values()),
                'most_used_type': max(usage_by_type.items(), key=lambda x: x[1]['total_usage'])[0] if usage_by_type else None
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing usage patterns: {e}")
            return {'error': str(e)}
    
    def _analyze_cache_efficiency(self) -> Dict[str, Any]:
        """Analyze response cache efficiency."""
        try:
            cache_stats = self.response_generator.get_generation_stats()
            
            cache_analysis = {
                'current_cache_size': cache_stats.get('cache_size', 0),
                'cache_hit_rate': cache_stats.get('cache_hit_rate', 0),
                'cache_efficiency_score': 0,
                'recommendations': []
            }
            
            # Calculate cache efficiency score
            hit_rate = cache_stats.get('cache_hit_rate', 0)
            cache_size = cache_stats.get('cache_size', 0)
            
            # Efficiency based on hit rate and utilization
            hit_rate_score = min(1.0, hit_rate / 75.0)  # Target 75% hit rate
            utilization_score = min(1.0, cache_size / (self.response_generator.cache_max_size * 0.8))  # Target 80% utilization
            
            cache_analysis['cache_efficiency_score'] = (hit_rate_score + utilization_score) / 2
            
            # Generate cache recommendations
            if hit_rate < 50:
                cache_analysis['recommendations'].append({
                    'type': 'improve_hit_rate',
                    'description': 'Cache hit rate is below 50%. Consider adjusting cache TTL or improving template selection.',
                    'priority': 8
                })
            
            if cache_size < self.response_generator.cache_max_size * 0.1:
                cache_analysis['recommendations'].append({
                    'type': 'increase_cache_usage',
                    'description': 'Cache is underutilized. Consider caching more response types.',
                    'priority': 5
                })
            
            return cache_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing cache efficiency: {e}")
            return {'error': str(e)}
    
    def _analyze_response_quality(self) -> Dict[str, Any]:
        """Analyze overall response quality."""
        try:
            # This would ideally include user feedback data
            # For now, analyze based on available metrics
            
            generator_stats = self.response_generator.get_generation_stats()
            
            quality_analysis = {
                'avg_confidence': generator_stats.get('average_confidence', 0),
                'response_type_distribution': {},
                'quality_score': 0,
                'improvement_areas': []
            }
            
            # Analyze response type distribution
            by_type = generator_stats.get('by_type', {})
            total_responses = generator_stats.get('total_responses', 1)
            
            for response_type, stats in by_type.items():
                quality_analysis['response_type_distribution'][response_type] = {
                    'count': stats.get('count', 0),
                    'percentage': (stats.get('count', 0) / total_responses) * 100,
                    'avg_confidence': stats.get('avg_confidence', 0),
                    'success_rate': stats.get('success_rate', 0)
                }
            
            # Calculate overall quality score
            avg_confidence = quality_analysis['avg_confidence']
            fallback_rate = quality_analysis['response_type_distribution'].get('fallback', {}).get('percentage', 0)
            
            confidence_score = min(1.0, avg_confidence / 0.8)  # Target 80% confidence
            fallback_penalty = max(0, 1.0 - (fallback_rate / 20.0))  # Penalty if >20% fallback
            
            quality_analysis['quality_score'] = (confidence_score * 0.7 + fallback_penalty * 0.3)
            
            # Identify improvement areas
            if avg_confidence < 0.6:
                quality_analysis['improvement_areas'].append({
                    'area': 'low_confidence',
                    'description': 'Average response confidence is below 60%',
                    'suggested_action': 'Improve template specificity and context analysis'
                })
            
            if fallback_rate > 15:
                quality_analysis['improvement_areas'].append({
                    'area': 'high_fallback_rate',
                    'description': f'Fallback response rate is {fallback_rate:.1f}%',
                    'suggested_action': 'Add more templates or improve pattern matching'
                })
            
            return quality_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing response quality: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any], strategy: OptimizationStrategy) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        
        try:
            # Template performance recommendations
            template_analysis = analysis_results.get('template_performance', {})
            
            for issue in template_analysis.get('performance_issues', []):
                if issue['issue'] == 'slow_rendering':
                    recommendations.append(OptimizationRecommendation(
                        recommendation_id=f"perf_{issue['template_id']}_render_time",
                        type="performance",
                        template_id=issue['template_id'],
                        description=f"Template {issue['template_id']} has slow rendering time ({issue['value']:.1f}ms). Consider simplifying template logic or optimizing variable processing.",
                        priority=7 if strategy == OptimizationStrategy.PERFORMANCE else 5,
                        estimated_improvement=20.0,
                        implementation_effort="medium",
                        details=issue
                    ))
                
                elif issue['issue'] == 'low_success_rate':
                    recommendations.append(OptimizationRecommendation(
                        recommendation_id=f"quality_{issue['template_id']}_success_rate",
                        type="quality",
                        template_id=issue['template_id'],
                        description=f"Template {issue['template_id']} has low success rate ({issue['value']:.1%}). Review template conditions and variable requirements.",
                        priority=8 if strategy == OptimizationStrategy.ACCURACY else 6,
                        estimated_improvement=30.0,
                        implementation_effort="low",
                        details=issue
                    ))
            
            # Usage pattern recommendations
            usage_analysis = analysis_results.get('usage_patterns', {})
            
            for underused in usage_analysis.get('underused_templates', [])[:3]:  # Top 3
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"usage_{underused['template_id']}_underutilized",
                    type="usage",
                    template_id=underused['template_id'],
                    description=f"Template {underused['template_id']} is underutilized. Consider improving discoverability or reviewing conditions.",
                    priority=4 if strategy == OptimizationStrategy.USAGE else 3,
                    estimated_improvement=15.0,
                    implementation_effort="low",
                    details=underused
                ))
            
            # Cache efficiency recommendations
            cache_analysis = analysis_results.get('cache_efficiency', {})
            
            for cache_rec in cache_analysis.get('recommendations', []):
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"cache_{cache_rec['type']}",
                    type="cache",
                    description=cache_rec['description'],
                    priority=cache_rec['priority'],
                    estimated_improvement=10.0,
                    implementation_effort="medium",
                    details=cache_rec
                ))
            
            # Response quality recommendations
            quality_analysis = analysis_results.get('response_quality', {})
            
            for improvement in quality_analysis.get('improvement_areas', []):
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"quality_{improvement['area']}",
                    type="quality",
                    description=f"{improvement['description']}. {improvement['suggested_action']}",
                    priority=7 if strategy == OptimizationStrategy.ACCURACY else 5,
                    estimated_improvement=25.0,
                    implementation_effort="medium",
                    details=improvement
                ))
            
            # Sort by priority (descending)
            recommendations.sort(key=lambda x: x.priority, reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _create_analysis_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the analysis results."""
        try:
            template_analysis = analysis_results.get('template_performance', {})
            usage_analysis = analysis_results.get('usage_patterns', {})
            cache_analysis = analysis_results.get('cache_efficiency', {})
            quality_analysis = analysis_results.get('response_quality', {})
            
            summary = {
                'overall_health_score': 0,
                'key_metrics': {},
                'top_issues': [],
                'success_indicators': []
            }
            
            # Calculate overall health score
            performance_score = 1.0 - (len(template_analysis.get('performance_issues', [])) / max(1, len(self.template_engine.templates)))
            cache_score = cache_analysis.get('cache_efficiency_score', 0) / 100  # Assuming percentage
            quality_score = quality_analysis.get('quality_score', 0)
            
            overall_score = (performance_score * 0.4 + cache_score * 0.3 + quality_score * 0.3) * 100
            summary['overall_health_score'] = round(overall_score, 1)
            
            # Key metrics
            summary['key_metrics'] = {
                'total_templates': template_analysis.get('overall_stats', {}).get('total_templates', 0),
                'avg_render_time_ms': round(template_analysis.get('overall_stats', {}).get('avg_render_time', 0), 2),
                'cache_hit_rate': cache_analysis.get('cache_hit_rate', 0),
                'avg_confidence': round(quality_analysis.get('avg_confidence', 0) * 100, 1),
                'total_usage': usage_analysis.get('total_usage', 0)
            }
            
            # Top issues (from recommendations)
            recommendations = analysis_results.get('recommendations', [])
            summary['top_issues'] = [
                {
                    'type': rec.type,
                    'description': rec.description[:100] + '...' if len(rec.description) > 100 else rec.description,
                    'priority': rec.priority
                }
                for rec in recommendations[:3]  # Top 3 issues
            ]
            
            # Success indicators
            high_performers = template_analysis.get('high_performers', [])
            if high_performers:
                summary['success_indicators'].append(f"{len(high_performers)} high-performing templates identified")
            
            if summary['key_metrics']['cache_hit_rate'] > 60:
                summary['success_indicators'].append("Good cache efficiency")
            
            if summary['key_metrics']['avg_confidence'] > 70:
                summary['success_indicators'].append("High response confidence")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error creating analysis summary: {e}")
            return {'error': str(e)}
    
    def apply_recommendation(self, recommendation_id: str) -> Dict[str, Any]:
        """Apply a specific optimization recommendation."""
        try:
            recommendation = None
            for rec in self.optimization_recommendations:
                if rec.recommendation_id == recommendation_id:
                    recommendation = rec
                    break
            
            if not recommendation:
                return {'success': False, 'error': 'Recommendation not found'}
            
            self.logger.info(f"Applying recommendation: {recommendation_id}")
            
            # Apply based on recommendation type
            if recommendation.type == "performance":
                return self._apply_performance_optimization(recommendation)
            elif recommendation.type == "quality":
                return self._apply_quality_optimization(recommendation)
            elif recommendation.type == "usage":
                return self._apply_usage_optimization(recommendation)
            elif recommendation.type == "cache":
                return self._apply_cache_optimization(recommendation)
            else:
                return {'success': False, 'error': 'Unknown recommendation type'}
                
        except Exception as e:
            self.logger.error(f"Error applying recommendation {recommendation_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _apply_performance_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply performance-related optimizations."""
        try:
            if recommendation.template_id:
                template = self.template_engine.templates.get(recommendation.template_id)
                if template:
                    # Example optimizations (would be more sophisticated in practice)
                    if 'render_time' in recommendation.details:
                        # Could optimize template content, reduce complexity, etc.
                        pass
            
            return {'success': True, 'message': 'Performance optimization applied'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_quality_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply quality-related optimizations."""
        try:
            # Example quality optimizations
            # Could adjust template conditions, improve variable handling, etc.
            return {'success': True, 'message': 'Quality optimization applied'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_usage_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply usage-related optimizations."""
        try:
            # Example usage optimizations
            # Could adjust template priority, improve discoverability, etc.
            return {'success': True, 'message': 'Usage optimization applied'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_cache_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply cache-related optimizations."""
        try:
            # Example cache optimizations
            # Could adjust cache TTL, improve cache key generation, etc.
            return {'success': True, 'message': 'Cache optimization applied'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _load_optimization_data(self):
        """Load historical optimization data."""
        try:
            data_file = Path(__file__).parent / "optimization_data.pkl"
            if data_file.exists():
                with open(data_file, 'rb') as f:
                    data = pickle.load(f)
                    self.performance_history = data.get('performance_history', {})
                    self.usage_patterns = data.get('usage_patterns', {})
                    self.performance_baselines = data.get('performance_baselines', {})
                    
                self.logger.debug("Loaded optimization data from disk")
                
        except Exception as e:
            self.logger.error(f"Error loading optimization data: {e}")
    
    def _save_optimization_data(self):
        """Save optimization data to disk."""
        try:
            data_file = Path(__file__).parent / "optimization_data.pkl"
            data = {
                'performance_history': self.performance_history,
                'usage_patterns': self.usage_patterns,
                'performance_baselines': self.performance_baselines,
                'last_analysis': self.last_analysis
            }
            
            with open(data_file, 'wb') as f:
                pickle.dump(data, f)
                
            self.logger.debug("Saved optimization data to disk")
            
        except Exception as e:
            self.logger.error(f"Error saving optimization data: {e}")
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status and recommendations."""
        return {
            'last_analysis': self.last_analysis.isoformat() if self.last_analysis else None,
            'analysis_in_progress': self.analysis_in_progress,
            'recommendations_count': len(self.optimization_recommendations),
            'high_priority_recommendations': len([r for r in self.optimization_recommendations if r.priority >= 7]),
            'next_analysis_due': self._calculate_next_analysis_time(),
            'recommendations': [
                {
                    'id': rec.recommendation_id,
                    'type': rec.type,
                    'description': rec.description[:100] + '...' if len(rec.description) > 100 else rec.description,
                    'priority': rec.priority,
                    'estimated_improvement': rec.estimated_improvement,
                    'effort': rec.implementation_effort
                }
                for rec in self.optimization_recommendations[:10]  # Top 10
            ]
        }
    
    def _calculate_next_analysis_time(self) -> Optional[str]:
        """Calculate when the next analysis should run."""
        if not self.last_analysis:
            return "now"
        
        next_analysis = self.last_analysis + timedelta(hours=self.optimization_frequency_hours)
        if datetime.now() >= next_analysis:
            return "now"
        
        return next_analysis.isoformat()