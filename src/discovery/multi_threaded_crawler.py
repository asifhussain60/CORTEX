"""
Multi-Threading File Crawler for CORTEX

Parallel file system traversal using ThreadPoolExecutor for improved performance.
Target: 50% reduction in scan time for large repositories (1000+ files).

Performance Comparison:
- Sequential: O(n) where n = number of files
- Multi-threaded: O(n/workers) with overhead for thread management

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
from pathlib import Path
from typing import List, Set, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import threading
import time


@dataclass
class CrawlResult:
    """Result of file crawl operation."""
    files: List[Path]
    total_size_bytes: int
    duration_seconds: float
    files_per_second: float


class MultiThreadedCrawler:
    """
    Thread-safe file system crawler with progress callback support.
    
    Uses ThreadPoolExecutor with configurable worker count to parallelize
    directory scanning and file filtering operations.
    
    Example:
        crawler = MultiThreadedCrawler(max_workers=4)
        result = crawler.crawl(
            root_path="src/",
            extensions=[".py", ".js"],
            progress_callback=lambda current, total: print(f"{current}/{total}")
        )
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize multi-threaded crawler.
        
        Args:
            max_workers: Number of concurrent worker threads (default: 4)
        """
        self.max_workers = max_workers
        self.exclusions = {
            'node_modules', 'venv', '.venv', 'env', '__pycache__', '.git',
            'dist', 'build', '.pytest_cache', '.mypy_cache', 'coverage',
            'cortex-brain/archives', 'cortex-brain/cache', '.vs', 'bin', 'obj',
            '.tox', '.eggs', '.idea', '__pypackages__', '.DS_Store'
        }
        
        # Thread-safe counters
        self._lock = threading.Lock()
        self._files_found = 0
        self._total_size = 0
    
    def crawl(
        self,
        root_path: str,
        extensions: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> CrawlResult:
        """
        Crawl directory tree and collect files matching criteria.
        
        Args:
            root_path: Root directory to start crawling
            extensions: Optional list of file extensions (e.g., ['.py', '.js'])
            progress_callback: Optional callback(current, total) for progress updates
        
        Returns:
            CrawlResult with files list, total size, duration, and throughput
        """
        start_time = time.time()
        root = Path(root_path)
        
        if not root.exists():
            return CrawlResult([], 0, 0.0, 0.0)
        
        # Reset counters
        self._files_found = 0
        self._total_size = 0
        
        # Phase 1: Collect all directories (fast, single-threaded)
        directories = self._collect_directories(root)
        
        # Phase 2: Scan directories in parallel (I/O bound, multi-threaded)
        all_files = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit directory scan tasks
            future_to_dir = {
                executor.submit(self._scan_directory, dir_path, extensions): dir_path
                for dir_path in directories
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_dir):
                try:
                    files = future.result()
                    all_files.extend(files)
                    
                    # Update progress
                    if progress_callback:
                        progress_callback(len(all_files), -1)  # -1 means unknown total
                        
                except Exception as e:
                    # Log error but continue processing
                    pass
        
        # Phase 3: Calculate statistics
        duration = time.time() - start_time
        files_per_second = len(all_files) / duration if duration > 0 else 0
        
        return CrawlResult(
            files=all_files,
            total_size_bytes=self._total_size,
            duration_seconds=duration,
            files_per_second=files_per_second
        )
    
    def _collect_directories(self, root: Path) -> List[Path]:
        """
        Collect all directories to scan (single-threaded, fast).
        
        Args:
            root: Root directory to start from
        
        Returns:
            List of directories to scan
        """
        directories = [root]
        
        try:
            for entry in root.rglob('*'):
                if entry.is_dir() and not self._should_exclude(entry):
                    directories.append(entry)
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass
        
        return directories
    
    def _scan_directory(self, directory: Path, extensions: Optional[List[str]]) -> List[Path]:
        """
        Scan a single directory for files matching criteria.
        
        This method is called in parallel by worker threads.
        
        Args:
            directory: Directory to scan
            extensions: Optional list of file extensions to match
        
        Returns:
            List of matching files in this directory
        """
        files = []
        
        try:
            for entry in directory.iterdir():
                # Only process files, not subdirectories (subdirs handled separately)
                if entry.is_file():
                    # Check extension filter
                    if extensions is None or entry.suffix in extensions:
                        # Thread-safe file addition
                        with self._lock:
                            self._files_found += 1
                            try:
                                file_size = entry.stat().st_size
                                self._total_size += file_size
                            except (PermissionError, OSError):
                                pass
                        
                        files.append(entry)
        
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass
        
        return files
    
    def _should_exclude(self, path: Path) -> bool:
        """
        Check if path should be excluded based on exclusion patterns.
        
        Args:
            path: Path to check
        
        Returns:
            True if path should be excluded, False otherwise
        """
        # Check if any part of path matches exclusion patterns
        parts = set(path.parts)
        return bool(parts.intersection(self.exclusions))
    
    def add_exclusion(self, pattern: str) -> None:
        """
        Add custom exclusion pattern.
        
        Args:
            pattern: Directory or file name pattern to exclude
        """
        self.exclusions.add(pattern)
    
    def remove_exclusion(self, pattern: str) -> None:
        """
        Remove exclusion pattern.
        
        Args:
            pattern: Pattern to remove from exclusions
        """
        self.exclusions.discard(pattern)
    
    def get_exclusions(self) -> Set[str]:
        """
        Get current exclusion patterns.
        
        Returns:
            Set of exclusion patterns
        """
        return self.exclusions.copy()


def crawl_repository(
    root_path: str,
    extensions: Optional[List[str]] = None,
    max_workers: int = 4,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> CrawlResult:
    """
    Convenience function for repository crawling.
    
    Args:
        root_path: Root directory to crawl
        extensions: Optional list of file extensions (e.g., ['.py', '.js'])
        max_workers: Number of concurrent worker threads
        progress_callback: Optional progress callback function
    
    Returns:
        CrawlResult with files, size, duration, and throughput
    
    Example:
        result = crawl_repository(
            "src/",
            extensions=[".py"],
            max_workers=4,
            progress_callback=lambda curr, total: print(f"Found {curr} files")
        )
        print(f"Scanned {len(result.files)} files in {result.duration_seconds:.2f}s")
    """
    crawler = MultiThreadedCrawler(max_workers=max_workers)
    return crawler.crawl(root_path, extensions, progress_callback)


if __name__ == '__main__':
    # Demo: Compare sequential vs parallel performance
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python multi_threaded_crawler.py <directory_path>")
        sys.exit(1)
    
    target_path = sys.argv[1]
    
    print(f"🔍 Crawling: {target_path}")
    print("-" * 60)
    
    # Test with 1 worker (sequential)
    print("📊 Sequential (1 worker):")
    result_seq = crawl_repository(target_path, max_workers=1)
    print(f"   Files: {len(result_seq.files)}")
    print(f"   Duration: {result_seq.duration_seconds:.2f}s")
    print(f"   Throughput: {result_seq.files_per_second:.0f} files/s")
    print()
    
    # Test with 4 workers (parallel)
    print("⚡ Parallel (4 workers):")
    result_par = crawl_repository(target_path, max_workers=4)
    print(f"   Files: {len(result_par.files)}")
    print(f"   Duration: {result_par.duration_seconds:.2f}s")
    print(f"   Throughput: {result_par.files_per_second:.0f} files/s")
    print()
    
    # Calculate improvement
    if result_seq.duration_seconds > 0:
        speedup = result_seq.duration_seconds / result_par.duration_seconds
        improvement = ((result_seq.duration_seconds - result_par.duration_seconds) / result_seq.duration_seconds) * 100
        print(f"🚀 Performance:")
        print(f"   Speedup: {speedup:.2f}x")
        print(f"   Improvement: {improvement:.1f}%")
