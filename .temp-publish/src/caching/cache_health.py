"""
Cache Health Monitoring
Provides health metrics and diagnostics for ValidationCache

Tracks:
- Cache size (MB)
- Entry age distribution
- Hit rate trends
- Stale entry detection
- Corruption detection

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.caching import get_cache

logger = logging.getLogger(__name__)


@dataclass
class CacheHealthReport:
    """Cache health assessment report."""
    overall_status: str  # 'healthy', 'warning', 'critical'
    cache_size_mb: float
    total_entries: int
    oldest_entry_age_days: float
    avg_entry_age_hours: float
    stale_entries: int
    hit_rate_overall: float
    issues: List[str]
    recommendations: List[str]


class CacheHealthMonitor:
    """
    Monitor cache health and detect issues.
    
    Provides:
    - Size monitoring (disk usage)
    - Age distribution (staleness detection)
    - Hit rate trends (effectiveness tracking)
    - Corruption detection (integrity validation)
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize cache health monitor.
        
        Args:
            project_root: Project root directory (auto-detected if None)
        """
        if project_root is None:
            project_root = Path.cwd()
            while project_root != project_root.parent:
                if (project_root / '.git').exists():
                    break
                project_root = project_root.parent
        
        self.project_root = project_root
        self.cache = get_cache()
    
    def check_health(self) -> CacheHealthReport:
        """
        Perform comprehensive cache health check.
        
        Returns:
            CacheHealthReport with status and recommendations
        """
        issues = []
        recommendations = []
        
        # Check cache size
        cache_size_mb = self._get_cache_size_mb()
        if cache_size_mb > 100:
            issues.append(f"Large cache size: {cache_size_mb:.1f}MB")
            recommendations.append("Consider clearing old entries with 'cortex cache clear --older-than 7d'")
        
        # Check entry age distribution
        total_entries, avg_age_hours, oldest_age_days, stale_count = self._get_age_distribution()
        
        if oldest_age_days > 30:
            issues.append(f"Very old entries detected: {oldest_age_days:.1f} days old")
            recommendations.append("Run 'cortex cache clear --stale' to remove entries older than 30 days")
        elif oldest_age_days > 7:
            issues.append(f"Old entries detected: {oldest_age_days:.1f} days old")
            recommendations.append("Consider running cleanup if cache performance degrades")
        
        if stale_count > 0:
            issues.append(f"{stale_count} stale entries (>7 days old)")
        
        # Check hit rate
        hit_rate = self._get_overall_hit_rate()
        if hit_rate < 0.3 and total_entries > 10:
            issues.append(f"Low hit rate: {hit_rate * 100:.1f}%")
            recommendations.append("Cache may not be effective. Consider reviewing cached operations or clearing cache.")
        
        # Check for corruption
        corruption_issues = self._check_corruption()
        if corruption_issues:
            issues.extend(corruption_issues)
            recommendations.append("Run 'cortex cache validate --repair' to fix corruption")
        
        # Determine overall status
        if len(issues) == 0:
            status = 'healthy'
        elif any('corruption' in issue.lower() or 'critical' in issue.lower() for issue in issues):
            status = 'critical'
        else:
            status = 'warning'
        
        if status == 'healthy' and not recommendations:
            recommendations.append("Cache is healthy! No action needed.")
        
        return CacheHealthReport(
            overall_status=status,
            cache_size_mb=cache_size_mb,
            total_entries=total_entries,
            oldest_entry_age_days=oldest_age_days,
            avg_entry_age_hours=avg_age_hours,
            stale_entries=stale_count,
            hit_rate_overall=hit_rate,
            issues=issues,
            recommendations=recommendations
        )
    
    def _get_cache_size_mb(self) -> float:
        """Get total cache size in MB."""
        try:
            cache_file = self.cache.cache_db
            if cache_file.exists():
                return cache_file.stat().st_size / (1024 * 1024)
            return 0.0
        except Exception as e:
            logger.warning(f"Failed to get cache size: {e}")
            return 0.0
    
    def _get_age_distribution(self) -> Tuple[int, float, float, int]:
        """
        Get cache entry age distribution.
        
        Returns:
            (total_entries, avg_age_hours, oldest_age_days, stale_count)
        """
        try:
            conn = sqlite3.connect(self.cache.cache_db)
            
            # Get all timestamps
            cursor = conn.execute("SELECT timestamp FROM cache_entries")
            timestamps = [row[0] for row in cursor.fetchall()]
            
            if not timestamps:
                conn.close()
                return (0, 0.0, 0.0, 0)
            
            now = datetime.now()
            ages_hours = []
            stale_count = 0
            
            for ts_str in timestamps:
                try:
                    ts = datetime.fromisoformat(ts_str)
                    age_hours = (now - ts).total_seconds() / 3600
                    ages_hours.append(age_hours)
                    
                    if age_hours > 168:  # 7 days
                        stale_count += 1
                except Exception:
                    continue
            
            total = len(timestamps)
            avg_age = sum(ages_hours) / len(ages_hours) if ages_hours else 0.0
            oldest_age_days = max(ages_hours) / 24 if ages_hours else 0.0
            
            conn.close()
            
            return (total, avg_age, oldest_age_days, stale_count)
        
        except Exception as e:
            logger.warning(f"Failed to get age distribution: {e}")
            return (0, 0.0, 0.0, 0)
    
    def _get_overall_hit_rate(self) -> float:
        """Get overall cache hit rate across all operations."""
        try:
            stats = self.cache.get_stats()
            if stats:
                return stats.get('hit_rate', 0.0)
            return 0.0
        except Exception as e:
            logger.warning(f"Failed to get hit rate: {e}")
            return 0.0
    
    def _check_corruption(self) -> List[str]:
        """
        Check for cache corruption.
        
        Returns:
            List of corruption issues found
        """
        issues = []
        
        try:
            conn = sqlite3.connect(self.cache.cache_db)
            
            # Check integrity
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            if result and result[0] != 'ok':
                issues.append(f"Database corruption detected: {result[0]}")
            
            # Check for orphaned stats
            cursor = conn.execute("""
                SELECT COUNT(*) FROM cache_stats 
                WHERE operation NOT IN (
                    SELECT DISTINCT operation FROM cache_entries
                )
            """)
            orphaned = cursor.fetchone()[0]
            if orphaned > 0:
                issues.append(f"{orphaned} orphaned statistics entries")
            
            # Check for invalid JSON
            cursor = conn.execute("SELECT operation, key, result_json FROM cache_entries")
            invalid_json = 0
            for row in cursor.fetchall():
                try:
                    import json
                    json.loads(row[2])
                except:
                    invalid_json += 1
            
            if invalid_json > 0:
                issues.append(f"{invalid_json} entries with invalid JSON")
            
            conn.close()
        
        except Exception as e:
            issues.append(f"Failed to check corruption: {e}")
        
        return issues
    
    def get_health_summary(self) -> str:
        """
        Get formatted health summary string.
        
        Returns:
            Human-readable health summary
        """
        report = self.check_health()
        
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌'
        }
        
        lines = [
            f"\n{status_emoji[report.overall_status]} Cache Health: {report.overall_status.upper()}",
            f"  Size: {report.cache_size_mb:.2f}MB",
            f"  Entries: {report.total_entries}",
            f"  Hit Rate: {report.hit_rate_overall * 100:.1f}%",
            f"  Avg Age: {report.avg_entry_age_hours:.1f}h",
            f"  Oldest: {report.oldest_entry_age_days:.1f}d",
            f"  Stale: {report.stale_entries}"
        ]
        
        if report.issues:
            lines.append("\nIssues:")
            for issue in report.issues:
                lines.append(f"  • {issue}")
        
        if report.recommendations:
            lines.append("\nRecommendations:")
            for rec in report.recommendations:
                lines.append(f"  • {rec}")
        
        return "\n".join(lines)


def get_cache_health() -> CacheHealthReport:
    """
    Convenience function to get cache health report.
    
    Returns:
        CacheHealthReport
    """
    monitor = CacheHealthMonitor()
    return monitor.check_health()


def print_cache_health():
    """Print cache health summary to console."""
    monitor = CacheHealthMonitor()
    print(monitor.get_health_summary())


def main():
    """CLI entry point for cache health check."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CORTEX Cache Health Monitor'
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        help='Project root directory (auto-detected if not specified)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON instead of formatted text'
    )
    
    args = parser.parse_args()
    
    monitor = CacheHealthMonitor(args.project_root)
    
    if args.json:
        import json
        from dataclasses import asdict
        report = monitor.check_health()
        print(json.dumps(asdict(report), indent=2))
    else:
        print(monitor.get_health_summary())


if __name__ == '__main__':
    main()
