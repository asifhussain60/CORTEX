"""
SPA (Single Page Application) infrastructure for LENS Dashboard.

Provides self-contained frontend with zero external CDN dependencies.
Includes GPT-spec compliant dashboard suite generation.
"""

from cortex.visualization.spa.dependency_bundler import (
    Dependency,
    DependencyBundler,
    bundle_dependencies,
)
from cortex.visualization.spa.models import (
    ArchitectureLayer,
    DashboardSuiteConfig,
    DependencyInfo,
    QualityMetric,
    Recommendation,
    RepoDashboardData,
    RepoManifestEntry,
    Severity,
    TestingMetrics,
    UseCase,
    UseCaseCategory,
    UseCasePersona,
    VulnerabilityFinding,
    to_dict,
)
from cortex.visualization.spa.suite_generator import (
    DashboardSuiteGenerator,
    GenerationResult,
    generate_dashboard_suite,
)

__all__ = [
    # Dependency bundler
    "DependencyBundler",
    "Dependency",
    "bundle_dependencies",
    # Data models
    "Severity",
    "UseCasePersona",
    "UseCaseCategory",
    "UseCase",
    "VulnerabilityFinding",
    "DependencyInfo",
    "QualityMetric",
    "ArchitectureLayer",
    "TestingMetrics",
    "Recommendation",
    "RepoDashboardData",
    "RepoManifestEntry",
    "DashboardSuiteConfig",
    "to_dict",
    # Suite generator
    "DashboardSuiteGenerator",
    "GenerationResult",
    "generate_dashboard_suite",
]
