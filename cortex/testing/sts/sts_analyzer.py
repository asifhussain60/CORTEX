"""COMPAT shim — cortex.testing.sts.sts_analyzer → cortex.mcp.tools.sts_analyzer.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/mcp/tools/sts_analyzer.py.
"""
# noqa: F401
from cortex.mcp.tools.sts_analyzer import PatternViolation, PatternDetector, MetricsCalculator, ShowcaseGenerator, analyze_sts_app

__all__ = ["PatternViolation", "PatternDetector", "MetricsCalculator", "ShowcaseGenerator", "analyze_sts_app"]
