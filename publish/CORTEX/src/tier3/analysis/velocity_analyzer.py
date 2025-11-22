"""
CORTEX Tier 3: Velocity Analysis
Analyzes commit velocity trends and detects productivity patterns.
"""

from datetime import datetime, timedelta, date
from typing import Dict, Any, List
from pathlib import Path

from ..metrics.git_metrics import GitMetric, GitMetricsCollector


class VelocityAnalyzer:
    """
    Analyzes commit velocity trends and productivity patterns.
    
    Features:
    - Commit velocity calculation
    - Trend analysis (increasing/stable/declining)
    - Productivity pattern detection
    - Historical comparisons
    """
    
    # Thresholds
    VELOCITY_DROP_THRESHOLD = 0.30   # >30% drop = warning
    VELOCITY_INCREASE_THRESHOLD = 0.30  # >30% increase = notable
    
    def __init__(self, git_collector: GitMetricsCollector):
        """
        Initialize analyzer.
        
        Args:
            git_collector: GitMetricsCollector instance
        """
        self.git_collector = git_collector
    
    def calculate_velocity(self, window_days: int = 7) -> Dict[str, Any]:
        """
        Calculate commit velocity trends.
        
        Args:
            window_days: Number of days per window
            
        Returns:
            Dictionary with velocity metrics and trend analysis
        """
        metrics = self.git_collector.get_metrics(days=window_days * 4)  # 4 windows
        
        if not metrics:
            return {
                'current_velocity': 0,
                'previous_velocity': 0,
                'trend': 'unknown',
                'change_percent': 0,
                'window_days': window_days
            }
        
        # Group by window
        current_window = []
        previous_window = []
        cutoff_date = (datetime.now() - timedelta(days=window_days)).date()
        
        for metric in metrics:
            if metric.metric_date >= cutoff_date:
                current_window.append(metric)
            else:
                previous_window.append(metric)
        
        # Calculate velocities
        current_velocity = sum(m.commits_count for m in current_window)
        previous_velocity = sum(m.commits_count for m in previous_window)
        
        # Determine trend
        if previous_velocity == 0:
            trend = 'stable'
            change_percent = 0
        else:
            change_percent = ((current_velocity - previous_velocity) / previous_velocity) * 100
            
            if change_percent < -self.VELOCITY_DROP_THRESHOLD * 100:
                trend = 'declining'
            elif change_percent > self.VELOCITY_INCREASE_THRESHOLD * 100:
                trend = 'increasing'
            else:
                trend = 'stable'
        
        return {
            'current_velocity': current_velocity,
            'previous_velocity': previous_velocity,
            'trend': trend,
            'change_percent': change_percent,
            'window_days': window_days
        }
    
    def get_productivity_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get productivity summary for a period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with productivity metrics
        """
        metrics = self.git_collector.get_metrics(days=days)
        
        if not metrics:
            return {
                'total_commits': 0,
                'total_lines_added': 0,
                'total_lines_deleted': 0,
                'net_growth': 0,
                'files_changed': 0,
                'avg_commits_per_day': 0.0,
                'avg_lines_per_commit': 0.0
            }
        
        total_commits = sum(m.commits_count for m in metrics)
        total_lines_added = sum(m.lines_added for m in metrics)
        total_lines_deleted = sum(m.lines_deleted for m in metrics)
        net_growth = sum(m.net_growth for m in metrics)
        files_changed = sum(m.files_changed for m in metrics)
        
        # Calculate averages
        active_days = len(set(m.metric_date for m in metrics))
        avg_commits_per_day = total_commits / active_days if active_days > 0 else 0
        avg_lines_per_commit = (total_lines_added + total_lines_deleted) / total_commits if total_commits > 0 else 0
        
        return {
            'total_commits': total_commits,
            'total_lines_added': total_lines_added,
            'total_lines_deleted': total_lines_deleted,
            'net_growth': net_growth,
            'files_changed': files_changed,
            'active_days': active_days,
            'avg_commits_per_day': round(avg_commits_per_day, 2),
            'avg_lines_per_commit': round(avg_lines_per_commit, 2)
        }
    
    def get_daily_breakdown(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get daily breakdown of commits.
        
        Args:
            days: Number of days to include
            
        Returns:
            List of dictionaries with daily metrics
        """
        metrics = self.git_collector.get_metrics(days=days)
        
        breakdown = []
        for metric in metrics:
            breakdown.append({
                'date': metric.metric_date.isoformat(),
                'commits': metric.commits_count,
                'lines_added': metric.lines_added,
                'lines_deleted': metric.lines_deleted,
                'net_growth': metric.net_growth,
                'files_changed': metric.files_changed
            })
        
        return breakdown
