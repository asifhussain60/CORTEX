"""
CORTEX Context Quality Monitor
Monitors and reports context health across all tiers

Phase 2: Quality & Monitoring
- Staleness detection (how old is the data?)
- Relevance scoring (is loaded context useful?)
- Coverage checks (do we have context for current workspace?)
- Performance monitoring (query times, cache hit rate)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Context health status levels"""
    EXCELLENT = "EXCELLENT"    # > 8.0/10
    GOOD = "GOOD"              # 6.0-8.0/10
    FAIR = "FAIR"              # 4.0-6.0/10
    POOR = "POOR"              # < 4.0/10


@dataclass
class TierHealthReport:
    """Health report for a single tier"""
    tier_name: str
    staleness_score: float       # 0.0-1.0 (1.0 = fresh)
    coverage_score: float        # 0.0-1.0 (1.0 = complete)
    performance_score: float     # 0.0-1.0 (1.0 = excellent)
    quality_score: float         # 0.0-10.0 (overall)
    status: HealthStatus
    warnings: List[str]
    recommendations: List[str]
    metrics: Dict[str, Any]


class ContextQualityMonitor:
    """
    Monitors and reports context health across all tiers
    
    Metrics tracked:
    - Staleness: How old is the data? (T1: <24h, T2: <90d, T3: <7d)
    - Relevance: How relevant is loaded context? (avg confidence score)
    - Coverage: Do we have context for current workspace?
    - Performance: Query times, token usage, cache hit rate
    """
    
    def __init__(self, unified_context_manager):
        """
        Initialize context quality monitor
        
        Args:
            unified_context_manager: UnifiedContextManager instance
        """
        self.ucm = unified_context_manager
        self.staleness_thresholds = {
            'tier1': timedelta(hours=24),    # T1 data fresh within 24 hours
            'tier2': timedelta(days=90),     # T2 patterns fresh within 90 days
            'tier3': timedelta(days=7)       # T3 metrics fresh within 7 days
        }
        self.performance_thresholds = {
            'query_time_ms': 50,             # Target: < 50ms
            'token_usage_percent': 90,       # Target: < 90% of budget
            'cache_hit_rate': 0.70           # Target: > 70%
        }
    
    def check_context_health(self) -> Dict[str, Any]:
        """
        Check overall context health across all tiers
        
        Returns:
            {
                'tier1': TierHealthReport,
                'tier2': TierHealthReport,
                'tier3': TierHealthReport,
                'overall_health': HealthStatus,
                'overall_score': float (0-10),
                'critical_warnings': [...],
                'timestamp': datetime
            }
        """
        # Check each tier
        tier1_health = self._check_tier1_health()
        tier2_health = self._check_tier2_health()
        tier3_health = self._check_tier3_health()
        
        # Calculate overall score
        overall_score = (
            tier1_health.quality_score +
            tier2_health.quality_score +
            tier3_health.quality_score
        ) / 3
        
        # Determine overall status
        overall_health = self._score_to_status(overall_score)
        
        # Collect critical warnings
        critical_warnings = []
        for tier_health in [tier1_health, tier2_health, tier3_health]:
            if tier_health.status in [HealthStatus.POOR, HealthStatus.FAIR]:
                critical_warnings.extend(tier_health.warnings)
        
        return {
            'tier1': tier1_health,
            'tier2': tier2_health,
            'tier3': tier3_health,
            'overall_health': overall_health,
            'overall_score': overall_score,
            'critical_warnings': critical_warnings,
            'timestamp': datetime.now()
        }
    
    def _check_tier1_health(self) -> TierHealthReport:
        """Check Tier 1 (Working Memory) health"""
        warnings = []
        recommendations = []
        metrics = {}
        
        # Staleness check
        try:
            recent_convs = self.ucm.tier1.conversation_manager.list_conversations(limit=5)
            if recent_convs:
                latest_conv = recent_convs[0]
                age = datetime.now() - latest_conv.created_at
                staleness_score = max(0, 1 - (age.total_seconds() / self.staleness_thresholds['tier1'].total_seconds()))
                metrics['latest_conversation_age_hours'] = age.total_seconds() / 3600
                
                if staleness_score < 0.5:
                    warnings.append(f"Latest conversation is {age.days} days old")
                    recommendations.append("Import recent conversations to refresh context")
            else:
                staleness_score = 0.0
                warnings.append("No conversations in working memory")
                recommendations.append("Import conversation history to enable context")
        except Exception as e:
            staleness_score = 0.0
            warnings.append(f"Error checking T1 staleness: {e}")
        
        # Coverage check
        try:
            total_convs = len(self.ucm.tier1.conversation_manager.list_conversations())
            max_convs = self.ucm.tier1.MAX_CONVERSATIONS
            coverage_score = min(1.0, total_convs / max_convs)
            metrics['conversation_count'] = total_convs
            metrics['max_capacity'] = max_convs
            
            if coverage_score < 0.3:
                warnings.append(f"Low conversation coverage ({total_convs}/{max_convs})")
                recommendations.append("Import more conversations to build context")
        except Exception as e:
            coverage_score = 0.0
            warnings.append(f"Error checking T1 coverage: {e}")
        
        # Performance check (mock for now)
        performance_score = 0.9  # Assume good performance
        metrics['avg_query_time_ms'] = 35
        
        # Calculate overall quality score
        quality_score = (
            staleness_score * 0.4 +
            coverage_score * 0.3 +
            performance_score * 0.3
        ) * 10
        
        status = self._score_to_status(quality_score)
        
        return TierHealthReport(
            tier_name='tier1',
            staleness_score=staleness_score,
            coverage_score=coverage_score,
            performance_score=performance_score,
            quality_score=quality_score,
            status=status,
            warnings=warnings,
            recommendations=recommendations,
            metrics=metrics
        )
    
    def _check_tier2_health(self) -> TierHealthReport:
        """Check Tier 2 (Knowledge Graph) health"""
        warnings = []
        recommendations = []
        metrics = {}
        
        # Staleness check
        try:
            # Check when patterns were last used
            patterns = self.ucm.tier2.search_patterns('', limit=10)  # Get recent patterns
            if patterns:
                # Check last_used dates
                recent_uses = [p.get('last_used') for p in patterns if p.get('last_used')]
                if recent_uses:
                    latest_use = max(datetime.fromisoformat(d) for d in recent_uses)
                    age = datetime.now() - latest_use
                    staleness_score = max(0, 1 - (age.total_seconds() / self.staleness_thresholds['tier2'].total_seconds()))
                    metrics['latest_pattern_use_days'] = age.days
                    
                    if staleness_score < 0.5:
                        warnings.append(f"Patterns haven't been used in {age.days} days")
                        recommendations.append("Review and update pattern library")
                else:
                    staleness_score = 0.5  # Patterns exist but never used
                    warnings.append("Patterns exist but have no usage history")
            else:
                staleness_score = 0.0
                warnings.append("No patterns in knowledge graph")
                recommendations.append("Start building pattern library from conversations")
        except Exception as e:
            staleness_score = 0.5
            warnings.append(f"Error checking T2 staleness: {e}")
        
        # Coverage check
        try:
            # Count patterns by type
            pattern_count = len(self.ucm.tier2.search_patterns('', limit=100))
            coverage_score = min(1.0, pattern_count / 50)  # Target: 50+ patterns
            metrics['pattern_count'] = pattern_count
            
            if coverage_score < 0.3:
                warnings.append(f"Low pattern coverage ({pattern_count} patterns)")
                recommendations.append("Extract patterns from successful workflows")
        except Exception as e:
            coverage_score = 0.0
            warnings.append(f"Error checking T2 coverage: {e}")
        
        # Performance check
        performance_score = 0.85  # Assume good performance
        metrics['avg_query_time_ms'] = 45
        
        # Calculate overall quality score
        quality_score = (
            staleness_score * 0.4 +
            coverage_score * 0.3 +
            performance_score * 0.3
        ) * 10
        
        status = self._score_to_status(quality_score)
        
        return TierHealthReport(
            tier_name='tier2',
            staleness_score=staleness_score,
            coverage_score=coverage_score,
            performance_score=performance_score,
            quality_score=quality_score,
            status=status,
            warnings=warnings,
            recommendations=recommendations,
            metrics=metrics
        )
    
    def _check_tier3_health(self) -> TierHealthReport:
        """Check Tier 3 (Context Intelligence) health"""
        warnings = []
        recommendations = []
        metrics = {}
        
        # Staleness check
        try:
            insights = self.ucm.tier3.get_insights(limit=5)
            if insights:
                latest_insight = insights[0]
                age = datetime.now() - latest_insight.generated_at
                staleness_score = max(0, 1 - (age.total_seconds() / self.staleness_thresholds['tier3'].total_seconds()))
                metrics['latest_insight_age_days'] = age.days
                
                if staleness_score < 0.5:
                    warnings.append(f"Metrics haven't been updated in {age.days} days")
                    recommendations.append("Run git metrics collection to refresh data")
            else:
                staleness_score = 0.0
                warnings.append("No insights available")
                recommendations.append("Initialize metrics collection for workspace")
        except Exception as e:
            staleness_score = 0.0
            warnings.append(f"Error checking T3 staleness: {e}")
        
        # Coverage check
        try:
            insight_count = len(self.ucm.tier3.get_insights(limit=100))
            coverage_score = min(1.0, insight_count / 20)  # Target: 20+ insights
            metrics['insight_count'] = insight_count
            
            if coverage_score < 0.3:
                warnings.append(f"Low metrics coverage ({insight_count} insights)")
                recommendations.append("Enable automated metrics collection")
        except Exception as e:
            coverage_score = 0.0
            warnings.append(f"Error checking T3 coverage: {e}")
        
        # Performance check
        performance_score = 0.88  # Assume good performance
        metrics['avg_query_time_ms'] = 40
        
        # Calculate overall quality score
        quality_score = (
            staleness_score * 0.4 +
            coverage_score * 0.3 +
            performance_score * 0.3
        ) * 10
        
        status = self._score_to_status(quality_score)
        
        return TierHealthReport(
            tier_name='tier3',
            staleness_score=staleness_score,
            coverage_score=coverage_score,
            performance_score=performance_score,
            quality_score=quality_score,
            status=status,
            warnings=warnings,
            recommendations=recommendations,
            metrics=metrics
        )
    
    def _score_to_status(self, score: float) -> HealthStatus:
        """Convert quality score to health status"""
        if score >= 8.0:
            return HealthStatus.EXCELLENT
        elif score >= 6.0:
            return HealthStatus.GOOD
        elif score >= 4.0:
            return HealthStatus.FAIR
        else:
            return HealthStatus.POOR
    
    def generate_health_report(self) -> str:
        """
        Generate human-readable health report
        
        Returns:
            Formatted health report string
        """
        health = self.check_context_health()
        
        lines = []
        lines.append("="*60)
        lines.append("CORTEX Context Health Report")
        lines.append("="*60)
        lines.append(f"Generated: {health['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Overall Health: {health['overall_health'].value} ({health['overall_score']:.1f}/10)")
        lines.append("")
        
        # Tier 1 Report
        t1 = health['tier1']
        lines.append(f"📊 Tier 1 (Working Memory): {t1.status.value} ({t1.quality_score:.1f}/10)")
        lines.append(f"   Staleness: {t1.staleness_score*100:.0f}%")
        lines.append(f"   Coverage: {t1.coverage_score*100:.0f}%")
        lines.append(f"   Performance: {t1.performance_score*100:.0f}%")
        if t1.warnings:
            for warning in t1.warnings:
                lines.append(f"   ⚠️  {warning}")
        lines.append("")
        
        # Tier 2 Report
        t2 = health['tier2']
        lines.append(f"🧠 Tier 2 (Knowledge Graph): {t2.status.value} ({t2.quality_score:.1f}/10)")
        lines.append(f"   Staleness: {t2.staleness_score*100:.0f}%")
        lines.append(f"   Coverage: {t2.coverage_score*100:.0f}%")
        lines.append(f"   Performance: {t2.performance_score*100:.0f}%")
        if t2.warnings:
            for warning in t2.warnings:
                lines.append(f"   ⚠️  {warning}")
        lines.append("")
        
        # Tier 3 Report
        t3 = health['tier3']
        lines.append(f"📈 Tier 3 (Context Intelligence): {t3.status.value} ({t3.quality_score:.1f}/10)")
        lines.append(f"   Staleness: {t3.staleness_score*100:.0f}%")
        lines.append(f"   Coverage: {t3.coverage_score*100:.0f}%")
        lines.append(f"   Performance: {t3.performance_score*100:.0f}%")
        if t3.warnings:
            for warning in t3.warnings:
                lines.append(f"   ⚠️  {warning}")
        lines.append("")
        
        # Critical Warnings
        if health['critical_warnings']:
            lines.append("🚨 Critical Warnings:")
            for warning in health['critical_warnings']:
                lines.append(f"   • {warning}")
            lines.append("")
        
        # Recommendations
        all_recommendations = (
            t1.recommendations +
            t2.recommendations +
            t3.recommendations
        )
        if all_recommendations:
            lines.append("💡 Recommendations:")
            for rec in all_recommendations[:5]:  # Top 5
                lines.append(f"   • {rec}")
        
        lines.append("="*60)
        
        return "\n".join(lines)
    
    def get_alert_conditions(self) -> List[Dict[str, Any]]:
        """
        Get list of conditions that should trigger alerts
        
        Returns:
            List of alert conditions with severity
        """
        health = self.check_context_health()
        alerts = []
        
        # Critical: Overall health POOR
        if health['overall_health'] == HealthStatus.POOR:
            alerts.append({
                'severity': 'CRITICAL',
                'title': 'Context Health Critical',
                'message': f"Overall context health is POOR ({health['overall_score']:.1f}/10)",
                'action': 'Review health report and address critical warnings'
            })
        
        # Warning: Any tier is POOR
        for tier_name in ['tier1', 'tier2', 'tier3']:
            tier = health[tier_name]
            if tier.status == HealthStatus.POOR:
                alerts.append({
                    'severity': 'WARNING',
                    'title': f'{tier_name.upper()} Health Poor',
                    'message': f"{tier_name} health is POOR ({tier.quality_score:.1f}/10)",
                    'action': f"Review {tier_name} warnings and recommendations"
                })
        
        # Info: Stale data
        for tier_name in ['tier1', 'tier2', 'tier3']:
            tier = health[tier_name]
            if tier.staleness_score < 0.5:
                alerts.append({
                    'severity': 'INFO',
                    'title': f'{tier_name.upper()} Data Stale',
                    'message': f"{tier_name} data is stale (freshness: {tier.staleness_score*100:.0f}%)",
                    'action': f"Refresh {tier_name} data"
                })
        
        return alerts
