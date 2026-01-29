"""
SPA (Single Page Application) infrastructure for LENS Dashboard.

Provides self-contained frontend with zero external CDN dependencies.
"""

from cortex.visualization.spa.dependency_bundler import (
    DependencyBundler,
    Dependency,
    bundle_dependencies,
)

__all__ = [
    "DependencyBundler",
    "Dependency",
    "bundle_dependencies",
]
