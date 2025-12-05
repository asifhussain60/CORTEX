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
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hotspot_period 
            ON context_file_hotspots(period_start, period_end)
        """)
        
        # Cache table for expensive git operations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_cache (
                cache_key TEXT PRIMARY KEY,
                cache_value TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        # Index for cache expiration cleanup
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires 
            ON context_cache(expires_at)
        """)
        
        conn.commit()
        conn.close()
    
    # ==== CACHE MANAGEMENT ====
    
    def _get_cache(self, cache_key: str) -> Optional[str]:
        """Get cached value if not expired."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clean expired entries first
        cursor.execute("""
            DELETE FROM context_cache
            WHERE expires_at < CURRENT_TIMESTAMP
        """)
        
        cursor.execute("""
            SELECT cache_value FROM context_cache
            WHERE cache_key = ?
              AND expires_at > CURRENT_TIMESTAMP
        """, (cache_key,))
        
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        
        return row[0] if row else None
    
    def _set_cache(self, cache_key: str, cache_value: str, ttl_minutes: int = 60):
        """Set cache value with expiration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
        
        cursor.execute("""
            INSERT OR REPLACE INTO context_cache (cache_key, cache_value, expires_at)
            VALUES (?, ?, ?)
        """, (cache_key, cache_value, expires_at.isoformat()))
        
        conn.commit()
        conn.close()
    
    def _clear_expired_cache(self):
        """Clean up expired cache entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM context_cache
            WHERE expires_at < CURRENT_TIMESTAMP
        """)
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
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
        Analyze file churn and identify unstable files with caching.
        
        Cache TTL: 60 minutes (to avoid expensive git operations)
        
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
        
        cache_key = f"file_hotspots_{days}d_{period_start}_{period_end}"
        cached = self._get_cache(cache_key)
        
        if cached:
            # Deserialize cached hotspots
            try:
                hotspots_data = json.loads(cached)
                hotspots = []
                for data in hotspots_data:
                    hotspot = FileHotspot(
                        file_path=data['file_path'],
                        period_start=datetime.fromisoformat(data['period_start']).date(),
                        period_end=datetime.fromisoformat(data['period_end']).date(),
                        total_commits=data['total_commits'],
                        file_edits=data['file_edits'],
                        churn_rate=data['churn_rate'],
                        stability=Stability[data['stability']]
                    )
                    hotspots.append(hotspot)
                return hotspots
            except (json.JSONDecodeError, KeyError):
                # Cache corrupted, regenerate
                pass
        
        # Cache miss or invalid - compute hotspots
        try:
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
            
            hotspots = []
            for file_path, edits in file_edits.items():
                churn_rate = edits / total_commits
                
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
            
            # Cache the results (60 minute TTL)
            hotspots_data = []
            for hotspot in hotspots:
                hotspots_data.append({
                    'file_path': hotspot.file_path,
                    'period_start': hotspot.period_start.isoformat(),
                    'period_end': hotspot.period_end.isoformat(),
                    'total_commits': hotspot.total_commits,
                    'file_edits': hotspot.file_edits,
                    'churn_rate': hotspot.churn_rate,
                    'stability': hotspot.stability.name
                })
            
            self._set_cache(cache_key, json.dumps(hotspots_data), ttl_minutes=60)
            
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
    
    # ========== Phase 3: TDD Workflow Enhancement - Real-Time Context Updates ==========
    
    def store_code_metrics(
        self,
        file_path: str,
        cyclomatic_complexity: int,
        cognitive_complexity: int,
        lines_of_code: int,
        source: str = 'tdd_green_phase'
    ) -> bool:
        """
        Store code metrics captured during GREEN phase of TDD.
        
        Part of Phase 3 Deliverable 3.3: Real-time dev context updates
        
        Args:
            file_path: Path to file being measured
            cyclomatic_complexity: Cyclomatic complexity score
            cognitive_complexity: Cognitive complexity score
            lines_of_code: Total lines of code
            source: Where metrics were captured from
        
        Returns:
            True if stored successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS code_metrics_realtime (
                    metric_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    cyclomatic_complexity INTEGER,
                    cognitive_complexity INTEGER,
                    lines_of_code INTEGER,
                    source TEXT NOT NULL,
                    measured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            metric_id = f"metric_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            cursor.execute('''
                INSERT INTO code_metrics_realtime
                (metric_id, file_path, cyclomatic_complexity, cognitive_complexity, 
                 lines_of_code, source, measured_at, captured_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric_id,
                file_path,
                cyclomatic_complexity,
                cognitive_complexity,
                lines_of_code,
                source,
                datetime.now(),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing code metrics: {e}")
            return False
    
    def get_code_metrics(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get most recent code metrics for a file.
        
        Args:
            file_path: File to retrieve metrics for
        
        Returns:
            Metrics dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT metric_id, cyclomatic_complexity, cognitive_complexity,
                       lines_of_code, source, measured_at, captured_at
                FROM code_metrics_realtime
                WHERE file_path = ?
                ORDER BY captured_at DESC
                LIMIT 1
            ''', (file_path,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'metric_id': row[0],
                    'file_path': file_path,
                    'cyclomatic_complexity': row[1],
                    'cognitive_complexity': row[2],
                    'lines_of_code': row[3],
                    'source': row[4],
                    'measured_at': row[5],
                    'captured_at': row[6]
                }
            return None
        except Exception as e:
            print(f"Error retrieving code metrics: {e}")
            return None
    
    def get_recent_improvements(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent code improvements from REFACTOR phase.
        
        Returns:
            List of improvement dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS refactoring_improvements (
                    improvement_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    improvement_type TEXT NOT NULL,
                    description TEXT,
                    before_complexity INTEGER,
                    after_complexity INTEGER,
                    improvement_percent REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                SELECT improvement_id, file_path, improvement_type, description,
                       before_complexity, after_complexity, improvement_percent, created_at
                FROM refactoring_improvements
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            improvements = []
            for row in rows:
                improvements.append({
                    'improvement_id': row[0],
                    'file_path': row[1],
                    'improvement_type': row[2],
                    'description': row[3],
                    'before_complexity': row[4],
                    'after_complexity': row[5],
                    'improvement_percent': row[6],
                    'created_at': row[7]
                })
            
            return improvements
        except Exception as e:
            print(f"Error retrieving improvements: {e}")
            return []
    
    def get_performance_metrics(self, feature: str) -> List[Dict[str, Any]]:
        """
        Get performance metrics for a feature from REFACTOR phase.
        
        Args:
            feature: Feature name to retrieve metrics for
        
        Returns:
            List of performance metric dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    metric_id TEXT PRIMARY KEY,
                    feature_name TEXT NOT NULL,
                    before_ms REAL NOT NULL,
                    after_ms REAL NOT NULL,
                    improvement_percent REAL,
                    measurement_type TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                SELECT metric_id, feature_name, before_ms, after_ms, 
                       improvement_percent, measurement_type, created_at
                FROM performance_metrics
                WHERE feature_name = ?
                ORDER BY created_at DESC
            ''', (feature,))
            
            rows = cursor.fetchall()
            conn.close()
            
            metrics = []
            for row in rows:
                metrics.append({
                    'metric_id': row[0],
                    'feature_name': row[1],
                    'before_ms': row[2],
                    'after_ms': row[3],
                    'improvement_percent': row[4],
                    'measurement_type': row[5],
                    'created_at': row[6]
                })
            
            return metrics
        except Exception as e:
            print(f"Error retrieving performance metrics: {e}")
            return []
    
    def get_complexity_changes(self, feature: str) -> List[Dict[str, Any]]:
        """
        Get complexity changes from REFACTOR phase.
        
        Args:
            feature: Feature name to retrieve complexity changes for
        
        Returns:
            List of complexity change dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS complexity_changes (
                    change_id TEXT PRIMARY KEY,
                    feature_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    before_complexity INTEGER NOT NULL,
                    after_complexity INTEGER NOT NULL,
                    change_percent REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                SELECT change_id, feature_name, file_path, before_complexity,
                       after_complexity, change_percent, created_at
                FROM complexity_changes
                WHERE feature_name = ?
                ORDER BY created_at DESC
            ''', (feature,))
            
            rows = cursor.fetchall()
            conn.close()
            
            changes = []
            for row in rows:
                changes.append({
                    'change_id': row[0],
                    'feature_name': row[1],
                    'file_path': row[2],
                    'before_complexity': row[3],
                    'after_complexity': row[4],
                    'change_percent': row[5],
                    'created_at': row[6]
                })
            
            return changes
        except Exception as e:
            print(f"Error retrieving complexity changes: {e}")
            return []
    
    def get_refactoring_impact(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get refactoring impact comparison (before/after metrics).
        
        Args:
            file_path: File to analyze
        
        Returns:
            Impact dictionary with before/after comparison
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get last 2 metrics (before and after refactoring)
            cursor.execute('''
                SELECT metric_id, cyclomatic_complexity, cognitive_complexity,
                       lines_of_code, source, measured_at
                FROM code_metrics_realtime
                WHERE file_path = ?
                ORDER BY captured_at DESC
                LIMIT 2
            ''', (file_path,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) >= 2:
                after = rows[0]
                before = rows[1]
                
                improvement_percent = 0
                if before[1] > 0:  # before cyclomatic_complexity
                    improvement_percent = ((before[1] - after[1]) / before[1]) * 100
                
                return {
                    'file_path': file_path,
                    'before': {
                        'cyclomatic_complexity': before[1],
                        'cognitive_complexity': before[2],
                        'lines_of_code': before[3],
                        'measured_at': before[5]
                    },
                    'after': {
                        'cyclomatic_complexity': after[1],
                        'cognitive_complexity': after[2],
                        'lines_of_code': after[3],
                        'measured_at': after[5]
                    },
                    'improvement_percent': improvement_percent
                }
            return None
        except Exception as e:
            print(f"Error calculating refactoring impact: {e}")
            return None
    
    def get_hotspots(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get file hotspots detected in real-time during development.
        
        Args:
            limit: Maximum number of hotspots to return
        
        Returns:
            List of hotspot dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hotspots_realtime (
                    hotspot_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    edit_count INTEGER DEFAULT 1,
                    last_edited DATETIME DEFAULT CURRENT_TIMESTAMP,
                    detection_source TEXT DEFAULT 'tdd_realtime'
                )
            ''')
            
            cursor.execute('''
                SELECT hotspot_id, file_path, edit_count, last_edited, detection_source
                FROM hotspots_realtime
                ORDER BY edit_count DESC, last_edited DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            hotspots = []
            for row in rows:
                hotspots.append({
                    'hotspot_id': row[0],
                    'file_path': row[1],
                    'edit_count': row[2],
                    'last_edited': row[3],
                    'detection_source': row[4]
                })
            
            return hotspots
        except Exception as e:
            print(f"Error retrieving hotspots: {e}")
            return []
    
    def increment_hotspot(self, file_path: str) -> bool:
        """
        Increment hotspot counter for a file (called during each TDD cycle).
        
        Args:
            file_path: File being edited
        
        Returns:
            True if updated successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hotspots_realtime (
                    hotspot_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    edit_count INTEGER DEFAULT 1,
                    last_edited DATETIME DEFAULT CURRENT_TIMESTAMP,
                    detection_source TEXT DEFAULT 'tdd_realtime'
                )
            ''')
            
            # Check if hotspot exists
            cursor.execute('''
                SELECT hotspot_id, edit_count FROM hotspots_realtime
                WHERE file_path = ?
            ''', (file_path,))
            
            row = cursor.fetchone()
            
            if row:
                # Update existing hotspot
                cursor.execute('''
                    UPDATE hotspots_realtime
                    SET edit_count = edit_count + 1,
                        last_edited = ?
                    WHERE file_path = ?
                ''', (datetime.now(), file_path))
            else:
                # Create new hotspot
                hotspot_id = f"hotspot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                cursor.execute('''
                    INSERT INTO hotspots_realtime
                    (hotspot_id, file_path, edit_count, last_edited, detection_source)
                    VALUES (?, ?, 1, ?, 'tdd_realtime')
                ''', (hotspot_id, file_path, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error incrementing hotspot: {e}")
            return False
    
    def get_all_metrics(self, source: str = 'tdd_green_phase') -> List[Dict[str, Any]]:
        """
        Get all metrics from a specific source.
        
        Args:
            source: Source to filter by
        
        Returns:
            List of metric dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT metric_id, file_path, cyclomatic_complexity, cognitive_complexity,
                       lines_of_code, source, measured_at, captured_at
                FROM code_metrics_realtime
                WHERE source = ?
                ORDER BY captured_at DESC
            ''', (source,))
            
            rows = cursor.fetchall()
            conn.close()
            
            metrics = []
            for row in rows:
                metrics.append({
                    'metric_id': row[0],
                    'file_path': row[1],
                    'cyclomatic_complexity': row[2],
                    'cognitive_complexity': row[3],
                    'lines_of_code': row[4],
                    'source': row[5],
                    'measured_at': row[6],
                    'captured_at': datetime.fromisoformat(row[7]) if isinstance(row[7], str) else row[7]
                })
            
            return metrics
        except Exception as e:
            print(f"Error retrieving all metrics: {e}")
            return []
    
    def extract_task_metrics_from_git(
        self,
        days: int = 30,
        repo_path: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract task-level metrics from git commit messages.
        
        Parses CORTEX-TDD checkpoint commits to extract:
        - Task ID, Feature name, Work Item ID
        - Time-to-RED, time-to-GREEN, time-to-REFACTOR
        - Task completion velocity
        
        Args:
            days: Number of days to analyze
            repo_path: Optional path to git repository
            
        Returns:
            List of task metric dicts
        """
        if repo_path is None:
            repo_path = self.db_path.parent.parent.parent
        
        repo_path = Path(repo_path)
        
        try:
            since_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            cmd = [
                "git", "-C", str(repo_path), "log",
                f"--since={since_str}",
                "--grep=CORTEX-TDD",
                "--pretty=format:%H|%ai|%B|||"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse commits and group by task
            tasks = {}
            
            for commit_block in result.stdout.split('|||'):
                if not commit_block.strip():
                    continue
                
                lines = commit_block.strip().split('\n')
                if len(lines) < 2:
                    continue
                
                # First line: sha|timestamp
                header = lines[0].split('|', 1)
                if len(header) != 2:
                    continue
                
                commit_sha = header[0]
                commit_time = datetime.fromisoformat(header[1].replace(' +0000', '+00:00').replace(' ', 'T', 1))
                
                # Parse commit body for task attribution
                task_id = None
                feature_name = None
                work_item_id = None
                checkpoint_type = None
                session_id = None
                
                for line in lines[1:]:
                    if line.startswith('CORTEX-TDD:'):
                        checkpoint_type = line.split(':', 1)[1].strip()
                    elif line.startswith('Task-ID:'):
                        task_id = line.split(':', 1)[1].strip()
                    elif line.startswith('Feature:'):
                        feature_name = line.split(':', 1)[1].strip()
                    elif line.startswith('Work-Item:'):
                        work_item_id = line.split(':', 1)[1].strip()
                    elif line.startswith('Session:'):
                        session_id = line.split(':', 1)[1].strip()
                
                # Group by task identifier (task_id or session_id)
                task_key = task_id or session_id
                if not task_key:
                    continue
                
                if task_key not in tasks:
                    tasks[task_key] = {
                        'task_id': task_id,
                        'feature_name': feature_name,
                        'work_item_id': work_item_id,
                        'session_id': session_id,
                        'checkpoints': [],
                        'red_time': None,
                        'green_time': None,
                        'refactor_time': None,
                        'completion_time': None,
                        'cycle_count': 0
                    }
                
                tasks[task_key]['checkpoints'].append({
                    'commit_sha': commit_sha,
                    'timestamp': commit_time,
                    'type': checkpoint_type
                })
            
            # Calculate time metrics for each task
            task_metrics = []
            for task_key, task_data in tasks.items():
                # Sort checkpoints by time
                task_data['checkpoints'].sort(key=lambda x: x['timestamp'])
                
                # Calculate phase durations
                red_start = None
                green_start = None
                refactor_start = None
                
                for checkpoint in task_data['checkpoints']:
                    cp_type = checkpoint['type']
                    cp_time = checkpoint['timestamp']
                    
                    if 'RED' in cp_type:
                        red_start = cp_time
                    elif 'GREEN' in cp_type and red_start:
                        task_data['red_time'] = (cp_time - red_start).total_seconds()
                        green_start = cp_time
                        task_data['cycle_count'] += 1
                    elif 'REFACTOR' in cp_type and green_start:
                        task_data['green_time'] = (cp_time - green_start).total_seconds()
                        refactor_start = cp_time
                    elif 'COMPLETE' in cp_type and refactor_start:
                        task_data['refactor_time'] = (cp_time - refactor_start).total_seconds()
                        task_data['completion_time'] = cp_time
                
                # Calculate total task duration
                if task_data['checkpoints']:
                    start = task_data['checkpoints'][0]['timestamp']
                    end = task_data['checkpoints'][-1]['timestamp']
                    task_data['total_duration_seconds'] = (end - start).total_seconds()
                
                task_metrics.append(task_data)
            
            return task_metrics
        
        except Exception as e:
            print(f"Error extracting task metrics: {e}")
            return []
    
    def calculate_task_velocity(
        self,
        days: int = 30,
        group_by: str = "week"
    ) -> List[Dict[str, Any]]:
        """
        Calculate task completion velocity over time.
        
        Args:
            days: Number of days to analyze
            group_by: Grouping period ("day", "week", "month")
            
        Returns:
            List of velocity data points
        """
        task_metrics = self.extract_task_metrics_from_git(days=days)
        
        # Group completed tasks by time period
        velocity_data = {}
        
        for task in task_metrics:
            if not task.get('completion_time'):
                continue
            
            completion_time = task['completion_time']
            
            # Determine time bucket
            if group_by == "day":
                bucket = completion_time.date()
            elif group_by == "week":
                bucket = completion_time.date() - timedelta(days=completion_time.weekday())
            elif group_by == "month":
                bucket = completion_time.replace(day=1).date()
            else:
                bucket = completion_time.date()
            
            if bucket not in velocity_data:
                velocity_data[bucket] = {
                    'period': bucket.isoformat(),
                    'tasks_completed': 0,
                    'total_duration': 0.0,
                    'total_cycles': 0,
                    'avg_red_time': 0.0,
                    'avg_green_time': 0.0,
                    'avg_refactor_time': 0.0
                }
            
            velocity_data[bucket]['tasks_completed'] += 1
            velocity_data[bucket]['total_duration'] += task.get('total_duration_seconds', 0)
            velocity_data[bucket]['total_cycles'] += task.get('cycle_count', 0)
            
            if task.get('red_time'):
                velocity_data[bucket]['avg_red_time'] += task['red_time']
            if task.get('green_time'):
                velocity_data[bucket]['avg_green_time'] += task['green_time']
            if task.get('refactor_time'):
                velocity_data[bucket]['avg_refactor_time'] += task['refactor_time']
        
        # Calculate averages
        result = []
        for bucket, data in sorted(velocity_data.items()):
            count = data['tasks_completed']
            if count > 0:
                data['avg_duration'] = data['total_duration'] / count
                data['avg_red_time'] = data['avg_red_time'] / count
                data['avg_green_time'] = data['avg_green_time'] / count
                data['avg_refactor_time'] = data['avg_refactor_time'] / count
            
            result.append(data)
        
        return result


