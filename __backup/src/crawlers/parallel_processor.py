"""
AC-CRAWLER-001: Multi-Threaded Parallel Processing
ThreadPoolExecutor with auto CPU detection, progress callbacks, error aggregation
"""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProgressUpdate:
    """Progress update from parallel processing"""
    completed: int
    total: int
    current_file: str
    elapsed_seconds: float
    errors: List[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        return (self.completed / self.total * 100) if self.total > 0 else 0


@dataclass
class ProcessingError:
    """Error during file processing"""
    file_path: str
    error: str
    timestamp: datetime = field(default_factory=datetime.now)


class ParallelProcessor:
    """
    Multi-threaded parallel processor with auto-scaling worker counts.
    
    AC-CRAWLER-001 Requirements:
    - ThreadPoolExecutor with auto CPU detection
    - Worker count: min(100, cpu_count * 4)
    - Progress callback support
    - Error aggregation without stopping
    - Batch processing with configurable batch size
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        batch_size: int = 10,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
    ):
        """
        Initialize parallel processor.

        Args:
            max_workers: Max thread count. Auto-detect if None.
            batch_size: Process files in batches
            progress_callback: Called with ProgressUpdate during processing
        """
        self.max_workers = max_workers or min(100, (os.cpu_count() or 1) * 4)
        self.batch_size = batch_size
        self.progress_callback = progress_callback
        self.errors: List[ProcessingError] = []

    def process_files(
        self,
        file_paths: List[str],
        processor_func: Callable[[str], Any],
    ) -> Dict[str, Any]:
        """
        Process files in parallel with progress tracking.

        Args:
            file_paths: List of file paths to process
            processor_func: Function that processes single file, returns result

        Returns:
            {
                "results": {file_path: result},
                "errors": [ProcessingError],
                "total_processed": int,
            }
        """
        results = {}
        self.errors = []
        total = len(file_paths)
        completed = 0
        start_time = datetime.now()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(processor_func, file_path): file_path
                for file_path in file_paths
            }

            for future in as_completed(futures):
                file_path = futures[future]
                completed += 1

                try:
                    result = future.result(timeout=30)
                    results[file_path] = result
                except Exception as e:
                    error = ProcessingError(
                        file_path=file_path, error=str(e)
                    )
                    self.errors.append(error)
                    logger.error(f"Error processing {file_path}: {e}")

                # Report progress
                if self.progress_callback:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    self.progress_callback(
                        ProgressUpdate(
                            completed=completed,
                            total=total,
                            current_file=file_path,
                            elapsed_seconds=elapsed,
                            errors=[e.error for e in self.errors],
                        )
                    )

        return {
            "results": results,
            "errors": self.errors,
            "total_processed": completed,
            "total_files": total,
            "failed": len(self.errors),
        }

    @property
    def worker_count(self) -> int:
        """Get configured worker count"""
        return self.max_workers
