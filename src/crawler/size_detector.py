"""
CORTEX Size Detection Engine
Rapidly estimates codebase size to select appropriate crawling strategy

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import os
import pathlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import time


class SizeCategory(Enum):
    """Codebase size categories with corresponding strategies"""
    SMALL = "SMALL"      # <50K LOC
    MEDIUM = "MEDIUM"    # 50K-250K LOC
    LARGE = "LARGE"      # 250K-1M LOC
    MASSIVE = "MASSIVE"  # 1M+ LOC


@dataclass
class SizeEstimate:
    """Results of size estimation"""
    total_files: int
    estimated_loc: int
    size_category: SizeCategory
    file_breakdown: Dict[str, int]  # Extension -> file count
    largest_files: List[Tuple[str, int]]  # (path, estimated LOC)
    detection_time_ms: float
    recommended_strategy: str


class SizeDetector:
    """
    Fast size estimation engine for codebase analysis
    
    Heuristics:
    - Average bytes per line: 40 (typical for code with comments)
    - File size → LOC conversion: file_size_bytes / 40
    - Timeout: 30 seconds maximum for detection
    """
    
    # Average bytes per line of code (empirical)
    AVG_BYTES_PER_LINE = 40
    
    # File extensions to analyze
    CODE_EXTENSIONS = {
        '.py': 'Python',
        '.cs': 'C#',
        '.java': 'Java',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.sql': 'SQL',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'Header',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala'
    }
    
    # Size category thresholds (in LOC)
    THRESHOLDS = {
        SizeCategory.SMALL: (0, 50_000),
        SizeCategory.MEDIUM: (50_000, 250_000),
        SizeCategory.LARGE: (250_000, 1_000_000),
        SizeCategory.MASSIVE: (1_000_000, float('inf'))
    }
    
    # Strategy recommendations
    STRATEGIES = {
        SizeCategory.SMALL: "Full Analysis",
        SizeCategory.MEDIUM: "Chunked Analysis",
        SizeCategory.LARGE: "Sampling + Chunking (20% sample)",
        SizeCategory.MASSIVE: "Intelligent Sampling (5% sample)"
    }
    
    def __init__(self, timeout_seconds: int = 30):
        """
        Initialize size detector
        
        Args:
            timeout_seconds: Maximum time for detection (default: 30s)
        """
        self.timeout_seconds = timeout_seconds
        self.start_time = None
    
    def detect(self, root_path: str, extensions: Optional[List[str]] = None) -> SizeEstimate:
        """
        Detect codebase size and recommend crawling strategy
        
        Args:
            root_path: Root directory to analyze
            extensions: Optional list of extensions to focus on (default: all CODE_EXTENSIONS)
        
        Returns:
            SizeEstimate with detection results
        
        Raises:
            TimeoutError: If detection exceeds timeout_seconds
            ValueError: If root_path doesn't exist
        """
        if not os.path.exists(root_path):
            raise ValueError(f"Path does not exist: {root_path}")
        
        self.start_time = time.time()
        
        # Use provided extensions or default to all
        target_extensions = set(extensions) if extensions else set(self.CODE_EXTENSIONS.keys())
        
        total_files = 0
        total_bytes = 0
        file_breakdown = {ext: 0 for ext in target_extensions}
        largest_files = []  # (path, estimated_loc)
        
        # Walk directory tree with timeout check
        for root, dirs, files in os.walk(root_path):
            # Check timeout
            if self._is_timeout():
                break
            
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]
            
            for file in files:
                ext = pathlib.Path(file).suffix.lower()
                
                if ext in target_extensions:
                    file_path = os.path.join(root, file)
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        estimated_loc = self._estimate_loc(file_size)
                        
                        total_files += 1
                        total_bytes += file_size
                        file_breakdown[ext] = file_breakdown.get(ext, 0) + 1
                        
                        # Track largest files (top 10)
                        largest_files.append((file_path, estimated_loc))
                        if len(largest_files) > 10:
                            largest_files.sort(key=lambda x: x[1], reverse=True)
                            largest_files = largest_files[:10]
                        
                    except (OSError, PermissionError):
                        # Skip files we can't read
                        continue
        
        # Calculate total estimated LOC
        estimated_loc = self._estimate_loc(total_bytes)
        
        # Determine size category
        size_category = self._categorize_size(estimated_loc)
        
        # Calculate detection time
        detection_time_ms = (time.time() - self.start_time) * 1000
        
        return SizeEstimate(
            total_files=total_files,
            estimated_loc=estimated_loc,
            size_category=size_category,
            file_breakdown=file_breakdown,
            largest_files=sorted(largest_files, key=lambda x: x[1], reverse=True),
            detection_time_ms=detection_time_ms,
            recommended_strategy=self.STRATEGIES[size_category]
        )
    
    def _estimate_loc(self, file_size_bytes: int) -> int:
        """
        Estimate lines of code from file size
        
        Args:
            file_size_bytes: File size in bytes
        
        Returns:
            Estimated lines of code
        """
        return max(1, file_size_bytes // self.AVG_BYTES_PER_LINE)
    
    def _categorize_size(self, estimated_loc: int) -> SizeCategory:
        """
        Categorize codebase size
        
        Args:
            estimated_loc: Estimated total lines of code
        
        Returns:
            Size category
        """
        for category, (min_loc, max_loc) in self.THRESHOLDS.items():
            if min_loc <= estimated_loc < max_loc:
                return category
        
        return SizeCategory.MASSIVE  # Default to massive for safety
    
    def _should_skip_dir(self, dirname: str) -> bool:
        """
        Check if directory should be skipped during scanning
        
        Args:
            dirname: Directory name
        
        Returns:
            True if directory should be skipped
        """
        skip_patterns = {
            'node_modules', '__pycache__', '.git', '.svn', '.hg',
            'bin', 'obj', 'build', 'dist', 'target', '.pytest_cache',
            '.venv', 'venv', 'env', '.env', 'coverage', '.coverage',
            '.tox', '.mypy_cache', '.gradle', '.idea', '.vscode'
        }
        return dirname in skip_patterns or dirname.startswith('.')
    
    def _is_timeout(self) -> bool:
        """
        Check if timeout has been reached
        
        Returns:
            True if timeout exceeded
        """
        if self.start_time is None:
            return False
        
        elapsed = time.time() - self.start_time
        return elapsed >= self.timeout_seconds
    
    def format_estimate(self, estimate: SizeEstimate) -> str:
        """
        Format size estimate for user display
        
        Args:
            estimate: Size estimate results
        
        Returns:
            Formatted string for display
        """
        lines = [
            f"🔍 Detected codebase size: ~{estimate.estimated_loc:,} LOC ({estimate.size_category.value})",
            f"📊 Strategy: {estimate.recommended_strategy}",
            f"⏱️ Detection time: {estimate.detection_time_ms:.0f}ms",
            "",
            f"📂 Files analyzed: {estimate.total_files:,}",
            ""
        ]
        
        # File breakdown
        if estimate.file_breakdown:
            lines.append("File types:")
            for ext, count in sorted(estimate.file_breakdown.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    lang = self.CODE_EXTENSIONS.get(ext, ext)
                    lines.append(f"  • {lang} ({ext}): {count:,} files")
        
        # Time estimates
        lines.append("")
        lines.append(self._estimate_crawl_time(estimate.size_category))
        
        return "\n".join(lines)
    
    def _estimate_crawl_time(self, category: SizeCategory) -> str:
        """
        Estimate crawl time based on size category
        
        Args:
            category: Size category
        
        Returns:
            Time estimate string
        """
        time_estimates = {
            SizeCategory.SMALL: "⏱️ Estimated time: 2-5 minutes",
            SizeCategory.MEDIUM: "⏱️ Estimated time: 5-15 minutes",
            SizeCategory.LARGE: "⏱️ Estimated time: 8-20 minutes",
            SizeCategory.MASSIVE: "⏱️ Estimated time: 10-30 minutes"
        }
        return time_estimates.get(category, "⏱️ Estimated time: Unknown")
