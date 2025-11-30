"""
Cleanup Operation Data Models

Data classes for cleanup orchestrator metrics and reporting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List


@dataclass
class CleanupMetrics:
    """Metrics from cleanup operation"""
    timestamp: datetime
    backups_deleted: int = 0
    backups_archived: int = 0
    files_reorganized: int = 0
    md_files_consolidated: int = 0
    root_files_cleaned: int = 0
    bloated_files_found: int = 0
    archived_docs_removed: int = 0
    space_freed_bytes: int = 0
    git_commits_created: int = 0
    duration_seconds: float = 0.0
    optimization_triggered: bool = False
    warnings: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
    
    @property
    def space_freed_mb(self) -> float:
        return self.space_freed_bytes / (1024 * 1024)
    
    @property
    def space_freed_gb(self) -> float:
        return self.space_freed_bytes / (1024 * 1024 * 1024)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['space_freed_mb'] = self.space_freed_mb
        data['space_freed_gb'] = self.space_freed_gb
        return data
