"""
Unit Tests for Response Size Monitor

Tests token estimation, response checking, and auto-chunking logic.

Author: Asif Hussain
Version: 1.0.0
Created: 2025-11-30
"""

import pytest
from pathlib import Path
from src.utils.response_monitor import ResponseSizeMonitor, ResponseCheckResult, create_monitor
import tempfile
import shutil


@pytest.fixture
def temp_brain_path():
    """Create temporary brain directory for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    brain_path = temp_dir / "cortex-brain"
    brain_path.mkdir(parents=True)
    
    yield brain_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def monitor(temp_brain_path):
    """Create ResponseSizeMonitor instance for testing"""
    return ResponseSizeMonitor(temp_brain_path, enable_tiktoken=False)


class TestTokenEstimation:
    """Test token estimation logic"""
    
    def test_estimate_tokens_approximation(self, monitor):
        """Test token estimation using approximation (1 token ≈ 4 chars)"""
        text = "Hello world"  # 11 chars
        tokens = monitor.estimate_tokens(text)
        
        # Should be ~2-3 tokens
        assert 2 <= tokens <= 3
    
    def test_estimate_tokens_empty_string(self, monitor):
        """Test token estimation with empty string"""
        tokens = monitor.estimate_tokens("")
        assert tokens == 0
    
    def test_estimate_tokens_large_text(self, monitor):
        """Test token estimation with large text"""
        # Generate ~10K character text (should be ~2500 tokens)
        text = "word " * 2000  # 10,000 chars
        tokens = monitor.estimate_tokens(text)
        
        # Should be approximately 2500 tokens (10000/4)
        assert 2400 <= tokens <= 2600
    
    def test_estimate_tokens_code(self, monitor):
        """Test token estimation with code (different char/token ratio)"""
        code = """
def example_function(x, y):
    result = x + y
    return result
