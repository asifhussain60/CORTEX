"""
Parallel File Processor

Multi-threaded file analysis using ThreadPoolExecutor with progress tracking,
error handling, and adaptive worker pool sizing.

Author: CORTEX Application Health Dashboard
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
import threading
import time
from pathlib import Path


@dataclass
class ProcessingResult:
    """Result from parallel processing operation"""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    results: List[Any] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    elapsed_time: float = 0.0
    throughput: float = 0.0  # files per second


class ParallelProcessor:
    """
    Multi-threaded file processor with adaptive worker pool
    
    Features:
    - Auto-detect CPU cores (default: min(100, cpu_count * 4))
    - Progress tracking with callbacks
    - Error handling with detailed error reporting
    - Thread-safe result aggregation
    - Performance metrics (throughput, timing)
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize parallel processor
        
        Args:
            max_workers: Maximum worker threads. If None, auto-detect
                        (min(100, cpu_count * 4))
        """
        if max_workers is None:
            cpu_count = os.cpu_count() or 4
            max_workers = min(100, cpu_count * 4)
        
        self.max_workers = max_workers
        self._lock = threading.Lock()
        self._progress_callback: Optional[Callable] = None
    
    def process_files(
        self,
        file_paths: List[str],
        processor_func: Callable[[str], Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ProcessingResult:
        """
        Process files in parallel using thread pool
        
        Args:
            file_paths: List of file paths to process
            processor_func: Function to call for each file (takes file_path, returns result)
            progress_callback: Optional callback(current, total) for progress updates
            
        Returns:
            ProcessingResult with aggregated results and metrics
        """
        result = ProcessingResult(total_files=len(file_paths))
        start_time = time.time()
        
        self._progress_callback = progress_callback
        
        if not file_paths:
            result.elapsed_time = time.time() - start_time
            return result
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self._safe_process, processor_func, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    success, data = future.result()
                    
                    with self._lock:
                        if success:
                            result.results.append(data)
                            result.processed_files += 1
                        else:
                            result.errors.append({
                                'file': file_path,
                                'error': str(data)
                            })
                            result.failed_files += 1
                        
                        # Progress callback
                        if self._progress_callback:
                            completed = result.processed_files + result.failed_files
                            self._progress_callback(completed, result.total_files)
                
                except Exception as e:
                    with self._lock:
                        result.errors.append({
                            'file': file_path,
                            'error': f"Future exception: {str(e)}"
                        })
                        result.failed_files += 1
        
        # Calculate metrics
        result.elapsed_time = time.time() - start_time
        if result.elapsed_time > 0:
            result.throughput = result.processed_files / result.elapsed_time
        
        return result
    
    def _safe_process(self, func: Callable, file_path: str) -> tuple:
        """
        Safely process a file with error handling
        
        Args:
            func: Processing function
            file_path: Path to file
            
        Returns:
            Tuple of (success: bool, result/error)
        """
        try:
            result = func(file_path)
            return (True, result)
        except Exception as e:
            return (False, e)
    
    def process_in_batches(
        self,
        file_paths: List[str],
        processor_func: Callable[[str], Any],
        batch_size: int = 1000,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ProcessingResult:
        """
        Process files in batches (useful for very large file sets)
        
        Args:
            file_paths: List of file paths
            processor_func: Processing function
            batch_size: Number of files per batch
            progress_callback: Progress callback
            
        Returns:
            Aggregated ProcessingResult
        """
        combined_result = ProcessingResult(total_files=len(file_paths))
        start_time = time.time()
        
        # Process in batches
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            
            # Adjust progress callback for batch offset
            def batch_progress(current, total):
                overall_current = i + current
                if progress_callback:
                    progress_callback(overall_current, len(file_paths))
            
            # Process batch
            batch_result = self.process_files(batch, processor_func, batch_progress)
            
            # Aggregate results
            combined_result.processed_files += batch_result.processed_files
            combined_result.failed_files += batch_result.failed_files
            combined_result.results.extend(batch_result.results)
            combined_result.errors.extend(batch_result.errors)
        
        # Calculate metrics
        combined_result.elapsed_time = time.time() - start_time
        if combined_result.elapsed_time > 0:
            combined_result.throughput = combined_result.processed_files / combined_result.elapsed_time
        
        return combined_result
