"""
CORTEX Tier 3: Development Context Intelligence
Part 1: Imports, Enums, and Data Classes
"""

import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import json


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


class Stability(Enum):
    """File stability classification."""
    STABLE = "STABLE"       # < 10% churn rate
    MODERATE = "MODERATE"   # 10-20% churn rate
    UNSTABLE = "UNSTABLE"   # > 20% churn rate


class TestType(Enum):
    """Types of tests tracked."""
    UI = "ui"
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"


class IntentType(Enum):
    """CORTEX intent types."""
    PLAN = "PLAN"
    EXECUTE = "EXECUTE"
    TEST = "TEST"
    VALIDATE = "VALIDATE"
    GOVERN = "GOVERN"
    CORRECT = "CORRECT"
    RESUME = "RESUME"
    ASK = "ASK"


@dataclass
class GitMetric:
    """Daily git activity metrics."""
    metric_date: date
    commits_count: int
    lines_added: int
    lines_deleted: int
    net_growth: int
    files_changed: int
    contributor: Optional[str] = None


@dataclass
class FileHotspot:
    """File churn analysis."""
    file_path: str
    period_start: date
    period_end: date
    total_commits: int
    file_edits: int
    churn_rate: float
    stability: Stability
    last_modified: Optional[datetime] = None
    lines_changed: int = 0


@dataclass
class TestMetric:
    """Daily test execution metrics."""
    metric_date: date
    test_type: TestType
    tests_discovered: int
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    pass_rate: float
    coverage_percentage: Optional[float] = None
    avg_duration_seconds: Optional[float] = None


@dataclass
class FlakyTest:
    """Flaky test tracking."""
    test_name: str
    test_type: TestType
    first_detected: datetime
    last_seen: datetime
    total_runs: int
    failure_count: int
    failure_rate: float
    status: str  # ACTIVE, FIXED, IGNORED
    failure_pattern: Optional[List[str]] = None
    resolution_notes: Optional[str] = None


@dataclass
class BuildMetric:
    """Daily build metrics."""
    metric_date: date
    builds_total: int
    builds_successful: int
    builds_failed: int
    success_rate: float
    avg_build_time_seconds: Optional[float] = None


@dataclass
class WorkPattern:
    """Work session patterns."""
    pattern_date: date
    time_slot: str  # e.g., "08-10"
    sessions_count: int
    sessions_successful: int
    success_rate: float
    avg_duration_minutes: Optional[int] = None
    avg_focus_duration_minutes: Optional[int] = None


@dataclass
class CortexUsage:
    """CORTEX usage metrics."""
    metric_date: date
    intent_type: IntentType
    requests_count: int
    successful_count: int
    failed_count: int
    avg_response_time_seconds: Optional[float] = None


@dataclass
class Correlation:
    """Correlation between metrics."""
    correlation_name: str
    description: str
    metric_a: str
    metric_b: str
    correlation_coefficient: float
    sample_size: int
    confidence_level: float
    insight: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


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


