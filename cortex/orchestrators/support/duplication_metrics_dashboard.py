"""
DuplicationMetricsDashboard - Real-time metrics and trending for duplication management.

Provides comprehensive metrics tracking:
- Duplication counts by category
- Severity distribution over time
- Resolution rate trends
- Top problem areas
- Consolidation progress

AC_START: IMPL-DuplicationMetricsDashboard-001
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import json

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator
from cortex.brain.core.orchestrator_base import (
    OrchestratorBase,
    OrchestrationContext,
    OrchestrationResult,
    OrchestrationStatus,
)
from cortex.orchestrators.support.duplication_registry import (
    DuplicationRegistry,
    DuplicationRecord,
    SeverityLevel,
    DuplicationStatus,
)


@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time."""
    timestamp: datetime
    total_duplications: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    resolved_count: int
    detected_count: int
    ignored_count: int
    pending_count: int
    by_category: Dict[str, int] = field(default_factory=dict)


class DuplicationMetricsDashboard(OrchestratorBase):
    """
    Metrics dashboard for duplication management and trending.
    
    Tracks metrics over time and provides trend analysis.
    """

    def __init__(self, context: Optional[OrchestrationContext] = None) -> None:
        """Initialize metrics dashboard."""
        if context is None:
            context = OrchestrationContext(
                orchestrator_id="DuplicationMetricsDashboard",
                orchestrator_name="DuplicationMetricsDashboard",
            )
        super().__init__(context)
        self.name = "DuplicationMetricsDashboard"
        self.version = "1.0.0"

        self._registry: Optional[DuplicationRegistry] = None
        self._snapshots: List[MetricSnapshot] = []
        self._retention_days = 30

    def set_registry(self, registry: DuplicationRegistry) -> None:
        """Set the duplication registry to monitor."""
        self._registry = registry

    def capture_snapshot(self) -> MetricSnapshot:
        """Capture current metrics snapshot."""
        if not self._registry:
            raise ValueError("Registry not set")

        stats = self._registry.get_statistics()
        snapshot = MetricSnapshot(
            timestamp=datetime.now(),
            total_duplications=stats['total_duplications'],
            critical_count=stats['severity_distribution'].get('CRITICAL', 0),
            high_count=stats['severity_distribution'].get('HIGH', 0),
            medium_count=stats['severity_distribution'].get('MEDIUM', 0),
            low_count=stats['severity_distribution'].get('LOW', 0),
            resolved_count=stats['status_distribution'].get('RESOLVED', 0),
            detected_count=stats['status_distribution'].get('DETECTED', 0),
            ignored_count=stats['status_distribution'].get('IGNORED', 0),
            pending_count=stats['status_distribution'].get('PENDING_REVIEW', 0),
            by_category=stats['category_distribution'],
        )
        self._snapshots.append(snapshot)
        self._cleanup_old_snapshots()
        return snapshot

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        if not self._registry:
            raise ValueError("Registry not set")

        stats = self._registry.get_statistics()
        return {
            'timestamp': datetime.now().isoformat(),
            'total_duplications': stats['total_duplications'],
            'by_severity': stats['severity_distribution'],
            'by_status': stats['status_distribution'],
            'by_category': stats['category_distribution'],
            'average_confidence': stats['average_confidence'],
        }

    def get_trend(self, days: int = 7) -> Dict[str, Any]:
        """Get trend data for last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_snapshots = [s for s in self._snapshots if s.timestamp >= cutoff]

        if not recent_snapshots:
            return {'error': 'No snapshots available', 'snapshots': []}

        return {
            'period_days': days,
            'snapshots': len(recent_snapshots),
            'first_snapshot': recent_snapshots[0].timestamp.isoformat(),
            'last_snapshot': recent_snapshots[-1].timestamp.isoformat(),
            'data': [
                {
                    'timestamp': s.timestamp.isoformat(),
                    'total': s.total_duplications,
                    'resolved': s.resolved_count,
                    'critical': s.critical_count,
                }
                for s in recent_snapshots
            ],
        }

    def get_category_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get severity distribution by category."""
        if not self._registry:
            raise ValueError("Registry not set")

        breakdown: Dict[str, Dict[str, int]] = {}
        for record in self._registry.get_all():
            if record.category not in breakdown:
                breakdown[record.category] = {
                    'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0
                }
            breakdown[record.category][record.severity.value] += 1

        return breakdown

    def get_resolution_rate(self) -> Dict[str, Any]:
        """Get resolution rate metrics."""
        if not self._registry:
            raise ValueError("Registry not set")

        stats = self._registry.get_statistics()
        total = stats['total_duplications']
        resolved = stats['status_distribution'].get('RESOLVED', 0)
        rate = (resolved / total * 100) if total > 0 else 0

        return {
            'total_duplications': total,
            'resolved': resolved,
            'pending': total - resolved,
            'resolution_rate_percent': round(rate, 2),
        }

    def get_top_problem_categories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top N problem categories."""
        if not self._registry:
            raise ValueError("Registry not set")

        breakdown = self.get_category_breakdown()
        categories = []

        for cat, sev_counts in breakdown.items():
            categories.append({
                'category': cat,
                'total': sum(sev_counts.values()),
                'critical': sev_counts.get('CRITICAL', 0),
                'high': sev_counts.get('HIGH', 0),
                'medium': sev_counts.get('MEDIUM', 0),
                'low': sev_counts.get('LOW', 0),
            })

        categories.sort(key=lambda x: (x['critical'], x['total']), reverse=True)
        return categories[:limit]

    def export_metrics(self, file_path: Path) -> None:
        """Export metrics to JSON file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            'generated_at': datetime.now().isoformat(),
            'current_metrics': self.get_current_metrics(),
            'category_breakdown': self.get_category_breakdown(),
            'resolution_rate': self.get_resolution_rate(),
            'top_categories': self.get_top_problem_categories(),
            'trend_7d': self.get_trend(days=7),
        }

        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)

    def _cleanup_old_snapshots(self) -> None:
        """Remove snapshots older than retention period."""
        cutoff = datetime.now() - timedelta(days=self._retention_days)
        self._snapshots = [s for s in self._snapshots if s.timestamp >= cutoff]

    async def execute(self, context: OrchestrationContext) -> OrchestrationResult:
        """Execute the dashboard orchestrator."""
        try:
            metrics = self.get_current_metrics()
            return OrchestrationResult(
                status=OrchestrationStatus.SUCCESS,
                data=metrics,
            )
        except Exception as e:
            return OrchestrationResult(
                status=OrchestrationStatus.FAILED,
                data={'error': str(e)},
            )

    def __repr__(self) -> str:
        """String representation."""
        return f"DuplicationMetricsDashboard(snapshots={len(self._snapshots)})"


# AC_COMPLETE: IMPL-DuplicationMetricsDashboard-001
