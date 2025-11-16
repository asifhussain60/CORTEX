"""
Quality Feedback Loop - Continuous Learning from Documentation Quality
Feature 5.5: Quality-Driven Adaptive Optimization

Connects documentation quality metrics to CORTEX Brain learning system for
continuous improvement and adaptive optimization of generation strategies.
"""

import json
import logging
import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

from .brain_connector import BrainConnector, QualityMetrics


class QualityDimension(Enum):
    """Quality dimensions for documentation assessment"""
    READABILITY = "readability"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    VISUAL_QUALITY = "visual_quality"
    STRUCTURE = "structure"
    USEFULNESS = "usefulness"
    MAINTAINABILITY = "maintainability"


@dataclass
class QualityFeedback:
    """User feedback on documentation quality"""
    feedback_id: str
    generation_id: str
    user_id: Optional[str]
    timestamp: str
    overall_rating: float  # 0.0 to 1.0
    dimension_ratings: Dict[str, float]  # QualityDimension -> score
    text_feedback: Optional[str]
    improvement_suggestions: List[str]
    would_recommend: bool
    time_to_understand: Optional[int]  # seconds
    found_errors: List[str]
    missing_content: List[str]


@dataclass
class QualityTrend:
    """Quality trend analysis over time"""
    dimension: str
    trend_direction: str  # 'improving', 'declining', 'stable'
    slope: float
    confidence: float
    sample_size: int
    time_span_days: int
    current_average: float
    target_average: float


@dataclass
class ImprovementRecommendation:
    """Recommendation for improving documentation quality"""
    recommendation_id: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'template', 'content', 'process', 'configuration'
    description: str
    expected_impact: float
    confidence: float
    supporting_evidence: List[str]
    implementation_effort: str  # 'low', 'medium', 'high'
    target_dimension: str


