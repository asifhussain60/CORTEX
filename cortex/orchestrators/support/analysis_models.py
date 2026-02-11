"""
Data structures for UnifiedAnalysisOrchestrator.
====================================================

Shared data classes used by tests and implementation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any


class AnalysisType(Enum):
    """Types of analysis."""
    COMPLEXITY = "complexity"
    SECURITY = "security"
    DEPENDENCIES = "dependencies"
    PERFORMANCE = "performance"


@dataclass
class LENSResult:
    """LENS analysis result."""
    analysis_type: AnalysisType
    score: float
    findings: List[str]
    recommendations: List[str]
    details: Dict[str, Any]


@dataclass
class ToolInfo:
    """Tool discovery information."""
    name: str
    category: str
    description: str
    version: Optional[str]
    installation_command: str
    is_installed: bool


@dataclass
class DependencyGraph:
    """Project dependency graph."""
    nodes: List[str]
    edges: List[tuple]
    has_cycles: bool
    unused_dependencies: List[str]
