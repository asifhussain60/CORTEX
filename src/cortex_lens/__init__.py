"""
CORTEX Lens - Universal Repository Intelligence Platform

Self-contained tool for analyzing any codebase and generating
adaptive static dashboards.

Example:
    >>> from cortex_lens import CortexLens
    >>> lens = CortexLens()
    >>> result = lens.analyze('/path/to/repo')
    >>> print(result['dashboard_path'])

Version: 1.0.0
Author: Asif Hussain
"""

__version__ = '1.0.0'
__author__ = 'Asif Hussain'

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    """Lazy import to avoid loading heavy modules at import time."""
    if name == 'CortexLens':
        from .orchestrator import CortexLens
        return CortexLens
    elif name == 'RepoTypeClassifier':
        from .core.classifier import RepoTypeClassifier
        return RepoTypeClassifier
    elif name == 'AnalyzerRegistry':
        from .analyzers.registry import AnalyzerRegistry
        return AnalyzerRegistry
    elif name == 'CollectorRegistry':
        from .collectors.registry import CollectorRegistry
        return CollectorRegistry
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'CortexLens',
    'RepoTypeClassifier',
    'AnalyzerRegistry',
    'CollectorRegistry',
]
