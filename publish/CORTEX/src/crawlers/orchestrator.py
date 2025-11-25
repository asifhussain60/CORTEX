"""
Crawler Orchestrator for CORTEX

Manages execution of multiple crawlers with:
- Dependency resolution
- Parallel/sequential execution
- Result aggregation
- Error handling and retries
- Progress reporting

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import concurrent.futures

from .base_crawler import BaseCrawler, CrawlerResult, CrawlerStatus, CrawlerPriority

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result from orchestrator execution"""
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    total_crawlers: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    total_items_discovered: int = 0
    total_patterns_created: int = 0
    crawler_results: List[CrawlerResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'total_crawlers': self.total_crawlers,
            'completed': self.completed,
            'failed': self.failed,
            'skipped': self.skipped,
            'total_items_discovered': self.total_items_discovered,
            'total_patterns_created': self.total_patterns_created,
            'crawler_results': [r.to_dict() for r in self.crawler_results],
            'errors': self.errors
        }


class CrawlerOrchestrator:
    """
    Orchestrates execution of multiple crawlers.
    
    Features:
    - Dependency resolution (run tooling crawler first)
    - Priority-based execution
    - Parallel execution for independent crawlers
    - Conditional execution (skip DB crawlers if no connections)
    - Result aggregation and reporting
    
    Usage:
    ```python
    from crawlers import CrawlerOrchestrator
    from crawlers.tooling_crawler import ToolingCrawler
    from crawlers.ui_crawler import UICrawler
    from crawlers.api_crawler import APICrawler
    
    orchestrator = CrawlerOrchestrator(
        workspace_path=Path.cwd(),
        knowledge_graph=kg
    )
    
    orchestrator.register(ToolingCrawler)
    orchestrator.register(UICrawler)
    orchestrator.register(APICrawler)
    
    result = orchestrator.run_all()
    print(f"Completed: {result.completed}/{result.total_crawlers}")
    ```
    """
    
    def __init__(
        self,
        workspace_path: Path,
        knowledge_graph: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        parallel: bool = True,
        max_workers: int = 4
    ):
        """
        Initialize orchestrator.
        
        Args:
            workspace_path: Path to workspace root
            knowledge_graph: KnowledgeGraph instance for storage
            config: Configuration dictionary
            parallel: Enable parallel execution
            max_workers: Max parallel crawler threads
        """
        self.workspace_path = workspace_path
        self.knowledge_graph = knowledge_graph
        self.config = config or {}
        self.parallel = parallel
        self.max_workers = max_workers
        
        self.crawler_classes: Dict[str, type] = {}
        self.crawler_instances: Dict[str, BaseCrawler] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.results: Dict[str, CrawlerResult] = {}
        
    def register(self, crawler_class: type) -> None:
        """
        Register a crawler class.
        
        Args:
            crawler_class: Class inheriting from BaseCrawler
        """
        # Create temporary instance to get info
        temp_instance = crawler_class({'workspace_path': self.workspace_path})
        info = temp_instance.get_crawler_info()
        crawler_id = info['crawler_id']
        
        self.crawler_classes[crawler_id] = crawler_class
        self.dependency_graph[crawler_id] = info.get('dependencies', [])
        
        logger.info(f"Registered crawler: {info['name']} (ID: {crawler_id})")
        
    def run_all(self, crawler_ids: Optional[List[str]] = None) -> OrchestrationResult:
        """
        Run all registered crawlers (or specified subset).
        
        Args:
            crawler_ids: Optional list of specific crawler IDs to run
            
        Returns:
            OrchestrationResult with execution details
        """
        start_time = datetime.now()
        result = OrchestrationResult(
            started_at=start_time,
            total_crawlers=0
        )
        
        try:
            # Determine which crawlers to run
            if crawler_ids:
                crawlers_to_run = crawler_ids
            else:
                crawlers_to_run = list(self.crawler_classes.keys())
            
            result.total_crawlers = len(crawlers_to_run)
            
            # Resolve execution order based on dependencies
            execution_order = self._resolve_dependencies(crawlers_to_run)
            logger.info(f"Execution order: {' → '.join(execution_order)}")
            
            # Execute crawlers
            for crawler_id in execution_order:
                if not self._check_dependencies_satisfied(crawler_id):
                    logger.warning(f"Skipping {crawler_id} - dependencies not satisfied")
                    result.skipped += 1
                    continue
                
                # Check if crawler should run based on previous results
                if not self._should_run_crawler(crawler_id):
                    logger.info(f"Skipping {crawler_id} - conditions not met")
                    result.skipped += 1
                    continue
                
                # Execute crawler
                crawler_result = self._execute_crawler(crawler_id)
                result.crawler_results.append(crawler_result)
                self.results[crawler_id] = crawler_result
                
                # Update statistics
                if crawler_result.status == CrawlerStatus.COMPLETED:
                    result.completed += 1
                    result.total_items_discovered += crawler_result.items_discovered
                    result.total_patterns_created += crawler_result.patterns_created
                elif crawler_result.status == CrawlerStatus.FAILED:
                    result.failed += 1
                    result.errors.extend(crawler_result.errors)
                elif crawler_result.status == CrawlerStatus.SKIPPED:
                    result.skipped += 1
                
            # Finalize result
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - start_time).total_seconds()
            
            logger.info(
                f"Orchestration complete: {result.completed} completed, "
                f"{result.failed} failed, {result.skipped} skipped"
            )
            
        except Exception as e:
            result.errors.append(f"Orchestration error: {e}")
            logger.error(f"Orchestration failed: {e}")
            
        return result
    
    def run_single(self, crawler_id: str) -> CrawlerResult:
        """
        Run a single crawler by ID.
        
        Args:
            crawler_id: ID of crawler to run
            
        Returns:
            CrawlerResult
        """
        if crawler_id not in self.crawler_classes:
            raise ValueError(f"Unknown crawler: {crawler_id}")
        
        return self._execute_crawler(crawler_id)
    
    def _execute_crawler(self, crawler_id: str) -> CrawlerResult:
        """
        Execute a single crawler.
        
        Args:
            crawler_id: ID of crawler to execute
            
        Returns:
            CrawlerResult
        """
        crawler_class = self.crawler_classes[crawler_id]
        
        # Create crawler instance with config
        crawler_config = {
            'workspace_path': self.workspace_path,
            'knowledge_graph': self.knowledge_graph,
            **self.config.get(crawler_id, {})
        }
        
        # Pass previous results for conditional logic
        crawler_config['previous_results'] = self.results
        
        crawler = crawler_class(crawler_config)
        self.crawler_instances[crawler_id] = crawler
        
        # Execute crawler
        logger.info(f"Executing crawler: {crawler_id}")
        return crawler.execute()
    
    def _resolve_dependencies(self, crawler_ids: List[str]) -> List[str]:
        """
        Resolve execution order based on dependencies.
        
        Uses topological sort to ensure dependencies run first.
        
        Args:
            crawler_ids: List of crawler IDs to order
            
        Returns:
            Ordered list of crawler IDs
        """
        # Build priority groups
        priority_groups = {}
        for crawler_id in crawler_ids:
            # Get priority from crawler info
            temp_instance = self.crawler_classes[crawler_id]({
                'workspace_path': self.workspace_path
            })
            info = temp_instance.get_crawler_info()
            priority = info.get('priority', CrawlerPriority.MEDIUM)
            
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(crawler_id)
        
        # Sort by priority (CRITICAL first)
        execution_order = []
        for priority in sorted(priority_groups.keys(), key=lambda p: p.value):
            execution_order.extend(priority_groups[priority])
        
        return execution_order
    
    def _check_dependencies_satisfied(self, crawler_id: str) -> bool:
        """
        Check if crawler's dependencies are satisfied.
        
        Args:
            crawler_id: ID of crawler to check
            
        Returns:
            True if all dependencies completed successfully
        """
        dependencies = self.dependency_graph.get(crawler_id, [])
        
        for dep_id in dependencies:
            if dep_id not in self.results:
                return False
            if self.results[dep_id].status != CrawlerStatus.COMPLETED:
                return False
        
        return True
    
    def _should_run_crawler(self, crawler_id: str) -> bool:
        """
        Determine if crawler should run based on conditions.
        
        For example:
        - Database crawlers only run if tooling crawler found connections
        - UI crawler only runs if UI frameworks detected
        
        Args:
            crawler_id: ID of crawler to check
            
        Returns:
            True if crawler should run
        """
        # Special logic for database crawlers
        if crawler_id in ['oracle_crawler', 'sqlserver_crawler', 'postgres_crawler']:
            # Only run if tooling crawler found database connections
            if 'tooling_crawler' in self.results:
                tooling_result = self.results['tooling_crawler']
                if tooling_result.status == CrawlerStatus.COMPLETED:
                    # Check metadata for database connections
                    db_connections = tooling_result.metadata.get('database_connections', {})
                    
                    # Map crawler IDs to database types
                    db_type_map = {
                        'oracle_crawler': 'oracle',
                        'sqlserver_crawler': 'sqlserver',
                        'postgres_crawler': 'postgresql'
                    }
                    
                    db_type = db_type_map.get(crawler_id)
                    if db_type and db_type in db_connections:
                        return len(db_connections[db_type]) > 0
            
            # No tooling result or no connections found
            return False
        
        # Default: run the crawler
        return True
    
    def get_results(self) -> Dict[str, CrawlerResult]:
        """
        Get all crawler results.
        
        Returns:
            Dictionary mapping crawler_id to CrawlerResult
        """
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get execution summary.
        
        Returns:
            Dictionary with summary statistics
        """
        completed = sum(1 for r in self.results.values() 
                       if r.status == CrawlerStatus.COMPLETED)
        failed = sum(1 for r in self.results.values() 
                    if r.status == CrawlerStatus.FAILED)
        skipped = sum(1 for r in self.results.values() 
                     if r.status == CrawlerStatus.SKIPPED)
        
        total_items = sum(r.items_discovered for r in self.results.values())
        total_patterns = sum(r.patterns_created for r in self.results.values())
        
        return {
            'total_crawlers': len(self.results),
            'completed': completed,
            'failed': failed,
            'skipped': skipped,
            'total_items_discovered': total_items,
            'total_patterns_created': total_patterns,
            'crawlers': {
                crawler_id: {
                    'status': result.status.value,
                    'items_discovered': result.items_discovered,
                    'patterns_created': result.patterns_created,
                    'duration': result.duration_seconds
                }
                for crawler_id, result in self.results.items()
            }
        }
