"""
Design Sync Models

Data models for Design Sync Orchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


@dataclass
class ImplementationState:
    """Current implementation reality."""
    operations: Dict[str, Dict] = field(default_factory=dict)
    modules: Dict[str, Path] = field(default_factory=dict)
    tests: Dict[str, int] = field(default_factory=dict)
    plugins: List[str] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)
    total_modules: int = 0
    implemented_modules: int = 0
    completion_percentage: float = 0.0


@dataclass
class DesignState:
    """Design document state."""
    version: str = "2.0"
    design_files: List[Path] = field(default_factory=list)
    status_files: List[Path] = field(default_factory=list)
    md_documents: List[Path] = field(default_factory=list)
    yaml_documents: List[Path] = field(default_factory=list)


@dataclass
class GapAnalysis:
    """Gaps between design and implementation."""
    overclaimed_completions: List[str] = field(default_factory=list)
    underclaimed_completions: List[str] = field(default_factory=list)
    missing_documentation: List[str] = field(default_factory=list)
    inconsistent_counts: List[Dict[str, Any]] = field(default_factory=list)
    redundant_status_files: List[Path] = field(default_factory=list)
    verbose_md_candidates: List[Path] = field(default_factory=list)


@dataclass
class SyncMetrics:
    """Metrics collected during sync."""
    sync_id: str
    timestamp: datetime
    implementation_discovered: bool = False
    gaps_analyzed: int = 0
    optimizations_integrated: int = 0
    md_to_yaml_converted: int = 0
    status_files_consolidated: int = 0
    git_commits: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)
    improvements: Dict[str, Any] = field(default_factory=dict)
