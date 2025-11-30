"""
ScanResult - Data class for crawler scan results.

Contains metrics, file information, and analysis data from application crawling.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ScanResult:
    """
    Results from a crawler scan operation.
    
    Attributes:
        root_path: Root directory that was scanned
        scan_level: Scan depth used ("overview", "standard", "deep")
        total_files: Total number of files discovered
        file_types: Dictionary mapping file extensions to counts
        file_paths: List of discovered file paths
        errors: List of error messages encountered during scan
    """
    root_path: str
    scan_level: str
    total_files: int = 0
    file_types: Dict[str, int] = None
    file_paths: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.file_types is None:
            self.file_types = {}
        if self.file_paths is None:
            self.file_paths = []
        if self.errors is None:
            self.errors = []
