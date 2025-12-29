"""
CORTEX Discovery Report Crawlers

This package contains crawlers that analyze different aspects of a project
to generate comprehensive discovery reports showcasing CORTEX intelligence.

Available Crawlers:
- FileScannerCrawler: Analyze file structure and technology stack
- GitAnalyzerCrawler: Extract development history and activity
- TestParserCrawler: Analyze test coverage and quality
- DocMapperCrawler: Map documentation structure
- BrainInspectorCrawler: Analyze CORTEX brain state (Tier 1/2/3)
- PluginRegistryCrawler: Inventory plugin ecosystem
- HealthAssessorCrawler: Evaluate project health and provide recommendations
"""

from .base_crawler import BaseCrawler
from .file_scanner import FileScannerCrawler
from .git_analyzer import GitAnalyzerCrawler
from .test_parser import TestParserCrawler
from .doc_mapper import DocMapperCrawler
from .brain_inspector import BrainInspectorCrawler
from .plugin_registry import PluginRegistryCrawler
from .health_assessor import HealthAssessorCrawler

__all__ = [
    'BaseCrawler',
    'FileScannerCrawler',
    'GitAnalyzerCrawler',
    'TestParserCrawler',
    'DocMapperCrawler',
    'BrainInspectorCrawler',
    'PluginRegistryCrawler',
    'HealthAssessorCrawler',
]
