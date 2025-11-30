"""
CORTEX Tier 3: Insight Generation
Generates actionable insights from collected metrics.
"""

from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum

from ..metrics.file_metrics import FileMetricsAnalyzer
from .velocity_analyzer import VelocityAnalyzer


class InsightType(Enum):
    """Types of insights that can be generated."""
    VELOCITY_DROP = "velocity_drop"
    FILE_HOTSPOT = "file_hotspot"
    FLAKY_TEST = "flaky_test"
    BUILD_HEALTH = "build_health"
    TEST_COVERAGE = "test_coverage"
    PRODUCTIVITY_TIME = "productivity_time"
    SESSION_DURATION = "session_duration"
    CORRELATION_DISCOVERY = "correlation_discovery"


class Severity(Enum):
    """Severity levels for insights."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class Insight:
    """Generated insights and recommendations."""
    insight_type: InsightType
    severity: Severity
    title: str
    description: str
    recommendation: Optional[str] = None
    related_entity: Optional[str] = None
    data_snapshot: Optional[Dict[str, Any]] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    dismissed: bool = False
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class InsightGenerator:
    """
    Generates insights from metrics.
    
    Features:
    - Velocity drop detection
    - File hotspot identification
    - Productivity pattern analysis
    - Actionable recommendations
    """
    
    # Thresholds
    HIGH_CHURN_THRESHOLD = 0.3  # >30% churn rate
    
    def __init__(self,
                velocity_analyzer: VelocityAnalyzer,
                file_analyzer: FileMetricsAnalyzer):
        """
        Initialize generator.
        
        Args:
            velocity_analyzer: VelocityAnalyzer instance
            file_analyzer: FileMetricsAnalyzer instance
        """
        self.velocity_analyzer = velocity_analyzer
        self.file_analyzer = file_analyzer
    
    def generate_insights(self) -> List[Insight]:
        """
        Generate insights from collected metrics.
        
        Returns:
            List of Insight objects
        """
        insights = []
        
        # Check velocity trends
        velocity = self.velocity_analyzer.calculate_velocity()
        if velocity['trend'] == 'declining':
            insights.append(Insight(
                insight_type=InsightType.VELOCITY_DROP,
                severity=Severity.WARNING,
                title=f"Commit velocity decreased {abs(velocity['change_percent']):.1f}%",
                description=f"Your commit rate has dropped from {velocity['previous_velocity']} "
                           f"to {velocity['current_velocity']} commits in the last "
                           f"{velocity['window_days']} days.",
                recommendation="Consider breaking work into smaller, more frequent commits "
                              "for better progress tracking.",
                data_snapshot=velocity
            ))
        
        # Check for unstable files
        unstable_files = self.file_analyzer.get_unstable_files(limit=5)
        for hotspot in unstable_files:
            if hotspot.churn_rate > self.HIGH_CHURN_THRESHOLD:
                insights.append(Insight(
                    insight_type=InsightType.FILE_HOTSPOT,
                    severity=Severity.WARNING,
                    title=f"High churn detected: {Path(hotspot.file_path).name}",
                    description=f"File {hotspot.file_path} has been modified in "
                               f"{hotspot.file_edits} of {hotspot.total_commits} commits "
                               f"({hotspot.churn_rate*100:.1f}% churn rate).",
                    recommendation="Consider refactoring this file to improve stability, "
                                  "or splitting it into smaller, more focused modules.",
                    related_entity=hotspot.file_path,
                    data_snapshot={
                        'churn_rate': hotspot.churn_rate,
                        'file_edits': hotspot.file_edits,
                        'total_commits': hotspot.total_commits
                    }
                ))
        
        return insights
    
    def get_productivity_insights(self, days: int = 30) -> List[Insight]:
        """
        Generate productivity-focused insights.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of Insight objects focused on productivity
        """
        insights = []
        
        # Get productivity summary
        summary = self.velocity_analyzer.get_productivity_summary(days=days)
        
        # Check if productivity is low
        if summary['avg_commits_per_day'] < 1.0:
            insights.append(Insight(
                insight_type=InsightType.PRODUCTIVITY_TIME,
                severity=Severity.INFO,
                title="Low commit frequency detected",
                description=f"Average of {summary['avg_commits_per_day']:.1f} commits per day "
                           f"over the last {days} days.",
                recommendation="Consider committing more frequently to improve progress tracking "
                              "and reduce risk of losing work.",
                data_snapshot=summary
            ))
        
        # Check for large commits
        if summary['avg_lines_per_commit'] > 500:
            insights.append(Insight(
                insight_type=InsightType.PRODUCTIVITY_TIME,
                severity=Severity.WARNING,
                title="Large commits detected",
                description=f"Average of {summary['avg_lines_per_commit']:.0f} lines per commit, "
                           f"which is higher than recommended.",
                recommendation="Consider breaking changes into smaller, atomic commits "
                              "for easier code review and debugging.",
                data_snapshot=summary
            ))
        
        return insights
    
    def get_file_health_insights(self) -> List[Insight]:
        """
        Generate file health insights.
        
        Returns:
            List of Insight objects focused on file health
        """
        insights = []
        
        # Get all unstable files
        unstable_files = self.file_analyzer.get_unstable_files(limit=10)
        
        if len(unstable_files) > 5:
            insights.append(Insight(
                insight_type=InsightType.FILE_HOTSPOT,
                severity=Severity.WARNING,
                title=f"{len(unstable_files)} unstable files detected",
                description=f"Multiple files show high churn rates, indicating potential "
                           f"architectural or design issues.",
                recommendation="Review the most unstable files and consider refactoring "
                              "to improve code stability and maintainability.",
                data_snapshot={
                    'unstable_count': len(unstable_files),
                    'top_files': [
                        {
                            'path': f.file_path,
                            'churn_rate': f.churn_rate
                        }
                        for f in unstable_files[:3]
                    ]
                }
            ))
        
        return insights
