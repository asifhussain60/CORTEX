"""
Data collectors for repository analysis.

14+ specialized collectors:
- HealthCollector: File count, LOC, language distribution
- ArchitectureCollector: Layer detection, dependencies
- SecurityCollector: OWASP analysis, vulnerabilities
- TechStackCollector: Technology inventory
- APIEndpointCollector: REST API catalog
- DatabaseSchemaCollector: Tables, views, procedures
- FrontendRoutesCollector: React/Vue/Angular routes
- DependencyCollector: NuGet/NPM packages
- ComplexityCollector: Cyclomatic complexity
- TestCoverageCollector: Coverage by layer
- CommentCollector: Comment extraction
- PerformanceCollector: Hot paths, slow queries
- ComplianceCollector: Regulatory keywords
- OwnershipCollector: Git blame analysis

Registry:
- CollectorRegistry: Execution matrix for repo types
"""

from .base import BaseCollector
from .registry import CollectorRegistry

__all__ = [
    'BaseCollector',
    'CollectorRegistry',
]
