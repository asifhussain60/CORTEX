"""
CORTEX Crawler System

Unified crawler architecture for discovering and extracting knowledge from:
- UI components (React, Angular, Vue, etc.)
- REST APIs (endpoints, OpenAPI specs)
- Databases (Oracle, SQL Server, PostgreSQL, etc.)
- Development tools and configurations

Architecture:
- BaseCrawler: Abstract base class for all crawlers
- CrawlerOrchestrator: Manages crawler execution and dependencies
- Individual Crawlers: Specialized implementations for each domain

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
"""

from .base_crawler import BaseCrawler, CrawlerResult, CrawlerStatus
from .orchestrator import CrawlerOrchestrator

__all__ = [
    'BaseCrawler',
    'CrawlerResult',
    'CrawlerStatus',
    'CrawlerOrchestrator',
]