class QualityFeedbackLoop:
    """
    Continuous learning system that collects quality metrics, analyzes trends,
    and provides recommendations for improving documentation generation.
    """
    
    def __init__(self, brain_connector: Optional[BrainConnector] = None):
        """
        Initialize quality feedback loop system
        
        Args:
            brain_connector: Connection to CORTEX Brain for persistent storage
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain_connector
        
        # Quality data storage
        self._quality_history: List[QualityMetrics] = []
        self._feedback_history: List[QualityFeedback] = []
        self._trend_cache: Dict[str, QualityTrend] = {}
        self._recommendations_cache: List[ImprovementRecommendation] = []
        
        # Quality thresholds for alerts
        self.quality_thresholds = {
            QualityDimension.READABILITY.value: 0.75,
            QualityDimension.COMPLETENESS.value: 0.80,
            QualityDimension.ACCURACY.value: 0.90,
            QualityDimension.VISUAL_QUALITY.value: 0.70,
            QualityDimension.STRUCTURE.value: 0.75,
            QualityDimension.USEFULNESS.value: 0.80,
            QualityDimension.MAINTAINABILITY.value: 0.75
        }
        
        # Load historical data
        self._load_quality_history()
        
        self.logger.info("QualityFeedbackLoop initialized")

    def record_quality_metrics(self, metrics: QualityMetrics):
        """
        Record quality metrics for learning and trend analysis
        
        Args:
            metrics: Quality metrics from documentation generation
        """
        try:
            # Add timestamp if not present
            if not metrics.timestamp:
                metrics.timestamp = datetime.now().isoformat()
            
            # Store in history
            self._quality_history.append(metrics)
            
            # Store in brain if available
            if self.brain:
                self.brain.record_documentation_quality(metrics)
            
            # Analyze for immediate feedback
            immediate_insights = self._analyze_immediate_quality(metrics)
            if immediate_insights:
                self.logger.info(f"Immediate quality insights: {immediate_insights}")
            
            # Update trend analysis
            self._update_quality_trends()
            
            # Check for quality alerts
            alerts = self._check_quality_alerts(metrics)
            for alert in alerts:
                self.logger.warning(f"Quality alert: {alert}")
            
            self.logger.debug(f"Recorded quality metrics: {metrics.generation_id}")
            
        except Exception as e:
            self.logger.error(f"Error recording quality metrics: {e}")

    def record_user_feedback(self, feedback: QualityFeedback):
        """
        Record user feedback for qualitative learning
        
        Args:
            feedback: User feedback on documentation quality
        """
        try:
            # Validate feedback
            if not 0 <= feedback.overall_rating <= 1:
                raise ValueError("Overall rating must be between 0 and 1")
            
            # Store feedback
            self._feedback_history.append(feedback)
            
            # Correlate with quality metrics
            self._correlate_feedback_with_metrics(feedback)
            
            # Extract insights from text feedback
            insights = self._extract_insights_from_text_feedback(feedback)
            if insights:
                self.logger.info(f"Text feedback insights: {insights}")
            
            # Update recommendations based on feedback
            self._update_recommendations_from_feedback(feedback)
            
            self.logger.info(f"Recorded user feedback: {feedback.feedback_id}")
            
        except Exception as e:
            self.logger.error(f"Error recording user feedback: {e}")

    def _analyze_immediate_quality(self, metrics: QualityMetrics) -> List[str]:
        """Analyze metrics for immediate insights"""
        insights = []
        
        # Check individual scores against thresholds
        scores = {
            QualityDimension.READABILITY.value: metrics.readability_score,
            QualityDimension.COMPLETENESS.value: metrics.completeness_score,
            QualityDimension.ACCURACY.value: metrics.accuracy_score
        }
        
        for dimension, score in scores.items():
            threshold = self.quality_thresholds.get(dimension, 0.75)
            if score < threshold:
                gap = threshold - score
                insights.append(f"{dimension} below threshold by {gap:.2f}")
        
        # Overall quality assessment
        if metrics.quality_score < 0.7:
            insights.append("Overall quality needs improvement")
        elif metrics.quality_score > 0.9:
            insights.append("Exceptional quality achieved")
        
        # User rating insights
        if metrics.user_rating and metrics.user_rating < 3:
            insights.append("Low user satisfaction detected")
        
        return insights

    def _check_quality_alerts(self, metrics: QualityMetrics) -> List[str]:
        """Check for quality alerts that require attention"""
        alerts = []
        
        # Critical quality failures
        if metrics.accuracy_score < 0.6:
            alerts.append("CRITICAL: Accuracy score below 60%")
        
        if metrics.quality_score < 0.5:
            alerts.append("CRITICAL: Overall quality score below 50%")
        
        # Warning level alerts
        if metrics.completeness_score < 0.7:
            alerts.append("WARNING: Incomplete documentation generated")
        
        if metrics.readability_score < 0.6:
            alerts.append("WARNING: Poor readability detected")
        
        # User feedback alerts
        if metrics.user_rating and metrics.user_rating <= 2:
            alerts.append("ALERT: Very low user rating received")
        
        return alerts

    def _update_quality_trends(self):
        """Update quality trend analysis with latest data"""
        if len(self._quality_history) < 5:
            return  # Need minimum data for trend analysis
        
        # Analyze trends for each quality dimension
        dimensions = [
            QualityDimension.READABILITY.value,
            QualityDimension.COMPLETENESS.value,
            QualityDimension.ACCURACY.value
        ]
        
        for dimension in dimensions:
            trend = self._calculate_dimension_trend(dimension)
            if trend:
                self._trend_cache[dimension] = trend
        
        # Update overall quality trend
        overall_trend = self._calculate_overall_quality_trend()
        if overall_trend:
            self._trend_cache['overall_quality'] = overall_trend

    def _calculate_dimension_trend(self, dimension: str) -> Optional[QualityTrend]:
        """Calculate trend for a specific quality dimension"""
        try:
            # Get recent metrics (last 30 entries or 30 days)
            recent_cutoff = datetime.now() - timedelta(days=30)
            recent_metrics = [
                m for m in self._quality_history[-30:]
                if m.timestamp and datetime.fromisoformat(m.timestamp) > recent_cutoff
            ]
            
            if len(recent_metrics) < 3:
                return None
            
            # Extract scores for dimension
            scores = []
            timestamps = []
            
            for metrics in recent_metrics:
                if dimension == QualityDimension.READABILITY.value:
                    score = metrics.readability_score
                elif dimension == QualityDimension.COMPLETENESS.value:
                    score = metrics.completeness_score
                elif dimension == QualityDimension.ACCURACY.value:
                    score = metrics.accuracy_score
                else:
                    continue
                
                scores.append(score)
                timestamps.append(datetime.fromisoformat(metrics.timestamp))
            
            if len(scores) < 3:
                return None
            
            # Calculate trend slope using linear regression
            slope = self._calculate_trend_slope(timestamps, scores)
            
            # Determine trend direction
            if abs(slope) < 0.01:
                trend_direction = 'stable'
            elif slope > 0:
                trend_direction = 'improving'
            else:
                trend_direction = 'declining'
            
            # Calculate confidence based on data consistency
            confidence = self._calculate_trend_confidence(scores, slope)
            
            # Current and target averages
            current_avg = statistics.mean(scores[-5:])  # Last 5 measurements
            target_avg = self.quality_thresholds.get(dimension, 0.8)
            
            return QualityTrend(
                dimension=dimension,
                trend_direction=trend_direction,
                slope=slope,
                confidence=confidence,
                sample_size=len(scores),
                time_span_days=(timestamps[-1] - timestamps[0]).days,
                current_average=current_avg,
                target_average=target_avg
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating trend for {dimension}: {e}")
            return None

    def _calculate_overall_quality_trend(self) -> Optional[QualityTrend]:
        """Calculate overall quality trend"""
        try:
            recent_cutoff = datetime.now() - timedelta(days=30)
            recent_metrics = [
                m for m in self._quality_history[-30:]
                if m.timestamp and datetime.fromisoformat(m.timestamp) > recent_cutoff
            ]
            
            if len(recent_metrics) < 3:
                return None
            
            scores = [m.quality_score for m in recent_metrics]
            timestamps = [datetime.fromisoformat(m.timestamp) for m in recent_metrics]
            
            slope = self._calculate_trend_slope(timestamps, scores)
            
            if abs(slope) < 0.01:
                trend_direction = 'stable'
            elif slope > 0:
                trend_direction = 'improving'
            else:
                trend_direction = 'declining'
            
            confidence = self._calculate_trend_confidence(scores, slope)
            
            return QualityTrend(
                dimension='overall_quality',
                trend_direction=trend_direction,
                slope=slope,
                confidence=confidence,
                sample_size=len(scores),
                time_span_days=(timestamps[-1] - timestamps[0]).days,
                current_average=statistics.mean(scores[-5:]),
                target_average=0.85
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating overall quality trend: {e}")
            return None

    def _calculate_trend_slope(self, timestamps: List[datetime], scores: List[float]) -> float:
        """Calculate linear regression slope for trend analysis"""
        if len(timestamps) != len(scores) or len(timestamps) < 2:
            return 0.0
        
        # Convert timestamps to numeric values (days since first timestamp)
        first_time = timestamps[0]
        x_values = [(ts - first_time).total_seconds() / 86400 for ts in timestamps]  # Days
        y_values = scores
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x_squared = sum(x * x for x in x_values)
        
        # Calculate slope using least squares formula
        denominator = n * sum_x_squared - sum_x * sum_x
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope

    def _calculate_trend_confidence(self, scores: List[float], slope: float) -> float:
        """Calculate confidence in trend analysis based on data variance"""
        if len(scores) < 3:
            return 0.0
        
        # Calculate R-squared for trend line fit
        mean_score = statistics.mean(scores)
        variance = statistics.variance(scores) if len(scores) > 1 else 0
        
        if variance == 0:
            return 1.0 if slope == 0 else 0.8
        
        # Simple confidence based on variance and sample size
        confidence = max(0.0, 1.0 - variance)
        confidence *= min(1.0, len(scores) / 10)  # Boost confidence with more data
        
        return confidence

    def _correlate_feedback_with_metrics(self, feedback: QualityFeedback):
        """Correlate user feedback with quantitative metrics"""
        # Find corresponding metrics
        matching_metrics = [
            m for m in self._quality_history
            if m.generation_id == feedback.generation_id
        ]
        
        if not matching_metrics:
            return
        
        metrics = matching_metrics[0]
        
        # Analyze correlation between user rating and quality score
        if feedback.overall_rating and metrics.quality_score:
            correlation_insight = self._analyze_rating_correlation(
                feedback.overall_rating,
                metrics.quality_score
            )
            if correlation_insight:
                self.logger.info(f"Rating correlation insight: {correlation_insight}")
        
        # Analyze dimension-specific correlations
        for dimension, user_rating in feedback.dimension_ratings.items():
            metric_score = self._get_metric_score_for_dimension(metrics, dimension)
            if metric_score:
                correlation = abs(user_rating - metric_score)
                if correlation > 0.3:
                    self.logger.warning(
                        f"Large correlation gap in {dimension}: "
                        f"user={user_rating:.2f}, metric={metric_score:.2f}"
                    )

    def _analyze_rating_correlation(self, user_rating: float, quality_score: float) -> Optional[str]:
        """Analyze correlation between user rating and quality metrics"""
        # Scale user rating to 0-1 if it's on different scale
        if user_rating > 1:
            user_rating = user_rating / 5.0  # Assume 1-5 scale
        
        correlation_gap = abs(user_rating - quality_score)
        
        if correlation_gap > 0.3:
            if user_rating > quality_score:
                return "Users rate higher than metrics suggest - review metric accuracy"
            else:
                return "Users rate lower than metrics suggest - investigate user experience issues"
        
        return None

    def _get_metric_score_for_dimension(self, metrics: QualityMetrics, dimension: str) -> Optional[float]:
        """Map quality dimension to corresponding metric score"""
        mapping = {
            QualityDimension.READABILITY.value: metrics.readability_score,
            QualityDimension.COMPLETENESS.value: metrics.completeness_score,
            QualityDimension.ACCURACY.value: metrics.accuracy_score
        }
        return mapping.get(dimension)

    def _extract_insights_from_text_feedback(self, feedback: QualityFeedback) -> List[str]:
        """Extract actionable insights from text feedback"""
        insights = []
        
        if feedback.text_feedback:
            text = feedback.text_feedback.lower()
            
            # Common feedback patterns
            if 'too long' in text or 'verbose' in text:
                insights.append("Users find documentation too lengthy")
            
            if 'confusing' in text or 'unclear' in text:
                insights.append("Clarity issues reported by users")
            
            if 'missing' in text or 'incomplete' in text:
                insights.append("Content gaps identified by users")
            
            if 'outdated' in text or 'wrong' in text:
                insights.append("Accuracy concerns raised by users")
        
        # Improvement suggestions analysis
        if feedback.improvement_suggestions:
            if len(feedback.improvement_suggestions) > 2:
                insights.append("Multiple improvement areas suggested")
        
        # Error reporting analysis
        if feedback.found_errors:
            insights.append(f"Users reported {len(feedback.found_errors)} errors")
        
        return insights

    def _update_recommendations_from_feedback(self, feedback: QualityFeedback):
        """Update improvement recommendations based on user feedback"""
        # Generate recommendations based on feedback patterns
        if feedback.overall_rating < 0.6:
            self._add_recommendation(
                "critical",
                "process",
                "Address low user satisfaction",
                0.8,
                0.9,
                [f"User rating: {feedback.overall_rating}"],
                "medium",
                QualityDimension.USEFULNESS.value
            )
        
        # Dimension-specific recommendations
        for dimension, rating in feedback.dimension_ratings.items():
            threshold = self.quality_thresholds.get(dimension, 0.75)
            if rating < threshold:
                self._add_recommendation(
                    "high" if rating < 0.5 else "medium",
                    "template",
                    f"Improve {dimension} in template design",
                    threshold - rating,
                    0.8,
                    [f"User rated {dimension}: {rating}"],
                    "medium",
                    dimension
                )
        
        # Content recommendations from text feedback
        if feedback.missing_content:
            self._add_recommendation(
                "high",
                "content",
                "Add missing content sections",
                0.6,
                0.85,
                [f"Missing: {', '.join(feedback.missing_content[:3])}"],
                "high",
                QualityDimension.COMPLETENESS.value
            )

    def _add_recommendation(
        self,
        priority: str,
        category: str,
        description: str,
        expected_impact: float,
        confidence: float,
        evidence: List[str],
        effort: str,
        target_dimension: str
    ):
        """Add improvement recommendation"""
        recommendation = ImprovementRecommendation(
            recommendation_id=f"rec_{len(self._recommendations_cache)}_{datetime.now().strftime('%Y%m%d%H%M')}",
            priority=priority,
            category=category,
            description=description,
            expected_impact=expected_impact,
            confidence=confidence,
            supporting_evidence=evidence,
            implementation_effort=effort,
            target_dimension=target_dimension
        )
        
        self._recommendations_cache.append(recommendation)
        
        # Keep only top 20 recommendations
        self._recommendations_cache.sort(
            key=lambda r: r.expected_impact * r.confidence,
            reverse=True
        )
        self._recommendations_cache = self._recommendations_cache[:20]

    def get_quality_insights(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive quality insights and recommendations
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Quality insights including trends and recommendations
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Filter recent data
        recent_metrics = [
            m for m in self._quality_history
            if m.timestamp and datetime.fromisoformat(m.timestamp) > cutoff
        ]
        
        recent_feedback = [
            f for f in self._feedback_history
            if datetime.fromisoformat(f.timestamp) > cutoff
        ]
        
        if not recent_metrics:
            return {"message": "No quality data available for analysis"}
        
        # Calculate current quality statistics
        quality_stats = self._calculate_quality_statistics(recent_metrics, recent_feedback)
        
        # Get trend analysis
        trends = dict(self._trend_cache)
        
        # Get top recommendations
        top_recommendations = sorted(
            self._recommendations_cache,
            key=lambda r: r.expected_impact * r.confidence,
            reverse=True
        )[:10]
        
        return {
            "analysis_period_days": days,
            "data_points": {
                "metrics": len(recent_metrics),
                "feedback": len(recent_feedback)
            },
            "quality_statistics": quality_stats,
            "trends": {k: asdict(v) for k, v in trends.items()},
            "recommendations": [asdict(r) for r in top_recommendations],
            "alerts": self._get_current_alerts(),
            "summary": self._generate_quality_summary(quality_stats, trends, top_recommendations)
        }

    def _calculate_quality_statistics(
        self,
        metrics: List[QualityMetrics],
        feedback: List[QualityFeedback]
    ) -> Dict[str, Any]:
        """Calculate quality statistics from recent data"""
        if not metrics:
            return {}
        
        # Quality score statistics
        quality_scores = [m.quality_score for m in metrics]
        readability_scores = [m.readability_score for m in metrics]
        completeness_scores = [m.completeness_score for m in metrics]
        accuracy_scores = [m.accuracy_score for m in metrics]
        
        # User rating statistics
        user_ratings = [f.overall_rating for f in feedback if f.overall_rating]
        
        return {
            "quality_scores": {
                "mean": statistics.mean(quality_scores),
                "median": statistics.median(quality_scores),
                "std_dev": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0,
                "min": min(quality_scores),
                "max": max(quality_scores)
            },
            "dimension_scores": {
                "readability": {
                    "mean": statistics.mean(readability_scores),
                    "below_threshold": len([s for s in readability_scores if s < 0.75])
                },
                "completeness": {
                    "mean": statistics.mean(completeness_scores),
                    "below_threshold": len([s for s in completeness_scores if s < 0.80])
                },
                "accuracy": {
                    "mean": statistics.mean(accuracy_scores),
                    "below_threshold": len([s for s in accuracy_scores if s < 0.90])
                }
            },
            "user_satisfaction": {
                "mean": statistics.mean(user_ratings) if user_ratings else None,
                "count": len(user_ratings),
                "satisfaction_rate": len([r for r in user_ratings if r > 0.7]) / len(user_ratings) if user_ratings else None
            },
            "improvement_areas": self._identify_improvement_areas(metrics, feedback)
        }

    def _identify_improvement_areas(
        self,
        metrics: List[QualityMetrics],
        feedback: List[QualityFeedback]
    ) -> List[str]:
        """Identify key areas needing improvement"""
        areas = []
        
        # Check metrics against thresholds
        avg_readability = statistics.mean([m.readability_score for m in metrics])
        avg_completeness = statistics.mean([m.completeness_score for m in metrics])
        avg_accuracy = statistics.mean([m.accuracy_score for m in metrics])
        
        if avg_readability < 0.75:
            areas.append("readability")
        if avg_completeness < 0.80:
            areas.append("completeness")
        if avg_accuracy < 0.90:
            areas.append("accuracy")
        
        # Check user feedback patterns
        if feedback:
            avg_user_rating = statistics.mean([f.overall_rating for f in feedback])
            if avg_user_rating < 0.7:
                areas.append("user_satisfaction")
        
        return areas

    def _get_current_alerts(self) -> List[str]:
        """Get current quality alerts"""
        alerts = []
        
        # Check recent trends
        for dimension, trend in self._trend_cache.items():
            if trend.trend_direction == 'declining' and trend.confidence > 0.7:
                alerts.append(f"Declining trend in {dimension}")
            
            if trend.current_average < trend.target_average * 0.8:
                alerts.append(f"{dimension} significantly below target")
        
        # Check recommendation priorities
        critical_recs = [r for r in self._recommendations_cache if r.priority == 'critical']
        if critical_recs:
            alerts.append(f"{len(critical_recs)} critical improvement recommendations")
        
        return alerts

    def _generate_quality_summary(
        self,
        stats: Dict[str, Any],
        trends: Dict[str, QualityTrend],
        recommendations: List[ImprovementRecommendation]
    ) -> str:
        """Generate human-readable quality summary"""
        if not stats:
            return "Insufficient data for quality analysis"
        
        quality_mean = stats.get('quality_scores', {}).get('mean', 0)
        
        # Overall assessment
        if quality_mean > 0.85:
            overall = "Excellent"
        elif quality_mean > 0.75:
            overall = "Good"
        elif quality_mean > 0.6:
            overall = "Needs Improvement"
        else:
            overall = "Poor"
        
        summary_parts = [f"Overall quality: {overall} ({quality_mean:.2f})"]
        
        # Trend summary
        improving_trends = [k for k, v in trends.items() if v.trend_direction == 'improving']
        declining_trends = [k for k, v in trends.items() if v.trend_direction == 'declining']
        
        if improving_trends:
            summary_parts.append(f"Improving: {', '.join(improving_trends[:2])}")
        if declining_trends:
            summary_parts.append(f"Declining: {', '.join(declining_trends[:2])}")
        
        # Recommendation summary
        high_priority_recs = [r for r in recommendations if r.priority in ['critical', 'high']]
        if high_priority_recs:
            summary_parts.append(f"{len(high_priority_recs)} high-priority improvements needed")
        
        return ". ".join(summary_parts)

    def _load_quality_history(self):
        """Load quality history from brain or cache"""
        # In full implementation, this would load from brain database
        self.logger.info("Quality history loaded")

    def export_quality_data(self, output_path: str) -> bool:
        """
        Export quality data for analysis or backup
        
        Args:
            output_path: Path to save quality data JSON
            
        Returns:
            True if successful
        """
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "quality_metrics": [asdict(m) for m in self._quality_history],
                "user_feedback": [asdict(f) for f in self._feedback_history],
                "trends": {k: asdict(v) for k, v in self._trend_cache.items()},
                "recommendations": [asdict(r) for r in self._recommendations_cache],
                "thresholds": self.quality_thresholds
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Quality data exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting quality data: {e}")
            return False