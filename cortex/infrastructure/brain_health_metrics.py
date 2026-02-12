"""
Brain Health Metrics - Prometheus Integration.

AC-PHASE38-002: Prometheus metrics export for brain health

Exports 6 Prometheus gauges:
1. cache_staleness_ratio
2. connectivity_score
3. knowledge_freshness
4. governance_coverage
5. domain_utilization
6. aggregate_health_score

Usage:
    metrics = BrainHealthMetrics()
    metrics.update_dimensions({
        'cache_staleness_ratio': 0.15,
        'connectivity_score': 95.0,
        ...
    })
    prometheus_text = metrics.export_prometheus()
"""

from typing import Any, Dict

from prometheus_client import CollectorRegistry, Gauge, generate_latest


class BrainHealthMetrics:
    """
    Prometheus metrics for CORTEX brain health monitoring.

    Provides real-time observability of brain cohesion and health dimensions.
    """

    def __init__(self, registry: CollectorRegistry = None):
        """
        Initialize Prometheus gauges for all health dimensions.

        Args:
            registry: Optional custom registry (defaults to new instance for testing)
        """
        self.registry = registry or CollectorRegistry()

        self.cache_staleness_gauge = Gauge(
            'cortex_brain_cache_staleness_ratio',
            'Ratio of stale cache entries (0.0-1.0, healthy: <=0.2)',
            registry=self.registry
        )

        self.connectivity_score_gauge = Gauge(
            'cortex_brain_connectivity_score',
            'Orchestrator connectivity health (0-100, healthy: >=90)',
            registry=self.registry
        )

        self.knowledge_freshness_gauge = Gauge(
            'cortex_brain_knowledge_freshness',
            'Knowledge freshness index (0-100, healthy: >=60)',
            registry=self.registry
        )

        self.governance_coverage_gauge = Gauge(
            'cortex_brain_governance_coverage',
            'Governance rule monitoring coverage (0-100, healthy: >=80)',
            registry=self.registry
        )

        self.domain_utilization_gauge = Gauge(
            'cortex_brain_domain_utilization',
            'Company domain utilization rate (0-100, healthy: >=50)',
            registry=self.registry
        )

        self.aggregate_health_score_gauge = Gauge(
            'cortex_brain_aggregate_health_score',
            'Overall brain health score (0-100)',
            registry=self.registry
        )

    def update_dimensions(self, dimensions: Dict[str, float]) -> None:
        """
        Update all health dimension gauges with new values.

        Args:
            dimensions: Dict with keys matching health dimensions
        """
        if 'cache_staleness_ratio' in dimensions:
            self.cache_staleness_gauge.set(dimensions['cache_staleness_ratio'])

        if 'connectivity_score' in dimensions:
            self.connectivity_score_gauge.set(dimensions['connectivity_score'])

        if 'knowledge_freshness' in dimensions:
            self.knowledge_freshness_gauge.set(dimensions['knowledge_freshness'])

        if 'governance_coverage' in dimensions:
            self.governance_coverage_gauge.set(dimensions['governance_coverage'])

        if 'domain_utilization' in dimensions:
            self.domain_utilization_gauge.set(dimensions['domain_utilization'])

        # Calculate aggregate if all dimensions present
        if all(k in dimensions for k in ['cache_staleness_ratio', 'connectivity_score',
                                         'knowledge_freshness', 'governance_coverage',
                                         'domain_utilization']):
            aggregate = self._calculate_aggregate(dimensions)
            self.aggregate_health_score_gauge.set(aggregate)

    def _calculate_aggregate(self, dimensions: Dict[str, float]) -> float:
        """
        Calculate aggregate health score from dimensions.

        Weighted formula (normalized to 0-100):
        - Cache staleness (inverted, 20%): (1 - ratio) * 100 * 0.20
        - Connectivity (25%): score * 0.25
        - Knowledge freshness (20%): freshness * 0.20
        - Governance coverage (20%): coverage * 0.20
        - Domain utilization (15%): utilization * 0.15
        """
        cache_score = (1 - dimensions['cache_staleness_ratio']) * 100 * 0.20
        connectivity_score = dimensions['connectivity_score'] * 0.25
        knowledge_score = dimensions['knowledge_freshness'] * 0.20
        governance_score = dimensions['governance_coverage'] * 0.20
        domain_score = dimensions['domain_utilization'] * 0.15

        return cache_score + connectivity_score + knowledge_score + governance_score + domain_score

    def export_prometheus(self) -> str:
        """
        Export all metrics in Prometheus text format.

        Returns:
            Prometheus-formatted metrics string
        """
        return generate_latest(self.registry).decode('utf-8')


# AC-PHASE38-002 ✅ Implementation complete
