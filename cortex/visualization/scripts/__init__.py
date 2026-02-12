"""
CORTEX Visualization Scripts Package.

Provides utility scripts for dashboard setup and management:
- bundle_dependencies: Download and bundle external dependencies
- lazy_module_loader: Optimize module loading with lazy loading

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-007
"""

__version__ = "1.0.0"
__author__ = "Asif Hussain"

from cortex.visualization.scripts.bundle_dependencies import (
    DependencyBundler,
    bundle_dependencies,
    verify_bundle,
)
from cortex.visualization.scripts.lazy_module_loader import (
    LazyModuleLoader,
    get_lazy_loader,
)

__all__ = [
    "DependencyBundler",
    "bundle_dependencies",
    "verify_bundle",
    "LazyModuleLoader",
    "get_lazy_loader",
]
