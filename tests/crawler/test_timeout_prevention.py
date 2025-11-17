"""
Tests for CORTEX Timeout Prevention System

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
import time
from unittest.mock import Mock

from src.crawler.timeout_prevention import (
    TimeoutPreventor,
    TimeoutConfig,
    TimeoutStrategy,
    TimeoutWarning,
    ProgressiveDisclosure
)


@pytest.fixture
def basic_config():
    """Create basic timeout configuration"""
    return TimeoutConfig(
        max_time_seconds=60,
        warning_threshold=0.8,
        strategy=TimeoutStrategy.GRACEFUL_STOP,
        allow_extension=True,
        max_extensions=2
    )


class TestTimeoutPreventor:
    """Test timeout prevention functionality"""
    
    def test_start_timer(self, basic_config):
        """Test timer initialization"""
        preventor = TimeoutPreventor(basic_config)
        preventor.start_timer()
        
        assert preventor.start_time is not None
        assert preventor.last_checkpoint_time is not None
    
    def test_no_warning_early_in_process(self, basic_config):
        """Test that no warning issued early in process"""
        preventor = TimeoutPreventor(basic_config)
        preventor.start_timer()
        
        # Check immediately (0% through)
        warning = preventor.check_timeout(files_processed=10, files_total=100)
        
        assert warning is None
    
    def test_warning_when_threshold_exceeded(self, basic_config):
        """Test warning when threshold exceeded"""
        preventor = TimeoutPreventor(basic_config)
        preventor.start_timer()
        
        # Simulate time passing
        preventor.start_time -= 50  # Pretend 50 seconds elapsed
        
        # Check (83% through time budget)
        warning = preventor.check_timeout(files_processed=10, files_total=100)
        
        assert warning is not None
        assert warning.percentage_used > 0.8
        assert warning.remaining_seconds < 60
    
    def test_should_stop_when_timeout(self, basic_config):
        """Test that should_stop returns True after timeout"""
        preventor = TimeoutPreventor(basic_config)
        preventor.start_timer()
        
        # Should not stop initially
        assert preventor.should_stop() is False
        
        # Simulate timeout
        preventor.start_time -= 65  # Pretend 65 seconds elapsed
        
        # Should stop now
        assert preventor.should_stop() is True
    
    def test_extension_request_success(self, basic_config):
        """Test successful time extension request"""
        preventor = TimeoutPreventor(basic_config)
        preventor.start_timer()
        
        # Request extension
        granted = preventor.request_extension(30)
        
        assert granted is True
        assert preventor.extensions_used == 1
        assert preventor.config.max_time_seconds == 90  # 60 + 30
    
    def test_extension_request_limit(self, basic_config):
        """Test extension request limit"""
        preventor = TimeoutPreventor(basic_config)
        preventor.start_timer()
        
        # Use all extensions
        preventor.request_extension(30)
        preventor.request_extension(30)
        
        # Third request should fail
        granted = preventor.request_extension(30)
        assert granted is False
        assert preventor.extensions_used == 2
    
    def test_extension_request_when_disabled(self):
        """Test extension request when not allowed"""
        config = TimeoutConfig(
            max_time_seconds=60,
            warning_threshold=0.8,
            strategy=TimeoutStrategy.GRACEFUL_STOP,
            allow_extension=False,
            max_extensions=0
        )
        
        preventor = TimeoutPreventor(config)
        preventor.start_timer()
        
        granted = preventor.request_extension(30)
        assert granted is False
    
    def test_timeout_checkpoint_creation(self, basic_config):
        """Test checkpoint creation on timeout"""
        preventor = TimeoutPreventor(basic_config)
        preventor.start_timer()
        
        checkpoint = preventor.create_timeout_checkpoint()
        
        assert 'elapsed_time' in checkpoint
        assert 'warnings_issued' in checkpoint
        assert 'extensions_used' in checkpoint
        assert 'final_strategy' in checkpoint
        assert 'checkpoint_hash' in checkpoint
    
    def test_warning_formatting(self, basic_config):
        """Test warning message formatting"""
        warning = TimeoutWarning(
            elapsed_seconds=50.0,
            remaining_seconds=10.0,
            percentage_used=0.83,
            files_processed=100,
            estimated_completion_time=70.0,
            will_timeout=True,
            recommended_action="Request time extension"
        )
        
        preventor = TimeoutPreventor(basic_config)
        formatted = preventor.format_warning(warning)
        
        assert "Timeout Warning" in formatted
        assert "83%" in formatted
        assert "Request time extension" in formatted
        assert "Timeout Likely" in formatted
    
    def test_timeout_report_formatting(self, basic_config):
        """Test final report formatting"""
        preventor = TimeoutPreventor(basic_config)
        preventor.start_timer()
        
        # Simulate some warnings
        preventor.start_time -= 50
        preventor.check_timeout(10, 100)
        
        report = preventor.format_timeout_report()
        
        assert "Timeout Prevention Report" in report
        assert "Budget Used:" in report
        assert "Warnings Issued:" in report
        assert "Extensions Used:" in report
    
    def test_multiple_warnings(self, basic_config):
        """Test multiple warnings are tracked"""
        preventor = TimeoutPreventor(basic_config)
        preventor.start_timer()
        
        # Issue multiple warnings
        preventor.start_time -= 50
        preventor.check_timeout(10, 100)
        preventor.start_time -= 5
        preventor.check_timeout(20, 100)
        
        assert len(preventor.warnings_issued) == 2


class TestProgressiveDisclosure:
    """Test progressive disclosure functionality"""
    
    def test_disclose_batch(self):
        """Test batch disclosure"""
        disclosed = []
        
        def callback(message):
            disclosed.append(message)
        
        disclosure = ProgressiveDisclosure(update_callback=callback)
        
        batch_results = {
            'modules': ['module1', 'module2'],
            'relationships': {'file1': ['file2']},
            'total_loc': 1000
        }
        
        disclosure.disclose_batch(batch_results, 50, 100)
        
        # Should have called callback
        assert len(disclosed) == 1
        assert "50%" in disclosed[0]
        assert "Modules found: 2" in disclosed[0]
    
    def test_cumulative_results(self):
        """Test cumulative result aggregation"""
        disclosure = ProgressiveDisclosure()
        
        # Disclose multiple batches
        disclosure.disclose_batch(
            {'modules': ['mod1'], 'relationships': {'f1': ['f2']}, 'total_loc': 500},
            25, 100
        )
        disclosure.disclose_batch(
            {'modules': ['mod2', 'mod1'], 'relationships': {'f3': ['f4']}, 'total_loc': 600},
            50, 100
        )
        
        cumulative = disclosure.get_cumulative_results()
        
        # Should combine results
        assert len(cumulative['modules']) == 2  # mod1, mod2 (deduplicated)
        assert cumulative['total_loc'] == 1100  # 500 + 600
        assert len(cumulative['relationships']) == 2
    
    def test_disclosure_tracking(self):
        """Test that disclosures are tracked"""
        disclosure = ProgressiveDisclosure()
        
        disclosure.disclose_batch({'modules': []}, 10, 100)
        disclosure.disclose_batch({'modules': []}, 20, 100)
        
        assert len(disclosure.disclosed_results) == 2
        assert disclosure.disclosed_results[0]['files_processed'] == 10
        assert disclosure.disclosed_results[1]['files_processed'] == 20


class TestTimeoutStrategies:
    """Test different timeout strategies"""
    
    def test_graceful_stop_strategy(self):
        """Test graceful stop strategy"""
        config = TimeoutConfig(
            max_time_seconds=60,
            warning_threshold=0.8,
            strategy=TimeoutStrategy.GRACEFUL_STOP,
            allow_extension=False,
            max_extensions=0
        )
        
        assert config.strategy == TimeoutStrategy.GRACEFUL_STOP
    
    def test_complete_chunk_strategy(self):
        """Test complete chunk strategy"""
        config = TimeoutConfig(
            max_time_seconds=60,
            warning_threshold=0.8,
            strategy=TimeoutStrategy.COMPLETE_CHUNK,
            allow_extension=False,
            max_extensions=0
        )
        
        assert config.strategy == TimeoutStrategy.COMPLETE_CHUNK
    
    def test_immediate_stop_strategy(self):
        """Test immediate stop strategy"""
        config = TimeoutConfig(
            max_time_seconds=60,
            warning_threshold=0.8,
            strategy=TimeoutStrategy.IMMEDIATE_STOP,
            allow_extension=False,
            max_extensions=0
        )
        
        assert config.strategy == TimeoutStrategy.IMMEDIATE_STOP


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
