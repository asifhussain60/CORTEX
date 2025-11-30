"""
CORTEX Tier 3: Architecture Health History Manager

High-level interface for recording and analyzing architecture health over time.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
import statistics

from src.tier3.storage.architecture_health_store import (
    ArchitectureHealthStore,
    ArchitectureHealthSnapshot
)


class ArchitectureHealthHistory:
    """
    High-level interface for architecture health tracking and analysis.
    
    Features:
    - Record health snapshots
    - Analyze trends (improving/degrading/stable)
    - Calculate velocity and forecast
    - Generate recommendations
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize architecture health history manager.
        
        Args:
            db_path: Path to SQLite database (default: cortex-brain/tier3/context.db)
        """
        self.store = ArchitectureHealthStore(db_path)
    
    def record_health_snapshot(
        self,
        overall_score: float,
        layer_scores: Dict[str, int],
        feature_breakdown: Dict[str, int],
        recommendations: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Record a new health snapshot with automatic trend detection.
        
        Args:
            overall_score: Overall health score (0-100)
            layer_scores: Scores by layer {discovered: 20, imported: 20, ...}
            feature_breakdown: {total: 15, healthy: 10, warning: 3, critical: 2}
            recommendations: Top 3 recommendations
            metadata: Additional context
            
        Returns:
            ID of inserted record
        """
        # Detect trend based on historical data
        trend_direction = self._detect_trend(overall_score)
        
        # Calculate debt estimate
        debt_estimate_hours = self._estimate_debt_hours(
            overall_score,
            feature_breakdown.get("critical", 0),
            feature_breakdown.get("warning", 0)
        )
        
        snapshot = ArchitectureHealthSnapshot(
            timestamp=datetime.now().isoformat(),
            overall_score=overall_score,
            layer_scores=layer_scores,
            trend_direction=trend_direction,
            debt_estimate_hours=debt_estimate_hours,
            feature_count=feature_breakdown.get("total", 0),
            features_healthy=feature_breakdown.get("healthy", 0),
            features_warning=feature_breakdown.get("warning", 0),
            features_critical=feature_breakdown.get("critical", 0),
            recommendations=recommendations[:3],  # Top 3 only
            metadata=metadata or {}
        )
        
        return self.store.record_snapshot(snapshot)
    
    def get_latest_health(self) -> Optional[ArchitectureHealthSnapshot]:
        """
        Get most recent health snapshot.
        
        Returns:
            Latest snapshot or None
        """
        return self.store.get_latest_snapshot()
    
    def analyze_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze health trends over specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Trend analysis with direction, velocity, and insights
        """
        trend_data = self.store.get_trend_data(days)
        
        if len(trend_data) < 2:
            return {
                "trend": "insufficient_data",
                "velocity": 0.0,
                "direction": "unknown",
                "score_change": 0.0,
                "snapshots_analyzed": len(trend_data),
                "insights": ["Need at least 2 snapshots for trend analysis"]
            }
        
        # Calculate velocity (score change per day)
        first_score = trend_data[0]["overall_score"]
        last_score = trend_data[-1]["overall_score"]
        score_change = last_score - first_score
        
        first_date = datetime.fromisoformat(trend_data[0]["timestamp"])
        last_date = datetime.fromisoformat(trend_data[-1]["timestamp"])
        days_elapsed = (last_date - first_date).days or 1  # Avoid division by zero
        
        velocity = score_change / days_elapsed
        
        # Determine trend direction
        if abs(velocity) < 0.1:  # Less than 0.1 points per day
            direction = "stable"
        elif velocity > 0:
            direction = "improving"
        else:
            direction = "degrading"
        
        # Calculate volatility
        scores = [d["overall_score"] for d in trend_data]
        volatility = statistics.stdev(scores) if len(scores) > 1 else 0.0
        
        # Generate insights
        insights = self._generate_trend_insights(
            direction, velocity, score_change, volatility, last_score
        )
        
        return {
            "trend": direction,
            "velocity": round(velocity, 3),
            "direction": direction,
            "score_change": round(score_change, 2),
            "volatility": round(volatility, 2),
            "current_score": round(last_score, 2),
            "snapshots_analyzed": len(trend_data),
            "period_days": days,
            "insights": insights
        }
    
    def forecast_health(self, months: int = 3) -> Dict[str, Any]:
        """
        Forecast future health based on current trends.
        
        Args:
            months: Number of months to forecast (default: 3)
            
        Returns:
            Forecast data with predicted score and confidence
        """
        # Get recent trend (last 30 days)
        trend_analysis = self.analyze_trends(days=30)
        
        if trend_analysis["trend"] == "insufficient_data":
            return {
                "forecast_available": False,
                "reason": "Insufficient historical data",
                "recommendation": "Record more health snapshots over time"
            }
        
        velocity = trend_analysis["velocity"]
        current_score = trend_analysis["current_score"]
        volatility = trend_analysis["volatility"]
        
        # Forecast future score
        days_ahead = months * 30
        predicted_change = velocity * days_ahead
        predicted_score = max(0, min(100, current_score + predicted_change))
        
        # Calculate confidence (lower volatility = higher confidence)
        confidence = max(0, min(100, 100 - (volatility * 10)))
        
        # Determine if intervention needed
        intervention_needed = predicted_score < 70
        
        return {
            "forecast_available": True,
            "months_ahead": months,
            "current_score": round(current_score, 2),
            "predicted_score": round(predicted_score, 2),
            "predicted_change": round(predicted_change, 2),
            "confidence_percentage": round(confidence, 2),
            "velocity_per_day": round(velocity, 3),
            "intervention_needed": intervention_needed,
            "forecast_date": (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d"),
            "warning": "Critical health level predicted" if predicted_score < 70 else None
        }
    
    def get_health_statistics(self) -> Dict[str, Any]:
        """
        Get aggregate statistics across all history.
        
        Returns:
            Statistics dictionary
        """
        return self.store.get_statistics()
    
    def _detect_trend(self, current_score: float) -> str:
        """
        Detect trend direction based on recent history.
        
        Args:
            current_score: Current overall score
            
        Returns:
            "improving", "degrading", or "stable"
        """
        recent_data = self.store.get_trend_data(days=7)
        
        if len(recent_data) < 2:
            return "stable"
        
        # Compare current score to recent average
        recent_scores = [d["overall_score"] for d in recent_data]
        recent_avg = statistics.mean(recent_scores)
        
        diff = current_score - recent_avg
        
        if diff > 2:
            return "improving"
        elif diff < -2:
            return "degrading"
        else:
            return "stable"
    
    def _estimate_debt_hours(
        self,
        overall_score: float,
        critical_count: int,
        warning_count: int
    ) -> float:
        """
        Estimate hours needed to reach 90% health.
        
        Args:
            overall_score: Current score
            critical_count: Number of critical features
            warning_count: Number of warning features
            
        Returns:
            Estimated hours
        """
        if overall_score >= 90:
            return 0.0
        
        # Base calculation: gap to 90% * base multiplier
        gap = 90 - overall_score
        base_hours = gap * 0.5  # 0.5 hours per percentage point
        
        # Add complexity for critical/warning features
        critical_penalty = critical_count * 4  # 4 hours per critical feature
        warning_penalty = warning_count * 1   # 1 hour per warning feature
        
        total_hours = base_hours + critical_penalty + warning_penalty
        
        return round(total_hours, 2)
    
    def _generate_trend_insights(
        self,
        direction: str,
        velocity: float,
        score_change: float,
        volatility: float,
        current_score: float
    ) -> List[str]:
        """Generate human-readable trend insights."""
        insights = []
        
        # Direction insights
        if direction == "improving":
            insights.append(f"✅ Architecture health improving at {abs(velocity):.2f} points/day")
        elif direction == "degrading":
            insights.append(f"⚠️ Architecture health declining at {abs(velocity):.2f} points/day")
        else:
            insights.append("➡️ Architecture health stable")
        
        # Score change insights
        if abs(score_change) > 10:
            insights.append(f"Significant change: {score_change:+.1f} points over period")
        
        # Volatility insights
        if volatility > 5:
            insights.append("⚠️ High volatility detected - health fluctuating significantly")
        
        # Current status insights
        if current_score >= 90:
            insights.append("✅ Health excellent - maintain current practices")
        elif current_score >= 70:
            insights.append("⚠️ Health acceptable - minor improvements recommended")
        else:
            insights.append("🚨 Health critical - immediate action required")
        
        return insights
