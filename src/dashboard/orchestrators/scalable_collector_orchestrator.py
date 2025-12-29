"""
Scalable Collector Orchestrator - coordinates multiple collectors for large-scale analysis.

Manages parallel execution of multiple collectors with:
- Configurable parallelism (max concurrent collectors)
- Aggregated progress tracking across all collectors
- Error isolation (one collector failure doesn't stop others)
- Result merging with conflict resolution
- Caching and incremental analysis
- Performance targets (10K+ files in < 60s)
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Type
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import hashlib
import json


@dataclass
class ExecutionStats:
    """Statistics for orchestrator execution."""
    total_time: float
    average_collector_time: float
    collectors_run: int
    collectors_failed: int
    total_files_processed: int


class ScalableCollectorOrchestrator:
    """
    Orchestrates multiple collectors for comprehensive project analysis.
    
    Features:
    - Parallel collector execution with configurable concurrency
    - Aggregated progress tracking across collectors
    - Error isolation between collectors
    - Result merging with multiple strategies
    - Caching and incremental analysis support
    - Performance optimization for large codebases
    """
    
    def __init__(
        self,
        project_root: str,
        collectors: Optional[List[Type]] = None,
        max_parallel_collectors: int = 4,
        enable_caching: bool = True,
        cache_ttl: int = 300,
        incremental: bool = False,
        timeout_per_collector: Optional[float] = None,
        progress_callback: Optional[Callable] = None,
        merge_strategy: str = "last_wins",
        enable_result_streaming: bool = False
    ):
        """
        Initialize orchestrator.
        
        Args:
            project_root: Root directory of project to analyze
            collectors: List of collector classes to run
            max_parallel_collectors: Maximum number of collectors to run concurrently
            enable_caching: Enable result caching
            cache_ttl: Cache time-to-live in seconds
            incremental: Enable incremental analysis
            timeout_per_collector: Timeout for each collector in seconds
            progress_callback: Callback for progress updates
            merge_strategy: Strategy for merging results ("last_wins", "combine", "error")
            enable_result_streaming: Stream results instead of buffering
        """
        if not project_root:
            raise ValueError("project_root is required")
        
        self.project_root = Path(project_root)
        if not self.project_root.exists():
            raise FileNotFoundError(f"Project root does not exist: {project_root}")
        
        self.collectors: List[Type] = collectors or []
        self.max_parallel_collectors = max_parallel_collectors
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.incremental = incremental
        self.timeout_per_collector = timeout_per_collector
        self.progress_callback = progress_callback
        self.merge_strategy = merge_strategy
        self.enable_result_streaming = enable_result_streaming
        
        # Set up cache directory
        self.cache_dir = self.project_root / ".cortex-cache" / "orchestrator"
        if self.enable_caching:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Execution tracking
        self._errors: List[str] = []
        self._execution_stats: Optional[ExecutionStats] = None
        self._collector_times: List[float] = []
    
    def register_collector(self, collector_class: Type) -> None:
        """
        Register a single collector class.
        
        Args:
            collector_class: Collector class to register
        """
        if collector_class not in self.collectors:
            self.collectors.append(collector_class)
    
    def register_collectors(self, collector_classes: List[Type]) -> None:
        """
        Register multiple collector classes.
        
        Args:
            collector_classes: List of collector classes to register
        """
        for collector_class in collector_classes:
            self.register_collector(collector_class)
    
    def run_all(self, ignore_errors: bool = False) -> List[Dict[str, Any]]:
        """
        Run all registered collectors in parallel.
        
        Args:
            ignore_errors: Continue running collectors if one fails
            
        Returns:
            List of results from each collector
        """
        results = []
        self._errors = []
        self._collector_times = []
        start_time = time.time()
        
        # Check for cached results
        if self.enable_caching and not self.incremental:
            cached = self._get_cached_orchestrator_results()
            if cached is not None:
                return cached
        
        with ThreadPoolExecutor(max_workers=self.max_parallel_collectors) as executor:
            # Submit collector execution tasks
            future_to_collector = {}
            for i, collector_class in enumerate(self.collectors):
                # Create collector instance
                # Handle both class instantiation and factory functions
                try:
                    if callable(collector_class):
                        # Check if it's a factory function (takes project_root)
                        import inspect
                        sig = inspect.signature(collector_class)
                        if len(sig.parameters) >= 1:
                            collector = collector_class(self.project_root)
                        else:
                            collector = collector_class()
                    else:
                        collector = collector_class(self.project_root)
                    
                    future = executor.submit(self._run_single_collector, collector, i)
                    future_to_collector[future] = (collector, i)
                except Exception as e:
                    error_msg = f"Error creating collector {collector_class.__name__}: {str(e)}"
                    self._errors.append(error_msg)
                    if not ignore_errors:
                        raise
            
            # Process results as they complete
            total_collectors = len(future_to_collector)
            completed_collectors = 0
            
            # Process futures with optional timeout
            timeout = self.timeout_per_collector if self.timeout_per_collector else None
            
            try:
                for future in as_completed(future_to_collector, timeout=timeout):
                    collector, collector_idx = future_to_collector[future]
                    completed_collectors += 1
                    
                    try:
                        # Get result (future is already done since it came from as_completed)
                        result = future.result()
                        
                        if result is not None:
                            results.append(result)
                        
                        # Update progress
                        if self.progress_callback:
                            self.progress_callback(
                                completed_collectors,
                                total_collectors,
                                0,  # current_files (TODO: aggregate from collectors)
                                0,  # total_files
                                f"Completed collector {collector_idx + 1}/{total_collectors}"
                            )
                    
                    except Exception as e:
                        error_msg = f"Error running collector {collector.__class__.__name__}: {str(e)}"
                        self._errors.append(error_msg)
                        if not ignore_errors:
                            raise
            
            except TimeoutError:
                # Timeout waiting for all futures - some collectors didn't complete in time
                # Mark pending futures as timed out
                for future, (collector, idx) in future_to_collector.items():
                    if not future.done():
                        error_msg = f"Timeout running collector {collector.__class__.__name__}"
                        self._errors.append(error_msg)
                        future.cancel()  # Try to cancel if not started
                
                if not ignore_errors:
                    raise TimeoutError(f"Orchestrator timeout after {timeout}s - {len(self._errors)} collectors timed out")
        
        # Calculate execution stats
        total_time = time.time() - start_time
        self._execution_stats = ExecutionStats(
            total_time=total_time,
            average_collector_time=sum(self._collector_times) / len(self._collector_times) if self._collector_times else 0,
            collectors_run=len(results),
            collectors_failed=len(self._errors),
            total_files_processed=0  # TODO: aggregate from collector progress
        )
        
        # Cache results
        if self.enable_caching:
            self._cache_orchestrator_results(results)
        
        return results
    
    def _run_single_collector(self, collector: Any, collector_idx: int) -> Optional[Dict[str, Any]]:
        """
        Run a single collector and track its execution time.
        
        Args:
            collector: Collector instance to run
            collector_idx: Index of collector in list
            
        Returns:
            Collector results or None
        """
        start_time = time.time()
        try:
            result = collector.collect()
            elapsed = time.time() - start_time
            self._collector_times.append(elapsed)
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            self._collector_times.append(elapsed)
            raise
    
    def run_and_merge(self) -> Dict[str, Any]:
        """
        Run all collectors and merge their results.
        
        Returns:
            Merged results from all collectors
        """
        results = self.run_all(ignore_errors=True)
        return self._merge_results(results)
    
    def _merge_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge results from multiple collectors.
        
        Args:
            results: List of collector results
            
        Returns:
            Merged result dictionary
        """
        merged = {}
        
        for result in results:
            if self.merge_strategy == "last_wins":
                # Later results overwrite earlier ones
                merged.update(result)
            elif self.merge_strategy == "combine":
                # Combine values for duplicate keys
                for key, value in result.items():
                    if key in merged:
                        if isinstance(merged[key], list):
                            merged[key].append(value)
                        else:
                            merged[key] = [merged[key], value]
                    else:
                        merged[key] = value
            elif self.merge_strategy == "error":
                # Raise error on duplicate keys
                for key in result:
                    if key in merged:
                        raise ValueError(f"Duplicate key in results: {key}")
                merged.update(result)
        
        return merged
    
    def get_errors(self) -> List[str]:
        """
        Get list of errors from last execution.
        
        Returns:
            List of error messages
        """
        return self._errors
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics from last run.
        
        Returns:
            Dictionary of execution statistics
        """
        if self._execution_stats is None:
            return {
                "total_time": 0,
                "average_collector_time": 0,
                "collectors_run": 0,
                "collectors_failed": 0,
                "total_files_processed": 0
            }
        
        return {
            "total_time": self._execution_stats.total_time,
            "average_collector_time": self._execution_stats.average_collector_time,
            "collectors_run": self._execution_stats.collectors_run,
            "collectors_failed": self._execution_stats.collectors_failed,
            "total_files_processed": self._execution_stats.total_files_processed
        }
    
    def _get_cache_key(self) -> str:
        """
        Generate cache key based on project state.
        
        Returns:
            Cache key string
        """
        # Use project root and collector list as cache key
        collector_names = sorted([c.__name__ for c in self.collectors])
        key_data = f"{self.project_root}:{':'.join(collector_names)}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _get_cached_orchestrator_results(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached orchestrator results if available.
        
        Returns:
            Cached results or None
        """
        if not self.enable_caching:
            return None
        
        cache_key = self._get_cache_key()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Check TTL
            if time.time() - cached['timestamp'] > self.cache_ttl:
                cache_file.unlink()
                return None
            
            return cached['results']
        except Exception:
            return None
    
    def _cache_orchestrator_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Cache orchestrator results.
        
        Args:
            results: Results to cache
        """
        if not self.enable_caching:
            return
        
        cache_key = self._get_cache_key()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': time.time(),
                    'results': results
                }, f)
        except Exception:
            pass  # Fail silently on cache errors
