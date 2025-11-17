"""
Tests for CORTEX Adaptive Crawling Strategies

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
from unittest.mock import Mock, call
import os

from src.crawler.adaptive_strategies import (
    AdaptiveCrawler,
    CrawlStrategy,
    CrawlConfig,
    CrawlProgress,
    CrawlResult
)
from src.crawler.size_detector import SizeCategory


@pytest.fixture
def sample_files():
    """Create sample file list"""
    return [
        '/project/src/main.py',
        '/project/src/utils.py',
        '/project/src/models.py',
        '/project/src/config.py',
        '/project/tests/test_main.py',
        '/project/tests/test_utils.py',
        '/project/docs/index.md',
        '/project/app.cs',
        '/project/program.cs'
    ]


@pytest.fixture
def mock_analyzer():
    """Create mock analyzer function"""
    def analyzer(file_path):
        return {
            'loc': 100,
            'dependencies': ['/other/file.py'],
            'module': os.path.basename(file_path).split('.')[0]
        }
    return analyzer


class TestAdaptiveCrawler:
    """Test adaptive crawler functionality"""
    
    def test_strategy_selection_small(self):
        """Test strategy selection for small codebase"""
        crawler = AdaptiveCrawler()
        config = crawler.select_strategy(SizeCategory.SMALL)
        
        assert config.strategy == CrawlStrategy.FULL_ANALYSIS
        assert config.sample_rate == 1.0
        assert config.expected_accuracy == 1.0
        assert config.time_budget_seconds == 300  # 5 minutes
    
    def test_strategy_selection_medium(self):
        """Test strategy selection for medium codebase"""
        crawler = AdaptiveCrawler()
        config = crawler.select_strategy(SizeCategory.MEDIUM)
        
        assert config.strategy == CrawlStrategy.CHUNKED_ANALYSIS
        assert config.sample_rate == 1.0
        assert config.chunk_size == 100
        assert config.time_budget_seconds == 900  # 15 minutes
    
    def test_strategy_selection_large(self):
        """Test strategy selection for large codebase"""
        crawler = AdaptiveCrawler()
        config = crawler.select_strategy(SizeCategory.LARGE)
        
        assert config.strategy == CrawlStrategy.SAMPLING_CHUNKED
        assert config.sample_rate == 0.20  # 20%
        assert config.expected_accuracy == 0.85  # 85%
        assert config.time_budget_seconds == 1200  # 20 minutes
    
    def test_strategy_selection_massive(self):
        """Test strategy selection for massive codebase"""
        crawler = AdaptiveCrawler()
        config = crawler.select_strategy(SizeCategory.MASSIVE)
        
        assert config.strategy == CrawlStrategy.INTELLIGENT_SAMPLING
        assert config.sample_rate == 0.05  # 5%
        assert config.expected_accuracy == 0.70  # 70%
        assert config.time_budget_seconds == 1800  # 30 minutes
    
    def test_full_analysis_crawl(self, sample_files, mock_analyzer):
        """Test full analysis strategy"""
        crawler = AdaptiveCrawler()
        config = CrawlConfig(
            strategy=CrawlStrategy.FULL_ANALYSIS,
            chunk_size=1000,
            sample_rate=1.0,
            time_budget_seconds=300,
            checkpoint_interval=100,
            expected_accuracy=1.0
        )
        
        result = crawler.crawl('/project', sample_files, config, mock_analyzer)
        
        # Should analyze all files
        assert result.files_analyzed == len(sample_files)
        assert result.files_skipped == 0
        assert result.strategy_used == CrawlStrategy.FULL_ANALYSIS
    
    def test_stratified_sampling(self, sample_files):
        """Test stratified sampling across file types"""
        crawler = AdaptiveCrawler()
        sampled = crawler._stratified_sample(sample_files, 0.50)
        
        # Should sample approximately 50%
        assert len(sampled) >= len(sample_files) * 0.4  # Allow some variance
        assert len(sampled) <= len(sample_files) * 0.6
        
        # Should include files from different extensions
        extensions = set(os.path.splitext(f)[1] for f in sampled)
        assert len(extensions) > 1  # Multiple file types
    
    def test_intelligent_sampling_prioritizes_main_files(self, sample_files):
        """Test that intelligent sampling prioritizes key files"""
        crawler = AdaptiveCrawler()
        sampled = crawler._intelligent_sample(sample_files, 0.30)
        
        # Should include priority files (main.py, config.py, program.cs)
        sampled_basenames = [os.path.basename(f) for f in sampled]
        
        # At least one priority file should be included
        priority_found = any(
            'main.' in name or 'config.' in name or 'program.' in name
            for name in sampled_basenames
        )
        assert priority_found
    
    def test_progress_callback(self, sample_files, mock_analyzer):
        """Test that progress callback is invoked"""
        progress_calls = []
        
        def progress_callback(progress: CrawlProgress):
            progress_calls.append(progress)
        
        crawler = AdaptiveCrawler(progress_callback=progress_callback)
        config = CrawlConfig(
            strategy=CrawlStrategy.FULL_ANALYSIS,
            chunk_size=1000,
            sample_rate=1.0,
            time_budget_seconds=300,
            checkpoint_interval=100,
            expected_accuracy=1.0
        )
        
        crawler.crawl('/project', sample_files, config, mock_analyzer)
        
        # Should have received progress updates
        assert len(progress_calls) > 0
        
        # Last progress should show completion
        last_progress = progress_calls[-1]
        assert last_progress.files_processed == len(sample_files)
    
    def test_checkpoint_creation(self, sample_files, mock_analyzer):
        """Test checkpoint creation during crawling"""
        crawler = AdaptiveCrawler()
        config = CrawlConfig(
            strategy=CrawlStrategy.FULL_ANALYSIS,
            chunk_size=1000,
            sample_rate=1.0,
            time_budget_seconds=300,
            checkpoint_interval=3,  # Checkpoint every 3 files
            expected_accuracy=1.0
        )
        
        result = crawler.crawl('/project', sample_files, config, mock_analyzer)
        
        # Should create checkpoints
        assert result.checkpoints_created > 0
        assert len(crawler.checkpoints) > 0
        
        # Checkpoint should have required fields
        checkpoint = crawler.checkpoints[0]
        assert 'files_processed' in checkpoint
        assert 'checkpoint_hash' in checkpoint
    
    def test_chunking(self):
        """Test file chunking"""
        crawler = AdaptiveCrawler()
        files = [f'file_{i}.py' for i in range(25)]
        
        chunks = crawler._create_chunks(files, chunk_size=10)
        
        # Should create 3 chunks (10, 10, 5)
        assert len(chunks) == 3
        assert len(chunks[0]) == 10
        assert len(chunks[1]) == 10
        assert len(chunks[2]) == 5
    
    def test_time_budget_enforcement(self, sample_files):
        """Test that time budget is enforced"""
        def slow_analyzer(file_path):
            import time
            time.sleep(0.1)  # Simulate slow analysis
            return {'loc': 100, 'dependencies': [], 'module': 'test'}
        
        crawler = AdaptiveCrawler()
        config = CrawlConfig(
            strategy=CrawlStrategy.FULL_ANALYSIS,
            chunk_size=1000,
            sample_rate=1.0,
            time_budget_seconds=1,  # Very short budget
            checkpoint_interval=100,
            expected_accuracy=1.0
        )
        
        result = crawler.crawl('/project', sample_files, config, slow_analyzer)
        
        # Should stop early due to time budget
        # (May not analyze all files due to timeout)
        assert result.actual_time_seconds <= 2.0  # Allow small buffer
    
    def test_error_handling_during_crawl(self, sample_files):
        """Test graceful error handling for failed files"""
        def failing_analyzer(file_path):
            if 'test_' in file_path:
                raise ValueError("Analysis failed")
            return {'loc': 100, 'dependencies': [], 'module': 'test'}
        
        crawler = AdaptiveCrawler()
        config = CrawlConfig(
            strategy=CrawlStrategy.FULL_ANALYSIS,
            chunk_size=1000,
            sample_rate=1.0,
            time_budget_seconds=300,
            checkpoint_interval=100,
            expected_accuracy=1.0
        )
        
        result = crawler.crawl('/project', sample_files, config, failing_analyzer)
        
        # Should skip failed files and continue
        assert result.files_skipped > 0
        assert result.files_analyzed < len(sample_files)
    
    def test_format_strategy_summary(self):
        """Test strategy summary formatting"""
        crawler = AdaptiveCrawler()
        config = CrawlConfig(
            strategy=CrawlStrategy.SAMPLING_CHUNKED,
            chunk_size=50,
            sample_rate=0.20,
            time_budget_seconds=1200,
            checkpoint_interval=100,
            expected_accuracy=0.85
        )
        
        summary = crawler.format_strategy_summary(config)
        
        assert "Sampling Chunked" in summary
        assert "20%" in summary
        assert "50 files" in summary
        assert "20 minutes" in summary
        assert "85%" in summary
    
    def test_format_crawl_results(self, sample_files, mock_analyzer):
        """Test crawl results formatting"""
        crawler = AdaptiveCrawler()
        config = CrawlConfig(
            strategy=CrawlStrategy.FULL_ANALYSIS,
            chunk_size=1000,
            sample_rate=1.0,
            time_budget_seconds=300,
            checkpoint_interval=100,
            expected_accuracy=1.0
        )
        
        result = crawler.crawl('/project', sample_files, config, mock_analyzer)
        formatted = crawler.format_crawl_results(result)
        
        assert "Crawl Complete" in formatted
        assert "Files Analyzed:" in formatted
        assert "Total LOC:" in formatted
        assert "Modules Found:" in formatted
        assert "Relationships Mapped:" in formatted


class TestCrawlDataStructures:
    """Test crawl-related data structures"""
    
    def test_crawl_config_creation(self):
        """Test CrawlConfig creation"""
        config = CrawlConfig(
            strategy=CrawlStrategy.CHUNKED_ANALYSIS,
            chunk_size=100,
            sample_rate=1.0,
            time_budget_seconds=900,
            checkpoint_interval=100,
            expected_accuracy=1.0
        )
        
        assert config.strategy == CrawlStrategy.CHUNKED_ANALYSIS
        assert config.chunk_size == 100
    
    def test_crawl_progress_creation(self):
        """Test CrawlProgress creation"""
        progress = CrawlProgress(
            files_processed=50,
            files_total=100,
            chunks_completed=1,
            chunks_total=2,
            current_file='test.py',
            elapsed_seconds=30.0,
            estimated_remaining_seconds=30.0
        )
        
        assert progress.files_processed == 50
        assert progress.current_file == 'test.py'
    
    def test_crawl_result_creation(self):
        """Test CrawlResult creation"""
        result = CrawlResult(
            files_analyzed=100,
            files_skipped=10,
            total_loc_analyzed=10000,
            strategy_used=CrawlStrategy.FULL_ANALYSIS,
            actual_time_seconds=120.0,
            accuracy_estimate=1.0,
            checkpoints_created=2,
            relationships_found={'file1.py': ['file2.py']},
            modules_discovered=['module1', 'module2']
        )
        
        assert result.files_analyzed == 100
        assert len(result.modules_discovered) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
