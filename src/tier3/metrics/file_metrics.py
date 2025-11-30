"""
CORTEX Tier 3: File Metrics Analysis
Handles file hotspot detection and churn analysis.
"""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import sqlite3


class Stability(Enum):
    """File stability classification."""
    STABLE = "STABLE"       # < 10% churn rate
    MODERATE = "MODERATE"   # 10-20% churn rate
    UNSTABLE = "UNSTABLE"   # > 20% churn rate


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


class FileMetricsAnalyzer:
    """
    Analyzes file churn and identifies unstable files.
    
    Features:
    - File edit frequency tracking
    - Churn rate calculation
    - Stability classification (STABLE/MODERATE/UNSTABLE)
    - Hotspot detection
    """
    
    # Thresholds
    CHURN_STABLE_THRESHOLD = 0.10    # <10% = stable
    CHURN_MODERATE_THRESHOLD = 0.20  # 10-20% = moderate
    
    def __init__(self, db_path: Path):
        """
        Initialize analyzer.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    def analyze_hotspots(self,
                        repo_path: Optional[Path] = None,
                        days: int = 30) -> List[FileHotspot]:
        """
        Analyze file churn and identify unstable files.
        
        Args:
            repo_path: Path to git repository
            days: Analysis window in days
            
        Returns:
            List of FileHotspot objects sorted by churn rate
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
                stability = self._classify_stability(churn_rate)
                
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
    
    def _classify_stability(self, churn_rate: float) -> Stability:
        """
        Classify file stability based on churn rate.
        
        Args:
            churn_rate: File churn rate (0.0 to 1.0)
            
        Returns:
            Stability enum value
        """
        if churn_rate < self.CHURN_STABLE_THRESHOLD:
            return Stability.STABLE
        elif churn_rate < self.CHURN_MODERATE_THRESHOLD:
            return Stability.MODERATE
        else:
            return Stability.UNSTABLE
    
    def save_hotspots(self, hotspots: List[FileHotspot]):
        """
        Save file hotspots to database.
        
        Args:
            hotspots: List of FileHotspot objects to save
        """
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
    
    def get_hotspots(self, days: int = 30, min_churn: float = 0.0) -> List[FileHotspot]:
        """
        Get file hotspots from database.
        
        Args:
            days: Number of days to look back
            min_churn: Minimum churn rate to include
            
        Returns:
            List of FileHotspot objects
        """
        since_date = datetime.now().date() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM context_file_hotspots
            WHERE period_end >= ?
              AND churn_rate >= ?
            ORDER BY churn_rate DESC
        """, (since_date.isoformat(), min_churn))
        
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
    
    def get_unstable_files(self, days: int = 30) -> List[FileHotspot]:
        """
        Get unstable files within time period.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of unstable FileHotspot objects
        """
        since_date = datetime.now().date() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM context_file_hotspots
            WHERE stability = 'UNSTABLE'
              AND period_end >= ?
            ORDER BY churn_rate DESC
        """, (since_date.isoformat(),))
        
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
    
    def get_hotspots_by_stability(self, 
                                  stability: Stability,
                                  limit: int = 10) -> List[FileHotspot]:
        """
        Get files by stability classification.
        
        Args:
            stability: Stability level to filter by
            limit: Maximum number of files to return
            
        Returns:
            List of FileHotspot objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM context_file_hotspots
            WHERE stability = ?
            ORDER BY churn_rate DESC
            LIMIT ?
        """, (stability.value, limit))
        
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
