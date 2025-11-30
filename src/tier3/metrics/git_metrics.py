"""
CORTEX Tier 3: Git Metrics Collection
Handles git activity tracking and commit velocity analysis.
"""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from typing import List, Optional, Dict
import sqlite3


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


class GitMetricsCollector:
    """
    Collects git activity metrics with delta optimization.
    
    Features:
    - Collects commit counts, line changes, file modifications
    - Per-contributor or aggregated metrics
    - Delta updates (only collect new commits)
    - Efficient subprocess-based git log parsing
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize collector.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    def collect_metrics(self,
                       repo_path: Optional[Path] = None,
                       since: Optional[datetime] = None,
                       days: int = 30) -> List[GitMetric]:
        """
        Collect git activity metrics with delta optimization.
        
        Args:
            repo_path: Path to git repository (default: workspace root)
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
    
    def save_metrics(self, metrics: List[GitMetric]):
        """
        Save git metrics to database.
        
        Args:
            metrics: List of GitMetric objects to save
        """
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
    
    def get_metrics(self,
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
