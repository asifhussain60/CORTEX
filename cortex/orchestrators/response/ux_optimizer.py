"""UX Optimizer

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class ResponseQualityMetrics:
    """Response quality metrics."""
    clarity_score: float = 0.0
    relevance_score: float = 0.0
    completeness_score: float = 0.0

__all__ = ["ResponseQualityMetrics"]
