"""
Data Collection Pipeline

Orchestrates collectors based on repository classification.
Supports parallel execution for independent collectors.
Integrates with FileCache for shared file I/O optimization.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class DataCollectionPipeline:
    """
    Execute collectors based on repo type
    
    Uses CollectorRegistry to determine which collectors to run
    and executes them in the correct order. Supports parallel execution
    for independent collectors to improve performance.
    
    Integrates with FileCache to eliminate redundant file I/O.
    """
    
    # Collectors that can run in parallel (no dependencies)
    INDEPENDENT_COLLECTORS = [
        'health', 'security', 'complexity', 'test_coverage', 
        'comment', 'tech_stack', 'dependency'
    ]
    
    # Collectors that depend on others (must run sequentially)
    DEPENDENT_COLLECTORS = [
        'architecture',  # May need health data
        'api_endpoint',  # May need architecture info
        'database_schema',
        'frontend_routes',
        'performance'
    ]
    
    def __init__(self, max_workers: int = 4, use_cache: bool = True):
        """
        Initialize pipeline
        
        Args:
            max_workers: Max parallel threads for collector execution
            use_cache: Whether to use shared FileCache
        """
        self._collector_registry = None
        self._max_workers = max_workers
        self._file_cache = None
        self._use_cache = use_cache
    
    def _get_file_cache(self):
        """Get or create file cache instance"""
        if self._file_cache is None and self._use_cache:
            from ..utils.file_cache import get_global_cache
            self._file_cache = get_global_cache(max_size_mb=100)
        return self._file_cache
    
    def execute(
        self,
        repo_path: Path,
        classification: Dict[str, Any],
        progress_callback: Optional[Callable[[str, str, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute all applicable collectors with parallel support
        
        Args:
            repo_path: Repository root path
            classification: Classification results
            progress_callback: Optional callback(phase, name, message)
            
        Returns:
            {
                'metadata': {...},
                'architecture': {...},
                'health': {...},
                'security': {...},
                ... (one key per collector)
            }
        """
        if self._collector_registry is None:
            from ..collectors.registry import CollectorRegistry
            self._collector_registry = CollectorRegistry()
            self._register_builtin_collectors()
        
        repo_type = classification['primary_type']
        logger.info(f"📦 Executing collectors for {repo_type}")
        
        if progress_callback:
            progress_callback("phase", "data_collection", f"Collecting data for {repo_type}...")
        
        # Get applicable collectors
        all_collectors = self._collector_registry.get_collectors_for_type(repo_type)
        
        # Separate into independent and dependent
        independent = {}
        dependent = {}
        
        for collector in all_collectors:
            name = collector.name
            if name in self.INDEPENDENT_COLLECTORS:
                independent[name] = collector
            else:
                dependent[name] = collector
        
        logger.info(f"📋 Running {len(independent)} parallel + {len(dependent)} sequential collectors")
        
        # Initialize result structure
        result = {
            'metadata': {
                'repo_name': repo_path.name,
                'repo_type': [repo_type],
                'scan_timestamp': datetime.now().isoformat(),
                'cortex_version': '1.0.0',
                'classification': classification
            }
        }
        
        # Phase 1: Run independent collectors in parallel
        if independent:
            if progress_callback:
                progress_callback("phase", "parallel_collection", 
                                f"Running {len(independent)} collectors in parallel...")
            
            parallel_results = self._execute_parallel(
                independent, repo_path, classification, progress_callback
            )
            result.update(parallel_results)
        
        # Phase 2: Run dependent collectors sequentially
        if dependent:
            if progress_callback:
                progress_callback("phase", "sequential_collection",
                                f"Running {len(dependent)} dependent collectors...")
            
            sequential_results = self._execute_sequential(
                dependent, repo_path, classification, progress_callback
            )
            result.update(sequential_results)
        
        logger.info(f"✅ Data collection complete: {len(result)} sections")
        
        return result
    
    def _execute_parallel(
        self,
        collectors: Dict[str, Any],
        repo_path: Path,
        classification: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute independent collectors in parallel"""
        result = {}
        completed = 0
        total = len(collectors)
        
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_name = {
                executor.submit(
                    collector.collect_safe, repo_path, classification
                ): name
                for name, collector in collectors.items()
            }
            
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                completed += 1
                
                if progress_callback:
                    progress_callback("collector", name, 
                                    f"Completed {completed}/{total}")
                
                try:
                    data = future.result()
                    key = self._normalize_key(name)
                    result[key] = data
                    logger.info(f"  ✓ {name}")
                    
                except Exception as e:
                    logger.error(f"  ✗ {name} failed: {e}")
                    result[name] = {'error': str(e), 'collector': name}
        
        return result
    
    def _execute_sequential(
        self,
        collectors: Dict[str, Any],
        repo_path: Path,
        classification: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute dependent collectors sequentially"""
        result = {}
        
        for name, collector in collectors.items():
            if progress_callback:
                progress_callback("collector", name, f"Running {name}...")
            
            logger.info(f"  ▸ {name}")
            
            try:
                data = collector.collect_safe(repo_path, classification)
                key = self._normalize_key(name)
                result[key] = data
                
            except Exception as e:
                logger.error(f"  ✗ {name} failed: {e}")
                result[name] = {'error': str(e), 'collector': name}
        
        return result
    
    def _normalize_key(self, name: str) -> str:
        """Normalize collector name to result key"""
        return name.replace('_collector', '').replace('Collector', '').lower()
    
    def _register_builtin_collectors(self):
        """Register built-in collectors"""
        try:
            from ..collectors.health_collector import HealthCollector
            self._collector_registry.register(HealthCollector())
        except Exception as e:
            logger.warning(f"Failed to register HealthCollector: {e}")
        
        try:
            from ..collectors.architecture_collector import ArchitectureCollector
            self._collector_registry.register(ArchitectureCollector())
        except Exception as e:
            logger.warning(f"Failed to register ArchitectureCollector: {e}")
        
        try:
            from ..collectors.api_endpoint_collector import APIEndpointCollector
            self._collector_registry.register(APIEndpointCollector())
        except Exception as e:
            logger.warning(f"Failed to register APIEndpointCollector: {e}")
        
        try:
            from ..collectors.comment_collector import CommentCollector
            self._collector_registry.register(CommentCollector())
        except Exception as e:
            logger.warning(f"Failed to register CommentCollector: {e}")
        
        try:
            from ..collectors.tech_stack_collector import TechStackCollector
            self._collector_registry.register(TechStackCollector())
        except Exception as e:
            logger.warning(f"Failed to register TechStackCollector: {e}")
        
        try:
            from ..collectors.dependency_collector import DependencyCollector
            self._collector_registry.register(DependencyCollector())
        except Exception as e:
            logger.warning(f"Failed to register DependencyCollector: {e}")
        
        try:
            from ..collectors.security_collector import SecurityCollector
            self._collector_registry.register(SecurityCollector())
        except Exception as e:
            logger.warning(f"Failed to register SecurityCollector: {e}")
        
        try:
            from ..collectors.complexity_collector import ComplexityCollector
            self._collector_registry.register(ComplexityCollector())
        except Exception as e:
            logger.warning(f"Failed to register ComplexityCollector: {e}")
        
        try:
            from ..collectors.test_coverage_collector import TestCoverageCollector
            self._collector_registry.register(TestCoverageCollector())
        except Exception as e:
            logger.warning(f"Failed to register TestCoverageCollector: {e}")
        
        logger.info(f"📝 Registered {len(self._collector_registry.list_collectors())} built-in collectors")
    
    def execute_single(
        self,
        collector_name: str,
        repo_path: Path,
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single collector
        
        Args:
            collector_name: Name of collector to run
            repo_path: Repository path
            classification: Classification results
            
        Returns:
            Collector results
        """
        if self._collector_registry is None:
            from ..collectors.registry import CollectorRegistry
            self._collector_registry = CollectorRegistry()
            self._register_builtin_collectors()
        
        collector = self._collector_registry.get_collector(collector_name)
        if not collector:
            raise ValueError(f"Collector not found: {collector_name}")
        
        return collector.collect_safe(repo_path, classification)
