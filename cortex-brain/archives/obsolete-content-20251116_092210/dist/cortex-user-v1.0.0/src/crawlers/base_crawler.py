"""
Base Crawler Class for CORTEX

Provides abstract base class and common infrastructure for all CORTEX crawlers.
All crawlers (UI, API, Database, etc.) inherit from BaseCrawler.

Architecture:
- Standardized lifecycle (initialize → validate → crawl → store → cleanup)
- Error handling and retry logic
- Progress reporting
- Result standardization
- Knowledge graph integration

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CrawlerStatus(Enum):
    """Crawler execution status"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    VALIDATING = "validating"
    CRAWLING = "crawling"
    STORING = "storing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class CrawlerPriority(Enum):
    """Crawler execution priority"""
    CRITICAL = 1  # Tooling crawler (determines what else to run)
    HIGH = 2      # UI, API crawlers
    MEDIUM = 3    # Database crawlers
    LOW = 4       # Optional crawlers


@dataclass
class CrawlerResult:
    """Standardized result from crawler execution"""
    crawler_id: str
    crawler_name: str
    status: CrawlerStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    items_discovered: int = 0
    items_stored: int = 0
    patterns_created: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies_satisfied: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'crawler_id': self.crawler_id,
            'crawler_name': self.crawler_name,
            'status': self.status.value,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'items_discovered': self.items_discovered,
            'items_stored': self.items_stored,
            'patterns_created': self.patterns_created,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'dependencies_satisfied': self.dependencies_satisfied
        }


class BaseCrawler(ABC):
    """
    Abstract base class for all CORTEX crawlers.
    
    All crawlers must:
    1. Inherit from BaseCrawler
    2. Implement get_crawler_info() method
    3. Implement validate() method
    4. Implement crawl() method
    5. Implement store_results() method
    
    Lifecycle:
    1. initialize() - Setup crawler (config, connections)
    2. validate() - Check if crawler can run (dependencies, credentials)
    3. crawl() - Execute discovery logic
    4. store_results() - Save to knowledge graph
    5. cleanup() - Release resources
    
    Example:
    ```python
    class UICrawler(BaseCrawler):
        def get_crawler_info(self) -> Dict[str, Any]:
            return {
                'crawler_id': 'ui_crawler',
                'name': 'UI Component Crawler',
                'version': '1.0.0',
                'priority': CrawlerPriority.HIGH,
                'dependencies': ['tooling_crawler']
            }
        
        def validate(self) -> bool:
            return self.workspace_path.exists()
        
        def crawl(self) -> Dict[str, Any]:
            # Discover UI components
            return {'components': [...]}
        
        def store_results(self, data: Dict[str, Any]) -> int:
            # Store in knowledge graph
            return len(data['components'])
    ```
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base crawler.
        
        Args:
            config: Configuration dictionary with crawler settings
        """
        self.config = config or {}
        self.workspace_path = self.config.get('workspace_path')
        self.knowledge_graph = self.config.get('knowledge_graph')
        self.result = None
        self._start_time = None
        
    @abstractmethod
    def get_crawler_info(self) -> Dict[str, Any]:
        """
        Get crawler metadata.
        
        Returns:
            Dictionary with:
                - crawler_id: Unique identifier
                - name: Human-readable name
                - version: Semantic version
                - priority: CrawlerPriority enum
                - dependencies: List of crawler_ids this depends on
                - description: Brief description
        """
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate crawler can execute.
        
        Checks:
        - Required dependencies available
        - Credentials present
        - Target resources accessible
        
        Returns:
            True if crawler can run, False otherwise
        """
        pass
    
    @abstractmethod
    def crawl(self) -> Dict[str, Any]:
        """
        Execute crawler discovery logic.
        
        Returns:
            Dictionary with discovered items (format varies by crawler)
        """
        pass
    
    @abstractmethod
    def store_results(self, data: Dict[str, Any]) -> int:
        """
        Store crawled data in knowledge graph.
        
        Args:
            data: Data returned from crawl()
            
        Returns:
            Number of patterns stored
        """
        pass
    
    def initialize(self) -> bool:
        """
        Initialize crawler (setup connections, validate config).
        
        Returns:
            True if initialization successful
        """
        try:
            info = self.get_crawler_info()
            logger.info(f"Initializing {info['name']} v{info['version']}")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def cleanup(self) -> None:
        """
        Cleanup resources (close connections, release locks).
        
        Called after crawler completes or fails.
        """
        pass
    
    def execute(self) -> CrawlerResult:
        """
        Execute complete crawler lifecycle.
        
        Lifecycle:
        1. Initialize
        2. Validate
        3. Crawl
        4. Store results
        5. Cleanup
        
        Returns:
            CrawlerResult with execution details
        """
        info = self.get_crawler_info()
        self._start_time = datetime.now()
        
        self.result = CrawlerResult(
            crawler_id=info['crawler_id'],
            crawler_name=info['name'],
            status=CrawlerStatus.PENDING,
            started_at=self._start_time
        )
        
        try:
            # Initialize
            self.result.status = CrawlerStatus.INITIALIZING
            if not self.initialize():
                self.result.status = CrawlerStatus.FAILED
                self.result.errors.append("Initialization failed")
                return self._finalize_result()
            
            # Validate
            self.result.status = CrawlerStatus.VALIDATING
            if not self.validate():
                self.result.status = CrawlerStatus.SKIPPED
                self.result.warnings.append("Validation failed - crawler skipped")
                return self._finalize_result()
            
            # Crawl
            self.result.status = CrawlerStatus.CRAWLING
            logger.info(f"Starting crawl: {info['name']}")
            data = self.crawl()
            self.result.items_discovered = self._count_items(data)
            logger.info(f"Discovered {self.result.items_discovered} items")
            
            # Store results
            self.result.status = CrawlerStatus.STORING
            if self.knowledge_graph:
                stored = self.store_results(data)
                self.result.items_stored = stored
                self.result.patterns_created = stored
                logger.info(f"Stored {stored} patterns")
            else:
                self.result.warnings.append("No knowledge graph provided - results not stored")
            
            # Success
            self.result.status = CrawlerStatus.COMPLETED
            logger.info(f"Crawler completed: {info['name']}")
            
        except Exception as e:
            self.result.status = CrawlerStatus.FAILED
            self.result.errors.append(str(e))
            logger.error(f"Crawler failed: {info['name']} - {e}")
            
        finally:
            self.cleanup()
            return self._finalize_result()
    
    def _finalize_result(self) -> CrawlerResult:
        """Finalize result with timing information"""
        self.result.completed_at = datetime.now()
        self.result.duration_seconds = (
            self.result.completed_at - self.result.started_at
        ).total_seconds()
        return self.result
    
    def _count_items(self, data: Dict[str, Any]) -> int:
        """
        Count discovered items from crawl data.
        
        Override this method if your crawler has custom counting logic.
        
        Args:
            data: Data returned from crawl()
            
        Returns:
            Number of items discovered
        """
        # Default: count all list items in data dictionary
        count = 0
        for value in data.values():
            if isinstance(value, list):
                count += len(value)
        return count