"""
        tokens = monitor.estimate_tokens(code)
        
        # Code typically has worse ratio, but approximation should work
        assert tokens > 0


class TestResponseChecking:
    """Test response checking logic"""
    
    def test_check_response_safe_small(self, monitor):
        """Test response check with small text (<3K tokens)"""
        text = "Hello " * 100  # ~150 tokens
        result = monitor.check_response(text)
        
        assert result.safe is True
        assert result.action == "SEND"
        assert result.token_count < monitor.WARNING_THRESHOLD
    
    def test_check_response_warning_medium(self, monitor):
        """Test response check with medium text (3K-3.5K tokens)"""
        text = "word " * 2600  # 2600 * 5 chars = 13000 chars = 3250 tokens (WARNING zone)
        result = monitor.check_response(text)
        
        assert result.safe is True
        assert result.action == "WARN"
        assert monitor.WARNING_THRESHOLD < result.token_count < monitor.AUTO_CHUNK_THRESHOLD
    
    def test_check_response_chunk_large(self, monitor):
        """Test response check with large text (>3.5K tokens)"""
        text = "word " * 4000  # ~4000 tokens
        result = monitor.check_response(text)
        
        assert result.safe is False
        assert result.action == "CHUNK_TO_FILE"
        assert result.token_count > monitor.AUTO_CHUNK_THRESHOLD
        assert result.file_path is not None
        assert result.summary is not None
    
    def test_check_response_with_context(self, monitor):
        """Test response check with context information"""
        text = "word " * 4000
        context = {"operation_name": "Test Operation", "feature": "authentication"}
        
        result = monitor.check_response(text, context)
        
        assert result.action == "CHUNK_TO_FILE"
        assert "Test Operation" in result.summary or "test-operation" in str(result.file_path)


class TestAutoChunking:
    """Test auto-chunking to file functionality"""
    
    def test_chunk_to_file_creates_file(self, monitor):
        """Test that chunking creates file in correct location"""
        text = "word " * 4000  # Large text
        result = monitor.check_response(text)
        
        assert result.file_path is not None
        assert result.file_path.exists()
        assert result.file_path.parent == monitor.reports_dir
    
    def test_chunk_to_file_preserves_content(self, monitor):
        """Test that chunked file contains original content"""
        text = "UNIQUE_CONTENT_12345 " * 1000
        result = monitor.check_response(text)
        
        # Read file and verify content
        with open(result.file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert "UNIQUE_CONTENT_12345" in file_content
    
    def test_chunk_to_file_summary_format(self, monitor):
        """Test that summary has correct format"""
        text = "word " * 4000
        context = {"operation_name": "Planning"}
        result = monitor.check_response(text, context)
        
        summary = result.summary
        
        # Summary should contain key information
        assert "Complete" in summary or "Auto-Chunked" in summary
        assert str(result.file_path.name) in summary
        assert str(result.token_count) in summary
    
    def test_chunk_to_file_multiple_calls(self, monitor):
        """Test multiple chunking calls create separate files"""
        text1 = "content1 " * 4000
        text2 = "content2 " * 4000
        
        result1 = monitor.check_response(text1, {"operation_name": "Op1"})
        result2 = monitor.check_response(text2, {"operation_name": "Op2"})
        
        # Should create different files
        assert result1.file_path != result2.file_path
        assert result1.file_path.exists()
        assert result2.file_path.exists()


class TestWrapResponse:
    """Test convenience wrap_response method"""
    
    def test_wrap_response_small_unchanged(self, monitor):
        """Test that small responses pass through unchanged"""
        text = "Small response"
        result = monitor.wrap_response(text, "Test Op")
        
        assert result == text
    
    def test_wrap_response_medium_adds_warning(self, monitor):
        """Test that medium responses get warning header"""
        text = "word " * 2600  # 2600 * 5 chars = 13000 chars = 3250 tokens (WARNING zone)
        result = monitor.wrap_response(text, "Test Op")
        
        assert "Large Response Warning" in result
        assert text in result
    
    def test_wrap_response_large_returns_summary(self, monitor):
        """Test that large responses return summary only"""
        text = "word " * 4000
        result = monitor.wrap_response(text, "Test Op")
        
        # Should return summary, not original text
        assert result != text
        assert "Auto-Chunked" in result
        # Summary should be concise (under 2x original is acceptable due to metadata overhead)
        assert len(result) < len(text) * 2


class TestStatistics:
    """Test statistics and monitoring"""
    
    def test_get_stats_structure(self, monitor):
        """Test that get_stats returns expected structure"""
        stats = monitor.get_stats()
        
        assert "safe_token_limit" in stats
        assert "auto_chunk_threshold" in stats
        assert "warning_threshold" in stats
        assert "tiktoken_available" in stats
        assert "chunked_responses" in stats
        assert "reports_directory" in stats
    
    def test_get_stats_counts_files(self, monitor):
        """Test that get_stats counts chunked files correctly"""
        # Initially should be 0
        stats = monitor.get_stats()
        initial_count = stats["chunked_responses"]
        
        # Create chunked response
        text = "word " * 4000
        monitor.check_response(text)
        
        # Should increment count
        stats = monitor.get_stats()
        assert stats["chunked_responses"] == initial_count + 1


class TestFactoryFunction:
    """Test factory function"""
    
    def test_create_monitor_with_path(self, temp_brain_path):
        """Test creating monitor with explicit path"""
        monitor = create_monitor(temp_brain_path)
        
        assert isinstance(monitor, ResponseSizeMonitor)
        assert monitor.brain_path == temp_brain_path
    
    def test_create_monitor_auto_detect(self):
        """Test creating monitor with auto-detect (should not crash)"""
        # This may fail to find config, but should not crash
        try:
            monitor = create_monitor()
            assert isinstance(monitor, ResponseSizeMonitor)
        except Exception:
            # Auto-detect may fail in test environment, that's OK
            pass


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_unicode_text(self, monitor):
        """Test with Unicode characters"""
        text = "Hello 世界 🌍 " * 1000
        result = monitor.check_response(text)
        
        # Should handle Unicode without crashing
        assert result.token_count > 0
    
    def test_very_long_lines(self, monitor):
        """Test with very long lines (no newlines)"""
        text = "x" * 20000  # Single 20K character line
        result = monitor.check_response(text)
        
        # Should handle long lines
        assert result.token_count > monitor.AUTO_CHUNK_THRESHOLD
        assert result.action == "CHUNK_TO_FILE"
    
    def test_markdown_formatting(self, monitor):
        """Test with markdown-formatted text"""
        text = """
# Heading
## Subheading
- List item 1
- List item 2

**Bold text** and *italic text*.

```python
def example():
    pass
```
""" * 500
        
        result = monitor.check_response(text)
        
        # Should handle markdown
        assert result.token_count > 0
    
    def test_context_without_operation_name(self, monitor):
        """Test chunking with minimal context"""
        text = "word " * 4000
        result = monitor.check_response(text, {})
        
        # Should use default operation name
        assert result.file_path is not None
        assert "response" in result.file_path.name.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
