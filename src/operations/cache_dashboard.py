"""
Cache Performance Dashboard
Display cache statistics, effectiveness metrics, and recommendations

Shows:
- Hit rates by operation (align, deploy, optimize, cleanup)
- Cache size and entry age distribution
- Performance impact (time saved)
- Recommendations for optimization

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logging.warning("Rich not available - dashboard will use plain text output")

from src.caching import get_cache

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Cache metrics for an operation."""
    operation: str
    total_entries: int
    hits: int
    misses: int
    hit_rate: float
    avg_entry_age_hours: float
    oldest_entry_days: float
    cache_size_mb: float
    estimated_time_saved_seconds: float


class CacheDashboard:
    """
    Cache performance dashboard with Rich visualization.
    
    Provides comprehensive view of:
    - Cache effectiveness (hit rates)
    - Cache health (size, age, staleness)
    - Performance impact (time saved)
    - Optimization recommendations
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize cache dashboard.
        
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
        self.console = Console() if RICH_AVAILABLE else None
    
    def show_dashboard(self, detailed: bool = False):
        """
        Display cache performance dashboard.
        
        Args:
            detailed: Show detailed per-key statistics
        """
        if RICH_AVAILABLE:
            self._show_rich_dashboard(detailed)
        else:
            self._show_plain_dashboard(detailed)
    
    def _show_rich_dashboard(self, detailed: bool):
        """Show dashboard with Rich formatting."""
        self.console.clear()
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]🚀 CORTEX ValidationCache Performance Dashboard[/bold cyan]",
            border_style="cyan"
        ))
        self.console.print()
        
        # Collect metrics for all operations
        operations = ['align', 'deploy', 'optimize', 'cleanup']
        metrics = []
        
        for operation in operations:
            op_metrics = self._get_operation_metrics(operation)
            if op_metrics:
                metrics.append(op_metrics)
        
        if not metrics:
            self.console.print("[yellow]⚠️  No cache data available. Run some operations first.[/yellow]")
            return
        
        # Table 1: Cache Effectiveness
        self._show_effectiveness_table(metrics)
        self.console.print()
        
        # Table 2: Cache Health
        self._show_health_table(metrics)
        self.console.print()
        
        # Table 3: Performance Impact
        self._show_performance_table(metrics)
        self.console.print()
        
        # Recommendations
        self._show_recommendations(metrics)
        self.console.print()
        
        # Detailed view (if requested)
        if detailed:
            self._show_detailed_stats()
            self.console.print()
    
    def _show_effectiveness_table(self, metrics: List[CacheMetrics]):
        """Display cache effectiveness table."""
        table = Table(
            title="📊 Cache Effectiveness",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Operation", style="cyan", no_wrap=True)
        table.add_column("Entries", justify="right", style="white")
        table.add_column("Hits", justify="right", style="green")
        table.add_column("Misses", justify="right", style="yellow")
        table.add_column("Hit Rate", justify="right", style="bold")
        table.add_column("Status", justify="center")
        
        for m in metrics:
            hit_rate_pct = m.hit_rate * 100
            
            # Color code hit rate
            if hit_rate_pct >= 80:
                hit_rate_str = f"[bold green]{hit_rate_pct:.1f}%[/bold green]"
                status = "[green]✓ Excellent[/green]"
            elif hit_rate_pct >= 60:
                hit_rate_str = f"[green]{hit_rate_pct:.1f}%[/green]"
                status = "[yellow]⚠ Good[/yellow]"
            elif hit_rate_pct >= 40:
                hit_rate_str = f"[yellow]{hit_rate_pct:.1f}%[/yellow]"
                status = "[yellow]⚠ Fair[/yellow]"
            else:
                hit_rate_str = f"[red]{hit_rate_pct:.1f}%[/red]"
                status = "[red]✗ Poor[/red]"
            
            table.add_row(
                m.operation.capitalize(),
                str(m.total_entries),
                str(m.hits),
                str(m.misses),
                hit_rate_str,
                status
            )
        
        self.console.print(table)
    
    def _show_health_table(self, metrics: List[CacheMetrics]):
        """Display cache health table."""
        table = Table(
            title="🏥 Cache Health",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Operation", style="cyan", no_wrap=True)
        table.add_column("Size (MB)", justify="right", style="white")
        table.add_column("Avg Age", justify="right", style="white")
        table.add_column("Oldest Entry", justify="right", style="white")
        table.add_column("Freshness", justify="center")
        
        for m in metrics:
            # Format age
            if m.avg_entry_age_hours < 1:
                avg_age_str = f"{m.avg_entry_age_hours * 60:.0f}m"
            else:
                avg_age_str = f"{m.avg_entry_age_hours:.1f}h"
            
            if m.oldest_entry_days < 1:
                oldest_str = f"{m.oldest_entry_days * 24:.1f}h"
            else:
                oldest_str = f"{m.oldest_entry_days:.1f}d"
            
            # Freshness indicator
            if m.oldest_entry_days < 1:
                freshness = "[green]✓ Fresh[/green]"
            elif m.oldest_entry_days < 7:
                freshness = "[yellow]⚠ Aging[/yellow]"
            else:
                freshness = "[red]✗ Stale[/red]"
            
            table.add_row(
                m.operation.capitalize(),
                f"{m.cache_size_mb:.2f}",
                avg_age_str,
                oldest_str,
                freshness
            )
        
        self.console.print(table)
    
    def _show_performance_table(self, metrics: List[CacheMetrics]):
        """Display performance impact table."""
        table = Table(
            title="⚡ Performance Impact",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Operation", style="cyan", no_wrap=True)
        table.add_column("Time Saved", justify="right", style="green")
        table.add_column("Est. Speedup", justify="right", style="bold")
        table.add_column("Impact", justify="center")
        
        total_time_saved = 0
        
        for m in metrics:
            time_saved = m.estimated_time_saved_seconds
            total_time_saved += time_saved
            
            # Format time saved
            if time_saved < 60:
                time_str = f"{time_saved:.1f}s"
            elif time_saved < 3600:
                time_str = f"{time_saved / 60:.1f}m"
            else:
                time_str = f"{time_saved / 3600:.1f}h"
            
            # Estimate speedup based on hit rate
            if m.hit_rate > 0:
                # Assume average operation time: align=70s, deploy=150s, optimize=45s, cleanup=22s
                base_times = {'align': 70, 'deploy': 150, 'optimize': 45, 'cleanup': 22}
                base_time = base_times.get(m.operation, 60)
                speedup = 1 / (1 - m.hit_rate * 0.9) if m.hit_rate > 0.1 else 1.0
                speedup_str = f"{speedup:.1f}x"
            else:
                speedup_str = "1.0x"
            
            # Impact indicator
            if time_saved > 300:
                impact = "[green]🔥 High[/green]"
            elif time_saved > 60:
                impact = "[yellow]⚡ Medium[/yellow]"
            elif time_saved > 10:
                impact = "[blue]💨 Low[/blue]"
            else:
                impact = "[dim]• Minimal[/dim]"
            
            table.add_row(
                m.operation.capitalize(),
                time_str,
                speedup_str,
                impact
            )
        
        # Add total row
        if total_time_saved > 60:
            total_str = f"{total_time_saved / 60:.1f}m"
        else:
            total_str = f"{total_time_saved:.1f}s"
        
        table.add_section()
        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{total_str}[/bold green]",
            "",
            ""
        )
        
        self.console.print(table)
    
    def _show_recommendations(self, metrics: List[CacheMetrics]):
        """Display optimization recommendations."""
        recommendations = []
        
        for m in metrics:
            # Low hit rate
            if m.hit_rate < 0.4 and m.total_entries > 0:
                recommendations.append(
                    f"[yellow]⚠[/yellow] {m.operation.capitalize()}: Low hit rate ({m.hit_rate * 100:.1f}%). "
                    f"Consider running this operation more frequently or checking for cache invalidation issues."
                )
            
            # Stale entries
            if m.oldest_entry_days > 7:
                recommendations.append(
                    f"[yellow]⚠[/yellow] {m.operation.capitalize()}: Stale entries detected "
                    f"(oldest: {m.oldest_entry_days:.1f}d). Consider clearing old cache: `cortex cache clear {m.operation}`"
                )
            
            # Large cache size
            if m.cache_size_mb > 50:
                recommendations.append(
                    f"[yellow]⚠[/yellow] {m.operation.capitalize()}: Large cache size ({m.cache_size_mb:.1f}MB). "
                    f"Consider periodic cleanup to free disk space."
                )
            
            # Excellent performance
            if m.hit_rate > 0.8 and m.total_entries > 5:
                recommendations.append(
                    f"[green]✓[/green] {m.operation.capitalize()}: Excellent cache performance ({m.hit_rate * 100:.1f}% hit rate). "
                    f"Saved ~{m.estimated_time_saved_seconds:.0f}s!"
                )
        
        if not recommendations:
            recommendations.append("[green]✓ Cache is healthy! No issues detected.[/green]")
        
        panel = Panel(
            "\n".join(recommendations),
            title="💡 Recommendations",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _show_detailed_stats(self):
        """Show detailed per-key statistics."""
        self.console.print("[bold cyan]📋 Detailed Statistics (All Cache Keys)[/bold cyan]")
        self.console.print()
        
        operations = ['align', 'deploy', 'optimize', 'cleanup']
        
        for operation in operations:
            keys = self.cache.get_all_keys(operation)
            
            if not keys:
                continue
            
            table = Table(
                title=f"{operation.capitalize()} Operation Keys",
                box=box.SIMPLE,
                show_header=True,
                header_style="bold white"
            )
            
            table.add_column("Cache Key", style="cyan")
            table.add_column("Age", justify="right", style="white")
            table.add_column("File Tracking", justify="center", style="white")
            
            for key in keys[:10]:  # Show first 10 keys
                # Get entry details (would need to query DB directly)
                table.add_row(key, "—", "✓")
            
            if len(keys) > 10:
                table.add_row(f"[dim]... and {len(keys) - 10} more keys[/dim]", "", "")
            
            self.console.print(table)
            self.console.print()
    
    def _get_operation_metrics(self, operation: str) -> Optional[CacheMetrics]:
        """
        Get metrics for a specific operation.
        
        Args:
            operation: Operation name
        
        Returns:
            CacheMetrics or None if no data
        """
        stats = self.cache.get_stats(operation)
        
        if not stats or stats.get('total', 0) == 0:
            return None
        
        hits = stats.get('hits', 0)
        misses = stats.get('misses', 0)
        total = hits + misses
        hit_rate = hits / total if total > 0 else 0.0
        
        # Get cache size and age from database
        cache_size_mb, avg_age_hours, oldest_days = self._query_cache_health(operation)
        
        # Estimate time saved (assume 2-3s per cache hit)
        estimated_time_saved = hits * 2.5
        
        return CacheMetrics(
            operation=operation,
            total_entries=stats.get('total', 0),
            hits=hits,
            misses=misses,
            hit_rate=hit_rate,
            avg_entry_age_hours=avg_age_hours,
            oldest_entry_days=oldest_days,
            cache_size_mb=cache_size_mb,
            estimated_time_saved_seconds=estimated_time_saved
        )
    
    def _query_cache_health(self, operation: str) -> tuple:
        """
        Query cache database for health metrics.
        
        Args:
            operation: Operation name
        
        Returns:
            (size_mb, avg_age_hours, oldest_days)
        """
        try:
            conn = sqlite3.connect(self.cache.cache_db)
            
            # Get total size
            cursor = conn.execute(
                "SELECT SUM(LENGTH(result_json) + LENGTH(file_hashes_json)) FROM cache_entries WHERE operation = ?",
                (operation,)
            )
            total_bytes = cursor.fetchone()[0] or 0
            size_mb = total_bytes / (1024 * 1024)
            
            # Get age statistics
            cursor = conn.execute(
                "SELECT timestamp FROM cache_entries WHERE operation = ? ORDER BY timestamp DESC",
                (operation,)
            )
            timestamps = [row[0] for row in cursor.fetchall()]
            
            if not timestamps:
                conn.close()
                return (0.0, 0.0, 0.0)
            
            now = datetime.now()
            ages = [(now - datetime.fromisoformat(ts)).total_seconds() / 3600 for ts in timestamps]
            
            avg_age_hours = sum(ages) / len(ages) if ages else 0.0
            oldest_days = max(ages) / 24 if ages else 0.0
            
            conn.close()
            
            return (size_mb, avg_age_hours, oldest_days)
        
        except Exception as e:
            logger.warning(f"Failed to query cache health: {e}")
            return (0.0, 0.0, 0.0)
    
    def _show_plain_dashboard(self, detailed: bool):
        """Show dashboard with plain text formatting (fallback)."""
        print("\n" + "=" * 80)
        print("CORTEX ValidationCache Performance Dashboard".center(80))
        print("=" * 80 + "\n")
        
        operations = ['align', 'deploy', 'optimize', 'cleanup']
        metrics = []
        
        for operation in operations:
            op_metrics = self._get_operation_metrics(operation)
            if op_metrics:
                metrics.append(op_metrics)
        
        if not metrics:
            print("⚠️  No cache data available. Run some operations first.\n")
            return
        
        # Cache Effectiveness
        print("📊 Cache Effectiveness")
        print("-" * 80)
        print(f"{'Operation':<15} {'Entries':>10} {'Hits':>10} {'Misses':>10} {'Hit Rate':>12} {'Status':>15}")
        print("-" * 80)
        
        for m in metrics:
            hit_rate_pct = m.hit_rate * 100
            status = "Excellent" if hit_rate_pct >= 80 else "Good" if hit_rate_pct >= 60 else "Fair" if hit_rate_pct >= 40 else "Poor"
            print(f"{m.operation.capitalize():<15} {m.total_entries:>10} {m.hits:>10} {m.misses:>10} {hit_rate_pct:>10.1f}% {status:>15}")
        
        print("\n")
        
        # Performance Impact
        print("⚡ Performance Impact")
        print("-" * 80)
        print(f"{'Operation':<15} {'Time Saved':>15} {'Est. Speedup':>15}")
        print("-" * 80)
        
        total_time_saved = 0
        for m in metrics:
            time_saved = m.estimated_time_saved_seconds
            total_time_saved += time_saved
            
            time_str = f"{time_saved:.1f}s" if time_saved < 60 else f"{time_saved / 60:.1f}m"
            
            if m.hit_rate > 0:
                base_times = {'align': 70, 'deploy': 150, 'optimize': 45, 'cleanup': 22}
                base_time = base_times.get(m.operation, 60)
                speedup = 1 / (1 - m.hit_rate * 0.9) if m.hit_rate > 0.1 else 1.0
                speedup_str = f"{speedup:.1f}x"
            else:
                speedup_str = "1.0x"
            
            print(f"{m.operation.capitalize():<15} {time_str:>15} {speedup_str:>15}")
        
        total_str = f"{total_time_saved:.1f}s" if total_time_saved < 60 else f"{total_time_saved / 60:.1f}m"
        print("-" * 80)
        print(f"{'TOTAL':<15} {total_str:>15}")
        
        print("\n" + "=" * 80 + "\n")


def main():
    """CLI entry point for cache dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CORTEX Cache Performance Dashboard'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed per-key statistics'
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        help='Project root directory (auto-detected if not specified)'
    )
    
    args = parser.parse_args()
    
    dashboard = CacheDashboard(args.project_root)
    dashboard.show_dashboard(detailed=args.detailed)


if __name__ == '__main__':
    main()
