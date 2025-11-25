"""
CORTEX Crawler System

Unified crawler architecture for discovering and extracting knowledge from:
- UI components (React, Angular, Vue, etc.)
- REST APIs (endpoints, OpenAPI specs)
- Databases (Oracle, SQL Server, PostgreSQL, etc.)
- Development tools and configurations
- Multi-application workspaces (NEW)

Architecture:
- BaseCrawler: Abstract base class for all crawlers
- CrawlerOrchestrator: Manages crawler execution and dependencies
- MultiApplicationOrchestrator: Progressive multi-app loading (NEW)
- Individual Crawlers: Specialized implementations for each domain

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
"""

from .base_crawler import BaseCrawler, CrawlerResult, CrawlerStatus, CrawlerPriority
from .orchestrator import CrawlerOrchestrator, OrchestrationResult

# Import specialized crawlers
try:
    from .tooling_crawler import ToolingCrawler
except ImportError:
    ToolingCrawler = None

try:
    from .ui_crawler import UICrawler
except ImportError:
    UICrawler = None

try:
    from .targeted_crawler import TargetedCrawler
except ImportError:
    TargetedCrawler = None

# Import multi-app components (Phase 1 implementation)
from .workspace_topology_crawler import WorkspaceTopologyCrawler, ApplicationInfo
from .application_scoped_crawler import ApplicationScopedCrawler, ApplicationContext
from .persistent_cache import PersistentApplicationCache
from .database_inference_engine import DatabaseSchemaInferenceEngine, TableInfo
from .multi_app_orchestrator import (
    MultiApplicationOrchestrator,
    SharedDatabaseContextManager,
    SharedDatabaseSchema
)

# Import Phase 2 activity tracking components
from .filesystem_activity_monitor import FileSystemActivityMonitor, ApplicationActivity, FileActivity
from .git_history_analyzer import GitHistoryAnalyzer, ApplicationGitActivity, FileChangeInfo
from .access_pattern_tracker import AccessPatternTracker, ApplicationAccessPattern, AccessInfo
from .application_prioritization_engine import ApplicationPrioritizationEngine, ApplicationPriority
from .smart_cache_manager import SmartCacheManager, ApplicationState
__all__ = [
    # Base classes
    'BaseCrawler',
    'CrawlerResult',
    'CrawlerStatus',
    'CrawlerPriority',
    
    # Orchestrators
    'CrawlerOrchestrator',
    'OrchestrationResult',
    'MultiApplicationOrchestrator',
    
    # Specialized crawlers (if available)
    'ToolingCrawler',
    'UICrawler',
    'TargetedCrawler',
    
    # Multi-app Phase 1 components
    'WorkspaceTopologyCrawler',
    'ApplicationScopedCrawler',
    'PersistentApplicationCache',
    'DatabaseSchemaInferenceEngine',
    'SharedDatabaseContextManager',
    
    # Multi-app Phase 2 components (Activity Tracking)
    'FileSystemActivityMonitor',
    'GitHistoryAnalyzer',
    'AccessPatternTracker',
    'ApplicationPrioritizationEngine',
    'SmartCacheManager',
    
    # Data classes
    'ApplicationInfo',
    'ApplicationContext',
    'TableInfo',
    'SharedDatabaseSchema',
]
