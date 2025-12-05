"""
Universal collector base class for dashboard data collection.
Provides language-agnostic file discovery, chunking, streaming, and parallel processing.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Generator, Optional, Set, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import mimetypes
import time
import hashlib
import json


@dataclass
class FileChunk:
    """Represents a chunk of files for parallel processing."""
    files: List[Path]
    chunk_id: int
    total_chunks: int


@dataclass
class CollectionProgress:
    """Progress tracking for collection operations."""
    files_processed: int
    total_files: int
    current_file: Optional[str]
    elapsed_time: float
    errors: List[str]


class UniversalCollectorBase:
    """
    Base collector class providing common functionality for all collectors.
    
    Features:
    - Language-agnostic file discovery with extension filtering
    - File chunking for parallel processing (default 100 files per chunk)
    - Streaming results to minimize memory usage
    - Progress tracking for long-running operations
    - Configurable exclusion patterns (node_modules, .git, etc.)
    - Result caching with TTL support
    """
    
    # Default exclusion patterns
    DEFAULT_EXCLUDED_DIRS = {
        'node_modules', '.git', '.venv', 'venv', '__pycache__', 
        'bin', 'obj', 'dist', 'build', '.pytest_cache', '.mypy_cache',
        'packages', '.nuget', 'TestResults'
    }
    
    DEFAULT_EXCLUDED_FILES = {
        '.min.js', '.min.css', '.map', '.dll', '.exe', '.pdb', '.cache'
    }
    
    def __init__(
        self, 
        project_root: str,
        chunk_size: int = 100,
        max_workers: int = 4,
        excluded_dirs: Optional[Set[str]] = None,
        excluded_files: Optional[Set[str]] = None,
        enable_caching: bool = True,
        cache_ttl: int = 300,
        incremental: bool = False,
        file_timeout: Optional[float] = None
    ):
        """
        Initialize universal collector.
        
        Args:
            project_root: Root directory of the project to analyze
            chunk_size: Number of files per chunk for parallel processing
            max_workers: Maximum number of parallel workers
            excluded_dirs: Additional directories to exclude (merged with defaults)
            excluded_files: Additional file patterns to exclude (merged with defaults)
            enable_caching: Enable result caching
            cache_ttl: Cache time-to-live in seconds
            incremental: Enable incremental mode (skip cached files)
            file_timeout: Timeout in seconds for processing individual files
        """
        if not project_root:
            raise ValueError("project_root is required")
        
        self.project_root = Path(project_root)
        if not self.project_root.exists():
            raise FileNotFoundError(f"Project root does not exist: {project_root}")
        
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.excluded_dirs = self.DEFAULT_EXCLUDED_DIRS.copy()
        if excluded_dirs:
            self.excluded_dirs.update(excluded_dirs)
        
        self.excluded_files = self.DEFAULT_EXCLUDED_FILES.copy()
        if excluded_files:
            self.excluded_files.update(excluded_files)
        
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.incremental = incremental
        self.file_timeout = file_timeout
        
        # Set up cache directory
        self.cache_dir = self.project_root / ".cortex-cache"
        if self.enable_caching:
            self.cache_dir.mkdir(exist_ok=True)
        
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._file_hashes: Dict[Path, str] = {}
        
        self._progress = CollectionProgress(
            files_processed=0,
            total_files=0,
            current_file=None,
            elapsed_time=0.0,
            errors=[]
        )
    
    def discover_files(
        self, 
        extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Discover files in project matching extension criteria.
        
        Args:
            extensions: File extensions to include (e.g., ['.py', '.cs'])
            exclude_patterns: Additional patterns to exclude
            exclude_dirs: Additional directories to exclude for this call
            
        Returns:
            List of discovered file paths
        """
        discovered = []
        
        # Merge excluded directories
        excluded = self.excluded_dirs.copy()
        if exclude_dirs:
            excluded.update(exclude_dirs)
        
        for root, dirs, files in os.walk(self.project_root):
            # Filter excluded directories in-place
            dirs[:] = [d for d in dirs if d not in excluded]
            
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                
                # Check excluded file patterns
                if any(pattern in file for pattern in self.excluded_files):
                    continue
                
                # Check extension filter
                if extensions and file_path.suffix not in extensions:
                    continue
                
                # Check additional exclusion patterns
                if exclude_patterns and any(pattern in str(file_path) for pattern in exclude_patterns):
                    continue
                
                discovered.append(file_path)
        
        return discovered
    
    def chunk_files(self, files: List[Path], chunk_size: Optional[int] = None) -> List[List[Path]]:
        """
        Split files into chunks for parallel processing.
        
        Args:
            files: List of files to chunk
            chunk_size: Override default chunk size
            
        Returns:
            List of file chunks (list of lists)
        """
        if not files:
            return []
        
        size = chunk_size if chunk_size is not None else self.chunk_size
        chunks = []
        
        for i in range(0, len(files), size):
            chunk_files = files[i:i + size]
            chunks.append(chunk_files)
        
        return chunks
    
    def stream_results(
        self, 
        process_func: callable,
        files: List[Path]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream processing results to minimize memory usage.
        
        Args:
            process_func: Function to process each file
            files: List of files to process
            
        Yields:
            Processing results for each file
        """
        self._progress.total_files = len(files)
        self._progress.files_processed = 0
        start_time = time.time()
        
        for file_path in files:
            self._progress.current_file = str(file_path)
            
            try:
                result = process_func(file_path)
                if result:
                    yield result
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                self._progress.errors.append(error_msg)
            finally:
                self._progress.files_processed += 1
                self._progress.elapsed_time = time.time() - start_time
    
    def process_parallel(
        self,
        files: List[Path],
        process_func: Callable,
        ignore_errors: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Process files in parallel using thread pool.
        
        Args:
            files: List of files to process
            process_func: Function to process each file
            ignore_errors: Continue processing on errors
            progress_callback: Callback function for progress updates
            
        Returns:
            List of processing results
        """
        results = []
        self._progress.total_files = len(files)
        self._progress.files_processed = 0
        start_time = time.time()
        
        # Filter out cached files if in incremental mode
        # Also filter out non-existent files
        files_to_process = []
        for file_path in files:
            # Check if file exists
            if not file_path.exists():
                error_msg = f"File not found: {file_path}"
                self._progress.errors.append(error_msg)
                if not ignore_errors:
                    raise FileNotFoundError(error_msg)
                continue
            
            if self.incremental:
                cached = self.get_cached_result_for_file(file_path)
                if cached is not None:
                    results.append(cached)
                    continue
            files_to_process.append(file_path)
        
        # Update total with files actually being processed
        self._progress.total_files = len(files_to_process)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for file_path in files_to_process:
                future = executor.submit(process_func, file_path)
                futures.append((future, file_path))
            
            # Process each future with individual timeout
            for future, file_path in futures:
                self._progress.current_file = str(file_path)
                
                try:
                    # Apply timeout to each individual future
                    if self.file_timeout:
                        result = future.result(timeout=self.file_timeout)
                    else:
                        result = future.result()
                    if result:
                        results.append(result)
                except TimeoutError:
                    error_msg = f"Timeout processing {file_path}"
                    self._progress.errors.append(error_msg)
                    # Don't add result on timeout
                    if not ignore_errors:
                        raise
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    self._progress.errors.append(error_msg)
                    # Don't add result on error
                    if not ignore_errors:
                        raise
                finally:
                    self._progress.files_processed += 1
                    self._progress.elapsed_time = time.time() - start_time
                    
                    # Call progress callback with (current, total, message)
                    if progress_callback:
                        progress_callback(
                            self._progress.files_processed,
                            self._progress.total_files,
                            f"Processing {self._progress.current_file}"
                        )
        
        return results
    
    def get_progress(self) -> CollectionProgress:
        """
        Get current collection progress.
        
        Returns:
            Current progress information
        """
        return self._progress
    
    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """
        Get cached result if available and not expired.
        
        Args:
            cache_key: Key for cached data
            
        Returns:
            Cached result or None if not found/expired
        """
        if not self.enable_caching:
            return None
        
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return result
            else:
                del self._cache[cache_key]
        
        return None
    
    def set_cached_result(self, cache_key: str, result: Any) -> None:
        """
        Cache result with current timestamp.
        
        Args:
            cache_key: Key for cached data
            result: Data to cache
        """
        if self.enable_caching:
            self._cache[cache_key] = (result, time.time())
    
    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
        self._file_hashes.clear()
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file contents.
        Always recalculates to detect file changes.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of file hash
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        file_hash = sha256.hexdigest()
        self._file_hashes[file_path] = file_hash
        return file_hash
    
    def cache_result(self, file_path: Path, result: Any) -> None:
        """
        Cache result for a specific file.
        
        Args:
            file_path: Path to file
            result: Result to cache
        """
        if not self.enable_caching:
            return
        
        file_hash = self.calculate_file_hash(file_path)
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        with open(cache_file, 'w') as f:
            json.dump({
                'file_path': str(file_path),
                'file_hash': file_hash,
                'timestamp': time.time(),
                'result': result
            }, f)
    
    def get_cached_result(self, file_path: Path) -> Optional[Any]:
        """
        Get cached result for a specific file (alias for get_cached_result_for_file).
        
        Args:
            file_path: Path to file
            
        Returns:
            Cached result or None if not found/expired/invalidated
        """
        return self.get_cached_result_for_file(file_path)
    
    def get_cached_result_for_file(self, file_path: Path) -> Optional[Any]:
        """
        Get cached result for a specific file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Cached result or None if not found/expired/invalidated
        """
        if not self.enable_caching:
            return None
        
        file_hash = self.calculate_file_hash(file_path)
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Check TTL
            if time.time() - cached['timestamp'] > self.cache_ttl:
                cache_file.unlink()
                return None
            
            # Verify hash matches (file hasn't changed)
            if cached['file_hash'] != file_hash:
                cache_file.unlink()
                return None
            
            return cached['result']
        except Exception:
            return None
    
    def is_large_file(self, file_path: Path, threshold_mb: float = 10) -> bool:
        """
        Check if file exceeds size threshold.
        
        Args:
            file_path: Path to file
            threshold_mb: Size threshold in megabytes
            
        Returns:
            True if file is larger than threshold
        """
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            return size_mb > threshold_mb
        except Exception:
            return False
    
    def read_file_chunks(self, file_path: Path, chunk_size: int = 1024) -> Generator[str, None, None]:
        """
        Read file in chunks for memory efficiency.
        
        Args:
            file_path: Path to file
            chunk_size: Number of lines per chunk
            
        Yields:
            File content chunks (strings)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for line in f:
                    lines.append(line)
                    if len(lines) >= chunk_size:
                        yield ''.join(lines)
                        lines = []
                if lines:
                    yield ''.join(lines)
        except Exception as e:
            error_msg = f"Error reading {file_path}: {str(e)}"
            self._progress.errors.append(error_msg)
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect data for this collector type.
        Must be implemented by subclasses.
        
        Returns:
            Collected data dictionary
        """
        raise NotImplementedError("Subclasses must implement collect()")