class ContextIntelligence:
    """
    Tier 3: Development Context Intelligence
    
    Provides real-time project analytics including:
    - Git activity tracking and commit velocity
    - File hotspot detection and churn analysis
    - Test metrics and flaky test detection
    - Build health monitoring
    - Work pattern analysis
    - CORTEX usage effectiveness
    - Correlation discovery and insights
    
    Performance targets:
    - Context queries: <10ms
    - Database size: <50KB
    - Update frequency: Delta updates (minimum 1 hour interval)
    """
    
    # Collection throttling
    MIN_COLLECTION_INTERVAL_HOURS = 1
    
    # Analysis windows
    DEFAULT_ANALYSIS_WINDOW_DAYS = 30
    VELOCITY_WINDOW_DAYS = 7
    HOTSPOT_WINDOW_DAYS = 30
    
    # Thresholds
    CHURN_STABLE_THRESHOLD = 0.10    # <10% = stable
    CHURN_MODERATE_THRESHOLD = 0.20  # 10-20% = moderate
    FLAKY_FAILURE_THRESHOLD = 0.20   # >20% failure rate = flaky
    VELOCITY_DROP_THRESHOLD = 0.30   # >30% drop = warning
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize Context Intelligence.
        
        Args:
            db_path: Path to SQLite database (default: cortex-brain/tier3/context.db)
        """
        if db_path is None:
            brain_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3"
            brain_dir.mkdir(parents=True, exist_ok=True)
            db_path = brain_dir / "context.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Git metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_git_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                commits_count INTEGER NOT NULL DEFAULT 0,
                lines_added INTEGER NOT NULL DEFAULT 0,
                lines_deleted INTEGER NOT NULL DEFAULT 0,
                net_growth INTEGER NOT NULL DEFAULT 0,
                files_changed INTEGER NOT NULL DEFAULT 0,
                contributor TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_date, contributor)
            )
        """)
        
        # Indexes for git metrics
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_git_date 
            ON context_git_metrics(metric_date DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_git_contributor 
            ON context_git_metrics(contributor)
        """)
        
        # File hotspots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_file_hotspots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                period_start DATE NOT NULL,
                period_end DATE NOT NULL,
                total_commits INTEGER NOT NULL DEFAULT 0,
                file_edits INTEGER NOT NULL DEFAULT 0,
                churn_rate REAL NOT NULL CHECK(churn_rate >= 0.0 AND churn_rate <= 1.0),
                stability TEXT NOT NULL CHECK(stability IN ('STABLE', 'MODERATE', 'UNSTABLE')),
                last_modified TIMESTAMP,
                lines_changed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_path, period_start, period_end)
            )
        """)
        
        # Indexes for hotspots
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hotspot_file 
            ON context_file_hotspots(file_path)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hotspot_churn 
            ON context_file_hotspots(churn_rate DESC)
        """)
        
        conn.commit()
        conn.close()
    
    # ==== GIT METRICS COLLECTION ====
    
    def collect_git_metrics(self, 
                           repo_path: Optional[Path] = None,
                           since: Optional[datetime] = None,
                           days: int = 30) -> List[GitMetric]:
        """
        Collect git activity metrics with delta optimization.
        
        Args:
            repo_path: Path to git repository (default: parent of cortex-brain)
            since: Only collect commits after this timestamp
            days: Number of days to collect (if since is None)
            
        Returns:
            List of GitMetric objects
        """
        if repo_path is None:
            repo_path = self.db_path.parent.parent.parent
        
        repo_path = Path(repo_path)
        
        # Determine collection start time
        if since is None:
            since = datetime.now() - timedelta(days=days)
        
        # Query git log
        try:
            since_str = since.strftime("%Y-%m-%d")
            cmd = [
                "git", "-C", str(repo_path), "log",
                f"--since={since_str}",
                "--pretty=format:%ad|%an",
                "--date=short",
                "--numstat"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse git log output
            metrics_by_date = {}
            current_date = None
            current_contributor = None
            
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                
                if '|' in line:
                    # Commit header: date|author
                    date_str, contributor = line.split('|', 1)
                    current_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    current_contributor = contributor
                    
                    # Initialize metric for this date
                    key = (current_date, current_contributor)
                    if key not in metrics_by_date:
                        metrics_by_date[key] = {
                            'commits': 0,
                            'lines_added': 0,
                            'lines_deleted': 0,
                            'files_changed': set()
                        }
                    metrics_by_date[key]['commits'] += 1
                
                else:
                    # File stats: added\tdeleted\tfilename
                    parts = line.split('\t')
                    if len(parts) >= 3 and current_date:
                        key = (current_date, current_contributor)
                        try:
                            added = int(parts[0]) if parts[0] != '-' else 0
                            deleted = int(parts[1]) if parts[1] != '-' else 0
                            filename = parts[2]
                            
                            metrics_by_date[key]['lines_added'] += added
                            metrics_by_date[key]['lines_deleted'] += deleted
                            metrics_by_date[key]['files_changed'].add(filename)
                        except (ValueError, IndexError):
                            pass
            
            # Convert to GitMetric objects
            metrics = []
            for (date_val, contributor), data in metrics_by_date.items():
                metric = GitMetric(
                    metric_date=date_val,
                    commits_count=data['commits'],
                    lines_added=data['lines_added'],
                    lines_deleted=data['lines_deleted'],
                    net_growth=data['lines_added'] - data['lines_deleted'],
                    files_changed=len(data['files_changed']),
                    contributor=contributor
                )
                metrics.append(metric)
            
            return metrics
            
        except subprocess.CalledProcessError:
            # Not a git repository or git command failed
            return []
        except Exception:
            return []
    
    def save_git_metrics(self, metrics: List[GitMetric]):
        """Save git metrics to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric in metrics:
            cursor.execute("""
                INSERT OR REPLACE INTO context_git_metrics
                (metric_date, commits_count, lines_added, lines_deleted, 
                 net_growth, files_changed, contributor)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.metric_date.isoformat(),
                metric.commits_count,
                metric.lines_added,
                metric.lines_deleted,
                metric.net_growth,
                metric.files_changed,
                metric.contributor
            ))
        
        conn.commit()
        conn.close()
    
    def get_git_metrics(self, 
                       days: int = 30,
                       contributor: Optional[str] = None) -> List[GitMetric]:
        """
        Retrieve git metrics from database.
        
        Args:
            days: Number of days to retrieve
            contributor: Filter by contributor (None = all aggregated)
            
        Returns:
            List of GitMetric objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).date()
        
        if contributor:
            cursor.execute("""
                SELECT * FROM context_git_metrics
                WHERE metric_date >= ?
                  AND contributor = ?
                ORDER BY metric_date DESC
            """, (since_date.isoformat(), contributor))
        else:
            # Aggregate across all contributors
            cursor.execute("""
                SELECT 
                    metric_date,
                    SUM(commits_count) as commits_count,
                    SUM(lines_added) as lines_added,
                    SUM(lines_deleted) as lines_deleted,
                    SUM(net_growth) as net_growth,
                    SUM(files_changed) as files_changed,
                    NULL as contributor
                FROM context_git_metrics
                WHERE metric_date >= ?
                GROUP BY metric_date
                ORDER BY metric_date DESC
            """, (since_date.isoformat(),))
        
        metrics = []
        for row in cursor.fetchall():
            metric = GitMetric(
                metric_date=datetime.fromisoformat(row['metric_date']).date(),
                commits_count=row['commits_count'],
                lines_added=row['lines_added'],
                lines_deleted=row['lines_deleted'],
                net_growth=row['net_growth'],
                files_changed=row['files_changed'],
                contributor=row['contributor']
            )
            metrics.append(metric)
        
        conn.close()
        return metrics
    
    # ==== FILE HOTSPOT ANALYSIS ====
    
    def analyze_file_hotspots(self,
                              repo_path: Optional[Path] = None,
                              days: int = 30) -> List[FileHotspot]:
        """
        Analyze file churn and identify unstable files.
        
        Args:
            repo_path: Path to git repository
            days: Analysis window in days
            
        Returns:
            List of FileHotspot objects
        """
        if repo_path is None:
            repo_path = self.db_path.parent.parent.parent
        
        repo_path = Path(repo_path)
        period_end = date.today()
        period_start = period_end - timedelta(days=days)
        
        try:
            # Get total commits in period
            since_str = period_start.strftime("%Y-%m-%d")
            cmd_total = [
                "git", "-C", str(repo_path), "rev-list",
                f"--since={since_str}",
                "--count", "HEAD"
            ]
            result_total = subprocess.run(cmd_total, capture_output=True, text=True, check=True)
            total_commits = int(result_total.stdout.strip())
            
            if total_commits == 0:
                return []
            
            # Get file edit counts
            cmd_files = [
                "git", "-C", str(repo_path), "log",
                f"--since={since_str}",
                "--name-only",
                "--pretty=format:"
            ]
            result_files = subprocess.run(cmd_files, capture_output=True, text=True, check=True)
            
            # Count edits per file
            file_edits = {}
            for line in result_files.stdout.split('\n'):
                if line.strip():
                    file_edits[line.strip()] = file_edits.get(line.strip(), 0) + 1
            
            # Calculate churn rates and stability
            hotspots = []
            for file_path, edits in file_edits.items():
                churn_rate = edits / total_commits
                
                # Classify stability
                if churn_rate < self.CHURN_STABLE_THRESHOLD:
                    stability = Stability.STABLE
                elif churn_rate < self.CHURN_MODERATE_THRESHOLD:
                    stability = Stability.MODERATE
                else:
                    stability = Stability.UNSTABLE
                
                hotspot = FileHotspot(
                    file_path=file_path,
                    period_start=period_start,
                    period_end=period_end,
                    total_commits=total_commits,
                    file_edits=edits,
                    churn_rate=churn_rate,
                    stability=stability
                )
                hotspots.append(hotspot)
            
            # Sort by churn rate (highest first)
            hotspots.sort(key=lambda h: h.churn_rate, reverse=True)
            
            return hotspots
            
        except Exception:
            return []
    
    def save_file_hotspots(self, hotspots: List[FileHotspot]):
        """Save file hotspots to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for hotspot in hotspots:
            cursor.execute("""
                INSERT OR REPLACE INTO context_file_hotspots
                (file_path, period_start, period_end, total_commits,
                 file_edits, churn_rate, stability, lines_changed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                hotspot.file_path,
                hotspot.period_start.isoformat(),
                hotspot.period_end.isoformat(),
                hotspot.total_commits,
                hotspot.file_edits,
                hotspot.churn_rate,
                hotspot.stability.value,
                hotspot.lines_changed
            ))
        
        conn.commit()
        conn.close()
    
    def get_unstable_files(self, limit: int = 10) -> List[FileHotspot]:
        """
        Get most unstable files (highest churn rate).
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of FileHotspot objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM context_file_hotspots
            WHERE stability = 'UNSTABLE'
            ORDER BY churn_rate DESC
            LIMIT ?
        """, (limit,))
        
        hotspots = []
        for row in cursor.fetchall():
            hotspot = FileHotspot(
                file_path=row['file_path'],
                period_start=datetime.fromisoformat(row['period_start']).date(),
                period_end=datetime.fromisoformat(row['period_end']).date(),
                total_commits=row['total_commits'],
                file_edits=row['file_edits'],
                churn_rate=row['churn_rate'],
                stability=Stability(row['stability']),
                lines_changed=row['lines_changed']
            )
            hotspots.append(hotspot)
        
        conn.close()
        return hotspots
    
    # ==== VELOCITY ANALYSIS ====
    
    def calculate_commit_velocity(self, window_days: int = 7) -> Dict[str, Any]:
        """
        Calculate commit velocity trends.
        
        Args:
            window_days: Number of days per window
            
        Returns:
            Dictionary with velocity metrics and trend analysis
        """
        metrics = self.get_git_metrics(days=window_days * 4)  # 4 windows
        
        if not metrics:
            return {
                'current_velocity': 0,
                'previous_velocity': 0,
                'trend': 'unknown',
                'change_percent': 0
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
            elif change_percent > self.VELOCITY_DROP_THRESHOLD * 100:
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
    
    # ==== INSIGHT GENERATION ====
    
    def generate_insights(self) -> List[Insight]:
        """
        Generate insights from collected metrics.
        
        Returns:
            List of Insight objects
        """
        insights = []
        
        # Check velocity trends
        velocity = self.calculate_commit_velocity()
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
        unstable_files = self.get_unstable_files(limit=5)
        for hotspot in unstable_files:
            if hotspot.churn_rate > 0.3:  # >30% churn
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
    
    # ==== HELPER METHODS ====
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive context summary.
        
        Returns:
            Dictionary with all context metrics
        """
        metrics = self.get_git_metrics(days=30)
        velocity = self.calculate_commit_velocity()
        unstable_files = self.get_unstable_files(limit=5)
        insights = self.generate_insights()
        
        return {
            'git_metrics': {
                'total_commits': sum(m.commits_count for m in metrics),
                'total_lines_added': sum(m.lines_added for m in metrics),
                'total_lines_deleted': sum(m.lines_deleted for m in metrics),
                'net_growth': sum(m.net_growth for m in metrics),
                'unique_files_changed': sum(m.files_changed for m in metrics)
            },
            'velocity': velocity,
            'unstable_files': [
                {
                    'file_path': h.file_path,
                    'churn_rate': h.churn_rate,
                    'stability': h.stability.value
                }
                for h in unstable_files
            ],
            'insights': [
                {
                    'type': i.insight_type.value,
                    'severity': i.severity.value,
                    'title': i.title,
                    'description': i.description
                }
                for i in insights
            ]
        }
    
    def update_all_metrics(self,
                          repo_path: Optional[Path] = None,
                          days: int = 30):
        """
        Update all metrics (git + file hotspots).
        
        Args:
            repo_path: Path to git repository
            days: Number of days to analyze
        """
        # Collect and save git metrics
        git_metrics = self.collect_git_metrics(repo_path=repo_path, days=days)
        if git_metrics:
            self.save_git_metrics(git_metrics)
        
        # Analyze and save file hotspots
        hotspots = self.analyze_file_hotspots(repo_path=repo_path, days=days)
        if hotspots:
            self.save_file_hotspots(hotspots)

