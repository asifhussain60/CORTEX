"""
Simple test to demonstrate the crawler system works.

Run: python -m pytest tests/crawlers/test_crawler_system.py -v
"""

import pytest
from pathlib import Path
from src.crawlers.base_crawler import BaseCrawler, CrawlerPriority, CrawlerStatus
from src.crawlers.orchestrator import CrawlerOrchestrator


class DummyCrawler(BaseCrawler):
    """Dummy crawler for testing"""
    
    def get_crawler_info(self):
        return {
            'crawler_id': 'dummy_crawler',
            'name': 'Dummy Test Crawler',
            'version': '1.0.0',
            'priority': CrawlerPriority.MEDIUM,
            'dependencies': [],
            'description': 'Test crawler'
        }
    
    def validate(self):
        return True
    
    def crawl(self):
        return {'items': ['item1', 'item2', 'item3']}
    
    def store_results(self, data):
        return len(data['items'])


def test_base_crawler_lifecycle():
    """Test base crawler execution lifecycle"""
    crawler = DummyCrawler({'workspace_path': Path.cwd()})
    result = crawler.execute()
    
    assert result.status == CrawlerStatus.COMPLETED
    assert result.items_discovered == 3
    assert result.duration_seconds > 0


def test_orchestrator_registration():
    """Test orchestrator can register crawlers"""
    orchestrator = CrawlerOrchestrator(
        workspace_path=Path.cwd(),
        knowledge_graph=None
    )
    
    orchestrator.register(DummyCrawler)
    
    assert 'dummy_crawler' in orchestrator.crawler_classes
    assert 'dummy_crawler' in orchestrator.dependency_graph


def test_orchestrator_execution():
    """Test orchestrator can run registered crawlers"""
    orchestrator = CrawlerOrchestrator(
        workspace_path=Path.cwd(),
        knowledge_graph=None
    )
    
    orchestrator.register(DummyCrawler)
    result = orchestrator.run_all()
    
    assert result.total_crawlers == 1
    assert result.completed == 1
    assert result.failed == 0
    assert result.total_items_discovered == 3


def test_crawler_priority_ordering():
    """Test crawlers execute in priority order"""
    
    class HighPriorityCrawler(BaseCrawler):
        def get_crawler_info(self):
            return {
                'crawler_id': 'high_priority',
                'name': 'High Priority',
                'version': '1.0.0',
                'priority': CrawlerPriority.HIGH,
                'dependencies': [],
                'description': 'High priority test'
            }
        
        def validate(self):
            return True
        
        def crawl(self):
            return {'items': [1]}
        
        def store_results(self, data):
            return 1
    
    class LowPriorityCrawler(BaseCrawler):
        def get_crawler_info(self):
            return {
                'crawler_id': 'low_priority',
                'name': 'Low Priority',
                'version': '1.0.0',
                'priority': CrawlerPriority.LOW,
                'dependencies': [],
                'description': 'Low priority test'
            }
        
        def validate(self):
            return True
        
        def crawl(self):
            return {'items': [1]}
        
        def store_results(self, data):
            return 1
    
    orchestrator = CrawlerOrchestrator(
        workspace_path=Path.cwd(),
        knowledge_graph=None
    )
    
    # Register in reverse priority order
    orchestrator.register(LowPriorityCrawler)
    orchestrator.register(HighPriorityCrawler)
    
    # Resolve execution order
    execution_order = orchestrator._resolve_dependencies(['high_priority', 'low_priority'])
    
    # High priority should come first
    assert execution_order[0] == 'high_priority'
    assert execution_order[1] == 'low_priority'


def test_crawler_with_dependencies():
    """Test crawler dependencies are resolved"""
    
    class DependentCrawler(BaseCrawler):
        def get_crawler_info(self):
            return {
                'crawler_id': 'dependent',
                'name': 'Dependent Crawler',
                'version': '1.0.0',
                'priority': CrawlerPriority.MEDIUM,
                'dependencies': ['dummy_crawler'],
                'description': 'Depends on dummy'
            }
        
        def validate(self):
            return True
        
        def crawl(self):
            return {'items': [1]}
        
        def store_results(self, data):
            return 1
    
    orchestrator = CrawlerOrchestrator(
        workspace_path=Path.cwd(),
        knowledge_graph=None
    )
    
    orchestrator.register(DummyCrawler)
    orchestrator.register(DependentCrawler)
    
    # Execute all
    result = orchestrator.run_all()
    
    # Both should complete
    assert result.total_crawlers == 2
    assert result.completed == 2


def test_crawler_skip_on_validation_failure():
    """Test crawler is skipped if validation fails"""
    
    class FailingCrawler(BaseCrawler):
        def get_crawler_info(self):
            return {
                'crawler_id': 'failing',
                'name': 'Failing Crawler',
                'version': '1.0.0',
                'priority': CrawlerPriority.MEDIUM,
                'dependencies': [],
                'description': 'Always fails validation'
            }
        
        def validate(self):
            return False  # Always fail
        
        def crawl(self):
            return {'items': []}
        
        def store_results(self, data):
            return 0
    
    crawler = FailingCrawler({'workspace_path': Path.cwd()})
    result = crawler.execute()
    
    assert result.status == CrawlerStatus.SKIPPED
    assert len(result.warnings) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
