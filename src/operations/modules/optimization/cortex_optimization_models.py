"""
Optimization Metrics Models

Data models for CORTEX optimization orchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List


@dataclass
class OptimizationMetrics:
    """Metrics collected during optimization execution."""
    optimization_id: str
    timestamp: datetime
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    issues_identified: int = 0
    optimizations_applied: int = 0
    optimizations_succeeded: int = 0
    optimizations_failed: int = 0
    doc_deduplication_count: int = 0
    git_commits: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    improvements: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
