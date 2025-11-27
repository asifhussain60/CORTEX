"""
Application Prioritization Engine for CORTEX

Aggregates multiple activity signals to intelligently prioritize applications for context loading.
Combines filesystem activity, git history, and access patterns into unified scoring system.

Features:
- Multi-signal aggregation (filesystem + git + access patterns)
- Weighted scoring algorithm
- Dynamic threshold adjustment
- Top-N selection for immediate loading
- Lazy loading queue for remaining apps

Performance Target: <200ms for 20 applications

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .filesystem_activity_monitor import FileSystemActivityMonitor, ApplicationActivity
from .git_history_analyzer import GitHistoryAnalyzer, ApplicationGitActivity
from .access_pattern_tracker import AccessPatternTracker, ApplicationAccessPattern

logger = logging.getLogger(__name__)


@dataclass
class ApplicationPriority:
    """Unified priority information for an application"""
    name: str
    path: str
    
    # Individual signal scores
    filesystem_score: float = 0.0
    git_score: float = 0.0
    access_score: float = 0.0
    dependency_score: float = 0.0
    
    # Unified score
    total_score: float = 0.0
    normalized_score: float = 0.0  # 0-100 scale
    
    # Priority tier
    tier: str = 'background'  # 'immediate', 'queued', 'background'
    
    # Supporting data
    filesystem_activity: Optional[ApplicationActivity] = None
    git_activity: Optional[ApplicationGitActivity] = None
    access_pattern: Optional[ApplicationAccessPattern] = None
    
    # Metadata
    last_activity: Optional[datetime] = None
    priority_rank: int = 0


class ApplicationPrioritizationEngine:
    """
    Intelligently prioritizes applications for context loading.
    
    Signal Weights:
    - Filesystem Activity: 40% (most recent indicator)
    - Git History: 30% (development activity)
    - Access Patterns: 20% (workflow patterns)
    - Dependencies: 10% (shared libraries, cross-app links)
    
    Priority Tiers:
    - Immediate: Top 2-3 apps (load immediately)
    - Queued: Next 3-5 apps (pre-warm cache)
    - Background: Remaining apps (lazy load on demand)
    
    Scoring Formula:
    total_score = (filesystem * 0.4) + (git * 0.3) + (access * 0.2) + (dependency * 0.1)
    normalized_score = (total_score / max_score) * 100
    """
    
    # Signal weights
    FILESYSTEM_WEIGHT = 0.40
    GIT_WEIGHT = 0.30
    ACCESS_WEIGHT = 0.20
    DEPENDENCY_WEIGHT = 0.10
    
    # Priority tier thresholds (normalized score)
    IMMEDIATE_THRESHOLD = 60.0  # Top priority
    QUEUED_THRESHOLD = 30.0     # Medium priority
    
    # Tier sizes
    IMMEDIATE_COUNT = 3  # Load top 3 apps immediately
    QUEUED_COUNT = 5     # Pre-warm next 5 apps
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize prioritization engine.
        
        Args:
            config: Configuration dictionary with:
                - workspace_path: Path to workspace root
                - applications: List of discovered applications
                - immediate_count: Number of apps to load immediately (default: 3)
                - queued_count: Number of apps to queue (default: 5)
        """
        self.workspace_path = config['workspace_path']
        self.applications = config['applications']
        self.immediate_count = config.get('immediate_count', self.IMMEDIATE_COUNT)
        self.queued_count = config.get('queued_count', self.QUEUED_COUNT)
        
        # Initialize activity monitors
        self.fs_monitor = FileSystemActivityMonitor(config)
        self.git_analyzer = GitHistoryAnalyzer(config)
        self.access_tracker = AccessPatternTracker(config)
        
        logger.info(f"Initialized Application Prioritization Engine")
        logger.info(f"Immediate tier: {self.immediate_count} apps, Queued tier: {self.queued_count} apps")
    
    def prioritize_applications(self) -> List[ApplicationPriority]:
        """
        Analyze all applications and calculate priority scores.
        
        Returns:
            List of ApplicationPriority sorted by score (descending)
        """
        logger.info("Starting application prioritization...")
        
        # Collect activity signals from all sources
        fs_activity = self.fs_monitor.scan_workspace_activity()
        git_activity = self.git_analyzer.analyze_git_activity()
        access_patterns = self.access_tracker.track_access_patterns()
        
        # Build unified priority data
        priorities = self._build_priorities(fs_activity, git_activity, access_patterns)
        
        # Calculate composite scores
        self._calculate_composite_scores(priorities)
        
        # Normalize scores to 0-100 scale
        self._normalize_scores(priorities)
        
        # Assign priority tiers
        self._assign_priority_tiers(priorities)
        
        # Sort by score
        priorities.sort(key=lambda x: x.total_score, reverse=True)
        
        # Assign ranks
        for i, priority in enumerate(priorities, 1):
            priority.priority_rank = i
        
        self._log_prioritization_results(priorities)
        
        return priorities
    
    def _build_priorities(
        self,
        fs_activity: Dict[str, ApplicationActivity],
        git_activity: Dict[str, ApplicationGitActivity],
        access_patterns: Dict[str, ApplicationAccessPattern]
    ) -> List[ApplicationPriority]:
        """
        Build ApplicationPriority objects from activity signals.
        
        Args:
            fs_activity: Filesystem activity data
            git_activity: Git history data
            access_patterns: Access pattern data
            
        Returns:
            List of ApplicationPriority objects
        """
        priorities = []
        
        for app in self.applications:
            app_name = app['name']
            app_path = app['path']
            
            # Get activity data for this app
            fs_data = fs_activity.get(app_name)
            git_data = git_activity.get(app_name)
            access_data = access_patterns.get(app_name)
            
            # Extract scores
            fs_score = fs_data.activity_score if fs_data else 0.0
            git_score = git_data.activity_score if git_data else 0.0
            access_score = access_data.activity_score if access_data else 0.0
            
            # Calculate dependency score
            dependency_score = self._calculate_dependency_score(
                app_name, fs_data, git_data, access_data
            )
            
            # Determine last activity time
            last_activity = self._get_last_activity_time(fs_data, git_data, access_data)
            
            priority = ApplicationPriority(
                name=app_name,
                path=app_path,
                filesystem_score=fs_score,
                git_score=git_score,
                access_score=access_score,
                dependency_score=dependency_score,
                filesystem_activity=fs_data,
                git_activity=git_data,
                access_pattern=access_data,
                last_activity=last_activity
            )
            
            priorities.append(priority)
        
        return priorities
    
    def _calculate_dependency_score(
        self,
        app_name: str,
        fs_data: Optional[ApplicationActivity],
        git_data: Optional[ApplicationGitActivity],
        access_data: Optional[ApplicationAccessPattern]
    ) -> float:
        """
        Calculate dependency score based on cross-application links.
        
        Apps that are frequently accessed together with other active apps
        get higher dependency scores.
        
        Args:
            app_name: Application name
            fs_data: Filesystem activity data
            git_data: Git activity data
            access_data: Access pattern data
            
        Returns:
            Dependency score (0-100)
        """
        score = 0.0
        
        # Cross-app navigation links
        if access_data and access_data.cross_app_links:
            # +10 points per linked app
            score += len(access_data.cross_app_links) * 10
        
        # Shared library indicator
        if 'common' in app_name.lower() or 'shared' in app_name.lower():
            # Shared libraries get +20 bonus
            score += 20
        
        return min(score, 100.0)
    
    def _get_last_activity_time(
        self,
        fs_data: Optional[ApplicationActivity],
        git_data: Optional[ApplicationGitActivity],
        access_data: Optional[ApplicationAccessPattern]
    ) -> Optional[datetime]:
        """
        Get the most recent activity time across all signals.
        
        Args:
            fs_data: Filesystem activity data
            git_data: Git activity data
            access_data: Access pattern data
            
        Returns:
            Most recent activity datetime or None
        """
        times = []
        
        if fs_data and fs_data.last_activity:
            times.append(fs_data.last_activity)
        
        if git_data and git_data.files_changed:
            git_times = [f.last_modified for f in git_data.files_changed]
            if git_times:
                times.append(max(git_times))
        
        if access_data and access_data.accessed_files:
            access_times = [a.access_time for a in access_data.accessed_files]
            if access_times:
                times.append(max(access_times))
        
        return max(times) if times else None
    
    def _calculate_composite_scores(self, priorities: List[ApplicationPriority]) -> None:
        """
        Calculate weighted composite scores.
        
        Formula:
        total_score = (fs * 0.4) + (git * 0.3) + (access * 0.2) + (dependency * 0.1)
        
        Args:
            priorities: List of ApplicationPriority (modified in place)
        """
        for priority in priorities:
            priority.total_score = (
                (priority.filesystem_score * self.FILESYSTEM_WEIGHT) +
                (priority.git_score * self.GIT_WEIGHT) +
                (priority.access_score * self.ACCESS_WEIGHT) +
                (priority.dependency_score * self.DEPENDENCY_WEIGHT)
            )
    
    def _normalize_scores(self, priorities: List[ApplicationPriority]) -> None:
        """
        Normalize scores to 0-100 scale.
        
        Args:
            priorities: List of ApplicationPriority (modified in place)
        """
        # Find max score
        max_score = max(p.total_score for p in priorities) if priorities else 1.0
        
        if max_score == 0:
            max_score = 1.0
        
        # Normalize
        for priority in priorities:
            priority.normalized_score = (priority.total_score / max_score) * 100.0
    
    def _assign_priority_tiers(self, priorities: List[ApplicationPriority]) -> None:
        """
        Assign priority tiers based on scores and tier limits.
        
        Tiers:
        - Immediate: Top N apps (load immediately)
        - Queued: Next M apps (pre-warm cache)
        - Background: Remaining apps (lazy load)
        
        Args:
            priorities: List of ApplicationPriority sorted by score (modified in place)
        """
        # Sort by score first
        sorted_priorities = sorted(priorities, key=lambda x: x.total_score, reverse=True)
        
        for i, priority in enumerate(sorted_priorities):
            if i < self.immediate_count:
                priority.tier = 'immediate'
            elif i < self.immediate_count + self.queued_count:
                priority.tier = 'queued'
            else:
                priority.tier = 'background'
    
    def _log_prioritization_results(self, priorities: List[ApplicationPriority]) -> None:
        """Log prioritization results"""
        logger.info("=" * 60)
        logger.info("Application Prioritization Results")
        logger.info("=" * 60)
        
        for priority in priorities[:10]:  # Top 10
            logger.info(
                f"#{priority.priority_rank} {priority.name} "
                f"[{priority.tier.upper()}] "
                f"Score: {priority.normalized_score:.1f} "
                f"(FS:{priority.filesystem_score:.0f} "
                f"Git:{priority.git_score:.0f} "
                f"Access:{priority.access_score:.0f} "
                f"Dep:{priority.dependency_score:.0f})"
            )
        
        if len(priorities) > 10:
            logger.info(f"... and {len(priorities) - 10} more applications")
        
        # Summary by tier
        tier_counts = {
            'immediate': sum(1 for p in priorities if p.tier == 'immediate'),
            'queued': sum(1 for p in priorities if p.tier == 'queued'),
            'background': sum(1 for p in priorities if p.tier == 'background')
        }
        
        logger.info("-" * 60)
        logger.info(f"Tier Distribution: Immediate={tier_counts['immediate']}, "
                   f"Queued={tier_counts['queued']}, "
                   f"Background={tier_counts['background']}")
        logger.info("=" * 60)
    
    def get_immediate_applications(self) -> List[ApplicationPriority]:
        """
        Get applications that should be loaded immediately.
        
        Returns:
            List of top-priority applications
        """
        priorities = self.prioritize_applications()
        return [p for p in priorities if p.tier == 'immediate']
    
    def get_queued_applications(self) -> List[ApplicationPriority]:
        """
        Get applications for cache pre-warming.
        
        Returns:
            List of queued applications
        """
        priorities = self.prioritize_applications()
        return [p for p in priorities if p.tier == 'queued']
    
    def to_dict(self, priority: ApplicationPriority) -> Dict[str, Any]:
        """Convert ApplicationPriority to dictionary"""
        return {
            'name': priority.name,
            'path': priority.path,
            'tier': priority.tier,
            'rank': priority.priority_rank,
            'scores': {
                'total': priority.total_score,
                'normalized': priority.normalized_score,
                'filesystem': priority.filesystem_score,
                'git': priority.git_score,
                'access': priority.access_score,
                'dependency': priority.dependency_score
            },
            'last_activity': priority.last_activity.isoformat() if priority.last_activity else None
        }
