"""
Targeted Crawler with Safety Mechanisms

Extension of BaseCrawler that adds bounded, task-focused crawling with:
- Radius Limits: Maximum N hops from origin
- Circuit Breakers: Timeout, file count, memory limits
- Task Scoping: Only follow relationships relevant to current operation
- Privacy Protection: Skip sensitive patterns

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import time
import logging
import re
import psutil
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import deque

from .base_crawler import BaseCrawler, CrawlerResult, CrawlerStatus, CrawlerPriority


logger = logging.getLogger(__name__)


class CrawlScope(Enum):
    """Task-focused crawl scopes - defines what to analyze."""
    VIEW_STRUCTURE = "view_structure"  # UI component hierarchy
    DATABASE_SCHEMA = "database_schema"  # Table relationships
    CODE_DEPENDENCIES = "code_dependencies"  # Import/call graph
    SIGNALR_FLOW = "signalr_flow"  # Real-time event chains
    API_ENDPOINTS = "api_endpoints"  # REST/GraphQL routes


class CircuitBreakerException(Exception):
    """Raised when circuit breaker triggers (timeout/limits exceeded)."""
    pass


class RadiusLimitException(Exception):
    """Raised when radius limit exceeded (too many hops from origin)."""
    pass


@dataclass
class TargetedCrawlerConfig:
    """Configuration for bounded crawler behavior."""
    
    # Radius Limits (prevent infinite loops in monoliths)
    max_depth: int = 3  # Maximum hops from origin
    max_breadth: int = 10  # Maximum children per node
    
    # Circuit Breakers (abort when limits exceeded)
    timeout_seconds: int = 30  # Abort after N seconds
    max_files: int = 50  # Maximum files to analyze
    max_memory_mb: int = 500  # Memory limit (MB)
    
    # Task Scoping (only follow relevant relationships)
    scope: CrawlScope = CrawlScope.VIEW_STRUCTURE
    follow_imports: bool = True  # Follow import statements
    follow_calls: bool = False  # Follow function calls (expensive)
    follow_db_fks: bool = True  # Follow foreign key relationships
    
    # Privacy Protection (skip sensitive patterns)
    skip_patterns: List[str] = field(default_factory=lambda: [
        r'.*password.*',
        r'.*secret.*',
        r'.*token.*',
        r'.*api[_-]?key.*',
        r'.*connection[_-]?string.*',
        r'.*credential.*',
    ])
    
    # Output Control
    verbose: bool = False
    max_result_size_mb: int = 5  # Limit result JSON size


@dataclass
class TargetedCrawlerResult:
    """
    Extended result with targeting metrics.
    
    Includes safety metrics to verify bounded behavior.
    """
    scope: CrawlScope
    origin: str  # Starting point (file path, table name, etc.)
    timestamp: str
    duration_seconds: float
    
    # Analysis Results
    nodes: List[Dict[str, Any]]  # Discovered nodes
    edges: List[Tuple[str, str, str]]  # (from, to, relationship_type)
    metadata: Dict[str, Any]  # Scope-specific metadata
    
    # Safety Metrics (verify bounded behavior)
    depth_reached: int
    files_analyzed: int
    memory_peak_mb: float
    circuit_breaker_triggered: bool
    radius_limit_hit: bool
    
    # Warnings (non-fatal issues)
    warnings: List[str] = field(default_factory=list)
    skipped_paths: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'scope': self.scope.value,
            'origin': self.origin,
            'timestamp': self.timestamp,
            'duration_seconds': round(self.duration_seconds, 2),
            'nodes': self.nodes,
            'edges': self.edges,
            'metadata': self.metadata,
            'safety_metrics': {
                'depth_reached': self.depth_reached,
                'files_analyzed': self.files_analyzed,
                'memory_peak_mb': round(self.memory_peak_mb, 2),
                'circuit_breaker_triggered': self.circuit_breaker_triggered,
                'radius_limit_hit': self.radius_limit_hit,
            },
            'warnings': self.warnings,
            'skipped_paths': self.skipped_paths,
        }


class TargetedCrawler(BaseCrawler):
    """
    Base class for bounded, task-focused crawlers.
    
    Extends BaseCrawler with safety mechanisms to prevent:
    - Infinite loops in monolithic applications
    - Excessive memory consumption
    - Long-running operations
    - Privacy violations
    
    Safety Features:
    1. **Radius Limits**: Stop after max_depth hops from origin
    2. **Circuit Breakers**: Abort if timeout/file count/memory exceeded
    3. **Task Scoping**: Only follow relationships relevant to current task
    4. **Privacy Protection**: Skip sensitive patterns (passwords, tokens)
    
    Subclasses implement scope-specific crawl logic.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize targeted crawler.
        
        Args:
            config: Configuration dictionary (merged with TargetedCrawlerConfig)
        """
        super().__init__(config)
        
        # Targeted crawler configuration
        self.targeted_config = TargetedCrawlerConfig(
            max_depth=self.config.get('max_depth', 3),
            max_breadth=self.config.get('max_breadth', 10),
            timeout_seconds=self.config.get('timeout_seconds', 30),
            max_files=self.config.get('max_files', 50),
            max_memory_mb=self.config.get('max_memory_mb', 500),
            scope=CrawlScope(self.config.get('scope', 'view_structure')),
            follow_imports=self.config.get('follow_imports', True),
            follow_calls=self.config.get('follow_calls', False),
            follow_db_fks=self.config.get('follow_db_fks', True),
            verbose=self.config.get('verbose', False),
        )
        
        # Safety tracking
        self.start_time: Optional[float] = None
        self.files_analyzed: int = 0
        self.memory_peak_mb: float = 0.0
        self.visited: Set[str] = set()
        self.warnings: List[str] = []
        self.skipped_paths: List[str] = []
    
    def execute(self, origin: str) -> TargetedCrawlerResult:
        """
        Main entry point for targeted crawl.
        
        Args:
            origin: Starting point (file path, table name, class name, etc.)
        
        Returns:
            TargetedCrawlerResult with discovered nodes, edges, and safety metrics
        
        Raises:
            CircuitBreakerException: If timeout/limits exceeded
            RadiusLimitException: If max depth exceeded
        """
        info = self.get_crawler_info()
        self._start_time = datetime.now()
        self.start_time = self._start_time.timestamp()
        
        # Initialize result tracking
        self.result = CrawlerResult(
            crawler_id=info['crawler_id'],
            crawler_name=info['name'],
            status=CrawlerStatus.INITIALIZING,
            started_at=self._start_time
        )
        
        circuit_breaker_triggered = False
        radius_limit_hit = False
        nodes = []
        edges = []
        max_depth = 0
        
        try:
            # Validate can run
            if not self.validate():
                self.result.status = CrawlerStatus.SKIPPED
                self.result.errors.append("Validation failed")
                return self._create_empty_result(origin)
            
            self.result.status = CrawlerStatus.CRAWLING
            self._log(f"Starting targeted crawl: {origin}")
            
            # Execute targeted crawl (subclass implements)
            nodes, edges, max_depth = self.crawl_targeted(origin)
            
            # Check if we hit radius limit
            radius_limit_hit = max_depth >= self.targeted_config.max_depth
            
            self.result.status = CrawlerStatus.COMPLETED
            self.result.items_discovered = len(nodes)
            
        except CircuitBreakerException as e:
            self._log(f"Circuit breaker triggered: {e}", "WARNING")
            circuit_breaker_triggered = True
            self.result.status = CrawlerStatus.FAILED
            self.result.errors.append(f"Circuit breaker: {e}")
            
        except RadiusLimitException as e:
            self._log(f"Radius limit hit: {e}", "INFO")
            radius_limit_hit = True
            self.result.status = CrawlerStatus.COMPLETED
            self.result.warnings.append(f"Radius limit: {e}")
            
        except Exception as e:
            self._log(f"Unexpected error: {e}", "ERROR")
            self.result.status = CrawlerStatus.FAILED
            self.result.errors.append(f"Error: {e}")
        
        # Calculate duration
        self.result.completed_at = datetime.now()
        duration = (self.result.completed_at - self._start_time).total_seconds()
        self.result.duration_seconds = duration
        
        # Update memory peak
        process = psutil.Process()
        self.memory_peak_mb = max(
            self.memory_peak_mb,
            process.memory_info().rss / (1024 * 1024)
        )
        
        # Create targeted result
        return TargetedCrawlerResult(
            scope=self.targeted_config.scope,
            origin=origin,
            timestamp=self.result.completed_at.isoformat(),
            duration_seconds=duration,
            nodes=nodes,
            edges=edges,
            metadata=self._get_targeted_metadata(),
            depth_reached=max_depth,
            files_analyzed=self.files_analyzed,
            memory_peak_mb=self.memory_peak_mb,
            circuit_breaker_triggered=circuit_breaker_triggered,
            radius_limit_hit=radius_limit_hit,
            warnings=self.warnings + self.result.warnings,
            skipped_paths=self.skipped_paths,
        )
    
    @abstractmethod
    def crawl_targeted(
        self,
        origin: str
    ) -> Tuple[List[Dict], List[Tuple[str, str, str]], int]:
        """
        Execute bounded crawl from origin.
        
        Subclasses implement scope-specific logic (view, database, code, etc.)
        
        Args:
            origin: Starting point for crawl
        
        Returns:
            Tuple of (nodes, edges, max_depth_reached)
        """
        pass
    
    @abstractmethod
    def _get_targeted_metadata(self) -> Dict[str, Any]:
        """
        Get scope-specific metadata.
        
        Returns:
            Dictionary with crawler-specific metadata
        """
        pass
    
    def _check_circuit_breakers(self) -> None:
        """
        Check if circuit breakers should trigger.
        
        Raises:
            CircuitBreakerException: If any limit exceeded
        """
        if self.start_time is None:
            return
        
        # Timeout check
        elapsed = time.time() - self.start_time
        if elapsed > self.targeted_config.timeout_seconds:
            raise CircuitBreakerException(
                f"Timeout: {elapsed:.1f}s > {self.targeted_config.timeout_seconds}s"
            )
        
        # File count check
        if self.files_analyzed > self.targeted_config.max_files:
            raise CircuitBreakerException(
                f"File limit: {self.files_analyzed} > {self.targeted_config.max_files}"
            )
        
        # Memory check
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        self.memory_peak_mb = max(self.memory_peak_mb, memory_mb)
        
        if memory_mb > self.targeted_config.max_memory_mb:
            raise CircuitBreakerException(
                f"Memory: {memory_mb:.1f} MB > {self.targeted_config.max_memory_mb} MB"
            )
    
    def _check_radius_limit(self, current_depth: int) -> None:
        """
        Check if radius limit exceeded.
        
        Args:
            current_depth: Current depth from origin
        
        Raises:
            RadiusLimitException: If depth exceeds max_depth
        """
        if current_depth > self.targeted_config.max_depth:
            raise RadiusLimitException(
                f"Depth {current_depth} > {self.targeted_config.max_depth}"
            )
    
    def _should_skip(self, path: str) -> bool:
        """
        Check if path should be skipped (privacy protection).
        
        Args:
            path: Path to check (file path, variable name, etc.)
        
        Returns:
            True if path matches skip patterns
        """
        path_lower = path.lower()
        for pattern in self.targeted_config.skip_patterns:
            if re.search(pattern, path_lower):
                self.warnings.append(f"Skipped sensitive: {path}")
                self.skipped_paths.append(path)
                return True
        
        return False
    
    def _mark_visited(self, node_id: str) -> bool:
        """
        Mark node as visited (prevents cycles).
        
        Args:
            node_id: Unique node identifier
        
        Returns:
            True if newly visited, False if already seen
        """
        if node_id in self.visited:
            return False
        
        self.visited.add(node_id)
        return True
    
    def _crawl_bfs(
        self,
        origin: str,
        get_children_func,
        node_type: str = "node"
    ) -> Tuple[List[Dict], List[Tuple[str, str, str]], int]:
        """
        Generic breadth-first crawl implementation.
        
        Explores all nodes at depth N before moving to depth N+1.
        Better for task-focused analysis (stays close to origin).
        
        Args:
            origin: Starting node
            get_children_func: Function(node_id, depth) -> List[child_ids]
            node_type: Type label for nodes
        
        Returns:
            Tuple of (nodes, edges, max_depth_reached)
        """
        nodes = []
        edges = []
        queue = deque([(origin, 0)])  # (node_id, depth)
        max_depth_reached = 0
        
        self._mark_visited(origin)
        nodes.append({
            'id': origin,
            'type': node_type,
            'depth': 0,
        })
        
        while queue:
            self._check_circuit_breakers()
            
            current_id, current_depth = queue.popleft()
            max_depth_reached = max(max_depth_reached, current_depth)
            
            # Check radius limit
            if current_depth >= self.targeted_config.max_depth:
                self._log(f"Radius limit at depth {current_depth}", "INFO")
                continue
            
            # Get children
            try:
                children = get_children_func(current_id, current_depth)
            except Exception as e:
                self.warnings.append(f"Failed children of {current_id}: {e}")
                continue
            
            # Limit breadth
            if len(children) > self.targeted_config.max_breadth:
                self.warnings.append(
                    f"Breadth limit: {len(children)} children at {current_id}"
                )
                children = children[:self.targeted_config.max_breadth]
            
            # Process children
            for child_id in children:
                if self._should_skip(child_id):
                    continue
                
                # Add edge
                edges.append((current_id, child_id, 'references'))
                
                # Visit child
                if self._mark_visited(child_id):
                    nodes.append({
                        'id': child_id,
                        'type': node_type,
                        'depth': current_depth + 1,
                    })
                    queue.append((child_id, current_depth + 1))
        
        return nodes, edges, max_depth_reached
    
    def _log(self, message: str, level: str = "INFO") -> None:
        """Log message if verbose mode enabled."""
        if self.targeted_config.verbose:
            log_func = getattr(logger, level.lower(), logger.info)
            log_func(f"[{self.__class__.__name__}] {message}")
    
    def _create_empty_result(self, origin: str) -> TargetedCrawlerResult:
        """Create empty result when validation fails."""
        return TargetedCrawlerResult(
            scope=self.targeted_config.scope,
            origin=origin,
            timestamp=datetime.now().isoformat(),
            duration_seconds=0.0,
            nodes=[],
            edges=[],
            metadata={},
            depth_reached=0,
            files_analyzed=0,
            memory_peak_mb=0.0,
            circuit_breaker_triggered=False,
            radius_limit_hit=False,
            warnings=self.warnings,
            skipped_paths=[],
        )
